---
type: 'Backlog'
title: 'Historical Harness Audit P0 Backlog'
description: 'Owner-provided earlier-session history, preserved as a research snapshot rather than the live completion ledger.'
status: 'archived'
created: '2026-10-26'
updated: '2026-10-27'
generated: 'agent'
verified: 'unverified'
owner: 'Andreas Elser'
tags: [history, research, harness-audit]
---

<!-- markdownlint-disable-next-line MD025 -->
# harness-audit backlog

Findings and deferred work, recorded 2026-10-26 while drafting v1 (P0). Nothing here blocks v1 unless marked **[v1]**.

Legend: **[v1]** resolve before or during v1, **[v1.1]** harness-triage, **[v2]** bootstrap, doctor, Go, sandbox, **[later]** unscheduled.

## 1. Catalog rough edges (from `checks/catalog.yaml` draft 0.1)

| ID | Item | Target |
|---|---|---|
| B-01 | `ORI-08` and `ORI-09` are LLM-judged gates, so Orientation L3 depends on LLM judgment. Decide whether to keep them as gates or demote to non-gating and let scripts approximate (import lines in CLAUDE.md, link to AGENTS.md). | [v1] |
| B-02 | Doc hygiene has a single gate (`DOC-02`) and no L1 gate. Intentional so repos without a docs site are not punished, but revisit after calibration. | [v1] |
| B-03 | `STA-08` (one config per tool) uses the `git_signal` detector loosely. Needs a real duplicate-config rule per tool (ruff vs flake8 vs pylint is not a conflict; two ruff configs at one scope is). | [v1] |
| B-04 | Entropy penalty formula is a placeholder: `min(10, round(10 * flagged / candidates * 5))`. Tune in P4, freeze before P5. | [v1] |
| B-05 | Regex sets under `sets:` are a first pass (test, lint, type commands). Expect misses on custom wrappers (`make verify`, `tox -e lint`, `hatch run`). | [v1] |
| B-06 | Python runner coverage is thin: hatch, poe, pdm scripts, uv run, and `[tool.*]` scripts in `pyproject.toml` are not parsed as runner targets yet. | [v1] |
| B-07 | Node monorepo tools (pnpm workspaces, turbo, nx, lerna, Bazel as in angular) are not modeled; workspace-level scripts may hide targets. | [v1] |
| B-08 | `ORI-10` carries an `only_if` param (more than one component) that `run_checks.py` must understand. Define the `only_if` vocabulary or remove the param. | [v1] |
| B-09 | `ci_runs` has three jobs mixed in one detector: command match, trigger match, and share-of-run-steps. Consider splitting into `ci_runs`, `ci_trigger`, `ci_ratio`. | [v1] |
| B-10 | `ENT-01` accepts any `package.json`, which every Node repo has. It is a weak L1 gate; require a `scripts` block with at least one entry. | [v1] |
| B-11 | Weights (Verification 25, Orientation 20, Static 15, Entry points 15, Triggers 10, Parity 10, Docs 5) and caps (40, 60, 70) are provisional. | [v1] |
| B-12 | Pass ratio of 0.6 per level is a guess; check sensitivity on the calibration set. | [v1] |

## 2. Data notes on `example-repos.json`

| ID | Item | Target |
|---|---|---|
| B-20 | `n8n` and `opencode` both list exactly 203,000 stars as of 2026-09. Possible copy error; re-check. | [v1] |
| B-21 | Most entries are `verified: false` with null license and creation date. Selection is fine; do not cite them as facts in reports. | [v1] |
| B-22 | `hermes-agent` has `ecosystem: other` and no languages listed, so it is outside v1 scope until its stack is known. | [later] |
| B-23 | Go and Rust repos (urfave-cli, cobra, tinyauth, dynacat, fzf, bat, ollama, kubernetes) are out of v1 scope; reuse them as the v2 Go calibration set. | [v2] |
| B-24 | Mixed Python and Node repos (immich, paperless-ngx, open-webui) drive the per-component design. If detection fails on them, per-component scoring needs rework. | [v1] |

## 3. Design decisions to revisit

