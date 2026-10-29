---
type: 'Application Guide'
title: 'Harness City Editor'
status: 'draft'
created: '2026-10-29'
updated: '2026-10-29'
generated: 'agent'
verified: 'unverified'
owner: 'Andreas Elser'
---

# Harness City Editor

    python3 tools/serve.py            # then open http://localhost:8000/editor.html

A separate page for the city layout. It shows the viewer itself (`index.html?embed` in a frame),
so districts, road tiles, station, rail and airport look exactly like the viewer at the chosen
demo level. The editor changes the viewer's layout and draws its own layers on top: terrain,
water, free streets and highways, extra tracks, other zones, placed models and vehicle paths.
The plain viewer does not read the map file yet. Design rules: [DESIGN.md](DESIGN.md), "Editor".

## Tools

| Key | Tool | What it does |
|---|---|---|
| 1 | Select / move | Select, drag to move, drag corners to resize zones, drag diamonds to bend curves |
| 2 | Terraform | Raise, lower, flatten, smooth, set height, water level; viewer areas stay flat |
| 3 | Trees | Paint or erase trees and bushes; seeded, so repeatable |
| 4 | Streets | Road tiles: drag a straight line of the viewer's tiles. Free: any angle, curves, highways |
| 5 | Tracks | Extra track next to the viewer's main line |
| 6 | Districts and zones | Drag a rectangle; a district moves, other zones are added |
| 7 | Place assets | Any model from the palette, R rotates, `[` and `]` scale |
| 8 | Vehicle paths | Cars, trucks, buses on roads; trains on tracks; ships and planes free |
| 9 | Erase | Delete what you click |

Other keys: G guided mode (cells and 45 degree steps), Q and E rotate, P plan view, Space or
right mouse drag pans, wheel zooms, Ctrl+Z and Ctrl+Y undo and redo, Enter or Esc ends a line.

## Start and export

* Start from the current city, the level 3 plan or an empty map (`editor.html?preset=l3`), or
  load a file with `?map=path.json`. Work is kept in the browser between visits.
* The header picks the demo city (its levels decide what the viewer builds), the airport
  overlay and the viewer's labels. Districts and the airport move by whole cells.
* Export: the map JSON (`*.city-map.json`, schema 2, with resolved vehicle paths), a GLB of the
  scene and a PNG of the view.

## Known limits

* Desktop first; touch editing is not supported yet.
* Rounded corners on free roads come from round junctions and curved segments, not from
  automatic fillets. Viewer buses and cars use the viewer's own routes, not editor paths.
* The airport express platform does not move with the airport yet.
* With software rendering (no GPU) the editor runs at a low frame rate.
* The palette holds the models of the current map. Other CC0 kits need an import with a
  NOTICE entry first (see `docs/0010/Research.md`).
