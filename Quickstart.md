# ClaimCourt — Quickstart
From zero to published dataset in 7 days.

---

## Day 0 — Setup (30 minutes)

### 1. Create the repo
```bash
mkdir claimcourt-dataset && cd claimcourt-dataset
git init
```

### 2. Install dependencies
```bash
pip install adaption faker pandas numpy scikit-learn kaggle jupyter requests
```

### 3. Set your environment variables
```bash
cp .env.example .env
# Fill in:
# ADAPTION_API_KEY  → adaptionlabs.ai/app/settings > API Keys
# KAGGLE_KEY        → kaggle.com > Account > Create API Token
```

### 4. Test the generator
```bash
python kickstart_generator.py
# Should print: 500 rows, fraud rate ~18%, 7 languages. If that works, you are ready.
```

---

## Day 1 — Talk to Your Father

Before writing more code, do this first.
Open `templates/domain_expert_interview.md` and go through it with him.
Write his answers in a new file: `domain_expert_notes.md`

This one conversation is worth more than any code improvement.
It is Section 3.5 of your research paper. Do not skip it.

---

## Day 2-3 — Generate Full Dataset

### Scale up
Edit the bottom of `kickstart_generator.py`:
```python
generate_sample(n_patients=15000, n_hospitals=800, n_claims=100000)
```

### Run
```bash
python kickstart_generator.py
# 3-5 minutes. Output: data/claims.csv, data/patients.csv, data/hospitals.csv
```

### Validate before moving on
```bash
python validators/stats_check.py data/claims.csv
# All 9 checks must pass before you touch Adaption or Kaggle
```

---

## Day 4 — Upload to Adaption

### Upload
```bash
python adaption/upload.py --file data/claims.csv --name indiaclaimguard-v1
# Saves dataset_id to .env automatically
```

### Run reasoning traces (most important step)
```bash
python adaption/run_recipes.py --reasoning-traces
# Estimate cost first, confirm, then run
# Takes 20-60 min. Output: data/claims_adapted.csv
# These traces become chain-of-thought training data for ClaimCourt
```

### Set Blueprint rules
Go to adaptionlabs.ai/app > your dataset > Blueprint. Add:
- fraud_confidence: float, 0.0 to 1.0
- claim_amount_approved_inr: must be <= claim_amount_requested_inr
- fraud_type: must be "legitimate" when fraud_label = 0

### Run AutoScientist (free until ~June 12)
Go to adaptionlabs.ai/app/autoscientist
Select your adapted dataset, set target: fraud_label, let it run.
Screenshot the results. This is Figure 1 in your paper.

---

## Day 5 — Publish on Kaggle

### Prepare
```bash
mkdir -p kaggle-upload
cp data/claims_adapted.csv kaggle-upload/claims.csv
cp data/patients.csv kaggle-upload/
cp data/hospitals.csv kaggle-upload/
cp kickstart_generator.py kaggle-upload/
cp templates/README_kaggle.md kaggle-upload/README.md
```

### Publish
```bash
kaggle datasets init -p kaggle-upload/
# Edit kaggle-upload/datapackage.json: set title and license CC BY 4.0
kaggle datasets create -p kaggle-upload/ --dir-mode zip
```

---

## Day 6 — Write the Paper

Write in this order (not introduction first):
1. Abstract (150 words, use paper.skill.md)
2. Section 3 (dataset — you know this best)
3. Section 5 (calibration reward — your core contribution)
4. Introduction last

Submit to arXiv the moment the draft is readable.
Do not wait for perfect. A submitted paper beats a perfect draft every time.

---

## Day 7 — Go Public

### X post
```
Just published IndiaClaimGuard — first open Indian health insurance
fraud dataset aligned to IRDAI's 2025 taxonomy.

100K claims · 7 Indian languages · 12 fraud types · confidence labels
Built with @adaption_ai reasoning traces

Kaggle: [link] | Paper: [arXiv link]

@adaption_ai @SaraHooker
```

### Then start outreach
Send 5 LinkedIn messages using `templates/outreach_message.md`.
Target: claims managers at Medi Assist, Star Health, HDFC Ergo.
Do not reach out before arXiv is live. The paper is your proof.

---

## Key Files Reference

| File | When to use |
|------|-------------|
| `.skills/SKILL.md` | Paste at top of every new Claude Code session |
| `.skills/adaption.skill.md` | When working with Adaption SDK |
| `.skills/generator.skill.md` | When modifying the dataset generator |
| `.skills/paper.skill.md` | When writing or editing the paper |
| `templates/domain_expert_interview.md` | Tonight, with your father |
| `templates/outreach_message.md` | After arXiv submission |
| `validators/stats_check.py` | Before every Kaggle publish |

---

## If Something Breaks

**Fraud rate off:** Edit `TARGET_FRAUD_RATE` in config.py and re-run.

**Adaption timeout:**
```python
from adaption import Adaption; import os
client = Adaption()
print(client.datasets.get_status(os.environ["ADAPTION_DATASET_ID"]).status)
```

**Kaggle credentials error:**
```bash
chmod 600 ~/.kaggle/kaggle.json
```

**Claude Code session lost context:** Paste `.skills/SKILL.md` at the top of your message. Every rule and schema is in there.

---

## The One Rule
Talk to your father before writing more code.
His 20 years of experience is your dataset's validation story.
No code can replace that.