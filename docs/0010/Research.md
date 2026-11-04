---
type: 'Research Note'
title: 'City and map editor: skills, frameworks and assets'
description: 'Research before building a Harness City editor for terrain, trees, roads, rail, vehicle paths, districts and export.'
status: 'draft'
created: '2026-10-29'
updated: '2026-10-29'
generated: 'agent'
verified: 'unverified'
owner: 'Andreas Elser'
tags:
  - 'harness-city'
  - 'editor'
  - 'research'
---

# City and map editor: skills, frameworks and assets

## 1. Question

The owner wants a complete city builder for Harness City:

* terrain editing (terraforming);
* tree placement;
* streets and tracks, both guided (grid, snapping) and free form;
* drawing street connections;
* paths for trucks, planes, ships and other moving objects;
* all CC0 assets available in a palette;
* editing districts by their main goal (the harness pillar);
* export of the result for use in the agent harness setup.

This note records what exists before anything is built. Nothing was implemented. Facts were
read on 2026-10-29 from the sources at the end. Rows marked "not read" are leads only.

## 2. Short answer

No ready-made editor fits. The closest projects are 2D canvas games, have no licence, or use
a perspective camera, which `DESIGN.md` forbids. The pieces do exist as MIT libraries that
fit the current stack (three.js r160, no bundler). The recommended route is a separate
editor page in `apps/harness-city/`, built from small MIT add-ons. It would write one
versioned map file (`city-map.json`) that the viewer reads. Assets come from the official
CC0 kits through the existing `tools/convert_assets.mjs` pipeline.

## 3. Agent skills

| Collection | What it offers | Fit for the editor | Licence |
|---|---|---|---|
| gamedev-skills/awesome-gamedev-agent-skills (the video) | 74 skills plus a router. Web: `threejs-scene-setup`, `threejs-gltf-loading`, `threejs-materials-lighting`, `phaser-*`, `pixijs-rendering`. Disciplines: `level-design`, `procedural-gen`, `save-systems`, `game-ui-ux`, `camera-systems`, `performance-optimization`, `game-ai`, `create-game-assets` | Useful: `save-systems` (plain data, atomic writes, schema versioning and migration), `procedural-gen` (seeded RNG, fBm heightmaps), `game-ui-ux`, `performance-optimization`, `game-ai` (path following). No editor, gizmo, terrain-brush or road skill | Apache-2.0 |
| cloudai-x/threejs-skills | 10 skills: fundamentals, geometry and instancing, materials, lighting, textures, animation, loaders, shaders, post-processing, interaction (raycasting, controls) | `threejs-interaction` and `threejs-geometry` help with picking and instanced trees | MIT |
| OpenAEC-Foundation/Three.js-Claude-Skill-Package | 24 skills, including controls (OrbitControls, MapControls, FlyControls, TransformControls), raycaster, performance, and a model optimizer agent | Controls and raycaster skills match the editor's needs | MIT |
| majidmanzarpour/threejs-game-skills | 9 skills for whole games, QA and generated assets (Tripo, Gemini, ElevenLabs) | Low. Generated assets are not CC0 kits and need paid services | MIT |

**Conflict to note:** `threejs-scene-setup` starts with `PerspectiveCamera` and `OrbitControls`.
Harness City pins an orthographic isometric camera with 90 degree rotation, and
`tools/check.py` now enforces it. Any skill output must be adapted to that camera.

Skills already available in this workspace that apply: `discovery-poc` (spike before a spec),
`prototype`, `frontend-design`, `tdd`, `testing-gatekeeper` and `codebase-design`.

## 4. Reference projects

| Project | What it shows | Reuse |
|---|---|---|
| LatridellActiveX/lowpoly-city | Vite, TypeScript and three.js isometric builder: free-form curved roads that snap to junctions and angles, lane markings, zoning along roads, power and water lines, traffic on the road graph, goods trucks, 90 degree rotation, undo and redo, saves with format v10 and migration | Ideas only. The page states no licence |
| zeikar/cimulity | PixiJS, 64x64 isometric map with raise, lower and level tools; water from elevation; congestion per road tile | MIT. 2D, so ideas only |
| KachmanLab/isometric-city (fork of amilich/isometric-city) | Canvas isometric engine, zoning, cars, trains, planes and seaplanes, pedestrians with pathfinding | MIT. Canvas 2D, so ideas only |
| lo-th/3d.city | three.js 3D city on micropolisJS, simulation in a Web Worker | MIT for the repo. The micropolisJS engine licence was not read |
| Kenney Starter Kit City Builder | Godot 4.6 grid builder: place, rotate, delete, save to a file, load a sample map | Code MIT, models CC0. The app already uses its road tiles |
| TheDuckCow/godot-road-generator | Road splines with per-point lane counts, procedural intersections, highway on and off ramps, auto-generated lane paths for traffic agents | MIT, Godot. The best model for the road data structure |

