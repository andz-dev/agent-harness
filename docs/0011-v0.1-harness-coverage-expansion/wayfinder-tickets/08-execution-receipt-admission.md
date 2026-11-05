---
type: "Wayfinder Ticket"
id: '0011'
version: "v0.1"
title: "Execution Receipt Admission"
description: "Decide which repository-local execution receipts can support observed-execution claims and how to validate them."
ticket_type: "wayfinder:grilling"
map: "docs/0011-v0.1-harness-coverage-expansion/Map.md"
interaction: "HITL"
status: "open"
blocked_by:
  - "03-safe-evidence-and-reachability"
  - "06-validation-and-acceptance"
claimed_by: "GitHub Copilot"
created: "2026-11-04"
updated: "2026-11-04"
generated: "agent"
verified: "unverified"
owner: "Andreas Elser"
tags: [wayfinder, evidence, execution]
sources:
  - "docs/0011-v0.1-harness-coverage-expansion/wayfinder-tickets/02-evidence-states-and-assurance.md#resolution"
  - "docs/0011-v0.1-harness-coverage-expansion/wayfinder-tickets/03-safe-evidence-and-reachability.md"
  - "docs/0011-v0.1-harness-coverage-expansion/wayfinder-tickets/06-validation-and-acceptance.md"
---

<!-- markdownlint-disable-next-line MD025 -->
# Execution Receipt Admission

## Question

Within the repository-only evidence boundary, which locally available execution
receipts may support an `execution observed` claim, what binds them to the target
revision and run, and how should issuer identity, integrity, freshness, partial
results and invalid receipts be handled? Do not infer a live CI connection or
host/cloud inspection from a repository declaration.
