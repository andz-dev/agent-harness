// Harness City map model: plain data, no three.js. Shared by the editor and tests.
// One file per city layout (city-map.json). See DESIGN.md "Editor" and "City map (grid)".

export const SCHEMA = 1;

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

// ---------- paths ----------
export function resolvePath(map, p) {
  const t = map.terrain;
  if (p.mode === "free") return (p.points || []).map((q) => [r3(q[0]), r3(q[1] ?? 0), r3(q[2])]);
  const g = p.mode === "rail" ? map.rail : map.roads, out = [];
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

// ---------- presets ----------
const DIST_NOW = {
  workflow_entry_points: [1, 8, 1, 7], verification: [10, 19, 1, 7], orientation: [21, 28, 1, 7],
  static_guardrails: [1, 8, 9, 15], automatic_triggers: [10, 15, 9, 15], pipeline_parity: [17, 23, 9, 15], doc_hygiene: [25, 28, 9, 15],
};
function cityRoadSegments() {
  const s = [];
  for (const z of [0, 8, 16]) s.push([-4, z, 33, z]);
  for (const x of [0, 9, 20, 29]) s.push([x, 0, x, 8]);
  for (const x of [0, 9, 16, 24, 29]) s.push([x, 8, x, 16]);
  for (const x of [9, 24]) s.push([x, 16, x, 19]);
  return s;
}
function districts() {
  return PILLARS.map((p) => { const [x0, x1, z0, z1] = DIST_NOW[p.k]; return { id: p.k, kind: "district", pillar: p.k, label: p.place, goal: p.goal, x0, x1, z0, z1 }; });
}
function scatterTrees(map, count, seed, keepOut) {
  const r = rng(seed), kinds = ["tree-oak", "tree-pine", "tree-fat"], t = map.terrain;
  for (let i = 0; i < count; i++) {
    const x = t.x0 + r() * (t.w - 1) * t.step, z = t.z0 + r() * (t.h - 1) * t.step, kind = kinds[Math.floor(r() * 3)], rot = Math.round(r() * 360), sc = r3(0.8 + r() * 0.5);
    if (keepOut(x, z) || heightAt(t, x, z) < t.water + 0.15 || heightAt(t, x, z) > 6) continue;
    map.props.push({ id: "p" + (map.props.length + 1), asset: kind, x: r3(x), z: r3(z), rot, scale: sc });
  }
}
function base(name, seed, ext) {
  return {
    schema: SCHEMA, name, seed,
    terrain: makeTerrain(...ext, 1),
    zones: districts(), roads: emptyGraph(), rail: emptyGraph(), props: [], paths: [],
  };
}
const inRect = (x, z, r, pad = 0) => x >= r[0] - pad && x <= r[1] + pad && z >= r[2] - pad && z <= r[3] + pad;

// Today's viewer layout (index.html constants), with the airport overlay on.
export function presetCurrent() {
  const m = base("Current city", 2026, [-14, 70, -10, 24]);
  m.roads = graphFromSegments(cityRoadSegments().concat([[33, 8, 64, 8], [33, 0, 46, 0], [46, 0, 46, 8]]), { kind: "street", lanes: 2, width: 1 }, "n", "e");
  m.rail = graphFromSegments([[-10.5, -1.75, 39.5, -1.75], [-10.5, -2.75, 39.5, -2.75], [-6, -3.75, 30, -3.75]], { kind: "track" }, "r", "t");
  m.zones.push({ id: "airport", kind: "airport", label: "Airport", goal: "Infrastructure overlay", x0: 47, x1: 63, z0: 1, z1: 7 });
  m.zones.push({ id: "airport-station", kind: "station", label: "Airport station", goal: "Airport express from the central station", x0: 39, x1: 45, z0: 2.5, z1: 5.5 });
  const city = [-4.5, 33.5, -4.5, 19.5], air = [33, 66, -4.5, 9.5];
  scatterTrees(m, 260, 7, (x, z) => inRect(x, z, city) || inRect(x, z, air));
  m.paths.push({ id: "v1", vehicle: "car", mode: "road", stops: stopIds(m.roads, [[-4, 0], [33, 16]]), speed: 3, loop: true });
  m.paths.push({ id: "v2", vehicle: "train", mode: "rail", stops: stopIds(m.rail, [[-10.5, -1.75], [39.5, -1.75]]), speed: 4, loop: true });
  return m;
}
function stopIds(g, pts) { return pts.map(([x, z]) => nearestNode(g, x, z, 2)?.id).filter(Boolean); }

// The agreed L3 layout (DESIGN.md "City map (grid)").
export function presetL3() {
  const m = base("Level 3 plan", 2026, [-24, 76, -26, 42]);
  const t = m.terrain, f = fbm(11);
  for (let j = 0; j < t.h; j++) for (let i = 0; i < t.w; i++) {
    const x = t.x0 + i, z = t.z0 + j;
    let h = 0;
    if (z < -19) h = Math.min(10, (-19 - z) * 1.3 * (0.6 + f(x * 0.15, z * 0.15)));
    if (z > 31) h = -0.9;
    else if (z > 30) h = -0.3;
    if (x >= 61 && x <= 71 && z >= -26 && z <= -19) h = Math.min(h, 0.2 + (-19 - z) * 0.2) + 0; // tunnel cut
    t.heights[j * t.w + i] = r3(h);
  }
  t.water = -0.35;
  const z = (id) => m.zones.find((q) => q.id === id);
  void z;
  m.zones.push(
    { id: "airport", kind: "airport", label: "Airport", goal: "Infrastructure overlay", x0: 43, x1: 59, z0: 1, z1: 7 },
    { id: "airport-station", kind: "station", label: "Airport station", goal: "Rail from the central station", x0: 35, x1: 41, z0: 2.5, z1: 5.5 },
    { id: "bank", kind: "bank", label: "Bank", goal: "Secrets and credentials", x0: -20, x1: -14, z0: 1, z1: 6.5 },
    { id: "court", kind: "court", label: "Court", goal: "Licenses and governance", x0: -13, x1: -7, z0: 1, z1: 6.5 },
    { id: "archive", kind: "archive", label: "City archive", goal: "Protected personal data, fenced", x0: -20, x1: -11, z0: 8.5, z1: 15 },
    { id: "mall", kind: "mall", label: "Shopping Mall", goal: "Dependencies in use", x0: 50, x1: 58, z0: 11, z1: 17 },
    { id: "industry", kind: "industry", label: "Goods industry", goal: "Where dependencies come from", x0: 48, x1: 62, z0: -18, z1: -8 },
    { id: "harbor", kind: "harbor", label: "Harbor", goal: "Outbound releases and publishing", x0: 6, x1: 32, z0: 24, z1: 30 },
  );
  const segs = cityRoadSegments().concat([
    [33, 8, 62.5, 8], [51, 7, 51, 8], [48, -6, 62.5, -6], [58, 14, 62.5, 14], [32, 30, 62.5, 30],
    [-20, 0, -4, 0], [-20, 8, -4, 8],
  ]);
  m.roads = graphFromSegments(segs, { kind: "street", lanes: 2, width: 1 }, "n", "e");
  const hw = graphFromSegments([[66, -24, 66, 40]], {}, "h", "x");
  // highway: own nodes, then link the spurs to it
  const map = new Map();
  for (const n of hw.nodes) map.set(n.id, addNode(m.roads, n.x, n.z).id);
  for (const e of hw.edges) addEdge(m.roads, map.get(e.a), map.get(e.b), { kind: "highway", lanes: 6, width: 7 });
  for (const zz of [-6, 8, 14, 30]) {
    const e = nearestEdge(m.roads, 66, zz, 0.5)?.edge;
    const hub = e ? splitEdge(m.roads, e, 66, zz) : null;
    const end = nearestNode(m.roads, 62.5, zz, 0.2);
    if (hub && end) addEdge(m.roads, end.id, hub.id, { kind: "street", lanes: 2, width: 1, ramp: true });
  }
  for (const e of m.roads.edges) {
    if (e.kind !== "highway") continue;
    const A = nodeById(m.roads, e.a), B = nodeById(m.roads, e.b);
    if (Math.max(A.z, B.z) > 31) e.bridge = true;
    if (Math.min(A.z, B.z) < -19) e.tunnel = true;
  }
  m.rail = graphFromSegments([[-10.5, -1.75, 33, -1.75], [-10.5, -2.75, 33, -2.75], [-6, -3.75, 30, -3.75], [41, 4, 43, 4]], { kind: "track" }, "r", "t");
  const ra = nearestNode(m.rail, 33, -1.75, 0.1), rb = nearestNode(m.rail, 41, 4, 0.1);
  const mid = addNode(m.rail, 37, 4, "r");
  addEdge(m.rail, ra.id, mid.id, { kind: "track" }, "t").c = [36.5, -1.75];
  addEdge(m.rail, mid.id, rb.id, { kind: "track" }, "t");
  const keep = [[-4.5, 33.5, -4.5, 19.5], [-21, -6, 0, 16], [33, 70, -19, 18], [5, 33, 23, 31]];
  scatterTrees(m, 520, 7, (x, z) => keep.some((r) => inRect(x, z, r)) || (x > 61 && x < 71));
  m.paths.push({ id: "v1", vehicle: "truck", mode: "road", stops: stopIds(m.roads, [[48, -6], [58, 14]]), speed: 2.2, loop: true });
  m.paths.push({ id: "v2", vehicle: "car", mode: "road", stops: stopIds(m.roads, [[33, 8], [51, 7]]), speed: 3, loop: true });
  m.paths.push({ id: "v3", vehicle: "truck", mode: "road", stops: stopIds(m.roads, [[62.5, 30], [32, 30]]), speed: 2.2, loop: true });
  m.paths.push({ id: "v4", vehicle: "train", mode: "rail", stops: stopIds(m.rail, [[-10.5, -1.75], [43, 4]]), speed: 4, loop: true });
  m.paths.push({ id: "v5", vehicle: "ship", mode: "free", points: [[10, -0.35, 36], [0, -0.35, 39], [-14, -0.35, 37], [-6, -0.35, 33.5], [8, -0.35, 33.5]], speed: 1.2, loop: true });
  m.paths.push({ id: "v6", vehicle: "plane", mode: "free", points: [[74, 7, -14], [60, 4, -2], [51, 1.2, 4], [40, 4, 12], [20, 8, 20]], speed: 7, loop: true });
  return m;
}

export const PRESETS = { current: presetCurrent, l3: presetL3, empty: () => ({ ...base("Empty map", 2026, [-20, 60, -20, 40]), zones: districts() }) };

// ---------- persistence ----------
export function validate(m) {
  const err = [];
  if (!m || typeof m !== "object") return ["map is not an object"];
  if (m.schema !== SCHEMA) err.push("unsupported schema " + m.schema);
  const t = m.terrain;
  if (!t || !Array.isArray(t.heights) || t.heights.length !== t.w * t.h) err.push("terrain heights do not match w x h");
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
export function migrate(obj) {
  if (obj && obj.schema === SCHEMA) return obj;
  throw new Error("Unknown map schema: " + (obj && obj.schema));
}
// Stable, rounded JSON. Paths also carry their resolved points for other tools.
export function serialize(m) {
  const out = {
    schema: SCHEMA, name: m.name, seed: m.seed, generator: "harness-city-editor",
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
  const err = validate(obj);
  if (err.length) throw new Error("Invalid map: " + err.join("; "));
  return obj;
}
export function clone(m) { return JSON.parse(JSON.stringify(m)); }
