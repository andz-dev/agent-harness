---
type: "Wayfinder Ticket"
id: '0011'
version: "v0.1"
title: "Validation And Acceptance"
description: "Decide how the specification will define representative validation and honest acceptance claims."
ticket_type: "wayfinder:grilling"
map: "docs/0011-v0.1-harness-coverage-expansion/Map.md"
interaction: "HITL"
status: "closed"
resolution: "owner-confirmed"
blocked_by:
  - "01-coverage-topics-and-applicability"
  - "02-evidence-states-and-assurance"
  - "03-safe-evidence-and-reachability"
  - "04-report-city-and-publication"
claimed_by: "GitHub Copilot"
created: "2026-11-04"
updated: "2026-11-04"
generated: "agent"
verified: "unverified"
owner: "Andreas Elser"
tags: [wayfinder, validation]
sources:
  - "docs/0010-v0.1-harness-coverage-discovery/research/coverage-findings.md"
  - "docs/0010-v0.1-harness-coverage-discovery/research/handoff.md"
---

<!-- markdownlint-disable-next-line MD025 -->
# Validation And Acceptance

## Question

What validation evidence and acceptance gates must the eventual specification
require to establish topic applicability, evidence-state behavior, safe report
projection and honest limitations across representative repository shapes?

The 0010 probe (11 real files, 16 source facts and 7 synthetic cases) is not a
representative cross-language corpus. Decide what broader fixture or repository
evidence is needed without claiming a universal security or quality guarantee.

## Resolution

2026-11-04: owner confirmed deterministic fixtures for every supported topic and
evidence state, plus representative repository samples for each adapter
ultimately selected. Do not set a universal sample count before the adapter set
is decided. Require must-fail controls showing that unknown evidence is not
promoted to verified, unsupported scope does not produce a fabricated score,
path escapes are rejected, sensitive values never appear in outputs, and
static declarations do not become execution claims. Report-to-city validation
must preserve topic, applicability and evidence-status distinctions; object
presence or a prototype preset must not imply observed audit evidence.

The specification must require reproducible tests and explicit limitations,
without a universal security or quality guarantee. The spec may be approved
with the current viewer-browser gate recorded as a prerequisite; viewer changes
are not accepted until the full browser suite passes. WN-031 remains open and
tracks that gate.
