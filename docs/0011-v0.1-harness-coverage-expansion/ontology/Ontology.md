---
type: 'Ontology'
id: '0011'
version: 'v0.1'
title: 'Coverage Vocabulary And Constraints'
description: 'Human review of canonical concepts, aliases, independent state meanings and traceability.'
status: 'draft'
created: '2026-11-05'
updated: '2026-11-05'
generated: 'agent'
verified: 'unverified'
owner: 'Andreas Elser'
doc_scope: 'proposal'
sources: ['../Plan.md', '../Architecture.md', '../Test-Plan.md', '../Mocking-Plan.md', '../Golden-Dataset/dataset.json']
---

# Coverage Vocabulary And Constraints

## Canonical Package

[ontology.json](ontology.json) is the ID-addressable implementation vocabulary.
Its 19 concepts have stable URN mappings, source traces and attributes. The
contexts refer to Architecture's owning sections rather than defining topology
again. [Architecture](../Architecture.md) alone owns runtime boundaries,
responsibilities, wire contracts and logging disposition.

| Term | Canonical concept | Not equivalent to |
|---|---|---|
| Core score | `concept.core_score` | Coverage count or security assurance |
| Component | `concept.component` | Entire mixed repository's single stack |
| Applicability | `concept.applicability` | Evidence or L0-L3 maturity |
| Evidence state | `concept.evidence` | Independently verified execution |
| Freshness | `concept.freshness` | Trustworthiness |
| Safe provenance | `concept.provenance` | Raw source excerpt |
| Local receipt | `concept.receipt` | Authenticated issuer receipt |
| Collection outcome | `concept.collection` | Receipt outcome |
| Configured runner edge | `concept.runner_edge` | Successful invocation |
| Coverage topic | `concept.topic` | Eighth score pillar |
| City projection | `concept.projection` | Evidence-strength upgrade |
| Coverage city object | `concept.city_object` | New independent city layout |
| Synthetic origin | `concept.synthetic_origin` | Real repository observation |
| Golden recipe | `concept.fixture` | Passing implementation test |
| Release gate | `concept.release_gate` | Bounded prototype probe |

## Ambiguity Resolution

Use `present_unverified`, never bare "verified", for a well-formed local receipt.
`execution_observed` remains in the contract vocabulary but has no producer in
this scope. Changed identity marks freshness stale without destroying the
historical evidence label. Collection `partial` and receipt `partial` belong to
different entities; they cannot share a status field.

Infrastructure names an existing overlay area. The seven catalog topics remain
unscored and may reference that area's existing checks. Airport/factory/highway
are topic anchors within the owner-fixed Grid/ISO city. A planned reservation is
not a completed visual model. The assistant's standalone alternatives are
superseded, not aliases for the selected design.

`concept.implementation_type`, `concept.logging` and
`concept.decision_log_override` preserve the Architecture section 6 derivation.
Any override needs an explicit Implementation decision entry, not a silent edit.
Storage concepts follow the [policy reference](../Plan.md#storage-policy-reference).

## Traceability And Validation

The JSON maps all fourteen ACs to concepts, architecture sections, test scenarios
and dataset fields. Each concept/event has a source trace; relation endpoints
resolve. No Architecture data-model gap was found: the golden outcomes use the
separate enums already declared in Architecture section 7. A future mismatch
must return to Architecture before implementation.

OWL/RDF was not requested and is intentionally not generated. No formal reasoner
or remote vocabulary registry is needed. This package remains agent-generated
and unverified by the owner; validation of structure is not human sign-off.
