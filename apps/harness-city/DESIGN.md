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
| Rail and siding | z -1.75, -2.75, -3.75; x -10.5..37 (ends at the airport station) | exists, end moves |
| Airport, moved west | x 45..61, z 1..7 (was x 47..63); 1.5 cells from the highway | exists, moves |
| Airport station, moved west | x 37..43 (was x 39..45); 3.5 cells from the city edge (x 33.5) | exists, moves |
| Civic quarter: bank, court, archive | x -20..-7, z 1..15 | planned |
| Shopping Mall (was supermarket) | x 50..58, z 11..17, entry road from the highway at z 14 with the toll gantry | planned |
| Goods industry | x 48..62, z -18..-8, land road at z -6 to the highway | planned |
| Harbor quay | x 6..32, z 24..30, water from z 31 southward | planned |
| Highway | north-south, x 62.5..69.5; tunnel z -30..-22 under the mountains, open road from the portal (z -22) to the harbor bridge (z 31..40) | planned |
| Core connector | z 8 from the city east gate (x 33.5) to the highway | planned |
| Mountain range | z -30..-20 along the whole north edge (x -24..78); the foot line wavers between z -20 and z -24 | planned |
| Tunnel portal | x 61.5..70.5 (frame 1 cell wider than the road), z -22; the mountain foot is cut flat here, so the road comes out of the rock face | planned |

Grid map, stored here so the layout survives without the plan artifact. One character is
2 x 2 cells; x runs from -24 to 78 and z from -30 to 42. It is drawn from the table above;
roads narrower than 2 cells (industry road, mall entry, civic streets) are not shown.

```text
       x-20      x0        x20       x40       x60
       |         |         |         |         |
z-30 ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^TTTT^^^^
     ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^TTTT^^^^
     ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^TTTT^^^^
     ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^TTTT^^^^
     ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^####^^^^
z-20 ...........................................####....
     ....................................IIIIIII####....
     ....................................IIIIIII####....
     ....................................IIIIIII####....
     ....................................IIIIIII####....
z-10 ....................................IIIIIII####....
     ...........................................####....
     ...........................................####....
     .......rrrrrrrrrrrrrrrrrrrrrrrrrrr.........####....
     ..........ccccccccccccccccccc..............####....
z0   ..BBBJJJJ.ccccccccccccccccccc.....PPPPPPPPP####....
     ..BBBJJJJ.ccccccccccccccccccc.ssssPPPPPPPPP####....
     ..BBBJJJJ.ccccccccccccccccccc.ssssPPPPPPPPP####....
     ..........ccccccccccccccccccc.....PPPPPPPPP####....
     ..AAAAA...ccccccccccccccccccc==============####....
z10  ..AAAAA...ccccccccccccccccccc........MMMM..####....
     ..AAAAA...ccccccccccccccccccc........MMMM..####....
     ..AAAAA...ccccccccccccccccccc........MMMM..####....
     ..........ccccccccccccccccccc........MMMM..####....
     ..........ccccccccccccccccccc..............####....
z20  ...........................................####....
     ...........................................####....
     ...............HHHHHHHHHHHHH...............####....
     ...............HHHHHHHHHHHHH...............####....
     ...............HHHHHHHHHHHHH...............####....
z30  ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~bbbb~~~~
     ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~bbbb~~~~
     ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~bbbb~~~~
     ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~bbbb~~~~
     ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~bbbb~~~~
z40  ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~bbbb~~~~
```

Legend: `^` mountains, `T` tunnel under the mountain, `#` open highway, `b` highway bridge on
pillars, `~` harbor water, `c` city core, `r` rail line, `s` airport station, `P` airport,
`=` roads (core connector z 8, industry land road z -6, mall entry z 14), `I` goods industry,
`M` Shopping Mall, `H` harbor quay, `B` bank, `J` court, `A` city archive. The tunnel portal is
where `T` meets `#` (z -22). Update this block with the table whenever a cell changes.

Decisions (2026-10-29):

* The camera stays as in "Camera": isometric, orthographic, with the rotate-left and
  rotate-right buttons. New objects must look right from all four rotations.
