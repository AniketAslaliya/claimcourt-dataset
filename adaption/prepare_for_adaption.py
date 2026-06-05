"""
adaption/prepare_for_adaption.py
Enrich claims.csv with claim_description and adjudication_reasoning columns
required by Adaption SDK column_mapping before upload.

Usage:
    python adaption/prepare_for_adaption.py
    python adaption/prepare_for_adaption.py --claims data/claims.csv --output data/claims_for_adaption.csv
"""

import os
import sys
import argparse

import pandas as pd
from dotenv import load_dotenv

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import ICD10_AMOUNTS

load_dotenv()


def build_claim_description(row: pd.Series) -> str:
    """Build a medically-framed prompt using one of 4 rotating styles for diversity."""
    days_to_file = (pd.Timestamp(row["date_of_claim"]) - pd.Timestamp(row["date_of_discharge"])).days
    policy_years = round(int(row["days_since_policy_start"]) / 365, 1)
    pre_existing = row["pre_existing_conditions"] if row["pre_existing_conditions"] != "none" else "no declared pre-existing conditions"
    cashless_str = "cashless" if row["is_cashless"] else "reimbursement"
    facility_status = "unregistered phantom facility" if row["is_phantom"] else "IRDAI-empanelled hospital"
    blacklist_str = "blacklisted" if row["provider_blacklist_flag"] else "not blacklisted"
    icd_match_str = "consistent with diagnosis" if row["icd_code_matches_procedure"] else "inconsistent with diagnosis — mismatch flagged"
    prior_fraud_str = "prior fraud recorded on this policy" if row["previous_fraud_on_policy"] else "no prior fraud history"
    identity_str = f"identity {('verified' if row['identity_verified'] else 'unverified')} via {row['kyc_type']}"

    # 4 rotating styles keyed by claim_id suffix to ensure even distribution
    style = int(row["claim_id"].replace("C", "")) % 4

    if style == 0:
        # Style A: Clinical case narrative
        return (
            f"Adjudication Request — Health Insurance Claim\n\n"
            f"A {row['age']}-year-old {row['gender']} patient ({row['language']}-speaking, {row['state']}) "
            f"was hospitalised at {row['hospital_name']} in {row['hospital_city']} "
            f"with a primary diagnosis of {row['diagnosis_description']} (ICD-10: {row['diagnosis_primary']}). "
            f"Inpatient stay: {row['date_of_admission']} to {row['date_of_discharge']} "
            f"({row['length_of_stay_days']} days). Medical history: {pre_existing}.\n\n"
            f"The treating facility is a {facility_status}, specialising in {row['specialization']}, "
            f"and is currently {blacklist_str}. "
            f"Claim submitted as {cashless_str} via {row['tpa']} TPA under a {row['policy_type']} "
            f"health policy active for {policy_years} years. "
            f"Billed amount: INR {int(row['claim_amount_requested_inr']):,}; "
            f"approved: INR {int(row['claim_amount_approved_inr']):,}. "
            f"Pharmacy share of total bill: {row['pharmacy_bill_ratio']*100:.0f}%.\n\n"
            f"Risk flags: Procedure is {icd_match_str}. {prior_fraud_str.capitalize()}. "
            f"{row['num_insurers_same_event']} insurer(s) for this event. "
            f"Readmission gap: {row['discharge_readmit_gap_days']} days. "
            f"Claim filed {days_to_file} days post-discharge. {identity_str.capitalize()}."
        )

    elif style == 1:
        # Style B: Adjudicator desk note
        return (
            f"IRDAI Fraud Screening — Inpatient Claim Review\n\n"
            f"Claim received from {row['tpa']} TPA for a {row['policy_type']} policyholder "
            f"({row['age']} years, {row['gender']}, {row['state']}). "
            f"Diagnosis on admission: {row['diagnosis_description']} (ICD-10: {row['diagnosis_primary']}). "
            f"Hospitalisation period: {row['length_of_stay_days']} days "
            f"({row['date_of_admission']} — {row['date_of_discharge']}). "
            f"Comorbidities on record: {pre_existing}.\n\n"
            f"Provider: {row['hospital_name']}, {row['hospital_city']} (Tier {row['city_tier']}), "
            f"{row['specialization']} specialisation. "
            f"Provider registry status: {facility_status}, {blacklist_str}. "
            f"Billing: INR {int(row['claim_amount_requested_inr']):,} requested under {cashless_str} mode; "
            f"INR {int(row['claim_amount_approved_inr']):,} sanctioned. "
            f"Pharmacy proportion: {row['pharmacy_bill_ratio']*100:.0f}% of total billed amount.\n\n"
            f"Screening indicators: ICD-procedure alignment is {icd_match_str}. "
            f"Policy tenure: {policy_years} years ({prior_fraud_str}). "
            f"Duplicate insurer check: {row['num_insurers_same_event']} insurer(s). "
            f"Post-discharge readmission gap: {row['discharge_readmit_gap_days']} days. "
            f"Filing delay: {days_to_file} days after discharge. "
            f"KYC status: {identity_str}."
        )

    elif style == 2:
        # Style C: Clinical audit summary
        return (
            f"Health Claim Clinical Audit — {row['diagnosis_description']}\n\n"
            f"Patient: {row['age']}-year-old {row['gender']}, {row['language']}-speaking, "
            f"domiciled in {row['state']}. "
            f"Presenting condition: {row['diagnosis_description']} (ICD-10: {row['diagnosis_primary']}). "
            f"Admitted {row['date_of_admission']}, discharged {row['date_of_discharge']} "
            f"after {row['length_of_stay_days']} days of inpatient treatment. "
            f"Declared medical history: {pre_existing}. "
            f"Patient {identity_str}.\n\n"
            f"Treating hospital: {row['hospital_name']} ({row['hospital_city']}, Tier {row['city_tier']}), "
            f"a {facility_status} with {row['specialization']} focus, currently {blacklist_str}. "
            f"Total treatment expenditure: INR {int(row['claim_amount_requested_inr']):,} "
            f"({cashless_str} claim, {row['tpa']}). "
            f"Sanctioned: INR {int(row['claim_amount_approved_inr']):,}. "
            f"Pharmacy-to-total ratio: {row['pharmacy_bill_ratio']*100:.0f}%.\n\n"
            f"Fraud screening: Procedure code is {icd_match_str}. "
            f"{prior_fraud_str.capitalize()}. "
            f"Multi-insurer flag: {row['num_insurers_same_event']} insurer(s) for this admission episode. "
            f"Discharge-readmission interval: {row['discharge_readmit_gap_days']} days. "
            f"Submission lag: {days_to_file} days post-discharge."
        )

    else:
        # Style D: Case referral format
        return (
            f"Insurance Fraud Referral — Medical Claim Assessment\n\n"
            f"Referral for clinical review: {row['diagnosis_description']} (ICD-10: {row['diagnosis_primary']}) "
            f"in a {row['age']}-year-old {row['gender']} patient from {row['state']} "
            f"({row['language']}-speaking). "
            f"Inpatient admission at {row['hospital_name']}, {row['hospital_city']}: "
            f"{row['date_of_admission']} to {row['date_of_discharge']} ({row['length_of_stay_days']} days). "
            f"Pre-existing conditions: {pre_existing}.\n\n"
            f"Hospital profile: {row['specialization']} facility, Tier {row['city_tier']} city. "
            f"Registry classification: {facility_status}. Blacklist status: {blacklist_str}. "
            f"Claim mode: {cashless_str} via {row['tpa']} under {row['policy_type']} cover "
            f"({policy_years}-year policy). "
            f"Claimed: INR {int(row['claim_amount_requested_inr']):,}. "
            f"Approved: INR {int(row['claim_amount_approved_inr']):,}. "
            f"Pharmacy bill share: {row['pharmacy_bill_ratio']*100:.0f}%.\n\n"
            f"Alert indicators: Procedure-diagnosis match is {icd_match_str}. "
            f"{prior_fraud_str.capitalize()}. "
            f"Insurers on record for this event: {row['num_insurers_same_event']}. "
            f"Days between discharge and readmission: {row['discharge_readmit_gap_days']}. "
            f"Claim submitted {days_to_file} days after discharge. "
            f"Identity check: {identity_str}."
        )


