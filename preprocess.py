import pandas as pd

df = pd.read_csv("data/train.csv")

# Fill missing values
df.fillna({
    "Gender": "Male",
    "Married": "Yes",
    "Dependents": 0,
    "Self_Employed": "No",
    "LoanAmount": df["LoanAmount"].mean(),
    "Loan_Amount_Term": 360,
    "Credit_History": 1
}, inplace=True)

print(df.isnull().sum())
df.to_csv("data/cleaned.csv", index=False)

print("Data cleaned ✅")