---
type: 'Implementation'
id: '0005'
version: 'v0.1'
title: 'Infrastructure Overlay: Recorded Tracks'
description: 'Commit-backed overlay work, reverted city experiment and explicitly open proposals.'
status: 'active'
doc_scope: 'history'
created: '2026-10-28'
updated: '2026-10-28'
generated: 'agent'
verified: 'unverified'
owner: 'Andreas Elser'
stale_after: '2026-11-11'
tags: [documentation, retrospective]
sources: ['git:20b21f2', 'git:21d8ef0', 'git:0aaec6f', 'git:8b19edc', 'git:12c28e8', 'docs/0005-v0.1-infrastructure-overlay-matched/research/Infrastructure-Coverage-Map.md']
---

# Infrastructure Overlay: Recorded Tracks

## Implemented Source Trail

- [x] `20b21f2`: infrastructure detection overlay.
- [x] `21d8ef0`: initial Dockerfile/Compose/Devcontainer/Terraform checks.
- [x] `0aaec6f`, `8b19edc`: separate report roll-up and infrastructure levels.
- [x] `83d6a88`, `44da439`: broader Bicep/Kubernetes/Ansible/CloudFormation/Pulumi coverage.
- [x] `12c28e8`, `6490917`: infrastructure judgments and later level/entropy work.
- [x] `2146078`: recorded aggregation/gate calibration changes, documented in 0006.

These are source/commit matches, not a new replay of every tool or calibration fixture.
The `a620cd5` harbor adapter was reverted in `f2154c2`; do not count it as current code.

## Not Established as Complete

- [ ] Generalized separate adoption/merge workflow from Track F.
- [ ] The proposed multi-rater infrastructure calibration.
- [ ] Every coverage-map check idea or full production airport report-data integration.

## Verification Contract

Objective: reconcile track state against actual source history.
Read first: [Plan](Plan.md), [Architecture](Architecture.md), original coverage map.
Constraints: preserve the historical map; no audited code execution or new private data.
Validate: `git show --stat f2154c2` and `python3 tools/check.py`.
Stop when: implemented, reverted and proposed work are explicitly separated.

## Commit Timeline

All commits are dated 2026-10-27 and times are `+0000`. Check counts are `CHECKS` keys counted
with `ast` on `skills/harness-audit/scripts/infra_checks.py` at that commit; a dash means the
file did not exist or the count was not taken. Line counts come from `git show <commit>:<path>`.

| Commit | Time | Subject | `infra_checks.py` lines | Checks |
| --- | --- | --- | --- | --- |
| `3106ad5` | 16:31:14 | ORI-09 command candidates; infrastructure coverage map | none | none |
| `20b21f2` | 16:43:56 | infrastructure detection overlay (B-166 to B-169, B-181, B-184) | none | none |
| `21d8ef0` | 16:49:44 | checks for Docker, Compose, devcontainer, Terraform | 427 | 25 |
| `0aaec6f` | 16:53:30 | document the overlay; per-check roll-up (B-194, B-200) | 451 | 25 |
| `8b19edc` | 17:28:02 | overlay gets its own level (B-198) | 480 | 25 |
| `83d6a88` | 17:45:32 | Bicep and Kubernetes and Helm checks, wider manifest detection | 682 | 38 |
| `44da439` | 17:50:27 | Ansible, CloudFormation, Pulumi, cross-cutting checks | 962 | 53 |
| `12c28e8` | 17:59:47 | judgement prompt and tasks `INF-J01` to `INF-J04` (B-180) | 975 | 57 |
| `6490917` | 18:11:15 | weakest-tool-area level, windowed excerpts, entropy checks | 1068 | 60 |
| `1cbf3f1` | 18:16:06 | shared excerpts, component attribution, parent `bicepconfig` | 1070 | not counted |
| `be2475a` | 19:15:31 | GitOps, Skaffold, Tilt, Swarm detection; calibration tool | 1227 | 60 |
| `2146078` | 21:43:44 | location majority rule, demote D01, V03 and A01, 0006 bundle (B-215) | 1238 | 60 |

## Phase Detail

