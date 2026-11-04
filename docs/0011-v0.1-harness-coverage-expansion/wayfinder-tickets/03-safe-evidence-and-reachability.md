---
type: "Wayfinder Ticket"
id: '0011'
version: "v0.1"
title: "Safe Evidence And Reachability"
description: "Decide safe repository evidence boundaries and the conditions for claiming checks or runners execute."
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
tags: [wayfinder, security, evidence]
sources:
  - "docs/0010-v0.1-harness-coverage-discovery/research/coverage-findings.md"
  - "docs/Whats-Next.md#WN-014"
---

<!-- markdownlint-disable-next-line MD025 -->
# Safe Evidence And Reachability

## Question

What bounded read, privacy/redaction and freshness rules are required before
the auditor may assess security-sensitive topics, MCP or skill provenance? Decide
how unsupported and infrastructure-only repositories are reported, and what
evidence is necessary before attributing CI, task-wrapper or hook execution to a
real target.

Account for the known Docker `ENV` redaction lead in 0010 without treating this
wayfinder as permission to patch runtime code. Static declarations must not be
reported as installed, reachable or enforced state without supporting evidence.

## Resolution

2026-11-04: owner confirmed a bounded, tracked-repository-file allowlist with
symlink rejection and no execution, import, installation or connection to the
audited repository. Security-sensitive checks must not read or retain secret
values; redaction is required before evidence is stored or displayed. The known
Docker `ENV` redaction defect blocks broader secret, MCP and skill-provenance
checks until it is fixed in the downstream specification/implementation work;
this wayfinder does not patch runtime code. Unsupported or infrastructure-only
repositories receive honest partial reports with explicit unsupported and
inapplicable areas, not fabricated quality scores. CI, hook and task-wrapper
tracing may establish configured/reachable targets, not hook installation or
execution; observed execution requires the receipt contract. No live CI or
host/cloud inspection is inferred.
