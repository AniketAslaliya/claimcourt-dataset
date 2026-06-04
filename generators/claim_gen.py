"""
generators/claim_gen.py
Generate insurance claims with ICD-10 codes, realistic INR amounts,
fraud type injection, date logic, and confidence scores.
"""

import numpy as np
import pandas as pd

from config import (
    TARGET_FRAUD_RATE,
    FRAUD_TYPES,
    FRAUD_DISTRIBUTION,
    CONFIDENCE_RANGES,
    ICD10_CODES,
    ICD10_AMOUNTS,
    TPA_LIST,
    POLICY_TYPES,
    POLICY_TYPE_WEIGHTS,
    CASHLESS_RATE,
    LOS_RANGE,
    PROCESSING_DAYS_LEGIT,
    PROCESSING_DAYS_FRAUD,
    GROUND_TRUTH_SOURCES,
    CLAIM_START_DATE,
    CLAIM_END_DATE,
)


def _assign_fraud(n_claims: int, rng: np.random.Generator):
    """Assign fraud labels and types to claims based on target fraud rate."""
    n_fraud = int(n_claims * TARGET_FRAUD_RATE)
    n_legit = n_claims - n_fraud

    # Fraud type assignment
    fraud_type_names = list(FRAUD_DISTRIBUTION.keys())
    fraud_type_weights = list(FRAUD_DISTRIBUTION.values())

    # Use integer indices to avoid numpy string truncation
    fraud_indices = rng.choice(
        len(fraud_type_names), size=n_fraud, p=fraud_type_weights
    )
    fraud_types_assigned = [fraud_type_names[i] for i in fraud_indices]

    # Build arrays as Python lists to avoid numpy string truncation
    labels = [0] * n_claims
    types = ["legitimate"] * n_claims

    for i in range(n_fraud):
        labels[i] = 1
        types[i] = fraud_types_assigned[i]

    # Shuffle together
    perm = rng.permutation(n_claims).tolist()
    labels = [labels[p] for p in perm]
    types = [types[p] for p in perm]

    return labels, types


def _generate_confidence(fraud_type: str, rng: np.random.Generator) -> float:
    """Generate confidence score within the range for this fraud type."""
    lo, hi = CONFIDENCE_RANGES[fraud_type]
    return round(float(rng.uniform(lo, hi)), 4)


def generate_claims(
    n_claims: int,
    patients_df: pd.DataFrame,
    hospitals_df: pd.DataFrame,
    rng: np.random.Generator,
) -> pd.DataFrame:
    """Generate n_claims insurance claims linked to patients and hospitals."""

    # Pre-compute
    patient_ids = patients_df["patient_id"].values
    hospital_ids = hospitals_df["hospital_id"].values
    icd_codes = list(ICD10_CODES.keys())

    # Fraud assignment
    fraud_labels, fraud_types = _assign_fraud(n_claims, rng)

    # Date range for admissions
    start_ts = pd.Timestamp(CLAIM_START_DATE)
    end_ts = pd.Timestamp(CLAIM_END_DATE)
    date_range_days = (end_ts - start_ts).days

    # Agent IDs for coordinated rings
    n_agents = max(20, n_claims // 500)
    agent_ids = [f"A{i+1:03d}" for i in range(n_agents)]

    records = []
    for i in range(n_claims):
        claim_id = f"C{i+1:07d}"
        fraud_label = int(fraud_labels[i])
        fraud_type = fraud_types[i]

        # Assign patient and hospital
        patient_id = rng.choice(patient_ids)
        hospital_id = rng.choice(hospital_ids)

        # ICD-10 code and description
        icd_code = rng.choice(icd_codes)
        diagnosis_desc = ICD10_CODES[icd_code]

        # Amount (base, before fraud adjustment)
        amt_lo, amt_hi = ICD10_AMOUNTS[icd_code]
        claim_amount_requested = int(rng.integers(amt_lo, amt_hi))

        # Approved amount (legitimate: 80-100% of requested)
        if fraud_label == 0:
            approval_ratio = rng.uniform(0.80, 1.0)
        else:
            # Fraud claims may get full approval (undetected) or partial
            approval_ratio = rng.uniform(0.50, 1.0)
        claim_amount_approved = int(claim_amount_requested * approval_ratio)

        # Dates
        admission_offset = rng.integers(0, date_range_days)
        date_of_admission = start_ts + pd.Timedelta(days=int(admission_offset))

        los = int(rng.integers(LOS_RANGE[0], LOS_RANGE[1] + 1))
        date_of_discharge = date_of_admission + pd.Timedelta(days=los)

        # Processing time
        if fraud_label == 1:
            proc_days = int(rng.integers(PROCESSING_DAYS_FRAUD[0], PROCESSING_DAYS_FRAUD[1] + 1))
        else:
            proc_days = int(rng.integers(PROCESSING_DAYS_LEGIT[0], PROCESSING_DAYS_LEGIT[1] + 1))
        date_of_claim = date_of_discharge + pd.Timedelta(days=proc_days)

        # Policy type
        policy_type = rng.choice(POLICY_TYPES, p=POLICY_TYPE_WEIGHTS)

        # Is cashless
        is_cashless = rng.random() < CASHLESS_RATE

        # TPA
        tpa = rng.choice(TPA_LIST)

        # Days since policy start (approximate)
        patient_row = patients_df.loc[patients_df["patient_id"] == patient_id].iloc[0]
        policy_start = pd.Timestamp(patient_row["policy_start_date"])
        days_since_policy = max(0, (date_of_admission - policy_start).days)

        # Confidence score
        fraud_confidence = _generate_confidence(fraud_type, rng)

        # Ground truth source
        gt_source = rng.choice(GROUND_TRUTH_SOURCES)

        # Default signal columns (fraud_gen will override these)
        provider_blacklist = False
        previous_fraud = False
        num_insurers_same_event = 1
        icd_matches_procedure = True
        discharge_readmit_gap = rng.integers(30, 365)
        pharmacy_bill_ratio = round(float(rng.uniform(0.05, 0.35)), 2)
        agent_id = rng.choice(agent_ids)

        records.append({
            "claim_id": claim_id,
            "patient_id": patient_id,
            "hospital_id": hospital_id,
            "diagnosis_primary": icd_code,
            "diagnosis_description": diagnosis_desc,
            "date_of_admission": date_of_admission.strftime("%Y-%m-%d"),
            "date_of_discharge": date_of_discharge.strftime("%Y-%m-%d"),
            "date_of_claim": date_of_claim.strftime("%Y-%m-%d"),
            "length_of_stay_days": los,
            "claim_amount_requested_inr": claim_amount_requested,
            "claim_amount_approved_inr": claim_amount_approved,
            "policy_type": policy_type,
            "is_cashless": is_cashless,
            "tpa": tpa,
            "provider_blacklist_flag": provider_blacklist,
            "previous_fraud_on_policy": previous_fraud,
            "days_since_policy_start": days_since_policy,
            "num_insurers_same_event": num_insurers_same_event,
            "icd_code_matches_procedure": icd_matches_procedure,
            "discharge_readmit_gap_days": int(discharge_readmit_gap),
            "pharmacy_bill_ratio": pharmacy_bill_ratio,
            "agent_id": agent_id,
            "fraud_label": fraud_label,
            "fraud_type": fraud_type,
            "fraud_confidence": fraud_confidence,
            "ground_truth_source": gt_source,
        })

    return pd.DataFrame(records)
