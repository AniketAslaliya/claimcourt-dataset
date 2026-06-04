# Skill: Dataset Generation & Validation

## Description
Generate, validate, and iterate on the IndiaClaimGuard synthetic dataset.

## Steps

### 1. Generate
```bash
python generate_dataset.py          # sample (500 rows)
python generate_dataset.py --full   # full (100K rows)
```

### 2. Validate
```bash
python validators/stats_check.py data/claims.csv
```
All 9 checks must pass:
- Fraud rate 18% +/-2%
- No nulls in required fields
- date_of_discharge >= date_of_admission
- date_of_claim >= date_of_discharge
- claim_amount_approved <= claim_amount_requested
- fraud_confidence in [0.0, 1.0]
- fraud_type='legitimate' when fraud_label=0
- All 13 fraud types present
- ICD codes valid format

### 3. If checks fail
- Fraud rate off: Edit `TARGET_FRAUD_RATE` in `config.py`
- Missing fraud types: Check `FRAUD_DISTRIBUTION` weights and sample size
- Date issues: Fix in `generators/claim_gen.py`
- Amount issues: Fix in `generators/fraud_gen.py` (bill inflation multiplier)

### 4. Iterate
Re-run generate + validate until all 9 pass. Only then proceed to Adaption upload.

## Reference Files
- `config.py` — all tunable parameters
- `.skills/generator.skill.md` — detailed generator rules
- `templates/DATA_DICTIONARY.md` — field documentation
