---
type: 'Implementation'
id: '0011'
version: 'v0.1'
title: 'Harness Coverage Expansion Implementation Playbook'
description: 'Five-phase execution contract with red-green gates and fixed Grid/ISO design; closed 2026-11-06 with the full browser gate moved to WN-031.'
status: 'done'
created: '2026-11-05'
updated: '2026-11-06'
generated: 'agent'
verified: 'unverified'
owner: 'Andreas Elser'
doc_scope: 'proposal'
sources: ['Plan.md', 'Architecture.md', 'Test-Plan.md', 'Mocking-Plan.md', 'Golden-Dataset/dataset.json', 'ontology/ontology.json']
---

# Harness Coverage Expansion Implementation Playbook

## Resume State

Follow-on requested by the owner on 2026-11-06: the visible physical city buildout
is tracked in [0012 Plan](../0012-v0.1-city-landmark-buildout/Plan.md) and
[0012 Implementation](../0012-v0.1-city-landmark-buildout/Implementation.md).
Airport, Factory, Mall, Bank, Archive, Highway, mountains/tunnel and bridge are
default scenery, separate from M4.3's conditional coverage markers. This is an
explicit scope addition, not a retrospective claim that M4.3 built those models.
M4.4's origin contract and the M4.5/M4.6 acceptance gates below remain unchanged.

Status: **closed 2026-11-06** by owner decision (light finish). All M1..M5 tasks are
checked against the fast gates below. The complete 42-test browser suite is not part
of 0011 any more; it is tracked as [WN-031](../Whats-Next.md) for CI or a GPU machine.
Next unfinished work: WN-031, then 0012 B4/B5 and the planned map areas after owner
approval. Final gates on the closing revision: `task tools:test` 19 passed;
`task --dir skills/harness-audit check` 297 passed, 169 subtests; `task app:check`
PASS; `python3 tools/check.py --integrity-only` PASS; `tools/city_grid.py --check` PASS;
`task --dir skills/harness-audit audit -- ../.. --out /tmp/...` exit 0, score 45.

History before closure. Last completed product task: M4.5. `task app:test -- city.spec.js`: 18 passed
across desktop and mobile Chromium. The new overview regression verifies no label
collisions over all four rotations at 1440 x 1000 and 390 x 844, nonblank canvas
pixels, screenshots, and keyboard focus/zoom. Existing real pointer/raycast and
inventory-selection cases also passed. M4.4 accepts optional `report.meta.synthetic`,
projects it as `city.synthetic`, preserves explicit true/false, and displays missing
legacy origin as unknown; `task tools:test` passed 19 tests and `task app:check`
passed deterministic synthetic generation plus online/offline standalone builds.

M4.3 connected the owner-confirmed airport=`security` mapping, factory topics,
and CI/build plus runner edges on the highway; added accessible topic inventory,
independent state/provenance details and selectable non-model markers; corrected
C10-C12 layout conflicts; and kept topic markers conditional on projected
references. M4.5 is complete. WN-031 full browser suite remains a production
prerequisite for M4.6; the owner-selected Grid and existing ISO city remain the
only layout.

M4.6 updated the four intentional adapted-runtime hashes; `python3 tools/check.py
--integrity-only` passes. WN-031 remains blocked: `CITY_TEST_PORT=18765 task
app:test` timed out at 900 seconds with 21 passed and 21 not run; retrying the
same 42-test suite with `--global-timeout=2400000` was interrupted after 4.4
minutes with 4 passed, 1 interrupted and 37 not run. A separate mobile run finished:
16 passed, 5 skipped (the editor is explicitly desktop-only); the next desktop-only run
was interrupted by the owner. No skipped or timed-out acceptance cases can close this
gate. Do not rerun the full suite in an agent session: the owner runs it on a GPU
machine or in CI (WN-031).

Stop 2026-11-06, awaiting owner review: the audit is usable now. `task --dir
skills/harness-audit audit -- ../.. --out /tmp/x` exits 0 and writes report.json/.md,
triage.json/.md and llm_tasks.json; `report_to_city.py` converts it; `task --dir
skills/harness-audit check` passed 297 tests. `tools/city_grid.py --check` passes, and
the landmark positions match the DESIGN grid. Further map work waits for owner approval.

Resume timestamp: 2026-11-06.

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

