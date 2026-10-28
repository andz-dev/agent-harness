---
type: 'Design'
title: 'Harness City Design'
status: 'active'
created: '2026-10-27'
updated: '2026-10-28'
generated: 'agent'
verified: 'unverified'
owner: 'Andreas Elser'
---

<!-- markdownlint-disable-next-line MD025 -->
# Harness City Design

The single source of truth for what the city shows and how. Every change to the city
starts here (see [AGENTS.md](AGENTS.md)). If code and this file disagree, fix one of them
in the same change.

## Purpose

A repository is a city. The city makes an audit result readable at a glance, and every
visible object explains itself when clicked. It is a view of the audit, never a second
scoring system.

## Principles

1. **Metaphor is data.** Each object stands for one audit fact. No decoration without
   meaning, except trees and ground.
2. **Level grows the thing.** Every area has levels L0 to L3: vacant fenced lot, small,
   working, agent-native. The same ladder applies everywhere (buildings, roads, transit,
   rail, airport).
3. **Reach shows as traffic.** Roads, buses, metro and trains show how well work reaches
   an area. A link is only as good as both ends (lower of the two levels).
4. **Next fix shows as construction.** Cranes and construction sites mark the next planned
   fix. **Decay shows entropy.** Wagons, graffiti, broken pylons.
5. **Overlays are not scored.** The 0-100 score comes from the seven pillars only. The
   infrastructure overlay has its own L0-L3 and is drawn outside the districts.
6. **Everything is explained.** Each clickable object has a side-panel text: question,
   what it stands for, what each level looks like (`levelList`). Add the text with the object.
7. **Deterministic.** Layout and randomness come from the repo id (`hash`, `rng`). The same
   data always draws the same city. No `Math.random` in scene building; cosmetic flicker in the animation loop is allowed.
8. **Honest.** Limits of the scan are listed (`lim`). Unknown is not drawn as good.

## Structure

| Pillar | Weight | Place | Colour |
|---|---|---|---|
| Verification | 25 | Hospital and test labs | `#d64545` |
| Orientation | 20 | City hall and visitor info | `#2f86c9` |
| Static guardrails | 15 | Police headquarters | `#33489c` |
| Workflow entry points | 15 | Central station and rail (transit hub) | `#24946a` |
| Automatic triggers | 10 | Fire and alarm station | `#e0672b` |
| Pipeline parity | 10 | Power plant and grid | `#d9a42a` |
| Doc hygiene | 5 | Public library | `#8a5bb5` |

Score = sum of level / 3 x weight, minus entropy penalty. Tiers: Thriving 80+,
Prosperous 60+, Working 45+, Neglected below. Pillar colours are fixed; do not reuse them
for other meanings. The pillar list lives in `PILLARS` in `index.html` and must match this table.

## Transit

The central station is visible in every city, including a closed station at L0.
Line level = lower of station level and district level: none (L0), one bus (L1),
underground metro plus buses with shelters (L2), frequent metro plus buses (L3).
New destinations (for example the airport) join this network and follow the same rule.

Surface and underground are permanent city views, independent of the airport prototype.
The underground view fades surface buildings and exposes the metro routes; it never
invents service below L2. View choice survives city and prototype option changes.
Restore original material properties before rebuilding or leaving the underground view.
Airport labels sit outside the buildings. Crowding hides secondary airport tags instead
of overlapping labels; all gate details remain available in the side panel.

PNG export captures the current camera, layer and visible labels, together with the city
summary, score, pillar legend, infrastructure levels and the selected object's description.
Descriptions wrap without clipping. Synthetic data and prototype overrides remain explicit
in the exported image. Export never changes the live camera or audit data.

## Infrastructure overlay (airport)

Status: **prototype** inside the real city, enabled with `?airport` (or the standalone build
`build_standalone.py --airport`). Not part of the default city yet. Details and open variants:
[../../docs/0007/airport-assets.md](../../docs/0007/research/airport-assets.md).

* The airport is the infrastructure overlay in teal `#0a9cb8`. It is never part of the 0-100 score
  and never replaces a district.
* It sits east of the districts, outside the city, on the same rail line and on the road row
  `z=8`. The station plot (airport station) and the airport plot together take about two
  district fields. A cross street joins them like the district blocks.
