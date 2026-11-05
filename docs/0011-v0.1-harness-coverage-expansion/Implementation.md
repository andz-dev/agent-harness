---
type: 'Implementation'
id: '0011'
version: 'v0.1'
title: 'Harness Coverage Expansion Implementation Playbook'
description: 'Unstarted five-phase execution contract with red-green gates and fixed Grid/ISO design.'
status: 'draft'
created: '2026-11-05'
updated: '2026-11-05'
generated: 'agent'
verified: 'unverified'
owner: 'Andreas Elser'
doc_scope: 'proposal'
sources: ['Plan.md', 'Architecture.md', 'Test-Plan.md', 'Mocking-Plan.md', 'Golden-Dataset/dataset.json', 'ontology/ontology.json']
---

# Harness Coverage Expansion Implementation Playbook

## Resume State

Current phase: **M1, not started**. Last completed product task: none.
Next action after owner authorization to implement: verify the current checkout,
read M1's bounded inputs, then begin one red-green safety/logging slice.
This specification run does not authorize or claim production implementation.

Open production blockers: known Docker legacy ENV redaction defect must be fixed
before expanded collection; WN-031 full browser suite must pass before viewer
acceptance. Neither blocks writing this specification. No scope or visual-layout
choice remains open. The owner selected the defined Grid and existing ISO city.

Pinned package: [Plan](Plan.md), [Architecture](Architecture.md),
[Test Plan](Test-Plan.md), [Mocking Plan](Mocking-Plan.md),
[golden oracle](Golden-Dataset/dataset.json) and
[ontology JSON](ontology/ontology.json). Read concept IDs, not the human glossary,
for domain vocabulary. Architecture owns boundaries and wire semantics.

## Execution Rules

Every task and exit criterion starts unchecked. A task may be checked only after
its required evidence is recorded. Write one behavioral regression, run it as a
separate step and record expected red, implement the smallest corresponding
change, then rerun green. Never count missing tests, zero collection, skips or
weakened assertions as success. Do not execute audited code or import/install its
packages. Keep all report/example inputs synthetic and outputs ignored.

Commands below run from the repository root using the existing locked project
environment. Missing planned test files are prerequisites to create via TDD,
not tests claimed present now. No runtime upgrades or new infrastructure.
Logging uses `lean-logging` and its `emit` API including opt-in TRACE; scan touched
paths for bypasses after each runnable slice. Preserve existing CLI JSON output.

## Phase M1: Safety And Logging Foundation

**Objective:** establish safe lifecycle emission and close the bounded-read and
Docker ENV redaction prerequisites before broader collectors.

**Read first:** Plan M1 and AC-5/14; Architecture sections 5/6; Test-Plan
INFRA-SAFE, UNIT-REDACT, SMOKE-LOG; existing infra checks/tests; ontology JSON
`concept.safe_read`, `concept.logging`, `concept.implementation_type`.
**Load the `lean-logging` skill before implementing or reviewing logging,
including TRACE.**

**Constraints:** no collector expansion before safety gate; no target execution;
no alternate logging API; no broad refactor or unrelated defect fixes.

validate: `task --dir skills/harness-audit test -- tests/test_logging_contract.py && task --dir skills/harness-audit test -- tests/test_infra_checks.py tests/test_coverage.py -k 'redact or safe_read'`

**Stop when:** shipped logging contract and all targeted redaction/read controls
are green, meaningful tests were collected, and no synthetic sentinel reaches
any captured sink. Safety failure stops M2/M3 collection work.

### M1 Tasks

