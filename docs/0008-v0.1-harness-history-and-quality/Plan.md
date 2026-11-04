---
type: 'Plan'
id: '0008'
version: 'v0.1'
title: 'Harness History and Quality Plan'
description: 'Observable criteria for retrospective documentation, city browser automation and comparable self-audit history.'
status: 'active'
doc_scope: 'history'
created: '2026-10-28'
updated: '2026-10-28'
generated: 'agent'
verified: 'unverified'
owner: 'Andreas Elser'
sources: ['Map.md', 'Ideation-Book.md', 'Taskfile.yml', 'skills/harness-audit/SKILL.md']
stale_after: '2026-11-11'
tags:
  - 'documentation'
---

# Harness History and Quality Plan

## Acceptance Criteria

| ID | Given / When / Then |
| --- | --- |
| AC-1 | Given local history, when the retrospective is read, then commit-backed changes and current uncommitted changes are distinguishable; no interview or historical test pass is invented. |
| AC-2 | Given the existing docs, when the basic bundle is created, then it has Ideation, Plan, Architecture and Implementation artifacts in one versioned directory, with an automatic discovery map and links; existing numbered folders remain intact. |
| AC-3 | Given installed development prerequisites, when `task app:test` runs, then real Chromium tests cover desktop and mobile layouts without an interactive browser tool. |
| AC-4 | Given synthetic city data, when browser tests run, then city selection, low-level station/transit rules, all airport controls and independent support facilities are exercised. |
| AC-5 | Given current camera/layer state, when PNG export is tested, then an actual nonblank PNG downloads with description text, the live camera is unchanged, and the offline build works with network requests blocked. |
| AC-6 | Given repeated airport rebuilds, when regression tests run, then material state and GPU allocation stabilize and page/console errors fail the test. |
| AC-7 | Given CI, when the normal check workflow runs, then it installs locked browser dependencies and runs the same browser entry point; no implicit skip converts missing browsers into a pass. |
| AC-8 | Given a static audit, when a history record is written, then it includes repository identity, commit/dirty state, report digest, engine/catalog fingerprints, score, check states and limitations without copying excerpts or secrets. |
| AC-9 | Given two history records, when compared, then compatible records report added/removed/changed check states and score/level deltas; different repositories or engine/catalog fingerprints are rejected as incomparable. |
| AC-10 | Given a shallow clone or incomplete judgment pass, when history is used, then limitations remain explicit; static history never becomes runtime-test or historical-CI evidence. |
| AC-11 | Given a Python test containing quoted placeholder fixture data, when the audit runs, then genuine test presence is not downgraded; actual placeholder comments, docstrings and explicit unimplemented stubs remain blocked. |
| AC-12 | Given ignored audit/browser output, when documentation validation runs, then generated Markdown does not break source-doc checks; tracked private/generated output still fails publication checks. |
| AC-13 | Given the audit skill, when an owner requests automated repository tests or history, then guidance separates static audit from explicitly authorized runtime execution and names the comparison/freshness limits. |
| AC-14 | Given new local utility commands, when they succeed or fail, then they emit bounded structured results or explicit errors and meaningful exit codes; no credentials or repository excerpts are logged by history tooling. |

## Problem and Inputs

The [Ideation Book](Ideation-Book.md) and [automatic map](Map.md) describe the historical
context. Current anchors are the repository Taskfile, CI workflow, city regression module
and audit skill. The raw first audit was 33/100 due to a demonstrated placeholder false
positive; the corrected-engine baseline is 55/100. Those are different measurement
conditions and must not be presented as a quality improvement.

## Scope

In scope: the four basic retrospective documents, automatic discovery/provenance,
headless browser regression, local audit-history receipts/comparison, the reproduced
detector and ignored-output defects, and focused contributor/skill guidance.

Out of scope: relocating imported docs, replaying historical removals, new audit weights,
invented judgment answers, live client setup, automatic hooks, deployments, remote CI
claims, installing dependencies into audited repositories or executing their code.

## Assumptions

Added by a retrospective deepening pass on 2026-11-04. Each assumption cites the file that
shows it at commit `90e9a52` (2026-10-28 14:09:55 +0100, read with `git show 90e9a52:<path>`).
`git diff --quiet 90e9a52 HEAD` over `Taskfile.yml`, `.github/workflows/check.yml`,
`apps/harness-city/playwright.config.js`, `apps/harness-city/tests`, `tools/audit_history.py` and
`skills/harness-audit/scripts` reports no difference, so those statements also hold in today's tree.

