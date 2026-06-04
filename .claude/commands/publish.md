# /publish — Prepare and publish to Kaggle

Prepare the kaggle-upload directory and publish the dataset.

## Steps
1. Verify `data/claims.csv` exists and passes all 9 validation checks
2. Create `kaggle-upload/` directory
3. Copy files:
   - `data/claims_adapted.csv` -> `kaggle-upload/claims.csv` (or `data/claims.csv` if adapted not ready)
   - `data/patients.csv` -> `kaggle-upload/`
   - `data/hospitals.csv` -> `kaggle-upload/`
   - `generate_dataset.py` -> `kaggle-upload/`
   - `Readme_Kaggle.md` -> `kaggle-upload/README.md`
4. Run `kaggle datasets init -p kaggle-upload/`
5. Edit `datapackage.json` with title and CC BY 4.0 license
6. Run `kaggle datasets create -p kaggle-upload/ --dir-mode zip`

## Prerequisites
- KAGGLE_USERNAME and KAGGLE_KEY in `.env`
- All validation checks passing
