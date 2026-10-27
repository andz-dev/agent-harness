---
type: 'Guide'
---

# harness-audit

Scores how well a repository equips AI agents and humans to work in it: orientation files, tests, linters,
hooks, task runner, CI parity, doc hygiene and entropy. Read-only, Python and Node repositories (v1).

## Installation

```
task setup
```

## Usage

```
task audit -- path/to/repo --out build/report
```

Writes `report.json` (validated against `schema/report.schema.json`), `report.md`, a ranked fix plan (`triage.md`, `triage.json`) and, when judgement checks
need a model, `llm_tasks.json`. Answer the tasks following `prompts/*.md`, then re-run with
`--llm-answers answers.json`. See `SKILL.md` for the agent workflow and `BACKLOG.md` for known gaps.

## Bootstrap (preview)

```
python3 -I scripts/bootstrap.py path/to/repo --report build/report/report.json --out build/bootstrap
```

Proposes the missing harness files into `build/bootstrap/proposed/`. Add `--apply` to write the new ones into the repository
(existing files are never overwritten).

## Status (v1.2)

Weights are frozen (see `calibration/WEIGHTS-FROZEN.md`). Validated on 18 public repositories against one rater's
gut scores: mean error about 5 points. Known gaps and next steps are in `BACKLOG.md` (B-1 to B-158).

## Development

`task check` runs lint and tests. See `AGENTS.md`.
