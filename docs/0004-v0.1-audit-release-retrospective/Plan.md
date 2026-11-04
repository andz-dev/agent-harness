---
type: 'Plan'
id: '0004'
version: 'v0.1'
title: 'Audit v1.2: Retrospective Acceptance Plan'
description: 'Evidence-derived acceptance boundaries for the recorded v1.2 changes and agreement work.'
status: 'active'
doc_scope: 'history'
created: '2026-10-28'
updated: '2026-10-28'
generated: 'agent'
verified: 'unverified'
owner: 'Andreas Elser'
stale_after: '2026-11-11'
tags: [documentation, retrospective]
sources: ['docs/0004-v0.1-audit-release-retrospective/research/Release-Notes-v1.2.md', 'docs/0004-v0.1-audit-release-retrospective/research/Agreement-Report-v1.2.md']
---

# Audit v1.2: Retrospective Acceptance Plan

## Acceptance Boundaries

| ID | Reconstructed behavior |
| --- | --- |
| V-1 | Placeholder-bearing incomplete guidance does not receive unqualified credit. |
| V-2 | DOC-06 resolves supported path facts mechanically; unresolved cases remain explicit. |
| V-3 | Excerpts and runner candidates use the release's documented budgets. |
| V-4 | Scoring weights/caps remain pinned and model answers remain quote-validated. |
| V-5 | Agreement reports separate verdict agreement, score effects and unresolved differences. |

## Scope

In scope: the three release commits `7fddcc3` (v1.2 placeholders, DOC-06, excerpt budgets,
agreement tool, first records), `8c9342f` (judgement prompt rules 7 and 8) and `b470917` (second
agreement run), with the original [release notes](research/Release-Notes-v1.2.md) and
[agreement report](research/Agreement-Report-v1.2.md). Commit `54babe0` (STA-09 mechanical)
falls between them and is planned in [0003](../0003-v0.1-harness-roadmap-evidence-matched/Plan.md).

Out of scope: Node hook proposals and the roadmap checklist (0003), the infrastructure overlay
(0005), its calibration (0006), Harness City changes and later quality gates (0008). Criteria for
a second human rater, a recalibration or a score change are left out because no evidence shows
any of them happened. The 141-test and 18-repository figures are historical statements, not
acceptance results of this folder.

## Acceptance Criteria (Given/When/Then)

These restate V-1 to V-5 as behavior the commits and their tests support. They describe what the
code was built to do, not a replay of the 2026-10-27 runs.

| ID | Given | When | Then | Evidence |
| --- | --- | --- | --- | --- |
| AC-1 (V-1) | a passing finding whose `found` evidence file still contains `TODO(human)` | `downgrade_placeholders` runs | the finding becomes `fail`, its note names `TODO(human)` and its last evidence item has kind `searched` | `PlaceholderTests.test_pass_on_file_with_placeholder_becomes_fail`, `7fddcc3` |
| AC-2 (V-1 edge) | a finished file with no placeholder | the same step runs | the finding stays `pass` | `test_finished_file_still_passes`, `7fddcc3` |
| AC-3 (V-2) | every backticked path in README, docs and agent files exists | the judgement plan is built | DOC-06 resolves `pass` by script and no DOC-06 task is created | `test_doc06_is_resolved_by_script_when_every_path_exists`, `7fddcc3` |
| AC-4 (V-2 edge) | a release-notes or history file names a removed path | `missing_paths` runs | the history file is skipped | `test_history_files_are_not_checked_for_dead_paths`, `7fddcc3`; its docstring names a fastapi regression |
| AC-5 (V-2 negative) | an agent file names a path that does not exist | the plan is built | DOC-06 stays a judgement task with the missing path as a candidate | `test_missing_path_candidates`, present at `b470917` and unchanged by `7fddcc3` |
| AC-6 (V-3) | agent and README files of 2000 lines each | excerpts are cut | the ORI-09 excerpt lines stay at or below `MAX_TASK_LINES` | `test_excerpt_budget` compares with the constant, so it follows the new value 1000; assertions on 400 and 200 are `Not recorded` |
| AC-7 (V-4) | the scoring module | the tests run | pillar weights, caps, pass ratio and entropy maximum equal the frozen values | `FrozenWeightsTests.test_weights_and_caps_are_frozen`, present at `b470917`; its file is not among the paths `7fddcc3` changes |
| AC-8 (V-4 negative) | a model answer with a forged quote, a quote from a file outside the task, a far line number or a very short quote | `apply_answers` runs | the status becomes `unknown` or the quote is rejected | `test_forged_quote_downgrades_to_unknown`, `test_quote_from_file_outside_the_task_is_rejected`, `test_far_line_number_is_rejected`, `test_trivially_short_quote_is_rejected`, present at `b470917` |
| AC-9 (V-5) | two answer directories sharing some repositories and tasks | `agreement.py` compares them | the rate, Cohen's kappa and every disagreement are listed, and only shared repositories and tasks count | `AgreementTests` (four tests), `7fddcc3` |
| AC-10 (V-5) | two scored runs of the same repositories | the report is written | per-repository score differences are stated | report text in `b470917`; no test, and the procedure is `Not recorded` |
| AC-11 (prompts) | a model note says the requested element is missing, or a tool file carries a generated marker | the prompts are applied | the status must match the note (rule 7); a marked generated copy counts as pointing to `AGENTS.md` (rule 8) | prompt diffs in `8c9342f`; no test isolates them, and ENT-05 agreement moves from 3 of 4 to 7 of 7 while ORI-08 stays 1 of 2 |

