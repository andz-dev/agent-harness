---
type: 'Plan'
id: '0003'
version: 'v0.1'
title: 'Harness Roadmap: Evidence-Matched Plan'
description: 'Roadmap phases and acceptance boundaries reconciled with later commits.'
status: 'active'
doc_scope: 'history'
created: '2026-10-28'
updated: '2026-10-28'
generated: 'agent'
verified: 'unverified'
owner: 'Andreas Elser'
stale_after: '2026-11-11'
tags: [documentation, retrospective]
sources: ['docs/0003-v0.1-harness-roadmap-evidence-matched/research/Repo Harness Next Steps.md', 'docs/0004-v0.1-audit-release-retrospective/research/Release-Notes-v1.2.md']
---

# Harness Roadmap: Evidence-Matched Plan

## Acceptance Boundaries

| ID | Observable requirement | Evidence state |
| --- | --- | --- |
| R-1 | Incomplete placeholder guidance does not earn a false pass. | v1.2 implementation; later fixture correction in `90e9a52` |
| R-2 | Script-resolvable paths and larger excerpts reduce avoidable unknowns. | Recorded in `7fddcc3` and release notes |
| R-3 | Calibration precedes any weight change. | Gate preserved; second human rater not established |
| R-4 | Bootstrap proposes reviewable changes separately from static audit. | Existing preview and `37e006f`; generalized adoption remains proposed |

## Scope

In scope: the owner's roadmap note committed in `23251df` and the later commits that match it:
`7fddcc3` (v1.2 placeholders, DOC-06, excerpts, agreement tool), `54babe0` (STA-09), `b470917`
(second agreement run), `37e006f` (Node hook proposal) and the placeholder fixture correction
in `90e9a52`. Intent per commit is recorded in the [Implementation](Implementation.md) phases.

Out of scope: the infrastructure overlay ([0005](../0005-v0.1-infrastructure-overlay-matched/Plan.md)),
calibration of that overlay ([0006](../0006-v0.1-infrastructure-calibration-retrospective/Plan.md))
and later quality gates ([0008](../0008-v0.1-harness-history-and-quality/Plan.md)). Go support is
out of scope by the backlog decision added in `20b21f2`. Acceptance criteria for a second human
rater and for recalibration are left out: no evidence shows either happened.

## Acceptance Criteria (Given/When/Then)

These restate R-1 to R-4 as behavior the commits and their tests support. They describe what
the code was built to do, not a replay of the old run.

| ID | Given | When | Then | Evidence |
| --- | --- | --- | --- | --- |
| AC-1 (R-1) | a passing finding whose evidence file still contains `TODO(human)` | `run_checks.downgrade_placeholders` runs | the finding becomes `fail` with a note naming the file | `test_pass_on_file_with_placeholder_becomes_fail`, `7fddcc3` |
| AC-2 (R-1) | a finished file with no placeholder | the same step runs | the finding stays `pass` | `test_finished_file_still_passes`, `7fddcc3` |
| AC-3 (R-1 edge) | Python test files that contain `TODO(human)` only inside a quoted string | VER-01 runs | VER-01 still passes | `test_test_fixture_strings_do_not_erase_python_test_presence`, `90e9a52` |
| AC-4 (R-1 negative) | Python test files with the marker in a comment, a docstring or a `NotImplementedError` call | VER-01 runs | VER-01 fails | `test_active_python_placeholders_still_block_test_presence`, `90e9a52` |
| AC-5 (R-2) | every backticked path in README, docs and agent files exists | the judgement plan is built | DOC-06 resolves as `pass` by script and no model task is needed | `test_doc06_is_resolved_by_script_when_every_path_exists`, `7fddcc3` |
| AC-6 (R-2 edge) | a changelog, release-notes or history file names a path that no longer exists | `missing_paths` runs | that file is skipped | `test_history_files_are_not_checked_for_dead_paths`, `7fddcc3` |
| AC-7 (R-2) | an agent file longer than 250 lines | excerpts are cut | up to 400 lines per file and 1000 per task are kept, and 200 runner targets | constants in `llm_layer.py` at `7fddcc3`; no dedicated test name recorded |
| AC-8 (STA-09) | a linter config for ruff, oxlint and similar, or only a formatter | the check runs | rule-id linters pass and a formatter-only repository fails | `test_ruff_and_oxlint_pass`, `test_formatter_only_fails`, `54babe0` |
| AC-9 (R-3) | two independent answer sets for the same tasks | `agreement.py` compares them | per-task agreement, Cohen's kappa and every disagreement are listed | `AgreementTests` in `test_agreement.py`, `7fddcc3` |
| AC-10 (R-4) | a Node repository without a hook manager | bootstrap proposes files | `.husky/pre-commit` and `package.json.patch` are proposed | `test_node_repo_gets_husky_hook_and_a_patch_proposal`, `37e006f` |
| AC-11 (R-4 negative) | the same repository and `--apply` | bootstrap writes | the patch is not written into the repository | `test_apply_never_writes_the_patch_into_the_repository`, `37e006f` |
| AC-12 (R-4 edge) | a repository with an existing hook manager, or a Python repository | bootstrap proposes files | no husky hook is proposed | `test_existing_hook_manager_is_respected`, `test_python_repos_do_not_get_husky`, `37e006f` |