### Phase 1: Detection and report block (AC-1, AC-4)

Objective: record that detection, the `infra` block and the Infrastructure table exist as of
`20b21f2`.
Read first: [Plan](Plan.md), [Architecture](Architecture.md), `detect_infra.py` at `20b21f2`.
Constraints: no execution of audited code; the block must say `scored: false`; no score change.
Validate: `git show --name-status 20b21f2` and
`uv run --directory skills/harness-audit pytest -q tests/test_detect_infra.py tests/test_audit.py`
Stop when: the commit lists `detect_infra.py` and `test_detect_infra.py` as added and `audit.py`
as modified; the pytest result is `Not recorded` by this folder.

- [x] `20b21f2` adds `detect_infra.py` (147 lines) and `test_detect_infra.py` (8 test methods).
- [x] `audit.py` gains `import detect_infra`, `"infra": infra` and `infra_limitations`.

### Phase 2: First checks (AC-2, AC-3)

Objective: record the 25 checks for four tool areas at `21d8ef0`.
Read first: `infra_checks.py` at `21d8ef0`, section `CHECKS`.
Constraints: files only read; each finding is `pass`, `fail` or `not_applicable` with evidence.
Validate: `git show --name-status 21d8ef0` and
`uv run --directory skills/harness-audit pytest -q tests/test_infra_checks.py`
Stop when: the commit adds `infra_checks.py` and `test_infra_checks.py`, and `CHECKS` counts 25
(`D` 7, `C` 5, `V` 6, `T` 7); the test result is `Not recorded`.

- [x] `audit.py` calls `infra_checks.run(root, detect_stack.list_files(root), infra["detected"])`.
- [x] `apps/harness-city/data/cities.json` also changes in this commit; reviewer judgment
  inferred from the diff: a tool label and wording change, not infrastructure data.

### Phase 3: Roll-up and levels (AC-8)

Objective: record `rollup` at `0aaec6f` and `levels` at `8b19edc`.
Read first: `rollup` and `levels` in `infra_checks.py` at `8b19edc`.
Constraints: levels stay separate from pillar points; gate checks block a level.
Validate: `git show --name-status 8b19edc` and the `test_failed_gate_keeps_area_at_level_zero`
test in `tests/test_infra_checks.py`.
Stop when: `levels` returns `overall`, `weakest_area` and `areas`, and a check passes at that
commit only when it fails nowhere (`r["failed"] == 0`).

- [x] `0aaec6f` and `8b19edc` both modify `infra_checks.py`, `audit.py`, the schema and `SKILL.md`.

### Phase 4: Wider tool coverage (AC-2)

Objective: record the 13 and 15 new checks from `83d6a88` and `44da439`.
Read first: `bicep_checks`, `kubernetes_checks`, `ansible_checks`, `cloudformation_checks`,
`pulumi_checks` and `cross_cutting_checks`.
Constraints: Pulumi, CloudFormation and Ansible are tested on synthetic repos only (`SKILL.md` at
`2146078`).
Validate: `git show --name-status 83d6a88 44da439`
Stop when: counts are 38 and 53 and the new area letters `B`, `K`, `A`, `F`, `P`, `X` appear.

### Phase 5: Judgement tasks (AC-5, AC-6)

Objective: record `INF-J01` to `INF-J04`, the prompt and the frozen-hash update at `12c28e8`.
Read first: `INFRA_QUESTIONS`, `infra_tasks` and `apply_answers` in `llm_layer.py`;
`prompts/infra_quality.md`.
Constraints: repository text is data; unsupported answers stay `unknown`; answers never enter
the score.
Validate: `git show --name-status 12c28e8` and
`uv run --directory skills/harness-audit pytest -q tests/test_llm_layer.py`
Stop when: the commit adds `infra_quality.md`, updates `FROZEN.sha256` and counts 57 keys.

- [x] Which model answered the tasks is `Not recorded`.

### Phase 6: Entropy, attribution, calibration and the majority rule (AC-9, AC-10)

