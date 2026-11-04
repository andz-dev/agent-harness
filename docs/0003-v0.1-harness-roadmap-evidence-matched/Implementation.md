---
type: 'Implementation'
id: '0003'
version: 'v0.1'
title: 'Harness Roadmap: Matched Outcomes'
description: 'Implemented roadmap pieces and unresolved decisions, separated by evidence.'
status: 'active'
doc_scope: 'history'
created: '2026-10-28'
updated: '2026-10-28'
generated: 'agent'
verified: 'unverified'
owner: 'Andreas Elser'
stale_after: '2026-11-11'
tags: [documentation, retrospective]
sources: ['git:7fddcc3', 'git:b470917', 'git:54babe0', 'git:37e006f', 'docs/0003-v0.1-harness-roadmap-evidence-matched/research/Repo Harness Next Steps.md']
---

# Harness Roadmap: Matched Outcomes

## Recorded Implementation

- [x] `7fddcc3`: v1.2 placeholder handling, DOC-06 and excerpt changes.
- [x] `b470917`: updated independent model-agreement record, not a second human rater.
- [x] `54babe0`: STA-09 becomes mechanical.
- [x] `37e006f`: Node hook/package patch proposals, not automatic installation.
- [x] `90e9a52`: later Python fixture placeholder correction with regression evidence.

## Still Open in the Available Evidence

- [ ] Establish a second independent human calibration rater and fresh holdout evidence.
- [ ] Resolve remaining formatter, generalized adoption and platform-scope decisions.
- [ ] Independently establish external Project/package synchronization if needed.

These are evidence dispositions, not a new authorization to execute the roadmap.
Do not mark all three original phases complete because selected later commits exist.

## Phase Detail

Each phase lists what the commit shows. Pass counts quoted below are statements copied from
commit messages or the backlog, not results of a run made for this retrospective.

### Phase 1: Roadmap preserved (no criteria)

Objective: record that the roadmap text exists in the repository as of `23251df`.
Read first: [Plan](Plan.md), [research/Repo Harness Next Steps.md](research/Repo%20Harness%20Next%20Steps.md).
Constraints: keep the owner's body unchanged; version labels, scores and estimates in it are not new results.
Validate: `git ls-tree -r --name-only 23251df docs/0003`
Stop when: the output lists `docs/0003/README.md` and `docs/0003/Repo Harness Next Steps.md`.

- [x] Both files are in the `23251df` tree.
- [x] The four basic documents of this folder were added later in `1b15eeb`.

### Phase 2: v1.2 trust fixes (AC-1, AC-2, AC-5, AC-6, AC-7, AC-9)

Objective: record placeholder downgrade, DOC-06 by script, larger excerpts and the agreement tool.
Read first: [Architecture](Architecture.md) section Code Logic; `git show 7fddcc3 --stat`.
Constraints: weights stay frozen; the audit never executes audited code; changed runtime files are recorded as reviewed updates in `extraction-manifest.json`.
Validate: `git show --stat 7fddcc3`
Stop when: the listing shows `run_checks.py`, `llm_layer.py`, `agreement.py`, their tests and `references/FROZEN.sha256`.

- [x] `run_checks.py` gains `PLACEHOLDER = "TODO(human)"` and `downgrade_placeholders`.
- [x] `llm_layer.py` gains `HISTORY_DOC`, a script pass for DOC-06, `MAX_FILE_LINES` 400, `MAX_TASK_LINES` 1000 and 200 runner targets.
- [x] `agreement.py` and `test_agreement.py` are added.
- [x] The commit message states "Skill tests: 145 passing; tools/check.py passes." The release notes and backlog say 141. Neither was re-run here.

### Phase 3: STA-09 mechanical (AC-8)

Objective: record the roadmap's STA-09 decision as implemented.
Read first: `git show 54babe0 -- skills/harness-audit/checks/catalog.yaml`.
Constraints: formatters do not count as linters; frozen hashes and manifest are refreshed with the change.
Validate: `git show --stat 54babe0`
Stop when: the listing shows `catalog.yaml`, `llm_layer.py`, `test_run_checks.py`, `test_audit.py` and `FROZEN.sha256`.

- [x] The detector changes from `llm` to `key_present` for ruff, pylint, flake8, eslint, biome and oxlint configs.
- [x] The commit message says re-scoring all 18 repositories left every score unchanged.
- [ ] Test result for this commit: `Not recorded: pass count in the commit message`.

### Phase 4: Independent agreement evidence (AC-9)

