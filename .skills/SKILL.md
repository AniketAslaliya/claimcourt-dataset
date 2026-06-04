# ClaimCourt Dataset — SKILL.md
# Drop this at the top of any Claude Code session for this project.
# It tells Claude exactly how everything works so you never repeat yourself.

## Project
IndiaClaimGuard: Synthetic Indian health insurance fraud dataset.
100K claims, 7 Indian languages, IRDAI-aligned fraud taxonomy,
confidence labels, reasoning traces via Adaption.

## Repo Structure
```
claimcourt-dataset/
├── PLAN.md                       # master strategy
├── .skills/
│   ├── SKILL.md                  # this file
│   ├── adaption.skill.md         # Adaption API patterns
│   ├── generator.skill.md        # dataset generation rules
│   └── paper.skill.md            # research paper conventions
├── generate_dataset.py           # main generator (entry point)
├── config.py                     # all tunable parameters
├── generators/
│   ├── patient_gen.py
│   ├── hospital_gen.py
│   ├── claim_gen.py
│   ├── document_gen.py
│   └── fraud_gen.py
├── validators/
│   └── stats_check.py
├── adaption/
│   ├── upload.py                 # upload to Adaption
│   ├── run_recipes.py            # run adaptation jobs
│   └── download_adapted.py      # download results
├── data/                         # generated CSVs (gitignored)
├── kaggle-upload/                # final export
├── templates/
│   ├── README_kaggle.md          # dataset card template
│   ├── DATA_DICTIONARY.md        # field documentation
│   └── outreach_message.md       # cold outreach template
└── notebooks/
    └── baseline_eda.ipynb
```

## Core Rules (never change without reason)

### Fraud Rate
Target: 18% (IRDAI estimate). Tolerance ±2%.
Fix fraud rate drift in `config.py → TARGET_FRAUD_RATE`, not elsewhere.

### Fraud Taxonomy (12 types, IRDAI-aligned)
```
0  = legitimate
1  = bill_inflation          (real admission, inflated charges)
2  = phantom_provider        (hospital never existed or never visited)
3  = identity_fraud          (policy on someone else's name)
4  = staged_accident         (fabricated incident)
5  = coordinated_ring        (multiple claimants, same provider, same window)
6  = duplicate_claim         (same event, multiple insurers)
7  = unnecessary_procedure   (real admission, procedures never done)
8  = icd_upcoding            (real admission, expensive code substituted)
9  = fake_policy             (policy document itself is forged)
10 = pre_existing_hidden     (condition existed before policy start)
11 = readmission_fraud       (discharged and readmitted same day)
12 = pharmacy_fraud          (medicines billed, never dispensed)
```

### Language Weights (population-representative)
```python
LANGUAGE_WEIGHTS = {
    "hindi": 0.30, "marathi": 0.12, "telugu": 0.12,
    "tamil": 0.15, "bengali": 0.10, "gujarati": 0.10, "punjabi": 0.11
}
# Must sum to 1.0. Never change without updating state mappings too.
```

### Confidence Labels (core research contribution — never remove)
```python
CONFIDENCE_RANGES = {
    "legitimate":            (0.75, 0.99),
    "bill_inflation":        (0.65, 0.95),
    "phantom_provider":      (0.85, 0.99),
    "identity_fraud":        (0.70, 0.92),
    "staged_accident":       (0.55, 0.85),
    "coordinated_ring":      (0.80, 0.98),
    "duplicate_claim":       (0.88, 0.99),
    "unnecessary_procedure": (0.50, 0.80),
    "icd_upcoding":          (0.60, 0.88),
    "fake_policy":           (0.80, 0.97),
    "pre_existing_hidden":   (0.55, 0.82),
    "readmission_fraud":     (0.75, 0.95),
    "pharmacy_fraud":        (0.65, 0.90),
}
```

### Reward Function (paper core contribution — never change without paper update)
```
R(action, confidence) =
  +1.0  correct AND well-calibrated
  +0.3  correct AND overconfident
   0.0  incorrect AND uncertain
  -0.8  incorrect AND overconfident
  -0.3  escalated to human (valid conservative move)
```

