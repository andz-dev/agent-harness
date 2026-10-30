---
type: 'Reference'
title: 'Entropy catalog'
description: 'The seven entropy checks of harness-audit, their verdicts, penalty rule and how the city draws them.'
status: 'active'
created: '2026-10-30'
updated: '2026-10-30'
generated: 'agent'
verified: 'unverified'
owner: 'Andreas Elser'
tags: [harness-audit, entropy, reference]
---

<!-- markdownlint-disable-next-line MD025 -->
# Entropy catalog

Entropy looks for harness files that rot: scripts nobody calls, configs that fight each other,
workflows that point at files that no longer exist. Source of truth is the `entropy:` block of
`skills/harness-audit/checks/catalog.yaml`; this page is a reading copy. Entropy never deletes
anything. The tool reports evidence and a human decides.

## Verdicts

| Verdict | Meaning |
| --- | --- |
| active | Referenced, executed or imported, and current |
| stale | Still used, but outdated |
| orphaned | Nothing references it |
| conflicting | Contradicts another source of truth |
| unknown | A human needs to decide |

## Checks

| ID | What it flags | Detector | Evidence | Verdict | State | In the city |
| --- | --- | --- | --- | --- | --- | --- |
| ENR-01 | Scripts in `scripts/`, `tools/` and `bin/` that no runner, CI, hook or doc references | git_signal | path, last commit date, zero inbound references | orphaned | Script | Abandoned wagon on the rail siding |
| ENR-02 | Two configs for the same tool at the same scope | git_signal | both paths | conflicting | Script | Graffiti on the police district wall |
| ENR-03 | Docs describing removed commands, paths or features | llm (`prompts/instruction_drift.md`) | doc line and the missing target | stale | Needs a model; not evaluated without one | Not drawn |
| ENR-04 | CI jobs or workflows referencing missing files, branches or scripts | ci_runs | workflow line and missing path | stale | Script | Broken pylon on the power line |
| ENR-05 | Agent instruction files contradicting the README or runner targets | llm (`prompts/instruction_drift.md`) | conflicting line pairs | conflicting | Needs a model; not evaluated without one | Not drawn |
| ENR-06 | Dependencies declared in a manifest but never imported (tooling packages allowlisted) | git_signal | package name and manifest line | orphaned | Not implemented | Not drawn |
| ENR-07 | Config files for tools absent from manifests, runners, CI and hooks | git_signal | config path | orphaned | Script | Not drawn |

Dead-file checks need Git history, so a shallow clone limits them.

## Penalty

The entropy penalty reduces the score by at most 10 points:

    min(10, round(20 x flagged_units / max(20, candidate_files)))

Numbered file families count once. The catalog marks the formula "Provisional; tuned in P4 and
frozen before P5". `skills/harness-audit/references/WEIGHTS-FROZEN.md` freezes only the maximum
of 10, so a freeze of the formula itself is not recorded (open question).

## Related

* [City design](../apps/harness-city/DESIGN.md): entropy marks in the city
* [What's Next](Whats-Next.md): WN-004 (compact scan export lacks findings)
