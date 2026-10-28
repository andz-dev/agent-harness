---
type: 'Implementation'
id: '0005'
version: 'v0.1'
title: 'Infrastructure Overlay: Recorded Tracks'
description: 'Commit-backed overlay work, reverted city experiment and explicitly open proposals.'
status: 'active'
created: '2026-10-28'
updated: '2026-10-28'
generated: 'agent'
verified: 'unverified'
owner: 'Andreas Elser'
stale_after: '2026-11-11'
tags: [documentation, retrospective]
sources: ['git:20b21f2', 'git:21d8ef0', 'git:0aaec6f', 'git:8b19edc', 'git:12c28e8', 'docs/0005/research/Infrastructure-Coverage-Map.md']
---

# Infrastructure Overlay: Recorded Tracks

## Implemented Source Trail

- [x] `20b21f2`: infrastructure detection overlay.
- [x] `21d8ef0`: initial Dockerfile/Compose/Devcontainer/Terraform checks.
- [x] `0aaec6f`, `8b19edc`: separate report roll-up and infrastructure levels.
- [x] `83d6a88`, `44da439`: broader Bicep/Kubernetes/Ansible/CloudFormation/Pulumi coverage.
- [x] `12c28e8`, `6490917`: infrastructure judgments and later level/entropy work.
- [x] `2146078`: recorded aggregation/gate calibration changes, documented in 0006.

These are source/commit matches, not a new replay of every tool or calibration fixture.
The `a620cd5` harbor adapter was reverted in `f2154c2`; do not count it as current code.

## Not Established as Complete

- [ ] Generalized separate adoption/merge workflow from Track F.
- [ ] The proposed multi-rater infrastructure calibration.
- [ ] Every coverage-map check idea or full production airport report-data integration.

## Verification Contract

Objective: reconcile track state against actual source history.
Read first: [Plan](Plan.md), [Architecture](Architecture.md), original coverage map.
Constraints: preserve the historical map; no audited code execution or new private data.
Validate: `git show --stat f2154c2` and `python3 tools/check.py`.
Stop when: implemented, reverted and proposed work are explicitly separated.