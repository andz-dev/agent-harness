---
type: "Wayfinder Ticket"
id: '0002'
version: "v0.2"
title: "Frozen Source And Historical Inputs"
description: "Retrospective source-selection record for the owner-directed adoption of harness-audit."
ticket_type: "wayfinder:task"
map: "docs/0002/Map.md"
interaction: "AFK"
status: "closed"
resolution: "source-reconstructed"
blocked_by: []
created: "2026-10-27"
updated: "2026-10-27"
generated: "agent"
verified: "unverified"
owner: "Andreas Elser"
tags: [wayfinder, provenance]
---

<!-- markdownlint-disable-next-line MD025 -->
# Frozen Source And Historical Inputs

## Question

Which implementation and historical inputs define the documentation baseline?

## Resolution

2026-10-27: the owner explicitly selected the existing
[harness-audit skill](../../../skills/harness-audit/SKILL.md)
and prohibited modifying it. Source inspection pinned commit
`766dd40add66b2806bab5c8d0926d3b5d13056a7`, skill tree
`e5c34a57bd87454c2857bb9f907aea24805b11d8`. The supplied
[backlog](../research/BACKLOG.md) and [catalog](../research/catalog.yaml) are
historical inputs. The active catalog is authoritative for current checks.
Documentation v0.2 does not relabel tool `0.1.0` or schema/catalog `0.1`.
This is reconstructed evidence of the owner's adoption, not a new product vote.
