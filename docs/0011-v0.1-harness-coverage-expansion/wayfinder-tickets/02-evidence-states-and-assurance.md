---
type: "Wayfinder Ticket"
id: '0011'
version: "v0.1"
title: "Evidence States And Assurance"
description: "Decide how audit evidence, provenance and assurance limits are represented."
ticket_type: "wayfinder:grilling"
map: "docs/0011-v0.1-harness-coverage-expansion/Map.md"
interaction: "HITL"
status: "closed"
resolution: "owner-confirmed"
blocked_by: []
claimed_by: "GitHub Copilot"
created: "2026-11-04"
updated: "2026-11-04"
generated: "agent"
verified: "unverified"
owner: "Andreas Elser"
tags: [wayfinder, evidence, assurance]
sources:
  - "docs/0010-v0.1-harness-coverage-discovery/research/coverage-findings.md"
  - "docs/0010-v0.1-harness-coverage-discovery/spike/result.json"
---

<!-- markdownlint-disable-next-line MD025 -->
# Evidence States And Assurance

## Question

What evidence states and provenance must the auditor preserve so that configured
or declared controls, shipped static checks, observed execution, prototypes and
unknowns cannot be conflated? Decide how source paths/digests, observation time,
staleness and assurance limits affect report claims.

Use the 0010 inventory as bounded evidence, not a representative calibration
corpus or proof of runtime enforcement. The existing score and weights are
already fixed for this effort; this ticket decides evidence meaning, not score
arithmetic.

## Resolution

2026-11-04: owner confirmed that applicability is separate from evidence
status. Applicability distinguishes applicable, inapplicable, unsupported and
undetermined; evidence status distinguishes declared, static implementation
found, execution observed, prototype/simulated and unknown. Each assertion
identifies the target repository revision, source paths and digests, an evidence
locator, collection method and observation time. Do not retain raw excerpts,
commands, endpoint identities or credentials. Mark evidence stale when its
referenced source digest changes. Claim execution observed only from a receipt
bound to the repository revision, run identity and time; without one, report
only what is declared or statically present. These states describe observations,
not security/quality guarantees, and do not alter the existing score.

Receipt sources and integrity/admission rules remain open in
[Execution Receipt Admission](08-execution-receipt-admission.md).
