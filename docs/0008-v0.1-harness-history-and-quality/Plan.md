---
type: 'Plan'
id: '0008'
version: 'v0.1'
title: 'Harness History and Quality Plan'
description: 'Observable criteria for retrospective documentation, city browser automation and comparable self-audit history.'
status: 'active'
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