## 5. Libraries (npm, checked 2026-10-29)

| Package | Version | Licence | Use in the editor |
|---|---|---|---|
| three (vendored r160; latest 0.186.1) | 0.160 in repo | MIT | Already used. Its examples include `TransformControls`, `MapControls`, `GLTFExporter` and `CatmullRomCurve3` |
| three.terrain.js (IceCreamYou/THREE.Terrain) | 3.1.1 | MIT | Heightmap generators (Perlin, Simplex, Diamond-Square, Worley, fault lines), heightmap image import, `ScatterMeshes` for trees. Needs r160 or later |
| three-mesh-bvh | 0.9.17 | MIT | Fast raycasts for terrain brushes and placement on large meshes |
| simplex-noise | 4.0.3 | MIT | Seeded noise for "guided" terrain presets |
| lil-gui / tweakpane | 0.21.0 / 4.0.5 | MIT | Property panels (brush size, lane count, path speed) |
| yuka | 0.7.8 (last release 2022) | MIT | Steering and path following. Old, so optional |
| three-pathfinding | 1.3.0 | MIT | Navmesh paths. Probably not needed, because vehicles follow drawn graphs and splines |
| @gltf-transform/* | already used | MIT | Asset conversion in `tools/convert_assets.mjs` |

## 6. CC0 asset sources

| Source | Content relevant here | Licence | Status |
|---|---|---|---|
| Kenney City Kit (Roads) | 90 objects: roads, barriers, traffic lights, signs | CC0 | page read; bridges and ramps not listed |
| Kenney City Kit (Industrial) | 40 models plus solar and wind | CC0 | page read |
| Kenney Watercraft Kit | 40+ boats and ships | CC0 | page read |
| Kenney Train Kit | About 50 trains and spline track | CC0 | page read |
| Kenney City Kit (Commercial, Suburban), Car Kit, Nature Kit | Buildings, cars, trees, rocks | CC0 | Commercial, Car and Nature are already in `@netforge/asset-library-files` |
| Quaternius packs | Nature, cars, props, animals | CC0 on the pack pages | partly in the netforge package |
| Poly Pizza | About 6,000 models | **Mixed CC0 and CC-BY** | Use only models whose page says CC0. The netforge NOTICE excludes CC-BY ones |

**Constraint:** this workspace cannot reach kenney.nl, quaternius.com or poly.pizza (HTTP 403
through the allowlist). npm and GitHub work. Kits that are not in the netforge package need
the owner to download the official zip and attach it, or a linked computer. Unofficial npm
mirrors exist, but they are not trusted as a source.

## 7. Requirements mapped to an approach

| Requirement | Guided mode | Free mode |
|---|---|---|
| Terraforming | Raise, lower, flatten, smooth and level brushes snapped to cells; presets from seeded noise; water level slider | Same brushes without snapping, any radius and strength |
| Trees | Paint with a density brush, seeded scatter, exclusion zones from districts and roads | Single click placement with rotation and scale |
| Streets | Grid draw (cells, straight, T, cross, corner), as the city has today | Polyline with fillet radius for rounded corners, snap to junctions and angles, lane count per segment, ramps |
| Tracks (rail) | Grid draw along x or z with stations | Spline track with minimum curve radius |
| Connections | Junctions join automatically when ends meet | Manual junction editing; bridges and tunnels as segment flags |
| Vehicle paths | Trucks and cars get routes on the road graph between two named stops | Ships and planes get free splines on water or in the air, with speed, dwell and loop |
| Assets | Palette from the registry (`assets.json`) grouped by kit | Any registered model with free transform (move, rotate, scale) |
| Districts | Pillar picker: each district is bound to one pillar key and its rectangle | Resize and move the rectangle; label and goal text |
| Export | `city-map.json` for the viewer | Plus GLB (`GLTFExporter`) and a PNG plan |

## 8. Proposed data model and export

One plain JSON file, `city-map.json`, with `schema: 1` and a migration function for later
versions. This follows the `save-systems` skill.

* `grid`: cell size, bounds and seed.
* `terrain`: heightmap (a base64 Float32 array or PNG), water level, mountains.
* `districts`: pillar key, rectangle and goal text. No score data; the score still comes
  from the audit report.
* `roads`: a graph with nodes (x, z, kind) and edges (lanes, fillet radius, bridge or tunnel
  flag, highway tier).
* `rail`: the same graph shape, plus stations.
* `paths`: per vehicle class (truck, car, ship, plane, train): a route on a graph, or a free
  spline with speed, dwell and phase.
* `props`: asset id, position, rotation and scale. Trees are scatter rules plus overrides.
* `overlays`: airport, harbor, mall, industry and civic quarter placements.

The viewer (`index.html`) keeps reading `data/cities.json` for audit data. It reads
`city-map.json` for layout and falls back to today's built-in layout when the file is
missing. The city never changes the score.

## 9. Architecture sketch

* A new page, `apps/harness-city/editor.html`, so the hash-pinned `index.html` stays unchanged
  until the viewer learns to read the map file.
* Shared modules (terrain, roads, assets, camera) are split out of `index.html` only after a
  reviewed baseline update, as `AGENTS.md` requires.
* Camera: the same orthographic isometric rig with rotation buttons. A top-down plan view is
  an orthographic camera looking straight down, so it keeps the rule.
* Command stack for undo and redo; every tool is one command type.
* Placement is deterministic: scatter uses the seeded `rng`, never `Math.random`.
* Tests: Playwright drives the editor with the preinstalled Chromium. A round trip test
  checks that export, import and export produce identical JSON.

## 10. Risks and conflicts

* `index.html` is a frozen, hash-pinned runtime file. Reading a map file needs a reviewed
  baseline update.
* The three.js version gap (r160 vendored, 0.186.1 current) is a separate decision.
  THREE.Terrain works with r160.
* Free placement can conflict with the grid-based registry and click explanations. Each new
  object type still needs a registry row and an explanation.
* Export embeds layout only. Public examples must stay synthetic.
* Asset licences: every imported file needs a `NOTICE.md` entry. Poly Pizza CC-BY models are
  excluded.

## 11. Decisions (owner, 2026-10-29)

1. The editor is separate; the viewer stays alone.
2. Export the map JSON, GLB and PNG.
3. Free roads at any angle, where technically possible; guided snapping stays available.
4. The editor may move the existing layout.
5. Assets: first the models of the current map, then all other kits.

The binding version of these decisions is the "Editor" section of `apps/harness-city/DESIGN.md`.

## 12. Suggested next step

Run a `discovery-poc` spike (`docs/0010/spike/`): an editor page with a terrain brush, grid
road drawing and `city-map.json` export and import, on the existing camera. Go criteria:
round trip without loss, 60 fps on the L3 map, works from all four rotations.

## Sources

* [awesome-gamedev-agent-skills video](https://www.youtube.com/watch?v=ZFNbWEwlDjQ) and
  [repository](https://github.com/gamedev-skills/awesome-gamedev-agent-skills) (cloned read-only, commit 19d93f9)
* [cloudai-x/threejs-skills](https://github.com/cloudai-x/threejs-skills)
* [OpenAEC-Foundation/Three.js-Claude-Skill-Package](https://github.com/OpenAEC-Foundation/Three.js-Claude-Skill-Package)
* [majidmanzarpour/threejs-game-skills](https://github.com/majidmanzarpour/threejs-game-skills)
* [LatridellActiveX/lowpoly-city](https://github.com/LatridellActiveX/lowpoly-city)
* [zeikar/cimulity](https://github.com/zeikar/cimulity)
* [KachmanLab/isometric-city](https://github.com/KachmanLab/isometric-city)
* [lo-th/3d.city](https://github.com/lo-th/3d.city)
* [Kenney Starter Kit City Builder](https://store.godotengine.org/asset/kenney/starter-kit-city-builder/)
* [TheDuckCow/godot-road-generator](https://github.com/TheDuckCow/godot-road-generator)
* [IceCreamYou/THREE.Terrain](https://github.com/IceCreamYou/THREE.Terrain)
* [City Kit Roads](https://opengameart.org/content/city-kit-roads),
  [City Kit Industrial](https://gamedev.net/news/5434-city-kit-industrial/),
  [Watercraft Kit](https://kenney-assets.itch.io/watercraft-kit),
  [Train Kit](https://opengameart.org/content/train-kit)
* [Poly.Pizza article](https://gamefromscratch.com/poly-pizza-a-replacement-to-google-poly/)
* npm registry metadata for the packages in section 5; `@netforge/asset-library-files` 0.2.0 NOTICE