## Phases

1. Make measurements trustworthy: placeholders, DOC-06 and excerpts.
2. Widen calibration evidence and compare independent judgments before recalibration.
3. Improve bootstrap/fix plans within explicit safety boundaries.

This sequencing comes from the original roadmap, not a newly approved implementation
order. Go support, Azure DevOps and a generalized adoption workflow are not silently added.

## Milestones and Delivery Slices

| Slice | Evidence | Outcome | Criteria |
| --- | --- | --- | --- |
| M1 Roadmap preserved | `23251df` | roadmap note and index stored as `docs/0003/` | none, record only |
| M2 v1.2 trust fixes | `7fddcc3` | placeholder downgrade, DOC-06 by script, larger excerpts, `agreement.py` | AC-1, AC-2, AC-5, AC-6, AC-7, AC-9 |
| M3 STA-09 | `54babe0` | detector becomes `key_present` | AC-8 |
| M4 Agreement evidence | `b470917` | second run recorded: 47 of 54 answers agree | AC-9 |
| M5 Node hooks | `37e006f` | husky hook and patch proposal | AC-10, AC-11, AC-12 |
| M6 Fixture correction | `90e9a52` | quoted fixture strings no longer cap VER-01 | AC-3, AC-4 |

## Assumptions

- Weights stay frozen: the release notes say a test pins them and `references/FROZEN.sha256` is
  refreshed by `7fddcc3` and `54babe0`. The name of that test is `Not recorded`.
- Historical test counts are statements, not fresh results: the `7fddcc3` commit message says
  145 passing, while the release notes and the backlog say 141.
- Agreement between two model runs is not human calibration; the backlog says a model is not
  an independent rater.
- Backlog identifiers (B-150 and so on) are those in `skills/harness-audit/BACKLOG.md` as
  committed. Roadmap items beyond that file are proposals.

## Risks and Mitigations

| Risk | Mitigation recorded in the tree |
| --- | --- |
| A placeholder fix hides a real pass | `90e9a52` narrows Python detection to active comments, docstrings and `NotImplementedError`, with a negative test |
| A script DOC-06 pass gives false coverage | backlog B-157 records that only backticked relative paths with an extension are checked |
| A scored file changes without review | `references/FROZEN.sha256` and manifest baselines are refreshed in the same commit |
| Bootstrap changes a repository unasked | `apply: False` on the patch entry and a test that `--apply` leaves it unwritten |
| Phase 2 evidence is claimed from model runs | the release notes list "One rater" under known limits |

## Validation Contract

Objective: reconcile roadmap requirements with actual implementation evidence.
Read first: original roadmap, [Architecture](Architecture.md), [Implementation](Implementation.md).
Constraints: frozen weights; audit never executes audited code; no inferred rater approval.
Validate: `git show --stat 7fddcc3` and `python3 tools/check.py`.
Stop when: each historical completion claim has a source and unresolved decisions stay open.
Current runtime changes require their own focused regression and `task check`.

Done for this retrospective means: every row above names a commit or test that Git can show,
and every unresolved roadmap decision stays listed below.

## Open Questions

- Who is the second human rater, and did they score the 18 repositories blind?
  `Not recorded: a rater name, ratings or a fresh holdout set`.
- Is the Implementation checklist's "formatter" and "platform-scope" open item still open? The
  backlog records B-144 (no credit for formatter-only repositories, decided by the user
  2026-10-27, committed in `37e006f`) and a Go-out-of-scope decision (`20b21f2`).
- Azure DevOps (B-155) is open in the backlog at `37e006f`; B-188 there says a diff-based merge
  mode supersedes B-151 to B-156 scope. Whether it was built is for later folders.
- Which test count is right, 141 or 145? `Not recorded: a re-run at 7fddcc3`.
- Roadmap step "Sync the Project" has no repository evidence: `Not recorded: Project sync`.