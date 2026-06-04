# IndiaClaimGuard

**Synthetic Indian Health Insurance Fraud Dataset — IRDAI-aligned**

100,000 claims · 7 Indian languages · 12 fraud types · Confidence labels · Reasoning traces

---

## What This Is

IndiaClaimGuard is the first open-source Indian health insurance fraud dataset
aligned to IRDAI's 2025 fraud taxonomy. It serves as the benchmark dataset
for the CalibFraud research paper, which introduces a calibrated reinforcement
learning approach to insurance claim adjudication.

**The core insight:** A model that is wrong and uncertain is far less dangerous
than one that is wrong and certain. IndiaClaimGuard includes ground-truth
confidence labels (`fraud_confidence`) that enable training models that know
when they don't know.

## Quick Start

```bash
# Clone
git clone git@github.com:AniketAslaliya/claimcourt-dataset.git
cd claimcourt-dataset

# Install
pip install -r requirements.txt

# Generate sample (500 rows, ~10 seconds)
python generate_dataset.py

# Generate full dataset (100K rows, ~3-5 minutes)
python generate_dataset.py --full

# Validate
python validators/stats_check.py data/claims.csv
```

## Repo Structure

```
claimcourt-dataset/
├── generate_dataset.py           # Main entry point
├── config.py                     # All tunable parameters
├── generators/
│   ├── patient_gen.py            # Indian patient profiles (7 languages)
│   ├── hospital_gen.py           # Hospital profiles + phantom injection
│   ├── claim_gen.py              # Claims with ICD-10 codes + INR amounts
│   ├── fraud_gen.py              # Fraud signal injection (12 types)
│   └── document_gen.py           # Document metadata + tampering
├── validators/
│   └── stats_check.py            # 9-check validation suite
├── adaption/
│   ├── upload.py                 # Upload to Adaption platform
│   └── run_recipes.py            # Run reasoning traces
├── .skills/
│   ├── SKILL.md                  # Project context (paste in AI sessions)
│   ├── generator.skill.md        # Generator rules
│   ├── adaption.skill.md         # Adaption API patterns
│   └── paper.skill.md            # Paper conventions
├── templates/
│   ├── domain_expert_interview.md
│   ├── outreach_message.md
│   └── DATA_DICTIONARY.md
├── data/                         # Generated CSVs (gitignored)
├── plan.md                       # Master strategy
└── Quickstart.md                 # 7-day execution guide
```

## Dataset Schema

### claims.csv (primary — 100K rows)
26 fields including `fraud_label`, `fraud_type`, `fraud_confidence`,
and fraud-specific signal columns. See [DATA_DICTIONARY.md](templates/DATA_DICTIONARY.md).

### patients.csv (~15K rows)
Indian patient profiles with regional names in native scripts and romanized forms.

### hospitals.csv (~800 rows)
Hospital profiles with Rohini IDs, phantom flags, and regional naming.

### documents.csv (~500K rows)
Document metadata per claim with tampering flags correlated to fraud types.

## Fraud Taxonomy (12 types, IRDAI-aligned)

| Code | Type | % of Fraud |
|------|------|-----------|
| 1 | bill_inflation | 25% |
| 2 | phantom_provider | 10% |
| 3 | identity_fraud | 1% |
| 4 | staged_accident | 3% |
| 5 | coordinated_ring | 10% |
| 6 | duplicate_claim | 8% |
| 7 | unnecessary_procedure | 15% |
| 8 | icd_upcoding | 12% |
| 9 | fake_policy | 1% |
| 10 | pre_existing_hidden | 2% |
| 11 | readmission_fraud | 5% |
| 12 | pharmacy_fraud | 8% |

## The Calibration Reward

```
R(action, confidence) =
  +1.0  correct AND well-calibrated
  +0.3  correct AND overconfident
   0.0  incorrect AND uncertain
  -0.8  incorrect AND overconfident
  -0.3  escalated to human (valid conservative move)
```

## Stack

- **Generator:** Python (Faker + NumPy + Pandas)
- **Adaptation:** [Adaption](https://adaptionlabs.ai) — reasoning traces + quality improvement
- **Publishing:** Kaggle + arXiv
- **Model:** ClaimCourt (calibrated RL agent)

## Paper

**CalibFraud: A Calibrated Reinforcement Learning Benchmark for
Sequential Insurance Claim Adjudication in India**

Target venues: arXiv → AAAI 2026 AI in Finance → NeurIPS 2026 Datasets Track

## License

CC BY 4.0 — Free for research and commercial use with attribution.

## Citation

```bibtex
@dataset{aslaliya2026indiaclaimguard,
  title={IndiaClaimGuard: Synthetic Indian Health Insurance Fraud Dataset},
  author={Aslaliya, Aniket},
  year={2026},
  url={https://www.kaggle.com/datasets/aniketaslaliya/indiaclaimguard},
  note={IRDAI-aligned, 100K claims, 7 Indian languages, 12 fraud types}
}
```
