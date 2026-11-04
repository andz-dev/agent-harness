---
type: "Wayfinder Ticket"
id: '0011'
version: "v0.1"
title: "Evidence States And Assurance"
description: "Decide how audit evidence, provenance and assurance limits are represented."
ticket_type: "wayfinder:grilling"
map: "docs/0011-v0.1-harness-coverage-expansion/Map.md"
interaction: "HITL"
status: "open"
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
