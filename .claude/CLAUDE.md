# ClaimCourt Dataset — CLAUDE.md

## Project Identity
**IndiaClaimGuard**: Synthetic Indian health insurance fraud dataset (IRDAI-aligned).
**CalibFraud**: Research paper on calibrated RL for claim adjudication.
**ClaimCourt**: The trained RL agent model.

## Architecture
```
generate_dataset.py  →  config.py + generators/  →  data/*.csv
                                                       ↓
                                              adaption/upload.py → Adaption Platform
                                              adaption/run_recipes.py → reasoning traces
                                                       ↓
                                              validators/stats_check.py → 9-check validation
```

## Key Constraints (NEVER violate)
- **Fraud rate**: 18% +/- 2% (IRDAI estimate). Fix drift in `config.py`, nowhere else.
- **Fraud taxonomy**: 12 types + legitimate. IRDAI 2025 aligned. Do NOT add/remove without updating paper.
- **Confidence labels**: Core research contribution. Range per type defined in `config.py → CONFIDENCE_RANGES`.
- **Language weights**: 7 languages, must sum to 1.0. Never change without updating state mappings.
- **Reward function**: Paper's core contribution. Never change without paper update.
- **Date ordering**: admission < discharge < claim. Always.
- **Amount ordering**: approved <= requested. Always.

## Code Style
- Python 3.11+
- Type hints on all function signatures
- Docstrings on all public functions (Google style)
- No hardcoded values — everything in `config.py`
- ASCII-only in print statements (Windows cp1252 compatibility)

## File Conventions
- CSV IDs: `P000001` (patients), `H0001` (hospitals), `C0000001` (claims), `D0000001` (documents), `A001` (agents)
- Dates: YYYY-MM-DD string format
- Amounts: integer INR (no paise)
- Booleans: True/False (Python native)

## Common Workflows
- **Generate sample**: `python generate_dataset.py` (500 rows, fast test)
- **Generate full**: `python generate_dataset.py --full` (100K rows, 3-5 min)
- **Validate**: `python validators/stats_check.py data/claims.csv`
- **Upload to Adaption**: `python adaption/upload.py --file data/claims.csv`
- **Run reasoning traces**: `python adaption/run_recipes.py --reasoning-traces`

## Dependencies
```
faker, pandas, numpy, scikit-learn, kaggle, jupyter, requests, adaption
```

## Environment Variables
```
ADAPTION_API_KEY, ADAPTION_DATASET_ID, KAGGLE_USERNAME, KAGGLE_KEY
```
