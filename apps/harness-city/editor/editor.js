// Harness City Editor. Edits city-map.json (see map.js and DESIGN.md "Editor").
// Same orthographic isometric camera as the viewer, with 90 degree rotation.
import * as THREE from "three";
import { GLTFLoader } from "three/addons/loaders/GLTFLoader.js";
import { GLTFExporter } from "three/addons/exporters/GLTFExporter.js";
import * as M from "./map.js";

const $ = (id) => document.getElementById(id);
const STORE = "harness-city-editor-map";
const ELEV = 0.82;

// ---------- state ----------
const S = {
  map: null, tool: "select", guided: false, play: true, sel: null,
  chain: null, drag: null, undo: [], redo: [], cursor: null, down: false,
  opt: {
    brush: "raise", radius: 3, strength: 0.06, level: 0,
    treeMode: "paint", treeRadius: 2.5, density: 4, avoid: true, kinds: ["tree-oak", "tree-pine", "tree-fat"],
    roadKind: "street", lanes: 2, curve: false,
    zoneKind: "district", pillar: "verification",
    asset: "house-a", rot: 0, scale: 1,
    vehicle: "truck", altitude: 6,
  },
};
const A = {}; // asset id -> scene
let MANIFEST = {};

// ---------- three setup ----------
const canvas = $("cv"), stage = $("stage");
const renderer = new THREE.WebGLRenderer({ canvas, antialias: true, preserveDrawingBuffer: true });
renderer.setPixelRatio(Math.min(2, window.devicePixelRatio || 1));
renderer.outputColorSpace = THREE.SRGBColorSpace;
renderer.shadowMap.enabled = true;
const scene = new THREE.Scene();
scene.background = new THREE.Color("#cfe0e8");
scene.add(new THREE.HemisphereLight("#f4f8ff", "#8aa77a", 1.35));
const sun = new THREE.DirectionalLight("#fff3dd", 2.3);
sun.castShadow = true; sun.shadow.mapSize.set(4096, 4096); sun.shadow.bias = -0.0004; sun.shadow.normalBias = 0.02;
scene.add(sun, sun.target);
const camera = new THREE.OrthographicCamera(-1, 1, 1, -1, -400, 600);
const view = { az: 45, zoom: 1, target: new THREE.Vector3(), plan: false };
const G = {};
for (const k of ["terrain", "water", "zones", "roads", "rail", "props", "paths", "vehicles", "handles", "cursor"]) { G[k] = new THREE.Group(); G[k].name = k; scene.add(G[k]); }

const matCache = new Map();
const mat = (c, o = {}) => { const k = c + JSON.stringify(o); if (!matCache.has(k)) matCache.set(k, new THREE.MeshStandardMaterial({ color: c, roughness: 0.85, ...o })); return matCache.get(k); };
function clear(g) { for (const c of [...g.children]) { g.remove(c); c.traverse((o) => { if (o.geometry && !o.userData.shared) o.geometry.dispose(); if (o.isSprite) o.material.map?.dispose(); }); } }

// ---------- camera ----------
function extent() { const t = S.map.terrain; return { x0: t.x0, x1: t.x0 + (t.w - 1) * t.step, z0: t.z0, z1: t.z0 + (t.h - 1) * t.step }; }
function homeView() { const e = extent(); view.target.set((e.x0 + e.x1) / 2, 0, (e.z0 + e.z1) / 2); view.zoom = 1; }
function placeCamera() {
  if (!S.map) return;
  const a = (view.az * Math.PI) / 180, d = 120, w = stage.clientWidth || 1, h = stage.clientHeight || 1;
  if (view.plan) { const b = a - Math.PI / 4; camera.position.set(view.target.x, 150, view.target.z); camera.up.set(-Math.sin(b), 0, -Math.cos(b)); }
  else { camera.position.set(view.target.x + Math.sin(a) * d, view.target.y + d * ELEV, view.target.z + Math.cos(a) * d); camera.up.set(0, 1, 0); }
  camera.lookAt(view.target);
  const e = extent(), span = Math.max(e.x1 - e.x0, e.z1 - e.z0), half = (span * (view.plan ? 0.55 : 0.5)) / view.zoom;
  camera.left = (-half * w) / h; camera.right = (half * w) / h; camera.top = half; camera.bottom = -half;
  camera.updateProjectionMatrix();
  sun.position.set(view.target.x + 40, 60, view.target.z + 30); sun.target.position.copy(view.target);
  const sc = sun.shadow.camera, r = span * 0.7; sc.left = -r; sc.right = r; sc.top = r; sc.bottom = -r; sc.far = 300; sc.updateProjectionMatrix();
}
function resize() { renderer.setSize(stage.clientWidth, stage.clientHeight, false); placeCamera(); }
let rotAnim = 0;
function rotate(d) {
  const from = view.az, to = view.az + d, t0 = performance.now();
  const reduce = matchMedia("(prefers-reduced-motion: reduce)").matches;
  cancelAnimationFrame(rotAnim);
  const step = (now) => { const u = reduce ? 1 : Math.min(1, (now - t0) / 380); view.az = from + (to - from) * (u < 0.5 ? 2 * u * u : 1 - Math.pow(-2 * u + 2, 2) / 2); placeCamera(); if (u < 1) rotAnim = requestAnimationFrame(step); else view.az = ((to % 360) + 360) % 360; };
  rotAnim = requestAnimationFrame(step);
}
function panBy(dx, dy) {
  const wpp = (camera.right - camera.left) / stage.clientWidth;
  const right = new THREE.Vector3().setFromMatrixColumn(camera.matrixWorld, 0); right.y = 0; right.normalize();
  const up = new THREE.Vector3().setFromMatrixColumn(camera.matrixWorld, 1); up.y = 0; up.normalize();
  const k = view.plan ? 1 : 1 / Math.sin(Math.atan(ELEV));
  view.target.addScaledVector(right, -dx * wpp).addScaledVector(up, dy * wpp * k);
  placeCamera();
}

// ---------- assets ----------
const PALETTE = [
  ["Nature", (id) => /^(tree|bush|grass|flower|rock|stump)/.test(id)],
  ["Buildings", (id) => /^(bld|house|tower|garage|hangar|tent|fountain|obelisk|column)/.test(id)],
  ["Vehicles", (id) => /(car|suv|taxi|van|truck|ambulance|tractor|digger|sedan)/.test(id)],
  ["Roads and ground", (id) => /^(road|pavement)/.test(id)],
  ["People", (id) => /^mini/.test(id)],
  ["Props", () => true],
];
async function loadAssets() {
  const pack = window.HARNESS_CITY_ASSETS || (await (await fetch("assets/assets.json")).json());
  try { MANIFEST = await (await fetch("assets/manifest.json")).json(); } catch { MANIFEST = {}; }
  const L = new GLTFLoader(), buf = (b64) => { const s = atob(b64), u = new Uint8Array(s.length); for (let i = 0; i < s.length; i++) u[i] = s.charCodeAt(i); return u.buffer; };
  const ids = Object.keys(pack); let n = 0;
  await Promise.all(ids.map((id) => L.parseAsync(buf(pack[id]), "").then((g) => {
    g.scene.traverse((m) => { if (m.isMesh) { m.castShadow = true; m.receiveShadow = true; m.geometry.userData.shared = true; m.userData.shared = true; } });
    A[id] = g.scene; $("loading").textContent = `Loading city assets… ${++n}/${ids.length}`;
  })));
  $("loading").hidden = true;
}
function placeAsset(id) {
  const src = A[id];
  if (!src) { const m = new THREE.Mesh(new THREE.BoxGeometry(0.6, 0.6, 0.6), mat("#c33")); return m; }
  const o = src.clone(); o.traverse((m) => { if (m.isMesh) m.userData.shared = true; }); return o;
}

