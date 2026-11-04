---
type: 'Release Notes'
title: 'harness-audit v1.2 Release Notes'
status: 'active'
created: '2026-10-27'
updated: '2026-10-27'
generated: 'agent'
verified: 'unverified'
owner: 'Andreas Elser'
---

<!-- markdownlint-disable-next-line MD025 -->
# harness-audit v1.2 Release Notes

## What it is
A read-only audit of how well a Python or Node repository equips AI agents and humans to work in it, plus a ranked fix plan and a bootstrap preview that proposes the missing files. It never runs the audited code.

## What is in v1.2
| Area | What | Since |
| --- | --- | --- |
| Audit | 7 pillars (L0-L3), 56 checks, gates, caps, entropy penalty, schema-validated `report.json` and `report.md` | v1.0 |
| Judgement layer | Script selects excerpts, a model answers, every quote is re-verified against the files | v1.0 |
| Calibration | Weights frozen on 12 repos, holdout of 6 run once; mean error about 5 points vs one rater | v1.0 |
| Fix plan | `triage.md` / `triage.json`: counterfactual ranking by points per effort, bundles of up to 3 checks, entropy cleanup | v1.1 |
| Bootstrap | `bootstrap.py` proposes AGENTS.md, CLAUDE.md, Taskfile, pre-commit (Python), CI, Dependabot, CONTRIBUTING; never overwrites; `--apply` optional | v1.1 preview |
| Placeholders | A check no longer passes on a file that still contains `TODO(human)` | v1.2 |
| DOC-06 | Resolved by script when every backticked path resolves; history files skipped | v1.2 |
| Excerpts | 400 lines per file, 1000 per task, 200 runner targets | v1.2 |
| Package | `harness-audit.skill` (zip, SKILL.md at `harness-audit/`) with tests, schema, prompts, references | v1.2 |

## Verified
- 141 tests pass in the repository and in an unzipped copy of the package.
- Weights, caps, level rule and pillar weights are pinned by a test and listed in `references/FROZEN.sha256`.
- 18 repositories re-scored with v1.2: mean absolute error 5.3, bias +3.1 against one rater's gut scores (see `scans/results-table.md`).

## Known limits
- One rater; six calibration scores were weak "keep it" answers; the holdout scores were given after seeing the ranking.
- The tool runs 3-5 points high on mature open-source repos.
- Judgement answers come from a model; DOC-06 is still unknown where dead-path candidates remain; STA-09 adds little signal.
- Python and Node only. Bootstrap proposes GitHub Actions only (no Azure DevOps yet).
- The script DOC-06 check covers backticked paths only, not Markdown links or commands.

## Install
Unzip `harness-audit.skill` into your skills folder (you get `harness-audit/SKILL.md`). Needs Python 3.11+ and `pip install pyyaml jsonschema`. Run `python3 -I scripts/audit.py <repo> --out <dir>` from the skill directory.
