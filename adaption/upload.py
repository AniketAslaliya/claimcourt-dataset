"""
adaption/upload.py
Upload claims.csv to Adaption and save dataset_id to .env
Usage: python adaption/upload.py --file data/claims.csv --name indiaclaimguard-v1
"""

import os
import time
import argparse
from adaption import Adaption


def upload_dataset(file_path: str, name: str):
    client = Adaption(api_key=os.environ["ADAPTION_API_KEY"])

    print(f"Uploading {file_path} as '{name}'...")
    result = client.datasets.upload_file(file_path, name=name)
    dataset_id = result.dataset_id
    print(f"Dataset ID: {dataset_id}")

    print("Waiting for file processing...")
    while True:
        status = client.datasets.get_status(dataset_id)
        if status.row_count is not None:
            break
        time.sleep(2)

    print(f"Ready: {status.row_count} rows")

    # Save dataset_id to .env for future use
    env_path = ".env"
    lines = []
    if os.path.exists(env_path):
        with open(env_path) as f:
            lines = [l for l in f.readlines() if not l.startswith("ADAPTION_DATASET_ID")]
    lines.append(f"ADAPTION_DATASET_ID={dataset_id}\n")
    with open(env_path, "w") as f:
        f.writelines(lines)
    print(f"Saved to .env: ADAPTION_DATASET_ID={dataset_id}")

    return dataset_id


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--file", default="data/claims.csv")
    parser.add_argument("--name", default="indiaclaimguard-v1")
    args = parser.parse_args()
    upload_dataset(args.file, args.name)
