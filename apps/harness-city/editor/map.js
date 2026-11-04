// Harness City map model: plain data, no three.js. Shared by the editor and tests.
// One file per city layout (city-map.json). See DESIGN.md "Editor" and "City map (grid)".

export const SCHEMA = 2;

export const PILLARS = [
  { k: "verification", n: "Verification", place: "Hospital & test labs", c: "#d64545", goal: "Can the agent tell whether it broke something?" },
  { k: "orientation", n: "Orientation", place: "City hall & visitor info", c: "#2f86c9", goal: "Can an agent find its way without reading everything?" },
  { k: "static_guardrails", n: "Static guardrails", place: "Police headquarters", c: "#33489c", goal: "Are style and correctness enforced, not suggested?" },
  { k: "workflow_entry_points", n: "Workflow entry points", place: "Central station & rail", c: "#24946a", goal: "Is there one obvious way to do common things?" },
  { k: "automatic_triggers", n: "Automatic triggers", place: "Fire & alarm station", c: "#e0672b", goal: "Do checks fire without anyone remembering?" },
  { k: "pipeline_parity", n: "Pipeline parity", place: "Power plant & grid", c: "#d9a42a", goal: "Does CI run what developers run locally?" },
  { k: "doc_hygiene", n: "Doc hygiene", place: "Public library", c: "#8a5bb5", goal: "Is the docs layer machine-readable and current?" },
];
export const PILLAR = Object.fromEntries(PILLARS.map((p) => [p.k, p]));

// Zone kinds besides districts. Overlays never change the score.
export const ZONE_KINDS = {
  airport: { n: "Airport", c: "#7d8a96" },
  station: { n: "Station", c: "#5a8f7b" },
  mall: { n: "Shopping Mall", c: "#c9784a" },
  industry: { n: "Goods industry", c: "#8f7a5a" },
  harbor: { n: "Harbor", c: "#4f7fa8" },
  bank: { n: "Bank", c: "#b59a3a" },
  court: { n: "Court", c: "#6d6a8f" },
  archive: { n: "Archive", c: "#5f6b5f" },
  park: { n: "Park", c: "#5c9a4d" },
  other: { n: "Zone", c: "#8a8f94" },
};

export const VEHICLES = {
  car: { n: "Car", net: "roads", c: "#2f86c9", speed: 3 },
  truck: { n: "Truck", net: "roads", c: "#c9784a", speed: 2.2 },
  bus: { n: "Bus", net: "roads", c: "#24946a", speed: 2.4 },
  train: { n: "Train", net: "rail", c: "#6a5a8c", speed: 4 },
  ship: { n: "Ship", net: "free", c: "#2c6f9e", speed: 1.2 },
  plane: { n: "Plane", net: "free", c: "#4a5560", speed: 7 },
};

// Deterministic generator (mulberry32). Scene building never uses Math.random.
export function rng(seed) {
  let a = seed >>> 0;
  return () => {
    a = (a + 0x6d2b79f5) >>> 0;
    let t = a;
    t = Math.imul(t ^ (t >>> 15), t | 1);
    t ^= t + Math.imul(t ^ (t >>> 7), t | 61);
    return ((t ^ (t >>> 14)) >>> 0) / 4294967296;
  };
}

const r3 = (v) => Math.round(v * 1000) / 1000;

// ---------- terrain ----------
export function makeTerrain(x0, x1, z0, z1, step = 1) {
  const w = Math.round((x1 - x0) / step) + 1, h = Math.round((z1 - z0) / step) + 1;
  return { x0, z0, step, w, h, water: -0.35, heights: new Array(w * h).fill(0) };
}
export function terrainIndex(t, i, j) { return j * t.w + i; }
export function heightAt(t, x, z) {
  const fx = (x - t.x0) / t.step, fz = (z - t.z0) / t.step;
  const i = Math.max(0, Math.min(t.w - 2, Math.floor(fx))), j = Math.max(0, Math.min(t.h - 2, Math.floor(fz)));
  const u = Math.max(0, Math.min(1, fx - i)), v = Math.max(0, Math.min(1, fz - j));
  const H = t.heights, a = H[j * t.w + i], b = H[j * t.w + i + 1], c = H[(j + 1) * t.w + i], d = H[(j + 1) * t.w + i + 1];
  return a * (1 - u) * (1 - v) + b * u * (1 - v) + c * (1 - u) * v + d * u * v;
}

