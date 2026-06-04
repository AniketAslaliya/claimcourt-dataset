# Skill: Adaption Platform Integration

## Description
Upload dataset to Adaption, run reasoning traces, download adapted data.

## Prerequisites
- `ADAPTION_API_KEY` set in `.env`
- `data/claims.csv` exists and passes all 9 validation checks

## Steps

### 1. Upload
```bash
python adaption/upload.py --file data/claims.csv --name indiaclaimguard-v1
```
Saves `ADAPTION_DATASET_ID` to `.env` automatically.

### 2. Set Blueprint (manual, in web UI)
Go to adaptionlabs.ai/app > your dataset > Blueprint. Add:
- fraud_confidence: float, 0.0 to 1.0
- claim_amount_approved_inr: must be <= claim_amount_requested_inr
- fraud_type: must be "legitimate" when fraud_label = 0

### 3. Run Reasoning Traces
```bash
python adaption/run_recipes.py --reasoning-traces
```
- Estimates cost first, asks for confirmation
- Takes 20-60 min for 100K rows
- Downloads to `data/claims_adapted.csv`

### 4. Run AutoScientist (web UI)
- Go to adaptionlabs.ai/app/autoscientist
- Select adapted dataset, target: fraud_label
- Screenshot results for Figure 1 in paper

## Troubleshooting
```python
from adaption import Adaption; import os
client = Adaption()
print(client.datasets.get_status(os.environ["ADAPTION_DATASET_ID"]).status)
```

## Reference Files
- `.skills/adaption.skill.md` — API patterns
- `adaption/upload.py` — upload script
- `adaption/run_recipes.py` — recipe runner
