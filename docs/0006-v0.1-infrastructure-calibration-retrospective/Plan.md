---
type: 'Plan'
id: '0006'
version: 'v0.1'
title: 'Infrastructure Calibration: Retrospective Plan'
description: 'Evaluation inputs, comparison boundaries and limits for the recorded calibration.'
status: 'active'
doc_scope: 'history'
created: '2026-10-28'
updated: '2026-10-28'
generated: 'agent'
verified: 'unverified'
owner: 'Andreas Elser'
stale_after: '2026-11-11'
tags: [documentation, retrospective]
sources: ['docs/0006-v0.1-infrastructure-calibration-retrospective/research/README.md', 'docs/0006-v0.1-infrastructure-calibration-retrospective/research/infra-levels-evaluation.json', 'git:2146078']
---

# Infrastructure Calibration: Retrospective Plan

## Acceptance Boundaries

| ID | Reconstructed evaluation requirement |
| --- | --- |
| C-1 | Preserve per-area votes and corresponding before/after tool levels in an explicit sidecar. |
| C-2 | Keep tool-level reveal separate from voting and support saving/loading the sidecar. |
| C-3 | Report exact/within-one agreement and error measures without disguising the sample limits. |
| C-4 | Rule changes do not change the frozen main score; sensitive secret gates retain their strictness. |
| C-5 | One-rater evidence is not generalized to independent multi-rater validation. |

## Recorded Sequence

Collect ratings, compare original outputs, evaluate aggregation/gate changes and retain
before/after results. The actual recorded changes are the location-majority rule and
specific gate/level demotions described in the original README, not a new formula inferred here.

## Scope

In scope, as shown by the commits: the tool added in `be2475a`, the rating decision recorded in
`37e006f`, the first result recorded in `b71d7db`, and the rule change, page, sidecar and README
added together in `2146078` (2026-10-27 21:43:44 `+0000`). The three research files are
byte-identical today (blob ids `28c0f5cb`, `69b7a905`, `05f9c994`); they were moved by `1b15eeb`
and `b745e58`.

