---
type: "Wayfinder Map"
id: '0002'
version: "v0.2"
title: "Harness Audit Adoption And Reverse Engineering"
description: "As-built decision provenance for adopting the frozen harness-audit solution, replacing the earlier prospective setup map."
ticket_type: "wayfinder:map"
status: "closed"
created: "2026-10-26"
updated: "2026-10-27"
stale_after: "2026-11-09"
generated: "agent"
verified: "unverified"
owner: "Andreas Elser"
tags: ["wayfinder", "agent-harness", "qualification"]
sources:
  - "Owner acceptance of completion and v0.2 recommendations, 2026-10-26"
  - "Owner request for combined static and agent-led repository evaluation, 2026-10-26"
  - "docs/skills/0036-v0.1-agent-harness-setup/Map.md, Destination and Notes"
---

<!-- markdownlint-disable-next-line MD025 -->
# Harness Audit Adoption And Reverse Engineering

## Destination

Reverse-engineer the existing `harness-audit` solution into a complete v0.2
documentation chain without changing that solution. Stop and retire the 0036
implementation. Document implemented behavior, historical evidence and known
limits separately; do not design a replacement or claim runtime qualification.

## Notes

The owner's explicit direction on 2026-10-27 supersedes the prospective map
below: adopt [harness-audit](../../skills/harness-audit/SKILL.md)
as-is and use the supplied [backlog](research/BACKLOG.md) and
[catalog snapshot](research/catalog.yaml) as history. This map is a retrospective
provenance index, not a replay of new HITL approvals. New task tickets record
completed source investigations; they do not authorize deployment or application.
Only this documentation/adoption effort is v0.2: tool `0.1.0`, schema/catalog
`0.1` and the skill's internal backlog versions remain unchanged.

Frozen source: commit `766dd40add66b2806bab5c8d0926d3b5d13056a7`, skill tree
`e5c34a57bd87454c2857bb9f907aea24805b11d8`. The full chain is documentation of
that snapshot. There is no remaining product-choice frontier for this as-built
scope; improvements in the backlog need a new owner-approved effort.

### Superseded Prospective Notes

The following paragraphs record the 2026-10-26 destination and are historical
only. In particular, complete activation and runtime enforcement are not
capabilities newly promised by the adopted read-only audit solution.

The owner accepted the completion and versioning recommendations on 2026-10-26
and requested agent-led repository evaluation in addition to static assessment.
This is a correction of the original assess-and-create goal, not a replacement
goal limited to instruction adapters. Preserve
Agent Harness Setup (historical source reference) and its seven
decisions as the historical baseline; do not rewrite or archive that folder
during this workflow.

Inherited policies remain in the original tickets' Resolution sections:
bounded inspection and provenance; selected clients and supported platforms;
exact proposal approval; preservation and revalidation; separately approved
checks; need-based integrations; and honest maintenance handoffs. Original
spec-run prohibitions are not exclusions of the capabilities being designed.
An original implementation limitation is not automatically a v0.2 requirement.

The accepted completion direction includes applicable guidance, preflight,
linting, formatting/type checks, meaningful tests, Git hooks, CI, security
boundaries and optional integrations. An assessment must expose missing,
unknown, deferred or inapplicable coverage. Approved creation must deliver the
reviewed changes and explicitly approved activation. Missing prerequisites,
declined activation and placeholder tests cannot establish full qualification.
The open tickets determine the precise contract; this paragraph is not an
approval to execute it against a project.

Static evidence, agent judgments and observed runtime behavior must remain
distinguishable. The new evaluation requirement does not authorize recursive
repository reads, execution, network access, installations, client sessions or
ingestion. The original root-only default remains until named scope expansion
is approved. No target repository is evaluated by charting this map.

Use the [local tracker](Tracker.md). Load `spec-workflow-orchestrator`,
`wayfinder`, `grilling` and `domain-modeling` for decisions; load each stage skill
before its work. Work serially in the main session. Charting resolves no child
tickets, and a later session resolves at most one HITL ticket with live owner
confirmation. Never substitute recommendations for the owner's answers.

## Decisions so far

- [Frozen Source And Historical Inputs](wayfinder-tickets/05-frozen-source-and-history.md#resolution): adopt the pinned skill without edits; treat the supplied research as historical snapshots.
- [As-Built Evaluation And Scoring](wayfinder-tickets/06-as-built-evaluation-and-scoring.md#resolution): reconstruct static, Git and quote-validated LLM findings, scoring and limitations from code.
- [Bootstrap Limits And Documentation Handoff](wayfinder-tickets/07-bootstrap-and-documentation-handoff.md#resolution): document proposal-first/create-only bootstrap and a documentation-only full chain; no live application or runtime proof.

## Not Yet Specified

No unresolved choices block documenting the frozen implementation. Known
behavioral limitations and future proposals stay in the source backlog and
[research findings](research/As-Built-Findings.md), not hidden as completed work.

## Out Of Scope

- Superseded prospective questions: [Dual Evaluation And Reconciled Coverage](wayfinder-tickets/01-dual-evaluation-and-reconciliation.md), [Approved Harness Creation And Activation](wayfinder-tickets/02-approved-creation-and-activation.md), [Enforcement Evidence And Qualification Verdicts](wayfinder-tickets/03-enforcement-and-qualification-evidence.md), and [Qualification Specification Readiness And Handoff](wayfinder-tickets/04-specification-readiness-and-handoff.md). The owner replaced their destination with as-built adoption on 2026-10-27; they were closed as superseded, not resolved in favor of their proposals.
- Implementing or deploying the skill during this specification workflow.
- Writing, activating hooks, running checks or making commits in a target repo.
- Unapproved nested/private-data inspection, secret reads or graph ingestion.
- Automatic tool installation, MCP connection, updates or scheduling.
- Requiring a universal stack, linter, CI provider, graph or integration bundle.
- Guaranteed correctness, security or savings based on an agent's confidence.

## Charting Done Contract

Superseded: the contract below records the earlier prospective charting run.
For this retrospective update, validate with the tracker command without
`charting=True`; all seven children are closed, four by scope supersession and
three with source-reconstructed task outcomes. Documentation checks do not prove
the frozen skill's runtime behavior.

- Objective: record the confirmed destination and the remaining decision frontier.
- Read first: the original map Destination and Notes, its seven Resolution
  sections, the owner exchange on 2026-10-26 and this folder's tracker.
- Constraints: write only the declared v0.2 planning paths; preserve the original
  baseline; no source-corpus changes, filesystem-root searches or live pilots.
- `validate:` run the tracker command in [Query And Validate](Tracker.md#query-and-validate),
  then `uv run --python 3.14 python scripts/verify.py --only docs`.
- Stop when: child identities, parentage, blocking and open/unclaimed states
  pass validation and the owner is shown the frontier and unresolved gates.