- [x] M1.1 First runnable milestone: load lean-logging, introduce its standard-library module and contract test in the established script/test layout, record red then green, and verify default severity, TRACE opt-in, bounds, retention, redaction and idempotent handlers. (AC-14; `concept.logging`, `concept.implementation_type`; SMOKE-LOG)
- [x] M1.2 Reproduce the legacy `ENV KEY value` leak with a synthetic sentinel; fix legacy, modern and multiline forms without weakening existing checks; assert every sink is clean. (AC-5, AC-14; `concept.safe_read`, `concept.logging`; UNIT-REDACT)
- [x] M1.3 Add the one bounded tracked regular-file reader in the proposed coverage module; reject parent escapes, symlink components, untracked files, identity swaps and exhausted budgets; use literal paths, not shell interpolation. (AC-5; `concept.safe_read`; INFRA-SAFE)
- [x] M1.4 Exercise no-execution/import/network tripwires and permission failures; verify the target/worktree is unchanged. (AC-5; `concept.safe_read`; E2E-STATIC)
- [x] M1 exit: run the exact gate; inspect touched logging paths for `print(`, direct `.debug/.info/.warning/.error` and `console.` bypasses; record red/green commands, result counts and safe evidence here. (AC-5, AC-14; `concept.logging`)

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

- [x] M2.1 Pin independent baseline core values from existing synthetic fixtures; add current/legacy report compatibility assertions before the additive envelope change. (AC-1; `concept.core_score`; UNIT-CORE, INT-REPORT)
- [x] M2.2 Implement schema/component/applicability/evidence/collection fields exactly as Architecture section 7; keep unsupported languages explicit and no-applicable-core score null. (AC-2, AC-3; `concept.component`, `concept.applicability`, `concept.collection`; UNIT-COMP, UNIT-STATES)
- [x] M2.3 Bind observations to safe revision/source digests/locators/method/UTC time; retain stale history while excluding it from current summaries. (AC-4; `concept.provenance`, `concept.freshness`; UNIT-PROVENANCE)
- [x] M2.4 Inventory the six receipt outcomes; reject self-claimed execution; do not resolve credentials, connect issuers or execute receipt commands. (AC-6; `concept.receipt`, `concept.evidence`; UNIT-RECEIPT)
- [x] M2.5 Wire bounded lifecycle events through `emit`, safe reason codes/counts/durations and content-free TRACE; retain JSON stdout. (AC-14; `concept.logging`; SMOKE-LOG)
- [x] M2 exit: run the gate, record counts, compare every unchanged core field and scan all sinks/logging paths for leaks or bypasses. (AC-1, AC-2, AC-3, AC-4, AC-6, AC-14; `concept.core_score`, `concept.logging`)

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

- [x] M3.1 Materialize PY-01/PY-02/NODE-01/NODE-02 and mixed/infra-only/Rust recipes in the established fixture layout; keep inputs deterministic and synthetic. (AC-2, AC-12; `concept.component`, `concept.fixture`; UNIT-COMP)
- [x] M3.2 Create the unscored seven-topic catalog, resolve references to existing check IDs, and collect safe static observations without duplicating core checks. (AC-8; `concept.topic`; UNIT-CATALOG)
- [x] M3.3 Add Python/Node component-local applicability; enumerate other detected languages as unsupported; generate every topic/applicability/evidence-state combination with must-reject execution claims. (AC-2, AC-3, AC-8, AC-12; `concept.component`, `concept.applicability`, `concept.evidence`, `concept.fixture`)
- [x] M3.4 Traverse allowlisted static CI/task/hook references with cycles, missing/dynamic/conditional targets and depth exhaustion; preserve unresolved reasons and never execute. (AC-7; `concept.runner_edge`; UNIT-RUNNER, E2E-STATIC)
- [x] M3.5 Run every must-fail oracle, including secret/path controls and unsupported scoring; record actual fixture counts and explained calibration limits rather than claim universal coverage. (AC-5, AC-12; `concept.safe_read`, `concept.fixture`; SMOKE-DATA, E2E-PARTIAL)
- [x] M3 exit: run the gate with meaningful case counts; check lifecycle logging bypasses and current core equality. (AC-2, AC-7, AC-8, AC-12; `concept.logging`, `concept.core_score`)

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

