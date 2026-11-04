---
type: "Wayfinder Ticket"
id: '0011'
version: "v0.1"
title: "Existing Backlog Disposition"
description: "Decide which open backlog topics are included in this specification and which remain separate."
ticket_type: "wayfinder:grilling"
map: "docs/0011-v0.1-harness-coverage-expansion/Map.md"
interaction: "HITL"
status: "closed"
resolution: "owner-confirmed"
blocked_by:
  - "01-coverage-topics-and-applicability"
  - "04-report-city-and-publication"
claimed_by: "GitHub Copilot"
created: "2026-11-04"
updated: "2026-11-04"
generated: "agent"
verified: "unverified"
owner: "Andreas Elser"
tags: [wayfinder, backlog]
sources:
  - "docs/Whats-Next.md"
  - "docs/0010-v0.1-harness-coverage-discovery/research/handoff.md"
---

<!-- markdownlint-disable-next-line MD025 -->
# Existing Backlog Disposition

## Question

After the topic taxonomy and report/city contract are decided, which existing
open backlog items should inform or be absorbed by this specification, and
which remain separate future work? In particular, reconcile WN-018, WN-020,
WN-021 through WN-029 and the explicitly parked WN-030.

Do not mark an item done merely because it is discussed or linked here. Only
finished work may be closed in `docs/Whats-Next.md`; promotion status is reserved
for a real versioned Plan.

## Resolution

2026-11-04: owner confirmed that WN-028 (coverage map) and WN-029 (coding
standards/language-linter gaps) are absorbed as specification inputs; their
backlog rows remain open until a real Plan exists. WN-018 and WN-021 through
WN-025 inform the separate unscored overlay taxonomy and applicable city-topic
requirements; only airport, factory and highway are in the initial later
prototype baseline, with other overlays conditional on applicability. Their
implementation and detailed visual work remain future work.

WN-017 (generating this repository's SBOM), WN-019 (full-road traffic), WN-020
(committed report/summary exception), WN-026 (highway growth detail), WN-027
(station growth), WN-030 (parked editor) and WN-031 (browser-suite gate) remain
separate items. WN-020 requires its own explicit publication decision. The
host/cloud/fleet exclusion remains captured by WN-033. No backlog row is closed
or promoted by this decision; statuses stay unchanged until work is completed
or a versioned Plan is created.
