---
type: "Wayfinder Ticket"
id: '0011'
version: "v0.1"
title: "Report City And Publication Contract"
description: "Decide how coverage evidence is reported, projected into the city and retained."
ticket_type: "wayfinder:grilling"
map: "docs/0011-v0.1-harness-coverage-expansion/Map.md"
interaction: "HITL"
status: "closed"
resolution: "owner-confirmed"
blocked_by:
  - "01-coverage-topics-and-applicability"
  - "02-evidence-states-and-assurance"
  - "03-safe-evidence-and-reachability"
claimed_by: "GitHub Copilot"
created: "2026-11-04"
updated: "2026-11-04"
generated: "agent"
verified: "unverified"
owner: "Andreas Elser"
tags: [wayfinder, report, harness-city]
sources:
  - "docs/0010-v0.1-harness-coverage-discovery/research/coverage-findings.md"
  - "docs/Whats-Next.md (WN-020, WN-021, WN-024, WN-025)"
---

<!-- markdownlint-disable-next-line MD025 -->
# Report City And Publication Contract

## Question

How should a report represent the agreed coverage states and project them into
Harness City without turning a prototype or simulated object into audit
evidence? Decide the minimum city-map requirements for the later
spec-workflow prototype, and whether a normalized summary may be committed.

Keep raw reports and source excerpts out of committed artifacts. Consider the
relevant city-overlay backlog as input, but do not assume the parked editor or
traffic work is part of this destination.

## Resolution

2026-11-04: owner confirmed that city objects represent topic areas while
separate visible indicators represent applicability and evidence status; an
object's presence never implies that a control exists or works. The later
spec-workflow prototype starts with an airport, factory and highway, adding
other overlays only when their coverage topics are applicable. This is not a
commitment to resume the parked editor or traffic simulation. Selecting an
object shows its topic evidence states, applicability, source references,
collection method, observation time and limitations, without secrets, raw
excerpts or commands. The existing prohibition on committed real-target audit
reports remains; any normalized-summary exception needs a separate explicit
owner decision under WN-020.
