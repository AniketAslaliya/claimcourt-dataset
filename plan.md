# ClaimCourt Dataset — Master Plan
**Goal:** Build IndiaClaimGuard, the first IRDAI-aligned synthetic Indian
health insurance fraud dataset. Publish on Kaggle. Use Adaption to adapt,
enrich, and train a model. Submit a research paper. Then approach HDFC,
Star Health, IRDAI with a real product backed by published work.

---

## The Stack (understand this first)

```
Your Generator (Python)
    ↓ generates raw 100K CSV
Adaption Adaptive Data
    ↓ cleans, adapts, adds reasoning traces via Blueprint
Adaption AutoScientist
    ↓ trains your model automatically (no PhD needed)
Kaggle
    ↓ public dataset published with baseline notebook
arXiv + Conference
    ↓ paper submitted
IRDAI / HDFC / Star Health
    ↓ product conversation with published proof
```

---

## Adaption Platform — What Each Tool Does For You

### Adaptive Data (use first)
Upload your generated CSV. The platform cleans it, detects issues,
and lets you run "recipes" on top of it to improve quality.
82% quality gain reported on average. This is how you go from
good synthetic data to near-real synthetic data.

Key recipes to use on your dataset:
- `reasoning_traces: True` — adds chain-of-thought reasoning to each
  claim investigation decision. This becomes training data for ClaimCourt's
  step-by-step adjudication agent. This is critical.
- `deduplication: True` — removes near-duplicate claim patterns
- `prompt_rephrase: True` — diversifies claim descriptions

### Blueprint (use for quality control)
Specification layer. You define rules, platform enforces them on
every data point. For ClaimCourt, your Blueprint rules are:
- ICD code must match procedure code
- Claim amount must be within realistic range for diagnosis
- Phantom hospitals must never have valid Rohini IDs
- Fraud confidence must match fraud type ranges
Blueprint makes these structural, not just comments in code.

### Forge (use when you get real documents)
When your father shares real claim documents (anonymized), or when
you get even one sample discharge summary or bill — feed it to Forge.
Forge accepts raw PDFs, scans, and docs with no preprocessing needed.
It extracts and maps to your schema automatically.
This is how synthetic becomes semi-real.

### AutoScientist (use last, after data is ready)
Point it at your adapted dataset, tell it the target column (fraud_label),
and it runs the full training loop automatically. Co-optimizes data and
model recipe together. Outperforms human-configured training by 35% on average.
This is how you get a trained model without needing to babysit hyperparameters.

---

## Phase 1 — Generate (Week 1)

**Goal:** 100K rows of realistic Indian insurance claims across 7 languages.

Run `generate_dataset.py` (already built and tested).
Produces: claims.csv, patients.csv, hospitals.csv, documents.csv

Target stats to hit before moving on:
- Fraud rate: 15-18% (matches IRDAI published estimate)
- 7 languages represented (Hindi, Tamil, Telugu, Bengali, Marathi, Gujarati, Punjabi)
- All 12 fraud types present (see fraud taxonomy below)
- Phantom hospital rate: ~8%
- No null values in required fields
- Date logic valid (discharge > admission, claim > discharge)

Run `validators/stats_check.py` to verify all of the above before upload.

**Father interview checklist (do this before generating full 100K):**
- What does a typical bill inflation look like on paper? What line item?
- How quickly are fraudulent claims usually filed vs legitimate?
- Do fraudulent claimants usually have pre-existing conditions hidden?
- What's the most common agent-linked fraud pattern he's seen?
- What does a readmission fraud look like in the paperwork?
- Pharmacy fraud: how are medicines billed that were never given?
Document his answers as `domain_expert_notes.md` in the repo.
This becomes your validation paragraph in the paper.

---

## Phase 2 — Adaption Upload and Adapt (Week 2)

**Step 1: Install SDK and authenticate**
```bash
pip install adaption
export ADAPTION_API_KEY=pt_live_...  # get from adaptionlabs.ai/app/settings
```

**Step 2: Upload claims.csv**
```python
from adaption import Adaption
client = Adaption()
result = client.datasets.upload_file("data/claims.csv", name="indiaclaimguard-v1")
dataset_id = result.dataset_id
print(dataset_id)  # save this, you'll use it in every subsequent call
```

**Step 3: Estimate cost before committing**
```python
estimate = client.datasets.run(
    dataset_id,
    column_mapping={"prompt": "claim_description", "completion": "adjudication_reasoning"},
    estimate=True,
)
print(f"Estimated credits: {estimate.estimated_credits_consumed}")
```

**Step 4: Run with reasoning traces (this is the key step)**
```python
run = client.datasets.run(
    dataset_id,
    column_mapping={
        "prompt": "claim_description",
        "completion": "adjudication_reasoning",
    },
    recipe_specification={
        "recipes": {
            "reasoning_traces": True,
            "deduplication": True,
        }
    },
)
print(f"Run started: {run.run_id}")
```

The reasoning traces Adaption adds become the chain-of-thought
training data for ClaimCourt's RL agent. Each adapted row will have
an intermediate reasoning path showing how the adjudication decision
was reached. This is your research contribution made concrete.

**Step 5: Wait and download**
```python
from adaption import DatasetTimeout
try:
    final = client.datasets.wait_for_completion(dataset_id, timeout=3600)
    print(f"Status: {final.status}")
except DatasetTimeout:
    print("Still running, check manually")

url = client.datasets.download(dataset_id)
print(f"Download: {url}")
```

