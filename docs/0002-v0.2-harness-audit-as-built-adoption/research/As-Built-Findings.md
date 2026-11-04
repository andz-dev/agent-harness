---
type: 'Research'
id: '0002'
version: 'v0.2'
title: 'Harness Audit As-Built Evidence'
description: 'Source pin, historical-input reconciliation and known limitations for documentation of the frozen harness-audit skill.'
status: 'active'
created: '2026-10-27'
updated: '2026-10-27'
generated: 'agent'
verified: 'unverified'
owner: 'Andreas Elser'
tags: [research, provenance, harness-audit]
---

<!-- markdownlint-disable-next-line MD025 -->
# Harness Audit As-Built Evidence

## Source Pin

Commit: `766dd40add66b2806bab5c8d0926d3b5d13056a7`.
Skill tree: `e5c34a57bd87454c2857bb9f907aea24805b11d8`.
The owner selected [this existing implementation](../../../skills/harness-audit/SKILL.md)
without changes. No remote fetch or replacement checkout was necessary.

## Historical Inputs

| Input | Observation | Treatment |
| --- | --- | --- |
| Research catalog | SHA-256 `d0384a2915c031a363a4026ba1cb67922c26921efffab088f19732637eb38a3a` | Historical draft; preserve bytes |
| Active catalog | SHA-256 `8c0dc5beefb6fb0b94ce3c6ed0184926439c8e165617e34c8c801c99f87cadec` | Current check authority |
| Research backlog | Earlier P0 history, including provisional weights and deferred features | Not a current completion ledger |
| Skill backlog | Adds implementation fixes, calibration, limitations and later sessions | Source-reported history, not newly reproduced measurements |

The live catalog contains 56 top-level `- id:` entries, counted by anchored
source-line matching. The eight test modules contain 137 `def test_` declarations,
counted from source. Neither number is a pytest collection or execution result.

## Behavior And Evidence

| Concern | Controlling source | As-built result |
| --- | --- | --- |
| Scope | `detect_stack.detect` | Python/Node components; unsupported/sample/tooling handling |
| Static checks | `run_checks.run`, active catalog | Paths, parsed config, runner/CI/hook heuristics; no target execution |
| Git checks | `git_signals.run` | Local metadata and entropy; shallow history limits |
| Agent tasks | `llm_layer.plan` | Selected excerpts/facts; no model client in the script |
| Agent answers | `llm_layer.apply_answers` | Quote verification; invalid/missing evidence becomes unknown |
| Reconciliation | `audit.assemble` | Replace matching check IDs with specialized findings before scoring |
| Score | `score.build` | Weighted levels, hard caps, entropy and arithmetic checks |
| Remediation | `triage.plan` | Counterfactual score-gain/effort ordering, not business priority |
| Bootstrap | `bootstrap.propose`, `bootstrap.write` | Output proposals; explicit create-only apply; no merge/activation proof |

## Limits Carried Forward

The code's L2 label is named Enforced, but the audit observes configuration,
not execution. A successful score is not a security certification or proof a
commit would be rejected. Quote verification authenticates text occurrence,
not the truth or meaning of a model conclusion. Per-check agent answers are
repository-wide. Excerpt truncation, component weighting, indirect runner/CI
attribution and missing dependency-usage analysis remain documented rough edges.

Current score rules supersede historical provisional formulas: seven weights
sum to 100; pass ratio is 0.6; hard caps are 40/60/70; entropy is bounded at 10;
orientation and entry-point levels are capped at verification plus one.
No calibration score, model agreement rate or runtime behavior was re-measured.

## Retirement Boundary

0036 is stopped. Its 21 tracked implementation files are removed from the
active skill tree; historical code remains in Git. Installed copies are not
silently deleted. The tracked retirement template records the flat skill name.
The replacement skill, research catalog and unrelated Harness City data are
outside this run's write scope.
