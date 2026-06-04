"""
adaption/run_recipes.py
Run Adaptive Data recipes on your uploaded dataset.
Primary recipe: reasoning_traces (chain-of-thought for each adjudication)
Usage: python adaption/run_recipes.py --dataset-id <id> --reasoning-traces
"""

import os
import argparse
import requests
from adaption import Adaption, DatasetTimeout


def run_adaptation(dataset_id: str, reasoning_traces: bool = True):
    client = Adaption(api_key=os.environ["ADAPTION_API_KEY"])

    # Step 1: Estimate cost first
    print("Estimating cost...")
    estimate = client.datasets.run(
        dataset_id,
        column_mapping={
            "prompt": "claim_description",
            "completion": "adjudication_reasoning",
        },
        estimate=True,
    )
    print(f"Estimated: {estimate.estimated_credits_consumed} credits, ~{estimate.estimated_minutes} min")
    confirm = input("Proceed? (y/n): ")
    if confirm.lower() != "y":
        print("Cancelled.")
        return

    # Step 2: Build recipe
    recipes = {}
    if reasoning_traces:
        recipes["reasoning_traces"] = True
        print("Reasoning traces: ON (chain-of-thought per claim decision)")
    recipes["deduplication"] = True

    # Step 3: Run
    print("Starting adaptation run...")
    run = client.datasets.run(
        dataset_id,
        column_mapping={
            "prompt": "claim_description",
            "completion": "adjudication_reasoning",
        },
        recipe_specification={"recipes": recipes},
    )
    print(f"Run started: {run.run_id}")

    # Step 4: Wait
    print("Waiting for completion (this takes 20-60 min for 100K rows)...")
    try:
        final = client.datasets.wait_for_completion(dataset_id, timeout=7200)
        print(f"Status: {final.status}")
        if final.error:
            raise RuntimeError(f"Run failed: {final.error.message}")
    except DatasetTimeout:
        print("Timed out. Check status manually:")
        print(f"  python -c \"from adaption import Adaption; c=Adaption(); print(c.datasets.get_status('{dataset_id}').status)\"")
        return

    # Step 5: Download
    print("Downloading adapted dataset...")
    url = client.datasets.download(dataset_id)
    r = requests.get(url)
    output_path = "data/claims_adapted.csv"
    with open(output_path, "wb") as f:
        f.write(r.content)
    print(f"Saved to: {output_path}")
    print("Done. The adapted dataset contains reasoning traces per claim decision.")
    print("Use this for ClaimCourt RL training — the traces are your chain-of-thought data.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--dataset-id", default=os.environ.get("ADAPTION_DATASET_ID"))
    parser.add_argument("--reasoning-traces", action="store_true", default=True)
    args = parser.parse_args()

    if not args.dataset_id:
        print("Error: provide --dataset-id or set ADAPTION_DATASET_ID in .env")
        exit(1)

    run_adaptation(args.dataset_id, args.reasoning_traces)