Out of scope: a second rater, any new rating, a rerun of the audit, any edit of the sidecar
values, the calibration of the 0-100 score (`calibrate.py` and the README's "12 calibration
repos, 6 holdout repos" belong to a different exercise), and the Harness City.

## Acceptance Criteria (Given/When/Then)

These restate C-1 to C-5 as checks that the folder's files support. They describe what the
evidence promises, not a replay of the old run. Test names come from `test_infra_checks.py` at
`2146078`; the results of running them are `Not recorded` by this folder. Page behaviour is read
from its source, not run in a browser.

| ID | Given | When | Then |
| --- | --- | --- | --- |
| AC-1 (C-1) | `research/infra-levels-evaluation.json` | it is parsed | `schema` is `infra-level-evaluation/0.1`, `ratings` has 35 records, and `comparison.tool_before` and `comparison.tool_after` have 35 entries over the same repository and area cells |
| AC-2 (C-2) | `research/infra-level-vote.html` | it is opened and the toggle is not pressed | the tool-level chips carry the `hidden` attribute; `Show tool levels` reveals the after levels, and `Load sidecar` and `Save sidecar` exist |
| AC-3 (C-3) | the sidecar | exact, within-one, mean absolute difference and direction are recomputed | before: 8 of 35 exact, 27 of 35 within one, 1.00, tool above 4 and below 23; after: 15 of 35, 32 of 35, 0.66, above 6 and below 14, equal to the README's 23%, 77%, 43% and 91% |
| AC-4 (C-4) | commits `b71d7db` and `2146078` | `git diff --stat` runs over `scripts/score.py` and `checks/catalog.yaml` | it prints nothing, and `STRICT` holds `INF-X05`, `INF-F03`, `INF-P03`, `INF-K06`, `INF-C03`, `INF-T06` |
| AC-5 (C-5) | the tree at `2146078` and today | it is searched for a rating file other than the sidecar | none is found and the sidecar names one `rater`; the README says "A second rater is still open (B-190)" |
| AC-6 (C-4, edge) | a non-secret check passing in 4 of 5 locations | `levels` runs | the check holds and the failing path stays in the roll-up; `test_a_clear_majority_of_locations_is_enough` |
| AC-7 (C-4, edge) | a secret check failing in one of five locations | `check_ok` runs | it returns false; `test_secret_checks_stay_all_or_nothing` |
| AC-8 (edge) | a Dockerfile with no `.dockerignore` | `levels` runs | `INF-D01` is not in `GATES` and the area can reach level 2; `test_missing_dockerignore_is_no_longer_a_gate` |
| AC-9 (negative, observed limit) | the sidecar | `infra_calibration.load_ratings` reads it | it returns `{}`, so `compare` cannot use the sidecar; observed on today's identical file, not an intended behaviour |

## Assumptions

- The rater's statement that tool levels were not seen while voting comes from the README alone.
  Nothing in the tree verifies it.
- The 35 cells are the 35 `ratings` records; the 15 repositories are the distinct `repo` values.
  Their commit ids and the tool reports are `Not recorded` (`reports/` is ignored by Git).
- The sidecar's `date` of `2026-10-27` is the only time stamp of the votes.
- The percentages in the README are accepted as historical figures and were recomputed by the
  reviewer from the sidecar; the recomputation matched.
- Tests exist for the rule change; this folder does not claim they were run.

## Milestones and Delivery Slices

| Slice | Evidence | Outcome | Criteria |
| --- | --- | --- | --- |
| M1 Tool | `be2475a` (19:15:31) | `infra_calibration.py` with `template` and `compare`, plus 5 tests | AC-9 context |
| M2 Rating decision | `37e006f` (21:02:52) | B-190 says the user rates 15 repositories and 35 cells himself | AC-5 |
| M3 First result | `b71d7db` (21:30:40) | B-215 records 23%, 77%, 1.0 and four causes, changes "not yet applied" | AC-3 |
| M4 Rule change and bundle | `2146078` (21:43:44) | `check_ok`, `STRICT`, three level moves, page, sidecar, README | AC-1, AC-2, AC-3, AC-4, AC-6, AC-7, AC-8 |
| M5 Relocation | `1b15eeb`, `b745e58` | research files moved with 100 percent similarity | AC-1 |

## Risks and Mitigations

| Risk | Mitigation recorded in the tree |
| --- | --- |
| One rater read as validation | README Limits: "the numbers show direction, not accuracy" |
| Fitting the tool to the rated sample | three two-level gaps were left as they are, per the README |
| Secret checks weakened by the majority rule | `STRICT` keeps six checks all-or-nothing; `INF-D06` and `INF-A03` are not in it, see the open questions |
| The sidecar rewritten or normalized | this folder's constraint and the README's "committed on purpose" note |
| The page's check lists read as the current rule | the README lists the demotions; the page itself was not updated, see the open questions |

## Validation Contract

Objective: preserve the recorded evaluation's structure and honest interpretation.
Read first: original README, JSON sidecar and [Architecture](Architecture.md).
Constraints: do not modify votes, create a new rater or claim the calibration was rerun.
Validate: `git show --stat 2146078` and `python3 tools/check.py`.
Stop when: the three original artifacts remain intact and comparison limits are explicit.

Any future calibration needs a separately defined sample/rater protocol and fresh evidence.

## Open Questions

- Conflict, ratings committed. `infra_calibration.py` says "Ratings files are not committed" and
  the B-215 line written by `2146078` says "ratings are not committed" before ending with
  "Ratings, the configurator and the sidecar are in `docs/0006/`". The README says the sidecar is
  "committed on purpose at the owner's request". All three stay as historical statements.
- Conflict, no rating exists. BACKLOG B-190 and B-202 at `2146078` say "no rating exists yet" and
  "no human rated any repo's infrastructure"; B-202 reads the same in today's tree, and the
  sidecar holds 35 ratings. Not corrected here.
- Conflict, page and rule. The page's embedded check lists show `INF-D01` and `INF-V03` as
  level-1 gates and `INF-A01` at level 1; `infra_checks.py` at `2146078` has all three at level 2
  and drops the first two from `GATES`. Whether the rater saw the old lists, the new ones or a
  different page is `Not recorded`.
- Observation, strict set. By title, `INF-D06` (no literal secrets in ENV or ARG) and `INF-A03`
  (no plaintext secrets in variables) are secret checks, and neither is in `STRICT` or `GATES`.
  The README names the six strict checks and does not mention them. Whether that was intended is
  `Not recorded`.
- How were the README percentages computed? `Not recorded`: no script in the tree writes the
  sidecar or reads its schema. The reviewer's recomputation matched.
- Which tool reports and which repository commits were rated? `Not recorded`.
- Which artifact did the rater use, the page or a file from `infra_calibration.py template`?
  `Not recorded`.
- Is there a test that loads or saves the sidecar in the page? `Not recorded`; no file under
  `skills/`, `tools/` or `apps/` mentions the page or the schema name at `2146078`.
- Does the page render with the font stylesheet unreachable? `Not recorded`.
- What protocol should a second rater follow? `Not recorded`; B-215 says only "Next: second rater".
- Why `0.6` for locations? `Not recorded`; `PASS_RATIO` was already `0.6` for the 60% of checks
  per level, with the comment "same rule as the pillars".