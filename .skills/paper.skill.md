# Research Paper — paper.skill.md
# Conventions for writing the CalibFraud paper.
# Read before writing or editing any section of the paper.

---

## Paper Identity
Title: CalibFraud: A Calibrated Reinforcement Learning Benchmark
       for Sequential Insurance Claim Adjudication in India
Short name: CalibFraud
Dataset name: IndiaClaimGuard
Model name: ClaimCourt

---

## Core Claim (one sentence — anchor every section to this)
Standard RL training produces overconfident agents; by penalizing
confident wrong decisions more than uncertain wrong decisions, ClaimCourt
learns to know what it doesn't know — a property that matters more than
raw accuracy in high-stakes insurance adjudication.

---

## Target Venues
1. arXiv (submit first — immediately after Kaggle publish, don't wait)
2. AAAI 2026 Workshop on AI in Finance
3. NeurIPS 2026 Datasets and Benchmarks Track (if dataset contribution framing)

---

## Paper Structure

### Abstract (150 words max)
Cover exactly these four things:
1. Problem: India loses ₹8,000+ crore annually to insurance fraud;
   IRDAI's April 2026 mandate requires all insurers to detect it
2. Gap: Existing AI tools are overconfident — wrong and certain is
   worse than wrong and uncertain in production adjudication
3. Contribution: IndiaClaimGuard dataset (100K claims, 7 languages,
   12 fraud types, confidence labels, reasoning traces via Adaption) +
   ClaimCourt agent trained with asymmetric calibration reward
4. Results: AUC > 0.92, calibration ECE < 0.05, outperforms standard
   GRPO baseline on calibration while matching on accuracy

### Section 1: Introduction
- Open with the ₹8,000 crore number (BCG × Medi Assist, Nov 2025)
- IRDAI 2025 Insurance Fraud Monitoring Framework, effective April 2026
- Why calibration matters: cite the CAPO paper on overconfidence in RL
- Two contributions: dataset + calibrated reward function
- Paper roadmap (one sentence per section)

### Section 2: Related Work
Three paragraphs:
1. ML for insurance fraud detection (cite existing Kaggle benchmark papers)
2. RL for sequential decision making in high-stakes domains
3. Calibration in ML (ECE metric, temperature scaling, CAPO paper)
Do NOT oversell how novel you are. State clearly what gap you fill.

### Section 3: IndiaClaimGuard Dataset
Subsections:
- 3.1 Motivation (no Indian fraud dataset exists with IRDAI taxonomy)
- 3.2 Schema (reference DATA_DICTIONARY.md; don't repeat every field)
- 3.3 Fraud Taxonomy (table of 12 types, IRDAI alignment, distribution)
- 3.4 Generation Methodology (Python generator, language pools, ICD codes)
- 3.5 Domain Expert Validation (father's input, anonymized; cite as "insurance agent, 20+ years experience")
- 3.6 Adaption Adaptation (Blueprint + reasoning traces; cite adaptionlabs.ai)
- 3.7 Statistics vs IRDAI published numbers (table comparing distributions)

### Section 4: ClaimCourt Architecture
- 4.1 RL Environment (OpenEnv-compliant, action space)
- 4.2 Observation Space (claim fields as structured input)
- 4.3 Action Space (approve | deny | escalate)
- 4.4 Episode Generation (procedural, 5000 episodes in hackathon)

### Section 5: The Calibration Reward (key contribution)
Include this table as a formal definition:

| Action     | Confidence | Reward |
|------------|------------|--------|
| Correct    | Calibrated | +1.0   |
| Correct    | Overconfident | +0.3 |
| Incorrect  | Uncertain  | 0.0    |
| Incorrect  | Overconfident | -0.8 |
| Escalated  | Any        | -0.3   |

Explain why -0.8 for overconfident wrong > 0.0 for uncertain wrong.
This asymmetry is the research contribution. Spend 2 paragraphs on it.

### Section 6: Experiments
- 6.1 Baseline: XGBoost on IndiaClaimGuard (standard classification)
- 6.2 Baseline: ClaimCourt trained with standard GRPO (no calibration reward)
- 6.3 ClaimCourt trained with asymmetric calibration reward
- 6.4 AutoScientist baseline (screenshot Figure 1 from Adaption)
Metrics: AUC-ROC, Precision, Recall, F1, ECE (Expected Calibration Error)

### Section 7: Results
Include:
- Table comparing all baselines on all 5 metrics
- Calibration curve plot (reliability diagram)
- Performance breakdown by fraud type (which types are hardest)
Honest about weaknesses. Don't cherry-pick.

### Section 8: Real-World Deployment Considerations
- Escalation rate in production (what % of claims go to human)
- IRDAI compliance implications (Form FMR-1 reporting)
- Limitations: synthetic data, no real validation beyond domain expert
- Future work: Forge + real TPA data, IRDAI sandbox

### Section 9: Conclusion
Three sentences:
1. What you built
2. What the key finding is
3. What the path forward is (IRDAI sandbox, real data)

---

## Metrics Definitions

### AUC-ROC
Area under ROC curve. Target > 0.92.
Standard fraud detection metric. Every reviewer expects this.

### ECE (Expected Calibration Error)
Measures how well confidence scores match actual accuracy.
ECE = 0 means perfectly calibrated. Target < 0.05.
This is YOUR differentiating metric. No other fraud paper measures this.
```python
# Compute ECE
from sklearn.calibration import calibration_curve
import numpy as np

def compute_ece(y_true, y_prob, n_bins=10):
    fraction_of_positives, mean_predicted_value = calibration_curve(
        y_true, y_prob, n_bins=n_bins
    )
    ece = np.mean(np.abs(fraction_of_positives - mean_predicted_value))
    return ece
```

### Calibration Curve
Plot predicted probability (x) vs actual frequency (y).
Perfect calibration = diagonal line.
Include this as a figure. It visually shows your contribution.

---

## Writing Rules
- No em dashes (use commas or restructure)
- No bullet points inside the paper body
- Every number must have a citation or say "in our experiments"
- Never say "novel" or "state-of-the-art" — show it with numbers
- Domain expert validation must be in Section 3.5 no matter what
- Acknowledge limitations before a reviewer can raise them

## Citation Keys (BibTeX handles in paper)
- IRDAI 2025 framework → irdai2025fraud
- BCG Medi Assist report → bcg2025india
- CAPO overconfidence paper → capo2026
- IndiaClaimGuard (your dataset) → aslaliya2026indiaclaimguard
- Adaption platform → adaption2026