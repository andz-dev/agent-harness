---
type: 'Test Plan'
id: '0011'
version: 'v0.1'
title: 'Harness Coverage Expansion Test Plan'
description: 'Scenario oracles and future execution gates for all fourteen coverage acceptance criteria.'
status: 'draft'
created: '2026-11-05'
updated: '2026-11-05'
generated: 'agent'
verified: 'unverified'
owner: 'Andreas Elser'
doc_scope: 'proposal'
sources: ['Plan.md', 'Architecture.md', 'Prototype-Decision.md']
---

# Harness Coverage Expansion Test Plan

## Context

Inputs: [Plan](Plan.md) AC-1..14 and [Architecture](Architecture.md) D1..D6,
sections 3/5/6/7. This file specifies future tests; no production test is claimed
written or passing. The prototype's limited checks are recorded separately.

## Acceptance Criteria Mapping

| AC | Scenarios | Types | Independent oracle |
|---|---|---|---|
| AC-1 | UNIT-CORE, INT-REPORT | unit, integration | Existing golden score/levels/weights/caps/entropy with coverage absent/present |
| AC-2 | UNIT-COMP, E2E-PARTIAL | unit, end-to-end | Two distinct samples per adapter; mixed, infra-only and unsupported null-score cases |
| AC-3 | UNIT-STATES, INT-CITY | unit, integration | Exact separate enums; unknown never verified |
| AC-4 | UNIT-PROVENANCE, INT-CITY | unit, integration | Changed digest/revision excluded from current summary; historical label retained |
| AC-5 | INFRA-SAFE, UNIT-REDACT, E2E-STATIC | infrastructure, unit, end-to-end | Reject escape/symlink/untracked/oversize; sentinel absent in every output |
| AC-6 | UNIT-RECEIPT, INT-REPORT | unit, integration | All six receipt outcomes; no execution_observed promotion |
| AC-7 | UNIT-RUNNER, E2E-STATIC | unit, end-to-end | Resolved/cycle/unresolved/budget edges; no process invocation |
| AC-8 | UNIT-CATALOG | unit | Seven topics, existing check-ID references, stable deterministic output |
| AC-9 | INT-CONVERT | integration | Legacy/current/future-coverage/rejected-envelope behavior |
| AC-10 | E2E-CITY | end-to-end | Topic inventory and real selection keep orthogonal states |
| AC-11 | E2E-EXPORT, INT-CITY | end-to-end, integration | Synthetic/simulation origin and limitations survive display/export |
| AC-12 | SMOKE-DATA, UNIT-COMP | smoke, unit | Stable fixture IDs and complete AC/scenario joins |
| AC-13 | E2E-CITY, E2E-EXPORT, INFRA-INTEGRITY | end-to-end, infrastructure | Desktop/mobile, four orientations, full browser suite, reviewed manifest |
| AC-14 | SMOKE-LOG, UNIT-REDACT | smoke, unit | Shipped logging contract and sentinel scan of all sinks |

## Scenario Matrix

| ID | Boundary and stimulus | Expected result |
|---|---|---|
| SMOKE-DATA | Load golden JSON twice and validate IDs/enums/joins | Byte-stable source; every topic/AC/scenario represented |
| SMOKE-LOG | Run shipped Python logging contract via task runner | Severity/TRACE/redaction/bounds/retention/idempotence pass; JSON stdout intact |
| INFRA-SAFE | Temporary Git worktree with tracked regular files and hostile paths | No untracked read, parent escape, directory-symlink traversal, file swap leak or shell interpretation |
| INFRA-INTEGRITY | Intended viewer change plus reviewed manifest update | Full integrity gate passes; no checksum bypass or private report output |
| UNIT-CORE | Same supported baseline before/after coverage | Exact core equality; additive fields only |
| UNIT-COMP | Python script/package; Node JS/TS package; mixed; infra-only; Rust | Component-local applicability; unsupported explicit; unavailable score null |
| UNIT-STATES | All applicability/evidence values including forbidden execution input | Contract permits vocabulary, producer rejects unauthenticated execution claims |
| UNIT-PROVENANCE | Same source, changed digest, changed revision, missing identity | Current/stale/unknown as defined; no stale item in current roll-up |
| UNIT-REDACT | Docker ENV modern/legacy/multiline and URL/token-like synthetic sentinels | No sentinel in report, projection, log, error or generated HTML |
| UNIT-RECEIPT | Absent/present/invalid/stale/partial/failed local receipts | Safe outcome retained; present remains unverified; no runtime claim |
| UNIT-RUNNER | CI to task to hook; cycle; dynamic/missing/conditional target; depth limit | Only static configured reachability; safe unresolved reason; no execution |
| UNIT-CATALOG | Catalog and report topic/check references | Unique stable IDs; seven topics; references resolve; deterministic ordering |
| INT-REPORT | Real collector and report assembler with real core scorer | Versioned additive contract; partial and failure semantics preserved |
| INT-CONVERT | Real converter reads legacy/current/future versions | Legacy core unchanged; current states exact; unsupported coverage visible; invalid envelope rejected |
| INT-CITY | Report to city projection and safe selection data | No state loss, duplication of score, raw evidence text or fabricated maturity |
| E2E-STATIC | Audit synthetic target with execution/import/network tripwires | Bounded reads only; tripwires never invoked; safe report emitted |
| E2E-PARTIAL | Audit infra-only and unsupported-language sample | Honest limitations, partial/unavailable score; no invented zero or extra adapter |
| E2E-CITY | Load synthetic projection in existing Grid/ISO viewer | Airport/factory/highway discoverable by keyboard inventory and pointer selection; details show state/provenance/limits |
| E2E-EXPORT | View and export synthetic/stale/simulated projection | Artifact keeps origin and limitations; no simulated-to-observed promotion |

