---
type: 'Application Guide'
---

# Harness City

An interactive 3D city for harness-audit results. Each repository is a city, its seven
harness pillars are districts (vacant lot L0 → skyline L3), traffic shows known limits,
construction sites show the next planned fix, and decay shows entropy findings.
Everything is static: no build step, no server-side code.

## Quick start

    python3 tools/serve.py            # then open http://localhost:8000/

(Browsers block `fetch()` on `file://`, hence the tiny server. Python 3 only, no packages.)

## Use your own scan results

    python3 tools/report_to_city.py harness-scan-compact.json -o data/cities.json
    python3 tools/report_to_city.py reports/ --title "Acme Harness City" --source "nightly scan"
    python3 tools/report_to_city.py a.json b.json --gut gut.json    # gut.json: {"repo-id": 70}

Inputs may be a scan export (`{"repos": [...]}`) or single-repo reports that follow
harness-audit's `schema/report.schema.json`; directories are searched for `*.json`. Reload the page.
To try another data file without overwriting: `index.html?data=data/other.json`.

## One file to share

    python3 tools/build_standalone.py                              # dist/harness-city.html (2.8 MB)
    python3 tools/build_standalone.py --offline -o dist/offline.html   # also inlines three.js (4.7 MB)

The standalone file has the data and all 3D models inlined, so it opens by double-click,
can be e-mailed, attached to a wiki page or uploaded to any static host. The default
build loads three.js 0.160 from jsDelivr; `--offline` needs no network at all.
Rebuild it after every data change.

## data/cities.json

    { "meta":   { "title", "tool", "scanDate", "source",         // all optional
                  "checks": { "ORI-04": {"p": 1, "l": 2, "g": true, "a": "all",
                                         "t": "title", "w": "why it matters"} } },  // from the catalog
      "cities": [ { "id": "repo", "score": 87,
                    "L": [3,2,3,3,3,2,1],      // verification, orientation, static_guardrails,
                                               // workflow_entry_points, automatic_triggers,
                                               // pipeline_parity, doc_hygiene  (0-3)
                    "comp": 101, "files": 32316, "pen": 0.0,
                    "gut": 80, "done": 93, "set": "calibration",           // optional
                    "steps": [ {"c": "CIP-05", "t": "text", "p": 3.3} ],   // next fixes (construction sites)
                    "ent":   [ {"c": "ENR-04", "p": "path"} ],             // decay: ENR-01 wagon, ENR-02 graffiti, ENR-04 pylon
                    "caps":  ["no-tests"],                                  // score cap: closes the hospital
                    "f":     [ {"c": "ORI-04", "s": "fail", "m": "component", "n": "note",
                                "e": [ {"k": "searched", "p": "AGENTS.md", "l": null, "x": "snippet"} ]} ],
                    "G":     [["VER-06"], [], [], [], [], [], []],      // gate failures per pillar
                    "lim":   ["scan limitation"] } ] }                  // f, G, lim optional

A fix's check id prefix (VER, ORI, STA, ENT, TRG, CIP, DOC) decides which district gets the
construction site. Tiers: Thriving ≥ 80, Prosperous ≥ 60, Working ≥ 45, Neglected below.

`meta.checks` is read from `skills/harness-audit/checks/catalog.yaml` (or `--catalog`) and
lists every check per pillar and level. `f` carries the report findings with their evidence
("searched" evidence is what was looked for and not found). Without findings, a district
still shows the checks needed for each level.

## Exploring a city

Click a building, its street, a bus, a construction site, the rail line or the power line;
the side panel explains what it stands for and lists the district's issues, missing files
and per-level checks. Click the city name for the score breakdown.

Public transport runs from the central station (workflow entry points) to every district.
A line's level is the lower of the station level and the district level: none (L0), one
bus (L1), underground metro plus sheltered buses (L2), frequent metro plus buses (L3).
The central station remains visible even at L0, closed with no service.

