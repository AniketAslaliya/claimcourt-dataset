# Adaption Platform — adaption.skill.md
# Reference for all Adaption API usage in this project.
# Based on docs.adaptionlabs.ai (read June 2026)

## Install and Auth
```bash
pip install adaption
export ADAPTION_API_KEY=pt_live_...
```

```python
from adaption import Adaption
client = Adaption()  # reads ADAPTION_API_KEY from env
```

---

## Upload Patterns

### Local CSV (primary method)
```python
result = client.datasets.upload_file("data/claims.csv", name="indiaclaimguard-v1")
dataset_id = result.dataset_id
# Wait for processing before running
import time
while True:
    status = client.datasets.get_status(dataset_id)
    if status.row_count is not None:
        break
    time.sleep(2)
print(f"Ready: {status.row_count} rows")
```

### From Kaggle (after publishing there)
```python
response = client.datasets.create_from_kaggle(
    url="https://www.kaggle.com/datasets/aniketaslaliya/indiaclaimguard",
    files=["claims.csv"],
)
# Async — wait before running
```

### From HuggingFace
```python
response = client.datasets.create_from_huggingface(
    url="https://huggingface.co/datasets/AniketAsla/indiaclaimguard",
    files=["claims.csv"],
)
```

---

## Run Patterns

### Always estimate first
```python
estimate = client.datasets.run(
    dataset_id,
    column_mapping={"prompt": "claim_description", "completion": "adjudication_reasoning"},
    estimate=True,
)
print(f"Cost: {estimate.estimated_credits_consumed} credits, ~{estimate.estimated_minutes} min")
```

### Full run with reasoning traces (primary ClaimCourt recipe)
```python
run = client.datasets.run(
    dataset_id,
    column_mapping={
        "prompt": "claim_description",        # the claim text/context
        "completion": "adjudication_reasoning", # the decision + reasoning
    },
    recipe_specification={
        "recipes": {
            "reasoning_traces": True,   # chain-of-thought per decision
            "deduplication": True,      # remove near-duplicate patterns
        }
    },
)
print(f"Run ID: {run.run_id}")
```

### Wait and handle timeout
```python
from adaption import DatasetTimeout
try:
    final = client.datasets.wait_for_completion(dataset_id, timeout=3600)
    print(f"Done: {final.status}")
    if final.error:
        raise RuntimeError(final.error.message)
except DatasetTimeout:
    # Job still running — check manually later
    status = client.datasets.get_status(dataset_id)
    print(f"Status: {status.status}")
```

### Download results
```python
url = client.datasets.download(dataset_id)
# url is presigned S3 link — download with requests or wget
import requests
r = requests.get(url)
with open("data/claims_adapted.csv", "wb") as f:
    f.write(r.content)
print("Downloaded adapted dataset")
```

---

## Blueprint (quality specification)
Set in the Adaption web UI at adaptionlabs.ai/app after upload.

Rules to set for IndiaClaimGuard:
- fraud_confidence: must be float between 0.0 and 1.0
- claim_amount_approved: must be <= claim_amount_requested
- rohini_id: phantom hospitals must not match format ROHINI-[1-8][0-9]{5}
- fraud_type: must be "legitimate" when fraud_label = 0

Blueprint is a structural constraint, not a filter. It enforces these
during the adaptation run so violations are corrected, not just flagged.

---

## Forge (for real documents later)
When you get real (anonymized) claim documents from your father or a TPA:

1. Go to adaptionlabs.ai/app
2. Upload PDFs, scans, or discharge summaries directly
3. Forge extracts fields automatically, no preprocessing needed
4. Maps to your schema via column_mapping in the run
5. Merge extracted real-structure data with synthetic rows

This is the upgrade path from pure synthetic to semi-real.
Do this after initial Kaggle publish. Version the dataset.

---

## AutoScientist (model training)

After your adapted dataset is ready:
1. Go to adaptionlabs.ai/app/autoscientist
2. Select your adapted claims dataset
3. Set target: fraud_label (binary)
4. Optional secondary target: fraud_type (multiclass)
5. Let it run — it self-optimizes data and training recipe together

AutoScientist is free for 30 days from May 13, 2026.
Screenshot Figure 1: win-rate curve across dataset sizes.
This becomes the baseline result in your paper.

---

## Evaluate Dataset Quality
```python
eval_status = client.datasets.get_evaluation(dataset_id)
print(eval_status)
# Check quality metrics after a run completes
# Document these numbers in paper Section 3 (Dataset)
```

---

## List All Your Datasets
```python
for dataset in client.datasets.list(status="succeeded"):
    print(f"{dataset.dataset_id} — {dataset.name} — {dataset.status}")
```

---

## Key Notes
- dataset_id persists across sessions — save to .env
- Reasoning traces are the most important recipe for ClaimCourt
- Blueprint rules run during adaptation, not as post-processing
- AutoScientist is free for 30 days (ends ~June 12, 2026 — use immediately)
- Forge is available to all Adaptive Data users (you have grantee access)
- 242 language coverage means your Hindi/Tamil/Telugu data is fully supported