---
type: 'Implementation'
id: '0006'
version: 'v0.1'
title: 'Infrastructure Calibration: Recorded Outcomes'
description: 'The B-215 calibration artifacts and rule changes with unresolved validation limits.'
status: 'active'
doc_scope: 'history'
created: '2026-10-28'
updated: '2026-10-28'
generated: 'agent'
verified: 'unverified'
owner: 'Andreas Elser'
stale_after: '2026-11-11'
tags: [documentation, retrospective]
sources: ['git:2146078', 'docs/0006-v0.1-infrastructure-calibration-retrospective/research/README.md', 'docs/0006-v0.1-infrastructure-calibration-retrospective/research/infra-levels-evaluation.json']
---

# Infrastructure Calibration: Recorded Outcomes

## Recorded Implementation

- [x] `2146078` introduces the page, 35-record sidecar and calibration README.
- [x] The same commit records B-215 aggregation/gate changes.
- [x] The README preserves reported before/after measures and their interpretation limits.

The README reports exact agreement from 23% to 43%, within-one agreement from 77%
to 91%, and mean absolute difference from 1.00 to 0.66. These are historical figures,
not calculations independently rerun by this documentation reconstruction.

## Unresolved Validation

- [ ] A second independent human rating remains open in the available evidence.
- [ ] The exercise does not establish accuracy across all repositories or L0/L3 ratings.
- [ ] The retained outliers are not silently refitted to improve this one sample.

## Verification Contract

Objective: match artifacts and rule-change provenance without rerunning the experiment.
Read first: [Plan](Plan.md), [Architecture](Architecture.md), original README.
Constraints: preserve original ratings; no new votes or private dataset publication.
Validate: `git show --stat 2146078` and `python3 tools/check.py`.
Stop when: original source hashes and structural evidence match, with human-validation limits retained.

## Phase Detail

Evidence labels: commit-time facts name the commit; "today's tree" facts were read on 2026-11-04.
The checkboxes record source and commit evidence, not a replay of the experiment.

### Phase 1: Comparison tool and rating decision (AC-5)

Objective: record that a comparison tool and a rater decision existed before the first result.
Read first: [Plan](Plan.md), BACKLOG B-190 in [BACKLOG.md](../../skills/harness-audit/BACKLOG.md).
Constraints: no new rating; do not infer when or how the rating session ran.
Validate: `git --no-pager show --stat be2475a` and `git --no-pager show 37e006f:skills/harness-audit/BACKLOG.md`
Stop when: the first lists `infra_calibration.py` and `test_infra_calibration.py` as added and
the second holds the B-190 text that names 15 repositories and 35 cells.

- [x] `be2475a` (19:15:31) adds `skills/harness-audit/scripts/infra_calibration.py` (128 lines) and
  a test file with 5 tests; the `template` command is documented to hide the tool levels and
  `test_template_hides_the_tool_levels` covers it.
- [x] `37e006f` (21:02:52) rewrites B-190: "the user rates the tool areas himself (decision
  2026-10-27; a second human may follow, a model is not an independent rater)".
- [ ] `Not recorded`: the file `infra-ratings-tool-areas.json` that B-190 names; it is in neither
  the tree at `2146078` nor today's tree.

### Phase 2: First result recorded (AC-3)

Objective: record the first measured agreement and the proposed changes.
Read first: B-215 at `b71d7db`.
Constraints: quote figures as historical; do not recompute them into new claims.
Validate: `git --no-pager show --stat b71d7db`
Stop when: the commit touches only `BACKLOG.md` and `extraction-manifest.json`.

- [x] `b71d7db` (21:30:40) adds B-215: exact 23%, within one level 77%, mean absolute difference
  1.0, tool below the rater in 23 cells and above in 4, with four causes of the two-level gaps.
- [x] The same text says the changes are "Proposed, not yet applied".

### Phase 3: Rule change (AC-4, AC-6, AC-7, AC-8)

Objective: record the aggregation and gate change and its tests.
Read first: [infra_checks.py](../../skills/harness-audit/scripts/infra_checks.py) and the diff of `2146078`.
Constraints: do not edit the frozen score files; do not change `STRICT` here.
Validate: `cd skills/harness-audit && python3 -I tests/test_infra_checks.py`
Stop when: the command exits 0; `git diff --stat b71d7db 2146078` over `scripts/score.py` and
`checks/catalog.yaml` is empty.

- [x] `2146078` adds `STRICT` (six checks) and `check_ok`, and `levels` uses `check_ok` for both
  the held-check count and the gate test.
- [x] `INF-D01` and `INF-V03` leave `GATES` and move to level 2; `INF-A01` moves to level 2.
- [x] New or replaced tests: `test_missing_dockerignore_is_no_longer_a_gate`,
  `test_half_the_locations_failing_fails_the_check` (replaces `test_one_failing_location_fails_the_check`),
  `test_a_clear_majority_of_locations_is_enough` and `test_secret_checks_stay_all_or_nothing`.
