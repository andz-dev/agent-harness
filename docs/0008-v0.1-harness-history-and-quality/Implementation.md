---
type: 'Implementation'
id: '0008'
version: 'v0.1'
title: 'Harness History and Quality Implementation'
description: 'Executed evidence, remaining milestones and restart state for the retrospective quality work.'
status: 'active'
doc_scope: 'history'
created: '2026-10-28'
updated: '2026-10-28'
generated: 'agent'
verified: 'unverified'
owner: 'Andreas Elser'
sources: ['Plan.md', 'Architecture.md', 'Map.md', 'Ideation-Book.md']
stale_after: '2026-11-11'
tags:
  - 'documentation'
---

# Harness History and Quality Implementation

## Context

The [Plan](Plan.md#acceptance-criteria) owns AC-1 through AC-14.
[Architecture](Architecture.md) owns component names, runtime boundaries and receipt
storage. This is the owner's reduced four-artifact retrospective: testing scenarios
live in Plan/Architecture and executable tests, not fabricated Test-Plan or ontology
stages. Existing imported artifacts are references, not newly executed workflow steps.

No grilling session, historical pass record, deployment, client setup or Git commit is
created. Evidence recorded below applies to this working tree and the observed local
environment unless a specific commit is named.

## M1: Basic Retrospective

Objective: reconstruct the requested documents and their real provenance (AC-1/2).
Read first: Map historical outline and Ideation decisions.
Constraints: preserve old paths and distinguish committed history from working-tree work.
Validate: `python3 tools/check.py`, plus the architecture-model/change-set validators.
Stop when: requested artifacts, metadata, sources and derived models validate.

- [x] Inspect local commits through `8deb536`; record the current uncommitted boundary.
- [x] Create automatic Map, Ideation Book, Plan and Architecture in versioned folder 0008.
- [x] Derive the architecture model; owning validator reports zero issues.
- [x] Complete artifact metadata, citation/diagram verification and document entry points.
- [x] Validate the basic bundle and record the reduced-workflow exceptions.

## M2: Evidence-Backed Repairs

Objective: fix reproduced self-audit/gate defects, not maximize a score (AC-11/12).
Read first: Ideation risks and the adjacent detector tests.
Constraints: preserve real placeholder detection and tracked-output publication rejection.
Validate: `task --dir skills/harness-audit test -- tests/test_run_checks.py` and `task tools:test`.
Stop when: positive cases and must-fail canaries demonstrate both boundaries.

- [x] Reproduce the false no-tests cap with quoted Python fixture placeholders.
- [x] Interpret Python comments/docstrings/unimplemented stubs structurally.
- [x] Preserve active placeholder rejection; 42 detector tests and three subtests pass.
- [x] Record original 33/100 and corrected-engine 55/100 baselines separately.
- [x] Repair source-document validation scanning ignored raw audit reports.
- [x] Add source/publication regression canaries for ignored and tracked output; four canaries pass.

## M3: Unattended City Browser Tests

Objective: run real city regressions through a repeatable local/CI command (AC-3..7).
Read first: app DESIGN.md, app AGENTS.md and check_city.js.
Constraints: trusted synthetic app only; no network dependency or unknown-server reuse.
Validate: `task app:test`.
Stop when: desktop/mobile tests, actual PNG downloads, offline/network and error gates pass.

- [x] Add exact locked Playwright 1.64.1 development dependency and matching Chromium setup.
- [x] Exercise city/transit selection, airport controls and independent support buildings.
- [x] Exercise layer/rebuild/GPU stability and actual nonblank PNG downloads.
- [x] Verify offline packaging with network blocked and retain synthetic failure artifacts.
- [x] Wire the same browser command into Task and SHA-pinned CI steps; missing prerequisites fail explicitly.

`task app:test` executed 18 cases: all passed, zero skipped/flaky/unexpected, measured
duration 607.1 seconds with software rendering. The first mobile four-tier capture
exceeded a 45-second budget after reaching all four states; its unchanged assertions
passed after a measured 90-second per-test budget was set. No test was removed or retried.

## M4: Comparable Static Audit History

Objective: retain immutable, compatible observations without executing audited code (AC-8..10/14).
Read first: Architecture data/storage and the report schema.
Constraints: explicit inputs, no excerpts/secrets, no replacement of existing receipts.
Validate: `task tools:test` and `python3 tools/audit_history.py --help`.
Stop when: recording/comparison works and malformed/incompatible inputs fail safely.

- [x] Implement owner-only, project-rooted immutable receipt recording.
- [x] Record report/Git/engine/catalog identity, score, levels, findings and limitation digests.
- [x] Compare compatible findings with explicit added/removed/changed states.
- [x] Reject repository/engine/catalog/schema mismatches and invalid or unsafe storage.
- [x] Record corrected baseline and final observation with honest working-tree caveats.

`task tools:test` passes 13 cases. The real compatible comparison is 55 to 55, no changed
check states and no mechanical regressions. Both observations retain seven unanswered
judgment checks. New untracked documents/manifests/tests are not credited as committed
audit evidence. The recorder explicitly discloses that Git state is observed at recording,
untracked contents are not fingerprinted and engine fingerprints are not process attestation.

## M5: Skill and Contributor Guidance

Objective: make runtime-test permission and history limits unambiguous (AC-13).
Read first: audit read-only boundary, Plan scope and existing contributor commands.
Constraints: no automatic hooks, client configuration or execution of audited code.
Validate: `python3 tools/check.py` and the skill's existing checks.
Stop when: commands, conditions and limits are reachable without bloating the skill entry.

- [x] Add a concise skill pointer to testing/history reference guidance.
- [x] Describe owner-authorized runtime tests separately from static audit observations.
- [x] Add contributor and root documentation entry points for the new commands and bundle.
- [x] Update only intentionally changed extraction baselines, preserving source hashes; integrity gate passes.

## M6: Consolidated Verification

Objective: demonstrate the actual result and preserve a truthful handoff (all ACs).
Read first: Plan acceptance criteria and all named verification gates.
Constraints: never delete, skip, weaken or narrow tests to make checks pass.
Validate: `task check`.
Stop when: required gates pass or an exact unresolved limitation is recorded.

- [x] Run full Python, tool, browser, documentation, build and integrity checks through `task check`.
- [x] Verify five Mermaid renders, all 13 cited local commits, citation QA (zero errors/warnings), metadata and derived model/change-set.
- [x] Inspect browser screenshots and measured receipt comparisons.
- [x] Update this record with actual outcomes, local artifact paths and residual gaps.

## Acceptance Criteria Traceability

Added by a retrospective deepening pass on 2026-11-04. The milestone column follows the
[Plan](Plan.md#workstreams) workstreams table. The "stated here" column quotes only evidence
already in this file; the "anchor" column names a test or code location read with
`git show 90e9a52:<path>` (commit 2026-10-28 14:09:55 +0100). A cell reading `Not recorded:` marks
evidence this file and the anchors do not provide. No result below was re-run in this pass.

<!-- atlas:table=acceptance-traceability -->

| AC | Milestone | Evidence stated here | Anchor at `90e9a52` | Gap |
| --- | --- | --- | --- | --- |
| AC-1 | M1 | M1: inspect local commits through `8deb536` and record the uncommitted boundary; M6: all 13 cited local commits verified | Map historical outline | Not recorded: the command used to verify the 13 commits |
| AC-2 | M1 | M1: Map, Ideation Book, Plan and Architecture created in folder 0008; Post-Commit Handoff says earlier numbered folders are preserved | the four documents in `docs/0008-v0.1-harness-history-and-quality/` | none |
| AC-3 | M3 | M3: `task app:test` executed 18 cases, all passed, zero skipped, flaky or unexpected, 607.1 seconds; Final Results: 652.0 seconds | `playwright.config.js` projects `desktop-chromium` and `mobile-chromium`; 3 spec files with 3 tests each | none |
| AC-4 | M3 | M3: exercise city and transit selection, airport controls and independent support buildings | `city.spec.js` "each synthetic city keeps its station and a contained layout"; `airport.spec.js` two support-control tests | Not recorded: a separate assertion for the low-level station and transit rules; this file only says "transit selection" |
| AC-5 | M3 | M3: actual nonblank PNG downloads; offline packaging with network blocked; 18 cases passed | `export.spec.js` "PNG download includes descriptions without changing the live camera" and "offline standalone renders and exports with all network requests blocked" | Not recorded: this file does not state the description-text or unchanged-camera assertion; only the test title does |
| AC-6 | M3 | M3: layer, rebuild and GPU stability exercised; Stop-when names the error and network gates | `airport.spec.js` "full airport regression preserves levels, materials, GPU state and PNG output"; `fixtures.js` `observedErrors` | none |
| AC-7 | M3 | M3: same browser command wired into Task and SHA-pinned CI steps, missing prerequisites fail explicitly | `Taskfile.yml` `check` runs `app:test`; `.github/workflows/check.yml` runs `task check` | Not recorded: any remote CI run (Final Results says none is claimed) |
| AC-8 | M4 | M4: immutable owner-only receipts record report, Git, engine and catalog identity, score, levels, findings and limitation digests | `tests/test_audit_history.py` `test_record_is_compact_immutable_and_owner_only` | none |
| AC-9 | M4 | M4: added, removed and changed states; mismatches rejected; real comparison 55 to 55 | `test_compare_reports_explicit_check_and_score_changes`, `test_compare_refuses_different_engine_fingerprints`, `test_compare_refuses_repository_catalog_and_clone_mismatches` | none |
| AC-10 | M4 | M4: Git state observed at recording, untracked contents not fingerprinted, seven unanswered judgments retained | `record` stores `clone_mode` and a `provenance_limit` text | Not recorded: a shallow-clone run or test result |
| AC-11 | M2 | M2: Python comments, docstrings and unimplemented stubs read structurally; active placeholder rejection preserved; 42 detector tests and three subtests pass | `skills/harness-audit/scripts/run_checks.py` (27 lines changed) and `tests/test_run_checks.py` (23 lines added) | none |
| AC-12 | M2 | M2: source-document scan no longer reads ignored raw reports; four canaries pass | `tests/test_repo_quality.py` four tests including `test_tracked_private_output_still_fails_publication` | none |
| AC-13 | M5 | M5: skill pointer, runtime tests described apart from static observations, contributor and root entry points | `skills/harness-audit/references/TESTING-AND-HISTORY.md` section "Two Evidence Paths" | Not recorded: this file does not state the comparison or freshness limits named in AC-13; the reference file's section "Repeated Static Audits" states some, for example that engine or catalog changes need a fresh baseline |
| AC-14 | M4 | M4: malformed or incompatible inputs fail safely; invalid or unsafe storage rejected | `main` in `tools/audit_history.py` prints a bounded JSON error (400 characters) to stderr and returns 2 | Not recorded: an observed exit code in this file |

Every criterion also falls under M6, whose recorded evidence is the aggregate `task check` result
in Resume State and Final Results.

## Decision Log

| Decision | Evidence and consequence |
| --- | --- |
| Reduced retrospective | Owner explicitly requested four basic docs and automatic discovery; no full-chain completion claim |
| Preserve original reports | 33/100 arose from quoted fixture placeholders; corrected engine reports 55/100 before remaining work |
| Genuine stub guard stays active | Comments, docstrings and explicit NotImplementedError stubs remain blocked by regression tests |
| No client onboarding | Existing Copilot/Claude entry points remain unchanged; client loading stays unverified |
| Logging override | Reuse bounded developer CLI result/error receipts and native runner/CI logs; no service-style logging framework is added |
| No automatic baseline updates | History receipts are immutable; incompatible metrics are rejected and screenshots are not auto-approved |
| Browser time budget | Preserve all assertions and zero retries; allow measured software-WebGL cost with a 90-second case limit and 15-minute aggregate limit |
| No fabricated score gain | Corrected compatible observations remain 55/100; commit new files and re-audit before claiming their score effect |

## Resume State

- Current milestone: implementation committed as `90e9a52`; documentation handoff finalized after that commit.
- Last verified evidence: aggregate `task check` passed: 251 skill tests plus three subtests, 13 tool tests, 18 browser cases with zero skipped/flaky/unexpected, deterministic builds and integrity/docs/publication checks.
- Open blockers: none; client configuration and historical CI verification are deliberately out of scope.
- Updated: 2026-10-28.

## Final Results

The requested basic bundle, browser automation and history tooling are implemented and
the full aggregate gate passed. The final browser run executed all 18 cases in 652.0
seconds on software-rendered Chromium. The Python suite passed 251 tests and three
subtests; root tooling passed 13 tests. No browser case was skipped or retried.

No source repository was executed by the auditor. Real runtime verification ran only
this trusted development checkout and its synthetic city fixtures. CI wiring is added,
but no remote CI pass or live client instruction loading is claimed. The owner subsequently
requested commit `90e9a52`; no new branch was created. Its fresh pre-commit `task check`
also passed, including all 18 browser cases. This documentation follow-up does not
automatically create another commit.

Local evidence is ignored, not published: `reports/self-audit/before/`,
`reports/self-audit/before-corrected/`, `reports/self-audit/after/`, app `test-results/`
and `playwright-report/`. Comparable receipt IDs are
`20261028T122021Z-033091ce7a55` and `20261028T123430Z-177d3624d447` under the
Architecture-declared dated history root. No raw excerpt is copied into these documents.

## Post-Commit Handoff

The static audit of commit `90e9a52` reports **42/100**, with seven judgment checks still
unanswered. Its receipt is `20261028T140136Z-843d16d40baf`, and the raw report is local
under `reports/self-audit/post-commit-90e9a52/`.

Compared with the preceding 55-point observation, the engine/catalog are compatible but
the assessed component coverage changed: the previously untracked Node package is now
included. Six formerly repo-wide not-applicable findings become app-scoped findings.
Node test presence and runner configuration pass; Node CI recognition and lint checks
are newly evaluated. ORI-03 and ORI-10 improve. No existing mechanical check changes
from pass to fail, so the 13-point score decrease is not a demonstrated runtime regression.

Remaining work is explicit, not marked complete by this docs pass:

- Node lint/format configuration and enforcement are not yet present.
- The static CI/docs recognizers do not follow the existing indirect `task check` chain.
- The orientation recognizer does not discover the versioned Architecture path.
- Python type checking, coverage and optional hook/ADR/update-bot gaps remain separate
  follow-ups; no hooks or client configuration are installed automatically.
- Remote CI results, live client loading and the seven judgment answers remain unverified.

The [documentation index](../README.md) is the entry point; earlier numbered folders are
preserved. Generated simulator HTML, raw reports and receipts remain outside the commit.