// ---------- build: terrain ----------
let terrainMesh = null, waterMesh = null;
const C = { bed: new THREE.Color("#a99c7c"), sand: new THREE.Color("#d8c99a"), grass: new THREE.Color("#8fb86a"), grass2: new THREE.Color("#6f9a55"), rock: new THREE.Color("#8d8a80"), snow: new THREE.Color("#f2f4f2") };
function colorFor(h, w, out) {
  if (h < w) return out.copy(C.bed);
  if (h < w + 0.2) return out.copy(C.sand);
  if (h < 1.5) return out.copy(C.grass).lerp(C.grass2, Math.max(0, h) / 1.5);
  if (h < 5) return out.copy(C.grass2).lerp(C.rock, (h - 1.5) / 3.5);
  return out.copy(C.rock).lerp(C.snow, Math.min(1, (h - 5) / 3));
}
function buildTerrain() {
  clear(G.terrain); clear(G.water);
  const t = S.map.terrain, geo = new THREE.BufferGeometry(), n = t.w * t.h;
  const pos = new Float32Array(n * 3), col = new Float32Array(n * 3), idx = [];
  for (let j = 0; j < t.h - 1; j++) for (let i = 0; i < t.w - 1; i++) { const a = j * t.w + i, b = a + 1, c = a + t.w, d = c + 1; idx.push(a, c, b, b, c, d); }
  geo.setAttribute("position", new THREE.BufferAttribute(pos, 3));
  geo.setAttribute("color", new THREE.BufferAttribute(col, 3));
  geo.setIndex(idx);
  terrainMesh = new THREE.Mesh(geo, new THREE.MeshStandardMaterial({ vertexColors: true, roughness: 0.95 }));
  terrainMesh.receiveShadow = true; terrainMesh.userData.pick = { type: "terrain" };
  G.terrain.add(terrainMesh);
  updateTerrain();
  const e = extent();
  waterMesh = new THREE.Mesh(new THREE.PlaneGeometry(e.x1 - e.x0, e.z1 - e.z0), new THREE.MeshStandardMaterial({ color: "#4f8fb8", transparent: true, opacity: 0.72, roughness: 0.3 }));
  waterMesh.rotation.x = -Math.PI / 2; waterMesh.position.set((e.x0 + e.x1) / 2, t.water, (e.z0 + e.z1) / 2);
  G.water.add(waterMesh);
}
function updateTerrain() {
  const t = S.map.terrain, g = terrainMesh.geometry, p = g.attributes.position.array, c = g.attributes.color.array, tmp = new THREE.Color();
  for (let j = 0; j < t.h; j++) for (let i = 0; i < t.w; i++) {
    const k = j * t.w + i, h = t.heights[k];
    p[k * 3] = t.x0 + i * t.step; p[k * 3 + 1] = h; p[k * 3 + 2] = t.z0 + j * t.step;
    colorFor(h, t.water, tmp); c[k * 3] = tmp.r; c[k * 3 + 1] = tmp.g; c[k * 3 + 2] = tmp.b;
  }
  g.attributes.position.needsUpdate = true; g.attributes.color.needsUpdate = true; g.computeVertexNormals(); g.computeBoundingSphere(); g.computeBoundingBox();
  if (waterMesh) waterMesh.position.y = t.water;
}
const hAt = (x, z) => M.heightAt(S.map.terrain, x, z);

// ---------- build: labels ----------
function label(text, sub, color) {
  const cv = document.createElement("canvas"), x = cv.getContext("2d"), f = 26;
  x.font = `600 ${f}px system-ui, sans-serif`;
  const w = Math.ceil(Math.max(x.measureText(text).width, sub ? x.measureText(sub).width * 0.7 : 0)) + 24, h = sub ? 66 : 40;
  cv.width = w; cv.height = h;
  x.fillStyle = color; x.globalAlpha = 0.92; x.beginPath(); x.roundRect(0, 0, w, h, 8); x.fill(); x.globalAlpha = 1;
  x.fillStyle = "#fff"; x.font = `600 ${f}px system-ui, sans-serif`; x.fillText(text, 12, 29);
  if (sub) { x.font = `${Math.round(f * 0.7)}px system-ui, sans-serif`; x.fillText(sub, 12, 56); }
  const tex = new THREE.CanvasTexture(cv); tex.colorSpace = THREE.SRGBColorSpace;
  const s = new THREE.Sprite(new THREE.SpriteMaterial({ map: tex, depthTest: false, transparent: true }));
  s.scale.set(w / 40, h / 40, 1); s.renderOrder = 10; s.userData.label = true;
  return s;
}

// ---------- build: zones ----------
function zoneColor(z) { return z.kind === "district" ? M.PILLAR[z.pillar]?.c || "#888" : (M.ZONE_KINDS[z.kind] || M.ZONE_KINDS.other).c; }
function buildZones() {
  clear(G.zones);
  for (const z of S.map.zones) {
    const w = z.x1 - z.x0, d = z.z1 - z.z0, cx = (z.x0 + z.x1) / 2, cz = (z.z0 + z.z1) / 2;
    const y = Math.max(hAt(z.x0, z.z0), hAt(z.x1, z.z0), hAt(z.x0, z.z1), hAt(z.x1, z.z1), hAt(cx, cz), S.map.terrain.water) + 0.04;
    const selected = S.sel && S.sel.type === "zone" && S.sel.id === z.id;
    const slab = new THREE.Mesh(new THREE.BoxGeometry(w, 0.08, d), new THREE.MeshStandardMaterial({ color: zoneColor(z), transparent: true, opacity: selected ? 0.75 : 0.5 }));
    slab.position.set(cx, y, cz); slab.receiveShadow = true; slab.userData.pick = { type: "zone", id: z.id };
    const edge = new THREE.LineSegments(new THREE.EdgesGeometry(slab.geometry), new THREE.LineBasicMaterial({ color: selected ? "#ffb400" : zoneColor(z) }));
    edge.position.copy(slab.position);
    const kindName = z.kind === "district" ? M.PILLAR[z.pillar]?.n : (M.ZONE_KINDS[z.kind] || {}).n;
    const lab = label(z.label || z.id, kindName && kindName !== z.label ? kindName : "", zoneColor(z));
    lab.position.set(cx, y + 1.2, cz);
    G.zones.add(slab, edge, lab);
  }
}

// ---------- build: roads and rail ----------
function ribbon(points, width, yOf, color, opts = {}) {
  const pos = [], idx = [];
  for (let i = 0; i < points.length; i++) {
    const p = points[i], q = points[Math.min(points.length - 1, i + 1)], o = points[Math.max(0, i - 1)];
    let tx = q[0] - o[0], tz = q[1] - o[1]; const L = Math.hypot(tx, tz) || 1; tx /= L; tz /= L;
    const nx = -tz * width / 2, nz = tx * width / 2, y = yOf(i, p);
    pos.push(p[0] + nx, y, p[1] + nz, p[0] - nx, y, p[1] - nz);
    if (i) { const a = (i - 1) * 2; idx.push(a, a + 2, a + 1, a + 1, a + 2, a + 3); }
  }
  const g = new THREE.BufferGeometry(); g.setAttribute("position", new THREE.Float32BufferAttribute(pos, 3)); g.setIndex(idx); g.computeVertexNormals();
  const m = new THREE.Mesh(g, opts.material || mat(color, opts.mo || {})); m.receiveShadow = true; return m;
}
function deckY(g, e) {
  const A = M.nodeById(g, e.a), B = M.nodeById(g, e.b), w = S.map.terrain.water;
  const ya = Math.max(hAt(A.x, A.z), w + 0.5), yb = Math.max(hAt(B.x, B.z), w + 0.5);
  return (t) => ya + (yb - ya) * t + 0.06;
}
function buildGraph(net) {
  const g = S.map[net], group = G[net]; clear(group);
  const isRail = net === "rail", deg = new Map();
  const hwy = new Set();
  for (const e of g.edges) { deg.set(e.a, Math.max(deg.get(e.a) || 0, e.width || 1)); deg.set(e.b, Math.max(deg.get(e.b) || 0, e.width || 1)); if (e.kind === "highway") { hwy.add(e.a); hwy.add(e.b); } }
  for (const e of g.edges) {
    const pts = M.edgePoints(g, e, 0.35), n = pts.length - 1, sel = S.sel && S.sel.type === "edge" && S.sel.net === net && S.sel.id === e.id;
    const flat = e.bridge ? deckY(g, e) : null;
    const yOf = (i, p) => (flat ? flat(i / n) : hAt(p[0], p[1]) + 0.04);
    let m;
    if (isRail) {
      m = ribbon(pts, 0.78, yOf, sel ? "#ffb400" : "#9c9184");
      for (const off of [-0.18, 0.18]) {
        const rp = pts.map((p, i) => { const q = pts[Math.min(n, i + 1)], o = pts[Math.max(0, i - 1)]; let tx = q[0] - o[0], tz = q[1] - o[1]; const L = Math.hypot(tx, tz) || 1; return [p[0] - (tz / L) * off, p[1] + (tx / L) * off]; });
        group.add(ribbon(rp, 0.05, (i, p) => yOf(i, p) + 0.06, "#b9c1c7", { mo: { metalness: 0.4, roughness: 0.5 } }));
      }
    } else {
      const col = sel ? "#ffb400" : e.kind === "highway" ? "#4a5560" : "#5d646b";
      m = ribbon(pts, e.width || 1, yOf, col, e.tunnel ? { mo: { transparent: true, opacity: 0.35 } } : {});
      if (e.kind === "highway") group.add(ribbon(pts, 0.08, (i, p) => yOf(i, p) + 0.01, "#e8e4d0"));
    }
    m.userData.pick = { type: "edge", net, id: e.id }; group.add(m);
    if (e.bridge) for (let i = 0; i <= n; i += 5) { const p = pts[i], top = yOf(i, p), bot = Math.min(hAt(p[0], p[1]), S.map.terrain.water - 1); const pil = new THREE.Mesh(new THREE.CylinderGeometry(0.12, 0.16, top - bot, 8), mat("#b8b0a2")); pil.position.set(p[0], (top + bot) / 2, p[1]); pil.castShadow = true; group.add(pil); }
  }
  if (!isRail) for (const n of g.nodes) {
    if (!deg.has(n.id)) continue;
    const disc = new THREE.Mesh(new THREE.CircleGeometry(deg.get(n.id) / 2, 24), mat(hwy.has(n.id) ? "#4a5560" : "#5d646b"));
    disc.rotation.x = -Math.PI / 2; disc.position.set(n.x, hAt(n.x, n.z) + 0.035, n.z); disc.receiveShadow = true;
    const onBridge = g.edges.some((e) => e.bridge && (e.a === n.id || e.b === n.id));
    if (onBridge) disc.position.y = Math.max(disc.position.y, S.map.terrain.water + 0.56);
    group.add(disc);
  }
}

