"""
validators/stats_check.py
Run this before publishing to Kaggle or uploading to Adaption.
All checks must pass. Fix issues in config.py or generators/, not here.
Usage: python validators/stats_check.py data/claims.csv
"""

import sys
import pandas as pd

REQUIRED_FRAUD_RATE = 0.18
TOLERANCE = 0.02
REQUIRED_FRAUD_TYPES = {
    "legitimate", "bill_inflation", "phantom_provider", "identity_fraud",
    "staged_accident", "coordinated_ring", "duplicate_claim",
    "unnecessary_procedure", "icd_upcoding", "fake_policy",
    "pre_existing_hidden", "readmission_fraud", "pharmacy_fraud",
}
VALID_ICD_PREFIXES = list("ABCDEFGHIJKLMNOPQRSTUVWXYZ") + ["Z"]


def check(condition, message):
    status = "✓" if condition else "✗"
    print(f"  {status} {message}")
    return condition


def run_checks(path):
    print(f"\nValidating: {path}")
    print("=" * 50)
    df = pd.read_csv(path)
    passed = 0
    total = 0

    # Fraud rate
    fraud_rate = df["fraud_label"].mean()
    ok = abs(fraud_rate - REQUIRED_FRAUD_RATE) <= TOLERANCE
    check(ok, f"Fraud rate: {fraud_rate:.1%} (target {REQUIRED_FRAUD_RATE:.0%} ±{TOLERANCE:.0%})")
    passed += ok; total += 1

    # No nulls in required fields
    required = ["claim_id", "patient_id", "hospital_id", "diagnosis_primary",
                "fraud_label", "fraud_type", "fraud_confidence"]
    nulls = df[required].isnull().sum().sum()
    ok = nulls == 0
    check(ok, f"No nulls in required fields (found {nulls})")
    passed += ok; total += 1

    # Date logic
    df["date_of_admission"] = pd.to_datetime(df["date_of_admission"])
    df["date_of_discharge"] = pd.to_datetime(df["date_of_discharge"])
    df["date_of_claim"] = pd.to_datetime(df["date_of_claim"])
    ok = (df["date_of_discharge"] >= df["date_of_admission"]).all()
    check(ok, "date_of_discharge >= date_of_admission")
    passed += ok; total += 1

    ok = (df["date_of_claim"] >= df["date_of_discharge"]).all()
    check(ok, "date_of_claim >= date_of_discharge")
    passed += ok; total += 1

    # Amount logic
    ok = (df["claim_amount_approved_inr"] <= df["claim_amount_requested_inr"]).all()
    check(ok, "claim_amount_approved <= claim_amount_requested")
    passed += ok; total += 1

    # Confidence range
    ok = df["fraud_confidence"].between(0.0, 1.0).all()
    check(ok, "fraud_confidence in [0.0, 1.0]")
    passed += ok; total += 1

    # Fraud type when label=0 must be "legitimate"
    mismatch = df[(df["fraud_label"] == 0) & (df["fraud_type"] != "legitimate")]
    ok = len(mismatch) == 0
    check(ok, f"fraud_type='legitimate' when fraud_label=0 ({len(mismatch)} mismatches)")
    passed += ok; total += 1

    # All fraud types present
    present = set(df["fraud_type"].unique())
    missing = REQUIRED_FRAUD_TYPES - present
    ok = len(missing) == 0
    check(ok, f"All 13 fraud types present (missing: {missing or 'none'})")
    passed += ok; total += 1

    # ICD codes format
    ok = df["diagnosis_primary"].str.match(r"^[A-Z]\d{2}(\.\d+)?$").all()
    check(ok, "ICD codes are valid format (letter + 2 digits)")
    passed += ok; total += 1

    print("=" * 50)
    print(f"Result: {passed}/{total} checks passed")
    if passed == total:
        print("ALL CHECKS PASSED. Safe to publish.")
    else:
        print(f"FIX {total - passed} ISSUE(S) BEFORE PUBLISHING.")
    print()
    return passed == total


if __name__ == "__main__":
    path = sys.argv[1] if len(sys.argv) > 1 else "data/claims.csv"
    success = run_checks(path)
    sys.exit(0 if success else 1)