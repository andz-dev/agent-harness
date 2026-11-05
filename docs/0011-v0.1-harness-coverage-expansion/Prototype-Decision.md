---
type: 'Prototype'
id: '0011'
version: 'v0.1'
title: 'Grid and ISO City Coverage Prototype Decision'
description: 'Synthetic evidence-presentation probe using the existing city and approved Grid.'
status: 'draft'
created: '2026-11-05'
updated: '2026-11-05'
generated: 'agent'
verified: 'unverified'
owner: 'Andreas Elser'
doc_scope: 'proposal'
sources: ['Plan.md', '../../apps/harness-city/DESIGN.md']
---

# Grid and ISO City Coverage Prototype Decision

## Question And Decision

Can separate applicability/evidence/freshness indicators be inspected without
changing the existing city score, layout vocabulary or isometric camera?

Owner decision, 2026-11-05: **use the defined Grid and the existing ISO city**.
This supersedes the assistant's standalone A/B/C alternatives and their proposed
selection gate. Those alternatives are not the baseline or acceptance evidence.
The probe supports additive evidence presentation; it is not production approval.

## Method

The ignored temporary harness embeds the real viewer through its existing
`?embed&airport` host interface. The source remains
[index.html](../../apps/harness-city/index.html); its builders, assets, district
colours, levels and orthographic camera are reused. It does not resume the
parked editor or edit production runtime files.

The harness adds selectable topic inspection and wire outlines for the
[Grid reservations](../../apps/harness-city/DESIGN.md#city-map-grid): airport
x 45..61/z 1..7; factory x 48..62/z -18..-8; highway x 62.5..69.5/z -30..40.
An outline is a planned reservation, not an implemented factory or highway.
Existing airport geometry/preset is not relabelled as measured evidence.

Three topics times seven presentation states exercise declared, static
implementation, unknown, simulated, stale, unsupported and inapplicable cases.
All data is explicitly synthetic and held in memory. Safe detail fields contain
only synthetic component/revision/path/digest/locator/method/time values.

## Observed Results

| Check | Result | Limits |
|---|---|---|
| JavaScript syntax and ignored output | Pass | Temporary harness only |
| 21 topic/state combinations | Pass; demo score stayed 100 | DOM-triggered selectors, not production pointer acceptance |
| Four 90-degree rotations | Pass; azimuth 45 to 405 degrees | Existing camera remains orthographic |
| Mobile, actual 390 x 844 | Nonblank canvas; 211 sampled colours; no horizontal overflow | Overview district labels crowd together |
| Desktop, actual 1440 x 1000 | Nonblank canvas; 1,025 sampled colours; no horizontal overflow | Overview district labels also crowd; not production framing |
| Existing city and assets | Present in screenshots | No new factory/highway production models tested |

Browser captures and HTML are disposable, ignored `dist/` outputs; their absence
in a fresh clone is expected. Use the existing viewer as the reproducible source
baseline, not a generated HTML bundle. Preview during this session:
`http://127.0.0.1:8011/dist/0011-grid-iso-prototype.html`.

## Carry-Forward Constraints

Use the defined Grid and existing ISO camera/scene builders. Keep the existing
selection/explanation pattern; unsupported and inapplicable topics remain
discoverable without inventing city maturity. Applicability, evidence,
freshness, receipt trust and simulation are separate display attributes.
Coverage cannot change core score or L0-L3 levels.

Production work must provide focus/zoom and label decluttering within the
existing visual design, keyboard-accessible topic inventory, mobile selection,
real raycast/pointer tests, all four orientations, and export-state preservation.
The overview screenshot does not establish those capabilities. WN-031's full
browser gate remains open; this bounded probe does not replace it.

## Handoff

Inputs: Plan AC-9/10/11/13 and app DESIGN Grid/Camera. Outputs: this decision and
the prototype sidecar. Architecture may proceed using the owner-fixed baseline.
Production implementation and owner review of this document remain unstarted.
