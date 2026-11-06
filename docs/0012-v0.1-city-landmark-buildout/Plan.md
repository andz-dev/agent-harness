---
type: 'Plan'
id: '0012'
version: 'v0.1'
title: 'Default City Landmark Buildout'
status: 'active'
created: '2026-11-06'
updated: '2026-11-06'
generated: 'agent'
verified: 'unverified'
owner: 'Andreas Elser'
doc_scope: 'implementation'
---

# Default City Landmark Buildout

## Objective

The owner requested visible Airport, Factory, Shopping Mall, Highway with mountains
and tunnel, Bank and the separate Archive, then explicitly requested implementation.
The earlier [0011 coverage milestone](../0011-v0.1-harness-coverage-expansion/Implementation.md)
provided conditional evidence markers, not this physical buildout. Preserve that history.

## Contract

Use the existing [Grid and ISO design](../../apps/harness-city/DESIGN.md), geometry
helpers and selection path. The normal city shows the requested landmarks for every
input, including legacy synthetic data without coverage. Airport simulation remains
opt-in through `?airport`; its existing level controls replace the default terminal.
Bank represents secrets/credentials; Archive represents protected data, not the public
library. Generated models require no downloaded assets or new dependency.

Scenery remains independent of applicability, evidence, freshness, score and levels.
No new assurance taxonomy, secret values or runner command strings are introduced.
Coverage selections retain their own report-derived detail and foreground clearance.

Autonomous implementation choices, subject to owner review: show a stable physical
landmark rather than inventing report-derived L0-L3; defer Harbor, Court, traffic
simulation and Bank/Archive evidence mappings. These are scope decisions, not claims
that the owner explicitly prohibited those future features.

## Acceptance

- AC-1: Default legacy city contains nine named physical targets: Airport, Factory,
  Mall, Bank, Archive, Highway, Mountains, Tunnel and Bridge, with no simulation bar.
- AC-2: Real keyboard and pointer selection explain each domain; no score mutation
  or claim that visible geometry is audit evidence.
- AC-3: Default fit contains the map in all four orthographic rotations on desktop
  and mobile; screenshots and canvas pixels establish nonblank rendering.
- AC-4: Existing city/coverage/airport interactions and offline PNG exports remain
  functional. Export identifies scenery independently from prototype evaluation.
- AC-5: Adapted-runtime hash is refreshed; required repository checks are reported
  honestly, including unrelated blockers. No 0011 release milestone is closed here.

## Validation

Use existing Playwright city and export files with synthetic data and loopback/file
inputs only. No audited code runs. Run `task app:test`, `task app:check`,
`task tools:test`, `python3 tools/check.py --integrity-only` and `python3 tools/check.py`.
Record any blocked gate in [Implementation](Implementation.md).

## Boundaries

0011 M4.4 synthetic-origin wire semantics are unresolved and unchanged. This work
does not resolve M4.5/M4.6, WN-031 or owner-reviewed viewer acceptance.
