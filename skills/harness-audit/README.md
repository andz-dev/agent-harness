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

## Infrastructure overlay

`scripts/detect_infra.py` finds infrastructure-as-code, container and dev-environment files. `scripts/infra_checks.py`
runs 56 checks on Dockerfiles (`INF-D01..D07`), Compose files (`INF-C01..C05`), devcontainers (`INF-V01..V06`),
Terraform/OpenTofu directories (`INF-T01..T07`), Bicep (`INF-B01..B06`), Kubernetes/Helm (`INF-K01..K07`), Ansible (`INF-A01..A04`), CloudFormation (`INF-F01..F03`), Pulumi (`INF-P01..P03`) and cross-cutting repository checks (`INF-X01..X05`). Four judgement checks (`INF-J01..J04`, prompt `prompts/infra_quality.md`) ask whether the agent files explain safe plan/apply handling, environments, credential sources and local checks. The report shows the result under "Infrastructure" and in the `infra`
block of `report.json` (`checks`, `summary`, `rollup`, `levels`). The overlay has its own level L0 to L3 per area and overall (weakest tool area; repo-wide areas reported separately), computed with the pillar rule; see `SKILL.md`.

It never changes the score (decision D1; a test pins it). Other IaC tools are detected but not checked yet. Plan and
backlog: `docs/0005/Infrastructure-Coverage-Map.md` in the repository root and `BACKLOG.md` sections 4v to 4x.