- [ ] M1.1 First runnable milestone: load lean-logging, introduce its standard-library module and contract test in the established script/test layout, record red then green, and verify default severity, TRACE opt-in, bounds, retention, redaction and idempotent handlers. (AC-14; `concept.logging`, `concept.implementation_type`; SMOKE-LOG)
- [ ] M1.2 Reproduce the legacy `ENV KEY value` leak with a synthetic sentinel; fix legacy, modern and multiline forms without weakening existing checks; assert every sink is clean. (AC-5, AC-14; `concept.safe_read`, `concept.logging`; UNIT-REDACT)
- [ ] M1.3 Add the one bounded tracked regular-file reader in the proposed coverage module; reject parent escapes, symlink components, untracked files, identity swaps and exhausted budgets; use literal paths, not shell interpolation. (AC-5; `concept.safe_read`; INFRA-SAFE)
- [ ] M1.4 Exercise no-execution/import/network tripwires and permission failures; verify the target/worktree is unchanged. (AC-5; `concept.safe_read`; E2E-STATIC)
- [ ] M1 exit: run the exact gate; inspect touched logging paths for `print(`, direct `.debug/.info/.warning/.error` and `console.` bypasses; record red/green commands, result counts and safe evidence here. (AC-5, AC-14; `concept.logging`)

## Phase M2: Versioned Contract And Provenance

**Objective:** add independent states, safe identity, receipt inventory and partial
report behavior while preserving the existing supported core result.

**Read first:** Plan M2, AC-1/2/3/4/6/14; Architecture sections 5/6/7; Test-Plan
UNIT-CORE/STATES/PROVENANCE/RECEIPT and INT-REPORT; ontology JSON
`concept.core_score`, `concept.component`, `concept.applicability`,
`concept.evidence`, `concept.freshness`, `concept.provenance`, `concept.receipt`,
`concept.collection`; load `lean-logging` for changed logging paths.

**Constraints:** M1 green; additive schema compatibility; no execution producer;
no raw content/error payloads in reports or logs; no new score pillar.

validate: `task --dir skills/harness-audit test -- tests/test_coverage.py tests/test_audit.py tests/test_score.py tests/test_logging_contract.py`

**Stop when:** schema and assembler agree, legacy baselines remain exact, changed
identity is excluded from current roll-ups, local receipts remain unverified,
and infra-only/unsupported cases have truthful availability and null score.

### M2 Tasks

- [ ] M2.1 Pin independent baseline core values from existing synthetic fixtures; add current/legacy report compatibility assertions before the additive envelope change. (AC-1; `concept.core_score`; UNIT-CORE, INT-REPORT)
- [ ] M2.2 Implement schema/component/applicability/evidence/collection fields exactly as Architecture section 7; keep unsupported languages explicit and no-applicable-core score null. (AC-2, AC-3; `concept.component`, `concept.applicability`, `concept.collection`; UNIT-COMP, UNIT-STATES)
- [ ] M2.3 Bind observations to safe revision/source digests/locators/method/UTC time; retain stale history while excluding it from current summaries. (AC-4; `concept.provenance`, `concept.freshness`; UNIT-PROVENANCE)
- [ ] M2.4 Inventory the six receipt outcomes; reject self-claimed execution; do not resolve credentials, connect issuers or execute receipt commands. (AC-6; `concept.receipt`, `concept.evidence`; UNIT-RECEIPT)
- [ ] M2.5 Wire bounded lifecycle events through `emit`, safe reason codes/counts/durations and content-free TRACE; retain JSON stdout. (AC-14; `concept.logging`; SMOKE-LOG)
- [ ] M2 exit: run the gate, record counts, compare every unchanged core field and scan all sinks/logging paths for leaks or bypasses. (AC-1, AC-2, AC-3, AC-4, AC-6, AC-14; `concept.core_score`, `concept.logging`)

## Phase M3: Catalog And Static Collection

**Objective:** implement Python/Node component-local topic coverage and bounded
configured runner reachability using deterministic fixtures.

**Read first:** Plan M3, AC-2/5/7/8/12; Architecture sections 2/5/7;
Mocking-Plan controls; Golden Dataset guide and selected case IDs; Test-Plan
UNIT-COMP/RUNNER/CATALOG and E2E-STATIC/PARTIAL; ontology JSON
`concept.component`, `concept.topic`, `concept.runner_edge`, `concept.fixture`;
load `lean-logging` before modifying collector events.

**Constraints:** M1/M2 green; Python and Node only; existing check-ID references;
no target commands/imports/install/connections; budgets bound all traversal.

validate: `task --dir skills/harness-audit test -- tests/test_coverage.py tests/test_detect_stack.py tests/test_run_checks.py`