- [x] M4.1 Update app DESIGN first for exact evidence indicators/inventory/selection/export semantics while preserving its existing Grid and Camera; add required registry/explanation/ladder entries for actual new objects. (AC-10, AC-13; `concept.city_object`; E2E-CITY)
- [x] M4.2 Extend the actual converter and existing root tests with accepted legacy/current/future-coverage/rejected-envelope cases; preserve all independent states and safe provenance. (AC-9; `concept.projection`; INT-CONVERT)
- [x] M4.3 Connect airport/factory/highway topics to the existing ISO city; implement any approved missing models only within current Grid reservations; keep evidence independent of geometry/maturity and expose unsupported/inapplicable topics in accessible inventory. (AC-10; `concept.city_object`, `concept.applicability`; INT-CITY, E2E-CITY)
- [x] M4.4 Preserve synthetic/simulation origin, stale labels and limitations through display and JSON/HTML/PNG export as applicable; do not mislabel airport presets. (AC-11; `concept.synthetic_origin`, `concept.freshness`; E2E-EXPORT)
- [x] M4.5 Resolve overview label crowding through focus/zoom/decluttering in the existing design; verify real pointer/raycast and keyboard selection, screenshots, canvas pixels, all rotations and actual desktop/mobile viewport size. (AC-13; `concept.city_object`; E2E-CITY)
- [x] M4.6 Complete owner-reviewed runtime manifest baseline update for intentional index changes, retaining frozen regression checks; record full browser-suite results and WN-031 disposition. (AC-13; `concept.release_gate`; INFRA-INTEGRITY)
  Disposition 2026-11-06: manifest integrity passes; browser results recorded below; full-suite gate moved to WN-031 by owner decision.
- [x] M4 exit: run the whole gate; no skipped/timed-out browser acceptance cases; inspect synthetic outputs and safe diagnostics. (AC-9, AC-10, AC-11, AC-13; `concept.projection`, `concept.release_gate`)
  Closed with the per-spec browser runs (city 18/18, export synthetic-origin) and the fast gates; the whole-suite run is WN-031.


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

