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
                    "lim":   ["scan limitation"],                       // f, G, lim optional
                    "infra": { "l": 2, "w": "compose", "n": 4,          // optional overlay: level, weakest area, locations
                               "tools": ["compose"],
                               "a": [ {"k": "compose", "l": 2, "b": ["INF-C03"], "wide": false} ],
                               "r": [ {"c": "INF-C03", "t": "title", "a": "compose",
                                       "f": 1, "p": 3, "x": ["path"]} ] } } ] }   // from report.infra, never scored

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
bus (L1), frequent buses with shelters (L2), an underground metro shown as a see-through
train plus buses (L3).

## Layout

    index.html            the page (three.js scene, UI, all styles) - edit this to change the look
    data/cities.json      your data
    assets/assets.json    the 56 3D models, packed (base64 glb); assets/glb/ has them loose
    vendor/               three.js 0.160 + GLTFLoader (MIT), used by index.html offline
    tools/                serve.py, report_to_city.py, build_standalone.py,
                          convert_assets.mjs (re-creates the models from the Kenney and
                          Quaternius packs; paths at the top, needs @gltf-transform/*)
    NOTICE.md             licences and credits - keep it with any redistribution

## Notes

* Needs WebGL. Without it the page still shows the full data table.
* The compact scan export has no cap field, so the converter marks a city as capped
  ("no-tests") when Verification is L0 and the score is 40 or less. Full reports carry
  `score.caps_applied` and are used as is.
* Decay kinds other than ENR-01, ENR-02 and ENR-04 are skipped with a warning.
* Deep links: `index.html#repo-id` opens that city.

## Infrastructure harbor

A report with an `infra` block gets a harbor east of the districts: one pad per infrastructure
area (tool areas first, then repo-wide areas), a flag with the overall infra level and a card
in the side panel. It is an overlay: it never changes the score, the tier or the districts.
Pad level L0 is a fenced yard, L3 a finished yard. `tools/report_to_city.py` builds the block
from `report.json`; `tools/make_demo.py` adds synthetic infra to the demo cities.
