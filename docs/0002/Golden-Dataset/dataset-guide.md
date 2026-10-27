---
type: 'Dataset Guide'
id: '0002'
version: 'v0.2'
title: 'Harness Audit Contract Dataset'
description: 'Deterministic synthetic positive, edge and negative scenario records for the as-built documentation criteria.'
status: 'draft'
created: '2026-10-27'
updated: '2026-10-27'
generated: 'agent'
verified: 'unverified'
owner: 'Andreas Elser'
tags: [dataset, synthetic, traceability]
sources: ['../Plan.md section 1', '../Test-Plan.md', '../Mocking-Plan.md']
---

<!-- markdownlint-disable-next-line MD025 -->
# Harness Audit Contract Dataset

[dataset.json](dataset.json) contains 14 ordered, synthetic contract records,
one per criterion. Each carries `id`, `class`, `ac`, `scenario`, `input` and
`expected`. Classes are positive, negative and edge. Seed 39 is a stable label;
no random generator or private repository data was used.

These are minimal scenario descriptions, not complete executable repositories,
actual report objects or new tests. Expected results describe the intended
as-built contracts traced in Test-Plan.md; their presence does not prove a
behavioral suite passed. The existing skill tests supply executable fixtures.
Re-run or extend those only in a separately authorized effort, preserving the
frozen snapshot here. No CSV was requested or needed.

Source and storage boundaries reference [Architecture section 10](../Architecture.md#10-local-storage).
The join gate requires all AC-1 through AC-14 in Plan, Test Plan, this dataset
and ontology criterion references, with every scenario ID resolving.
