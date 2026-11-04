---
type: "Wayfinder Ticket"
id: '0011'
version: "v0.1"
title: "Coverage Topics And Applicability"
description: "Decide the topic taxonomy and applicability contract for broad repository-level harness coverage."
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

## Resolution

2026-11-04: owner confirmed that the existing seven pillars remain the only
scored core; broader security, SBOM/supply-chain, MCP, skills/extensions and
language-standard coverage are separate unscored overlays, with existing checks
linked rather than duplicated. Assess applicability per detected repository
component, keeping inapplicable distinct from unknown or unsupported; missing
evidence must not silently become failure or assurance. The specification will
name an explicit, supportable adapter set, retain Python and Node as the current
baseline and make no universal language-coverage claim. Exact evidence-state
semantics remain for [Evidence States And Assurance](02-evidence-states-and-assurance.md);
the initial adapter set is a new downstream decision.