def build_adjudication_reasoning(row: pd.Series) -> str:
    """Build fraud-type-aware chain-of-thought reasoning from observable claim signals."""
    fraud_type = str(row["fraud_type"])
    fraud_label = int(row["fraud_label"])
    conf = float(row["fraud_confidence"])

    icd = str(row["diagnosis_primary"])
    amount_req = int(row["claim_amount_requested_inr"])
    los = int(row["length_of_stay_days"])
    days_policy = int(row["days_since_policy_start"])
    n_insurers = int(row["num_insurers_same_event"])
    icd_match = bool(row["icd_code_matches_procedure"])
    readmit_gap = int(row["discharge_readmit_gap_days"])
    pharma_ratio = float(row["pharmacy_bill_ratio"])
    blacklist = bool(row["provider_blacklist_flag"])
    prior_fraud = bool(row["previous_fraud_on_policy"])
    is_phantom = bool(row["is_phantom"])
    identity_verified = bool(row["identity_verified"])
    pre_existing = str(row["pre_existing_conditions"])

    icd_lo, icd_hi = ICD10_AMOUNTS.get(icd, (0, 999999))
    amount_ratio = amount_req / icd_hi if icd_hi > 0 else 1.0

    discharge_date = pd.Timestamp(row["date_of_discharge"])
    claim_date = pd.Timestamp(row["date_of_claim"])
    days_to_file = (claim_date - discharge_date).days

    if fraud_type == "legitimate":
        blacklist_note = "provider is not blacklisted" if not blacklist else "provider is blacklisted — escalate for audit"
        phantom_note = "facility is IRDAI-registered" if not is_phantom else "facility flagged as phantom — escalate to Rohini registry"
        return (
            f"Step 1 (Amount): The claimed amount of INR {amount_req:,} for {row['diagnosis_description']} "
            f"(ICD-10: {icd}) falls within the expected clinical cost range of INR {icd_lo:,}–{icd_hi:,} "
            f"at {amount_ratio:.2f}x the ceiling. No billing irregularity detected. PASS.\n"
            f"Step 2 (Policy): Policy has been active for {days_policy} days, indicating an established "
            f"policyholder relationship. No prior fraud recorded on this policy. "
            f"Patient identity is {'confirmed via ' + row['kyc_type'] if identity_verified else 'unverified — flag for KYC review'}. PASS.\n"
            f"Step 3 (Provider): The treating facility is {blacklist_note}, and {phantom_note}. "
            f"Provider credentials appear valid under IRDAI empanelment standards. PASS.\n"
            f"Step 4 (Clinical): The procedure billed is consistent with the stated diagnosis. "
            f"A {los}-day inpatient stay is clinically appropriate for {row['diagnosis_description']}. "
            f"Pharmacy expenditure at {pharma_ratio*100:.0f}% of total bill is within the acceptable clinical norm of 45%. PASS.\n"
            f"Step 5 (Pattern): Only {n_insurers} insurer involved — no duplicate claim risk. "
            f"Readmission interval of {readmit_gap} days is clinically normal. "
            f"Claim was submitted {days_to_file} days post-discharge, within the standard processing window. PASS.\n"
            f"Decision: APPROVE. All five clinical and procedural checks passed. "
            f"This claim presents no indicators of fraud or misrepresentation. Confidence: {conf:.2f}."
        )

    elif fraud_type == "bill_inflation":
        decision = "DENY" if conf > 0.85 else "FLAG"
        return (
            f"Step 1 (Amount): Requested INR {amount_req:,} for {icd} ({row['diagnosis_description']}). "
            f"ICD ceiling INR {icd_hi:,}. Amount is {amount_ratio:.1f}x the ceiling - significantly inflated. FAIL.\n"
            f"Step 2 (Policy): Policy age {days_policy} days. Prior fraud: {prior_fraud}. "
            f"{'Additional risk factor.' if prior_fraud else 'No prior fraud.'}\n"
            f"Step 3 (Provider): Blacklisted: {blacklist}. "
            f"{'Blacklisted provider compounds risk.' if blacklist else 'Provider not blacklisted.'}\n"
            f"Step 4 (Clinical): LOS {los} days. ICD match: {icd_match}. Pharmacy ratio {pharma_ratio:.2f}. "
            f"Bill itemisation review required.\n"
            f"Step 5 (Pattern): Amount {amount_ratio:.1f}x above ICD ceiling exceeds 1.4x flag threshold. "
            f"Consistent with systematic bill inflation.\n"
            f"Decision: {decision}. Bill inflation detected - {amount_ratio:.1f}x above ICD ceiling. Confidence: {conf:.2f}."
        )

    elif fraud_type == "phantom_provider":
        return (
            f"Step 1 (Amount): Requested INR {amount_req:,}. Amount within possible range.\n"
            f"Step 2 (Policy): Policy age {days_policy} days. Identity verified: {identity_verified}.\n"
            f"Step 3 (Provider): CRITICAL - Blacklist flag: YES. Phantom status: {is_phantom}. "
            f"Rohini ID verification failed. Hospital not found in IRDAI-empanelled registry. FAIL.\n"
            f"Step 4 (Clinical): Claim at unverified provider cannot be adjudicated on clinical merits.\n"
            f"Step 5 (Pattern): Phantom provider pattern confirmed. No legitimate services verifiable.\n"
            f"Decision: DENY. Phantom provider - not registered in Rohini. Confidence: {conf:.2f}."
        )

    elif fraud_type == "identity_fraud":
        kyc_note = "KYC not verified - additional risk." if not identity_verified else "KYC verified but inception timing remains suspicious."
        return (
            f"Step 1 (Amount): Requested INR {amount_req:,} for {icd}. Ratio {amount_ratio:.2f}x ceiling.\n"
            f"Step 2 (Policy): ALERT - Policy age only {days_policy} days (watch threshold: 90 days). "
            f"High-value claim within 90 days of policy inception is a strong identity fraud indicator. "
            f"{kyc_note} FAIL.\n"
            f"Step 3 (Provider): Blacklisted: {blacklist}. Phantom: {is_phantom}.\n"
            f"Step 4 (Clinical): Pre-existing: {pre_existing}. "
            f"{'Pre-existing conditions present - possible policy misrepresentation.' if pre_existing != 'none' else 'No declared pre-existing conditions.'}\n"
            f"Step 5 (Pattern): Inception timing (day {days_policy}) below 90-day watch window. "
            f"Refer to KYC team for identity document audit.\n"
            f"Decision: FLAG. Identity fraud suspected - policy age {days_policy} days. Confidence: {conf:.2f}."
        )

    elif fraud_type == "staged_accident":
        return (
            f"Step 1 (Amount): Requested INR {amount_req:,} for {icd} ({row['diagnosis_description']}). "
            f"Ratio {amount_ratio:.2f}x ICD ceiling.\n"
            f"Step 2 (Policy): Policy age {days_policy} days. Prior fraud: {prior_fraud}.\n"
            f"Step 3 (Provider): Blacklisted: {blacklist}. Phantom: {is_phantom}.\n"
            f"Step 4 (Clinical): ALERT - Trauma diagnosis ({icd}) with no documented prior treatment history. "
            f"LOS {los} days. Claim filed only {days_to_file} days post-discharge. "
            f"Staged accidents typically have unusually fast filing. ICD match: {icd_match}. FAIL.\n"
            f"Step 5 (Pattern): Trauma ICD + rapid filing ({days_to_file} days) consistent with staged accident. "
            f"Request FIR and police report for verification.\n"
            f"Decision: FLAG. Staged accident suspected - rapid filing after trauma claim. Confidence: {conf:.2f}."
        )

    elif fraud_type == "coordinated_ring":
        decision = "DENY" if conf >= 0.92 else "FLAG"
        return (
            f"Step 1 (Amount): Requested INR {amount_req:,}. Ratio {amount_ratio:.2f}x ICD ceiling.\n"
            f"Step 2 (Policy): Policy age {days_policy} days. Prior fraud: {prior_fraud}.\n"
            f"Step 3 (Provider): ALERT - Blacklisted: {blacklist}. "
            f"Agent {row['agent_id']} linked to multiple claims at same hospital within 30-day window. FAIL.\n"
            f"Step 4 (Clinical): {icd} LOS {los} days. ICD match: {icd_match}.\n"
            f"Step 5 (Pattern): Hospital + agent + tight admission window cluster is indicative of a coordinated ring. "
            f"Cross-reference agent {row['agent_id']} full claim history.\n"
            f"Decision: {decision}. Coordinated ring - agent/hospital clustering detected. Confidence: {conf:.2f}."
        )

    elif fraud_type == "duplicate_claim":
        return (
            f"Step 1 (Amount): Requested INR {amount_req:,} for {icd}.\n"
            f"Step 2 (Policy): Policy age {days_policy} days. Prior fraud: {prior_fraud}.\n"
            f"Step 3 (Provider): Blacklisted: {blacklist}. Phantom: {is_phantom}.\n"
            f"Step 4 (Clinical): LOS {los} days. ICD match: {icd_match}.\n"
            f"Step 5 (Pattern): CRITICAL - {n_insurers} insurers recorded for the same hospitalization event. "
            f"IRDAI prohibits multi-insurer claims for a single event without prior disclosure. FAIL.\n"
            f"Decision: DENY. Duplicate claim - {n_insurers} insurers for same event. Confidence: {conf:.2f}."
        )

    elif fraud_type == "unnecessary_procedure":
        return (
            f"Step 1 (Amount): Requested INR {amount_req:,} for {icd} ({row['diagnosis_description']}). "
            f"Ratio {amount_ratio:.2f}x ceiling.\n"
            f"Step 2 (Policy): Policy age {days_policy} days. Prior fraud: {prior_fraud}.\n"
            f"Step 3 (Provider): Blacklisted: {blacklist}. Phantom: {is_phantom}.\n"
            f"Step 4 (Clinical): ALERT - ICD {icd} does NOT match the billed procedure. "
            f"Procedure cannot be clinically justified by {row['diagnosis_description']}. "
            f"LOS {los} days. Pharmacy ratio {pharma_ratio:.2f}. FAIL.\n"
            f"Step 5 (Pattern): Diagnosis-procedure mismatch without complication coding is the hallmark of "
            f"unnecessary procedure billing. Refer to medical officer for clinical audit.\n"
            f"Decision: FLAG. Unnecessary procedure - ICD-procedure mismatch. Confidence: {conf:.2f}."
        )

    elif fraud_type == "icd_upcoding":
        decision = "DENY" if conf >= 0.80 else "FLAG"
        return (
            f"Step 1 (Amount): Requested INR {amount_req:,} for {icd} ({row['diagnosis_description']}). "
            f"ICD ceiling INR {icd_hi:,}. Amount is {amount_ratio:.1f}x ceiling - elevated. FAIL.\n"
            f"Step 2 (Policy): Policy age {days_policy} days. Prior fraud: {prior_fraud}.\n"
            f"Step 3 (Provider): Blacklisted: {blacklist}. Phantom: {is_phantom}.\n"
            f"Step 4 (Clinical): ALERT - ICD {icd} does NOT match billed procedure. "
            f"Combined with {amount_ratio:.1f}x elevated amount, consistent with upcoding - billing a "
            f"more severe diagnosis than clinically warranted. LOS {los} days. FAIL.\n"
            f"Step 5 (Pattern): Upcoding confirmed: procedure mismatch + inflated amount. "
            f"Cross-reference discharge summary with billed ICD.\n"
            f"Decision: {decision}. ICD upcoding - mismatch + {amount_ratio:.1f}x inflation. Confidence: {conf:.2f}."
        )

    elif fraud_type == "fake_policy":
        return (
            f"Step 1 (Amount): Requested INR {amount_req:,} for {icd}.\n"
            f"Step 2 (Policy): CRITICAL - Prior fraud on policy: YES. Policy age {days_policy} days (<30-day threshold). "
            f"Policy document authenticity in question. Identity: {identity_verified} via {row['kyc_type']}. FAIL.\n"
            f"Step 3 (Provider): Blacklisted: {blacklist}. Phantom: {is_phantom}.\n"
            f"Step 4 (Clinical): Cannot adjudicate clinical merits on a policy flagged as potentially forged.\n"
            f"Step 5 (Pattern): Fake policy pattern: prior fraud flag + policy age {days_policy} days. "
            f"Refer to policy issuance audit team immediately.\n"
            f"Decision: DENY. Fake policy - prior fraud + {days_policy}-day-old policy. Confidence: {conf:.2f}."
        )

    elif fraud_type == "pre_existing_hidden":
        pre_note = (
            f"Declared pre-existing: {pre_existing}."
            if pre_existing != "none"
            else "No declared pre-existing, but diagnosis pattern suggests undisclosed history."
        )
        return (
            f"Step 1 (Amount): Requested INR {amount_req:,} for {icd} ({row['diagnosis_description']}). "
            f"Ratio {amount_ratio:.2f}x ceiling.\n"
            f"Step 2 (Policy): ALERT - Policy age {days_policy} days. {pre_note} "
            f"Chronic condition claim within first {days_policy} days raises non-disclosure suspicion. FAIL.\n"
            f"Step 3 (Provider): Blacklisted: {blacklist}. Phantom: {is_phantom}.\n"
            f"Step 4 (Clinical): {icd} ({row['diagnosis_description']}) is a chronic/complex condition. "
            f"LOS {los} days. ICD match: {icd_match}.\n"
            f"Step 5 (Pattern): Pre-existing hidden: chronic diagnosis + low policy age ({days_policy} days). "
            f"Request pre-policy medical records.\n"
            f"Decision: FLAG. Pre-existing condition possibly hidden - policy age {days_policy} days. Confidence: {conf:.2f}."
        )

    elif fraud_type == "readmission_fraud":
        return (
            f"Step 1 (Amount): Requested INR {amount_req:,} for {icd}. Ratio {amount_ratio:.2f}x ceiling.\n"
            f"Step 2 (Policy): Policy age {days_policy} days. Prior fraud: {prior_fraud}.\n"
            f"Step 3 (Provider): Blacklisted: {blacklist}. Phantom: {is_phantom}.\n"
            f"Step 4 (Clinical): ALERT - Discharge-to-readmission gap is {readmit_gap} day(s). "
            f"Same-day or next-day readmission is atypical and consistent with splitting a single episode "
            f"into multiple billable events. LOS {los} days. FAIL.\n"
            f"Step 5 (Pattern): Readmit gap {readmit_gap} day(s) below 2-day threshold. "
            f"Review for duplicate episode billing.\n"
            f"Decision: FLAG. Readmission fraud - gap {readmit_gap} day(s). Confidence: {conf:.2f}."
        )

    elif fraud_type == "pharmacy_fraud":
        decision = "DENY" if conf >= 0.80 else "FLAG"
        return (
            f"Step 1 (Amount): Requested INR {amount_req:,} for {icd}. Ratio {amount_ratio:.2f}x ceiling.\n"
            f"Step 2 (Policy): Policy age {days_policy} days. Prior fraud: {prior_fraud}.\n"
            f"Step 3 (Provider): Blacklisted: {blacklist}. Phantom: {is_phantom}.\n"
            f"Step 4 (Clinical): ALERT - Pharmacy bill ratio {pharma_ratio:.2f} ({pharma_ratio*100:.0f}% of total). "
            f"Normal upper bound is 0.45 (45%). This significantly exceeds norms - suggests fabricated or "
            f"inflated pharmacy bills. LOS {los} days for {icd}. FAIL.\n"
            f"Step 5 (Pattern): Pharmacy fraud: ratio {pharma_ratio:.2f} exceeds 0.60 threshold. "
            f"Request original pharmacy receipts and prescriptions.\n"
            f"Decision: {decision}. Pharmacy fraud - ratio {pharma_ratio:.2f} ({pharma_ratio*100:.0f}%). Confidence: {conf:.2f}."
        )

    else:
        decision = "FLAG" if fraud_label == 1 else "APPROVE"
        return (
            f"Claim {row['claim_id']}: fraud_label={fraud_label}, fraud_type={fraud_type}, "
            f"confidence={conf:.2f}.\nDecision: {decision}."
        )


