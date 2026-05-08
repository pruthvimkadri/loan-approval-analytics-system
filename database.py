import sqlite3
from config import Config

def get_connection():
    return sqlite3.connect(Config.DATABASE)

def init_db():
    conn = get_connection()
    cursor = conn.cursor()

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
            credit_history REAL,
            property_area TEXT,
            result TEXT,
            confidence REAL
        )
    """)

    conn.commit()
    conn.close()