* The highway enters through a tunnel in a mountain range at the north edge and crosses the
  harbor water on a bridge on pillars. The tunnel runs z -30..-22 hidden under the mountain;
  the portal (stone frame, dark opening, lamps) sits at z -22 and is the first thing the road
  shows. From the portal the road is open. The tunnel is as wide as the highway at that tier
  and the portal stays the same size at every level. Cars and trucks drive in and out of the
  portal. The portal must look right from all four rotations, because the mountain hides the
  road behind it. Industry (z -18..-8) keeps 4 cells to the portal. The rail no longer crosses it, because the airport and
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

Decided 2026-10-30: the airport moves two cells east of the first proposal (airport x 45..61, station x 37..43), so the station is a gateway 3.5 cells outside the city edge and not against it. The exact position of the central station is still approximate.

## Editor

Status: second version, decisions from the owner on 2026-10-29. Parked on 2026-10-30: the code stays in the repo, no further editor work until the owner resumes it. Research: `docs/0010/Research.md`.
Usage: [EDITOR.md](EDITOR.md).

* The editor is a separate page, `editor.html`. It shows the viewer itself: `index.html?embed`
  runs in a frame and draws the city with the viewer's own builders, assets and level ladder.
  The editor only changes the layout and adds its own layers on top. The viewer page stays
  alone and unchanged without `?embed`.
* Layout as data: the viewer reads its layout from one `LAYOUT` object (districts `DIST`, road
  cells `ROADS`, rail tracks and siding, power line, bus link columns, meadow trees and ground,
  airport offset). Its defaults are the built-in city, so the default viewer draws exactly the
  same scene (checked with a scene fingerprint of every demo city, with and without airport).
  `applyLayout` and `window.__city` are the host interface for the editor.
* The station hub is the street in front of the station district; bus routes follow the
  district's front street. Moving districts keeps transit attached to them.
* Viewer-drawn in the editor: districts, guided streets (road cells, kit tiles), main rail line,
  power line, airport. Editor layers: terrain and water, free streets and highways, extra tracks,
  other zones (mall, industry, harbor, bank, court, archive), placed models, vehicle paths.
* Terrain brushes do not change cells under districts, road cells or the airport, because the
  viewer draws those flat.
* It edits one versioned map file (`city-map.json`, `schema: 2`; schema 1 files are migrated).
  Export formats: the map JSON, a GLB of the scene and a PNG image of the current view.
* Streets and tracks can be drawn guided (road cells, the viewer's tiles) or free (any angle,
  curves). Free is the default where it works.
* The editor may move the existing layout (districts, airport), not only add overlays.
* Asset palette: first the models the current map uses (the viewer's registry), then the
  other CC0 kits once they are imported with a NOTICE entry.
* Camera: the same orthographic isometric rig with 90 degree rotation. A top-down plan view
  is allowed in the editor only; it is still orthographic.
* Placement is deterministic: scatter uses a seeded generator from the map seed, never
  `Math.random`.
* Districts keep their pillar key. Editing a district changes its place, size, label and goal
  text, never a level or score. The editor shows a synthetic demo city's levels.
* Editor handles (junction spheres, curve diamonds, zone corners, brush rings) are tools, not
  city objects, so they need no registry row. Objects that the viewer will show still do.
* Known limit: the airport express platform on the main rail line does not move with the
  airport yet.
* The default viewer does not read `city-map.json` yet; only the editor applies it.

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
| wagon (abandoned) | `wagon` | ENR-01 orphaned script, on the rail siding |
| graffiti wall | `graffitiWall` | ENR-02 conflicting configs, police district |
| broken pylon, power cable | `pylon`, `cable` | ENR-04 stale CI reference (broken); power line (intact) |
| cooling tower | `coolingTower` | pipeline parity, power plant |
| construction crane, site | `crane` | next fix in a district |
| traffic light, cone, barrier | `trafficLight`, `cone`, `barrier` | district street ladder: L0 closed, L1 one lane |
| district landmark | `landmark` | one landmark per pillar and level |
| clock texture | `clockTex` | city hall clock face (texture helper, not a model) |

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
