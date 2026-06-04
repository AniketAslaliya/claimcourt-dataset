"""
generators package
Synthetic data generators for IndiaClaimGuard dataset.
"""

from generators.patient_gen import generate_patients
from generators.hospital_gen import generate_hospitals
from generators.claim_gen import generate_claims
from generators.fraud_gen import inject_fraud_signals
from generators.document_gen import generate_documents

__all__ = [
    "generate_patients",
    "generate_hospitals",
    "generate_claims",
    "inject_fraud_signals",
    "generate_documents",
]
