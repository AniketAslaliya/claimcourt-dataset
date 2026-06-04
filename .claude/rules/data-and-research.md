# Data & Research Rules — templates/, paper, Kaggle

## Data Dictionary
- Every new field MUST be added to `templates/DATA_DICTIONARY.md` before merge.
- Field descriptions must include type, range, and example value.
- Fraud signal interpretation must be documented.

## Paper Rules (from paper.skill.md)
- No em dashes. Use commas or restructure.
- No bullet points in paper body.
- Every number must have a citation or say "in our experiments".
- Never say "novel" or "state-of-the-art" — show with numbers.
- Domain expert validation goes in Section 3.5 — always.
- Acknowledge limitations before reviewers raise them.

## Kaggle Publishing
- Run `validators/stats_check.py` before every publish.
- Dataset title: "IndiaClaimGuard: Synthetic Indian Health Insurance Fraud Dataset (IRDAI-aligned, 100K)"
- License: CC BY 4.0 always.
- Include `generate_dataset.py` in upload for reproducibility.

## README/Documentation
- Keep Kaggle README (`Readme_Kaggle.md`) and GitHub README (`README.md`) in sync.
- Baseline results section must be updated after AutoScientist run.
- Citation bibtex must use key `aslaliya2026indiaclaimguard`.