- A-1: The toolchain is Python 3.14, uv `0.11.23`, Task `3.51.1` and Node 24 in CI
  (`.github/workflows/check.yml`); `apps/harness-city/package.json` only requires Node `>=22`.
- A-2: Chromium runs with software rendering (`--use-angle=swiftshader` in `playwright.config.js`);
  the 90-second case limit and 900-second global limit assume that cost.
- A-3: Browser setup is a separate step (`task app:setup`; CI runs `playwright install --with-deps
  chromium`), so a missing browser fails instead of skipping.
- A-4: Test data is synthetic. `tools/check.py` function `demo` requires the dataset's
  `meta.source` to say synthetic, four cities whose ids end in `-demo`, and levels L0 to L3.
- A-5: `.data/`, `reports/`, `dist/`, `playwright-report/` and `test-results/` are ignored
  (`.gitignore` at `90e9a52`), and `record` in `tools/audit_history.py` refuses to write unless
  `.data/` is ignored.
- A-6: Receipts are comparable only for the same repository, report schema, tool version,
  engine and catalog fingerprints and clone mode (`compare` in `tools/audit_history.py`).
- A-7: Recorded test counts (251 skill tests plus 3 subtests, 13 tooling tests, 18 browser cases)
  are statements in the commit message of `90e9a52` and in [Implementation](Implementation.md);
  this pass did not re-run them.

## Workstreams

| Slice | Criteria | Deliverable |
| --- | --- | --- |
| M1 | AC-1, AC-2 | Basic retrospective and provenance checks |
| M2 | AC-11, AC-12 | Detector/validation regressions and minimal repairs |
| M3 | AC-3 through AC-7 | Locked Playwright runner, meaningful tests and CI wiring |
| M4 | AC-8 through AC-10, AC-14 | Local structured history recorder and comparator |
| M5 | AC-13 | Progressive-disclosure testing/history guidance for the skill |
| M6 | All | Fresh verification and an honest completion/handoff record |

## Validation and Definition of Done

The commands below are the ones [Implementation](Implementation.md) already names per milestone;
this pass adds none. A milestone is done when its Stop-when line holds. The plan is done when the
M6 gate passes or an exact unresolved limitation is recorded; tests are never deleted, skipped or
weakened to reach that state.

| Slice | Validate command | Source |
| --- | --- | --- |
| M1 | `python3 tools/check.py` | Implementation M1 |
| M1 | the architecture-model and change-set validators | Implementation M1 names them without a command line; Not recorded: the exact command lines |
| M2 | `task --dir skills/harness-audit test -- tests/test_run_checks.py` | Implementation M2 |
| M2, M4 | `task tools:test` | Implementation M2 and M4 |
| M3 | `task app:test` | Implementation M3 |
| M4 | `python3 tools/audit_history.py --help` | Implementation M4 |
| M5 | `python3 tools/check.py` and the skill's existing checks | Implementation M5; Not recorded: which skill command "existing checks" means |
| M6 | `task check` | Implementation M6 |

Historical results, not re-run in this pass: Implementation records `task check` passing with 251
skill tests plus 3 subtests, 13 tooling tests and 18 browser cases, and the `90e9a52` commit message
states the same counts. Today's tree has the same `Taskfile.yml` check chain. Not recorded: a
result of `task check` against today's tree.

### M1: Retrospective

Objective: reconstruct the basic artifacts without falsifying history.
Read first: Map historical outline and Ideation decisions.
Constraints: preserve old folders and distinguish committed/current evidence.
Validate: `python3 tools/check.py` and the bundle-specific checks described in Implementation.
Stop when: metadata, local links, cited commit objects and requested artifacts validate.
Document: record the reduced-workflow exception and unverified historical claims.

### M2: Reproduced Defects

Objective: repair only the observed self-audit and ignored-output defects.
Read first: Ideation risks and the adjacent detector tests.
Constraints: preserve active-stub and tracked-private-output rejection.
Validate: `task --dir skills/harness-audit test -- tests/test_run_checks.py` and `task tools:test`.
Stop when: must-fail canaries and positive regressions pass without weakening checks.
Document: separate the original 33-point result from the corrected 55-point baseline.

### M3: Browser Gate