---

## Common Tasks

### Add a new language
1. Add to `LANGUAGE_POOLS` in `generators/patient_gen.py`
   Include both native script names AND romanized names
   Map to realistic states in `"states"` key
2. Add weight in `config.py → LANGUAGE_WEIGHTS` (must sum to 1.0)
3. Add hospital name templates for that region in `generators/hospital_gen.py`
4. Run generator, verify new language in stats output
5. Update DATA_DICTIONARY.md language section

### Add a new fraud type
1. Add to `FRAUD_TYPES` dict (new int key + snake_case value)
2. Add confidence range to `CONFIDENCE_RANGES`
3. Add weight to `FRAUD_DISTRIBUTION` (adjust others, must sum to 1.0)
4. Add realism rule in `generators/fraud_gen.py`:
   - what document signals does this fraud type produce?
   - what amount pattern does it follow?
   - what timing pattern? (days since policy start, processing speed)
5. Update DATA_DICTIONARY.md fraud type table
6. Update paper fraud taxonomy section

### Scale to 100K rows
Edit `config.py`:
```python
N_PATIENTS = 15000
N_HOSPITALS = 800
N_CLAIMS = 100000
```
Then: `python generate_dataset.py`
Expected runtime: 3-5 minutes.

### Validate before publishing
```bash
python validators/stats_check.py data/claims.csv
```
All checks must pass:
- ✓ Fraud rate 18% ±2%
- ✓ No nulls in required fields
- ✓ date_of_discharge > date_of_admission
- ✓ claim_amount_approved <= claim_amount_requested
- ✓ All ICD codes valid ICD-10 format
- ✓ fraud_confidence between 0.0 and 1.0
- ✓ fraud_type = "legitimate" when fraud_label = 0
- ✓ 7 languages present
- ✓ Phantom hospitals have invalid Rohini IDs

### Upload to Adaption
```bash
python adaption/upload.py --file data/claims.csv --name indiaclaimguard-v1
# Prints dataset_id — save this to .env as ADAPTION_DATASET_ID
```

### Run reasoning traces on Adaption
```bash
python adaption/run_recipes.py --dataset-id $ADAPTION_DATASET_ID --reasoning-traces
# Takes 20-60 min for 100K rows. Downloads to data/claims_adapted.csv
```

### Publish to Kaggle
```bash
# First time only:
kaggle datasets init -p kaggle-upload/
# Edit kaggle-upload/datapackage.json (title, license CC BY 4.0)
kaggle datasets create -p kaggle-upload/ --dir-mode zip

# Updates:
kaggle datasets version -p kaggle-upload/ -m "describe what changed"
```

---

## Realism Rules (enforced in code)

| Fraud Type          | Signal in Data                                           |
|--------------------|----------------------------------------------------------|
| bill_inflation     | claim_amount 1.5-3x realistic range; docs tampered       |
| phantom_provider   | rohini_id invalid; hospital_registered=False             |
| identity_fraud     | policy_age_days < 90; kyc_verified = False               |
| staged_accident    | ICD = trauma codes; no prior medical history             |
| coordinated_ring   | 3-8 claims, same hospital_id, same 30-day window         |
| duplicate_claim    | num_insurers_same_event > 1                              |
| unnecessary_proc   | procedure_code mismatch with diagnosis severity          |
| icd_upcoding       | icd_code_matches_procedure = False; amount inflated      |
| readmission_fraud  | discharge_readmit_gap_days = 0 or 1                      |
| pharmacy_fraud     | pharmacy_bill_ratio > 0.60 (abnormally high)             |
| fake_policy        | policy document tampered; agent_fraud_flag = True        |
| pre_existing_hidden| condition in history contradicts claimed onset date      |

---

## Environment Variables
```bash
ADAPTION_API_KEY=pt_live_...        # from adaptionlabs.ai/app/settings
ADAPTION_DATASET_ID=...             # set after first upload
KAGGLE_USERNAME=...                 # from kaggle.json
KAGGLE_KEY=...                      # from kaggle.json
```

## Dependencies
```bash
pip install adaption faker pandas numpy scikit-learn kaggle jupyter
```