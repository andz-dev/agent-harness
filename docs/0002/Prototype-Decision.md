---
type: 'Prototype Decision'
id: '0002'
version: 'v0.2'
title: 'As-Built Contract Walkthrough'
description: 'Mandatory prototype-stage record using a throwaway source-contract probe, with runtime and human acceptance explicitly unclaimed.'
status: 'draft'
created: '2026-10-27'
updated: '2026-10-27'
generated: 'agent'
verified: 'unverified'
owner: 'Andreas Elser'
tags: [prototype, source-contract, limits]
sources: ['Plan.md', 'research/As-Built-Findings.md']
---

<!-- markdownlint-disable-next-line MD025 -->
# As-Built Contract Walkthrough

## Question And Artifact

Does the reconstructed contract match the source being adopted, or silently
restore the old setup/activation design? The owner requested reverse engineering,
not a new UI or production implementation. The declared throwaway artifact is
[contract-probe.sh](prototype/contract-probe.sh); it only inspects source text
and Git differences. It neither imports nor executes the adopted Python code.

Run from the repo root:

```bash
bash docs/0002/prototype/contract-probe.sh
```

## Walkthrough And Carry-Forward

| Case | Source observation | Documentation decision |
| --- | --- | --- |
| Old skill resumes | Entry point must be absent | Stop 0036; do not use its resume state |
| Replacement changes | Pinned Git diff must be empty | Freeze code, versions, weights and tests |
| Agent answer lacks valid quotes | apply_answers demotes it to unknown | No semantic truth inferred from confidence |
| Bootstrap is proposed | Default path writes only output proposals | No target-write claim without explicit --apply |
| Target file already exists | write skips it | No merge/activation protocol promised |
| Catalog differs from history | Two distinct pinned hashes | Live rules win; snapshot remains history |

This walkthrough supports source-contract consistency only. It does not
exercise all branches, isolated commit rejection, client loading, model answers
or the frozen skill's test suite. No live owner reaction to a new interactive
prototype is invented. Design-prototype acceptance therefore remains limited;
the requested full chain proceeds as an as-built record with this warning,
not as a newly behavior-verified implementation design.

The earlier 0036 discovery spike and prototype concern the retired implementation
and are not substituted as evidence for this one. No Plan rule needs amendment:
the Plan already separates audit classification from runtime qualification.
