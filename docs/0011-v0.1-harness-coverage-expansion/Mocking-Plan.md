---
type: 'Mocking Plan'
id: '0011'
version: 'v0.1'
title: 'Harness Coverage Expansion Mocking Plan'
description: 'Deterministic external-boundary controls without mocking coverage decisions or city projection.'
status: 'draft'
created: '2026-11-05'
updated: '2026-11-05'
generated: 'agent'
verified: 'unverified'
owner: 'Andreas Elser'
doc_scope: 'proposal'
sources: ['Architecture.md', 'Test-Plan.md']
---

# Harness Coverage Expansion Mocking Plan

## Boundary Policy

Input digest: [Architecture](Architecture.md) sections 3/5/6/7 define local-only
bounded reads, additive report projection and full logging; [Test Plan](Test-Plan.md)
defines consumers below. No new external service is part of this design.
Mocks are proposed fixtures/test controls, not implemented product components.

Keep the real scorer, topic resolution, schema validation, receipt classification,
converter and viewer. Never stub the very decision whose truth is under test.

## Control Inventory

| ID | Boundary | Fidelity / deterministic setup | Success and failure behavior | Consumer |
|---|---|---|---|---|
| MOCK-FS | OS filesystem and tracked metadata | Real temporary Git repository, not a fake path resolver | Tracked regular input; reject escapes/symlinks/untracked/swap/oversize; safe permission failure | INFRA-SAFE, UNIT-REDACT, E2E-STATIC |
| MOCK-CLOCK | Observation time | Fixed UTC clock stub at 2026-11-05T00:00:00Z | Stable timestamps; missing/invalid identity yields unknown freshness, not current | UNIT-PROVENANCE, INT-REPORT |
| MOCK-CAPABILITY | Process/import/network boundary | Fail-fast test tripwire; permitted Git metadata operation scoped separately | No target process/import/socket call; attempted call fails immediately with a safe sentinel | E2E-STATIC, UNIT-RUNNER |
| MOCK-RECEIPT | Untrusted local receipt file | Literal synthetic receipt variants on real filesystem | Absent/present/invalid/stale/partial/failed; all remain unverified | UNIT-RECEIPT, INT-REPORT |
| MOCK-OUTPUT | Report/log/export sink | Temporary file/stream capture | Valid output captured; safe write/permission failure; sentinel absent in every sink | SMOKE-LOG, UNIT-REDACT, E2E-EXPORT |
| MOCK-VERSION | Input report bytes | Static synthetic legacy/current/future/malformed fixtures | Preserve supported core, mark unsupported coverage, reject invalid envelope | INT-CONVERT, INT-CITY |
| MOCK-BROWSER-DATA | Browser input data | Deterministic synthetic converted JSON only | Real city renders with current/unknown/stale/simulated state; malformed input safely limited | E2E-CITY, E2E-EXPORT |

The fixed clock is only a test seam; do not make a new runtime time service.
Do not mock Three.js, raycasting, screenshots or the production DOM in E2E cases.

## Failure Fidelity

File permissions/type changes and safe-read budgets are actual OS/test-boundary
conditions. Inject read errors only when a platform cannot reproduce a condition
deterministically, and retain at least one real-filesystem integration path.
Use distinct synthetic sensitive sentinels in legacy and modern Docker ENV syntax;
check stdout, stderr, retained logs, JSON reports, city JSON and generated HTML.
Expected sentinels belong only in private temporary fixture inputs and assertions,
not committed audit outputs or prototype screenshots.

Local receipt fixtures can claim success or contain a command, but that text is
untrusted input. Never execute it, connect to its endpoints, authenticate its
issuer by assertion, or use its self-declared status as execution evidence.
Missing/dynamic runner nodes are unresolved; cycles/depth exhaustion terminate
with the exact reason in Architecture section 7.

No timeout/auth/rate-limit protocol simulation is needed: there is no remote API
client. Add none merely to fill a template. Network attempts are forbidden and
tested by tripwire rather than by a fake successful remote service.

## Artifact And Reset Strategy

The [golden dataset](Golden-Dataset/dataset-guide.md) owns fixed case IDs and
expected outcomes. Implementation materializes its recipe records into temporary
tracked fixture trees or the established audit fixture location; consumers use
stable IDs. Reuse existing test helpers after inspecting their public behavior.
Avoid a new reusable mock framework for seven small boundary controls.

Follow the [storage policy reference](Plan.md#storage-policy-reference) for output
and configuration tests. Every test owns and cleans its temporary directories;
no shared-terminal `cd`, persistent environment export, real credentials or
network setup. Assert worktree status unchanged by the target audit.

## Contract Drift And Handoff

Schema changes update Architecture first, then mock values, golden records,
ontology and scenario assertions in that order. Do not repair mismatches by
loosening enums or promoting evidence. Each mock has named consumers; the future
tests must exercise both successful and failing boundary behavior.

Outputs: this plan and stage sidecar. No executable mocks were created. Golden
Dataset may proceed using these deterministic boundaries; release acceptance
still requires the actual tests from Test-Plan, including WN-031.
