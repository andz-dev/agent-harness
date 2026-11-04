---
type: 'Plan'
id: '0005'
version: 'v0.1'
title: 'Infrastructure Overlay: Matched Plan'
description: 'Coverage tracks and observable boundaries reconciled with implementation commits.'
status: 'active'
doc_scope: 'history'
created: '2026-10-28'
updated: '2026-10-28'
generated: 'agent'
verified: 'unverified'
owner: 'Andreas Elser'
stale_after: '2026-11-11'
tags: [documentation, retrospective]
sources: ['docs/0005-v0.1-infrastructure-overlay-matched/research/Infrastructure-Coverage-Map.md', 'git:0aaec6f', 'git:8b19edc', 'git:12c28e8']
---

# Infrastructure Overlay: Matched Plan

## Acceptance Boundaries

| ID | Observable requirement |
| --- | --- |
| I-1 | Detected infrastructure is attributed by kind and location. |
| I-2 | Static findings include evidence and distinguish pass/fail/unknown/not-applicable. |
| I-3 | Infrastructure levels and roll-ups remain separate from pillar points and score. |
| I-4 | Judgment answers require verified quotes and retain unsupported unknowns. |
| I-5 | No terraform/docker/kubectl/devcontainer execution occurs during audit. |

## Matched Workstreams

Detection precedes initial container/Terraform checks, report output, area levels and
broader tool coverage. Judgment and entropy arrive through later commits. The historical
harbor city adapter was implemented then reverted; the current airport is a separate
opt-in evaluation. A proposed generalized adoption skill is not treated as delivered.

## Validation Contract

Objective: identify implemented tracks without claiming every proposed check exists.
Read first: original coverage map, [Architecture](Architecture.md), [Implementation](Implementation.md).
Constraints: frozen main score; read-only audit; no deployment or owner-file overwrite.
Validate: `git show --stat 20b21f2`, `git show --stat 12c28e8` and `python3 tools/check.py`.
Stop when: each completion has a source/commit and unimplemented proposals remain explicit.
New detector work still requires focused synthetic regressions and the current `task check`.

## Scope

In scope, as shown by the commits `20b21f2` through `2146078`: static detection of
infrastructure files, mechanical checks for Dockerfile, Compose, devcontainer, Terraform and
OpenTofu, Bicep, Kubernetes and Helm, Ansible, CloudFormation and Pulumi, cross-cutting checks,
infrastructure entropy checks, four judgement tasks, the `infra` block in `report.json`, the
Infrastructure section of `report.md`, area and overall levels, and the calibration comparison
tool. Evidence basis for every row below is the tree at `2146078` unless a commit is named.

Out of scope or not delivered: execution of any infrastructure tool (map decision D4), a new
pillar or any change to the frozen 0-100 score, the Harness City adapter (`a620cd5` added a
harbor overlay and `f2154c2` reverted it, "B-182, B-183 reopened"), the separate adoption skill
of Track F, and calibration by more than one rater. Go support is out of scope per the map.

## Acceptance Criteria (Given/When/Then)

These restate I-1 to I-5 as checks that the folder's behaviour supports. They describe what the
overlay promises, not a replay of any old run. The test names come from the test files at
`2146078`; the results of running them are `Not recorded` by this folder.

| ID | Given | When | Then |
| --- | --- | --- | --- |
| AC-1 (I-1) | a repository holding `infra/main.tf`, a `Dockerfile` and `.devcontainer/devcontainer.json` | `detect_infra.detect` runs | it returns entries with `kind`, `tool`, `scope` and `status` `detected-not-scored`, and `tools` equals `["devcontainer", "docker", "terraform"]` |
| AC-2 (I-2) | a Dockerfile that uses an unpinned base, runs as root and sets a literal secret | the Dockerfile checks run | the matching `INF-D` checks fail and each finding carries evidence; `test_latest_bare_root_and_secret_fail` covers it |
| AC-3 (I-2) | a Compose file that defines no services | the Compose checks run | the findings are `not_applicable`; `test_file_without_services_is_not_applicable` covers it |
| AC-4 (I-3) | the same repository scored with and without infrastructure files | the audit runs twice | the 0-100 score is equal and the report holds an `infra` block with `levels`; `test_infra_files_never_change_the_score` covers it |
| AC-5 (I-4) | infrastructure exists and an agent file exists | the planner and `--llm-answers` pass run | four tasks `INF-J01` to `INF-J04` appear, and an answer with no verified quote becomes `unknown`; `test_infra_judgement_answers_reach_the_report_without_touching_the_score` covers the report path |
| AC-6 (I-4, edge) | infrastructure exists and no agent instruction file exists | `infra_tasks` runs | no task is written and four findings fail by script with the note "Nothing to judge: no agent instruction file." |
| AC-7 (I-5) | any audited repository with Terraform or Docker files | the overlay scripts run | no `terraform`, `docker`, `kubectl` or `devcontainer` process starts; a `git grep` for `subprocess` in the three overlay scripts returns no line. A test that asserts this directly is `Not recorded` |
| AC-8 (I-3, edge) | an area whose gate check fails | `levels` runs | the area stays at level 0; `test_failed_gate_keeps_area_at_level_zero` covers it |
| AC-9 (I-3, edge) | a non-secret check passing in a clear majority of locations | `levels` runs | the check holds for the area; `test_a_clear_majority_of_locations_is_enough` covers it, and `test_secret_checks_stay_all_or_nothing` pins the strict set |
| AC-10 (negative) | a repository with no infrastructure | the checks and levels run | no findings and no overall level; `test_no_infra_no_findings` and `test_no_infra_has_no_level` cover it |