// Brush: raise | lower | flatten | smooth | level (set to target). Returns changed index range.
export function applyBrush(t, kind, x, z, radius, strength, target = 0, snap = 0) {
  const s = t.step, i0 = Math.max(0, Math.floor((x - radius - t.x0) / s)), i1 = Math.min(t.w - 1, Math.ceil((x + radius - t.x0) / s));
  const j0 = Math.max(0, Math.floor((z - radius - t.z0) / s)), j1 = Math.min(t.h - 1, Math.ceil((z + radius - t.z0) / s));
  const H = t.heights, src = kind === "smooth" ? H.slice() : null;
  for (let j = j0; j <= j1; j++) for (let i = i0; i <= i1; i++) {
    const px = t.x0 + i * s, pz = t.z0 + j * s, d = Math.hypot(px - x, pz - z);
    if (d > radius) continue;
    const f = strength * (snap ? 1 : 0.5 * (1 + Math.cos((Math.PI * d) / radius)));
    const k = j * t.w + i;
    if (kind === "raise") H[k] += f;
    else if (kind === "lower") H[k] -= f;
    else if (kind === "flatten" || kind === "level") H[k] += (target - H[k]) * Math.min(1, f * 4);
    else if (kind === "smooth") {
      let sum = 0, n = 0;
      for (let dj = -1; dj <= 1; dj++) for (let di = -1; di <= 1; di++) {
        const ii = i + di, jj = j + dj;
        if (ii >= 0 && jj >= 0 && ii < t.w && jj < t.h) { sum += src[jj * t.w + ii]; n++; }
      }
      H[k] += (sum / n - H[k]) * Math.min(1, f * 4);
    }
    if (snap) H[k] = Math.round(H[k] / snap) * snap;
    H[k] = Math.max(-4, Math.min(14, H[k]));
  }
  return { i0, i1, j0, j1 };
}

function noise2(seed) {
  const r = rng(seed), P = Array.from({ length: 256 }, () => r());
  const g = (i, j) => P[(i * 73 + j * 151 + ((i * j) & 255)) & 255];
  return (x, z) => {
    const i = Math.floor(x), j = Math.floor(z), u = x - i, v = z - j, su = u * u * (3 - 2 * u), sv = v * v * (3 - 2 * v);
    return g(i, j) * (1 - su) * (1 - sv) + g(i + 1, j) * su * (1 - sv) + g(i, j + 1) * (1 - su) * sv + g(i + 1, j + 1) * su * sv;
  };
}
export function fbm(seed) {
  const n = noise2(seed);
  return (x, z) => { let a = 0, amp = 0.5, f = 1; for (let o = 0; o < 4; o++) { a += amp * n(x * f, z * f); amp *= 0.5; f *= 2; } return a; };
}

