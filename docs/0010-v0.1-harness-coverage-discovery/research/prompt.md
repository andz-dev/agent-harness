---
type: 'Research'
title: 'Harness coverage discovery: verbatim owner prompts'
description: 'Original goal and discovery authorization, retained without rewriting the owner intent.'
status: 'active'
created: '2026-11-04'
updated: '2026-11-04'
generated: 'agent'
verified: 'unverified'
owner: 'Andreas Elser'
tags: [discovery, prompt]
sources: ['Owner messages in this session, 2026-11-04']
---

# Owner Prompts

## Original Goal

> My goal is to have an project harness audit skill, scanning a repository regarding rules, guardrails, security under the responsibility of the used technology and structure and then creates an audit-report to give an "city map" of the current project and its harness state.
> The harness is the most important part for today's Agentic AI workflow and the auditor as a first skill helps to gives teams an number and a map which can be then shown in the city to determine the quality.
> The important thing is that I want to go with that also in areas for an SBOM, Linter, Pipelines (local and possibly cloud) but also MCP servers, agent skills, VS Code extensions and so on.
> The `docs` directories provides a large history of what we already did, but the latest research topics to give way more harness options are not yet implemted or fully covered.
>
> Sample repositories can be set up in a `.repo` directory using the available skill to scan and then create an overall picture of what is needed to really have an implementation status we can go further.
>
> Also this repo can be used to "eat you own dog food".
>
> You are working autonously the next 2 hours, because I am away from the screen. Park questions and collect them if you cannot resolve them.

## Discovery Authorization

> Follow instructions in #prompt:SKILL.md with these arguments: let us bring this into scope. Use the existing **0010** directory for it, rename it to follow the pattern and then create the discovery poc. Work autonumously.

## Execution Authorization

> Start implementation

## Interpretation

"Implementation" here starts the requested discovery procedure, not the later product implementation.
The subject is a repository and its declared harness, not a machine inventory. Seven topic groups
are used: rules and infrastructure, lint, pipelines, SBOM, MCP, skills, and extensions. Security
is cross-cutting rather than an eighth weighted pillar. The decision is whether an evidence-first
coverage contract is worth taking into the specification workflow.

The realistic sample is the repository's own tracked source and configuration. The killing
assumption is that useful coverage cannot be expressed without executing subject code or claiming
that declarations and missing evidence prove enforcement. Questions are carried in the frozen card
with an owner and a recommendation, not left as unattended prompts.