- [x] M5.1 Run the complete test/lint/build/conversion/documentation/integrity gates on the final revision, with collected counts and safe command evidence. (AC-1, AC-2, AC-3, AC-4, AC-5, AC-6, AC-7, AC-8, AC-9, AC-10, AC-11, AC-12, AC-13, AC-14; `concept.release_gate`)
- [x] M5.2 Review catalog/adapters, fixture coverage, output privacy and logging bypass scan; record budget/sample calibration limitations and known unsupported areas. (AC-5, AC-8, AC-12, AC-14; `concept.fixture`, `concept.logging`)
- [x] M5.3 Update owner-facing README and this Resume State with actual outcomes, red-green evidence, final hashes, approved limitations and next unfinished task; obtain owner review without self-assigning human-reviewed metadata. (AC-12, AC-13; `concept.release_gate`)
- [x] M5 exit: every phase gate evidenced and every acceptance criterion met, or explicitly remain blocked rather than declare release done. (AC-1, AC-2, AC-3, AC-4, AC-5, AC-6, AC-7, AC-8, AC-9, AC-10, AC-11, AC-12, AC-13, AC-14; `concept.release_gate`)

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
| 2026-11-05 | Owner approved raising harness-audit's Python floor to 3.14+; copied the shipped lean-logging module/catalog into the established scripts layout and added the project-owned contract test. | M1.1; `pyproject.toml`, `uv.lock`, `SKILL.md`; Python 3.14.6 contract and skill checks passed. |
| 2026-11-05 | INF-D06 now joins Dockerfile continuation lines for secret assignment detection and emits only the variable name in evidence; existing finding/status behavior remains covered. | M1.2; synthetic modern, legacy and multiline cases in `tests/test_infra_checks.py`. |
| 2026-11-05 | The bounded reader uses directory-relative no-follow opens, named file/total/path budgets and pre/open/post identity comparison; unsupported platforms return unknown. | M1.3; Architecture section 5 and `INFRA-SAFE`; 7 real-filesystem tests pass. |
| 2026-11-05 | M1 complete. Files: logger/catalog, logging and infrastructure tests, bounded reader, audit tripwire test, skill README/setup metadata, lock and this playbook. Decisions: Python 3.14+ uses the shipped logger; evidence contains only secret variable names; the reader fails closed on identity/symlink/platform uncertainty. Open question: reader-to-report integration begins in M2/M3; WN-031 remains a later viewer gate. | Exact M1 gate passed 9 tests and 3 subtests; `task --dir skills/harness-audit lint` passed; `task --dir skills/harness-audit test -- tests/test_audit.py tests/test_coverage.py` passed 16 tests. |
| 2026-11-05 | M2.1 froze the legacy synthetic report core before adding coverage: seven pillar values/weights, score 19 from raw 20 minus entropy 1, and the fixed entropy item. The generated legacy report remains schema-valid with coverage absent. | `test_legacy_core_baseline_is_pinned` in `tests/test_audit.py`; 29 audit/score tests passed. |
| 2026-11-05 | Owner selected a top-level `quality` sibling beside `coverage`; available/partial reports keep existing score/pillars and unavailable reports omit fabricated core fields. | Architecture D7 and section 7; AC-1/2. |
| 2026-11-05 | M2.2 adds a version-1 coverage envelope with explicit component applicability, closed state enums, collection budgets/reasons, and a top-level quality sibling. Supported core fields remain unchanged; unsupported-only reports omit them and report null quality score. | `audit.py`, `report.schema.json`, and CLI tests; exact M2 gate passed 48 tests. |
| 2026-11-05 | M2.3 adds safe provenance construction, revision/digest freshness classification, observation binding, and current-only filtering; stale evidence labels remain historical and unchanged. | `coverage.py` and `tests/test_coverage.py`; 13 tests and 3 subtests passed. |
| 2026-11-05 | M2.4 classifies local receipts as absent/present_unverified/invalid/stale/partial/failed, emits no raw receipt fields, and never promotes a claim to execution_observed. | `classify_receipt` in `coverage.py`; 16 tests and 9 subtests passed. |
| 2026-11-05 | M2.5 emits bounded collection/conversion lifecycle events through `emit`; TRACE contains aggregate counts only, and conversion rejection logs a safe reason/count with the actual exit status. | CLI output and rejection canaries; exact M2 gate 59 tests and 9 subtests; Ruff passes. |
| 2026-11-05 | M2 complete. Files: `audit.py`, `coverage.py`, `triage.py`, `report.schema.json`, `test_audit.py`, `test_coverage.py`, and this playbook, plus prior phase files. Decisions: top-level quality sibling, unscored coverage, no fabricated score, local receipts remain unverified, and Python 3.14+ for shipped logging. Open question: observation collection, catalog and runner graph are M3; WN-031 remains M4/M5. | Exact M2 gate passed 59 tests and 9 subtests; `task --dir skills/harness-audit lint` passed; direct-output scan found only established CLI summaries/argument handling, no direct logging calls. |
| 2026-11-05 | M3.1 materialized the seven golden component recipes as deterministic synthetic directories under the skill test fixtures. Two Python and two Node samples classify separately; mixed, infra-only and Rust-only cases match the expected support boundary. | Exact M3 gate passed 85 tests and 19 subtests; Ruff passed. |
| 2026-11-05 | M3.2 added the unscored seven-topic catalog, validated all core/INF references and limits, and wired bounded tracked-source observations into reports without duplicating score checks. Testing locators are specific to test config/files; MCP/skills locators avoid generic instruction-file false positives. | Exact M3 gate passed 89 tests and 26 subtests; Ruff passed, 43 files formatted. |
| 2026-11-05 | M3.3 now emits one observation for every detected component/topic pair, including unsupported language and no-source unknown states; the report validator rejects incomplete/duplicate pairs and `execution_observed`. | `coverage.py`, `audit.py`, `test_coverage.py`, `test_audit.py`; 109 tests and 166 subtests passed; Ruff and `task integrity` passed. Runner traversal remains M3.4. |
| 2026-11-05 | M3.4 adds allowlisted static CI/task/hook traversal with bounded graph depth, cycle detection, and safe reason codes for missing/dynamic/conditional/ambiguous targets; audited commands are never invoked. | `coverage.py`, `audit.py`, runner/report tests, and adapted-runtime hashes; 112 tests and 166 subtests passed; Ruff and `task integrity` passed. M3.5 must-fail oracles remain. |
| 2026-11-05 | M3.5 exercises the full must-fail set and golden joins; unsupported-only topics remain unsupported/unknown, infra-only produces no observations or score, and synthetic secret sentinels are absent from every captured audit output. Calibration is 43 golden cases, seven component recipes (two per supported adapter plus mixed/infra/Rust), and three topic-source fixtures; no universal coverage claim is made. | Expanded M3 safety/report suite: 180 passed, 169 subtests; logging contract: 7 passed; exact M3 gate: 95 passed, 166 subtests; Ruff and `task integrity` passed. |
| 2026-11-05 | M3 complete. Files across the phase: component/topic fixtures, coverage catalog, `coverage.py`, `audit.py`, coverage/report tests, adapted-runtime manifest hashes and this playbook. Decisions: keep coverage unscored; enumerate all component/topic states; reject static execution claims; trace only bounded catalogued static runner declarations. Open limitation: the initial synthetic adapter/runner sample is intentionally small; WN-031 remains a later viewer/release gate. | Exact M3 gate passed 95 tests and 166 subtests; expanded must-fail/report suite passed 180 tests and 169 subtests; logging contract passed 7 tests; Ruff and `task integrity` passed. Next phase: M4 existing Grid/ISO city projection. |
| 2026-11-05 | Updated the extraction manifest's adapted-runtime hashes for intentional 0011 changes; preserved original source hashes and marked `triage.py` adapted. | `task integrity`: PASS. |
| 2026-11-05 | Current root `task check` passed skill lint/tests, repo-quality, demo conversion and city build, but Playwright timed out after 21 passed, 5 skipped and 2 not run; WN-031 remains open. `task precommit` then confirmed only the pre-existing Trail learning frontmatter error remains. | `.trail/learnings/2026-11-04-resolve-backlog-id-collisions-on-merge-andreas.md` is unchanged. |
| 2026-11-05 | M4.1 defines airport/factory/highway as coverage anchors, with factory and highway remaining planned locations rather than approved models. The keyboard inventory and selection panel preserve independent applicability/evidence/freshness, safe provenance, limitations and synthetic origin; none maps to L0-L3 or score. | `apps/harness-city/DESIGN.md`; `task tools:test`: 15 passed, including the repository design check. Only the declared design file changed; next task is M4.2. |
| 2026-11-05 | M4.2 preserves legacy core without adding coverage and carries supported version-1 observations/provenance unchanged; unknown coverage versions retain core but expose only an unsupported marker and fixed limitation; unknown report-envelope majors fail before output with a fixed diagnostic. | `apps/harness-city/tools/report_to_city.py`, `tests/test_repo_quality.py`; schema-valid current report plus legacy/future cases; 10 root tests passed. Next task is M4.3. |
| 2026-11-05 | At the M4.3 resume check, the airport mapping was blocked: Plan section 6 says airport = infrastructure; Architecture section 7 derived airport = `security` from `INF-*` references but awaited owner confirmation. Atlas found the corresponding 0005 rule, although the source is marked `proposed`; no runtime mapping existed. | No product or test changes were made while blocked. Resolved by the following owner decision. |
| 2026-11-05 | Owner confirmed the 0005 rule for 0011: every coverage topic whose `check_ids` reference `INF-*` anchors on Airport; current `security` therefore maps to Airport, while its Plan area remains Infrastructure. | Recorded in Architecture section 7. M4.3 implementation proceeds against this mapping and the existing Grid reservations. |
| 2026-11-05 | The first coverage-inventory test run reached the topic detail but expected the raw enum `static_implementation_found`; the UI correctly renders the design label “static implementation found.” | Update the assertion to the displayed label; no product behavior change is needed. |
| 2026-11-05 | M4.3 connects report coverage to the existing city: all seven topics appear in an accessible inventory; selection shows independent states and safe provenance; the owner-mapped airport and only referenced factory/highway anchors expose their topics; highway shows runner-edge counts without target names or execution claims. Applied DESIGN C10-C12 first, documented ring markers as reservations rather than buildings, and updated the adapted-runtime hash. | Files: `apps/harness-city/DESIGN.md`, `apps/harness-city/index.html`, `apps/harness-city/tests/city.spec.js`, `apps/harness-city/tests/fixtures.js`, `docs/0011-v0.1-harness-coverage-expansion/Architecture.md`, `docs/0011-v0.1-harness-coverage-expansion/Implementation.md`, `extraction-manifest.json`. `task tools:test`: 19 passed; `task app:check`: four schema-valid synthetic profiles converted deterministically and online/offline builds passed; `task app:test -- city.spec.js`: 14 passed across desktop/mobile; `python3 tools/check.py --integrity-only`: PASS. Full `python3 tools/check.py` still reports only the unrelated pre-existing Trail learning frontmatter error. Next: M4.4. |
| 2026-11-06 | M4.4 remains blocked after checking AC-11, Architecture, the report schema, ontology and golden dataset: the outcome is explicit, but the canonical report input field, city projection field and behavior when legacy input omits origin are not. The ontology's `meta.synthetic` dataset trace does not define those wire semantics, and deriving origin from `prototype_simulated` is explicitly prohibited. No product/test files changed; awaiting owner choice before implementation. | M4.4; `Plan.md` AC-11, `Architecture.md` section 7, `skills/harness-audit/schema/report.schema.json`, `ontology/ontology.json`, `Golden-Dataset/dataset.json`. |
| 2026-11-06 | Owner resolved M4.4: accept optional `report.meta.synthetic`, copy it to each projected `city.synthetic`, and map omitted legacy origin to null/visibly unknown. | AC-11; Architecture section 7; INT-CITY and E2E-EXPORT. |
| 2026-11-06 | M4.4 completed. Files: report schema, converter, demo report producer/data, city panel/PNG description, conversion and export tests, Architecture/design/README/ontology/golden/resume records. The root suite passed 19 tests; `task app:check` passed deterministic generation plus online/offline builds; focused desktop E2E-EXPORT passed with synthetic, non-synthetic and unknown panel states and synthetic/unknown PNG descriptions. WN-031 and M4.5/M4.6 remain open. | `task tools:test`; `task app:check`; `CITY_TEST_PORT=18765 task app:test -- export.spec.js --project=desktop-chromium -g "synthetic origin"`. |
| 2026-11-06 | M4.5 completed. DESIGN now requires deterministic stable-order overlap suppression. The city spec passes 18 tests across desktop/mobile, including actual pointer/raycast and keyboard selection, focus/zoom, collision checks at all four rotations and 1440x1000/390x844, screenshots and nonblank canvas pixels. The full viewport screenshots were inspected; no clipping or incoherent overlaps remained. WN-031 full-suite gate and M4.6 manifest review remain. | `CITY_TEST_PORT=18765 task app:test -- city.spec.js`; screenshot artifacts remain ignored under `apps/harness-city/test-results/artifacts/`. |
| 2026-11-06 | M4.6 partially completed: refreshed four already-adapted runtime hashes and `python3 tools/check.py --integrity-only` passes. The full 42-test browser suite timed out after 900 seconds (21 passed, 21 not run); the extended retry was interrupted after 4.4 minutes (4 passed, 1 interrupted, 37 not run). WN-031 is unresolved; M4.6 and M4 exit remain unchecked. | `extraction-manifest.json`; `python3 tools/check.py --integrity-only`; full `task app:test` results. |
| 2026-11-06 | Owner decision: close 0011 with the fast gates and move the complete browser suite (WN-031) to the backlog for CI or a GPU machine. This overrides the Test-Plan rule that only a full unskipped run closes M4.6/M4 exit for this version. Phase summary M4/M5: files touched across M4 are the report schema, converter, demo producer/data, city `index.html`, city tests/fixtures, DESIGN/README, Architecture/ontology/golden dataset and the extraction manifest. Decisions: owner topic-to-anchor mapping, `meta.synthetic` origin with unknown for legacy input, stable-order label decluttering. M5.2 relies on the M3.5 calibration record (43 golden cases, 7 component recipes, 3 topic-source fixtures; Python/Node only, no universal coverage claim) and reports staying under ignored paths. Carried forward: WN-031, 0012 B4/B5, planned map areas (Court, Harbor, power-line extension, traffic). | Final gates: root tests 19 passed; skill check 297 passed, 169 subtests; `task app:check`, integrity and city-grid PASS; real audit run exit 0. |
| 2026-11-05 | M4.3 is blocked: the seven catalog topic IDs and the three city anchor IDs have no defined association in the report schema or architecture. No mapping was inferred and no viewer code changed. | Await owner choice: supply a topic-to-anchor table; keep the anchors as focus locations with a global, unassociated inventory and amend AC-10/M4.3; or add a versioned upstream mapping field to the catalog/report contract. |
| 2026-11-05 | Correction to the previous row: Plan section 6 already mapped airport = infrastructure, factory = build/artifact/dependency supply chain, highway = CI/task/hook reachability. Architecture section 7 now resolves these to catalog topic IDs, links the 0005, 0007 and 0009 designs (with back-references there), and notes that 0009 used the highway for supply-chain delivery. | Owner pointed to the earlier folders; artifact-atlas `ask` located 0009 Design-Proposal and 0007 airport assets. Derived airport row awaits owner confirmation. |
| 2026-11-05 | DESIGN City map redrawn at one character per cell from a single coordinate table, checked for overlapping plots and crossings. Export conflicts C6..C9 recorded with resolutions (C8 changed to one spur at x 44); new conflicts C10..C14 found against the code and the 0009/0011 meanings. `dependencies` moved off the airport. | Source: `research/Repo harness audit and security - Claude.pdf` (east edge cropped at x 50) and `index.html` `AP`, `airSetup`, `buildRail`, tree scatter. |
| 2026-11-05 | M4.4 blocker after M4.3 completion: Architecture section 7 requires synthetic origin at record and projection level; ontology `concept.synthetic_origin` requires a boolean `synthetic`; the closed version-1 coverage schema defines no such field, and the converter passes supported coverage through unchanged. Ticket 04 does not resolve the field location. `prototype_simulated` is an independent evidence state and cannot substitute for origin. | No M4.4 code or tests changed. Await owner decision on the canonical input field and backward-compatible absence semantics (for example, optional `coverage.synthetic` versus a separately defined projection origin). Amend schema/Architecture/ontology first as needed. M4.4 remains unchecked; stop here. |

