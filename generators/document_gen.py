"""
generators/document_gen.py
Generate document metadata per claim.
Each claim has 4-5 documents (discharge summary, bill, lab report,
prescription, pre-authorization). Tampering flags match fraud types.
"""

import numpy as np
import pandas as pd


# Document types and their base presence probability
DOC_TYPES = {
    "discharge_summary": 0.98,
    "bill":              0.99,
    "lab_report":        0.85,
    "prescription":      0.80,
    "pre_auth":          0.65,
}

# Fraud types that produce tampered documents
TAMPERED_FRAUD_TYPES = {
    "bill_inflation",
    "phantom_provider",
    "icd_upcoding",
    "fake_policy",
    "pharmacy_fraud",
}

# Tamper type per fraud type
TAMPER_TYPE_MAP = {
    "bill_inflation":   ["altered_amount", "altered_amount", "forged_signature"],
    "phantom_provider": ["fake_letterhead", "forged_signature", "fake_letterhead"],
    "icd_upcoding":     ["altered_amount", "forged_signature"],
    "fake_policy":      ["forged_signature", "fake_letterhead", "altered_amount"],
    "pharmacy_fraud":   ["altered_amount", "altered_amount"],
}


def generate_documents(
    claims_df: pd.DataFrame,
    rng: np.random.Generator,
) -> pd.DataFrame:
    """Generate document metadata for each claim."""
    records = []
    doc_counter = 0

    for _, claim in claims_df.iterrows():
        claim_id = claim["claim_id"]
        fraud_type = claim["fraud_type"]
        fraud_label = claim["fraud_label"]

        for doc_type, presence_prob in DOC_TYPES.items():
            doc_counter += 1
            doc_id = f"D{doc_counter:07d}"

            # Is document present?
            is_present = rng.random() < presence_prob

            # Tampering
            is_tampered = False
            tamper_type = "none"

            if fraud_label == 1 and fraud_type in TAMPERED_FRAUD_TYPES and is_present:
                # High probability of tampering for these fraud types
                if rng.random() < 0.75:
                    is_tampered = True
                    tamper_options = TAMPER_TYPE_MAP.get(fraud_type, ["altered_amount"])
                    tamper_type = rng.choice(tamper_options)

            # Upload delay
            if fraud_label == 1:
                upload_delay = int(rng.integers(1, 6))   # 1-5 days (faster)
            else:
                upload_delay = int(rng.integers(5, 15))  # 5-14 days (normal)

            records.append({
                "doc_id": doc_id,
                "claim_id": claim_id,
                "doc_type": doc_type,
                "is_present": is_present,
                "is_tampered": is_tampered,
                "tamper_type": tamper_type,
                "upload_delay_days": upload_delay,
            })

    return pd.DataFrame(records)