def prepare(
    claims_path: str,
    patients_path: str,
    hospitals_path: str,
    output_path: str,
) -> None:
    """Join, enrich, and save claims dataset ready for Adaption upload."""
    print(f"Loading {claims_path}...")
    claims = pd.read_csv(claims_path)

    print(f"Loading {patients_path}...")
    patients = pd.read_csv(patients_path)[
        [
            "patient_id", "age", "gender", "language", "state",
            "pre_existing_conditions", "identity_verified", "kyc_type",
            "number_of_claims_lifetime", "number_of_claims_last_12m",
        ]
    ]

    print(f"Loading {hospitals_path}...")
    hospitals = pd.read_csv(hospitals_path)[
        ["hospital_id", "name", "city", "tier", "specialization", "is_phantom", "blacklisted"]
    ].rename(columns={"name": "hospital_name", "city": "hospital_city", "tier": "city_tier"})

    df = claims.merge(patients, on="patient_id", how="left")
    df = df.merge(hospitals, on="hospital_id", how="left")

    print(f"Building claim_description for {len(df):,} rows...")
    df["claim_description"] = df.apply(build_claim_description, axis=1)

    print("Building adjudication_reasoning...")
    df["adjudication_reasoning"] = df.apply(build_adjudication_reasoning, axis=1)

    # Keep only the two text columns + claim_id for traceability.
    # Dropping all structured columns prevents Adaption from injecting raw CSV
    # data (bare numbers, timestamps) into the enhanced prompt, which tanks
    # quality score. fraud_label/fraud_type are also dropped to remove the
    # answer-leakage signal that reduces training quality.
    output_df = df[["claim_id", "claim_description", "adjudication_reasoning"]]

    out_dir = os.path.dirname(output_path)
    if out_dir:
        os.makedirs(out_dir, exist_ok=True)
    output_df.to_csv(output_path, index=False)

    def _safe(text: str) -> str:
        return text.encode("ascii", errors="replace").decode("ascii")

    print(f"\nSaved {len(output_df):,} rows -> {output_path}")
    print(f"Columns: {list(output_df.columns)}")
    print("\n--- Sample claim_description ---")
    print(_safe(output_df["claim_description"].iloc[0]))
    print("\n--- Sample adjudication_reasoning ---")
    print(_safe(output_df["adjudication_reasoning"].iloc[0]))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Prepare claims for Adaption upload")
    parser.add_argument("--claims", default="data/claims.csv")
    parser.add_argument("--patients", default="data/patients.csv")
    parser.add_argument("--hospitals", default="data/hospitals.csv")
    parser.add_argument("--output", default="data/claims_for_adaption.csv")
    args = parser.parse_args()

    for p in [args.claims, args.patients, args.hospitals]:
        if not os.path.exists(p):
            print(f"Error: {p} not found. Run generate_dataset.py first.")
            exit(1)

    prepare(args.claims, args.patients, args.hospitals, args.output)