## Definition Of Done

- [x] All product phase tasks and exit criteria have actual evidence; docs QA alone does not count.
- [x] Every AC has passing scenarios and deterministic independent fixture expectations.
- [x] Docker ENV safety, read boundary, unverified receipts and state preservation are enforced by tests.
- [ ] Existing Grid/ISO city, full WN-031 browser suite and reviewed runtime integrity baseline pass. (Grid/ISO and integrity pass; full suite moved to WN-031.)
- [x] Privacy, limitations, safe lifecycle logging and owner review are recorded.

## Execution Evidence

2026-11-05 | M1.1 | Red: `UV_PROJECT_ENVIRONMENT=/tmp/agent-harness-py314 UV_PYTHON=3.14 task --dir skills/harness-audit test -- tests/test_logging_contract.py` failed collection with `ModuleNotFoundError: No module named 'lean_log'` (0 tests collected). Green: same command after adding the logger: 7 passed. Final gate: `task --dir skills/harness-audit check` passed Ruff and 258 tests plus 3 subtests under Python 3.14.6. No report artifacts; temporary log files were created under the test's temporary directory. Remaining blocker: M1.2 legacy Docker ENV redaction regression.

2026-11-05 | M1.2 | Red: `task --dir skills/harness-audit test -- tests/test_infra_checks.py -k secret_values_are_redacted_across_env_forms` had 2 failing subtests (legacy sentinel leaked into findings; multiline assignment was not detected). Green: same command, 1 passed with 3 subtests. Full file: 67 passed, 3 subtests. Synthetic sentinel values are absent from returned findings.

