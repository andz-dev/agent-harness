---
type: 'Design Proposal'
title: 'Harness City airport assets'
status: 'draft'
created: '2026-10-27'
updated: '2026-10-28'
generated: 'agent'
verified: 'unverified'
owner: 'Andreas Elser'
---

<!-- markdownlint-disable-next-line MD025 -->
# Harness City airport: asset definition (draft)

Status: proposal for review. The earlier harbor overlay was reverted; the airport replaces it.

## What it shows

The airport is the **infrastructure overlay** (levels L0 to L3, never part of the 0-100 score).
Main-airport size = weakest applicable core area (Terraform, Compose or Dockerfile).
Each infra area gets its own **gate** with its own level. Devcontainer and Agent guidance
are independent benefits, not blockers. Repos without core infrastructure get no main
airport; applicable supporting facilities can still appear.

## Placement

* Outside the city, east of the rail line, on a plot as large as two district fields.
* One **access road** from the city's east road (reuses `road-straight`, `road-lamps`, `road-t`).
* One **airport station** (new asset, same style as the central station) at the terminal.
  The central station gets a spur: bus shuttle at L1, express train at L2+, so the airport is
  reachable from the hub. Line quality = lower of airport level and station level, as for districts.

## Tiers

| Level | Airport | Planes | Traffic |
|---|---|---|---|
| L0 | Fenced airstrip, closed barrier, wind sock limp, no buildings | none | none |
| L1 | Small airfield: short runway, visible hangar, passenger office, wind sock | 1 propeller plane | rare take-off/landing |
| L2 | Regional: runway, terminal, tower, 4 aircraft stands, apron, station | 1 jet, 1 propeller plane | arrivals and departures with taxiing |
| L3 | Enterprise hub: 2 runways, large terminal with jet bridges, cargo hangar, business jets, holiday charter planes | 5-6 mixed | constant arrivals and departures, ground vehicles |

## Prototype

The airport is built **inside the real city app** (same kit models, roads, rail, lighting, labels,
side panel), not as a separate page. Enable it with `index.html?airport`, or build the standalone
file with `python3 tools/build_standalone.py --offline --airport`. A control bar above the city
switches the station-link variant (A/B/C), per-area gate levels, container count and presets.
Surface / Underground is now a permanent city control, independent of the airport variant.
Pick another repository to see how the station level changes the link.

### Evaluation update (2026-10-28)

* Changing Compose, Dockerfile or Terraform may lower the main airport because the weakest
  applicable core area controls its size. L1 keeps both a prominent hangar and a passenger office;
  lowering a level no longer leaves an apparently empty terminal plot. L0 stays closed.
* Rebuilds restore surface material properties before applying the selected layer and release
  scene-owned GPU resources, without disposing shared kit models or caches. Repeated
  Compose L1/L2 round trips must return to the same material state and GPU allocation.
* Every city has a central station, including a closed L0 station. No service at L0, buses
  at L1, underground metro and buses at L2+. Connection level is the weaker endpoint.
* The permanent underground view works without an airport, persists across option/city
  changes and is no longer reset by A/B/C. It is not a new audit score or pillar.
* The download arrow exports the current map and labels with city summary, score, legend,
  infrastructure levels, selected description and scan limitations. The image identifies
  synthetic data and simulated overrides; evaluation controls are not audited results.
* The airport remains opt-in while its design is evaluated. Construction is separate from
  airport maturity; a small airfield is not represented merely as a construction site.

Regenerate this offline simulator from the app source, never by editing its embedded script:

```sh
python3 apps/harness-city/tools/build_standalone.py --offline --airport -o docs/0007/research/city-airport-prototype.html
python3 tools/offline_fonts.py docs/0007/research/city-airport-prototype.html
```

