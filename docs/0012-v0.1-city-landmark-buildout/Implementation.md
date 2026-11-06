---
type: 'Implementation'
id: '0012'
version: 'v0.1'
title: 'City Landmark Buildout Implementation'
status: 'active'
created: '2026-11-06'
updated: '2026-11-06'
generated: 'agent'
verified: 'unverified'
owner: 'Andreas Elser'
doc_scope: 'implementation'
---

# City Landmark Buildout Implementation

## Resume State

Physical landmark geometry and selection are implemented. Focused default-city
and coverage-pointer checks pass in desktop and mobile Chromium. Export, full
regression, root checks and adapted-runtime baseline refresh are pending.
Resume date: 2026-11-06. Contract: [Plan](Plan.md).

## Tasks

- [x] B1: DESIGN-first scope and deterministic physical models at the agreed Grid
  footprints, with default Airport and separately opt-in evaluation. (AC-1)
- [x] B2: Named keyboard buttons and actual mesh raycast selection; scenery/evidence
  separation and score preservation. Coverage rings stay above foundations. (AC-2)
- [x] B3: Full-map fit, four-rotation desktop/mobile screenshots and nonblank canvas
  pixel check. Camera matrices update independently from background animation. (AC-3)
- [ ] B4: Export descriptions and existing browser regressions verified. (AC-4)
- [ ] B5: Manifest refresh, root checks, traceability and final gate report. (AC-5)

## Evidence And Decisions

2026-11-06: `task app:test -- city.spec.js --grep 'default city has'` initially
reported **2 failed**: expected default Airport count 1, received 0. After geometry
implementation and camera-matrix correction it reported **2 passed**. Strengthened
the same case with real pointer selections for all nine targets and canvas pixels;
final focused run reported **2 passed (2.3m)**, no skips. Screenshots are ignored
Playwright outputs, not committed datasets.

`task app:test -- city.spec.js` reported **14 passed, 2 failed** on ambiguous
Factory coverage-button locators. Exact accessible names exposed a real coplanar
foundation/ring overlap on desktop. Raised coverage rings from y .12 to .2;
`task app:test -- city.spec.js --grep 'real pointer targets'` then reported
**2 passed (51.7s)**. Assertions were retained, not skipped or weakened.

Source changes: [runtime](../../apps/harness-city/index.html),
[design](../../apps/harness-city/DESIGN.md),
[browser regression](../../apps/harness-city/tests/city.spec.js).
Legacy city data and seven scored districts remain unchanged. The default Airport
has no gate levels; prototype mode keeps its existing simulation logic.

The original [0011 resume state](../0011-v0.1-harness-coverage-expansion/Implementation.md)
remains blocked at M4.4; this follow-on does not invent a synthetic-origin field.