## Execution Design

### Smoke

`SMOKE-LOG` is mandatory because Architecture section 6 derives full logging for
runnable scripts. Load `lean-logging`, copy its contract test with the module,
then run `task --dir skills/harness-audit test -- tests/test_logging_contract.py`.
`SMOKE-DATA` validates the golden oracle before fixture materialization.

### Infrastructure

Use temporary repositories, explicit subprocess `cwd`, and no shared-terminal
directory changes. Model tracked-path changes/races at the read boundary; use
real filesystem and Git metadata, not fake containment checks. Inject process,
import and socket tripwires at external capabilities. Restore nothing in the
owner worktree. Platform-incompatible symlink/no-follow cases must report a
missing prerequisite, never silently count as full safety acceptance.

### End-To-End

`E2E-STATIC` goes from explicit synthetic target root to actual report.
`E2E-CITY` goes from actual converter output to the actual existing city, not a
replacement mock scene or the temporary host prototype. Cover airport, factory
and highway; all four 90-degree orientations; pointer/raycast and keyboard
inventory; focus/zoom; desktop 1440 x 1000 and mobile 390 x 844, plus the existing
suite's configured viewports. Assert actual inner size before pointer coordinates.
Check canvas pixels and screenshots, label decluttering, no overlapping controls
or clipped text, state details, and topic inventory for unsupported/inapplicable.
Images are diagnostic outputs in ignored directories, not golden private reports.

WN-031 requires the **entire** browser suite green. A narrowed prototype check,
software-renderer timeout, skipped case or screenshot alone cannot close it.

### Integration

Exercise real report schema validation, scorer, converter and viewer data path.
Compare untouched legacy core fields structurally to independent existing
fixtures. Add future-version cases without changing accepted legacy fixtures.
Use [storage policy](Plan.md#storage-policy-reference) for output/config tests;
no database/service mocks are required.

### Unit

Test public collection/projection behavior, not private helper call order.
Expected states come from the golden oracle and closed tickets, not from
recomputing implementation algorithms. Distinct test IDs expose regressions.

## Failure Controls

Must fail if unknown becomes verified; unsupported becomes a numeric score;
any synthetic sentinel reaches any sink; a path escapes; a declaration/local
receipt becomes execution_observed; stale/simulation origin is erased in city
projection; unsupported version is silently interpreted; or coverage affects core.
Treat zero collected tests as failure. Never weaken or skip frozen tests.

## Test Ownership And Commands

| Slice | Existing ownership / planned addition | Future gate |
|---|---|---|
| M1 | Audit infra tests; new coverage and shipped logging contract tests | `task --dir skills/harness-audit test -- tests/test_logging_contract.py tests/test_infra_checks.py tests/test_coverage.py -k 'logging or redact or safe_read'` |
| M2 | Audit coverage/audit/score tests | `task --dir skills/harness-audit test -- tests/test_coverage.py tests/test_audit.py tests/test_score.py tests/test_logging_contract.py` |
| M3 | Audit coverage/detection/check tests | `task --dir skills/harness-audit test -- tests/test_coverage.py tests/test_detect_stack.py tests/test_run_checks.py` |
| M4 | Root repo-quality tests and existing city browser suite; add coverage cases | `task tools:test && task app:check && task app:test` |
| M5 | Required complete gates | `task check && task integrity` |

These commands are future implementation gates. Some named files do not exist
yet; a missing file is a failed prerequisite, not a current regression or pass.

## Scaffold And TDD Handoff

Five text category placeholders exist under this bundle's `tests/`: smoke,
infrastructure, e2e, integration and unit. They are documentation scaffolds,
not runnable tests, not skipped tests, and not a second production suite.
Materialize each case in the ownership locations above during implementation.

For each behavioral boundary: write one regression test, run it in a separate
step and record its expected red failure, implement the smallest change, rerun
to green, then move to the next boundary. No horizontal batch of speculative
tests. Product acceptance remains untested until those gates actually run.

## Handoff

All fourteen criteria map to scenarios. Mocking owns external-capability controls;
Golden Dataset owns deterministic case values; Implementation owns execution
order. Dataset validation is specification QA, not product acceptance.