Surface and Underground select the permanent city layer, including cities without an
airport. Underground fades surface buildings to expose metro routes. The choice survives
repository and airport-option changes; it does not invent service for L0 or L1 connections.

The download arrow exports a PNG of the current view and visible labels, plus a wrapped
description containing the score, district legend, infrastructure levels, selected object
details and scan limitations. The export keeps the live camera unchanged. Synthetic
provenance and airport evaluation overrides are identified in the image.

## Airport prototype (infrastructure overlay)

`index.html?airport` (or `tools/build_standalone.py --airport`) adds an airport east of the
city with a control bar for the station-link variants and gate levels.
It is a draft and never changes the score. See [DESIGN.md](DESIGN.md) and
[docs/0007](../../docs/0007/research/airport-assets.md).

The lowest applicable core level (Terraform, Compose or Dockerfile) determines the main
airport size. L0 is a closed airstrip;
L1 retains a hangar and small passenger office; L2 restores the regional terminal; L3 is
the hub. A dash means not applicable, not L0. The control bar simulates infrastructure
levels for evaluation and does not change the report or score.

Every applicable area has its own fixed-position forecourt pylon, even at L0. Height,
bands and colour show that area's level. Devcontainer adds an independent developer
side-terminal; Agent guidance adds a guidance office. Their facilities grow with their
own L0-L3 and never lower or close the main airport. L0 closes only the supporting
facility; a dash removes it. Cross-cutting remains independent and non-blocking.
The control bar explicitly names only the limiting core area(s).
Aircraft capacity is separate (0, 2, 4 or 6 stands). Enabling an area never hides another
area or resizes the terminal while the overall level stays the same.
With support areas only, supporting facilities remain visible without a main airport,
runway or main-airport transport service. This does not change any audit result or score.

## Browser regression checks

Run the unattended suite from the repository root with `task app:test` after `task setup`.
It launches its own synthetic loopback server and real desktop/mobile Chromium projects,
tests actual controls and PNG downloads, and checks an offline standalone file with
network blocked. Page/console errors and missing browsers fail the run. CI uses the same
command; output stays ignored in `test-results/` and `playwright-report/` under this app.
Use `task app:test -- airport.spec.js --project=desktop-chromium` for a focused case.

Serve the default synthetic data with `?airport`, wait for the city and asset sheet to
load, then run in the browser console:

```js
const { checkCity } = await import("./tools/check_city.js");
await checkCity();
```

This dependency-free check exercises the real option controls, low-level buildings,
all per-area controls, fixed-level terminal stability, transport thresholds, station
landmarks, repeated rebuild material/GPU stability and a
nonblank PNG download. It restores the original repository, airport settings, layer and
camera. It downloads one synthetic PNG. Also inspect desktop/mobile screenshots and test
the offline standalone build; the browser check module itself is not embedded in that build.

## Layout

    index.html            the page (three.js scene, UI, all styles) - edit this to change the look
    data/cities.json      your data
    assets/assets.json    the 56 3D models, packed (base64 glb); assets/glb/ has them loose
    vendor/               three.js 0.160 + GLTFLoader (MIT), used by index.html offline
    tools/                serve.py, report_to_city.py, build_standalone.py,
                          convert_assets.mjs (re-creates the models from the Kenney and
                          Quaternius packs; paths at the top, needs @gltf-transform/*)
    DESIGN.md             design principles, pillar table, asset registry (read before changing)
    AGENTS.md             rules for agents working on the city
    NOTICE.md             licences and credits - keep it with any redistribution

## Notes

* Needs WebGL. Without it the page still shows the full data table.
* The compact scan export has no cap field, so the converter marks a city as capped
  ("no-tests") when Verification is L0 and the score is 40 or less. Full reports carry
  `score.caps_applied` and are used as is.
* Decay kinds other than ENR-01, ENR-02 and ENR-04 are skipped with a warning.
* Deep links: `index.html#repo-id` opens that city.