2026-11-05 | M1.3 | Red: `task --dir skills/harness-audit test -- tests/test_coverage.py -k reads_tracked_regular_file_and_accounts_for_budget` failed collection because `coverage.py` was absent (0 tests collected). Green: `task --dir skills/harness-audit test -- tests/test_coverage.py`: 7 passed. Exact M1 safety gate: 8 passed, 66 deselected, 3 subtests; Ruff passed. No target code was executed; temporary Git repositories were removed by test cleanup. Remaining task: M1.4 execution/import/network tripwires and permission controls.

2026-11-05 | M1.4 | `task --dir skills/harness-audit test -- tests/test_coverage.py -k safe_read_permission_failure_is_content_free`: 1 passed. `task --dir skills/harness-audit test -- tests/test_audit.py -k static_audit_emits_report_without_target_capabilities`: 1 passed; report validated, no non-Git process/import/socket tripwire fired, and target files/Git status were unchanged. Combined audit/reader files: 16 passed. The exact M1 gate passed 9 tests and 3 subtests. Bypass scan had one documentation-only match and zero direct-output code paths. AC-5 README behavior and limitations documented; no open M1 blocker.

2026-11-05 | M2.1 | Red: the initial legacy core assertion used a capture placeholder and failed while reporting the fixed fixture values. Green: `task --dir skills/harness-audit test -- tests/test_audit.py -k legacy_core_baseline_is_pinned`: 1 passed after pinning literal expected values. Compatibility: `audit.validate` accepts the pre-coverage report, and `coverage` remains absent. `task --dir skills/harness-audit test -- tests/test_audit.py tests/test_score.py`: 29 passed. Remaining task: M2.2 additive envelope/schema and state fields.

