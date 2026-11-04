---
type: 'Implementation'
id: '0004'
version: 'v0.1'
title: 'Audit v1.2: Recorded Release and Agreement'
description: 'Commit-backed release outcomes and the historical agreement result without new experiment claims.'
status: 'active'
doc_scope: 'history'
created: '2026-10-28'
updated: '2026-10-28'
generated: 'agent'
verified: 'unverified'
owner: 'Andreas Elser'
stale_after: '2026-11-11'
tags: [documentation, retrospective]
sources: ['git:7fddcc3', 'git:8c9342f', 'git:b470917', 'docs/0004-v0.1-audit-release-retrospective/research/Agreement-Report-v1.2.md']
---

# Audit v1.2: Recorded Release and Agreement

## Recorded Outcomes

- [x] `7fddcc3` introduces v1.2 code and the three original development-record files.
- [x] `8c9342f` records judgment prompt tightening before the later agreement update.
- [x] `b470917` updates the report to the second independent model comparison.

The report records 47/54 agreement (87%), kappa 0.768, and identical scores for 13
of 15 repositories. These numbers are retained historical statements. No new blind
model run, human rating or original 141-test environment was executed by this reconstruction.

## Unresolved Evidence

- [ ] Independent human calibration beyond the original rater remains unestablished here.
- [ ] Historical external package/Project synchronization is not independently revalidated.
## Phase Detail

Each phase lists what the commit shows. Test counts and agreement figures quoted below are
statements copied from commit messages, the backlog or the reports. Checked boxes mean the
listing or text was read for this retrospective on 2026-11-04, not that a test was run.

### Phase 1: v1.2 import (AC-1 to AC-7, AC-9)

Objective: record the placeholder downgrade, DOC-06 script check, excerpt budgets, agreement tool and first records.
Read first: [Plan](Plan.md), [Architecture](Architecture.md) section Code Logic, `git show --numstat 7fddcc3`.
Constraints: weights stay frozen; the audit never executes audited code; changed runtime files become `reviewed-update` records in `extraction-manifest.json`.
Validate: `git show --stat 7fddcc3`
Stop when: the listing shows `run_checks.py`, `llm_layer.py`, `agreement.py`, `test_agreement.py`, `FROZEN.sha256` and the three files under `docs/0004/`.

- [x] `run_checks.py` gains `PLACEHOLDER = "TODO(human)"` and `downgrade_placeholders` (+23 lines).
- [x] `llm_layer.py` gains `HISTORY_DOC`, a script pass for DOC-06, `MAX_FILE_LINES` 400, `MAX_TASK_LINES` 1000 and 200 runner targets (17 added, 6 removed).
- [x] `agreement.py` (94 lines) and `test_agreement.py` (52 lines, four tests) are added.
- [x] `audit.py` `VERSION` and the `pyproject.toml` version change from `0.1.0` to `1.2.0`.
- [x] BACKLOG sections 4s and 4t are added; `EXTRACTION.md` gains a "Reviewed Updates" section.
- [x] The commit message states "Skill tests: 145 passing; tools/check.py passes." The release notes and BACKLOG say 141. Neither was re-run here.

### Phase 2: STA-09 mechanical, context only

Objective: note that `54babe0` sits between the import and the prompt fix and is not a deliverable of this folder.
Read first: [0003 Implementation](../0003-v0.1-harness-roadmap-evidence-matched/Implementation.md), `git show --stat 54babe0`.
Constraints: do not count its tests or hash refresh as v1.2 import work.
Validate: `git show --stat 54babe0`
Stop when: the listing shows `catalog.yaml`, `llm_layer.py`, `test_run_checks.py`, `test_audit.py` and `FROZEN.sha256`.

- [x] The detector for STA-09 is `key_present` in the catalog at `8c9342f`.
- [ ] Test result for this commit: `Not recorded: pass count in the commit message`.

### Phase 3: Judgement prompt rules (AC-11)

Objective: record the two prompt rules added after the first agreement run.
Read first: BACKLOG section 4u, `git show 8c9342f -- skills/harness-audit/prompts`.
Constraints: the changed prompts alter what judgement runs return, so earlier answer sets are not comparable (B-163).
Validate: `git show --stat 8c9342f`
Stop when: the listing shows both prompt files, `FROZEN.sha256`, `extraction-manifest.json` and `BACKLOG.md`.

- [x] `orientation_quality.md` gains rule 7: the status must match the note.
- [x] `instruction_drift.md` gains rule 8: a symlink, identical copy, import or generated marker counts as pointing to `AGENTS.md`; a hand-written duplicate fails.
- [ ] Test result for this commit: `Not recorded: pass count in the commit message`.

### Phase 4: Second agreement run (AC-9, AC-10)

Objective: record the second model-to-model agreement result and its limits.
Read first: [Agreement report](research/Agreement-Report-v1.2.md), BACKLOG B-164 and B-165.
Constraints: model runs are not a human rater; answer files are not committed.
Validate: `git show --stat b470917`
Stop when: the listing shows the agreement report, the manifest and the backlog.

