# Harness City airport: asset definition (draft)

Status: proposal for review. The earlier harbor overlay was reverted; the airport replaces it.

## What it shows

The airport is the **infrastructure overlay** (levels L0 to L3, never part of the 0-100 score).
Size = overall infra level (weakest tool area). Each infra area gets its own **gate**
with its own level. Repos without real infrastructure get no airport.

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
| L1 | Small airfield: short runway, one hangar, wind sock | 1 propeller plane | rare take-off/landing |
| L2 | Regional: runway, terminal, tower, 2 gates, apron, station | 1 jet, 1 propeller plane | arrivals and departures with taxiing |
| L3 | Enterprise hub: 2 runways, large terminal with jet bridges, cargo hangar, business jets, holiday charter planes | 5-6 mixed | constant arrivals and departures, ground vehicles |

## Gates

One gate per infra area (tool areas first, then repo-wide: agent guidance, cross-cutting, entropy).
Gate sign shows the area name and level; the gate glows by level (L0 closed, L3 full light).
Maximum 8 gates; the rest are summarised on the terminal sign.

## Assets

Existing (CC0 kit): `hangar`, `road-*`, `fence`, `crate`, `generator`, `delivery-van`,
`firetruck`, `barrels`, `cone`, `barrier`, `dish`.

New, generated in code (the kit has no aircraft, same approach as trains and cranes):

| Asset | Used at |
|---|---|
| runway (tarmac, centre line, threshold marks, edge lights) | L1+ (2x at L3) |
| taxiway and apron | L2+ |
| wind sock | L0+ |
| propeller plane | L1+ |
| regional jet | L2+ |
| business jet | L3 |
| charter / holiday plane (colored livery) | L3 |
| terminal (small / large) | L2 / L3 |
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

## Station link: what exists, what to prototype

Found in git (`a3f9c69`, already on main): the central station is the transit hub
(`buildTransit` in `index.html`). Each district gets a line whose quality is the lower of the
station level and the district level: bus at L1/L2 on the road, and at L3 an **underground metro**
drawn as a see-through ghost train on a ribbon between an "M" portal at the station and an "M"
sign at the district. There is no layer switch yet; the metro is always visible, semi-transparent.

The airport and its cargo (Docker containers) become two more stops on this network.
Three variants to try in a prototype page, switchable at runtime:

| Variant | Idea | Pro | Con |
|---|---|---|---|
| A. Same network | Airport = one more district stop: bus on the access road (L1-L2), metro (L3). Cargo apron beside the terminal | Cheapest, consistent with districts | Metro and road look alike, "connection of harness and infra" is easy to miss |
| B. Underground layer | A toggle "Underground" fades the city to a ghost, shows all metro lines incl. airport line and station boxes; trains run in it | Shows the whole network, makes the harness-to-infra link explicit | One more mode to learn; needs layer toggle and camera handling |
| C. Dedicated airport line | One distinct colored express line (road + rail/metro) from the central station to the airport station, always visible, plus an optional underground layer for the rest | Strongest message: the repo harness is wired to the infrastructure | Special case outside the "lower of both ends" rule |

Docker and containers: air freight. Cargo hangar with stacked shipping containers per
Dockerfile/Compose service (count by detected images), cargo planes and trucks between
apron and hangar. This keeps "container = Docker" literal.

Recommendation to test first: C with the underground toggle from B, because the user goal is
to show the harness and the infrastructure as connected, not only adjacent.

## Open points

* "Road and central station asset": I read this as an access road plus an airport station.
  Say if the station should instead be a second hub building.
* Credits: generated assets need no new licence entry; NOTICE.md gets one line.
