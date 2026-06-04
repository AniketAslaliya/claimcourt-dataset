"""
generators/fraud_gen.py
Post-processing pass that injects realistic fraud signals per type.
Each fraud type has specific column signatures matching the Realism Rules
defined in SKILL.md.
"""

import numpy as np
import pandas as pd

from config import ICD10_AMOUNTS


def inject_fraud_signals(
    claims_df: pd.DataFrame,
    hospitals_df: pd.DataFrame,
    rng: np.random.Generator,
) -> tuple[pd.DataFrame, pd.DataFrame]:
    """
    Mutate claims_df in place to inject realistic fraud signals.
    Returns (claims_df, hospitals_df) with updated flags.
    """
    df = claims_df.copy()
    hosp = hospitals_df.copy()

    # Index fraud rows by type for efficient processing
    for fraud_type in df["fraud_type"].unique():
        if fraud_type == "legitimate":
            continue

        mask = df["fraud_type"] == fraud_type
        idx = df.index[mask]

        if fraud_type == "bill_inflation":
            # Inflate amounts by 1.5-3.0x
            for i in idx:
                multiplier = rng.uniform(1.5, 3.0)
                df.at[i, "claim_amount_requested_inr"] = int(
                    df.at[i, "claim_amount_requested_inr"] * multiplier
                )
                # Approved might also be inflated (if undetected)
                df.at[i, "claim_amount_approved_inr"] = int(
                    df.at[i, "claim_amount_approved_inr"] * rng.uniform(1.2, 2.5)
                )
                # Ensure approved <= requested
                df.at[i, "claim_amount_approved_inr"] = min(
                    df.at[i, "claim_amount_approved_inr"],
                    df.at[i, "claim_amount_requested_inr"],
                )

        elif fraud_type == "phantom_provider":
            # Mark hospitals as phantom
            phantom_hosp_ids = df.loc[idx, "hospital_id"].unique()
            for hid in phantom_hosp_ids:
                hmask = hosp["hospital_id"] == hid
                if hmask.any():
                    hosp.loc[hmask, "is_phantom"] = True
                    # Invalidate Rohini ID
                    bad_rohini = rng.choice([
                        "PENDING", "NA", f"ROH-{rng.integers(10000, 99999)}",
                        f"ROHINI-0{rng.integers(10000, 99999)}",
                    ])
                    hosp.loc[hmask, "rohini_id"] = bad_rohini
            # Provider blacklist flag
            df.loc[idx, "provider_blacklist_flag"] = True

        elif fraud_type == "identity_fraud":
            # Policy age < 90 days, KYC not verified
            df.loc[idx, "days_since_policy_start"] = rng.integers(5, 90, size=len(idx))

        elif fraud_type == "staged_accident":
            # Trauma ICD codes, no prior history
            trauma_codes = ["S72.0", "S06.3"]
            for i in idx:
                code = rng.choice(trauma_codes)
                df.at[i, "diagnosis_primary"] = code
                df.at[i, "diagnosis_description"] = {
                    "S72.0": "Femur fracture",
                    "S06.3": "Traumatic brain injury",
                }[code]
                # Adjust amounts to match new ICD code
                lo, hi = ICD10_AMOUNTS[code]
                df.at[i, "claim_amount_requested_inr"] = int(rng.integers(lo, hi))
                df.at[i, "claim_amount_approved_inr"] = int(
                    df.at[i, "claim_amount_requested_inr"] * rng.uniform(0.7, 1.0)
                )

        elif fraud_type == "coordinated_ring":
            # Group 3-8 claims by city + 30-day window + same agent
            ring_size = min(len(idx), int(rng.integers(3, 9)))
            ring_idx = rng.choice(idx, size=ring_size, replace=False)
            # Same hospital, same agent, tight date window
            shared_hospital = df.at[ring_idx[0], "hospital_id"]
            shared_agent = df.at[ring_idx[0], "agent_id"]
            base_date = pd.Timestamp(df.at[ring_idx[0], "date_of_admission"])
            for j, ri in enumerate(ring_idx):
                df.at[ri, "hospital_id"] = shared_hospital
                df.at[ri, "agent_id"] = shared_agent
                # Within 30-day window
                offset = int(rng.integers(0, 30))
                new_admit = base_date + pd.Timedelta(days=offset)
                df.at[ri, "date_of_admission"] = new_admit.strftime("%Y-%m-%d")
                los = int(df.at[ri, "length_of_stay_days"])
                df.at[ri, "date_of_discharge"] = (
                    new_admit + pd.Timedelta(days=los)
                ).strftime("%Y-%m-%d")
                df.at[ri, "date_of_claim"] = (
                    new_admit + pd.Timedelta(days=los + int(rng.integers(2, 5)))
                ).strftime("%Y-%m-%d")
            # Mark hospital as blacklisted
            hmask = hosp["hospital_id"] == shared_hospital
            if hmask.any():
                hosp.loc[hmask, "blacklisted"] = True

        elif fraud_type == "duplicate_claim":
            # Multiple insurers for same event
            df.loc[idx, "num_insurers_same_event"] = rng.integers(2, 5, size=len(idx))

        elif fraud_type == "unnecessary_procedure":
            # Procedure code mismatch with diagnosis severity
            df.loc[idx, "icd_code_matches_procedure"] = False

        elif fraud_type == "icd_upcoding":
            # ICD code mismatch + inflated amount
            df.loc[idx, "icd_code_matches_procedure"] = False
            for i in idx:
                # Inflate amount moderately (1.3-2.0x)
                df.at[i, "claim_amount_requested_inr"] = int(
                    df.at[i, "claim_amount_requested_inr"] * rng.uniform(1.3, 2.0)
                )
                df.at[i, "claim_amount_approved_inr"] = min(
                    int(df.at[i, "claim_amount_approved_inr"] * rng.uniform(1.1, 1.8)),
                    df.at[i, "claim_amount_requested_inr"],
                )

        elif fraud_type == "fake_policy":
            # Policy document forged, agent fraud flag
            df.loc[idx, "previous_fraud_on_policy"] = True
            df.loc[idx, "days_since_policy_start"] = rng.integers(1, 30, size=len(idx))

        elif fraud_type == "pre_existing_hidden":
            # Condition existed before policy start
            df.loc[idx, "days_since_policy_start"] = rng.integers(10, 180, size=len(idx))

        elif fraud_type == "readmission_fraud":
            # Discharged and readmitted same day (gap = 0 or 1)
            df.loc[idx, "discharge_readmit_gap_days"] = rng.integers(0, 2, size=len(idx))

        elif fraud_type == "pharmacy_fraud":
            # Abnormally high pharmacy bill ratio (> 0.60)
            df.loc[idx, "pharmacy_bill_ratio"] = [
                round(float(rng.uniform(0.60, 0.95)), 2) for _ in range(len(idx))
            ]

    # Update hospital fraud stats
    for hid in hosp["hospital_id"]:
        claims_for_hosp = df[df["hospital_id"] == hid]
        total = len(claims_for_hosp)
        if total > 0:
            fraud_count = claims_for_hosp["fraud_label"].sum()
            hosp.loc[hosp["hospital_id"] == hid, "total_claims_filed"] = total
            hosp.loc[hosp["hospital_id"] == hid, "fraud_claims_ratio"] = round(
                fraud_count / total, 4
            )
            # Blacklist hospitals with > 30% fraud ratio
            if fraud_count / total > 0.30:
                hosp.loc[hosp["hospital_id"] == hid, "blacklisted"] = True

    # Mark provider_blacklist for claims at blacklisted hospitals
    blacklisted_ids = set(hosp.loc[hosp["blacklisted"] == True, "hospital_id"])
    df.loc[df["hospital_id"].isin(blacklisted_ids), "provider_blacklist_flag"] = True

    return df, hosp