// ---------- graphs (roads, rail) ----------
export function emptyGraph() { return { nodes: [], edges: [] }; }
export function nodeById(g, id) { return g.nodes.find((n) => n.id === id); }
function nextId(list, prefix) {
  let m = 0;
  for (const it of list) { const v = Number(String(it.id).slice(prefix.length)); if (v > m) m = v; }
  return prefix + (m + 1);
}
export function addNode(g, x, z, prefix = "n") { const n = { id: nextId(g.nodes, prefix), x: r3(x), z: r3(z) }; g.nodes.push(n); return n; }
export function addEdge(g, a, b, props = {}, prefix = "e") {
  if (a === b) return null;
  const dup = g.edges.find((e) => (e.a === a && e.b === b) || (e.a === b && e.b === a));
  if (dup) return dup;
  const e = { id: nextId(g.edges, prefix), a, b, ...props };
  g.edges.push(e);
  return e;
}
export function removeNode(g, id) { g.nodes = g.nodes.filter((n) => n.id !== id); g.edges = g.edges.filter((e) => e.a !== id && e.b !== id); }
export function removeEdge(g, id) {
  g.edges = g.edges.filter((e) => e.id !== id);
  const used = new Set(g.edges.flatMap((e) => [e.a, e.b]));
  g.nodes = g.nodes.filter((n) => used.has(n.id));
}
export function nearestNode(g, x, z, maxD = 0.8) {
  let best = null, bd = maxD;
  for (const n of g.nodes) { const d = Math.hypot(n.x - x, n.z - z); if (d <= bd) { bd = d; best = n; } }
  return best;
}
// Points along an edge: straight, or a quadratic curve through control point c.
export function edgePoints(g, e, step = 0.5) {
  const A = nodeById(g, e.a), B = nodeById(g, e.b);
  if (!A || !B) return [];
  const c = e.c, len = Math.hypot(B.x - A.x, B.z - A.z) * (c ? 1.15 : 1), n = Math.max(1, Math.ceil(len / step)), out = [];
  for (let k = 0; k <= n; k++) {
    const t = k / n;
    if (c) {
      const u = 1 - t;
      out.push([u * u * A.x + 2 * u * t * c[0] + t * t * B.x, u * u * A.z + 2 * u * t * c[1] + t * t * B.z]);
    } else out.push([A.x + (B.x - A.x) * t, A.z + (B.z - A.z) * t]);
  }
  return out;
}
export function edgeLength(g, e) { const p = edgePoints(g, e, 0.25); let L = 0; for (let i = 1; i < p.length; i++) L += Math.hypot(p[i][0] - p[i - 1][0], p[i][1] - p[i - 1][1]); return L; }

// Split an edge at the point nearest to (x, z); returns the new node.
export function splitEdge(g, e, x, z) {
  const A = nodeById(g, e.a), B = nodeById(g, e.b);
  const dx = B.x - A.x, dz = B.z - A.z, L2 = dx * dx + dz * dz || 1;
  const t = Math.max(0.05, Math.min(0.95, ((x - A.x) * dx + (z - A.z) * dz) / L2));
  const props = { ...e }; delete props.id; delete props.a; delete props.b; delete props.c;
  const n = addNode(g, A.x + dx * t, A.z + dz * t, A.id.replace(/\d+$/, ""));
  g.edges = g.edges.filter((q) => q.id !== e.id);
  const pre = e.id.replace(/\d+$/, "");
  addEdge(g, A.id, n.id, props, pre);
  addEdge(g, n.id, B.id, props, pre);
  return n;
}
// Distance from (x, z) to the nearest edge; returns {edge, d}.
export function nearestEdge(g, x, z, maxD = 0.6) {
  let best = null, bd = maxD;
  for (const e of g.edges) {
    const p = edgePoints(g, e, 0.25);
    for (const q of p) { const d = Math.hypot(q[0] - x, q[1] - z); if (d < bd) { bd = d; best = e; } }
  }
  return best ? { edge: best, d: bd } : null;
}
export function shortestPath(g, from, to) {
  if (from === to) return [from];
  const adj = new Map(g.nodes.map((n) => [n.id, []]));
  for (const e of g.edges) {
    if (e.tunnelClosed) continue;
    const L = edgeLength(g, e);
    adj.get(e.a)?.push([e.b, L]);
    if (!e.oneway) adj.get(e.b)?.push([e.a, L]);
  }
  const dist = new Map([[from, 0]]), prev = new Map(), open = new Set([from]);
  while (open.size) {
    let u = null, du = Infinity;
    for (const v of open) { const d = dist.get(v); if (d < du) { du = d; u = v; } }
    open.delete(u);
    if (u === to) break;
    for (const [v, w] of adj.get(u) || []) {
      const nd = du + w;
      if (nd < (dist.get(v) ?? Infinity)) { dist.set(v, nd); prev.set(v, u); open.add(v); }
    }
  }
  if (!dist.has(to)) return null;
  const out = [to];
  while (out[0] !== from) out.unshift(prev.get(out[0]));
  return out;
}
// Build a graph from axis segments [[x0,z0,x1,z1], ...], joining where segments meet.
export function graphFromSegments(segs, props, prefix = "n", eprefix = "e") {
  const g = emptyGraph(), key = (x, z) => r3(x) + "," + r3(z), byKey = new Map();
  const node = (x, z) => { const k = key(x, z); if (!byKey.has(k)) byKey.set(k, addNode(g, x, z, prefix)); return byKey.get(k); };
  const onSeg = (s, x, z) => {
    const [ax, az, bx, bz] = s, cross = (bx - ax) * (z - az) - (bz - az) * (x - ax);
    if (Math.abs(cross) > 1e-6) return false;
    return x >= Math.min(ax, bx) - 1e-6 && x <= Math.max(ax, bx) + 1e-6 && z >= Math.min(az, bz) - 1e-6 && z <= Math.max(az, bz) + 1e-6;
  };
  for (const s of segs) {
    const pts = [[s[0], s[1]], [s[2], s[3]]];
    for (const o of segs) for (const q of [[o[0], o[1]], [o[2], o[3]]]) if (onSeg(s, q[0], q[1])) pts.push(q);
    for (const o of segs) { // crossings of axis-aligned segments
      if (o === s) continue;
      const sh = s[1] === s[3], oh = o[1] === o[3];
      if (sh !== oh) {
        const p = sh ? [o[0], s[1]] : [s[0], o[1]];
        if (onSeg(s, p[0], p[1]) && onSeg(o, p[0], p[1])) pts.push(p);
      }
    }
    const d = (p) => Math.hypot(p[0] - s[0], p[1] - s[1]);
    const uniq = [...new Map(pts.map((p) => [key(p[0], p[1]), p])).values()].sort((a, b) => d(a) - d(b));
    for (let i = 1; i < uniq.length; i++) addEdge(g, node(...uniq[i - 1]).id, node(...uniq[i]).id, { ...props }, eprefix);
  }
  return g;
}