// ---------- build: props ----------
function buildProps() {
  clear(G.props);
  for (const p of S.map.props) {
    const o = placeAsset(p.asset); o.position.set(p.x, hAt(p.x, p.z), p.z); o.rotation.y = ((p.rot || 0) * Math.PI) / 180; o.scale.setScalar(p.scale || 1);
    o.userData.pick = { type: "prop", id: p.id };
    if (S.sel && S.sel.type === "prop" && S.sel.id === p.id) { const ring = new THREE.Mesh(new THREE.RingGeometry(0.45, 0.55, 24), new THREE.MeshBasicMaterial({ color: "#ffb400", side: THREE.DoubleSide })); ring.rotation.x = -Math.PI / 2; ring.position.set(p.x, hAt(p.x, p.z) + 0.06, p.z); G.props.add(ring); }
    G.props.add(o);
  }
}

// ---------- build: paths and vehicles ----------
const RUNNERS = [];
function vehicleMesh(kind) {
  if (kind === "car") return placeAsset("sedan");
  if (kind === "truck") return placeAsset("truck");
  if (kind === "bus") return placeAsset("delivery-van");
  const g = new THREE.Group();
  if (kind === "train") { for (let i = 0; i < 3; i++) { const b = new THREE.Mesh(new THREE.BoxGeometry(1.1, 0.42, 0.5), mat(i ? "#e9e2d0" : "#6a5a8c")); b.position.set(-i * 1.2, 0.3, 0); b.castShadow = true; g.add(b); } }
  if (kind === "ship") { const h = new THREE.Mesh(new THREE.BoxGeometry(2.4, 0.4, 0.8), mat("#2c4f6e")); h.position.y = 0.15; const c = new THREE.Mesh(new THREE.BoxGeometry(0.8, 0.5, 0.6), mat("#e9e2d0")); c.position.set(-0.5, 0.6, 0); for (const k of [h, c]) { k.castShadow = true; g.add(k); } for (let i = 0; i < 3; i++) { const box = new THREE.Mesh(new THREE.BoxGeometry(0.4, 0.3, 0.6), mat(["#c9784a", "#2f86c9", "#d9a42a"][i])); box.position.set(0.35 + i * 0.4, 0.5, 0); g.add(box); } }
  if (kind === "plane") { const f = new THREE.Mesh(new THREE.CylinderGeometry(0.18, 0.18, 2, 10), mat("#f2f4f2")); f.rotation.z = Math.PI / 2; const w = new THREE.Mesh(new THREE.BoxGeometry(0.5, 0.05, 2.4), mat("#cfd6dc")); const t = new THREE.Mesh(new THREE.BoxGeometry(0.3, 0.5, 0.05), mat("#2f86c9")); t.position.set(-0.9, 0.3, 0); for (const k of [f, w, t]) { k.castShadow = true; g.add(k); } }
  return g;
}
function smoothFree(pts) {
  if (pts.length < 3) return pts;
  const curve = new THREE.CatmullRomCurve3(pts.map((p) => new THREE.Vector3(p[0], p[1], p[2])), false, "centripetal");
  return curve.getPoints(Math.max(16, pts.length * 12)).map((v) => [v.x, v.y, v.z]);
}
function buildPaths() {
  clear(G.paths); clear(G.vehicles); RUNNERS.length = 0;
  for (const p of S.map.paths) {
    const V = M.VEHICLES[p.vehicle] || M.VEHICLES.car;
    let pts = M.resolvePath(S.map, p);
    if (p.mode === "free") pts = smoothFree(pts);
    if (pts.length < 2) continue;
    const sel = S.sel && S.sel.type === "path" && S.sel.id === p.id;
    const line = new THREE.Line(new THREE.BufferGeometry().setFromPoints(pts.map((q) => new THREE.Vector3(q[0], q[1] + 0.12, q[2]))), new THREE.LineDashedMaterial({ color: sel ? "#ffb400" : V.c, dashSize: 0.5, gapSize: 0.3, depthTest: false }));
    line.computeLineDistances(); line.renderOrder = 5; line.userData.pick = { type: "path", id: p.id }; G.paths.add(line);
    const cum = [0]; for (let i = 1; i < pts.length; i++) cum.push(cum[i - 1] + Math.hypot(pts[i][0] - pts[i - 1][0], pts[i][1] - pts[i - 1][1], pts[i][2] - pts[i - 1][2]));
    const mesh = vehicleMesh(p.vehicle); G.vehicles.add(mesh);
    RUNNERS.push({ p, pts, cum, mesh, speed: p.speed || V.speed, phase: (M.rng(p.id.length * 97 + S.map.seed)() * cum[cum.length - 1]) });
  }
}
function runVehicles(time) {
  for (const r of RUNNERS) {
    const L = r.cum[r.cum.length - 1]; if (!L) continue;
    let s = (r.phase + (S.play ? time * r.speed : 0)) % (r.p.loop === false ? L : 2 * L);
    if (s > L) s = 2 * L - s; // ping-pong for road and rail routes
    let i = 1; while (i < r.cum.length - 1 && r.cum[i] < s) i++;
    const a = r.pts[i - 1], b = r.pts[i], u = (s - r.cum[i - 1]) / (r.cum[i] - r.cum[i - 1] || 1);
    r.mesh.position.set(a[0] + (b[0] - a[0]) * u, a[1] + (b[1] - a[1]) * u, a[2] + (b[2] - a[2]) * u);
    const forward = (r.phase + time * r.speed) % (2 * L) <= L || r.p.loop === false;
    r.mesh.rotation.y = Math.atan2(-(b[2] - a[2]), b[0] - a[0]) + (forward ? 0 : Math.PI);
  }
}

