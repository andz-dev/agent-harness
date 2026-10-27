---
type: 'Report'
title: 'Judgement Agreement Report (v1.2)'
status: 'active'
created: '2026-10-27'
updated: '2026-10-27'
generated: 'agent'
verified: 'unverified'
owner: 'Andreas Elser'
---

<!-- markdownlint-disable-next-line MD025 -->
# Judgement Agreement Report (v1.2)

Second run, after the prompt fixes in B-162 and with DOC-06 resolved by script where possible.
Two blind runs (A and B) by independent subagents over the 15 repos that have judgement tasks.
First run (before the fixes, 12 repos): 33/49 agree (67%), kappa 0.36.

Repos: 15 · answers compared: 54 · agreement: 47/54 (87%) · Cohen's kappa: 0.768

| Task | Agree | Total |
| --- | --- | --- |
| DOC-06 | 7 | 9 |
| ENT-05 | 7 | 7 |
| ORI-05 | 6 | 7 |
| ORI-06 | 7 | 7 |
| ORI-08 | 1 | 2 |
| ORI-09 | 5 | 7 |
| TRG-06 | 1 | 1 |
| VER-11 | 13 | 14 |

## Disagreements

| Repo | Task | Run A | Run B |
| --- | --- | --- | --- |
| home-assistant-core | ORI-08 | pass | unknown |
| home-assistant-core | ORI-09 | pass | unknown |
| immich-public-proxy | VER-11 | pass | fail |
| n8n | ORI-09 | unknown | pass |
| nextjs | DOC-06 | pass | unknown |
| opencode | ORI-05 | fail | pass |
| vllm | DOC-06 | pass | unknown |

## Effect on scores

Scoring each repo with run A and run B answers: 13 of 15 repos get the same score; n8n differs
by 7 (78 vs 85, ORI-09 unknown vs pass) and opencode by 6 (42 vs 48, ORI-05 fail vs pass). Mean difference 0.9 points.
Answer files are not committed (see AGENTS.md).