// ---------- road cells (the viewer's road tiles) ----------
export const cellKey = (x, z) => x + "," + z;
export const cellId = (k) => "c:" + k;
export function cellsFromSegments(segs) {
  const out = new Set();
  for (const [x0, z0, x1, z1] of segs) {
    if (z0 === z1) for (let x = Math.min(x0, x1); x <= Math.max(x0, x1); x++) out.add(cellKey(x, z0));
    else for (let z = Math.min(z0, z1); z <= Math.max(z0, z1); z++) out.add(cellKey(x0, z));
  }
  return [...out];
}
// One routing graph from road cells and free roads. Free nodes join a cell within 0.6.
// The viewer adds the airport streets itself (index.html airSetup), shifted with the airport.
export function airRoadCells(map) {
  if (!map.view || !map.view.airport) return [];
  const { dx, dz } = map.layout.airport, out = [];
  for (let x = 34; x <= 64; x++) out.push(cellKey(x + dx, 8 + dz));
  for (let x = 34; x <= 46; x++) out.push(cellKey(x + dx, 0 + dz));
  for (let z = 1; z <= 7; z++) out.push(cellKey(46 + dx, z + dz));
  return out;
}
export function roadNetwork(map) {
  const g = emptyGraph(), cells = new Set(map.layout.roads.concat(airRoadCells(map)));
  for (const k of cells) { const [x, z] = k.split(",").map(Number); g.nodes.push({ id: cellId(k), x, z, cell: true }); }
  for (const k of cells) {
    const [x, z] = k.split(",").map(Number);
    for (const [dx, dz] of [[1, 0], [0, 1]]) { const n = cellKey(x + dx, z + dz); if (cells.has(n)) g.edges.push({ id: "ce:" + k + ">" + n, a: cellId(k), b: cellId(n), kind: "street" }); }
  }
  for (const n of map.roads.nodes) {
    g.nodes.push(n);
    const k = cellKey(Math.round(n.x), Math.round(n.z));
    if (cells.has(k) && Math.hypot(Math.round(n.x) - n.x, Math.round(n.z) - n.z) <= 0.6) g.edges.push({ id: "j:" + n.id, a: n.id, b: cellId(k), kind: "street" });
  }
  for (const e of map.roads.edges) g.edges.push(e);
  return g;
}
export function railNetwork(map) {
  const g = emptyGraph(), r = map.layout.rail, x0 = r.x0 ?? -10.5, x1 = r.x1 ?? railEnd(map);
  r.tracks.forEach((z, i) => { g.nodes.push({ id: "m" + i + "a", x: x0, z }, { id: "m" + i + "b", x: x1, z }); g.edges.push({ id: "m" + i, a: "m" + i + "a", b: "m" + i + "b", kind: "track" }); });
  for (const n of map.rail.nodes) g.nodes.push(n);
  for (const e of map.rail.edges) g.edges.push(e);
  return g;
}
function railEnd(map) { return map.view.airport ? 72.5 + map.layout.airport.dx : 39.5; }