// ---------- handles ----------
function buildHandles() {
  clear(G.handles);
  const show = ["select", "road", "rail", "path", "erase"].includes(S.tool);
  if (!show) return;
  const sph = new THREE.SphereGeometry(0.2, 10, 8); sph.userData.shared = true;
  for (const net of ["roads", "rail"]) {
    if (S.tool === "road" && net !== "roads") continue;
    if (S.tool === "rail" && net !== "rail") continue;
    const g = S.map[net];
    for (const n of g.nodes) { const h = new THREE.Mesh(sph, new THREE.MeshBasicMaterial({ color: net === "rail" ? "#a897d3" : "#ffffff", depthTest: false })); h.position.set(n.x, hAt(n.x, n.z) + 0.25, n.z); h.renderOrder = 8; h.userData.pick = { type: "node", net, id: n.id }; G.handles.add(h); }
    if (S.tool === "select") for (const e of g.edges) if (e.c) { const h = new THREE.Mesh(new THREE.OctahedronGeometry(0.22), new THREE.MeshBasicMaterial({ color: "#ffb400", depthTest: false })); h.position.set(e.c[0], hAt(e.c[0], e.c[1]) + 0.25, e.c[1]); h.renderOrder = 8; h.userData.pick = { type: "ctrl", net, id: e.id }; G.handles.add(h); }
  }
  for (const p of S.map.paths) if (p.mode === "free" && (S.tool === "path" || (S.sel && S.sel.type === "path" && S.sel.id === p.id))) {
    p.points.forEach((q, i) => { const h = new THREE.Mesh(sph, new THREE.MeshBasicMaterial({ color: M.VEHICLES[p.vehicle].c, depthTest: false })); h.position.set(q[0], q[1] + 0.2, q[2]); h.renderOrder = 8; h.userData.pick = { type: "pathpt", id: p.id, i }; G.handles.add(h); });
  }
  if (S.sel && S.sel.type === "zone") {
    const z = S.map.zones.find((q) => q.id === S.sel.id);
    if (z) for (const [cx, cz, corner] of [[z.x0, z.z0, "x0z0"], [z.x1, z.z0, "x1z0"], [z.x0, z.z1, "x0z1"], [z.x1, z.z1, "x1z1"]]) { const h = new THREE.Mesh(new THREE.BoxGeometry(0.4, 0.4, 0.4), new THREE.MeshBasicMaterial({ color: "#ffb400", depthTest: false })); h.position.set(cx, hAt(cx, cz) + 0.3, cz); h.renderOrder = 9; h.userData.pick = { type: "corner", id: z.id, corner }; G.handles.add(h); }
  }
}

function rebuild(parts = "all") {
  const all = parts === "all", has = (k) => all || parts.includes(k);
  if (has("terrain")) buildTerrain();
  if (has("zones")) buildZones();
  if (has("roads")) buildGraph("roads");
  if (has("rail")) buildGraph("rail");
  if (has("props")) buildProps();
  if (has("paths")) buildPaths();
  buildHandles();
  const m = S.map;
  $("counts").textContent = `${m.zones.length} zones · ${m.roads.edges.length} road segments · ${m.rail.edges.length} track segments · ${m.props.length} props · ${m.paths.length} paths`;
  save();
}

// ---------- undo ----------
function snapshot() { return JSON.stringify(S.map); }
function begin() { S.pending = snapshot(); }
function commit(parts) {
  if (S.pending == null) return;
  const now = snapshot();
  if (now !== S.pending) { S.undo.push(S.pending); if (S.undo.length > 60) S.undo.shift(); S.redo.length = 0; }
  S.pending = null; rebuild(parts);
}
function change(parts, fn) { begin(); fn(); commit(parts); }
function undoRedo(from, to) { if (!from.length) return; to.push(snapshot()); S.map = JSON.parse(from.pop()); S.sel = null; S.chain = null; rebuild(); inspect(); }

// ---------- persistence ----------
let saveTimer = 0;
function save() { clearTimeout(saveTimer); saveTimer = setTimeout(() => { try { localStorage.setItem(STORE, snapshot()); } catch { /* storage unavailable */ } }, 400); }
function loadMap(m, keepView = false) {
  S.map = m; S.sel = null; S.chain = null;
  if (!keepView) homeView();
  rebuild(); placeCamera(); inspect();
}
function download(name, blob) { const a = document.createElement("a"); a.href = URL.createObjectURL(blob); a.download = name; document.body.appendChild(a); a.click(); setTimeout(() => { URL.revokeObjectURL(a.href); a.remove(); }, 500); }
function slug() { return (S.map.name || "city").toLowerCase().replace(/[^a-z0-9]+/g, "-").replace(/^-|-$/g, "") || "city"; }
function exportJson() { const text = M.serialize(S.map); download(`${slug()}.city-map.json`, new Blob([text], { type: "application/json" })); msg("Exported the map JSON."); return text; }
function exportRoot() {
  const root = new THREE.Group(); root.name = S.map.name || "Harness City";
  for (const k of ["terrain", "water", "zones", "roads", "rail", "props"]) {
    const c = G[k].clone(true); c.traverse((o) => { if (o.isSprite || o.isLine || o.isLineSegments) o.visible = false; });
    c.children = c.children.filter((o) => !o.isSprite && !o.isLine && !o.isLineSegments); root.add(c);
  }
  return root;
}
function exportGlb() {
  return new Promise((ok, fail) => {
    new GLTFExporter().parse(exportRoot(), (res) => { const blob = new Blob([res], { type: "model/gltf-binary" }); download(`${slug()}.glb`, blob); msg("Exported the GLB scene."); ok(blob.size); }, (e) => { msg("GLB export failed: " + e.message, true); fail(e); }, { binary: true, onlyVisible: true });
  });
}
function exportPng() { G.handles.visible = false; G.cursor.visible = false; renderer.render(scene, camera); const url = renderer.domElement.toDataURL("image/png"); G.handles.visible = true; G.cursor.visible = true; fetch(url).then((r) => r.blob()).then((b) => download(`${slug()}.png`, b)); msg("Exported the PNG view."); return url.length; }
function msg(t, err = false) { const el = $("msg"); el.textContent = t; el.className = err ? "err" : ""; }

// ---------- picking ----------
const ray = new THREE.Raycaster(), ndc = new THREE.Vector2();
function setRay(ev) { const r = canvas.getBoundingClientRect(); ndc.set(((ev.clientX - r.left) / r.width) * 2 - 1, -((ev.clientY - r.top) / r.height) * 2 + 1); ray.setFromCamera(ndc, camera); }
function ground(ev) {
  setRay(ev);
  const hit = ray.intersectObject(terrainMesh, false)[0];
  if (hit) return hit.point;
  const p = new THREE.Vector3(); return ray.ray.intersectPlane(new THREE.Plane(new THREE.Vector3(0, 1, 0), 0), p) ? p : null;
}
function pick(ev, groups) {
  setRay(ev);
  for (const g of groups) {
    const hits = ray.intersectObjects(G[g].children, true);
    for (const h of hits) { let o = h.object; while (o && !o.userData.pick) o = o.parent; if (o && o.userData.pick && o.visible !== false) return o.userData.pick; }
  }
  return null;
}
const snap = (v, s = 1) => (S.guided ? Math.round(v / s) * s : Math.round(v * 1000) / 1000);
function snapAngle(from, x, z) {
  if (!S.guided || !from) return [x, z];
  const dx = x - from.x, dz = z - from.z, L = Math.round(Math.hypot(dx, dz)), a = Math.round(Math.atan2(dz, dx) / (Math.PI / 4)) * (Math.PI / 4);
  return [Math.round((from.x + Math.cos(a) * L) * 2) / 2, Math.round((from.z + Math.sin(a) * L) * 2) / 2];
}

// ---------- tools ----------
const TOOLS = [
  ["select", "Select / move", "1", "Click to select. Drag to move. Drag corners to resize zones. Drag the orange diamonds to bend curves. Delete removes."],
  ["terrain", "Terraform", "2", "Drag to sculpt. Guided snaps the brush to cells and heights to 0.25 steps."],
  ["trees", "Trees", "3", "Drag to paint trees, or switch to erase. Placement is seeded, so it is repeatable."],
  ["road", "Streets", "4", "Click to add points; click a road to join it. Enter or Esc ends the street. Guided snaps to cells and 45 degree steps."],
  ["rail", "Tracks", "5", "Click to add track points; Enter or Esc ends. Curve makes smooth bends."],
  ["zone", "Districts and zones", "6", "Drag a rectangle. A district moves to the new place; each pillar has one district."],
  ["prop", "Place assets", "7", "Pick a model in the palette, click to place. R rotates, [ and ] scale."],
  ["path", "Vehicle paths", "8", "Trucks, cars, buses: click road junctions as stops. Trains: track nodes. Ships and planes: click free points. Enter ends."],
  ["erase", "Erase", "9", "Click an object, a road segment, a node or a path to delete it."],
];
function setTool(t) {
  finishChain(); S.tool = t;
  for (const b of $("tools").children) b.setAttribute("aria-pressed", String(b.dataset.tool === t));
  $("hint").textContent = TOOLS.find((x) => x[0] === t)[3];
  renderOpts(); buildHandles(); updateCursor();
}
function finishChain() {
  if (S.chain) { S.chain = null; commit(S.tool === "rail" ? ["rail"] : S.tool === "path" ? ["paths"] : ["roads", "paths"]); }
  clear(G.cursor);
}