Objective: record the second model-to-model agreement run.
Read first: [Agreement report](../0004-v0.1-audit-release-retrospective/research/Agreement-Report-v1.2.md).
Constraints: model runs are not a human rater; answer files are not committed.
Validate: `git show --stat b470917`
Stop when: the listing shows the agreement report, the manifest and the backlog.

- [x] The report records 47 of 54 answers in agreement, Cohen's kappa 0.768, over 15 repositories.
- [ ] Test result for this commit: `Not recorded: documentation-only commit message`.

### Phase 5: Node hook proposal (AC-10, AC-11, AC-12)

Objective: record that bootstrap proposes Node hooks as a patch, never as an applied edit.
Read first: `git show 37e006f -- skills/harness-audit/scripts/bootstrap.py`.
Constraints: the patch entry carries `apply: False`; an existing hook manager is respected.
Validate: `git show --stat 37e006f`
Stop when: the listing shows `bootstrap.py`, `test_bootstrap.py`, the manifest and the backlog.

- [x] `gen_husky` and `gen_husky_patch` are added, plus two proposal entries.
- [x] `NodeHooksTests` adds five tests, including that `--apply` does not write the patch.
- [ ] Test result for this commit: `Not recorded: pass count in the commit message`.

### Phase 6: Placeholder fixture correction (AC-3, AC-4)

Objective: record the later fix for quoted Python fixture strings.
Read first: `git show 90e9a52 -- skills/harness-audit/scripts/run_checks.py`.
Constraints: active placeholders in comments, docstrings and `NotImplementedError` still block; assertions are not weakened.
Validate: `git show --stat 90e9a52`
Stop when: the listing shows `run_checks.py` and `test_run_checks.py`.

- [x] `placeholder_count` is added and used by `downgrade_placeholders`.
- [x] The commit message states "task check passed (251 skill tests plus 3 subtests, 13 tooling tests and 18 browser cases)". It is a historical statement.

## Verification and Handoff

Objective: preserve the phase/commit correspondence without rerunning old experiments.
Read first: [Plan](Plan.md), original roadmap and v1.2 records in 0004.
Constraints: no weight changes, fabricated ratings or implicit bootstrap application.
Validate: `git show --stat 54babe0` and `python3 tools/check.py`.
Stop when: claimed source changes match Git and remaining decisions are explicit.
Historical counts are not fresh test results; current checks live in the root Taskfile.

## Acceptance Criteria Traceability

| Criterion | Phase | Evidence |
| --- | --- | --- |
| AC-1, AC-2 | 2 | `PlaceholderTests` in `test_run_checks.py`, `7fddcc3` |
| AC-3, AC-4 | 6 | two tests added to `test_run_checks.py`, `90e9a52` |
| AC-5, AC-6 | 2 | two tests added to `test_llm_layer.py`, `7fddcc3` |
| AC-7 | 2 | constants in `llm_layer.py`; no dedicated test recorded |
| AC-8 | 3 | `Sta09MechanicalTests`, `54babe0` |
| AC-9 | 2 and 4 | `AgreementTests`, `7fddcc3`; report in `b470917` |
| AC-10, AC-11, AC-12 | 5 | `NodeHooksTests`, `37e006f` |

## Decision Log

| Decision | Basis |
| --- | --- |
| Match only commits whose diffs show the roadmap item | Git diffs of `7fddcc3`, `54babe0`, `37e006f` |
| Do not mark roadmap phases 2 and 3 complete | no second human rater is recorded; Azure DevOps (B-155) is open in the backlog at `37e006f` |
| Keep model agreement separate from human calibration | backlog B-190: "a model is not an independent rater" |
| Record backlog decisions without rewriting the checklist above | B-144 (formatter-only, `37e006f`), B-151 (Node hooks first, `37e006f`) and Go out of scope (`20b21f2`) resolve open decisions that the first list still shows open; a reviewed change should reconcile them |
| Quote historical pass counts only as statements | commit messages give 145 and 141 for the same release; no re-run exists |

## Resume State

- Current phase: none open; this folder is a finished retrospective.
- Last verified: the `git show --stat` listings above, read when this document was deepened.
- Open items: second human rater, fresh holdout, Azure DevOps and monorepo proposals, and the
  checklist reconciliation named in the Decision Log.
- Next step: run the Phase 2 `Validate:` command before relying on any v1.2 statement.

## Final Verification

Run `python3 tools/check.py`. It validates the current tree only, including integrity and
document checks; it does not re-run the 2026-10-27 experiments. The roadmap commits' own
regression results are `Not recorded` beyond the commit-message statements quoted above.