**Stop when:** seven-topic/state fixture coverage, two samples per adapter,
mixed/infra-only/unsupported cases and runner failure controls pass without
changing the core or leaking any sentinel.

### M3 Tasks

- [ ] M3.1 Materialize PY-01/PY-02/NODE-01/NODE-02 and mixed/infra-only/Rust recipes in the established fixture layout; keep inputs deterministic and synthetic. (AC-2, AC-12; `concept.component`, `concept.fixture`; UNIT-COMP)
- [ ] M3.2 Create the unscored seven-topic catalog, resolve references to existing check IDs, and collect safe static observations without duplicating core checks. (AC-8; `concept.topic`; UNIT-CATALOG)
- [ ] M3.3 Add Python/Node component-local applicability; enumerate other detected languages as unsupported; generate every topic/applicability/evidence-state combination with must-reject execution claims. (AC-2, AC-3, AC-8, AC-12; `concept.component`, `concept.applicability`, `concept.evidence`, `concept.fixture`)
- [ ] M3.4 Traverse allowlisted static CI/task/hook references with cycles, missing/dynamic/conditional targets and depth exhaustion; preserve unresolved reasons and never execute. (AC-7; `concept.runner_edge`; UNIT-RUNNER, E2E-STATIC)
- [ ] M3.5 Run every must-fail oracle, including secret/path controls and unsupported scoring; record actual fixture counts and explained calibration limits rather than claim universal coverage. (AC-5, AC-12; `concept.safe_read`, `concept.fixture`; SMOKE-DATA, E2E-PARTIAL)
- [ ] M3 exit: run the gate with meaningful case counts; check lifecycle logging bypasses and current core equality. (AC-2, AC-7, AC-8, AC-12; `concept.logging`, `concept.core_score`)

## Phase M4: Existing Grid And ISO City Projection

**Objective:** preserve report state through conversion and display it in the
owner-selected existing Grid/ISO city, not a standalone alternative layout.

**Read first:** Plan M4, AC-9/10/11/13; Architecture sections 5/7/8;
Prototype-Decision; app AGENTS, README and DESIGN Grid/Camera; Test-Plan
INT-CONVERT/CITY and E2E-CITY/EXPORT; ontology JSON `concept.projection`,
`concept.city_object`, `concept.synthetic_origin`, `concept.release_gate`.
Load `lean-logging` before changing converter diagnostics.

**Constraints:** M3 green; keep seven scored districts, Grid coordinates,
orthographic ISO camera, assets and selection pattern; editor remains parked;
no real reports in tracked assets; reviewed manifest update, never bypass.

validate: `task tools:test && task app:check && task app:test`

**Stop when:** legacy/current/unsupported version behavior, every topic/state,
all four rotations, keyboard/pointer selection, exports and actual mobile/desktop
rendering pass the full suite. WN-031 is a prerequisite, not a waiver.

### M4 Tasks

- [ ] M4.1 Update app DESIGN first for exact evidence indicators/inventory/selection/export semantics while preserving its existing Grid and Camera; add required registry/explanation/ladder entries for actual new objects. (AC-10, AC-13; `concept.city_object`; E2E-CITY)
- [ ] M4.2 Extend the actual converter and existing root tests with accepted legacy/current/future-coverage/rejected-envelope cases; preserve all independent states and safe provenance. (AC-9; `concept.projection`; INT-CONVERT)
- [ ] M4.3 Connect airport/factory/highway topics to the existing ISO city; implement any approved missing models only within current Grid reservations; keep evidence independent of geometry/maturity and expose unsupported/inapplicable topics in accessible inventory. (AC-10; `concept.city_object`, `concept.applicability`; INT-CITY, E2E-CITY)
- [ ] M4.4 Preserve synthetic/simulation origin, stale labels and limitations through display and JSON/HTML/PNG export as applicable; do not mislabel airport presets. (AC-11; `concept.synthetic_origin`, `concept.freshness`; E2E-EXPORT)
- [ ] M4.5 Resolve overview label crowding through focus/zoom/decluttering in the existing design; verify real pointer/raycast and keyboard selection, screenshots, canvas pixels, all rotations and actual desktop/mobile viewport size. (AC-13; `concept.city_object`; E2E-CITY)
- [ ] M4.6 Complete owner-reviewed runtime manifest baseline update for intentional index changes, retaining frozen regression checks; record full browser-suite results and WN-031 disposition. (AC-13; `concept.release_gate`; INFRA-INTEGRITY)
- [ ] M4 exit: run the whole gate; no skipped/timed-out browser acceptance cases; inspect synthetic outputs and safe diagnostics. (AC-9, AC-10, AC-11, AC-13; `concept.projection`, `concept.release_gate`)

