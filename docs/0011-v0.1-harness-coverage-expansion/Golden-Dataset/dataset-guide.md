---
type: 'Golden Dataset'
id: '0011'
version: 'v0.1'
title: 'Coverage Golden Dataset Guide'
description: 'Synthetic deterministic recipes, independent expectations and scenario traceability.'
status: 'draft'
created: '2026-11-05'
updated: '2026-11-05'
generated: 'agent'
verified: 'unverified'
owner: 'Andreas Elser'
doc_scope: 'proposal'
sources: ['../Architecture.md', '../Test-Plan.md', '../Mocking-Plan.md']
---

# Coverage Golden Dataset Guide

## Purpose

[dataset.json](dataset.json) is a hand-authored deterministic oracle of synthetic
input recipes and expected behavior. It is not a report dump, runtime benchmark,
security certification, downloaded corpus or claim that future tests passed.
No real audited repository was copied into this bundle.

## Schema And Reproduction

`meta` records identity, version, synthetic provenance, timestamp and source
artifacts. `topics`, `applicability` and `evidence` pin catalog/enum vocabulary.
Each `cases[]` record requires unique `id`, `class` (`happy`, `edge`, `negative`),
nonempty `scenarios` and `acs`, `recipe` input and `expected` output assertions.
Expectations are partial predicates over the real output, not fake complete
reports. Consumers must assert every predicate, not just load the JSON.

Materialize one recipe at a time into a temporary tracked fixture tree. Fixed
file names, fixed UTC clock, sorted paths and actual SHA-256 of deterministic
fixture bytes produce repeatable source identities. For changed-digest cases,
alter one tracked fixture byte; do not mock the digest calculator. For race/symlink
cases use the real boundary with deterministic synchronization where possible.
The recipe descriptions are semantic fixture requirements; implementing their
small fixture builders is an unchecked future task, not hidden completed work.

`baseline` names the existing supported core fixture selected during M1 after
verifying it in the checkout. Compare exact independent expected core values
and baseline equality; never calculate the expected score using the new collector.
Synthetic flags apply even to recipe observations labelled declared/static.
The malformed execution claim is an adversarial **input**, not allowed output.

## Coverage And Assumptions

Two distinct Python samples (stdlib script, typed package) and two Node samples
(JavaScript package, TypeScript workspace) meet the Plan's initial sample minimum.
Mixed, infra-only and unsupported Rust cases limit overgeneralization. This is
not representative of all Python/Node tooling and introduces no Rust adapter.

Seven topic IDs are proposed catalog keys, not new score pillars. Infrastructure
is an existing overlay area, not an eighth scored topic; airport views relevant
security/dependency/CI-build observations through existing check references.
Every topic has a fixture recipe. Full seven-topic/every-state combinations are
generated from this pinned vocabulary during M3; representative explicit cases
here anchor the independent expected semantics for each state. Check IDs must
be resolved against the existing catalog during implementation, never invented.

All applicability values are represented. All evidence values are represented,
including `execution_observed` only as a must-reject producer claim. Six receipt
outcomes cover absent/present-unverified/invalid/stale/partial/failed; there is no
verified issuer outcome in this scope. All collection outcomes and failure paths
must be tested even when the recipe is not a full serialized report.

`CITY-GRID` pins the existing Grid/ISO viewer, not a standalone layout. Its expected
non-overlapping labels describe a production acceptance target; the temporary
prototype did **not** meet that production framing target. WN-031 remains open.

## Scenario Mapping And Validation

Every recipe carries its Test-Plan scenario IDs and Plan AC IDs. The validation
gate checks JSON syntax, unique IDs, required fields, all 14 AC joins, every
declared test scenario, all seven topic recipes and minimum adapter samples.
Negative controls cover path escape, secret emission, unknown promotion,
unsupported scoring, declaration-as-execution and report-to-city state loss.

No CSV is necessary for nested recipes. No executable tests are added in this
stage. Outputs/configuration tests follow the
[storage policy reference](../Plan.md#storage-policy-reference).

## Handoff

Ontology uses these field names and state meanings without redefining runtime
boundaries. Implementation materializes recipes and records red/green evidence
in the existing test suites. Any required new enum is an Architecture back-edge,
not an unrecorded dataset extension.
