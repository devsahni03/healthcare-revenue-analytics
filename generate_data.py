"""
Generates a realistic synthetic healthcare revenue-cycle dataset:
encounters, billing, payer, denial reasons, department.
Scale: ~70,000 encounters, mirroring the scope described in the resume project.
"""
import numpy as np
import pandas as pd
from datetime import datetime, timedelta
import random

np.random.seed(42)
random.seed(42)

N = 72000

departments = ["Cardiology", "Orthopedics", "Emergency", "Oncology", "General Medicine",
               "Radiology", "Surgery", "Pediatrics", "Neurology"]
dept_weights = [0.14, 0.12, 0.20, 0.08, 0.16, 0.10, 0.10, 0.06, 0.04]

payers = ["Aetna", "UnitedHealthcare", "Cigna", "Medicare", "Medicaid", "BlueCross BlueShield", "Self-Pay"]
payer_weights = [0.16, 0.18, 0.12, 0.22, 0.12, 0.15, 0.05]

denial_reasons = [
    "Prior Authorization Missing", "Coding Error", "Duplicate Claim",
    "Coverage Terminated", "Medical Necessity Not Met", "Timely Filing Limit Exceeded",
    "Incorrect Patient Info", "Non-Covered Service"
]

status_options = ["Paid", "Denied", "Partially Paid", "Pending"]

start_date = datetime(2024, 1, 1)
end_date = datetime(2025, 12, 31)
date_range_days = (end_date - start_date).days

rows = []
for i in range(N):
    dept = np.random.choice(departments, p=dept_weights)
    payer = np.random.choice(payers, p=payer_weights)

    # base billed amount varies by department (in INR)
    dept_base = {
        "Cardiology": 2000, "Orthopedics": 2300, "Emergency": 820,
        "Oncology": 2900, "General Medicine": 640, "Radiology": 550,
        "Surgery": 3200, "Pediatrics": 600, "Neurology": 2550
    }
    billed = max(150, np.random.normal(dept_base[dept], dept_base[dept] * 0.35))

    service_date = start_date + timedelta(days=random.randint(0, date_range_days))

    # denial probability varies by payer (Self-Pay and Medicaid slightly higher, reflecting real patterns)
    denial_prob = {
        "Aetna": 0.09, "UnitedHealthcare": 0.10, "Cigna": 0.085, "Medicare": 0.11,
        "Medicaid": 0.14, "BlueCross BlueShield": 0.095, "Self-Pay": 0.05
    }[payer]

    roll = random.random()
    if roll < denial_prob:
        claim_status = "Denied"
        denial_reason = np.random.choice(denial_reasons)
        allowed = 0
        paid = 0
    elif roll < denial_prob + 0.06:
        claim_status = "Partially Paid"
        denial_reason = np.random.choice(denial_reasons)
        allowed = billed * np.random.uniform(0.4, 0.75)
        paid = allowed * np.random.uniform(0.6, 0.95)
    elif roll < denial_prob + 0.06 + 0.05:
        claim_status = "Pending"
        denial_reason = None
        allowed = None
        paid = None
    else:
        claim_status = "Paid"
        denial_reason = None
        allowed = billed * np.random.uniform(0.82, 0.98)
        paid = allowed * np.random.uniform(0.95, 1.0)

    rows.append({
        "encounter_id": f"ENC{100000+i}",
        "patient_id": f"PAT{random.randint(10000, 45000)}",
        "department": dept,
        "payer": payer,
        "service_date": service_date.strftime("%Y-%m-%d"),
        "billed_amount": round(billed, 2),
        "allowed_amount": round(allowed, 2) if allowed is not None else None,
        "paid_amount": round(paid, 2) if paid is not None else None,
        "claim_status": claim_status,
        "denial_reason": denial_reason,
    })

df = pd.DataFrame(rows)
df.to_csv("/home/claude/healthcare_project/data/healthcare_encounters.csv", index=False)
print(df.shape)
print(df["claim_status"].value_counts(normalize=True))
print("Total billed (Cr):", round(df["billed_amount"].sum() / 1e7, 2))