// graph drawing (roads and rail)
function graphClick(net, pt) {
  const g = S.map[net];
  if (!S.chain) { begin(); S.chain = { net, last: null, prevC: null }; }
  const last = S.chain.last ? M.nodeById(g, S.chain.last) : null;
  let [x, z] = S.guided ? snapAngle(last, snap(pt.x, 0.5), snap(pt.z, 0.5)) : [pt.x, pt.z];
  let node = M.nearestNode(g, x, z, S.guided ? 0.6 : 0.8);
  if (!node) {
    const ne = M.nearestEdge(g, x, z, net === "rail" ? 0.45 : 0.6);
    node = ne ? M.splitEdge(g, ne.edge, x, z) : M.addNode(g, x, z, net === "rail" ? "r" : "n");
  }
  if (last && node.id !== last.id) {
    const props = net === "rail" ? { kind: "track" } : { kind: S.opt.roadKind, lanes: S.opt.lanes, width: S.opt.roadKind === "highway" ? Math.max(3, S.opt.lanes) : Math.max(1, S.opt.lanes / 2) };
    const e = M.addEdge(g, last.id, node.id, props, net === "rail" ? "t" : "e");
    if (e && S.opt.curve && S.chain.prevC) { e.c = [2 * last.x - S.chain.prevC[0], 2 * last.z - S.chain.prevC[1]]; }
    if (e && S.opt.curve && !S.chain.prevC) e.c = [(last.x + node.x) / 2, (last.z + node.z) / 2];
    S.chain.prevC = e && e.c ? e.c : [(last.x + node.x) / 2, (last.z + node.z) / 2];
    if (e && net === "roads") { const pts = M.edgePoints(g, e, 0.5); if (pts.some((p) => hAt(p[0], p[1]) < S.map.terrain.water)) e.bridge = true; }
  }
  S.chain.last = node.id;
  buildGraph(net); buildHandles();
}
function pathClick(ev, pt) {
  const V = M.VEHICLES[S.opt.vehicle];
  if (!S.chain) {
    begin();
    const id = "v" + (Math.max(0, ...S.map.paths.map((p) => Number(String(p.id).slice(1)) || 0)) + 1);
    const p = { id, vehicle: S.opt.vehicle, mode: V.net === "free" ? "free" : V.net === "rail" ? "rail" : "road", speed: V.speed, loop: true };
    if (p.mode === "free") p.points = []; else p.stops = [];
    S.map.paths.push(p); S.chain = { path: id };
  }
  const p = S.map.paths.find((q) => q.id === S.chain.path);
  if (p.mode === "free") {
    const y = p.vehicle === "ship" ? S.map.terrain.water : Math.max(hAt(pt.x, pt.z) + 0.5, S.opt.altitude);
    p.points.push([snap(pt.x, 0.5), Math.round(y * 100) / 100, snap(pt.z, 0.5)]);
  } else {
    const g = p.mode === "rail" ? S.map.rail : S.map.roads, n = M.nearestNode(g, pt.x, pt.z, 2.5);
    if (!n) { msg(`No ${p.mode === "rail" ? "track" : "road"} node near here.`, true); return; }
    if (p.stops[p.stops.length - 1] !== n.id) p.stops.push(n.id);
    if (p.stops.length > 1 && !M.shortestPath(g, p.stops[p.stops.length - 2], n.id)) msg("These stops are not connected.", true); else msg("");
  }
  buildPaths(); buildHandles();
}
function brushStep(pt, dt) {
  const t = S.map.terrain, o = S.opt, x = S.guided ? Math.round(pt.x) : pt.x, z = S.guided ? Math.round(pt.z) : pt.z;
  const kind = o.brush === "water" ? null : o.brush;
  if (o.brush === "water") { t.water = Math.round(o.level * 100) / 100; updateTerrain(); return; }
  const target = o.brush === "flatten" ? (S.flatTo ??= hAt(x, z)) : o.level;
  M.applyBrush(t, kind, x, z, o.radius, o.strength * Math.min(3, dt * 60), target, S.guided ? 0.25 : 0);
  updateTerrain();
}
function treeStep(pt) {
  const o = S.opt, m = S.map;
  if (S.lastStamp && Math.hypot(pt.x - S.lastStamp.x, pt.z - S.lastStamp.z) < o.treeRadius * 0.6) return;
  S.lastStamp = { x: pt.x, z: pt.z };
  if (o.treeMode === "erase") {
    const before = m.props.length;
    m.props = m.props.filter((p) => !(/^(tree|bush)/.test(p.asset) && Math.hypot(p.x - pt.x, p.z - pt.z) <= o.treeRadius));
    if (m.props.length !== before) buildProps();
    return;
  }
  m.scatter = (m.scatter || 0) + 1;
  const r = M.rng(m.seed * 7919 + m.scatter);
  const roadNear = (x, z) => ["roads", "rail"].some((net) => { const ne = M.nearestEdge(m[net], x, z, 1.4); if (!ne) return false; const w = net === "rail" ? 0.8 : ne.edge.width || 1; return ne.d < w / 2 + 0.4; });
  const inZone = (x, z) => m.zones.some((q) => x >= q.x0 && x <= q.x1 && z >= q.z0 && z <= q.z1);
  for (let k = 0; k < o.density; k++) {
    const a = r() * Math.PI * 2, d = Math.sqrt(r()) * o.treeRadius, x = pt.x + Math.cos(a) * d, z = pt.z + Math.sin(a) * d;
    const kind = o.kinds[Math.floor(r() * o.kinds.length)] || "tree-oak", rot = Math.round(r() * 360), sc = Math.round((0.8 + r() * 0.5) * 100) / 100;
    if (hAt(x, z) < m.terrain.water + 0.15 || roadNear(x, z) || (o.avoid && inZone(x, z))) continue;
    if (m.props.some((p) => Math.hypot(p.x - x, p.z - z) < 0.45)) continue;
    const id = "p" + (Math.max(0, ...m.props.map((p) => Number(String(p.id).slice(1)) || 0)) + 1);
    m.props.push({ id, asset: kind, x: Math.round(x * 1000) / 1000, z: Math.round(z * 1000) / 1000, rot, scale: sc });
  }
  buildProps();
}
function deleteSel(target = S.sel) {
  if (!target) return;
  change("all", () => {
    const m = S.map;
    if (target.type === "zone") { const z = m.zones.find((q) => q.id === target.id); if (z && z.kind === "district") { msg("Districts cannot be deleted; each pillar keeps one district. Move or resize it instead.", true); return; } m.zones = m.zones.filter((q) => q.id !== target.id); }
    if (target.type === "prop") m.props = m.props.filter((p) => p.id !== target.id);
    if (target.type === "edge") M.removeEdge(m[target.net], target.id);
    if (target.type === "node") M.removeNode(m[target.net], target.id);
    if (target.type === "path") m.paths = m.paths.filter((p) => p.id !== target.id);
    if (target.type === "pathpt") { const p = m.paths.find((q) => q.id === target.id); p.points.splice(target.i, 1); if (p.points.length < 2) m.paths = m.paths.filter((q) => q !== p); }
    for (const p of m.paths) if (p.stops) { const g = p.mode === "rail" ? m.rail : m.roads; p.stops = p.stops.filter((s) => M.nodeById(g, s)); }
    S.sel = null;
  });
  inspect();
}

