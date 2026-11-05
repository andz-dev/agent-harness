---
type: 'Plan'
id: '0011'
version: 'v0.1'
title: 'Harness Coverage Expansion Plan'
description: 'Acceptance criteria and safety-first delivery slices for additive repository coverage and evidence-led city projection.'
doc_scope: 'proposal'
status: 'draft'
created: '2026-11-05'
updated: '2026-11-05'
stale_after: '2026-12-05'
generated: 'agent'
verified: 'unverified'
owner: 'Andreas Elser'
skills: [harness-audit]
tags: [plan, harness, coverage]
sources: ['Map.md', 'Ideation-Book.md', 'Research-Paper.md', 'Whitepaper.md', '../Whats-Next.md']
---

# Harness Coverage Expansion Plan

## 1. Acceptance Criteria

| ID | Given | When | Then |
| --- | --- | --- | --- |
| AC-1 | A supported baseline report | Coverage is added or omitted | Seven pillar levels, weights, entropy, caps and score are byte-equivalent after removing only the additive coverage fields; no overlay affects arithmetic |
| AC-2 | Python, Node, mixed, infrastructure-only or other-language inputs | Components are detected | Every component has explicit applicability; detected unsupported languages are listed; unsupported-only inputs get a partial report with unavailable score, never zero or an invented quality score |
| AC-3 | A component-topic pair | Coverage is collected | Applicability and evidence status use separate closed enums; unknown is not a failure, inapplicable is not unknown, and unsupported is not silently omitted |
| AC-4 | A retained assertion | It is serialized or displayed | Revision, source path/digest, safe locator, method, observation time and limitations are retained; changed source digests mark it stale and exclude it from current-evidence summaries |
| AC-5 | Traversal, symlink, untracked, oversized or secret-bearing inputs | Safe collection runs | Reads are restricted to bounded allowlisted tracked regular files; escapes and links are rejected; sensitive values, raw excerpts, commands and endpoint identities occur in no output channel |
| AC-6 | A local receipt, including valid-looking, forged, stale, failed and partial variants | Receipt admission runs | It is presence-only and unverified; none can produce execution_observed; malformed or oversized input produces a safe limitation, not an assurance claim |
| AC-7 | CI, hooks and task-wrapper declarations | Reachability is traced | Only configured target reachability is reported; cycles, dynamic commands and missing targets are bounded and disclosed; installation/execution is not inferred |
| AC-8 | Each supported topic | Its Python/Node or repository-neutral collector runs | The versioned topic catalog links existing check IDs, defines applicability, locators and limits, and has deterministic positive, edge and negative fixtures; no universal coverage claim is made |
| AC-9 | Legacy, current and unsupported-version reports | Conversion runs | Legacy reports explicitly lack coverage; current reports preserve all component-topic states and provenance; unsupported versions are rejected with a safe diagnostic rather than guessed |
| AC-10 | Applicable or undetermined airport/factory/highway topics | A city object is selected | Topic identity and independent applicability/evidence/freshness indicators are shown with safe details; object presence and L0-L3 geometry imply no coverage assurance; inapplicable/unsupported topics remain discoverable in the inventory |
| AC-11 | A simulated preset or synthetic prototype | It is viewed or exported | Synthetic/prototype provenance stays explicit and can never be promoted into observed evidence; conditional extra overlays require applicable topics |
| AC-12 | Representative Python and Node samples plus mixed/unsupported/infra-only cases | Validation runs | Every AC maps to a scenario and deterministic fixture or reasoned non-data gate; must-fail controls catch false assurance, fabricated score, path escape, leakage and execution promotion |
| AC-13 | Proposed viewer or imported-runtime changes | They are accepted for release | Full app browser suite passes without skips/weakened assertions; four rotations and desktop/mobile views are checked; adapted-runtime changes receive a reviewed baseline update, never integrity bypass |
| AC-14 | New runnable coverage stages | Normal, verbose, error and termination paths run | The lean-logging contract is preserved with redacted lifecycle/TRACE events and correct sinks; collected content never appears in diagnostics; logs remain uncommitted |

## 2. Problem Statement

Broader repository coverage must remain explainable without conflating declarations,
implementation, execution, applicability or visual maturity. The output is an
additive unscored coverage contract, not a recalibration or security certificate.

## 3. Inputs Analyzed