## Assumptions

- The frozen score and catalog stay byte-identical: the blobs of `score.py` and `catalog.yaml`
  are equal at `3106ad5` and `2146078`, so the overlay's promise rests on files the overlay does
  not edit.
- Git is available. `detect_stack.list_files` uses `git ls-files -z` when `.git` exists and a
  directory walk otherwise; whether the report records which of the two was used is
  `Not recorded` here.
- Text matching is enough for a first level. `SKILL.md` calls the results leads, not verdicts.
- The model answers for `INF-J01` to `INF-J04` come from an external run; which model is
  `Not recorded`.
- Synthetic trees stand in for real repositories in tests. BACKLOG B-211 at `2146078` names
  `n8n`, `home-assistant-core` and `opencode` as the three calibration repositories with both
  infrastructure and agent files.

## Milestones and Delivery Slices

| Slice | Commits | Outcome | Criteria |
| --- | --- | --- | --- |
| M1 Detection and report block | `20b21f2` | `detect_infra.py`, `infra` block, Infrastructure table | AC-1, AC-4 |
| M2 First checks | `21d8ef0` | 25 checks for Dockerfile, Compose, devcontainer, Terraform | AC-2, AC-3 |
| M3 Roll-up and levels | `0aaec6f`, `8b19edc` | per-check roll-up, area and overall levels | AC-8 |
| M4 Wider tool coverage | `83d6a88`, `44da439` | 38 then 53 checks with Bicep, Kubernetes, Ansible, CloudFormation, Pulumi, cross-cutting | AC-2 |
| M5 Judgement | `12c28e8` | `INF-J01` to `INF-J04`, prompt, frozen-hash update | AC-5, AC-6 |
| M6 Entropy, attribution, calibration | `6490917`, `1cbf3f1`, `be2475a`, `2146078` | entropy checks, component attribution, GitOps detection, calibration tool, majority rule | AC-9, AC-10 |

Check counts are `CHECKS` keys counted with `ast` at each commit. Not delivered in any slice: the
city adapter and the adoption skill. Done means each delivered slice has a commit and a named
test; it does not mean every idea in the map exists.

## Risks and Mitigations

| Risk | Mitigation recorded in the tree |
| --- | --- |
| The overlay level is read as part of the score | `SKILL.md`: "Do not add the two together"; limitation line in the report |
| A check passes on text that CI never runs | the report keeps quoted evidence and `SKILL.md` calls results leads |
| A frozen file changes without review | `FROZEN.sha256` is updated in the same commits as each `llm_layer.py` change |
| Uncalibrated levels are cited as measured | BACKLOG B-202 says levels are uncalibrated; calibration limits sit in [0006](../0006-v0.1-infrastructure-calibration-retrospective/Plan.md) |
| One weak location decides a monorepo | `2146078` changes the rule to a 60 percent location majority and keeps the roll-up listing the failing paths |

## Open Questions

- Conflict, check count. The map says "56 checks" at `44da439` and `12c28e8`; `CHECKS` has 53
  mechanical keys at `44da439` and 53 mechanical plus 4 judgement keys at `12c28e8`; `SKILL.md`
  at `2146078` says "59 script checks" and 4 judgement checks, while the code has 56 and 4.
  All three statements stay as historical; none is corrected here.
- Conflict, status. The map lists the component model (B-170) and infra entropy (B-179) under
  "Still `todo`"; BACKLOG at `2146078` marks both "Done in part" and the code has `attribute` and
  `INF-E01` to `INF-E03`.
- Conflict, ratings. `infra_calibration.py` and BACKLOG B-215 say ratings files are not
  committed; commit `2146078` adds `infra-levels-evaluation.json`.
- Which model or tool produced the infrastructure judgement answers? `Not recorded`.
- Why did Bicep and Kubernetes precede judgement and entropy, against the map's suggested order?
  `Not recorded`.
- Is there a test that fails when an overlay script starts a child process? `Not recorded`.