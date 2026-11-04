---
type: "Wayfinder Map"
id: '0011'
version: "v0.1"
title: "Evidence-First Harness Coverage Expansion"
description: "Decisions toward an approved specification for broader repository-scoped harness auditing and evidence-led city visualization."
ticket_type: "wayfinder:map"
status: "open"
created: "2026-11-04"
updated: "2026-11-04"
generated: "agent"
verified: "unverified"
owner: "Andreas Elser"
tags: [wayfinder, harness, coverage]
sources:
  - "docs/0010-v0.1-harness-coverage-discovery/Ideation-Book.md"
  - "docs/0010-v0.1-harness-coverage-discovery/research/coverage-findings.md"
  - "docs/0002-v0.2-harness-audit-as-built-adoption/Tracker.md"
  - "docs/Whats-Next.md"
---

<!-- markdownlint-disable-next-line MD025 -->
# Evidence-First Harness Coverage Expansion

## Destination

Reach an owner-approved, implementation-ready specification for a broader
repository-scoped harness auditor and its evidence-led report-to-city contract.
Stop before running `spec-workflow-orchestrator` or implementing the specification.

## Notes

- The requested coverage includes relevant code quality, security, testing,
  CI/build, MCP, agent skills, SBOM, dependency/supply-chain and related topics.
  Applicability and unknown coverage must be explicit; this is not a promise that
  every topic applies to every repository.
- Preserve the existing seven-pillar scoring arithmetic and weights. Broader
  coverage remains distinct from the existing score.
- Repository files are the evidence boundary for this version. Machine-installed
  state, cloud-connected evidence and fleet-wide scoring are excluded and tracked
  as [Host and cloud audit evidence](../Whats-Next.md).
- The spec must define how city visualization reflects report evidence and keeps
  prototypes distinct. The visual draft, including airport, factory, highway and
  related city elements, belongs to the later prototype stage of the owner's
  `spec-workflow-orchestrator` run.
- Existing backlog items are inputs, not completed work: WN-028 and WN-029 are
  direct coverage-map candidates; WN-018 and WN-021 through WN-027 may inform
  topic or city requirements; WN-017 (generating this repository's SBOM) is
  distinct from auditing arbitrary repositories; WN-020 publication, WN-030's
  parked editor and WN-031's browser-suite gate remain unresolved unless their
  own work is completed.
- Use the [local Markdown tracker](../0002-v0.2-harness-audit-as-built-adoption/Tracker.md).
  Charting closes no tickets and records no owner decisions beyond those stated
  in this map.

## Decisions so far

<!-- No child decisions have been resolved during charting. -->

## Not yet specified

No additional decision is sharp enough to ticket beyond the six open child
questions. Revisit this section as their resolutions expose the next frontier.

## Out of scope

- Machine-installed state, cloud-connected evidence and fleet-wide scoring;
  recorded for a future effort in [Host and cloud audit evidence](../Whats-Next.md).
- Recalibrating or changing the existing seven-pillar score or weights.
- Running the downstream specification workflow or implementing its resulting
  checks, report changes or city visualization in this wayfinder effort.
- Resuming the parked city editor or expanding traffic simulation; the later
  prototype is for validating the requested city visualization, not an editor
  commitment.