// ---------- pointer ----------
let panning = null;
canvas.addEventListener("contextmenu", (e) => e.preventDefault());
canvas.addEventListener("pointerdown", (ev) => {
  canvas.setPointerCapture(ev.pointerId);
  if (ev.button === 1 || ev.button === 2 || S.space) {
    if (ev.button === 2 && S.chain) { finishChain(); return; }
    panning = { x: ev.clientX, y: ev.clientY }; return;
  }
  const pt = ground(ev); if (!pt) return;
  S.down = true; S.lastT = performance.now(); S.flatTo = null; S.lastStamp = null;
  const t = S.tool;
  if (t === "select") {
    const hit = pick(ev, ["handles", "vehicles", "props", "paths", "zones", "roads", "rail"]);
    if (hit && ["node", "ctrl", "pathpt", "corner"].includes(hit.type)) { begin(); S.drag = { hit, start: pt.clone() }; return; }
    S.sel = hit && hit.type !== "terrain" ? hit : null;
    if (S.sel) { begin(); S.drag = { hit: S.sel, start: pt.clone(), orig: JSON.parse(JSON.stringify(itemOf(S.sel) || {})) }; }
    rebuild(["zones", "roads", "rail", "props", "paths"]); inspect(); return;
  }
  if (t === "terrain" || t === "trees") { begin(); if (t === "terrain") brushStep(pt, 1 / 60); else treeStep(pt); return; }
  if (t === "road") return graphClick("roads", pt);
  if (t === "rail") return graphClick("rail", pt);
  if (t === "path") return pathClick(ev, pt);
  if (t === "zone") { begin(); S.drag = { zone: true, start: [snap(pt.x), snap(pt.z)] }; return; }
  if (t === "prop") {
    change(["props"], () => { const id = "p" + (Math.max(0, ...S.map.props.map((p) => Number(String(p.id).slice(1)) || 0)) + 1); S.map.props.push({ id, asset: S.opt.asset, x: snap(pt.x, 0.5), z: snap(pt.z, 0.5), rot: S.opt.rot, scale: S.opt.scale }); });
    return;
  }
  if (t === "erase") { const hit = pick(ev, ["handles", "props", "paths", "zones", "roads", "rail"]); if (hit) deleteSel(hit); }
});
canvas.addEventListener("pointermove", (ev) => {
  if (panning) { panBy(ev.clientX - panning.x, ev.clientY - panning.y); panning = { x: ev.clientX, y: ev.clientY }; return; }
  const pt = ground(ev); S.cursor = pt;
  if (pt) $("pos").textContent = `x ${pt.x.toFixed(1)}  z ${pt.z.toFixed(1)}  height ${hAt(pt.x, pt.z).toFixed(2)}`;
  updateCursor();
  if (!S.down || !pt) return;
  const now = performance.now(), dt = (now - S.lastT) / 1000; S.lastT = now;
  if (S.tool === "terrain") return brushStep(pt, dt);
  if (S.tool === "trees") return treeStep(pt);
  if (S.drag) dragTo(pt);
});
canvas.addEventListener("pointerup", () => {
  if (panning) { panning = null; return; }
  if (!S.down) return;
  S.down = false;
  if (S.tool === "terrain") { commit("all"); return; }
  if (S.tool === "trees") { commit(["props"]); return; }
  if (S.drag && S.drag.zone) {
    const d = S.drag, [x0, z0] = d.start, [x1, z1] = d.end || d.start;
    if (Math.abs(x1 - x0) >= 1 && Math.abs(z1 - z0) >= 1) {
      const r = { x0: Math.min(x0, x1), x1: Math.max(x0, x1), z0: Math.min(z0, z1), z1: Math.max(z0, z1) };
      if (S.opt.zoneKind === "district") { const z = S.map.zones.find((q) => q.kind === "district" && q.pillar === S.opt.pillar); Object.assign(z, r); S.sel = { type: "zone", id: z.id }; }
      else { const k = S.opt.zoneKind, id = k + "-" + (S.map.zones.filter((q) => q.kind === k).length + 1); S.map.zones.push({ id, kind: k, label: M.ZONE_KINDS[k].n, goal: "", ...r }); S.sel = { type: "zone", id }; }
    }
    S.drag = null; clear(G.cursor); commit(["zones"]); inspect(); return;
  }
  if (S.drag) { S.drag = null; commit("all"); inspect(); }
});
canvas.addEventListener("wheel", (ev) => { ev.preventDefault(); view.zoom = Math.max(0.35, Math.min(12, view.zoom * (ev.deltaY < 0 ? 1.12 : 1 / 1.12))); placeCamera(); }, { passive: false });
canvas.addEventListener("dblclick", () => finishChain());

function itemOf(sel) {
  const m = S.map;
  if (sel.type === "zone" || sel.type === "corner") return m.zones.find((q) => q.id === sel.id);
  if (sel.type === "prop") return m.props.find((q) => q.id === sel.id);
  if (sel.type === "edge" || sel.type === "ctrl") return m[sel.net].edges.find((q) => q.id === sel.id);
  if (sel.type === "node") return M.nodeById(m[sel.net], sel.id);
  if (sel.type === "path" || sel.type === "pathpt") return m.paths.find((q) => q.id === sel.id);
  return null;
}
function dragTo(pt) {
  const d = S.drag, h = d.hit;
  if (d.zone) {
    d.end = [snap(pt.x), snap(pt.z)]; clear(G.cursor);
    const [x0, z0] = d.start, [x1, z1] = d.end, w = Math.abs(x1 - x0), dd = Math.abs(z1 - z0);
    if (w > 0 && dd > 0) { const b = new THREE.Mesh(new THREE.BoxGeometry(w, 0.1, dd), new THREE.MeshBasicMaterial({ color: "#ffb400", transparent: true, opacity: 0.45 })); b.position.set((x0 + x1) / 2, hAt((x0 + x1) / 2, (z0 + z1) / 2) + 0.1, (z0 + z1) / 2); G.cursor.add(b); }
    return;
  }
  const it = itemOf(h); if (!it) return;
  const dx = pt.x - d.start.x, dz = pt.z - d.start.z;
  if (h.type === "zone") { const o = d.orig, sx = snap(o.x0 + dx) - o.x0, sz = snap(o.z0 + dz) - o.z0; Object.assign(it, { x0: o.x0 + sx, x1: o.x1 + sx, z0: o.z0 + sz, z1: o.z1 + sz }); buildZones(); }
  else if (h.type === "corner") { const c = h.corner, x = snap(pt.x), z = snap(pt.z); if (c.includes("x0")) it.x0 = Math.min(x, it.x1 - 1); else it.x1 = Math.max(x, it.x0 + 1); if (c.includes("z0")) it.z0 = Math.min(z, it.z1 - 1); else it.z1 = Math.max(z, it.z0 + 1); buildZones(); }
  else if (h.type === "prop") { it.x = snap(d.orig.x + dx, 0.5); it.z = snap(d.orig.z + dz, 0.5); buildProps(); }
  else if (h.type === "node") { it.x = snap(pt.x, 0.5); it.z = snap(pt.z, 0.5); buildGraph(h.net); buildPaths(); }
  else if (h.type === "ctrl") { it.c = [snap(pt.x, 0.5), snap(pt.z, 0.5)]; buildGraph(h.net); buildPaths(); }
  else if (h.type === "pathpt") { const q = it.points[h.i]; q[0] = snap(pt.x, 0.5); q[2] = snap(pt.z, 0.5); buildPaths(); }
  else if (h.type === "edge") { return; }
  buildHandles();
}
function updateCursor() {
  if (S.drag && S.drag.zone) return;
  clear(G.cursor); const pt = S.cursor; if (!pt) return;
  const ringAt = (r, color) => { const ring = new THREE.Mesh(new THREE.RingGeometry(r - 0.08, r, 48), new THREE.MeshBasicMaterial({ color, side: THREE.DoubleSide, depthTest: false, transparent: true, opacity: 0.9 })); ring.rotation.x = -Math.PI / 2; ring.position.set(S.guided ? Math.round(pt.x) : pt.x, hAt(pt.x, pt.z) + 0.1, S.guided ? Math.round(pt.z) : pt.z); ring.renderOrder = 9; G.cursor.add(ring); };
  if (S.tool === "terrain") ringAt(S.opt.radius, "#ffb400");
  if (S.tool === "trees") ringAt(S.opt.treeRadius, S.opt.treeMode === "erase" ? "#b3261e" : "#3f8f3a");
  if ((S.tool === "road" || S.tool === "rail") && S.chain && S.chain.last) {
    const g = S.map[S.chain.net], a = M.nodeById(g, S.chain.last), [x, z] = S.guided ? snapAngle(a, snap(pt.x, 0.5), snap(pt.z, 0.5)) : [pt.x, pt.z];
    const line = new THREE.Line(new THREE.BufferGeometry().setFromPoints([new THREE.Vector3(a.x, hAt(a.x, a.z) + 0.2, a.z), new THREE.Vector3(x, hAt(x, z) + 0.2, z)]), new THREE.LineBasicMaterial({ color: "#ffb400", depthTest: false }));
    line.renderOrder = 9; G.cursor.add(line);
  }
  if (S.tool === "prop" && A[S.opt.asset]) { const o = placeAsset(S.opt.asset); o.position.set(snap(pt.x, 0.5), hAt(pt.x, pt.z), snap(pt.z, 0.5)); o.rotation.y = (S.opt.rot * Math.PI) / 180; o.scale.setScalar(S.opt.scale); o.traverse((m) => { if (m.isMesh) { m.material = m.material.clone(); m.material.transparent = true; m.material.opacity = 0.55; } }); G.cursor.add(o); }
}

