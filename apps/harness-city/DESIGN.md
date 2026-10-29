---
type: 'Design'
title: 'Harness City Design'
status: 'active'
created: '2026-10-27'
updated: '2026-10-29'
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

## City map (grid)

Status: planned layout for the full level 3 city, agreed 2026-10-29 (second round the same day). The plan view is in the
Harness City L3 Plan artifact; this section is the source of truth. Units are grid cells,
x east, z south. Existing coordinates come from `DIST`, `ROADS`, `AP` and `BOUNDS` in `index.html`.

| Area | Cells (x, z) | State |
|---|---|---|
| City core, seven districts | x -4.5..33.5, z -4.5..19.5 (road grid at z 0, 8, 16) | exists |
| Rail and siding | z -1.75, -2.75, -3.75; x -10.5..35 (ends at the airport station) | exists, end moves |
| Airport, moved west | x 43..59, z 1..7 (was x 47..63) | exists, moves |
| Airport station, moved west | x 35..41 (was x 39..45) | exists, moves |
| Civic quarter: bank, court, archive | x -20..-7, z 1..15 | planned |
| Shopping Mall (was supermarket) | x 50..58, z 11..17, entry road from the highway at z 14 with the toll gantry | planned |
| Goods industry | x 48..62, z -18..-8, land road at z -6 to the highway | planned |
| Harbor quay | x 6..32, z 24..30, water from z 31 southward | planned |
| Highway | north-south, x 62.5..69.5, from the mountain tunnel (z -24) to the harbor bridge (z 40) | planned |
| Core connector | z 8 from the city east gate (x 33.5) to the highway | planned |
| Mountain range | z < -20 along the north edge, tunnel portal at x 62.5..69.5 | planned |

Decisions (2026-10-29):

* The camera stays as in "Camera": isometric, orthographic, with the rotate-left and
  rotate-right buttons. New objects must look right from all four rotations.
* The highway enters through a tunnel in a mountain range at the north edge and crosses the
  harbor water on a bridge on pillars. The rail no longer crosses it, because the airport and
  its station moved west.
* The city core connects to the highway through the core connector at z 8.
* Industry sits in the north with a land road to the highway. Goods trucks drive
  industry, highway, mall entry (toll gantry), Shopping Mall.
* The highway grows with the score tier. Neglected and Working: narrow, one lane each way.
  Prosperous and Thriving: the full grid width (three lanes each way at Thriving). The airport
  and harbor spurs appear from the Working tier.
* The Shopping Mall (renamed from supermarket) gets its own entry road from the highway.
* Trees, pylons and other scenery use exclusion zones for every planned rectangle above.
* The civic quarter connects through the central station: bus only on lower levels, bus and
  subway from level 2, like the airport.
* The power line runs west to east and feeds the harbor, the airport and the industry.
* Moving objects (cars, trucks, ships, planes, trains) may use the whole map in any direction,
  not only the x axis, with rounded corners, ramps and slow-downs on exits.
* Before building a new model, check the CC0 kits (see NOTICE.md and the research note in
  `docs/0009/`). New external assets need a NOTICE entry.

Open: the airport station (x 35..41) sits against the city edge (x 33.5); accept it as the gateway or move the airport two cells east.

## Editor

Status: first version, decisions from the owner on 2026-10-29. Research: `docs/0010/Research.md`.

* The editor is a separate page, `editor.html`. The viewer (`index.html`) stays alone and is not
  changed by the editor work.
* It edits one versioned map file (`city-map.json`, `schema: 1`). Export formats: the map JSON,
  a GLB of the scene, and a PNG image of the current view.
* Streets and tracks can be drawn guided (snapped to cells and 45 degree steps) or free (any
  angle, curves). Free is the default where it works.
* The editor may move the existing layout (districts, airport, station), not only add overlays.
* Asset palette: first the models the current map uses (the registry in `assets/assets.json`),
  then the other CC0 kits once they are imported with a NOTICE entry.
* Camera: the same orthographic isometric rig with 90 degree rotation buttons. A top-down plan
  view is allowed in the editor only; it is still orthographic.
* Placement is deterministic: scatter uses a seeded generator from the map seed, never
  `Math.random`.
* Districts keep their pillar key. Editing a district changes its place, size, label and goal
  text, never a level or score.
* Editor handles (junction spheres, curve diamonds, zone corners, brush rings) are tools, not
  city objects, so they need no registry row. Objects that the viewer will show still do.
* Map file content: terrain heightmap and water level, zones (districts keep the pillar key),
  road and rail graphs (nodes, edges with lanes, width, curve control point, bridge, tunnel,
  one-way), props (model id, place, rotation, scale) and paths (road or rail stops, or free
  points), plus the resolved points of every path for other tools.
* The viewer does not read `city-map.json` yet. Connecting it is a separate, reviewed change to
  the hash-pinned `index.html`.

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