**Step 6: Apply Blueprint rules**
Go to adaptionlabs.ai/app after upload and set Blueprint constraints:
- fraud_confidence must be between 0.0 and 1.0
- claim_amount_approved_inr must be <= claim_amount_requested_inr
- is_phantom hospitals must have rohini_id = invalid format
Document that Blueprint was used in your paper methodology section.

---

## Phase 3 — Publish on Kaggle (Week 2-3)

**Files to upload:**
```
kaggle-upload/
├── claims.csv               (adapted by Adaption)
├── patients.csv
├── hospitals.csv
├── documents.csv
├── README.md                (dataset card — template in /templates/)
├── DATA_DICTIONARY.md       (every field explained)
├── generate_dataset.py      (full generation code)
├── domain_expert_notes.md   (father's validation, anonymized)
└── notebooks/
    └── baseline_eda.ipynb   (EDA + XGBoost baseline for others to beat)
```

**Publish commands:**
```bash
pip install kaggle
# Place kaggle.json at ~/.kaggle/kaggle.json
kaggle datasets init -p kaggle-upload/
# Edit datapackage.json: title, description, license CC BY 4.0
kaggle datasets create -p kaggle-upload/ --dir-mode zip
```

**Dataset title on Kaggle:**
"IndiaClaimGuard: Synthetic Indian Health Insurance Fraud Dataset (IRDAI-aligned, 100K)"

**Kaggle tags:**
insurance-fraud, india, healthcare, tabular, synthetic,
classification, anomaly-detection, rl, finance, icd-10, irdai

---

## Phase 4 — AutoScientist (Week 3)

After Kaggle publish, use AutoScientist to train your ClaimCourt model.
AutoScientist is free for 30 days from their May 2026 launch.

Target column: fraud_label (binary classification)
Secondary target: fraud_type (multiclass, 12 categories)

AutoScientist co-optimizes your data and training recipe automatically.
Screenshot the win-rate curve and AUC improvement. This becomes Figure 1
in your paper (showing your adapted dataset trains better than baseline).

---

## Phase 5 — Research Paper (Week 3-4)

**Title:** CalibFraud: A Calibrated Reinforcement Learning Benchmark for
Sequential Insurance Claim Adjudication in India

**Abstract (write this first, 150 words):**
Cover: problem (₹8000cr fraud, IRDAI 2026 mandate), gap (overconfident AI),
contribution (asymmetric reward + IndiaClaimGuard dataset + reasoning traces),
results (calibration ECE < 0.05, AUC > 0.92).

**Structure:**
1. Introduction
2. Related Work (fraud detection ML, RL calibration, CAPO paper)
3. IndiaClaimGuard Dataset (schema, generation, domain expert validation,
   Adaption adaptation pipeline, statistics vs IRDAI published numbers)
4. ClaimCourt Architecture (RL environment, action space, reward function)
5. The Calibration Reward (formal definition, asymmetric penalty table)
6. Experiments (AutoScientist baseline, ClaimCourt vs standard GRPO)
7. Results (AUC, F1, ECE, calibration curves)
8. Real-World Deployment Considerations
9. Conclusion

**Key equation (your research contribution):**
```
R(action, confidence) =
  +1.0  correct AND well-calibrated
  +0.3  correct AND overconfident
   0.0  incorrect AND uncertain
  -0.8  incorrect AND overconfident
  -0.3  escalated to human
```

**Target venues:**
- Primary: arXiv (submit immediately, don't wait for acceptance)
- AAAI 2026 Workshop on AI in Finance
- NeurIPS 2026 Datasets and Benchmarks Track

---

## Phase 6 — Outreach (Month 2)

Order matters. Do not approach companies before the arXiv paper is live.

**Week 1 after arXiv:**
Post on X tagging @adaption_ai and Sara Hooker. Write one LinkedIn post
about the dataset and paper. Link both. This is your public signal.

**Week 2 after arXiv:**
LinkedIn cold outreach to claims managers at Medi Assist, Star Health,
HDFC Ergo. Message template is in `/templates/outreach_message.md`.
Offer: early access to model + co-authorship on follow-up paper in
exchange for anonymized real claim samples to validate dataset.

**Month 3:**
Apply to IRDAI Innovation Sandbox. Application goes much stronger with
a published dataset, a submitted paper, and at least one private insurer
who has engaged with the work.

---

## Full Timeline

| Day   | Milestone                                              |
|-------|--------------------------------------------------------|
| 1-2   | Father interview, domain_expert_notes.md complete      |
| 3-5   | Generator rebuilt with all 12 fraud types + new fields |
| 6-7   | 100K rows generated, stats_check passes                |
| 8-9   | Adaption upload, reasoning traces run, Blueprint set   |
| 10    | Kaggle published with baseline notebook                |
| 11-14 | AutoScientist run, paper first draft written           |
| 15    | arXiv submission                                       |
| 16    | X post + LinkedIn post tagging Adaption                |
| 30    | Outreach to 10 TPAs and insurers                       |
| 45    | ClaimCourt API MVP on HuggingFace Spaces               |
| 60    | First real company engagement                          |
| 90    | IRDAI Innovation Sandbox application                   |

---

## What Stands You Apart From Every Other Fraud Dataset

1. Only Indian dataset aligned to IRDAI 2025 fraud taxonomy
2. 7 regional languages including native scripts
3. Confidence labels — nobody else has this
4. Reasoning traces from Adaption — chain-of-thought adjudication data
5. Domain expert validation (insurance agent, 20+ years experience)
6. 12 fraud types including readmission, pharmacy, ICD upcoding, fake policy
7. Full generation code published so it is reproducible
8. Backed by 3rd place hackathon + Adaption inaugural research grant
9. Calibrated reward function is the paper's core contribution, not just accuracy