* Size follows the weakest applicable core area: Terraform, Compose and Dockerfile only.
  Devcontainer is an optional developer side-terminal; Agent guidance is a guidance office.
  Their own L0-L3 grows the supporting facility, but never lowers or closes the main airport.
  L0 means a closed supporting facility; not applicable means the facility is absent.
  Cross-cutting remains independent and non-blocking. With support areas only, show those
  facilities without a main airport, runway or main-airport transport service. This is a
  visualization rule only; audit results and the city score remain unchanged.
* Each infra area is a gate; a closed
  gate (L0) has a barrier. Repo-wide areas get gates too. Every applicable area has its own
  fixed-position forecourt status pylon at every airport level, including L0. Pylon height,
  lit bands and colour show that area's own level. Devcontainer, Agent guidance and
  Cross-cutting do not change the overall level. The control bar names the limiting core area(s).
  Aircraft stands are separate: capacity is 0 / 2 / 4 / 6 for L0 / L1 / L2 / L3. Adding an
  area never removes another area's display or changes the footprint at a fixed overall level.
* L0 fenced airstrip, L1 small airfield with a visible hangar and passenger building,
  L2 regional (terminal, tower, 4 stands), L3 hub (6 stands,
  canopy, tall tower, charters, crane). Repos without real infrastructure get no airport.
* The forecourt street follows the district street ladder (closed, one lane, two lanes,
  boulevard) at the airport level.
* Docker and Compose are air freight: containers on the cargo apron, capped by level (4, 8, 12).
* The link to the central station is only as good as both ends (lower of station level and
  airport level), the same rule as every district line: bus at L1+, metro at L2+, and in variant C an
  express train on its own rail platforms.

## Assets

* Kit models (Kenney, Quaternius, CC0) live in `assets/` and are loaded with `put` and
  `instanced`. Credits stay in `NOTICE.md`.
* Anything not in a kit (trains, planes, cranes, signs) is generated in code with the
  helpers `box`, `cyl`, `barrier`, `cone`, `textSprite`, `groundPlane`. No new binary
  assets or fonts without a `NOTICE.md` entry and a licence.
* Every generated asset has one builder function and is listed in the registry below.

### Asset registry

| Asset | Builder | Stands for |
|---|---|---|
| train, train car | `trainCar`, `buildRail` | workflow entry points |
| bus, bus stop | `busModel`, `busStop` | transit line L1-L2 |
| metro train, M sign | `ghostTrain`, `metroSign` | transit line L2+; permanent underground view |
| airport plot, runway, taxiway | `buildAirportAll`, kit `road-straight` and `pavement` | infrastructure overlay |
| airplane (prop, jet, business, charter, cargo) | `airPlane`, `airFlight` | infra traffic by level |
| terminal, tower, jet bridge, hangar, small passenger building | `buildAirportAll` | infra level L2+ / L1+ |
| forecourt area-status pylons, bands and barriers | `buildAirportAll` | each applicable tool or repo-wide area's own L0-L3 |
| developer side-terminal, guidance office | `buildAirportSupport` | independent Devcontainer / Agent guidance benefits; never blockers |
| airport station, express platforms | `buildAirportAll` | station link |
| containers, crane | `buildAirportAll` | Docker and Compose |

Add a row when you add an asset.

## Camera

Isometric: orthographic camera, azimuth 45 degrees, fixed elevation (height 0.82 x distance), drag pans, wheel or pinch zooms, rotation in 90 degree steps. Prototypes and new views must use the same camera, not a perspective one.

## Animation

Moving objects use the `shuttle` model (route, speed, dwell, phase) or the rail loop.
Speed and count rise with level; L0 means no traffic. Animation depends on time only, not
on frame rate, and must stop when the tab is hidden.

## Data contract

The page reads `data/cities.json` (format in [README.md](README.md)). New visual features
need data fields that are optional, so old files still render. Demo data is synthetic
(`tools/make_demo.py`) and covers every level of every new feature.

## Change checklist

Automated browser verification uses the trusted synthetic city only. The runner owns a
loopback server and exercises desktop/mobile layouts, actual controls, layer and rebuild
state, downloadable PNGs and offline packaging. Page/console errors and missing browser
prerequisites fail the run. Failure screenshots and traces stay ignored; reference images
are never automatically replaced to make a test pass. These tests execute this application,
not repositories examined by the read-only auditor.

1. Update this file (principle, table or registry).
2. Add the click explanation and level ladder text.
3. Add optional data fields to the converter and README.
4. Extend the synthetic demo so every level shows.
5. `task check`, then look at a screenshot of each demo tier.
