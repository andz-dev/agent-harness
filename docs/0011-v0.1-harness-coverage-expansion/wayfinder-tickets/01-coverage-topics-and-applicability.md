---
type: "Wayfinder Ticket"
id: '0011'
version: "v0.1"
title: "Coverage Topics And Applicability"
description: "Decide the topic taxonomy and applicability contract for broad repository-level harness coverage."
ticket_type: "wayfinder:grilling"
map: "docs/0011-v0.1-harness-coverage-expansion/Map.md"
interaction: "HITL"
status: "open"
blocked_by: []
created: "2026-11-04"
updated: "2026-11-04"
generated: "agent"
verified: "unverified"
owner: "Andreas Elser"
tags: [wayfinder, coverage, applicability]
sources:
  - "docs/0010-v0.1-harness-coverage-discovery/research/coverage-findings.md"
  - "docs/Whats-Next.md (WN-018, WN-028, WN-029)"
---

<!-- markdownlint-disable-next-line MD025 -->
# Coverage Topics And Applicability

## Question

Which repository-level topics belong in the expanded auditor, how should they
be grouped (core score, overlays or optional evidence), and how should
technology/language applicability and unknown coverage be represented? Cover
code quality, security, tests, CI/build, MCP, agent skills, SBOM,
dependencies/supply chain and related controls without assuming every topic
applies to every repository.

Reconcile the existing coverage-map and coding-standard/language-linter backlog
items (WN-028 and WN-029) with the broader overlay proposal (WN-018). Distinguish
auditing arbitrary repositories' SBOMs from WN-017's separate feature to generate
this repository's own SBOM in CI. This decides taxonomy and scope, not catalog
implementation or score changes.
