import pandas as pd
import numpy as np
import pickle

from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, classification_report
from xgboost import XGBClassifier

# =========================
# 1. LOAD DATA
# =========================
df = pd.read_csv(r"D:\LoanApprovalproject\data\train.csv")

# =========================
# 2. DATA CLEANING
# =========================
df = df.ffill()   # fill missing values

# Drop unnecessary column
if 'Loan_ID' in df.columns:
    df.drop('Loan_ID', axis=1, inplace=True)

# Convert target column
df['Loan_Status'] = df['Loan_Status'].map({'Y': 1, 'N': 0})

# =========================
# 3. FEATURE ENGINEERING
# =========================

# Create new feature (IMPORTANT 🔥)
df['TotalIncome'] = df['ApplicantIncome'] + df['CoapplicantIncome']

# Drop old columns
df.drop(['ApplicantIncome', 'CoapplicantIncome'], axis=1, inplace=True)

# Convert categorical to numeric
df = pd.get_dummies(df, drop_first=True)

# =========================
# 4. SPLIT DATA
# =========================
X = df.drop('Loan_Status', axis=1)
y = df['Loan_Status']

X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42
)

# =========================
# 5. MODEL (XGBOOST 🔥)
# =========================
model = XGBClassifier(
    n_estimators=300,
    learning_rate=0.05,
    max_depth=4,
    scale_pos_weight=1.5,   # handle imbalance
    random_state=42,
    use_label_encoder=False,
    eval_metric='logloss'
)

model.fit(X_train, y_train)

# =========================
# 6. EVALUATION
# =========================
y_pred = model.predict(X_test)

print("\n✅ Accuracy:", accuracy_score(y_test, y_pred))
print("\n📊 Classification Report:\n")
print(classification_report(y_test, y_pred))

# =========================
# 7. SAVE MODEL FILES
# =========================
pickle.dump(model, open("model.pkl", "wb"))

# Save feature columns (VERY IMPORTANT for Flask)
pickle.dump(X.columns, open("features.pkl", "wb"))

print("\n✅ Model + features saved successfully")
print(type(model))
print(X.columns)