- [x] The report records 47 of 54 answers in agreement (87 percent), Cohen's kappa 0.768, over 15 repositories; the first run was 33 of 49 over 12.
- [x] The "Effect on scores" section states 13 of 15 repositories scored the same, n8n 78 versus 85, opencode 42 versus 48, mean difference 0.9.
- [ ] How that section was computed: `Not recorded: the procedure or tool`.
- [ ] Test result for this commit: `Not recorded: documentation-only commit message`.

### Phase 5: Retrospective records (no criteria)

Objective: record how the four basic documents and the research files reached today's folder.
Read first: [Workflow Report](Workflow-Report.md), [History crosswalk](../History-Match.md).
Constraints: the original release notes and report are preserved unchanged; the research files are renames with similarity 100 percent (report, notes) and 79 percent (index).
Validate: `git log --name-status --format=%h -- docs/0004 docs/0004-v0.1-audit-release-retrospective`
Stop when: the output shows `1b15eeb` adding four documents and `b745e58` renaming the folder.

- [x] `1b15eeb` adds the four documents and moves the three records under `research/`.
- [x] `b745e58` renames `docs/0004` to this folder and adds the Workflow Report and sidecars.
## Verification Contract

Objective: preserve the release/agreement distinction and its limitations.
Read first: [Plan](Plan.md), original release notes and agreement report.
Constraints: no invented answers, raw private reports or retrospective pass claims.
Validate: `git show --stat b470917` and `python3 tools/check.py`.
Stop when: files, commits and historical figures agree with their sources.

The original index's "first comparison" description is older than the report body;
the later body and its Git update identify the current historical run.

## Acceptance Criteria Traceability

| Criterion | Phase | Evidence |
| --- | --- | --- |
| AC-1, AC-2 | 1 | `PlaceholderTests` in `test_run_checks.py`, `7fddcc3` |
| AC-3, AC-4 | 1 | two tests added to `test_llm_layer.py`, `7fddcc3` |
| AC-5 | 1 | `test_missing_path_candidates`, present before and after `7fddcc3` |
| AC-6 | 1 | `test_excerpt_budget` against `MAX_TASK_LINES`; the 400 and 200 values are constants without a dedicated test |
| AC-7 | 1 and 3 | `FrozenWeightsTests` in `test_score.py`; `score.py` hash line unchanged across the release commits |
| AC-8 | 1 | `ApplyTests` in `test_llm_layer.py`, present at `b470917` |
| AC-9 | 1 and 4 | `AgreementTests`, `7fddcc3`; reports in `7fddcc3` and `b470917` |
| AC-10 | 4 | report text in `b470917`; computation `Not recorded` |
| AC-11 | 3 and 4 | prompt diffs in `8c9342f`; per-task rates in the second report |

## Decision Log

| Decision | Basis |
| --- | --- |
| Match only the three release commits and treat `54babe0` as context | Plan Scope; `54babe0` is planned in 0003 |
| Keep model agreement separate from human calibration | the report calls both runs "independent subagents"; the release notes list "One rater" |
| Quote historical pass counts only as statements | the `7fddcc3` message says 145, the release notes and BACKLOG 4s say 141; a static count of `def test_` lines is 145 at `7fddcc3` (reviewer count, not a pytest run), which matches the message but does not explain 141 |
| Keep the `SKILL.md` sentence "34 of 51" unedited and log it | the first report says 33 of 49 and the second 47 of 54; the manifest shows `SKILL.md` unchanged by the release commits; no run with 34 of 51 is recorded |
| Keep BACKLOG B-160 "11 of 16" unedited and log it | the first report's disagreement table has 16 rows and 14 involve `unknown` (reviewer count) |
| Note that B-165 omits two second-run splits | the second report lists nextjs DOC-06 and vllm DOC-06, which B-165 does not name |
| Do not claim the 87 percent rise is due to the prompt rules alone | the two runs differ in repository count (12 and 15), task ids (STA-09 absent in the second) and DOC-06 comparisons (12 and 9) |
| Record the second run as taking place after `54babe0` | commit timestamps 16:09:58 and 16:25:58; reviewer judgment, run times are `Not recorded` |
| Do not edit the skill's backlog from this folder | today's B-164 path lacks `research/`; fixing it needs a reviewed runtime-adjacent change |

## Resume State

- Current phase: none open; this folder is a finished retrospective.
- Last verified: the `git show --numstat` listings of `7fddcc3`, `8c9342f` and `b470917`, the
  two report versions and the code at `b470917`, read when this document was deepened.
- Open items: the three count conflicts in the Decision Log, the "Effect on scores" procedure,
  runs A and B model details, a second human rater, the missing package and score table, and the
  B-164 path.
- Next step: run the Phase 1 `Validate:` command before relying on any v1.2 statement.

## Final Verification

Run `python3 tools/check.py`. It validates the current tree only: frontmatter types, local links,
extraction integrity and publication patterns. It does not re-run the 2026-10-27 tests or the two
agreement runs. The release commits' own regression results are `Not recorded` beyond the
commit-message statement of 145 passing tests and the release-notes statement of 141.
