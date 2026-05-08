import pandas as pd
import numpy as np

df = pd.read_csv("data/cleaned.csv")

# Add new features
df["CIBIL_Score"] = np.random.randint(300, 900, len(df))
df["Age"] = np.random.randint(21, 60, len(df))
df["Debt_to_Income"] = df["LoanAmount"] / df["ApplicantIncome"]

df.to_csv("data/final.csv", index=False)

print("Features added ✅")