"""
adaption/download_adapted.py
Download adapted dataset from Adaption after a run completes.
Usage: python adaption/download_adapted.py [--dataset-id <id>]
"""

import os
import argparse
import requests
from dotenv import load_dotenv
load_dotenv()
from adaption import Adaption


def download_adapted(dataset_id: str, output_path: str = "data/claims_adapted.csv"):
    """Download the adapted dataset from Adaption."""
    client = Adaption(api_key=os.environ["ADAPTION_API_KEY"])

    # Check status first
    print(f"Checking status for dataset: {dataset_id}")
    status = client.datasets.get_status(dataset_id)
    print(f"Status: {status.status}")

    if status.status != "succeeded":
        print(f"Dataset is not ready. Current status: {status.status}")
        if status.status == "running":
            print("Still running. Wait and try again later.")
        elif status.error:
            print(f"Error: {status.error.message}")
        return None

    # Download
    print("Downloading adapted dataset...")
    url = client.datasets.download(dataset_id)
    r = requests.get(url)
    r.raise_for_status()

    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, "wb") as f:
        f.write(r.content)

    print(f"Saved to: {output_path}")
    print(f"Size: {len(r.content) / 1024 / 1024:.1f} MB")

    # Evaluate quality
    print("\nChecking dataset quality metrics...")
    try:
        eval_status = client.datasets.get_evaluation(dataset_id)
        print(f"Quality evaluation: {eval_status}")
    except Exception as e:
        print(f"Could not retrieve evaluation: {e}")

    return output_path


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Download adapted dataset from Adaption")
    parser.add_argument(
        "--dataset-id",
        default=os.environ.get("ADAPTION_DATASET_ID"),
        help="Adaption dataset ID (default: from ADAPTION_DATASET_ID env var)",
    )
    parser.add_argument(
        "--output",
        default="data/claims_adapted.csv",
        help="Output file path (default: data/claims_adapted.csv)",
    )
    args = parser.parse_args()

    if not args.dataset_id:
        print("Error: provide --dataset-id or set ADAPTION_DATASET_ID in .env")
        exit(1)

    download_adapted(args.dataset_id, args.output)
