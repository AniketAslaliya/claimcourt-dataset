# Dataset Generator — generator.skill.md
# Rules for generating realistic Indian insurance fraud data.
# Read this before modifying any file in /generators/

---

## Entry Point
```bash
python generate_dataset.py          # sample (500 rows, fast test)
python generate_dataset.py --full   # full 100K rows
```

---

## What Each Generator Does

### patient_gen.py
Generates Indian patient profiles with:
- Regional language names (native script + romanized)
- Realistic age distribution (Gaussian mean=45, sd=18, clamp 1-95)
- State mapped to language (Hindi → UP/MP/Rajasthan, Tamil → TN/Puducherry etc.)
- KYC type realistic for India (Aadhaar most common at 60%)
- Pre-existing conditions correlated with age:
  - Under 30: conditions = "none" 90% of the time
  - 30-50: diabetes/hypertension possible
  - Over 50: higher probability of multiple conditions

### hospital_gen.py
Generates Indian hospital profiles with:
- Regional naming in local languages (see templates in LANGUAGE_POOLS)
- City tier distribution (Tier1: 30%, Tier2: 40%, Tier3: 30%)
- Rohini ID: valid format ROHINI-[1-8][0-9]{5} for real hospitals
- Phantom hospitals (8% rate): invalid/missing Rohini IDs, shorter history
- Specializations realistic for tier (cardiac/cancer skew tier1)

### claim_gen.py
Generates claims with:
- ICD-10 codes from India's top 20 health insurance diagnosis codes
- Claim amounts from realistic INR ranges per diagnosis
- Fraud type injection based on FRAUD_DISTRIBUTION weights
- Document presence/tampering patterns matching fraud type
- Processing day patterns (legitimate: 7-21 days; fraud often 2-5 days)

### fraud_gen.py
Injects realistic fraud signals:
- Each fraud type has specific column signatures (see REALISM RULES)
- Coordinated rings: groups 3-8 claims by city + 30-day window
- Confidence scores reflect how detectable each fraud type is

### document_gen.py
Generates document metadata per claim:
- doc_types: discharge_summary, bill, lab_report, prescription, pre_auth
- is_tampered: True for fraud types 1,2,8,9,12
- tamper_type: altered_amount | forged_signature | fake_letterhead | none
- upload_delay_days: fraud claims often upload faster (2-5 days vs 7-14)

---

## Full Schema Reference

### claims.csv (primary file)
```
claim_id                    str     C0000001 format
patient_id                  str     P000001 format
hospital_id                 str     H0001 format
diagnosis_primary           str     ICD-10 code (e.g., K80.2)
diagnosis_description       str     human readable
date_of_admission           date    YYYY-MM-DD
date_of_discharge           date    YYYY-MM-DD (> admission)
date_of_claim               date    YYYY-MM-DD (> discharge)
length_of_stay_days         int     1-30
claim_amount_requested_inr  int     5000-2500000
claim_amount_approved_inr   int     <= requested
policy_type                 str     individual|family|group_corporate
is_cashless                 bool    65% True
tpa                         str     Medi Assist|Paramount|Raksha|etc.
provider_blacklist_flag     bool    True for repeat fraud hospitals
previous_fraud_on_policy    bool    True if prior fraud finding
days_since_policy_start     int     calculated field
num_insurers_same_event     int     >1 = duplicate claim signal
icd_code_matches_procedure  bool    False = upcoding signal
discharge_readmit_gap_days  int     0-1 = readmission fraud signal
pharmacy_bill_ratio         float   >0.60 = pharmacy fraud signal
agent_id                    str     A001 format (links fraud rings)
fraud_label                 int     0 or 1
fraud_type                  str     from FRAUD_TYPES dict
fraud_confidence            float   0.0-1.0 (ground truth certainty)
ground_truth_source         str     rule_engine|expert_review|pattern_detection
```

### patients.csv
```
claimant_id, name, language, age, gender, state, policy_start_date,
pre_existing_conditions, number_of_claims_lifetime,
number_of_claims_last_12m, average_claim_amount,
identity_verified, kyc_type
```

