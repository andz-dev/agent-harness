---
type: 'Project Guide'
title: 'Harness City Rules'
status: 'active'
created: '2026-10-27'
updated: '2026-10-27'
generated: 'agent'
verified: 'unverified'
owner: 'Andreas Elser'
---

<!-- markdownlint-disable-next-line MD025 -->
# Harness City Rules

Read [DESIGN.md](DESIGN.md) before any change to the city, including small ones.

* Follow the design principles. If a change needs a new principle, change DESIGN.md first
  and say so in the commit.
* New or changed visual objects: update the asset registry, the click explanation and the
  level ladder in the same change.
* The city never changes the score. Overlays stay outside the districts.
* Camera is pinned: isometric, orthographic, with the rotate-left and rotate-right buttons. No
  perspective camera, and every new object must look right from all four rotations.
  `tools/check.py` fails if this changes.
* No `Math.random` in scene building (layout, placement, routes); use `hash` and `rng` seeded by the repo id.
* New 3D models only generated in code, or from a CC0 kit with a `NOTICE.md` entry.
* Demo data stays synthetic and covers every level (`python3 tools/make_demo.py`, then
  `--check`).
* `index.html` is an adapted runtime file: after editing it, run the manifest rehash and
  `python3 tools/check.py` from the repo root, then look at a screenshot of each demo tier.
* Open design questions go to `docs/0007/` or the next free docs folder, not into code comments.