// ---------- panels ----------
const h = (tag, attrs = {}, kids = []) => { const e = document.createElement(tag); for (const [k, v] of Object.entries(attrs)) { if (k === "on") for (const [ev, fn] of Object.entries(v)) e.addEventListener(ev, fn); else if (k === "text") e.textContent = v; else if (v !== undefined && v !== false) e.setAttribute(k, v === true ? "" : v); } for (const c of [].concat(kids)) if (c) e.append(c); return e; };
function field(lbl, input) { return h("div", { class: "row" }, [h("label", { text: lbl }), input]); }
function num(id, value, step, onInput, min, max) { const i = h("input", { id, type: "number", step, value, min, max }); i.addEventListener("input", () => { const v = Number(i.value); if (Number.isFinite(v)) onInput(v); }); return i; }
function sel(id, value, options, onChange) { const s = h("select", { id }); for (const [v, t] of options) s.append(h("option", { value: v, text: t, selected: v === value })); s.addEventListener("change", () => onChange(s.value)); return s; }
function check(id, value, text, onChange) { const i = h("input", { id, type: "checkbox", checked: value }); i.addEventListener("change", () => onChange(i.checked)); return h("div", { class: "row chk" }, [i, h("label", { for: id, text: text.trim() })]); }
function renderOpts() {
  const o = S.opt, box = $("opts"); box.replaceChildren(); $("optTitle").textContent = TOOLS.find((x) => x[0] === S.tool)[1];
  if (S.tool === "terrain") {
    box.append(field("Brush", sel("o-brush", o.brush, [["raise", "Raise"], ["lower", "Lower"], ["flatten", "Flatten"], ["smooth", "Smooth"], ["level", "Set height"], ["water", "Water level"]], (v) => { o.brush = v; renderOpts(); })));
    box.append(field("Radius", num("o-radius", o.radius, 0.5, (v) => { o.radius = Math.max(0.5, v); updateCursor(); }, 0.5, 20)));
    box.append(field("Strength", num("o-strength", o.strength, 0.01, (v) => (o.strength = v), 0.01, 1)));
    if (o.brush === "level" || o.brush === "water") box.append(field(o.brush === "water" ? "Water" : "Height", num("o-level", o.brush === "water" ? S.map.terrain.water : o.level, 0.05, (v) => (o.level = v), -4, 14)));
  }
  if (S.tool === "trees") {
    box.append(field("Mode", sel("o-tmode", o.treeMode, [["paint", "Paint"], ["erase", "Erase"]], (v) => { o.treeMode = v; updateCursor(); })));
    box.append(field("Radius", num("o-tradius", o.treeRadius, 0.5, (v) => { o.treeRadius = Math.max(0.5, v); updateCursor(); }, 0.5, 15)));
    box.append(field("Per stamp", num("o-density", o.density, 1, (v) => (o.density = Math.max(1, Math.round(v))), 1, 30)));
    box.append(check("o-avoid", o.avoid, " Keep out of zones and districts", (v) => (o.avoid = v)));
    for (const k of ["tree-oak", "tree-pine", "tree-fat", "bush", "bush-large"]) box.append(check("o-k-" + k, o.kinds.includes(k), " " + k, (v) => { o.kinds = v ? [...new Set([...o.kinds, k])] : o.kinds.filter((x) => x !== k); }));
  }
  if (S.tool === "road") {
    box.append(field("Kind", sel("o-rkind", o.roadKind, [["street", "Street"], ["highway", "Highway"]], (v) => { o.roadKind = v; o.lanes = v === "highway" ? 6 : 2; renderOpts(); })));
    box.append(field("Lanes", num("o-lanes", o.lanes, 1, (v) => (o.lanes = Math.max(1, Math.round(v))), 1, 8)));
  }
  if (S.tool === "road" || S.tool === "rail") box.append(check("o-curve", o.curve, " Curve (smooth bends between points)", (v) => (o.curve = v)));
  if (S.tool === "zone") {
    box.append(field("Kind", sel("o-zkind", o.zoneKind, [["district", "District (pillar)"], ...Object.entries(M.ZONE_KINDS).map(([k, v]) => [k, v.n])], (v) => { o.zoneKind = v; renderOpts(); })));
    if (o.zoneKind === "district") box.append(field("Pillar", sel("o-pillar", o.pillar, M.PILLARS.map((p) => [p.k, p.n]), (v) => (o.pillar = v))));
  }
  if (S.tool === "prop") {
    box.append(h("p", { class: "small", text: "Selected model: " + o.asset }));
    box.append(field("Rotation", num("o-rot", o.rot, 15, (v) => { o.rot = v; updateCursor(); }, -360, 360)));
    box.append(field("Scale", num("o-scale", o.scale, 0.1, (v) => { o.scale = Math.max(0.1, v); updateCursor(); }, 0.1, 10)));
  }
  if (S.tool === "path") {
    box.append(field("Vehicle", sel("o-veh", o.vehicle, Object.entries(M.VEHICLES).map(([k, v]) => [k, `${v.n} (${v.net === "free" ? "free" : v.net})`]), (v) => { finishChain(); o.vehicle = v; renderOpts(); })));
    if (o.vehicle === "plane") box.append(field("Altitude", num("o-alt", o.altitude, 0.5, (v) => (o.altitude = v), 0, 30)));
    box.append(h("button", { id: "o-endpath", text: "End path", on: { click: () => finishChain() } }));
  }
  if (S.tool === "select" || S.tool === "erase" || !box.childElementCount) box.append(h("p", { class: "small", text: TOOLS.find((x) => x[0] === S.tool)[3] }));
}
function inspect() {
  const box = $("insp"); box.replaceChildren();
  const it = S.sel && itemOf(S.sel);
  if (!it) { box.append(h("p", { class: "small", text: "Nothing selected. Use Select and click an object." })); return; }
  const set = (parts, fn) => change(parts, fn);
  const t = S.sel.type;
  if (t === "zone") {
    if (it.kind === "district") {
      const p = M.PILLAR[it.pillar];
      box.append(h("p", { class: "small", text: `District for the pillar ${p.n}. Its level and score come from the audit, not from the editor.` }));
    } else box.append(field("Kind", sel("i-kind", it.kind, Object.entries(M.ZONE_KINDS).map(([k, v]) => [k, v.n]), (v) => set(["zones"], () => (it.kind = v)))));
    const lab = h("input", { id: "i-label", type: "text", value: it.label || "" }); lab.addEventListener("change", () => set(["zones"], () => (it.label = lab.value)));
    const goal = h("input", { id: "i-goal", type: "text", value: it.goal || "" }); goal.addEventListener("change", () => set(["zones"], () => (it.goal = goal.value)));
    box.append(field("Label", lab), field("Main goal", goal));
    for (const k of ["x0", "x1", "z0", "z1"]) box.append(field(k, num("i-" + k, it[k], 0.5, (v) => set(["zones"], () => (it[k] = v)))));
  }
  if (t === "prop") {
    box.append(field("Model", sel("i-asset", it.asset, Object.keys(A).sort().map((k) => [k, k]), (v) => set(["props"], () => (it.asset = v)))));
    for (const [k, st] of [["x", 0.5], ["z", 0.5], ["rot", 15], ["scale", 0.1]]) box.append(field(k, num("i-" + k, it[k] ?? (k === "scale" ? 1 : 0), st, (v) => set(["props"], () => (it[k] = v)))));
  }
  if (t === "edge") {
    box.append(h("p", { class: "small", text: `${S.sel.net === "rail" ? "Track" : "Road"} segment ${it.id}` }));
    if (S.sel.net === "roads") {
      box.append(field("Kind", sel("i-ekind", it.kind || "street", [["street", "Street"], ["highway", "Highway"]], (v) => set(["roads"], () => (it.kind = v)))));
      box.append(field("Lanes", num("i-lanes", it.lanes || 2, 1, (v) => set(["roads"], () => (it.lanes = v)), 1, 8)));
      box.append(field("Width", num("i-width", it.width || 1, 0.25, (v) => set(["roads"], () => (it.width = v)), 0.5, 10)));
      box.append(check("i-oneway", !!it.oneway, " One way (a to b)", (v) => set(["roads", "paths"], () => (it.oneway = v || undefined))));
    }
    box.append(check("i-bridge", !!it.bridge, " Bridge on pillars", (v) => set([S.sel.net], () => (it.bridge = v || undefined))));
    box.append(check("i-tunnel", !!it.tunnel, " Tunnel", (v) => set([S.sel.net], () => (it.tunnel = v || undefined))));
    box.append(check("i-curve", !!it.c, " Curved (drag the diamond)", (v) => set([S.sel.net], () => { if (v) { const a = M.nodeById(S.map[S.sel.net], it.a), b = M.nodeById(S.map[S.sel.net], it.b); it.c = [(a.x + b.x) / 2 + (b.z - a.z) * 0.25, (a.z + b.z) / 2 - (b.x - a.x) * 0.25]; } else delete it.c; })));
  }
  if (t === "path") {
    box.append(field("Vehicle", sel("i-veh", it.vehicle, Object.entries(M.VEHICLES).filter(([, v]) => (v.net === "free") === (it.mode === "free") && (it.mode !== "rail" || v.net === "rail")).map(([k, v]) => [k, v.n]), (v) => set(["paths"], () => (it.vehicle = v)))));
    box.append(field("Speed", num("i-speed", it.speed, 0.1, (v) => set(["paths"], () => (it.speed = v)), 0.1, 20)));
    box.append(check("i-loop", it.loop !== false, " Return trip", (v) => set(["paths"], () => (it.loop = v))));
    box.append(h("p", { class: "small", text: it.mode === "free" ? `${it.points.length} free points` : `Stops: ${it.stops.join(" → ")}` }));
  }
  if (t === "node") box.append(h("p", { class: "small", text: `Junction ${it.id} at ${it.x}, ${it.z}` }));
  box.append(h("button", { id: "i-delete", text: "Delete", on: { click: () => deleteSel() } }));
}
function renderPalette() {
  const box = $("pal"); box.replaceChildren();
  const used = new Set(), ids = Object.keys(A).sort();
  for (const [name, test] of PALETTE) {
    const group = ids.filter((id) => !used.has(id) && test(id)); if (!group.length) continue;
    box.append(h("h3", { text: `${name} (${group.length})` }));
    for (const id of group) { used.add(id); box.append(h("button", { "data-asset": id, title: MANIFEST[id] ? `${id}, size ${MANIFEST[id].size.join(" x ")}` : id, "aria-pressed": String(S.opt.asset === id), text: id, on: { click: () => { S.opt.asset = id; setTool("prop"); renderPalette(); } } })); }
  }
  box.append(h("p", { class: "small", text: "These are the models of the current map. Other CC0 kits appear here after they are imported with a NOTICE entry." }));
}

