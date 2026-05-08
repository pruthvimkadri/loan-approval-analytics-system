print("LOAN DASHBOARD APP RUNNING")
from flask import Flask, render_template, request, redirect, url_for, session
import pickle
import pandas as pd
import sqlite3
from datetime import datetime

app = Flask(__name__)
app.secret_key = "secret123"  # Required for login session

# ---------------------------
# LOAD MODEL
# ---------------------------
model = pickle.load(open("model.pkl", "rb"))

DB_PATH = r"D:\LoanApprovalproject\model\predictions.db"

# ---------------------------
# INIT DATABASE
# ---------------------------
def init_db():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # Predictions table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS predictions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            time TEXT,
            gender TEXT,
            married TEXT,
            dependents TEXT,
            education TEXT,
            self_employed TEXT,
            applicant_income REAL,
            coapplicant_income REAL,
            total_income REAL,
            loan_amount REAL,
            loan_term REAL,
            credit_history TEXT,
            property_area TEXT,
            result TEXT,
            confidence REAL,
            reason TEXT
        )
    """)

    # Users table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE,
            password TEXT
        )
    """)

    # Insert default user only once
    cursor.execute("SELECT * FROM users WHERE username='admin'")
    if not cursor.fetchone():
        cursor.execute(
            "INSERT INTO users (username, password) VALUES (?, ?)",
            ("admin", "1234")
        )

    conn.commit()
    conn.close()

init_db()

