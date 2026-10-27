---
type: "Wayfinder Ticket"
id: '0002'
version: "v0.2"
title: "Dual Evaluation And Reconciled Coverage"
description: "Decide how static evidence and agent-led repository review cover harness concerns and combine without hiding gaps or disagreements."
ticket_type: "wayfinder:grilling"
map: "docs/0002/Map.md"
interaction: "HITL"
status: "closed"
resolution: "superseded"
blocked_by: []
created: "2026-10-26"
updated: "2026-10-26"
stale_after: "2026-11-09"
generated: "agent"
verified: "unverified"
owner: "Andreas Elser"
tags: ["wayfinder", "qualification", "evaluation"]
sources:
  - "Owner request for static plus agent-led repository evaluation, 2026-10-26"
  - "docs/skills/0036-v0.1-agent-harness-setup/wayfinder-tickets/01-evidence-and-assessment-scope.md, Resolution"
---

<!-- markdownlint-disable-next-line MD025 -->
# Dual Evaluation And Reconciled Coverage

## Resolution

Superseded on 2026-10-27.

The owner adopted the existing frozen `harness-audit` implementation instead of
continuing this prospective design. This question is a closed scope exclusion,
not an approved answer. See [the replacement map](../Map.md).

## Question

What must static assessment and agent-led repository evaluation each contribute
to a complete dry-run report, and how are their findings reconciled?

The owner requires both approaches. Decide the applicable coverage inventory,
whether the agent must review every concern rather than only scanner findings,
and how it discovers unsupported conventions within the approved scope. Define
the minimum source evidence for an agent finding, missing-evidence behavior,
provenance, contradictory findings, stale context and what a limited evaluation
may claim. Confidence or agreement is not proof of runtime enforcement.

Keep review distinct from execution: use approved reads only, request named scope
expansion when necessary, and never treat a discovered command as execution
permission. Decide whether direct owner-approved exploration beyond root files
is sufficient or an exact file list must be reviewed first. Private-data and
secret exclusions continue to apply.

Stress-test a monorepo with no root manifest, an unfamiliar CI provider, a static
scanner that misses a real control, a misleading instruction file, and an agent
that cannot obtain enough evidence. Define how the final report carries both
original findings and a reasoned reconciliation rather than averaging scores or
silently choosing the most optimistic result.

This decides the contract, not scanners, prompts, model vendors or schemas.