### hospitals.csv
```
hospital_id, name, region, city, tier, is_phantom, rohini_id,
empanelment_date, specialization, total_claims_filed,
fraud_claims_ratio, blacklisted
```

### documents.csv
```
doc_id, claim_id, doc_type, is_present, is_tampered,
tamper_type, upload_delay_days
```

---

## ICD-10 Codes Used (India top claims)
```python
ICD10_CODES = {
    "J18.9": "Pneumonia",           "K80.2": "Gallbladder calculus",
    "I21.9": "Acute MI",            "N20.0": "Kidney calculus",
    "K35.2": "Acute appendicitis",  "O80":   "Normal delivery",
    "S72.0": "Femur fracture",      "I63.9": "Cerebral infarction",
    "K92.1": "GI bleed",            "J44.1": "COPD exacerbation",
    "N18.9": "Chronic kidney",      "E11.9": "Type 2 diabetes",
    "C34.9": "Lung cancer",         "G35":   "Multiple sclerosis",
    "M16.9": "Hip replacement",     "H26.9": "Cataract",
    "K57.3": "Diverticular disease","I10":   "Hypertension",
    "Z51.1": "Chemotherapy",        "S06.3": "Traumatic brain injury",
}
```

---

## Amount Ranges by Diagnosis (INR)
Always use these ranges. Never use random amounts.
Bill inflation fraud multiplies by 1.5-3.0x.
```python
ICD10_AMOUNTS = {
    "J18.9": (25000, 80000),    "K80.2": (80000, 200000),
    "I21.9": (150000, 500000),  "N20.0": (40000, 120000),
    "K35.2": (60000, 150000),   "O80":   (30000, 80000),
    "S72.0": (150000, 400000),  "I63.9": (100000, 350000),
    "K92.1": (30000, 90000),    "J44.1": (20000, 60000),
    "N18.9": (50000, 150000),   "E11.9": (15000, 45000),
    "C34.9": (200000, 800000),  "G35":   (80000, 250000),
    "M16.9": (180000, 450000),  "H26.9": (30000, 80000),
    "K57.3": (40000, 100000),   "I10":   (15000, 40000),
    "Z51.1": (100000, 400000),  "S06.3": (120000, 600000),
}
```

---

## Fraud Distribution (must sum to 1.0)
```python
FRAUD_DISTRIBUTION = {
    "bill_inflation":        0.25,
    "unnecessary_procedure": 0.15,
    "icd_upcoding":          0.12,
    "phantom_provider":      0.10,
    "coordinated_ring":      0.10,
    "duplicate_claim":       0.08,
    "pharmacy_fraud":        0.08,
    "readmission_fraud":     0.05,
    "staged_accident":       0.03,
    "pre_existing_hidden":   0.02,
    "identity_fraud":        0.01,
    "fake_policy":           0.01,
}
```

---

## Hospital Name Templates by Region
```python
HOSPITAL_TEMPLATES = {
    "hindi_belt": [
        "{deity} अस्पताल", "श्री {surname} मेडिकल सेंटर",
        "{city} जिला अस्पताल", "Shri {surname} Medical Centre",
        "{deity} Care Hospital", "आयुष्मान {surname} क्लिनिक",
    ],
    "south": [
        "{deity} Hospital and Research Centre",
        "Sri {surname} Multi-Speciality Hospital",
        "காந்தி மருத்துவமனை", "Vijaya {surname} Hospital",
        "ஸ்ரீ {deity} கிளினிக்", "{surname} Apollo Clinic",
    ],
    "west": [
        "{surname} Hospital Pvt Ltd", "Shree {deity} Multispeciality",
        "સર {surname} હૉસ્પિટલ", "{city} Nursing Home",
        "Wockhardt {city} Centre",
    ],
    "east": [
        "{surname} Nursing Home", "Calcutta {deity} Hospital",
        "সেবা নার্সিং হোম", "{surname} Medical College & Hospital",
    ],
    "phantom": [  # slightly off, fake-sounding
        "{city} Advanced Wellness Hub", "National {deity} Diagnostic Centre",
        "IndiaFirst HealthCare {city}", "MedPro Solutions {city}",
        "QuickHeal Clinic {city}",
    ],
}
```