- [x] Observed on 2026-11-04 in today's tree: the command printed "Ran 66 tests" and "OK", and the
  focused `python3 -I tests/test_infra_calibration.py` printed "Ran 5 tests" and "OK". The test
  file and `infra_checks.py` have no diff against `2146078`. A passing run at `2146078` or in
  CI is `Not recorded`.

### Phase 4: Evidence bundle (AC-1, AC-2, AC-3, AC-9)

Objective: record what the page, the sidecar and the README contain.
Read first: [Architecture](Architecture.md) sections Code Logic and Data and Storage.
Constraints: no edit of any vote; the page is read, not run.
Validate: `python3 -m json.tool docs/0006-v0.1-infrastructure-calibration-retrospective/research/infra-levels-evaluation.json > /dev/null`
Stop when: the command exits 0 and `git --no-pager show --stat 2146078` lists the README, the
page and the sidecar as added.

- [x] The sidecar has 35 `ratings`, 35 `tool_before` and 35 `tool_after` entries over 15 repositories.
- [x] The page embeds a `SIDE` object equal to the sidecar (parsed and compared by the reviewer).
- [x] Recomputed by the reviewer: 8 of 35 exact and 15 of 35 exact; 27 and 32 within one; mean
  absolute difference 1.00 and 0.66; tool above 4 and 6, below 23 and 14. The README says the same.
- [x] After the change the tool reaches L3 in two cells (`ansible-for-devops` ansible and
  `open-webui` dockerfile), both rated L2, as the README says.
- [ ] `Not recorded`: a browser session of the page, the output of `Save sidecar`, and which
  browser the rater used.

### Phase 5: Relocation (AC-1)

Objective: record how the files reached this folder.
Read first: `git --no-pager show -M --name-status 1b15eeb`.
Constraints: keep the three research files byte-identical.
Validate: `python3 tools/check.py`
Stop when: the command prints PASS and the three blob ids equal those at `2146078`.

- [x] `1b15eeb` (2026-10-28) moves the three files into `docs/0006/research/` as `R100` and adds
  the four topic documents.
- [x] `b745e58` (2026-11-04) moves them into this folder, again as `R100`, and adds the Workflow
  Report and the stage sidecars.

## Acceptance Criteria Traceability

| Criterion | Phase | Evidence |
| --- | --- | --- |
| AC-1 | 4, 5 | sidecar parse, three blob ids equal at `2146078` and today |
| AC-2 | 4 | page source: `hidden` chips, `toolLevel`, `Load sidecar`, `Save sidecar` |
| AC-3 | 2, 4 | B-215 at `b71d7db`, README table, reviewer recomputation |
| AC-4 | 3 | empty `git diff --stat` over `score.py` and `catalog.yaml`, `STRICT` |
| AC-5 | 1, 4 | one `rater` in the sidecar, no other rating file, README Limits |
| AC-6 | 3 | `test_a_clear_majority_of_locations_is_enough` |
| AC-7 | 3 | `test_secret_checks_stay_all_or_nothing` |
| AC-8 | 3 | `test_missing_dockerignore_is_no_longer_a_gate` |
| AC-9 | 4 | `load_ratings` returns `{}` on the sidecar |

## Decision Log

| Decision | Basis |
| --- | --- |
| Keep "ratings are not committed" as a historical statement | the `infra_calibration.py` docstring and the B-215 line written by `2146078` say it; `2146078` also commits the sidecar; the README says "committed on purpose at the owner's request" |
| Keep B-190 "no rating exists yet" and B-202 "no human rated" as historical | both are unchanged by `2146078`; B-202 reads the same in today's tree; the sidecar holds 35 ratings |
| Do not edit the page's embedded check lists | the page lists `INF-D01` and `INF-V03` as level-1 gates, `infra_checks.py` at the same commit does not; the page is byte-identical to `2146078` and the README says the rater saw check lists |
| Do not bridge the sidecar and the `repos` format | `load_ratings` returns `{}` for the sidecar; no code change is in this folder's scope |
| Treat the README percentages as historical, recomputed once | no script writes the sidecar; the reviewer's recomputation matched |
| Record the strict-set observation without judging it | `INF-D06` and `INF-A03` are secret checks by title and are neither strict nor gates |
| Take blindness from the README only | the page embeds the after levels behind a `hidden` attribute; which artifact the rater used is `Not recorded` |
| Label commit-time and today's facts separately | blob ids of the three research files, `infra_checks.py` and `infra_calibration.py` are equal at `2146078` and today |
| Leave unknowns as `Not recorded` | no session log, rater interview, report set or CI log exists in this tree |

## Resume State

- Current phase: none open; this folder is a finished retrospective.
- Last verified: the unit-test runs and the sidecar parse above, on 2026-11-04.
- Open items: a second independent rating; the ratings-committed, no-rating-exists and page
  catalogue conflicts; the sidecar format gap; the strict-set question; the reports and
  repository commits behind the 35 cells.
- Next step: run the Phase 3 and Phase 4 `validate:` commands before relying on any statement here.

## Final Verification

Run `python3 tools/check.py`. It covers frontmatter types, relative links, extraction integrity
and publication patterns, and describes the current tree only. It has no rule specific to the
sidecar (no line of `tools/check.py` mentions it) and says nothing about the quality of the ratings.