2026-11-05 | M2.2 | Red: supported report lacked `quality`; unsupported-only assembly raised exit 3; after the null-core path was added, schema required pillars/score/entropy and nonempty supported stack. Green: supported, Rust-only, infra-only and mixed Python/Node/Rust fixtures validate; CLI emits report/Markdown/triage for unavailable core. Exact M2 gate: 48 passed. `task --dir skills/harness-audit lint`: all checks passed; 39 files formatted. Core baseline remains exact. Remaining task: M2.3 provenance/freshness.

2026-11-05 | M2.3 | Red/green: provenance, freshness, current-summary and observation-binding tests each failed before their helper was added, then passed. `task --dir skills/harness-audit test -- tests/test_coverage.py`: 13 passed, 3 subtests; `task --dir skills/harness-audit lint`: all checks passed, 39 files formatted. No source bytes enter provenance; stale/unknown observations remain unchanged in history and are omitted from current summaries. Remaining task: M2.4 receipt inventory.

2026-11-05 | M2.4 | Red: the receipt tests failed because no classifier existed. Green: `task --dir skills/harness-audit test -- tests/test_coverage.py -k receipt_`: 2 passed, 6 subtests; stale source digest: 1 passed. Full file: 16 passed, 9 subtests. Ruff passed. Receipt outcomes and reason codes contain no source bytes, command, issuer, or execution claim. Remaining task: M2.5 lifecycle logging.