Objective: execute synthetic city behavior unattended on desktop/mobile and offline.
Read first: city DESIGN.md, app AGENTS.md and check_city.js.
Constraints: no audited code, private data, external network requirement or reused unknown server.
Validate: `task app:test`.
Stop when: both projects execute every test, actual PNGs decode and error/network gates hold.
Document: prerequisites, artifacts, CI invocation and measured results.

### M4 and M5: History and Guidance

Objective: make repeated static results reproducible and comparison limits explicit.
Read first: skill read-only boundary, report schema and Architecture storage contract.
Constraints: no raw excerpts in history, no overwrite of synthetic city data, no cross-engine score claims.
Validate: `task tools:test` and `python3 tools/audit_history.py --help`.
Stop when: compatible comparisons work and incompatible/malformed inputs fail explicitly.
Document: commands for owners and the distinction between static and runtime evidence.

### M6: Final Gate

Objective: demonstrate the requested changes against fresh evidence.
Read first: all acceptance criteria and Implementation resume state.
Constraints: do not delete, skip, weaken or narrow tests to make checks pass.
Validate: `task check`.
Stop when: all required checks run successfully or a concrete unresolved limitation is disclosed.
Document: actual results, local report locations, working-tree caveats and remaining judgments.

## Risks and Decisions

- Browser installation is a development setup step; a missing browser is not a successful test.
- Screenshot evidence is platform-sensitive. Pixel nonblank/layout checks are portable;
  golden-image replacement is an explicit reviewed action, not an automatic baseline update.
- History records fingerprint the engine/catalog because fixes can change measurements.
- The audit reads tracked files where possible. New untracked files may be omitted until
  committed; this task creates no commits and must disclose that limit.
- Logging uses the existing bounded CLI result/error pattern for local developer utilities;
  no service, log rotation, scheduler or additional logging framework is introduced.

## Open Decisions

No historical grilling is required. Human review of reconstructed intent, future commits,
live client loading and any optional hook installation remains with the owner.

## Open Questions

Added by the 2026-11-04 deepening pass; evidence is read-only Git and retained files.

1. Remote CI. Not recorded: any GitHub Actions run of `.github/workflows/check.yml`. This Plan's
   scope and Implementation both say no remote CI pass is claimed. The job sets
   `timeout-minutes: 20` while Implementation records local browser runs of 607.1 and 652.0
   seconds, so the remote duration margin is unverified.
2. Client loading. Not recorded: any observation that Copilot, Claude Code or Pi loads
   `AGENTS.md`, `CLAUDE.md` or the skill from this repository. Implementation lists it as
   deliberately out of scope.
3. Judgment answers. Both the 55-point and the 42-point observations keep seven judgment checks
   `unknown`; Not recorded: any answered judgment pass.
4. Conflict, Plan Risks versus Git. This Plan says "this task creates no commits", but commit
   `90e9a52` (2026-10-28 14:09:55 +0100, Andreas Elser) exists and contains the work. Implementation
   Final Results explains that the owner subsequently requested it. Both statements are kept; the
   Plan sentence describes the state before that request.
5. Conflict, receipt versus handoff. Implementation Post-Commit Handoff says the static audit of
   commit `90e9a52` reports 42/100. The receipt `20261028T140136Z-843d16d40baf` in today's
   `.data/` has `commit` `90e9a52ee1989028447ac3e69c7315101380fb26` and `dirty: true`. A dirty
   tree at recording means the 42 is not a clean-commit result. Not recorded: which paths were
   dirty, since the receipt stores only a status digest.
6. Resume State wording. Implementation says the "documentation handoff finalized after that
   commit". `git show 90e9a52:docs/0008-v0.1-harness-history-and-quality/Implementation.md` has
   159 lines and no Post-Commit Handoff section; `1b15eeb` (2026-10-28 22:39:47 +0100) has one.
   This agrees with the wording; the Resume State does not name `1b15eeb`.
7. Git configuration of audited repositories. At `90e9a52` `tools/audit_history.py` runs Git with
   `core.fsmonitor=false` and `core.hooksPath=/dev/null`, but `git grep` finds no such setting
   in `skills/harness-audit/scripts`. Not recorded: whether the owner accepts that difference or
   treats it as a defect.
8. Storage policy. Architecture says storage follows "the shared application-storage policy read
   during this run". Not recorded: that policy file or its location.
9. Node versions. `package.json` allows Node `>=22`, CI uses Node 24. Not recorded: a run on
   Node 22.