---
type: 'Reference'
---

# Weights frozen (2026-10-26)

Frozen after calibration round 2 (12 repos, independent second opinion, tuning step 1; BACKLOG 4k-4n).

- Pillar weights: Verification 25, Orientation 20, Static guardrails 15, Workflow entry points 15, Automatic triggers 10, Pipeline parity 10, Doc hygiene 5.
- Caps: no-tests 40, no-ci 60, no-orientation 70. Pass ratio 0.6. Entropy max penalty 10.
- Verification cap: Orientation and Entry points <= Verification level + 1.
- Calibration result: MAE 5.1 vs human gut scores, bias +1.4, Spearman ~0.84.

Rules from now on: no change to weights, caps, level rule or check levels/gates until the holdout is reported. Detector bug fixes are allowed but must be logged in BACKLOG and re-verify `FROZEN.sha256` intentionally (a changed hash is listed in the holdout report).
