---
type: 'Maintenance Learning'
title: Airport rebuild ownership and permanent underground
author: Andreas
date: 2026-10-28
branch: feat/harness-city-airport
touches:
  - apps/harness-city/DESIGN.md
  - apps/harness-city/NOTICE.md
  - apps/harness-city/README.md
  - apps/harness-city/index.html
  - docs/0007/research/airport-assets.md
  - extraction-manifest.json
  - apps/harness-city/tools/check_city.js
  - docs/0007/city-airport-prototype.html
---

## Decided
The main airport uses the weakest applicable core area: Terraform, Compose or Dockerfile. The owner revised the original weakest-tool rule: Devcontainer is a non-blocking developer side-terminal and Agent guidance a non-blocking guidance office. Each grows independently at L0-L3; a dash removes it. Cross-cutting remains independent. Support-only configurations show facilities without a main airport or airport service. L0 core has no service, L1 keeps a hangar and passenger office with buses, L2+ adds metro using the weaker station/destination endpoint. Underground is a permanent city view independent of AIR variants.

## Tried and ruled out
Compose changes produced no exceptions or invalid transforms. Lower tool levels intentionally removed the old L2 terminal. Repeated rebuilds did leak GPU geometry: 342 to 718 after eight toggles; releasing scene-owned resources stabilized allocation at each level.

## Watch out
Restore airDim material baselines BEFORE removing/rebuilding the city; merely clearing its map loses shared material originals. Never dispose cached MAT/GEO/TEX or kit assets. Render the panel AFTER build to avoid stale airport descriptions. Regenerate docs/0007/city-airport-prototype.html from app source; it is not an independent implementation. Browser checks live in apps/harness-city/tools/check_city.js. Shared-browser PNG downloads can succeed natively without a Playwright download event; inspect the PNG blob or downloaded file.

## Follow-up: every area needs visible feedback
The owner reported Devcontainer breaking the airport and Agent guidance/Cross-cutting having no effect. The capacity-limited list hid applicable areas, including the tool lowering the overall level. Separate fixed aircraft capacity (0/2/4/6 stands) from fixed-position forecourt status pylons for every applicable area at all levels. Repo-wide areas change their own pylon height, bands and colour, not the overall level. Name the limiting tools in the control bar. Browser regressions must cover all six area controls, not only Terraform and Compose, and verify terminal width stays unchanged at a fixed overall level.

## Owner revision: support facilities are benefits
The previous Devcontainer-blocking behavior is superseded. Only explicitly marked core areas enter the visualization minimum; do not infer core status from whether an area is repo-wide. Devcontainer and Agent guidance must have independent, clickable facilities and cannot change core size, stands or transport. Keep audit scoring untouched. No applicable core means no main airport, even with a Devcontainer; render the applicable benefits separately.
