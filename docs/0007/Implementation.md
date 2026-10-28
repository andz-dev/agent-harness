---
type: 'Implementation'
id: '0007'
version: 'v0.1'
title: 'Airport Overlay: Recorded Implementation and Gaps'
description: 'Airport evolution from proposal to the current tested opt-in evaluation.'
status: 'active'
created: '2026-10-28'
updated: '2026-10-28'
generated: 'agent'
verified: 'unverified'
owner: 'Andreas Elser'
stale_after: '2026-11-11'
tags: [documentation, retrospective]
sources: ['git:3bfdf2b', 'git:f85a36d', 'git:38fab47', 'git:8deb536', 'git:90e9a52', 'docs/0008-v0.1-harness-history-and-quality/Implementation.md']
---

# Airport Overlay: Recorded Implementation and Gaps

## Recorded Evolution

- [x] `3bfdf2b`, `f85a36d`: asset proposal and station-link alternatives.
- [x] `38fab47`, `3f450d5`, `c2a342f`: separate prototype, mobile behavior and orthographic camera.
- [x] `8deb536`: evaluator moves inside the real city rather than remaining a separate toy page.
- [x] `90e9a52`: stable rebuilds, permanent underground, L2 metro, PNG export and non-blocking support facilities.
- [x] The same implementation commit includes automated desktop/mobile/offline browser tests.

The 0008 [implementation record](../0008-v0.1-harness-history-and-quality/Implementation.md)
owns the executed test evidence. This documentation pass does not claim a fresh runtime
run. The local generated simulator has no tracked originating commit at its docs path.

## Open Work

- [ ] Integrate actual report infrastructure into the city through an explicit reviewed data contract.
- [ ] Decide whether and when the evaluated airport becomes a default product view.
- [ ] Review remaining proposed assets against actual metaphor value before claiming them implemented.

## Verification Contract

Objective: preserve the current opt-in evaluation and truthful evidence boundary.
Read first: [Plan](Plan.md), [Architecture](Architecture.md), app DESIGN.md.
Constraints: no score changes, private datasets or manually edited generated bundles.
Validate: `task app:test` for runtime work and `python3 tools/check.py` for documentation.
Stop when: required checks pass and remaining prototype/data-integration limits are explicit.

The old harbor was reverted (`a620cd5`, `f2154c2`); its adapter is not counted as current work.