Decision authority: [Map decisions](Map.md#decisions-so-far) and eight closed
tickets, especially [receipt admission](wayfinder-tickets/08-execution-receipt-admission.md#resolution).
Synthesis: [ideation](Ideation-Book.md#decision-summary),
[research results/limits](Research-Paper.md#results) and
[whitepaper recommendation](Whitepaper.md#recommended-next-steps).
WN-028/WN-029 in the [backlog](../Whats-Next.md) are promoted inputs, not
implemented features. Supporting 0010 observations remain historical.

## 4. Scope

In: repository-only static evidence, Python and Node adapters, neutral topic
definitions, safe partial reports, bounded configured-target tracing, report
versioning and airport/factory/highway coverage projection. Initial topics:
code quality/standards, testing, CI/build, security declarations, dependencies/
SBOM/supply chain, MCP, and agent skills/extensions. Existing checks are linked,
not rerun or duplicated merely to populate an overlay.

Out: new language adapters; executing/importing/installing audited code; host,
cloud or fleet data; authenticated receipt infrastructure; score changes;
real-report publication; editor resumption; traffic simulation and growth detail.
WN-017, WN-019/020, WN-026/027, WN-030/031 and WN-033 remain separate work.

## 5. Assumptions And Conflicts

| Conflict or unknown | Resolution | Basis |
| --- | --- | --- |
| Map says stop before spec workflow | Superseded for this run by the owner's 2026-11-05 request and explicit path/source approval; original remains historical | Current authorization |
| Ticket 02 permits revision-bound receipts | Narrowed by ticket 08: no execution claim without independent issuer authentication; no such boundary exists in v0.1 | Owner-confirmed later decision |
| Existing city grows by L0-L3 | Coverage indicators are orthogonal; no applicability/evidence-to-level conversion is permitted | Ticket 04; design prototype must evaluate this |
| Partial report versus legacy score shape | Add versioned envelope; unavailable quality score is null, with explicit partial status and limitations | Tickets 03/07/08 |
| Representative sample quantity | Two distinct synthetic samples per supported adapter plus mixed/infra-only/unsupported cases is the initial test-design minimum, not a generalization claim | Scope fixed to Python/Node; AC-12 |
| Prototype visual choice | Original alternative-layout selection is superseded by the owner's 2026-11-05 instruction: use the defined Grid and existing ISO city; evaluate evidence presentation there, not a replacement city | Current owner instruction; app DESIGN City map and Camera |

## 6. Proposed Approach

Use the existing static pipeline and report schema as integration points. Add a
coverage contract version, topic catalog and bounded collection API; keep core
scoring untouched. Freshness is separate from evidence state. A report contains
one or more assertions per component/topic, not a single invented confidence rank.
Reserve execution_observed for a future authenticated path; reject it from v0.1
repository-local collection and synthetic-to-real conversion.

Use the existing Grid and ISO city defined in
[DESIGN](../../apps/harness-city/DESIGN.md#city-map-grid), preserving its
[camera](../../apps/harness-city/DESIGN.md#camera), district colours, assets,
scene builders and selection model. No standalone replacement layout or new
visual-style choice is required. Airport remains at x 45..61, z 1..7; the
goods-industry/factory reservation is x 48..62, z -18..-8; highway is
x 62.5..69.5, with the specified tunnel/bridge reservations. These are design
reservations, not a claim that every planned object is implemented.

Topic-to-object mapping: airport = infrastructure, factory =
build/artifact/dependency supply chain, highway = CI/task/hook reachability.
Shared topics may reference multiple objects by stable topic ID;
objects never create duplicate score contributions. Later architecture owns
the exact wire schema and field responsibilities.

### Storage Policy Reference

Application storage/configuration follows the shared policy identified here:
`~/.agents/shared/references/application-storage-configuration-policy.md`,
sections 2, 6, 8 and 9 (installed maintainer asset; no portable public URL has
been verified). Downstream artifacts link to this
[policy reference](#storage-policy-reference), not a copy of its rules.
This plan introduces no persistence migration, new
configuration source, database, external root or report-publication exception.
Concrete integration with existing report/history output needs an explicit
Architecture disposition before implementation. This docs run writes synthetic
artifacts only. Prototype state is memory-only.

## 7. Milestones

| Slice | Outcome | ACs | Dependency |
| --- | --- | --- | --- |
| M1 | Safe evidence access and Docker ENV regression | AC-5 | None; blocks sensitive expansion |
| M2 | Coverage enums, provenance, partial reports and logging | AC-1, AC-2, AC-3, AC-4, AC-6, AC-14 | M1 |
| M3 | Topic catalog, collectors and reachability | AC-7, AC-8, AC-12 | M2 |
| M4 | Versioned conversion within the existing Grid and ISO city | AC-9, AC-10, AC-11 | M3 and evidence-presentation prototype |
| M5 | Complete regression, browser and integrity gates | AC-12, AC-13 | M1-M4 and WN-031 |

## 8. Risks

Redaction leakage is release-blocking; test all sinks, including failed parsing.
Static target graphs can be cyclic/dynamic; report unknown instead of evaluating
commands. Unsupported-only inputs can corrupt legacy assumptions; test schema,
Markdown and converter behavior. Unreviewed runtime hashes cannot be normalized
away; review baseline updates separately. No fixture or browser gate may be
deleted, skipped, weakened or narrowed to claim success.

## 9. Validation And Definition Of Done

Commands below are implementation gates, **not results of this docs run**. Planned
test modules are created by implementation using test-first discipline. A missing
test is a failing prerequisite, never a successful zero-test run. Run from repo root.

### M1 Contract

**Objective:** Stop unsafe reads and evidence leaks.
**Read first:** AC-5; skill AGENTS; existing infra check tests.
**Constraints:** No audited code execution, no real secrets, no baseline bypass.
**validate:** `task --dir skills/harness-audit test -- tests/test_infra_checks.py tests/test_coverage.py -k 'redact or safe_read'`
**Stop when:** All canaries and read-boundary scenarios run and pass with no skips.
**Document:** Record AC-5 behavior and limitations in the skill README.

### M2 Contract

**Objective:** Preserve score compatibility and honest evidence semantics.
**Read first:** AC-1..AC-6, AC-14; load `lean-logging` before implementing or
reviewing logging, including TRACE; discover existing logger before configuration.
**Constraints:** No score arithmetic change; local receipts remain unverified.
**validate:** `task --dir skills/harness-audit test -- tests/test_coverage.py tests/test_audit.py tests/test_score.py tests/test_logging_contract.py`
**Stop when:** Schema, partial-report, core regression and logging contract checks
pass with all required scenarios collected.
**Document:** Record coverage version and compatibility semantics.

### M3 Contract

**Objective:** Add topic-specific coverage without duplicate scoring.
**Read first:** AC-7/8/12; future Test-Plan topic matrix.
**Constraints:** Python/Node only; no task or hook command execution.
**validate:** `task --dir skills/harness-audit test -- tests/test_coverage.py tests/test_detect_stack.py tests/test_run_checks.py`
**Stop when:** Every topic and adapter sample maps to passing scenarios and
must-fail controls reject every prohibited promotion.
**Document:** Publish supported topic/adapter limits, not assurance claims.

### M4 Contract

**Objective:** Preserve coverage states through conversion and city selection.
**Read first:** AC-9/10/11; Prototype decision; app AGENTS and DESIGN Grid/Camera.
**Constraints:** Update DESIGN before changing a design decision; no score or
prototype-to-real promotion; no new traffic/editor scope.
**validate:** `task tools:test && task app:check && task app:test`
**Stop when:** Converter contract and full browser suite pass, including mobile,
four rotations, unsupported/legacy inputs and synthetic provenance.
**Document:** Update asset registry, click explanation and level-ladder distinction.

### M5 Contract

**Objective:** Accept only fully checked implementation.
**Read first:** AC-12/13; extraction manifest; WN-031.
**Constraints:** Reviewed baseline updates only; no generated/private report commits.
**validate:** `task check && task integrity`
**Stop when:** Full gates exit 0 without weakened assertions and review approves
intentional runtime baseline changes; otherwise retain explicit blockers.
**Document:** Record exact commands, outcomes and remaining limits.

## 10. Open Questions

No visual-layout selection remains open: the owner selected the defined Grid
and existing ISO city on 2026-11-05, superseding the proposed alternatives.
The mandatory prototype still evaluates evidence presentation against that
baseline. Unavailable storage or logging integration details block the relevant
implementation phase, not permission to invent a new runtime or external service.

## 11. Next Steps

Original next step (superseded): evaluate three standalone visual alternatives.
Updated next step: use the defined Grid and existing ISO city, evaluate the
evidence-presentation contract on synthetic data, and carry the result into
Architecture, testing, mocks, golden dataset, ontology and Implementation.
All product tasks remain unstarted.