## Recorded Sequence

`7fddcc3` imports the v1.2 changes and first records. Prompt correction `8c9342f`
precedes the updated agreement report in `b470917`. Later changes such as mechanical
STA-09 and fixture-aware placeholder detection are not mislabeled as original v1.2 work.

## Milestones and Delivery Slices

Intent per commit comes from the commit messages; the criteria column uses the table above.

| Slice | Evidence | Recorded intent | Criteria |
| --- | --- | --- | --- |
| M1 v1.2 import | `7fddcc3` (16:00:13) | "placeholder downgrade, DOC-06 script check, agreement tool", plus the release notes, first report and index | AC-1 to AC-7, AC-9 |
| M2 STA-09 context | `54babe0` (16:09:58) | "make STA-09 a mechanical check (B-128)"; planned in 0003 | none here |
| M3 Prompt rules | `8c9342f` (16:11:28) | "tighten judgement prompts for ENT-05 and ORI-08 (B-162)"; existing answer sets need re-answering (B-163) | AC-11 |
| M4 Second agreement run | `b470917` (16:25:58) | "second agreement run, 87% agreement (B-164, B-165)" | AC-9, AC-10 |
| M5 Retrospective records | `1b15eeb`, `b745e58` | the four basic documents, the research move and the folder rename | none, record only |

Reviewer judgment inferred from the timestamps: the second run happened on a tree that already
contained M2, which fits the second report having no STA-09 row.

## Assumptions

- Weights stay frozen: `references/FROZEN.sha256` keeps the same `score.py` line across all
  three release commits, and `FrozenWeightsTests` pins the values.
- Historical test counts are statements: the `7fddcc3` commit message says 145 passing, the
  release notes and BACKLOG section 4s say 141. A static count of `def test_` lines under
  `skills/harness-audit/tests` is 137 before and 145 at `7fddcc3` and 147 at `b470917` (reviewer
  count, not a pytest run).
- Runs A and B are model runs: the report calls them "independent subagents". Their
  independence, model names and prompts are `Not recorded`.
- The 15 repositories are those "that have judgement tasks" among the 12 calibration and 6
  holdout repositories (report text); their names appear only in the disagreement tables.
- Answer files are not committed, so none of the agreement figures can be recomputed from the
  repository.
- Backlog identifiers (B-158 and so on) are those in `skills/harness-audit/BACKLOG.md` as
  committed.

## Risks and Mitigations

| Risk | Mitigation recorded in the tree |
| --- | --- |
| A placeholder fix hides a real pass | `PlaceholderTests` pin both the downgrade and the finished-file case; a later fixture correction is planned in 0003 |
| A script DOC-06 pass over-credits | BACKLOG B-157 records that only backticked relative paths with an extension are checked |
| A prompt change leaves old answers in use | BACKLOG B-163 states the old answer sets are not comparable and calls for re-answering |
| Agreement read as human calibration | the release notes list "One rater" under known limits; the report is titled as two model runs |
| A scored file changes without review | `FROZEN.sha256` and manifest records are refreshed in the same commit |
| Small samples inflate or deflate rates | the report prints per-task totals, several of them 1 or 2 |

## Validation Contract

Objective: match release claims to recorded implementation and declared limits.
Read first: original release/agreement files and [Architecture](Architecture.md).
Constraints: historical datasets/answers are not republished or fabricated; no frozen-weight change.
Validate: `git show --stat 7fddcc3`, `git show --stat b470917` and `python3 tools/check.py`.
Stop when: the historical release and later report are distinguishable from fresh checks.

The release's 141-test and 18-repository figures remain historical claims. Current
execution evidence belongs to the current root `task check`, not this reconstructed plan.

Done for this retrospective means: every acceptance row above names a commit or a test that Git
can show, every historical figure is quoted as a statement, and every unresolved question below
stays listed.

## Open Questions

- Which test count is right, 141 or 145? The commit message of `7fddcc3` says 145 and the release
  notes and BACKLOG section 4s say 141. `Not recorded: a pytest run at 7fddcc3`.
- What did `SKILL.md` mean by "they agreed on 34 of 51 in testing"? The first report says 33 of
  49 and the second 47 of 54; the manifest shows `SKILL.md` unchanged by the release commits and
  today's tree still carries the sentence. `Not recorded: a run with 34 of 51`.
- BACKLOG B-160 says "11 of 16" disagreements were `unknown` versus a verdict. The first
  report's table has 16 disagreements and 14 of them involve `unknown` on one side (reviewer
  count). `Not recorded: the basis of the 11`.
- BACKLOG B-165 lists five remaining splits; the second report's table lists seven, adding
  nextjs DOC-06 and vllm DOC-06 (both `pass` versus `unknown`).
- How were the "Effect on scores" figures computed (13 of 15 identical, n8n 78 versus 85,
  opencode 42 versus 48, mean difference 0.9)? `Not recorded: the procedure or tool`.
- Which models ran A and B, and was B-158's re-answer list fully covered?
  `Not recorded: model names, run commands, answer files`.
- Who is the second human rater? `Not recorded: a rater name, ratings or a fresh holdout set`.
- Where are `harness-audit.skill` and `scans/results-table.md`, named by the release notes?
  `Not recorded: either artifact in any ref`.
- Today's BACKLOG B-164 points at `docs/0004-v0.1-audit-release-retrospective/Agreement-Report-v1.2.md`,
  but the file lives under `research/`. A reviewed change to the skill's backlog should fix the path.