// ---------- paths ----------
export function resolvePath(map, p) {
  const t = map.terrain;
  if (p.mode === "free") return (p.points || []).map((q) => [r3(q[0]), r3(q[1] ?? 0), r3(q[2])]);
  const g = p.mode === "rail" ? railNetwork(map) : roadNetwork(map), out = [];
  const stops = p.stops || [];
  for (let s = 1; s < stops.length; s++) {
    const route = shortestPath(g, stops[s - 1], stops[s]);
    if (!route) continue;
    for (let i = 1; i < route.length; i++) {
      const e = g.edges.find((q) => (q.a === route[i - 1] && q.b === route[i]) || (q.b === route[i - 1] && q.a === route[i]));
      let pts = edgePoints(g, e, 0.5);
      if (e.a !== route[i - 1]) pts = pts.slice().reverse();
      for (const q of out.length ? pts.slice(1) : pts) out.push([r3(q[0]), r3(heightAt(t, q[0], q[1]) + 0.05), r3(q[1])]);
    }
  }
  return out;
}

// ---------- viewer layout ----------
export const DIST_NOW = {
  workflow_entry_points: [1, 8, 1, 7], verification: [10, 19, 1, 7], orientation: [21, 28, 1, 7],
  static_guardrails: [1, 8, 9, 15], automatic_triggers: [10, 15, 9, 15], pipeline_parity: [17, 23, 9, 15], doc_hygiene: [25, 28, 9, 15],
};
export const AIRPORT_HOME = { x0: 47, x1: 63, z0: 1, z1: 7, sx0: 39, sx1: 45 };
function cityRoadSegments() {
  const s = [];
  for (const z of [0, 8, 16]) s.push([-4, z, 33, z]);
  for (const x of [0, 9, 20, 29]) s.push([x, 1, x, 7]);
  for (const x of [0, 9, 16, 24, 29]) s.push([x, 9, x, 15]);
  for (const x of [9, 24]) s.push([x, 17, x, 19]);
  return s;
}
export function defaultLayout() {
  return {
    roads: cellsFromSegments(cityRoadSegments()),
    rail: { tracks: [-1.75, -2.75], siding: -3.75, x0: null, x1: null },
    power: { z: 17.3, from: 22, to: -2, step: 3 },
    airport: { dx: 0, dz: 0 },
  };
}
// The layout object the viewer's applyLayout reads.
export function viewerLayout(map) {
  const L = map.layout, districts = {};
  for (const z of map.zones) if (z.kind === "district") districts[z.pillar] = { x0: Math.round(z.x0), x1: Math.round(z.x1), z0: Math.round(z.z0), z1: Math.round(z.z1) };
  const st = districts.workflow_entry_points, hubZ = st ? st.z1 + 1 : 8;
  const cells = new Set(L.roads);
  let links = [...new Set(L.roads.map((k) => k.split(",").map(Number)).filter(([, z]) => z === hubZ + 1).map(([x]) => x))].sort((a, b) => a - b);
  if (!links.length) links = [0, 9, 16, 24, 29];
  const keepOut = [[-1, 30, -4.4, 17.8]];
  return {
    districts, roads: [...cells], links,
    rail: { ...L.rail, tracks: L.rail.tracks.slice() }, power: { ...L.power }, airport: { ...L.airport },
    meadow: { trees: false, ground: false, keepOut },
  };
}
// Moving the airport zone moves the viewer's airport by whole cells.
export function syncAirport(map) {
  const a = map.zones.find((z) => z.id === "airport");
  if (!a) return;
  const dx = Math.round(a.x0 - AIRPORT_HOME.x0), dz = Math.round(a.z0 - AIRPORT_HOME.z0);
  map.layout.airport = { dx, dz };
  Object.assign(a, { x0: AIRPORT_HOME.x0 + dx, x1: AIRPORT_HOME.x1 + dx, z0: AIRPORT_HOME.z0 + dz, z1: AIRPORT_HOME.z1 + dz });
  const s = map.zones.find((z) => z.id === "airport-station");
  if (s) Object.assign(s, { x0: AIRPORT_HOME.sx0 + dx, x1: AIRPORT_HOME.sx1 + dx, z0: 2.5 + dz, z1: 5.5 + dz });
}
export function isViewerZone(z) { return z.kind === "district" || z.id === "airport" || z.id === "airport-station"; }
// Cells the viewer draws flat: terrain brushes leave them alone.
export function protectedAt(map, x, z) {
  for (const q of map.zones) if (isViewerZone(q) && x >= q.x0 - 0.6 && x <= q.x1 + 0.6 && z >= q.z0 - 0.6 && z <= q.z1 + 0.6) return true;
  const k = cellKey(Math.round(x), Math.round(z));
  return map.layout.roads.includes(k);
}

