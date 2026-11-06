---
type: 'Ideation Book'
id: '0013'
version: 'v0.1'
title: 'Audit Scan Coverage, Categorized Report and Static Rule Catalog'
description: 'Goal, scope and feasibility record for the follow-on to 0011: finding categories, static scanner presence checks and a per-run rule catalog.'
doc_scope: 'proposal'
status: 'draft'
created: '2026-11-06'
updated: '2026-11-06'
stale_after: '2026-11-20'
generated: 'agent'
verified: 'unverified'
owner: 'Andreas Elser'
tags: [harness, ideation, report, catalog]
sources:
  - 'discovery/2026-11-06-static-scanner-coverage-and-categorized-report-feasibility/Ideation-Book.md'
  - 'research/2026-11-06-official-rule-references.md'
  - 'https://github.com/ossf/scorecard/blob/main/docs/checks.md'
---

# Audit Scan Coverage, Categorized Report and Static Rule Catalog

## Table Of Contents

- [Context](#context)
- [Initial Idea](#initial-idea)
- [Feasibility](#feasibility)
- [Decision Summary](#decision-summary)
- [Next Actions](#next-actions)
- [References](#references)

## Context

The 0011 audit run on a real repository gave a score and a failure list grouped by pillar. The owner wants to see
categories, the missing Security, SBOM, license and linter scans, richer data and sidecars, the backlog items in
the next version, and a static catalog that explains every rule with links to official practice. The city map stays
untouched.

## Initial Idea

Keep the frozen 0-100 score. Add an unscored category on every finding, an overview in `report.md`, scanner-presence
checks for Python, Node, Go and Rust, and a catalog written on every run that lists each rule with its limits and
verified public references. Reference links orient the reader; they do not claim conformance.

## Feasibility

The [discovery](discovery/2026-11-06-static-scanner-coverage-and-categorized-report-feasibility/Ideation-Book.md)
returned GO on real evidence: all 116 existing checks fit nine categories and match an oracle built from Scorecard
vocabulary ([1](#ref-1)). A [source list](research/2026-11-06-official-rule-references.md) gives verified official
references for every category. Limits: the oracle shares an author with the rules, Go and Rust detection is tested
on documented file names only, and no scanner is ever run.

## Decision Summary

The nine categories are final (owner, 2026-11-06). Scanner presence stays unscored (proposed, reasons in the
[Plan](Plan.md#why-scanner-presence-stays-out-of-the-score-d2)). WN-017 joins as its own slice. The catalog is static
and written on every run.

## Next Actions

1. Owner reviews the [Plan](Plan.md) decisions D2, D5 and D6.
2. Run the remaining spec stages: Architecture, Test Plan, Mocking Plan, Golden Dataset, Ontology, Implementation.
3. Implement test-first from the Plan's milestones.

## References

- <a id="ref-1"></a>[1] OpenSSF, "Scorecard checks", GitHub, retrieved 2026-11-06. https://github.com/ossf/scorecard/blob/main/docs/checks.md