# ---------------------------
# SAVE TO DB
# ---------------------------
def save_prediction(data, result, prob, raw, reason):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO predictions 
        (time, gender, married, dependents, education, self_employed,
         applicant_income, coapplicant_income, total_income,
         loan_amount, loan_term, credit_history, property_area,
         result, confidence, reason)
        VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)
    """, (
        str(datetime.now()),
        raw["Gender"],
        raw["Married"],
        raw["Dependents"],
        raw["Education"],
        raw["Self_Employed"],
        raw["ApplicantIncome"],
        raw["CoapplicantIncome"],
        data["TotalIncome"],
        data["LoanAmount"],
        data["Loan_Amount_Term"],
        raw["Credit_History"],
        raw["Property_Area"],
        result,
        float(prob),
        reason
    ))

    conn.commit()
    conn.close()

# ---------------------------
# REASON FUNCTION
# ---------------------------
def generate_reason(data, raw):
    reasons = []

    if data['TotalIncome'] < 3000:
        reasons.append("Low income")

    if raw['Credit_History'] == "Bad":
        reasons.append("Poor credit history")

    if data['LoanAmount'] > data['TotalIncome'] * 0.5:
        reasons.append("Loan amount high compared to income")

    if not reasons:
        return "Strong applicant profile"

    return ", ".join(reasons)

# ---------------------------
# LOGIN ROUTE
# ---------------------------
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()

        cursor.execute(
            "SELECT * FROM users WHERE username=? AND password=?",
            (username, password)
        )
        user = cursor.fetchone()
        conn.close()

        if user:
            session['user'] = username
            return redirect(url_for('home'))
        else:
            return render_template("login.html", error="Invalid credentials")

    return render_template("login.html")

@app.route('/logout')
def logout():
    session.pop('user', None)
    return redirect(url_for('login'))

# ---------------------------
# HOME ROUTE
# ---------------------------
@app.route('/')
def home():
    if 'user' not in session:
        return redirect(url_for('login'))
    return render_template("index.html")

# ---------------------------
# PREDICT ROUTE
# ---------------------------
@app.route('/predict', methods=['POST'])
def predict():
    try:
        if 'user' not in session:
            return redirect('/login')

        credit_raw = request.form['Credit_History']

        raw = {
            "Gender": request.form['Gender'],
            "Married": request.form['Married'],
            "Dependents": request.form['Dependents'],
            "Education": request.form['Education'],
            "Self_Employed": request.form['Self_Employed'],
            "ApplicantIncome": float(request.form['ApplicantIncome']),
            "CoapplicantIncome": float(request.form['CoapplicantIncome']),
            "Property_Area": request.form['Property_Area'],
            "Credit_History": credit_raw
        }

        total_income = raw["ApplicantIncome"] + raw["CoapplicantIncome"]

        data = {
            'LoanAmount': float(request.form['LoanAmount']),
            'Loan_Amount_Term': float(request.form['Loan_Term']),
            'Credit_History': 1 if credit_raw == "Good" else 0,
            'TotalIncome': total_income,

            'Gender_Male': 1 if raw["Gender"] == 'Male' else 0,
            'Married_Yes': 1 if raw["Married"] == 'Yes' else 0,
            'Dependents_1': 1 if raw["Dependents"] == '1' else 0,
            'Dependents_2': 1 if raw["Dependents"] == '2' else 0,
            'Dependents_3+': 1 if raw["Dependents"] == '3+' else 0,
            'Education_Not Graduate': 1 if raw["Education"] == 'Not Graduate' else 0,
            'Self_Employed_Yes': 1 if raw["Self_Employed"] == 'Yes' else 0,
            'Property_Area_Semiurban': 1 if raw["Property_Area"] == 'Semiurban' else 0,
            'Property_Area_Urban': 1 if raw["Property_Area"] == 'Urban' else 0
        }

        df = pd.DataFrame([data])

        pred = model.predict(df)[0]
        prob = round(model.predict_proba(df)[0][pred] * 100, 2)

        result = "Approved" if pred == 1 else "Rejected"
        reason = generate_reason(data, raw)

        save_prediction(data, result, prob, raw, reason)

        return render_template(
            "index.html",
            prediction_text=result,
            probability=prob,
            reason=reason
        )

    except Exception as e:
        return f"Error: {str(e)}"

# ---------------------------
# DASHBOARD ROUTE
# ---------------------------
@app.route('/dashboard')
def dashboard():
    if 'user' not in session:
        return redirect(url_for('login'))

    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    # Total predictions
    cursor.execute("SELECT COUNT(*) AS total FROM predictions")
    total_predictions = cursor.fetchone()["total"]

    # Approved count
    cursor.execute("SELECT COUNT(*) AS approved FROM predictions WHERE result='Approved'")
    approved_count = cursor.fetchone()["approved"]

    # Rejected count
    cursor.execute("SELECT COUNT(*) AS rejected FROM predictions WHERE result='Rejected'")
    rejected_count = cursor.fetchone()["rejected"]

    # Approval rate
    approval_rate = round((approved_count / total_predictions) * 100, 2) if total_predictions > 0 else 0

    # Average confidence
    cursor.execute("SELECT AVG(confidence) AS avg_conf FROM predictions")
    avg_conf_row = cursor.fetchone()
    average_confidence = round(avg_conf_row["avg_conf"], 2) if avg_conf_row["avg_conf"] else 0

    # Result distribution for pie chart
    cursor.execute("""
        SELECT result, COUNT(*) AS cnt
        FROM predictions
        GROUP BY result
    """)
    result_rows = cursor.fetchall()

    chart_labels = [row["result"] for row in result_rows]
    chart_values = [row["cnt"] for row in result_rows]

    # Recent predictions
    cursor.execute("""
        SELECT time, applicant_income, coapplicant_income, loan_amount,
               credit_history, result, confidence, reason
        FROM predictions
        ORDER BY id DESC
        LIMIT 5
    """)
    recent_predictions = cursor.fetchall()

    conn.close()

    return render_template(
        "dashboard.html",
        total_predictions=total_predictions,
        approved_count=approved_count,
        rejected_count=rejected_count,
        approval_rate=approval_rate,
        average_confidence=average_confidence,
        chart_labels=chart_labels,
        chart_values=chart_values,
        recent_predictions=recent_predictions
    )

# ---------------------------
# RUN
# ---------------------------
if __name__ == "__main__":
    app.run(debug=True)