| ID | Item | Target |
|---|---|---|
| B-30 | v1 never runs repo code, so test speed cannot be measured. L3 "fast subset exists" is inferred from config only. A sandboxed run mode (possibly via App-Gate's container setup) would allow real timings. | [v2] |
| B-31 | Single headline score vs per-pillar only. Kept both with hard caps; watch for gaming and for scores that feel wrong on holdout repos. | [v1] |
| B-32 | Audit is stack-neutral, bootstrap is opinionated (Taskfile + pre-commit + Ruff/ESLint). Consider an L3 bonus for any single entry point that CI also calls, regardless of tool. | [v1] |
| B-33 | Copilot instruction support evolves; re-verify current AGENTS.md and agent-hook support in Copilot before freezing `ORI-08` and `TRG-05`. | [v1] |
| B-34 | Report language is English throughout (assumed; the repos are English). | [v1] |
| B-35 | Shallow clone (`--depth 1`) vs `--filter=blob:none`: entropy checks need history. Decide per check which clone mode it requires and fail soft when only shallow history exists. | [v1] |

## 4. Later versions

### v1.1: `harness-triage`
- Deeper entropy analysis: reference graph across runners, CI, hooks and docs; last-touch dates; dead config detection.
- Verdict workflow: active, stale, orphaned, conflicting, unknown, each with evidence. Never deletes.
- Dependency usage analysis (`ENR-06`) with an allowlist for tooling-only packages.
- HTML triage view reusing repo-atlas rendering.

### v2
- `harness-bootstrap`: proposes and creates missing pieces pillar by pillar, with diffs before applying. Reference stack: Taskfile.dev, pre-commit framework, Ruff, mypy or pyright, pytest, ESLint and Prettier (or Biome), Vitest or Jest, `tsc --noEmit`, CI calling `task ci`.
- `harness-doctor`: Taskfile target that runs the audit locally and in CI without any agent, to show the harness is a repo property.
- Go support (golangci-lint, `go test -race`, goreleaser) and possibly Rust.
- Optional sandboxed run mode for real test timings.
- Score history across audits of the same repo, to show whether a harness is improving.

### Later
- Combined report with App-Gate (safe), repo-atlas (understood) and harness-audit (workable).
- Terraform, Docker Compose and Azure pipeline specifics as extra pillars or components.
- Org-level roll-up across many repos.
- Instruction drift check as a standalone, cheap CI job.

## 4b. Schema findings (from `report.schema.json` draft 0.1)

The schema validates the example report and rejects all 15 negative cases. It cannot enforce everything, so these gaps move into code:

| ID | Item | Target |
|---|---|---|
| B-40 | JSON Schema cannot check arithmetic: `points = level / 3 * weight`, `raw = sum(points)`, `final = round(min(raw, caps) - penalty)`. `score.py` needs a self-check that recomputes and compares, and the example generator should fail loudly on mismatch. | [v1] |
| B-41 | Rule for choosing `top_gaps` is undefined. Proposal: failed gate checks first, ordered by pillar weight, then lowest level; max 5. | [v1] |
| B-42 | `findings[].gate` duplicates `catalog.yaml`. Decide whether the report copies it (self-contained, can drift) or the reader joins on `check_id` (no drift, needs the catalog). | [v1] |
| B-43 | `caps_applied[].id` is a closed enum (`no-tests`, `no-ci`, `no-orientation`). Adding a cap means a schema change; fine for v1, revisit if caps grow. | [v1] |
| B-44 | Findings for `not_applicable` and `unknown` may have empty evidence by design. `unknown` from the LLM layer should always say why in `note`; not enforced yet. | [v1] |
| B-45 | `pass` requires at least one `found` evidence item, `fail` requires at least one item of either kind. Check that real detectors can always produce a `searched` entry that is useful, not just a repeated glob list. | [v1] |
| B-46 | Per-component results exist only on `pillars[].by_component`; findings carry an optional `component`. Verify on immich, paperless-ngx and open-webui that this is enough to explain a weak component. | [v1] |
| B-47 | No field for the audited repo's declared license or visibility. Not needed for scoring; add only if reports get shared. | [later] |
| B-48 | Schema version is pinned with `const: "0.1"`. Define a migration rule before the first non-draft release so old reports stay readable. | [v1.1] |

## 5. Risks carried forward

- Stack-neutral detection is the hard part; the catalog will grow after P1.
- Big repos overwhelm the LLM layer; it must only see script-selected excerpts.
- The score may reward ceremony over substance (a large CI that gates nothing). The "enforced" criteria and the holdout set are the guard.
- Orientation is new territory: many OSS repos will score L0 or L1 there. That is the finding, not a bug.

## 6. Test sets (from the plan)

- Dev (2): flask, express
- Calibration (8): httpie-cli, immich-public-proxy, fastapi, paperless-ngx, opencode, vite, home-assistant-core, n8n
- Holdout (6): rich, fastify, open-webui, nestjs, django, nextjs

Holdout stays untouched until weights are frozen.