// ---------- keyboard and buttons ----------
addEventListener("keydown", (ev) => {
  if (ev.target.closest && ev.target.closest("input,select,textarea")) return;
  const k = ev.key;
  if ((ev.ctrlKey || ev.metaKey) && k.toLowerCase() === "z") { ev.preventDefault(); ev.shiftKey ? undoRedo(S.redo, S.undo) : undoRedo(S.undo, S.redo); return; }
  if ((ev.ctrlKey || ev.metaKey) && k.toLowerCase() === "y") { ev.preventDefault(); undoRedo(S.redo, S.undo); return; }
  if (k === " ") { S.space = true; ev.preventDefault(); return; }
  if (k === "Escape" || k === "Enter") return finishChain();
  if (k === "Delete" || k === "Backspace") return deleteSel();
  if (/^[1-9]$/.test(k)) return setTool(TOOLS[Number(k) - 1][0]);
  if (k === "g" || k === "G") return toggleGuided();
  if (k === "q" || k === "Q") return rotate(-90);
  if (k === "e" || k === "E") return rotate(90);
  if (k === "p" || k === "P") return togglePlan();
  if (k === "r" || k === "R") { S.opt.rot = (S.opt.rot + (S.guided ? 90 : 15)) % 360; renderOpts(); updateCursor(); return; }
  if (k === "[" || k === "]") { S.opt.scale = Math.max(0.1, Math.round((S.opt.scale + (k === "]" ? 0.1 : -0.1)) * 10) / 10); renderOpts(); updateCursor(); return; }
  const pan = { ArrowLeft: [40, 0], ArrowRight: [-40, 0], ArrowUp: [0, 40], ArrowDown: [0, -40] }[k];
  if (pan) { ev.preventDefault(); panBy(...pan); }
});
addEventListener("keyup", (ev) => { if (ev.key === " ") S.space = false; });
function toggleGuided() { S.guided = !S.guided; $("guided").setAttribute("aria-pressed", String(S.guided)); updateCursor(); }
function togglePlan() { view.plan = !view.plan; $("plan").setAttribute("aria-pressed", String(view.plan)); placeCamera(); }
$("guided").onclick = toggleGuided; $("plan").onclick = togglePlan;
$("rotL").onclick = () => rotate(-90); $("rotR").onclick = () => rotate(90);
$("undo").onclick = () => undoRedo(S.undo, S.redo); $("redo").onclick = () => undoRedo(S.redo, S.undo);
$("play").onclick = () => { S.play = !S.play; $("play").setAttribute("aria-pressed", String(S.play)); };
$("new").onclick = () => { begin(); S.map = M.PRESETS[$("preset").value](); commit("all"); homeView(); placeCamera(); inspect(); msg("Started from: " + S.map.name); };
$("import").onclick = () => $("file").click();
$("file").onchange = async () => { const f = $("file").files[0]; if (!f) return; try { const m = M.deserialize(await f.text()); begin(); S.map = m; commit("all"); homeView(); placeCamera(); msg("Imported " + f.name); } catch (e) { msg(e.message, true); } $("file").value = ""; };
$("exJson").onclick = exportJson; $("exGlb").onclick = () => exportGlb().catch(() => {}); $("exPng").onclick = exportPng;
for (const [id, name, key] of TOOLS) $("tools").append(h("button", { "data-tool": id, "aria-pressed": "false", on: { click: () => setTool(id) } }, [document.createTextNode(name), h("kbd", { text: key })]));
addEventListener("resize", resize);

// ---------- start ----------
let last = performance.now(), clock = 0, visible = true;
document.addEventListener("visibilitychange", () => (visible = !document.hidden));
function frame(now) {
  const dt = Math.min(0.1, (now - last) / 1000); last = now; if (visible) clock += dt;
  if (S.down && S.tool === "terrain" && S.cursor && !panning) brushStep(S.cursor, dt);
  runVehicles(clock); renderer.render(scene, camera); requestAnimationFrame(frame);
}
async function start() {
  await loadAssets();
  const q = new URLSearchParams(location.search);
  let m = null;
  if (q.get("map")) { try { m = M.deserialize(await (await fetch(q.get("map"))).text()); } catch (e) { msg(e.message, true); } }
  if (!m && q.get("preset") && M.PRESETS[q.get("preset")]) m = M.PRESETS[q.get("preset")]();
  if (!m && !q.has("fresh")) { try { const s = localStorage.getItem(STORE); if (s) m = M.deserialize(s); } catch { m = null; } }
  if (!m) m = M.presetCurrent();
  $("preset").value = q.get("preset") || "current";
  resize(); loadMap(m); renderPalette(); setTool("select");
  requestAnimationFrame(frame);
}
window.__editor = {
  ready: start(),
  get map() { return S.map; }, get state() { return S; }, view,
  serialize: () => M.serialize(S.map), load: (text) => loadMap(M.deserialize(text)),
  setTool, rotate, exportJson, exportGlb, exportPng, toggleGuided, togglePlan, finishChain,
  undo: () => undoRedo(S.undo, S.redo), redo: () => undoRedo(S.redo, S.undo),
  screenOf: (x, z) => { const v = new THREE.Vector3(x, hAt(x, z), z).project(camera), r = canvas.getBoundingClientRect(); return { x: r.left + ((v.x + 1) / 2) * r.width, y: r.top + ((1 - v.y) / 2) * r.height }; },
};
