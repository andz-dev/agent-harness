---
type: 'Ontology'
id: '0002'
version: 'v0.2'
title: 'Harness Audit Vocabulary'
description: 'Source-traced vocabulary for the adopted audit; runtime boundaries remain owned by Architecture.md.'
status: 'draft'
created: '2026-10-27'
updated: '2026-10-27'
generated: 'agent'
verified: 'unverified'
owner: 'Andreas Elser'
tags: [ontology, vocabulary, harness-audit]
sources: ['../Plan.md section 1', '../Architecture.md section 9', '../Test-Plan.md', '../Mocking-Plan.md', '../Golden-Dataset/dataset.json']
---

<!-- markdownlint-disable-next-line MD025 -->
# Harness Audit Vocabulary

Machine consumers use [ontology.json](ontology.json), not this explanatory file.

| Concept | Meaning | Avoid |
| --- | --- | --- |
| Source snapshot | Frozen implementation identity selected by the owner | Treating docs v0.2 as tool version 0.2 |
| Component | A detected Python/Node audit unit with a kind | Assuming every manifest is a product component |
| Finding | One check result and its source/evidence | Treating missing evidence as pass |
| Agent task | A bounded judgment request with selected excerpts and facts | Whole-repository independent evaluation |
| Verified quote | Text occurrence matched against the target file | Verified semantic truth or runtime behavior |
| Pillar level | Static rule-derived classification | Runtime enforcement certificate |
| Entropy item | Evidence-backed stale/orphan/conflict candidate | Permission to delete |
| Triage step | A counterfactual score-gain/effort proposal | Business-priority decision or approval |
| Bootstrap proposal | Generated missing-file content plus skipped alternatives | Merge transaction or hook activation |
| Adoption completion | Documentation and preservation gates completed | Frozen skill's full behavioral validation |

Relations: tasks produce answers; quote validation supports findings; findings
contribute to pillars and triage; reports supply bootstrap proposals. Exact
system boundaries, persistence and status fields are referenced from
[Architecture sections 5, 9 and 10](../Architecture.md#5-ingress-egress-and-trust),
not redefined here. The catalog label Enforced is preserved but means static
classification in this model. No unresolved schema field was invented by the
ontology. OWL/Turtle was not requested and is intentionally absent.
