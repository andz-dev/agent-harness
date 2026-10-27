---
type: "Wayfinder Ticket"
id: '0002'
version: "v0.2"
title: "Approved Harness Creation And Activation"
description: "Decide the approved change and activation surface needed to deliver a functioning harness while preserving existing tooling."
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
tags: ["wayfinder", "approval", "activation"]
sources:
  - "Owner acceptance of approved creation and activation direction, 2026-10-26"
  - "docs/skills/0036-v0.1-agent-harness-setup/wayfinder-tickets/03-proposal-approval-and-safe-application.md, Resolution"
---

<!-- markdownlint-disable-next-line MD025 -->
# Approved Harness Creation And Activation

## Resolution

Superseded on 2026-10-27.

The owner selected frozen as-built adoption, not this proposed activation
contract. Closed as a scope exclusion; no application authority is inferred.
See [the replacement map](../Map.md).

## Question

Which exact kinds of approved changes may v0.2 apply to turn a reviewed harness
proposal into working controls, and which operations remain separate or unsupported?

The owner has accepted creation/update and explicitly approved activation as the
completion direction. Decide the boundary for preserving and merging existing
configuration, executable permissions, repository-local hook activation, check
entry points and CI file changes. Do not infer permission for global Git
configuration, remote policy changes, tool installation or project execution.
Retain the original exact-proposal, source revalidation, preservation, separate
check approval and partial-failure/recovery policies.

Define the dry-run disclosure for file diffs and non-file effects, prerequisites,
unsupported operations, declined actions and an already-satisfied proposal. If a
framework or meaningful test suite is absent, decide how its setup is proposed
and what must remain blocked instead of writing a trivial test or an unknown
command and calling the harness complete.

Stress-test an existing hook manager, dirty configuration, changed authority
between review and apply, missing tools, a denied activation and partial failure.
Select the permission contract, not a mandatory hook manager or tool bundle.