// ---------- presets ----------
function districts() {
  return PILLARS.map((p) => { const [x0, x1, z0, z1] = DIST_NOW[p.k]; return { id: p.k, kind: "district", pillar: p.k, label: p.place, goal: p.goal, x0, x1, z0, z1 }; });
}
function airportZones(dx = 0, dz = 0) {
  const A = AIRPORT_HOME;
  return [
    { id: "airport", kind: "airport", label: "Airport", goal: "Infrastructure overlay", x0: A.x0 + dx, x1: A.x1 + dx, z0: A.z0 + dz, z1: A.z1 + dz },
    { id: "airport-station", kind: "station", label: "Airport station", goal: "Rail and transit from the central station", x0: A.sx0 + dx, x1: A.sx1 + dx, z0: 2.5 + dz, z1: 5.5 + dz },
  ];
}
function scatterTrees(map, count, seed, keepOut) {
  const r = rng(seed), kinds = ["tree-pine", "tree-oak", "tree-fat"], t = map.terrain;
  for (let i = 0; i < count; i++) {
    const x = t.x0 + r() * (t.w - 1) * t.step, z = t.z0 + r() * (t.h - 1) * t.step, kind = kinds[Math.floor(r() * 3)], rot = Math.round(r() * 360), sc = r3(0.8 + r() * 0.5);
    if (keepOut(x, z) || heightAt(t, x, z) < t.water + 0.15 || heightAt(t, x, z) > 6) continue;
    map.props.push({ id: "p" + (map.props.length + 1), asset: kind, x: r3(x), z: r3(z), rot, scale: sc });
  }
}
function base(name, seed, ext, airport = true) {
  return {
    schema: SCHEMA, name, seed, view: { city: "thriving-demo", airport },
    layout: defaultLayout(), terrain: makeTerrain(...ext, 1),
    zones: districts().concat(airport ? airportZones() : []), roads: emptyGraph(), rail: emptyGraph(), props: [], paths: [],
  };
}
const inRect = (x, z, r, pad = 0) => x >= r[0] - pad && x <= r[1] + pad && z >= r[2] - pad && z <= r[3] + pad;
const near = (map, x, z) => cellId(cellKey(x, z));

// Today's viewer layout with the airport overlay on.
export function presetCurrent() {
  const m = base("Current city", 2026, [-16, 76, -12, 28]);
  const city = [-4.5, 33.5, -4.5, 19.5], air = [33, 66, -4.5, 9.5];
  scatterTrees(m, 300, 7, (x, z) => inRect(x, z, city) || inRect(x, z, air) || (z > -4.6 && z < -0.9));
  m.paths.push({ id: "v1", vehicle: "car", mode: "road", stops: [near(m, -4, 0), near(m, 33, 16)], speed: 3, loop: true });
  return m;
}

