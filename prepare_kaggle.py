"""
prepare_kaggle.py
Prepare the kaggle-upload/ directory with all files needed for publishing.
Run this before `kaggle datasets create`.

Usage:
    python prepare_kaggle.py                 # uses raw claims.csv
    python prepare_kaggle.py --adapted       # uses claims_adapted.csv if available
"""

import os
import shutil
import json
import argparse


KAGGLE_DIR = "kaggle-upload"

FILES_TO_COPY = {
    "data/patients.csv": "patients.csv",
    "data/hospitals.csv": "hospitals.csv",
    "generate_dataset.py": "generate_dataset.py",
    "config.py": "config.py",
    "Readme_Kaggle.md": "README.md",
    "templates/DATA_DICTIONARY.md": "DATA_DICTIONARY.md",
}

DATASET_METADATA = {
    "title": "IndiaClaimGuard: Synthetic Indian Health Insurance Fraud Dataset (IRDAI-aligned, 100K)",
    "id": "aniketaslaliya/indiaclaimguard",
    "licenses": [{"name": "CC-BY-4.0"}],
    "keywords": [
        "insurance-fraud", "india", "healthcare", "tabular", "synthetic",
        "classification", "anomaly-detection", "rl", "finance", "icd-10", "irdai",
    ],
    "resources": [],
}


def prepare_kaggle(use_adapted: bool = False):
    """Copy all files to kaggle-upload/ and create dataset-metadata.json."""

    # Create directory
    os.makedirs(KAGGLE_DIR, exist_ok=True)
    print(f"Preparing {KAGGLE_DIR}/...")

    # Claims file (adapted or raw)
    if use_adapted and os.path.exists("data/claims_adapted.csv"):
        src = "data/claims_adapted.csv"
        print(f"  Using adapted dataset: {src}")
    else:
        src = "data/claims.csv"
        if use_adapted:
            print(f"  Adapted dataset not found, falling back to: {src}")
        else:
            print(f"  Using raw dataset: {src}")

    shutil.copy2(src, os.path.join(KAGGLE_DIR, "claims.csv"))
    print(f"  Copied {src} -> claims.csv")

    # Copy other files
    for source, dest in FILES_TO_COPY.items():
        if os.path.exists(source):
            shutil.copy2(source, os.path.join(KAGGLE_DIR, dest))
            print(f"  Copied {source} -> {dest}")
        else:
            print(f"  WARNING: {source} not found, skipping")

    # Copy documents.csv if it exists
    if os.path.exists("data/documents.csv"):
        shutil.copy2("data/documents.csv", os.path.join(KAGGLE_DIR, "documents.csv"))
        print(f"  Copied data/documents.csv -> documents.csv")

    # Copy baseline results if available
    if os.path.exists("data/baseline_results.json"):
        shutil.copy2(
            "data/baseline_results.json",
            os.path.join(KAGGLE_DIR, "baseline_results.json"),
        )
        print(f"  Copied data/baseline_results.json -> baseline_results.json")

    # Copy baseline EDA script
    if os.path.exists("notebooks/baseline_eda.py"):
        shutil.copy2(
            "notebooks/baseline_eda.py",
            os.path.join(KAGGLE_DIR, "baseline_eda.py"),
        )
        print(f"  Copied notebooks/baseline_eda.py -> baseline_eda.py")

    # Create dataset-metadata.json
    metadata_path = os.path.join(KAGGLE_DIR, "dataset-metadata.json")
    with open(metadata_path, "w") as f:
        json.dump(DATASET_METADATA, f, indent=2)
    print(f"  Created dataset-metadata.json")

    # Summary
    files = os.listdir(KAGGLE_DIR)
    print(f"\n{KAGGLE_DIR}/ ready with {len(files)} files:")
    for f in sorted(files):
        size = os.path.getsize(os.path.join(KAGGLE_DIR, f))
        print(f"  {f:35s} {size/1024:>8.1f} KB")

    print(f"\nNext steps:")
    print(f"  1. Review {KAGGLE_DIR}/dataset-metadata.json")
    print(f"  2. kaggle datasets create -p {KAGGLE_DIR}/ --dir-mode zip")
    print(f"  Or for updates:")
    print(f"  2. kaggle datasets version -p {KAGGLE_DIR}/ -m \"describe changes\"")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Prepare Kaggle upload directory")
    parser.add_argument(
        "--adapted", action="store_true",
        help="Use adapted claims.csv if available",
    )
    args = parser.parse_args()
    prepare_kaggle(args.adapted)
