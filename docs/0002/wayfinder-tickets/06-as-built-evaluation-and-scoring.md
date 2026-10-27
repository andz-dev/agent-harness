---
type: "Wayfinder Ticket"
id: '0002'
version: "v0.2"
title: "As-Built Evaluation And Scoring"
description: "Source-reconstructed evaluation, reconciliation, scoring and uncertainty rules of the frozen implementation."
ticket_type: "wayfinder:task"
map: "docs/0002/Map.md"
interaction: "AFK"
status: "closed"
resolution: "source-reconstructed"
blocked_by: ["05-frozen-source-and-history"]
created: "2026-10-27"
updated: "2026-10-27"
generated: "agent"
verified: "unverified"
owner: "Andreas Elser"
tags: [wayfinder, evaluation]
---

<!-- markdownlint-disable-next-line MD025 -->
# As-Built Evaluation And Scoring

## Question

How does the implemented static-plus-agent workflow actually combine evidence?

## Resolution

2026-10-27 source inspection: `audit.assemble` detects components, runs static
and Git checks, plans LLM tasks and optionally applies agent-supplied answers.
`llm_layer.apply_answers` validates quotes, changes unsupported pass/fail answers
to unknown, and supplies unknown findings for missing answers. It does not call
a model. Findings replaced by Git/LLM check IDs are not independently averaged.
`score.build` derives seven weighted pillars, gate/ratio levels, caps, entropy
and top gaps, then checks arithmetic. See the [as-built findings](../research/As-Built-Findings.md).
These are heuristic static audit outcomes, not observed check execution or
commit rejection. Runtime qualification remains outside the frozen solution.
