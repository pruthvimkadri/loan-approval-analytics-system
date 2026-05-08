import pandas as pd
from datetime import datetime

def generate_reason(data):
    if data['TotalIncome'] < 3000:
        return "Low income"
    elif data['Credit_History'] == 0:
        return "Poor credit history"
    return "Good financial profile"


def export_to_csv(db_model):
    data = db_model.query.all()

    rows = []
    for d in data:
        rows.append({
            "Time": d.time,
            "Gender": d.gender,
            "Married": d.married,
            "Dependents": d.dependents,
            "Education": d.education,
            "Self_Employed": d.self_employed,
            "ApplicantIncome": d.applicant_income,
            "CoapplicantIncome": d.coapplicant_income,
            "TotalIncome": d.total_income,
            "LoanAmount": d.loan_amount,
            "LoanTerm": d.loan_term,
            "CreditHistory": d.credit_history,
            "PropertyArea": d.property_area,
            "Result": d.result,
            "Confidence": d.confidence
        })

    df = pd.DataFrame(rows)
    df.to_csv("data/predictions_export.csv", index=False)