## Phase M5: Release Evidence And Maintenance

**Objective:** establish complete, reproducible acceptance evidence without
claiming static observations certify execution or security.

**Read first:** Plan M5 and all ACs; Architecture section 9; Test-Plan gates;
ontology JSON `concept.release_gate`, `concept.fixture`, `concept.logging`;
[storage policy reference](Plan.md#storage-policy-reference).

**Constraints:** M1..M4 exits evidenced; no private report publication, no scope
expansion, no checkbox completion from historical or prototype checks.

validate: `task check && task integrity`

**Stop when:** all required gates pass on the final revision, all AC/scenario/
fixture/task joins are complete, owner review is recorded and limitations remain
visible. A failed gate leaves its task unchecked.

### M5 Tasks

- [ ] M5.1 Run the complete test/lint/build/conversion/documentation/integrity gates on the final revision, with collected counts and safe command evidence. (AC-1, AC-2, AC-3, AC-4, AC-5, AC-6, AC-7, AC-8, AC-9, AC-10, AC-11, AC-12, AC-13, AC-14; `concept.release_gate`)
- [ ] M5.2 Review catalog/adapters, fixture coverage, output privacy and logging bypass scan; record budget/sample calibration limitations and known unsupported areas. (AC-5, AC-8, AC-12, AC-14; `concept.fixture`, `concept.logging`)
- [ ] M5.3 Update owner-facing README and this Resume State with actual outcomes, red-green evidence, final hashes, approved limitations and next unfinished task; obtain owner review without self-assigning human-reviewed metadata. (AC-12, AC-13; `concept.release_gate`)
- [ ] M5 exit: every phase gate evidenced and every acceptance criterion met, or explicitly remain blocked rather than declare release done. (AC-1, AC-2, AC-3, AC-4, AC-5, AC-6, AC-7, AC-8, AC-9, AC-10, AC-11, AC-12, AC-13, AC-14; `concept.release_gate`)

## Rollout And Rollback

Legacy core remains independently usable. Additive coverage is accepted only
after schema/converter validation; unknown coverage is visibly unsupported,
never silently trusted. Roll back the intentional product slice with owner
approval and restore its reviewed manifest baseline together; do not rewrite
report history, erase limitations or disable integrity checks. No database or
destructive migration is required. No runtime feature flag is assumed to exist.

## Decision Log

| Date | Decision | Source / effect |
|---|---|---|
| 2026-11-05 | Existing Grid and ISO city, not standalone alternatives | Owner correction; Plan section 5 and Prototype-Decision |
| 2026-11-05 | Logging foundation is first in M1; detailed events remain M2 | Architecture section 6; supports Plan AC-14; no disposition override |
| 2026-11-05 | Receipt claims stay unverified; no execution producer | Closed ticket 08 and Architecture section 7 |
| 2026-11-05 | No Architecture enum gap or logging-type override carried forward | ontology JSON validation; future gaps require explicit back-edge |

## Definition Of Done

- [ ] All product phase tasks and exit criteria have actual evidence; docs QA alone does not count.
- [ ] Every AC has passing scenarios and deterministic independent fixture expectations.
- [ ] Docker ENV safety, read boundary, unverified receipts and state preservation are enforced by tests.
- [ ] Existing Grid/ISO city, full WN-031 browser suite and reviewed runtime integrity baseline pass.
- [ ] Privacy, limitations, safe lifecycle logging and owner review are recorded.

## Execution Evidence

No product red/green run yet. Add one bounded entry per implemented boundary:
date/revision, task ID, red command and expected failure, green command and
collected counts, safe artifact location, and remaining blocker. Keep raw target
output and private paths out of this tracked record.
