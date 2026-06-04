# Backend Rules — generators/, adaption/, validators/

## Generator Rules
- All tunable values MUST come from `config.py`. Never hardcode.
- Each generator module has ONE public function (e.g., `generate_patients`).
- RNG: Always accept `np.random.Generator` as parameter. Never use global random state.
- Schema: Match the field list in `.skills/generator.skill.md` exactly.
- IDs: Use zero-padded format (`P000001`, `H0001`, `C0000001`).

## Fraud Signal Rules
- `fraud_gen.py` is a POST-PROCESSING pass. It mutates claims_df, not generates from scratch.
- Each fraud type MUST have its column signature from the Realism Rules table in SKILL.md.
- Never add a fraud type without updating: config.py, fraud_gen.py, DATA_DICTIONARY.md, and the paper.

## Validation Rules
- `stats_check.py` is the gatekeeper. All 9 checks must pass before any publish.
- Never modify the checker to make tests pass. Fix the generators instead.

## Adaption SDK Rules
- Always estimate cost before running (`estimate=True`).
- Always save `dataset_id` to `.env` after upload.
- Handle `DatasetTimeout` gracefully with manual check instructions.

## Python Conventions
- Type hints on all function signatures.
- Google-style docstrings.
- `print()` must use ASCII only (Windows cp1252).
- No `from config import *` — import specific names.