// The agreed L3 layout (DESIGN.md "City map (grid)").
export function presetL3() {
  const m = base("Level 3 plan", 2026, [-24, 76, -26, 42]);
  const t = m.terrain, f = fbm(11);
  for (let j = 0; j < t.h; j++) for (let i = 0; i < t.w; i++) {
    const x = t.x0 + i, z = t.z0 + j;
    let h = 0;
    if (z < -19) h = Math.min(10, (-19 - z) * 1.3 * (0.6 + f(x * 0.15, z * 0.15)));
    if (z > 31) h = -0.9; else if (z > 30) h = -0.3;
    if (x >= 61 && x <= 71 && z < -19) h = Math.min(h, 0.2 + (-19 - z) * 0.2);
    t.heights[j * t.w + i] = r3(h);
  }
  m.zones = districts().concat(airportZones(-2, 0));
  syncAirport(m);
  m.zones.push(
    { id: "bank", kind: "bank", label: "Bank", goal: "Secrets and credentials", x0: -20, x1: -14, z0: 1, z1: 6.5 },
    { id: "court", kind: "court", label: "Court", goal: "Licenses and governance", x0: -13, x1: -7, z0: 1, z1: 6.5 },
    { id: "archive", kind: "archive", label: "City archive", goal: "Protected personal data, fenced", x0: -20, x1: -11, z0: 8.5, z1: 15 },
    { id: "mall", kind: "mall", label: "Shopping Mall", goal: "Dependencies in use", x0: 50, x1: 58, z0: 11, z1: 17 },
    { id: "industry", kind: "industry", label: "Goods industry", goal: "Where dependencies come from", x0: 48, x1: 62, z0: -18, z1: -8 },
    { id: "harbor", kind: "harbor", label: "Harbor", goal: "Outbound releases and publishing", x0: 6, x1: 32, z0: 24, z1: 30 },
  );
  // guided streets (viewer tiles): civic quarter, connector to the highway, spurs
  m.layout.roads = [...new Set(m.layout.roads.concat(cellsFromSegments([
    [-20, 0, -5, 0], [-20, 8, -5, 8], [61, 8, 62, 8], [48, -6, 62, -6], [58, 14, 62, 14], [32, 30, 62, 30], [53, 7, 53, 7],
  ])))];
  // highway (free road, 3 + 3 lanes) with ramps to the cell street ends at x 62
  const g = m.roads, hw = [];
  for (const z of [-30, -22, -6, 8, 14, 30, 40]) hw.push(addNode(g, 66, z));
  for (let i = 1; i < hw.length; i++) {
    const e = addEdge(g, hw[i - 1].id, hw[i].id, { kind: "highway", lanes: 6, width: 7 });
    if (hw[i].z > 31) e.bridge = true;
    if (hw[i].z <= -22) e.tunnel = true; // tunnel z -30..-22, portal at z -22
  }
  for (const n of hw.slice(2, 6)) { const end = addNode(g, 62, n.z); addEdge(g, end.id, n.id, { kind: "street", lanes: 2, width: 1, ramp: true }); }
  const keep = [[-4.5, 33.5, -4.6, 19.5], [-21, -6, -1, 16], [29, 70, -19, 18], [5, 33, 23, 31]];
  scatterTrees(m, 520, 7, (x, z) => keep.some((r) => inRect(x, z, r)) || (x > 61 && x < 71));
  m.paths.push({ id: "v1", vehicle: "truck", mode: "road", stops: [near(m, 48, -6), near(m, 58, 14)], speed: 2.2, loop: true });
  m.paths.push({ id: "v2", vehicle: "truck", mode: "road", stops: [near(m, 62, 30), near(m, 32, 30)], speed: 2.2, loop: true });
  m.paths.push({ id: "v3", vehicle: "car", mode: "road", stops: [near(m, -20, 8), near(m, 62, 8)], speed: 3, loop: true });
  m.paths.push({ id: "v4", vehicle: "ship", mode: "free", points: [[10, -0.35, 36], [0, -0.35, 39], [-14, -0.35, 37], [-6, -0.35, 33.5], [8, -0.35, 33.5]], speed: 1.2, loop: true });
  return m;
}