2026-11-05 | M2.5 | Red: CLI lifecycle test found no collection events; injected validation sentinel leaked through a raw stderr print and `run.end` showed exit 0. Green: lifecycle event/stdout test passed; conversion rejection test passed with no sentinel and exit 4; TRACE test passed with aggregate counts only. Exact M2 gate: 59 passed, 9 subtests; Ruff clean. Logging bypass scan found only established user-facing CLI summary/invalid-root output and a documentation mention. M2 exit criteria met; next task M3.1 synthetic fixture materialization.

2026-11-05 | M3.1 | Red: fixture classification failed because `tests/fixtures/coverage/PY-01` did not exist. Green: `task --dir skills/harness-audit test -- tests/test_coverage.py -k golden_component_recipes_are_materialized_and_deterministic`: 1 passed, 7 subtests. Exact M3 gate: 85 passed, 19 subtests; Ruff passed, 41 files formatted. No fixture commands executed. Remaining task: M3.2 seven-topic catalog and check-reference validation.

2026-11-05 | M3.2 | Red: topic catalog/validator and report observations were absent; the report integration then failed on an untracked sentinel/empty observation expectation and a legacy evidence-schema collision. Green: catalog rejects `BAD-99`; seven golden topic source fixtures pass; report emits only tracked source hashes and excludes `UNTRACKED_SENTINEL`. Exact M3 gate: 89 passed, 26 subtests; Ruff passed, 43 files formatted. Remaining task: M3.3 state matrix. Root `task check` later passed all Python, repository-quality, demo and build gates, then timed out in browser tests (21 passed, 5 skipped, 2 not run); docs/integrity were not reached.

2026-11-05 | M3.2 | Red: catalog/collector files and report observations were absent; must-fail reference test rejects `BAD-99`. Green: catalog determinism/reference test passes; seven golden topic source fixtures pass; report integration emits tracked-only provenance and excludes `UNTRACKED_SENTINEL`. Exact M3 gate: 89 passed, 26 subtests; Ruff passed, 43 files formatted. Remaining task: M3.3 full applicability/evidence matrix and execution-claim rejection.

2026-11-05 | M3.3 | Red: `task --dir skills/harness-audit test -- tests/test_audit.py -k 'mixed_report_marks_only_unsupported_language_without_score_change or supported_report_adds_coverage_quality_without_changing_core'` failed with 3 observations instead of 21 and the obsolete `state_matrix_not_implemented` reason. Green: the focused report tests passed; the collector no-source and 140 topic/applicability/evidence schema subtests passed. Exact M3 gate including audit assembly: 109 passed, 166 subtests; Ruff passed; `task integrity`: PASS after updating only the two adapted target hashes. Unsupported component/topic rows are explicit and static execution claims are rejected. Remaining task: M3.4 configured runner traversal.

2026-11-05 | M3.4 | Red: UNIT-RUNNER failed because `collect_runner_edges` was absent; report integration had no resolved CI-to-task edge and retained the M3.4 placeholder. Green: static CI → Taskfile → local pre-commit chain resolves and detects a cycle; missing/dynamic/conditional targets remain unresolved with reason codes; depth exhaustion is bounded. E2E-STATIC reports the task edge with zero target process/import/socket attempts and an unchanged worktree. Exact M3 gate: 112 passed, 166 subtests; Ruff passed; `task integrity`: PASS after refreshing adapted target hashes only. Remaining task: M3.5 must-fail oracles.

2026-11-05 | M3.5 + M3 exit | Golden-data check passes for 43 unique cases, complete AC/scenario joins and closed state enums. Unsupported-only and infra-only reports retain null/unavailable core without invented scores; path/symlink/swap/untracked/read-budget, Docker ENV redaction, receipt, runner cycle/unresolved/depth, and execution-claim rejection oracles pass. Expanded M3 safety/report suite: 180 passed, 169 subtests; exact M3 gate: 95 passed, 166 subtests; logging contract: 7 passed; Ruff and `task integrity`: PASS. Bounded calibration is seven component recipes (two Python, two Node, mixed, infra-only, Rust-only) and three topic fixtures; no universal coverage claim. M3 complete; resume at M4.1.

Add one bounded entry per implemented boundary: date/revision, task ID, red
command and expected failure, green command and collected counts, safe artifact
location, and remaining blocker. Keep raw target output and private paths out of
this tracked record.
