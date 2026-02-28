# RLVR Recent Papers Summary

| # | Concept | Key Idea | Papers |
|---|---------|----------|--------|
| 1 | Entropy Calibration | Treat uncertainty, not just binary correctness | 2602.22751 |
| 2 | Context‑Augmented RL | Full reference solutions as context; multi‑turn sampling | 2602.22623 |
| 3 | Mutual‑Info Skill Learning | Token‑level MI reward in GRPO to boost pass@k | 2602.22296 |
| 4 | Action‑Aware SFT + KL | For GUI agents: action‑aware SFT, KL trust‑region, adaptive scaling | 2602.22190 |
| 5 | Difficulty‑Aware Normalization | Group roll‑outs by difficulty; share std within groups | 2602.21743 |
| 6 | Rubric‑Based Curriculum | Stratified rubrics, learn from easier to harder | 2602.21628 |
| 7 | Asymmetric Confidence Penalty | Modulate negative advantage with confidence shift | 2602.21420 |

## Themes
* **Uncertainty & Calibration** – EGPO, MI‑learning.
* **Rich Verification** – ContextRL, RuCL.
* **Explore & Avoid Over‑confidence** – ACE, MI reward.
* **Multimodal & GUI** – Durian, GUI‑Libra.

All works extend RLVR + GRPO by adding calibration/regularization layers to improve sample efficiency, reduce reward hacking, and broaden applicability.