Browser regression instructions are in the [app guide](../../../apps/harness-city/README.md#browser-regression-checks).

Decisions made in the prototype: one runway at every level (L3 differs by terminal, stands,
tower, planes and crane); the airport station is a plot west of the airport and the express
line uses the existing rail line with its own platforms; aircraft capacity is 2 stands (L1),
4 stands (L2), 6 stands (L3). Area-status gates are independent of this capacity.

## Gates

Every applicable infrastructure area has a fixed-position status gate/pylon along the
forecourt, including at L0. No area disappears behind an aircraft-capacity cap. A grey
pylon and barrier means L0; amber with one band is L1; taller green with two bands is L2;
tall blue with three bands is L3. Each pylon opens the area's four-level explanation.

Devcontainer adds an independent developer side-terminal; Agent guidance adds a guidance
office beside the main airport. Each has its own L0-L3: closed facility, small facility,
working facility with an entrance canopy, expanded facility with upper floor/equipment.
Neither can lower or close the main airport. Cross-cutting remains independent and
non-blocking. Only Terraform, Compose and Dockerfile participate in the core minimum.
The control bar labels core areas and benefits, and names the limiting core area(s).
A dash removes that area's pylon and supporting facility, if any; it is not a failure.
Support-only configurations show those facilities without a main airport or airport service.
Adding or removing an area keeps the other pylons in place and never changes aircraft
capacity or terminal width at the same overall level. Aircraft stands and jet bridges
are separate from these area-status gates.

## Assets

Existing (CC0 kit): `hangar`, `road-*`, `fence`, `crate`, `generator`, `delivery-van`,
`firetruck`, `barrels`, `cone`, `barrier`, `dish`.

New, generated in code (the kit has no aircraft, same approach as trains and cranes):

| Asset | Used at |
|---|---|
| runway (tarmac, centre line, threshold marks, edge lights) | one at every level; closed at L0 |
| taxiway and apron | L2+ |
| wind sock | L0+ |
| propeller plane | L1+ |
| regional jet | L2+ |
| business jet | L3 |
| charter / holiday plane (colored livery) | L3 |
| passenger office, terminal (regional / large) | L1 / L2 / L3 |
| developer side-terminal, agent guidance office | own independent L0-L3; absent when not applicable |
| control tower | L2+ |
| jet bridge | L2+ per gate |
| cargo hangar | L3 |
| airport station (platform, canopy, sign) | L2+ (shuttle stop at L1) |
| baggage tug, fuel truck, stairs | L2+ ground vehicles |
| gate sign | per area |

## Animation

Same loop model as trains and cars: a plane has a route (approach, touch-down, roll-out,
taxi to gate, dwell, push-back, taxi, take-off). Speed and count rise with level.
L0 has no traffic. Lights blink; wind sock follows a slow sine.

## Panel and data

* Click the airport: overall level, weakest area, level explanation, tier look.
* Click a gate: area level, blocked-by checks, failing locations.
* Data: optional `infra` block per city in `cities.json`, built from `report.infra` by
  `tools/report_to_city.py` (same shape as the reverted harbor: `l`, `w`, `n`, `tools`, `a`, `r`).
* Demo cities get synthetic infra (thriving L3, prosperous L2, working L1, absent L0 or none).

## Station link: original evaluation options

Original baseline in git (`a3f9c69`, already on main): the central station is the transit hub
(`buildTransit` in `index.html`). Each district gets a line whose quality is the lower of the
station level and the district level: bus at L1/L2 on the road, and at L3 an **underground metro**
drawn as a see-through ghost train on a ribbon between an "M" portal at the station and an "M"
sign at the district. That baseline had no layer switch; the metro was always visible,
semi-transparent. The accepted update above replaces its L3 threshold with L2+ and adds
the permanent layer control.

The airport and its cargo (Docker containers) become two more stops on this network.
Three variants to try in a prototype page, switchable at runtime:

| Variant | Idea | Pro | Con |
|---|---|---|---|
| A. Same network | Airport = one more stop: buses L1+, metro L2+. Cargo apron beside the terminal | Consistent with districts | Airport link can be easy to miss |
| B. Underground layer | Same network, now using the permanent Surface / Underground control | Shows the whole network | Retained for comparison; the layer is no longer exclusive to B |
| C. Dedicated airport line | Dedicated express platforms and trains at L2+, alongside the bus/metro network | Makes the harness-to-infrastructure link explicit | Additional rail service to explain; still capped by the weaker endpoint |

Docker and containers: air freight. Cargo hangar with stacked shipping containers per
Dockerfile/Compose service (count by detected images), cargo planes and trucks between
apron and hangar. This keeps "container = Docker" literal.

Recommendation to test first: C with the underground toggle from B, because the user goal is
to show the harness and the infrastructure as connected, not only adjacent.

## Open points

* "Road and central station asset": I read this as an access road plus an airport station.
  Say if the station should instead be a second hub building.
* Credits: generated assets need no new licence entry; NOTICE.md gets one line.