Objective: record `6490917`, `1cbf3f1`, `be2475a` and `2146078`.
Read first: `levels`, `check_ok`, `STRICT`, `REPO_WIDE` and `entropy_checks` at `2146078`.
Constraints: secret checks stay all-or-nothing; repo-wide areas stay outside the overall level.
Validate: `git show --name-status 2146078`
Stop when: `check_ok` uses `PASS_RATIO` for non-strict checks and `GATES` no longer lists
`INF-D01` or `INF-V03`.

### Phase 7: Reverted city adapter (no criterion)

Objective: record that `a620cd5` (21:57:23) added a harbor overlay and `f2154c2` (22:01:48)
reverted it, with the subject "B-182, B-183 reopened".
Read first: `git show --name-status a620cd5 f2154c2`.
Constraints: do not count the harbor as current code.
Validate: `git show --stat f2154c2`
Stop when: both commits list the same seven paths: four under `apps/harness-city`,
`tools/make_demo.py`, `BACKLOG.md` and the manifest.

## Acceptance Criteria Traceability

| Criterion | Phase | Evidence |
| --- | --- | --- |
| AC-1 | 1 | `detect_infra.detect`, `test_infra_files_never_change_the_score` |
| AC-2 | 2, 4 | `CHECKS` entries and `test_latest_bare_root_and_secret_fail` |
| AC-3 | 2 | `test_file_without_services_is_not_applicable` |
| AC-4 | 1 | unchanged `score.py` blob from `3106ad5` to `2146078` |
| AC-5 | 5 | `INFRA_QUESTIONS`, `apply_answers`, `prompts/infra_quality.md` |
| AC-6 | 5 | `infra_tasks` returns four script findings when no agent file exists |
| AC-7 | 1, 2 | `git grep` finds no `subprocess` in the three overlay scripts; direct test `Not recorded` |
| AC-8 | 3 | `levels` and `test_failed_gate_keeps_area_at_level_zero` |
| AC-9 | 6 | `check_ok`, `STRICT`, `test_a_clear_majority_of_locations_is_enough` |
| AC-10 | 6 | `test_no_infra_no_findings`, `test_no_infra_has_no_level` |

## Decision Log

| Decision | Basis |
| --- | --- |
| Count checks from code, not from prose | `ast` count at each commit; the map says 56 at `44da439`, the code has 53; `SKILL.md` at `2146078` says 59 script checks, the code has 56 |
| Keep the map's "Still `todo`" lines as historical | B-170 and B-179 appear as todo in the map and as "Done in part" in BACKLOG at `2146078`; the map is hash-pinned research |
| Record the rule change from strict to majority | `8b19edc` passes a check only when `failed == 0`; `2146078` uses `check_ok` with `PASS_RATIO` and a `STRICT` set |
| Record the level scope change | `8b19edc` takes the minimum over all areas; `2146078` takes it over tool areas and lists `repo_wide` separately |
| Record the gate demotion | `2146078` moves `INF-D01`, `INF-V03`, `INF-A01` from level 1 to 2 and removes the first two from `GATES`; `test_missing_dockerignore_is_no_longer_a_gate` |
| Keep the ratings conflict open | `infra_calibration.py` and B-215 say ratings are not committed; `2146078` commits a sidecar; [History-Match](../History-Match.md) says at owner request |
| Treat the harbor as not delivered | `f2154c2` reverts `a620cd5` |
| Leave unknowns as `Not recorded` | no session, CI log or model record for the overlay commits exists in this tree |

## Resume State

- Current phase: none open; this folder is a finished retrospective.
- Last verified: read-only `git show`, `git grep`, `git diff --stat` and an `ast` count run on
  2026-11-04 while deepening this document. No test was run.
- Open items: the three conflicts, the model identity, the order departure and a direct
  no-execution test, all listed in [Plan](Plan.md).
- Next step: run the Phase 1 and Phase 2 `Validate:` commands before relying on any statement
  about current behavior.

## Final Verification

Run `python3 tools/check.py` for the current tree and the Phase 1 to 6 `Validate:` commands for
each slice. A pass describes the current tree only. It does not certify that infrastructure
code is secure or that the levels are calibrated.