export const PRESETS = { current: presetCurrent, l3: presetL3, empty: () => { const m = base("Empty map", 2026, [-20, 60, -20, 40], false); m.layout.roads = []; return m; } };

// ---------- persistence ----------
export function validate(m) {
  const err = [];
  if (!m || typeof m !== "object") return ["map is not an object"];
  if (m.schema !== SCHEMA) err.push("unsupported schema " + m.schema);
  const t = m.terrain;
  if (!t || !Array.isArray(t.heights) || t.heights.length !== t.w * t.h) err.push("terrain heights do not match w x h");
  if (!m.layout || !Array.isArray(m.layout.roads) || !m.layout.rail || !Array.isArray(m.layout.rail.tracks)) err.push("layout must have road cells and rail tracks");
  else for (const k of m.layout.roads) if (!/^-?\d+,-?\d+$/.test(k)) { err.push("road cell " + k + " is not x,z"); break; }
  if (!m.view || typeof m.view.city !== "string") err.push("view.city must name a demo city");
  for (const key of ["zones", "props", "paths"]) if (!Array.isArray(m[key])) err.push(key + " must be a list");
  for (const key of ["roads", "rail"]) {
    const g = m[key];
    if (!g || !Array.isArray(g.nodes) || !Array.isArray(g.edges)) { err.push(key + " must have nodes and edges"); continue; }
    const ids = new Set(g.nodes.map((n) => n.id));
    for (const e of g.edges) if (!ids.has(e.a) || !ids.has(e.b)) err.push(key + " edge " + e.id + " points to a missing node");
  }
  for (const z of m.zones || []) {
    if (z.kind === "district" && !PILLAR[z.pillar]) err.push("district " + z.id + " has unknown pillar " + z.pillar);
    if (!(z.x1 > z.x0 && z.z1 > z.z0)) err.push("zone " + z.id + " has an empty rectangle");
  }
  const keys = (m.zones || []).filter((z) => z.kind === "district").map((z) => z.pillar);
  for (const p of PILLARS) if (!keys.includes(p.k)) err.push("missing district for pillar " + p.k);
  return err;
}
// Schema 1 had no viewer layout: it gets the built-in one, its graphs stay free roads and tracks.
export function migrate(obj) {
  if (obj && obj.schema === SCHEMA) return obj;
  if (obj && obj.schema === 1) {
    const m = { ...obj, schema: SCHEMA, view: { city: "thriving-demo", airport: true }, layout: defaultLayout() };
    if (!m.zones.some((z) => z.id === "airport")) m.zones = m.zones.concat(airportZones());
    syncAirport(m);
    return m;
  }
  throw new Error("Unknown map schema: " + (obj && obj.schema));
}
// Stable, rounded JSON. Paths also carry their resolved points for other tools.
export function serialize(m) {
  const out = {
    schema: SCHEMA, name: m.name, seed: m.seed, generator: "harness-city-editor", view: m.view,
    layout: { ...m.layout, roads: [...m.layout.roads].sort() },
    terrain: { ...m.terrain, heights: m.terrain.heights.map(r3) },
    zones: m.zones.map((z) => ({ ...z, x0: r3(z.x0), x1: r3(z.x1), z0: r3(z.z0), z1: r3(z.z1) })),
    roads: m.roads, rail: m.rail,
    props: m.props.map((p) => ({ ...p, x: r3(p.x), z: r3(p.z), scale: r3(p.scale ?? 1), rot: r3(p.rot ?? 0) })),
    paths: m.paths.map((p) => { const q = { ...p }; delete q.resolved; return q; }),
  };
  out.resolved = Object.fromEntries(m.paths.map((p) => [p.id, resolvePath(m, p)]));
  return JSON.stringify(out, null, 1);
}
export function deserialize(text) {
  const obj = migrate(JSON.parse(text));
  delete obj.resolved;
  delete obj.generator;
  obj.layout.roads = [...obj.layout.roads].sort();
  const err = validate(obj);
  if (err.length) throw new Error("Invalid map: " + err.join("; "));
  return obj;
}
export function clone(m) { return JSON.parse(JSON.stringify(m)); }
