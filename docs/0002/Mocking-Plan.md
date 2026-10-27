---
type: 'Mocking Plan'
id: '0002'
version: 'v0.2'
title: 'Harness Audit Boundary Fixtures'
description: 'As-built test-boundary mapping for filesystem, Git and agent-answer fixtures without replacing internal scoring or reconciliation.'
status: 'draft'
created: '2026-10-27'
updated: '2026-10-27'
generated: 'agent'
verified: 'unverified'
owner: 'Andreas Elser'
tags: [mocking, fixtures, harness-audit]
sources: ['Architecture.md sections 5 and 9', 'Test-Plan.md']
---

<!-- markdownlint-disable-next-line MD025 -->
# Harness Audit Boundary Fixtures

## Boundary Catalog

| Boundary | Fidelity And Cases | Consumer |
| --- | --- | --- |
| Local repository files | Real temporary files; unsupported manifests, malformed config, sample/workspace layouts, existing proposal files | UNIT-02, INT-03, E2E-10 |
| Git metadata | Isolated local Git repositories; full, shallow or absent history; no network or private origin required | INT-04, INF-01 |
| Agent/model output | Fixed answer JSON; correct/invented quotes, missing/duplicate IDs, unknown verdicts | UNIT-05, E2E-06 |
| Report output | Temporary output directories and schema-invalid synthetic reports | SMOKE-08 |
| Adoption baseline | Pinned Git source comparison, not a fake source tree | INF-01, INF-12, UNIT-13 |

No service, queue or remote API is implemented in the audit engine, so no HTTP
mock is required for this as-built scope. Host-managed model access is outside
the script: supplied answers test the boundary without pretending a model ran.
Keep actual internal detection, reconciliation, score arithmetic and triage
logic real when behavioral tests are later authorized. Do not mock a successful
score into existence or use the source probe as a behavioral test.

## Determinism And Failure Policy

Use the deterministic records in Golden-Dataset/dataset.json as scenario
descriptions, not sensitive copied repository contents. Existing fixtures/tests
remain inside the frozen skill and are unchanged. No new mock implementation is
shipped by this docs run. Filesystem failures must preserve target data; output
artifacts are not evidence of successful target-code execution. Retention and
storage boundaries refer to Architecture section 10, not a parallel policy.
