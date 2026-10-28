---
type: 'Maintenance Learning'
title: Self-audit fixtures and automated city gates
author: Andreas
date: 2026-10-28
branch: feat/harness-city-airport
touches:
  - ".github/workflows/check.yml"
  - README.md
  - Taskfile.yml
  - apps/harness-city/DESIGN.md
  - apps/harness-city/NOTICE.md
  - apps/harness-city/README.md
  - apps/harness-city/index.html
  - docs/0007/research/airport-assets.md
  - extraction-manifest.json
  - skills/harness-audit/SKILL.md
---

## Decided
The owner requested a reduced retrospective only: Map plus Ideation-Book, Plan, Architecture and Implementation in docs/0008-v0.1-harness-history-and-quality. Preserve older numbered docs and distinguish committed history from working-tree work; no grilling or invented historical pass records.

## Tried and ruled out
Self-audit initially reported 33/100 despite citing 12 test files. Python fixture strings containing TODO(human) triggered placeholder downgrades. AST/token-aware handling fixes the false cap while comments, docstrings and explicit NotImplementedError stubs remain blocked. Corrected compatible observations are 55 to 55, not a 22-point quality improvement.

## Watch out
task check now includes 251 skill tests, 13 root tooling tests and 18 real desktop/mobile Playwright tests. Software WebGL takes about 11 minutes; keep the measured 90-second case and 15-minute aggregate budgets, zero retries and no skips. task app:test owns a loopback server and builds a network-blocked offline fixture. tools/audit_history.py writes ignored immutable owner-only receipts and rejects engine/catalog/repository mismatches. Raw reports remain private; untracked files may be omitted by the Git-aware audit. Generated Trail notes need type frontmatter for this repository gate.
