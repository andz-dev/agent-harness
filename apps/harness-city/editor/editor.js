// Harness City Editor. Edits city-map.json (see map.js and DESIGN.md "Editor").
// The city itself is drawn by the viewer (index.html?embed) in a frame, with its own builders
// and assets. The editor changes the viewer's layout and adds its own layers to the same scene.
import * as M from "./map.js";

const $ = (id) => document.getElementById(id);
const STORE = "harness-city-editor-map";
const ELEV = 0.82;
let THREE, host, canvas, frameWin, exporterMod = null;

// ---------- state ----------
const S = {
  map: null, tool: "select", guided: false, play: true, sel: null,
  chain: null, drag: null, undo: [], redo: [], cursor: null, down: false, space: false,
  cells: new Set(),
  opt: {
    brush: "raise", radius: 3, strength: 0.06, level: 0,
    treeMode: "paint", treeRadius: 2.5, density: 4, avoid: true, kinds: ["tree-pine", "tree-oak", "tree-fat"],
    roadMode: "tiles", roadKind: "street", lanes: 2, curve: false,
    zoneKind: "district", pillar: "verification",
    asset: "house-a", rot: 0, scale: 1,
    vehicle: "truck", altitude: 6,
  },
};
const G = {};
const view = { plan: false };

// ---------- host (the viewer in the frame) ----------
function frameUrl(m) { return `index.html?embed${m.view.airport ? "&airport" : ""}#${encodeURIComponent(m.view.city)}`; }
let hostKey = "";
function connect(m) {
  const key = frameUrl(m);
  if (host && key === hostKey) return Promise.resolve();
  hostKey = key; host = null;
  $("loading").hidden = false; $("loading").textContent = "Loading the city…";
  const frame = $("view");
  return new Promise((ok, fail) => {
    frame.onload = () => {
      frameWin = frame.contentWindow;
      const t0 = performance.now();
      const wait = () => {
        if (frameWin.__city) { mount(frameWin.__city); ok(); return; }
        if (performance.now() - t0 > 120000) { fail(new Error("The viewer did not start.")); return; }
        setTimeout(wait, 100);
      };
      wait();
    };
    frame.src = key;
  });
}
function mount(h) {
  host = h; THREE = h.THREE; canvas = h.canvas;
  for (const k of ["terrain", "water", "zones", "roads", "rail", "props", "paths", "vehicles", "handles", "cursor"]) { G[k] = new THREE.Group(); G[k].name = "editor-" + k; h.scene.add(G[k]); }
  bindInput(canvas, frameWin);
  $("loading").hidden = true;
}
function applyViewer() { host.applyLayout(M.viewerLayout(S.map)); host.rebuild(); }

const matCache = new Map();
const mat = (c, o = {}) => { const k = c + JSON.stringify(o); if (!matCache.has(k)) matCache.set(k, new THREE.MeshStandardMaterial({ color: c, roughness: 0.85, ...o })); return matCache.get(k); };
function clear(g) { for (const c of [...g.children]) { g.remove(c); c.traverse((o) => { if (o.geometry && !o.userData.shared) o.geometry.dispose(); if (o.isSprite) o.material.map?.dispose(); }); } }

// ---------- camera (the viewer's isometric rig) ----------
function extent() { const t = S.map.terrain; return { x0: t.x0, x1: t.x0 + (t.w - 1) * t.step, z0: t.z0, z1: t.z0 + (t.h - 1) * t.step }; }
function homeView() {
  const e = extent(), v = host.view;
  v.target.set((e.x0 + e.x1) / 2, 0, (e.z0 + e.z1) / 2); v.az = 45; v.zoom = 1;
  host.placeCamera();
  const span = Math.max(e.x1 - e.x0, e.z1 - e.z0), half = host.camera.top;
  v.zoom = Math.max(0.2, half / (span * 0.5));
  place();
}
function place() {
  host.placeCamera();
  if (view.plan) {
    const v = host.view, cam = host.camera, b = (v.az * Math.PI) / 180 - Math.PI / 4;
    cam.position.set(v.target.x, 150, v.target.z); cam.up.set(-Math.sin(b), 0, -Math.cos(b)); cam.lookAt(v.target);
  } else host.camera.up.set(0, 1, 0);
}
let rotAnim = 0, rotTo = null;
function rotate(d) {
  const v = host.view, from = v.az, to = (rotTo ?? v.az) + d, t0 = performance.now();
  rotTo = to;
  const reduce = matchMedia("(prefers-reduced-motion: reduce)").matches;
  cancelAnimationFrame(rotAnim);
  const step = (now) => { const u = reduce ? 1 : Math.min(1, (now - t0) / 380); v.az = from + (to - from) * (u < 0.5 ? 2 * u * u : 1 - Math.pow(-2 * u + 2, 2) / 2); place(); if (u < 1) rotAnim = requestAnimationFrame(step); else { v.az = ((to % 360) + 360) % 360; rotTo = null; place(); } };
  rotAnim = requestAnimationFrame(step);
}
function panBy(dx, dy) {
  const cam = host.camera, wpp = (cam.right - cam.left) / canvas.clientWidth;
  const right = new THREE.Vector3().setFromMatrixColumn(cam.matrixWorld, 0); right.y = 0; right.normalize();
  const up = new THREE.Vector3().setFromMatrixColumn(cam.matrixWorld, 1); up.y = 0; up.normalize();
  const k = view.plan ? 1 : 1 / Math.sin(Math.atan(ELEV));
  host.view.target.addScaledVector(right, -dx * wpp).addScaledVector(up, dy * wpp * k);
  place();
}

// ---------- assets (the viewer's registry) ----------
const PALETTE = [
  ["Nature", (id) => /^(tree|bush|grass|flower|rock|stump)/.test(id)],
  ["Buildings", (id) => /^(bld|house|tower|garage|hangar|tent|fountain|obelisk|column)/.test(id)],
  ["Vehicles", (id) => /(car|suv|taxi|van|truck|ambulance|tractor|digger|sedan)/.test(id)],
  ["Roads and ground", (id) => /^(road|pavement)/.test(id)],
  ["People", (id) => /^mini/.test(id)],
  ["Props", () => true],
];
function placeAsset(id) {
  const src = host.assets[id];
  if (!src) return new THREE.Mesh(new THREE.BoxGeometry(0.6, 0.6, 0.6), mat("#c33"));
  const o = src.clone(); o.traverse((m) => { if (m.isMesh) { m.userData.shared = true; m.castShadow = true; } }); return o;
}

// ---------- terrain ----------
let terrainMesh = null, waterMesh = null, C = null;
function colorFor(h, w, out) {
  if (h < w) return out.copy(C.bed);
  if (h < w + 0.2) return out.copy(C.sand);
  if (h < 1.5) return out.copy(C.grass).lerp(C.grass2, Math.max(0, h) / 1.5);
  if (h < 5) return out.copy(C.grass2).lerp(C.rock, (h - 1.5) / 3.5);
  return out.copy(C.rock).lerp(C.snow, Math.min(1, (h - 5) / 3));
}
function buildTerrain() {
  C = C || { bed: new THREE.Color("#a99c7c"), sand: new THREE.Color("#d8c99a"), grass: new THREE.Color("#a9cf8f"), grass2: new THREE.Color("#7fa866"), rock: new THREE.Color("#8d8a80"), snow: new THREE.Color("#f2f4f2") };
  clear(G.terrain); clear(G.water);
  const t = S.map.terrain, geo = new THREE.BufferGeometry(), n = t.w * t.h, idx = [];
  for (let j = 0; j < t.h - 1; j++) for (let i = 0; i < t.w - 1; i++) { const a = j * t.w + i, b = a + 1, c = a + t.w, d = c + 1; idx.push(a, c, b, b, c, d); }
  // typed arrays must come from the viewer's realm (three.js checks them with instanceof)
  geo.setAttribute("position", new THREE.Float32BufferAttribute(n * 3, 3));
  geo.setAttribute("color", new THREE.Float32BufferAttribute(n * 3, 3));
  geo.setIndex(idx);
  terrainMesh = new THREE.Mesh(geo, new THREE.MeshStandardMaterial({ vertexColors: true, roughness: 0.95 }));
  terrainMesh.receiveShadow = true; terrainMesh.position.y = -0.005; terrainMesh.userData.pick = { type: "terrain" };
  G.terrain.add(terrainMesh); updateTerrain();
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

// ---------- labels for editor zones ----------
function label(text, sub, color) {
  const cv = frameWin.document.createElement("canvas"), x = cv.getContext("2d"), f = 26;
  x.font = `600 ${f}px system-ui, sans-serif`;
  const w = Math.ceil(Math.max(x.measureText(text).width, sub ? x.measureText(sub).width * 0.7 : 0)) + 24, h = sub ? 66 : 40;
  cv.width = w; cv.height = h;
  x.fillStyle = color; x.globalAlpha = 0.92; x.beginPath(); x.roundRect(0, 0, w, h, 8); x.fill(); x.globalAlpha = 1;
  x.fillStyle = "#fff"; x.font = `600 ${f}px system-ui, sans-serif`; x.fillText(text, 12, 29);
  if (sub) { x.font = `${Math.round(f * 0.7)}px system-ui, sans-serif`; x.fillText(sub, 12, 56); }
  const tex = new THREE.CanvasTexture(cv); tex.colorSpace = THREE.SRGBColorSpace;
  const s = new THREE.Sprite(new THREE.SpriteMaterial({ map: tex, depthTest: false, transparent: true }));
  s.scale.set(w / 40, h / 40, 1); s.renderOrder = 10;
  return s;
}

// ---------- zones ----------
function zoneColor(z) { return z.kind === "district" ? M.PILLAR[z.pillar]?.c || "#888" : (M.ZONE_KINDS[z.kind] || M.ZONE_KINDS.other).c; }
function buildZones() {
  clear(G.zones);
  for (const z of S.map.zones) {
    const w = z.x1 - z.x0, d = z.z1 - z.z0, cx = (z.x0 + z.x1) / 2, cz = (z.z0 + z.z1) / 2, viewer = M.isViewerZone(z);
    const pad = z.kind === "district" ? 1 : 0, y = viewer ? 0.02 : Math.max(hAt(z.x0, z.z0), hAt(z.x1, z.z0), hAt(z.x0, z.z1), hAt(z.x1, z.z1), hAt(cx, cz), S.map.terrain.water) + 0.04;
    const selected = S.sel && S.sel.type === "zone" && S.sel.id === z.id;
    // viewer zones: invisible pick box (the viewer draws them); editor zones: a coloured plot
    const slab = new THREE.Mesh(new THREE.BoxGeometry(w + pad, viewer ? 0.6 : 0.08, d + pad), new THREE.MeshStandardMaterial({ color: zoneColor(z), transparent: true, opacity: viewer ? 0 : selected ? 0.75 : 0.5, depthWrite: !viewer }));
    slab.position.set(cx, viewer ? 0.3 : y, cz); slab.receiveShadow = true; slab.userData.pick = { type: "zone", id: z.id }; slab.userData.noExport = viewer;
    G.zones.add(slab);
    if (selected || !viewer) {
      const outline = new THREE.LineSegments(new THREE.EdgesGeometry(new THREE.BoxGeometry(w + pad, 0.08, d + pad)), new THREE.LineBasicMaterial({ color: selected ? "#ffb400" : zoneColor(z), depthTest: !selected }));
      outline.position.set(cx, viewer ? 0.06 : y, cz); outline.renderOrder = 7; G.zones.add(outline);
    }
    if (!viewer) { const kindName = (M.ZONE_KINDS[z.kind] || {}).n; const lab = label(z.label || z.id, kindName && kindName !== z.label ? kindName : "", zoneColor(z)); lab.position.set(cx, y + 1.2, cz); G.zones.add(lab); }
  }
}

// ---------- free roads and extra tracks ----------
function ribbon(points, width, yOf, color, opts = {}) {
  const pos = [], idx = [];
  for (let i = 0; i < points.length; i++) {
    const p = points[i], q = points[Math.min(points.length - 1, i + 1)], o = points[Math.max(0, i - 1)];
    let tx = q[0] - o[0], tz = q[1] - o[1]; const L = Math.hypot(tx, tz) || 1; tx /= L; tz /= L;
    const nx = (-tz * width) / 2, nz = (tx * width) / 2, y = yOf(i, p);
    pos.push(p[0] + nx, y, p[1] + nz, p[0] - nx, y, p[1] - nz);
    if (i) { const a = (i - 1) * 2; idx.push(a, a + 2, a + 1, a + 1, a + 2, a + 3); }
  }
  const g = new THREE.BufferGeometry(); g.setAttribute("position", new THREE.Float32BufferAttribute(pos, 3)); g.setIndex(idx); g.computeVertexNormals();
  const m = new THREE.Mesh(g, mat(color, opts.mo || {})); m.receiveShadow = true; return m;
}
function offsetLine(pts, off) {
  const n = pts.length - 1;
  return pts.map((p, i) => { const q = pts[Math.min(n, i + 1)], o = pts[Math.max(0, i - 1)]; let tx = q[0] - o[0], tz = q[1] - o[1]; const L = Math.hypot(tx, tz) || 1; return [p[0] - (tz / L) * off, p[1] + (tx / L) * off]; });
}
function deckY(g, e) {
  const A = M.nodeById(g, e.a), B = M.nodeById(g, e.b), w = S.map.terrain.water;
  const ya = Math.max(hAt(A.x, A.z), w + 0.5), yb = Math.max(hAt(B.x, B.z), w + 0.5);
  return (t) => ya + (yb - ya) * t + 0.06;
}
const ASPHALT = "#55595d", HIGHWAY = "#4a4f54";
function buildGraph(net) {
  const g = S.map[net], group = G[net]; clear(group);
  const isRail = net === "rail", deg = new Map(), hwy = new Set();
  for (const e of g.edges) { for (const n of [e.a, e.b]) deg.set(n, Math.max(deg.get(n) || 0, e.width || 1)); if (e.kind === "highway") { hwy.add(e.a); hwy.add(e.b); } }
  for (const e of g.edges) {
    const pts = M.edgePoints(g, e, 0.35), n = pts.length - 1, sel = S.sel && S.sel.type === "edge" && S.sel.net === net && S.sel.id === e.id;
    const flat = e.bridge ? deckY(g, e) : null;
    const yOf = (i, p) => (flat ? flat(i / n) : hAt(p[0], p[1]) + 0.045);
    let m;
    if (isRail) {
      m = ribbon(pts, 0.78, yOf, sel ? "#ffb400" : "#9c9184");
      for (const off of [-0.18, 0.18]) group.add(ribbon(offsetLine(pts, off), 0.05, (i, p) => yOf(i, p) + 0.06, "#b9c1c7", { mo: { metalness: 0.4, roughness: 0.5 } }));
    } else {
      const col = sel ? "#ffb400" : e.kind === "highway" ? HIGHWAY : ASPHALT;
      m = ribbon(pts, e.width || 1, yOf, col, e.tunnel ? { mo: { transparent: true, opacity: 0.35 } } : {});
      // lane markings like the kit tiles: dashed centre line, solid edge lines on highways
      for (let i = 0; i + 1 < pts.length; i += 3) group.add(ribbon([pts[i], pts[i + 1]], 0.06, (k, p) => yOf(i, p) + 0.008, "#f1efe6"));
      if (e.kind === "highway") for (const off of [-(e.width || 1) / 2 + 0.25, (e.width || 1) / 2 - 0.25]) group.add(ribbon(offsetLine(pts, off), 0.08, (i, p) => yOf(i, p) + 0.008, "#f1efe6"));
    }
    m.userData.pick = { type: "edge", net, id: e.id }; group.add(m);
    if (e.bridge) for (let i = 0; i <= n; i += 5) { const p = pts[i], top = yOf(i, p), bot = Math.min(hAt(p[0], p[1]), S.map.terrain.water - 1); const pil = new THREE.Mesh(new THREE.CylinderGeometry(0.14, 0.18, top - bot, 8), mat("#b8b0a2")); pil.position.set(p[0], (top + bot) / 2, p[1]); pil.castShadow = true; group.add(pil); }
  }
  if (!isRail) for (const nd of g.nodes) {
    if (!deg.has(nd.id)) continue;
    const disc = new THREE.Mesh(new THREE.CircleGeometry(deg.get(nd.id) / 2, 24), mat(hwy.has(nd.id) ? HIGHWAY : ASPHALT));
    disc.rotation.x = -Math.PI / 2; disc.position.set(nd.x, hAt(nd.x, nd.z) + 0.04, nd.z); disc.receiveShadow = true;
    if (g.edges.some((e) => e.bridge && (e.a === nd.id || e.b === nd.id))) disc.position.y = Math.max(disc.position.y, S.map.terrain.water + 0.56);
    group.add(disc);
  }
}

// ---------- props ----------
function buildProps() {
  clear(G.props);
  for (const p of S.map.props) {
    const o = placeAsset(p.asset); o.position.set(p.x, hAt(p.x, p.z), p.z); o.rotation.y = ((p.rot || 0) * Math.PI) / 180; o.scale.setScalar(p.scale || 1);
    o.userData.pick = { type: "prop", id: p.id };
    if (S.sel && S.sel.type === "prop" && S.sel.id === p.id) { const ring = new THREE.Mesh(new THREE.RingGeometry(0.45, 0.55, 24), new THREE.MeshBasicMaterial({ color: "#ffb400", side: THREE.DoubleSide })); ring.rotation.x = -Math.PI / 2; ring.position.set(p.x, hAt(p.x, p.z) + 0.06, p.z); ring.userData.noExport = true; G.props.add(ring); }
    G.props.add(o);
  }
}

// ---------- paths and vehicles ----------
const RUNNERS = [];
function vehicleMesh(kind) {
  if (kind === "car") return placeAsset("sedan");
  if (kind === "truck") return placeAsset("truck");
  if (kind === "bus") return placeAsset("delivery-van");
  const g = new THREE.Group();
  if (kind === "train") for (let i = 0; i < 3; i++) { const b = new THREE.Mesh(new THREE.BoxGeometry(1.05, 0.32, 0.36), mat(i ? "#e8e6e1" : "#6a5a8c")); b.position.set(-i * 1.12, 0.26, 0); b.castShadow = true; g.add(b); }
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
    const line = new THREE.Line(new THREE.BufferGeometry().setFromPoints(pts.map((q) => new THREE.Vector3(q[0], q[1] + 0.14, q[2]))), new THREE.LineDashedMaterial({ color: sel ? "#ffb400" : V.c, dashSize: 0.5, gapSize: 0.3, depthTest: false }));
    line.computeLineDistances(); line.renderOrder = 5; line.userData.pick = { type: "path", id: p.id }; G.paths.add(line);
    const cum = [0]; for (let i = 1; i < pts.length; i++) cum.push(cum[i - 1] + Math.hypot(pts[i][0] - pts[i - 1][0], pts[i][1] - pts[i - 1][1], pts[i][2] - pts[i - 1][2]));
    const mesh = vehicleMesh(p.vehicle); mesh.userData.noExport = true; G.vehicles.add(mesh);
    RUNNERS.push({ p, pts, cum, mesh, speed: p.speed || V.speed, phase: M.rng(p.id.length * 97 + S.map.seed)() * cum[cum.length - 1] });
  }
}
function runVehicles(time) {
  for (const r of RUNNERS) {
    const L = r.cum[r.cum.length - 1]; if (!L) continue;
    const raw = (r.phase + (S.play ? time * r.speed : 0)) % (r.p.loop === false ? L : 2 * L);
    const back = raw > L, s = back ? 2 * L - raw : raw;
    let i = 1; while (i < r.cum.length - 1 && r.cum[i] < s) i++;
    const a = r.pts[i - 1], b = r.pts[i], u = (s - r.cum[i - 1]) / (r.cum[i] - r.cum[i - 1] || 1);
    r.mesh.position.set(a[0] + (b[0] - a[0]) * u, a[1] + (b[1] - a[1]) * u, a[2] + (b[2] - a[2]) * u);
    r.mesh.rotation.y = Math.atan2(-(b[2] - a[2]), b[0] - a[0]) + (back ? Math.PI : 0);
  }
}

// ---------- handles ----------
function buildHandles() {
  clear(G.handles);
  if (!["select", "road", "rail", "path", "erase"].includes(S.tool)) return;
  const sph = new THREE.SphereGeometry(0.2, 10, 8);
  const ball = (x, y, z, color, pick) => { const h = new THREE.Mesh(sph, new THREE.MeshBasicMaterial({ color, depthTest: false })); h.position.set(x, y, z); h.renderOrder = 8; h.userData.pick = pick; G.handles.add(h); };
  for (const net of ["roads", "rail"]) {
    if ((S.tool === "road" && net !== "roads") || (S.tool === "rail" && net !== "rail")) continue;
    const g = S.map[net];
    for (const n of g.nodes) ball(n.x, hAt(n.x, n.z) + 0.25, n.z, net === "rail" ? "#a897d3" : "#ffffff", { type: "node", net, id: n.id });
    if (S.tool === "select") for (const e of g.edges) if (e.c) { const h = new THREE.Mesh(new THREE.OctahedronGeometry(0.22), new THREE.MeshBasicMaterial({ color: "#ffb400", depthTest: false })); h.position.set(e.c[0], hAt(e.c[0], e.c[1]) + 0.25, e.c[1]); h.renderOrder = 8; h.userData.pick = { type: "ctrl", net, id: e.id }; G.handles.add(h); }
  }
  for (const p of S.map.paths) if (p.mode === "free" && (S.tool === "path" || (S.sel && S.sel.type === "path" && S.sel.id === p.id))) p.points.forEach((q, i) => ball(q[0], q[1] + 0.2, q[2], M.VEHICLES[p.vehicle].c, { type: "pathpt", id: p.id, i }));
  if (S.sel && S.sel.type === "zone") {
    const z = S.map.zones.find((q) => q.id === S.sel.id);
    if (z && z.id !== "airport" && z.id !== "airport-station") for (const [cx, cz, corner] of [[z.x0, z.z0, "x0z0"], [z.x1, z.z0, "x1z0"], [z.x0, z.z1, "x0z1"], [z.x1, z.z1, "x1z1"]]) { const h = new THREE.Mesh(new THREE.BoxGeometry(0.4, 0.4, 0.4), new THREE.MeshBasicMaterial({ color: "#ffb400", depthTest: false })); h.position.set(cx, hAt(cx, cz) + 0.3, cz); h.renderOrder = 9; h.userData.pick = { type: "corner", id: z.id, corner }; G.handles.add(h); }
  }
}

function refreshCells() { S.cells = new Set(S.map.layout.roads); }
function rebuild(parts = "all") {
  const all = parts === "all", has = (k) => all || parts.includes(k);
  if (has("viewer")) { refreshCells(); applyViewer(); }
  if (has("terrain")) buildTerrain();
  if (has("zones")) buildZones();
  if (has("roads")) buildGraph("roads");
  if (has("rail")) buildGraph("rail");
  if (has("props")) buildProps();
  if (has("paths")) buildPaths();
  buildHandles();
  const m = S.map;
  $("counts").textContent = `${m.zones.length} zones · ${m.layout.roads.length} road tiles · ${m.roads.edges.length} free road segments · ${m.rail.edges.length} extra tracks · ${m.props.length} models · ${m.paths.length} paths`;
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
async function undoRedo(from, to) { if (!from.length) return; to.push(snapshot()); await loadMap(JSON.parse(from.pop()), true); }

// ---------- persistence ----------
let saveTimer = 0;
function save() { clearTimeout(saveTimer); saveTimer = setTimeout(() => { try { localStorage.setItem(STORE, snapshot()); } catch { /* storage unavailable */ } }, 400); }
async function loadMap(m, keepView = false) {
  S.map = m; S.sel = null; S.chain = null;
  await connect(m);
  $("city").value = m.view.city; $("airport").setAttribute("aria-pressed", String(!!m.view.airport));
  rebuild();
  if (!keepView) homeView(); else place();
  inspect();
}
function download(name, blob) { const a = document.createElement("a"); a.href = URL.createObjectURL(blob); a.download = name; document.body.appendChild(a); a.click(); setTimeout(() => { URL.revokeObjectURL(a.href); a.remove(); }, 500); }
function slug() { return (S.map.name || "city").toLowerCase().replace(/[^a-z0-9]+/g, "-").replace(/^-|-$/g, "") || "city"; }
function exportJson() { const text = M.serialize(S.map); download(`${slug()}.city-map.json`, new Blob([text], { type: "application/json" })); msg("Exported the map JSON."); return text; }
function exportRoot() {
  const root = new THREE.Group(); root.name = S.map.name || "Harness City";
  const keep = (o) => !(o.isSprite || o.isLine || o.isLineSegments || o.userData.noExport || (o.material && !Array.isArray(o.material) && o.material.transparent && o.material.opacity === 0));
  const copy = (src) => { const c = src.clone(false); for (const ch of src.children) if (keep(ch)) c.add(copy(ch)); return c; };
  if (host.city) root.add(copy(host.city));
  for (const k of ["terrain", "water", "zones", "roads", "rail", "props"]) root.add(copy(G[k]));
  return root;
}
async function exportGlb() {
  exporterMod = exporterMod || (await host.importModule("./vendor/jsm/exporters/GLTFExporter.js"));
  return new Promise((ok, fail) => {
    new exporterMod.GLTFExporter().parse(exportRoot(), (res) => { const blob = new Blob([res], { type: "model/gltf-binary" }); download(`${slug()}.glb`, blob); msg("Exported the GLB scene."); ok(blob.size); }, (e) => { msg("GLB export failed: " + e.message, true); fail(e); }, { binary: true, onlyVisible: true });
  });
}
function exportPng() {
  G.handles.visible = false; G.cursor.visible = false; host.renderer.render(host.scene, host.camera);
  const url = host.renderer.domElement.toDataURL("image/png");
  G.handles.visible = true; G.cursor.visible = true;
  fetch(url).then((r) => r.blob()).then((b) => download(`${slug()}.png`, b)); msg("Exported the PNG view."); return url.length;
}
function msg(t, err = false) { const el = $("msg"); el.textContent = t; el.className = err ? "err" : ""; }

// ---------- picking ----------
let ray = null;
function setRay(ev) { ray = ray || new THREE.Raycaster(); const r = canvas.getBoundingClientRect(); ray.setFromCamera(new THREE.Vector2(((ev.clientX - r.left) / r.width) * 2 - 1, -((ev.clientY - r.top) / r.height) * 2 + 1), host.camera); }
function ground(ev) {
  setRay(ev);
  const hit = terrainMesh && ray.intersectObject(terrainMesh, false)[0];
  if (hit) return hit.point;
  const p = new THREE.Vector3(); return ray.ray.intersectPlane(new THREE.Plane(new THREE.Vector3(0, 1, 0), 0), p) ? p : null;
}
function pick(ev, groups) {
  setRay(ev);
  for (const g of groups) {
    const hits = ray.intersectObjects(G[g].children, true);
    for (const h of hits) { let o = h.object; while (o && !o.userData.pick) o = o.parent; if (o && o.userData.pick) return o.userData.pick; }
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
  ["select", "Select / move", "1", "Click to select. Drag districts, the airport, zones, models and junctions. Drag corners to resize. Delete removes."],
  ["terrain", "Terraform", "2", "Drag to sculpt the land around the city. The viewer's districts, road tiles and airport stay flat."],
  ["trees", "Trees", "3", "Drag to paint trees, or switch to erase. Placement is seeded, so it is repeatable."],
  ["road", "Streets", "4", "Road tiles: drag a straight line of the viewer's tiles. Free: click points for any angle, curves and highways; Enter ends."],
  ["rail", "Tracks", "5", "Extra track next to the viewer's main line. Click points; Enter or Esc ends. Curve makes smooth bends."],
  ["zone", "Districts and zones", "6", "Drag a rectangle. A district moves there; other kinds add a zone (mall, harbor, bank and more)."],
  ["prop", "Place assets", "7", "Pick a model in the palette, click to place. R rotates, [ and ] scale."],
  ["path", "Vehicle paths", "8", "Trucks, cars, buses: click street stops (tiles or free roads). Trains: track ends. Ships and planes: free points. Enter ends."],
  ["erase", "Erase", "9", "Click a model, zone, free road, track, path or road tile to delete it."],
];
function setTool(t) {
  finishChain(); S.tool = t;
  for (const b of $("tools").children) b.setAttribute("aria-pressed", String(b.dataset.tool === t));
  $("hint").textContent = TOOLS.find((x) => x[0] === t)[3];
  renderOpts(); buildHandles(); updateCursor();
}
function finishChain() {
  if (S.chain) { S.chain = null; commit(S.tool === "rail" ? ["rail", "paths"] : S.tool === "path" ? ["paths"] : ["roads", "paths"]); }
  if (G.cursor) clear(G.cursor);
}
function graphClick(net, pt) {
  const g = S.map[net];
  if (!S.chain) { begin(); S.chain = { net, last: null, prevC: null }; }
  const last = S.chain.last ? M.nodeById(g, S.chain.last) : null;
  const [x, z] = S.guided ? snapAngle(last, snap(pt.x, 0.5), snap(pt.z, 0.5)) : [pt.x, pt.z];
  let node = M.nearestNode(g, x, z, S.guided ? 0.6 : 0.8);
  if (!node) {
    const ne = M.nearestEdge(g, x, z, net === "rail" ? 0.45 : 0.6);
    node = ne ? M.splitEdge(g, ne.edge, x, z) : M.addNode(g, x, z, net === "rail" ? "r" : "n");
  }
  if (last && node.id !== last.id) {
    const props = net === "rail" ? { kind: "track" } : { kind: S.opt.roadKind, lanes: S.opt.lanes, width: S.opt.roadKind === "highway" ? Math.max(3, S.opt.lanes + 1) : Math.max(1, S.opt.lanes / 2) };
    const e = M.addEdge(g, last.id, node.id, props, net === "rail" ? "t" : "e");
    if (e && S.opt.curve) e.c = S.chain.prevC ? [2 * last.x - S.chain.prevC[0], 2 * last.z - S.chain.prevC[1]] : [(last.x + node.x) / 2, (last.z + node.z) / 2];
    S.chain.prevC = e && e.c ? e.c : [(last.x + node.x) / 2, (last.z + node.z) / 2];
    if (e && net === "roads" && M.edgePoints(g, e, 0.5).some((p) => hAt(p[0], p[1]) < S.map.terrain.water)) e.bridge = true;
  }
  S.chain.last = node.id;
  buildGraph(net); buildHandles();
}
function cellLine(a, b) {
  const [ax, az] = a, [bx, bz] = b, out = [];
  if (Math.abs(bx - ax) >= Math.abs(bz - az)) for (let x = Math.min(ax, bx); x <= Math.max(ax, bx); x++) out.push(M.cellKey(x, az));
  else for (let z = Math.min(az, bz); z <= Math.max(az, bz); z++) out.push(M.cellKey(ax, z));
  return out;
}
function pathNetwork(p) { return p.mode === "rail" ? M.railNetwork(S.map) : M.roadNetwork(S.map); }
function pathClick(pt) {
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
    const g = pathNetwork(p), n = M.nearestNode(g, pt.x, pt.z, p.mode === "rail" ? 3 : 1.5);
    if (!n) { msg(`No ${p.mode === "rail" ? "track end" : "street"} near here.`, true); return; }
    if (p.stops[p.stops.length - 1] !== n.id) p.stops.push(n.id);
    const bad = p.stops.length > 1 && !M.shortestPath(g, p.stops[p.stops.length - 2], n.id);
    msg(bad ? "These stops are not connected." : "", bad);
  }
  buildPaths(); buildHandles();
}
function protectedAt(x, z) {
  for (const q of S.map.zones) if (M.isViewerZone(q) && x >= q.x0 - 1.2 && x <= q.x1 + 1.2 && z >= q.z0 - 1.2 && z <= q.z1 + 1.2) return true;
  for (let dx = -1; dx <= 1; dx++) for (let dz = -1; dz <= 1; dz++) if (S.cells.has(M.cellKey(Math.round(x) + dx, Math.round(z) + dz))) return true;
  return false;
}
function brushStep(pt, dt) {
  const t = S.map.terrain, o = S.opt, x = S.guided ? Math.round(pt.x) : pt.x, z = S.guided ? Math.round(pt.z) : pt.z;
  if (o.brush === "water") { t.water = Math.round(o.level * 100) / 100; updateTerrain(); return; }
  const target = o.brush === "flatten" ? (S.flatTo ??= hAt(x, z)) : o.level;
  // keep the cells the viewer draws flat
  const keep = [], r = o.radius + 1;
  for (let j = Math.max(0, Math.floor((z - r - t.z0) / t.step)); j <= Math.min(t.h - 1, Math.ceil((z + r - t.z0) / t.step)); j++)
    for (let i = Math.max(0, Math.floor((x - r - t.x0) / t.step)); i <= Math.min(t.w - 1, Math.ceil((x + r - t.x0) / t.step)); i++)
      if (protectedAt(t.x0 + i * t.step, t.z0 + j * t.step)) keep.push([j * t.w + i, t.heights[j * t.w + i]]);
  M.applyBrush(t, o.brush, x, z, o.radius, o.strength * Math.min(3, dt * 60), target, S.guided ? 0.25 : 0);
  for (const [k, h] of keep) t.heights[k] = h;
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
  const roadNear = (x, z) => S.cells.has(M.cellKey(Math.round(x), Math.round(z))) || ["roads", "rail"].some((net) => { const ne = M.nearestEdge(m[net], x, z, 4); if (!ne) return false; const w = net === "rail" ? 0.8 : ne.edge.width || 1; return ne.d < w / 2 + 0.4; });
  const inZone = (x, z) => m.zones.some((q) => x >= q.x0 - 0.6 && x <= q.x1 + 0.6 && z >= q.z0 - 0.6 && z <= q.z1 + 0.6);
  const onRail = (x, z) => m.layout.rail.tracks.concat([m.layout.rail.siding]).some((tz) => Math.abs(z - tz) < 0.6);
  for (let k = 0; k < o.density; k++) {
    const a = r() * Math.PI * 2, d = Math.sqrt(r()) * o.treeRadius, x = pt.x + Math.cos(a) * d, z = pt.z + Math.sin(a) * d;
    const kind = o.kinds[Math.floor(r() * o.kinds.length)] || "tree-oak", rot = Math.round(r() * 360), sc = Math.round((0.8 + r() * 0.5) * 100) / 100;
    if (hAt(x, z) < m.terrain.water + 0.15 || roadNear(x, z) || onRail(x, z) || (o.avoid && inZone(x, z))) continue;
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
    if (target.type === "zone") { const z = m.zones.find((q) => q.id === target.id); if (z && M.isViewerZone(z)) { msg("Districts and the airport are drawn by the viewer and cannot be deleted. Move them instead.", true); return; } m.zones = m.zones.filter((q) => q.id !== target.id); }
    if (target.type === "prop") m.props = m.props.filter((p) => p.id !== target.id);
    if (target.type === "edge") M.removeEdge(m[target.net], target.id);
    if (target.type === "node") M.removeNode(m[target.net], target.id);
    if (target.type === "path") m.paths = m.paths.filter((p) => p.id !== target.id);
    if (target.type === "cell") m.layout.roads = m.layout.roads.filter((k) => k !== target.id);
    if (target.type === "pathpt") { const p = m.paths.find((q) => q.id === target.id); p.points.splice(target.i, 1); if (p.points.length < 2) m.paths = m.paths.filter((q) => q !== p); }
    for (const p of m.paths) if (p.stops) { const g = p.mode === "rail" ? M.railNetwork(m) : M.roadNetwork(m); p.stops = p.stops.filter((s) => M.nodeById(g, s)); }
    S.sel = null;
  });
  inspect();
}

// ---------- pointer ----------
let panning = null;
function bindInput(cv, win) {
  cv.addEventListener("contextmenu", (e) => e.preventDefault());
  cv.addEventListener("pointerdown", onDown);
  cv.addEventListener("pointermove", onMove);
  cv.addEventListener("pointerup", onUp);
  cv.addEventListener("dblclick", () => finishChain());
  cv.addEventListener("wheel", (ev) => { ev.preventDefault(); host.view.zoom = Math.max(0.15, Math.min(14, host.view.zoom * (ev.deltaY < 0 ? 1.12 : 1 / 1.12))); place(); }, { passive: false });
  win.addEventListener("keydown", onKey); win.addEventListener("keyup", onKeyUp);
}
function onDown(ev) {
  canvas.setPointerCapture(ev.pointerId);
  if (ev.button === 1 || ev.button === 2 || S.space) { if (ev.button === 2 && S.chain) { finishChain(); return; } panning = { x: ev.clientX, y: ev.clientY }; return; }
  const pt = ground(ev); if (!pt) return;
  S.down = true; S.lastT = performance.now(); S.flatTo = null; S.lastStamp = null;
  const t = S.tool;
  if (t === "select") {
    const hit = pick(ev, ["handles", "props", "paths", "roads", "rail", "zones"]);
    if (hit && ["node", "ctrl", "pathpt", "corner"].includes(hit.type)) { begin(); S.drag = { hit, start: pt.clone() }; return; }
    S.sel = hit && hit.type !== "terrain" ? hit : null;
    if (S.sel) { begin(); S.drag = { hit: S.sel, start: pt.clone(), orig: JSON.parse(JSON.stringify(itemOf(S.sel) || {})) }; }
    rebuild(["zones", "roads", "rail", "props", "paths"]); inspect(); return;
  }
  if (t === "terrain" || t === "trees") { begin(); if (t === "terrain") brushStep(pt, 1 / 60); else treeStep(pt); return; }
  if (t === "road" && S.opt.roadMode === "tiles") { begin(); S.drag = { cells: true, start: [Math.round(pt.x), Math.round(pt.z)] }; updateCellPreview(pt); return; }
  if (t === "road") return graphClick("roads", pt);
  if (t === "rail") return graphClick("rail", pt);
  if (t === "path") return pathClick(pt);
  if (t === "zone") { begin(); S.drag = { zone: true, start: [Math.round(pt.x), Math.round(pt.z)] }; return; }
  if (t === "prop") {
    change(["props"], () => { const id = "p" + (Math.max(0, ...S.map.props.map((p) => Number(String(p.id).slice(1)) || 0)) + 1); S.map.props.push({ id, asset: S.opt.asset, x: snap(pt.x, 0.5), z: snap(pt.z, 0.5), rot: S.opt.rot, scale: S.opt.scale }); });
    return;
  }
  if (t === "erase") {
    const hit = pick(ev, ["handles", "props", "paths", "roads", "rail", "zones"]);
    const cell = M.cellKey(Math.round(pt.x), Math.round(pt.z));
    if (hit && !(hit.type === "zone" && S.cells.has(cell))) deleteSel(hit);
    else if (S.cells.has(cell)) deleteSel({ type: "cell", id: cell });
  }
}
function onMove(ev) {
  if (panning) { panBy(ev.clientX - panning.x, ev.clientY - panning.y); panning = { x: ev.clientX, y: ev.clientY }; return; }
  const pt = ground(ev); S.cursor = pt;
  if (pt) $("pos").textContent = `x ${pt.x.toFixed(1)}  z ${pt.z.toFixed(1)}  height ${hAt(pt.x, pt.z).toFixed(2)}`;
  updateCursor();
  if (!S.down || !pt) return;
  const now = performance.now(), dt = (now - S.lastT) / 1000; S.lastT = now;
  if (S.tool === "terrain") return brushStep(pt, dt);
  if (S.tool === "trees") return treeStep(pt);
  if (S.drag && S.drag.cells) return updateCellPreview(pt);
  if (S.drag) dragTo(pt);
}
function onUp() {
  if (panning) { panning = null; return; }
  if (!S.down) return;
  S.down = false;
  if (S.tool === "terrain") { commit(["terrain", "zones", "roads", "rail", "props", "paths"]); return; }
  if (S.tool === "trees") { commit(["props"]); return; }
  const d = S.drag; S.drag = null;
  if (d && d.cells) {
    const add = cellLine(d.start, d.end || d.start);
    S.map.layout.roads = [...new Set(S.map.layout.roads.concat(add))];
    clear(G.cursor); commit(["viewer", "paths"]); msg(`Added ${add.length} road tile${add.length > 1 ? "s" : ""}.`); return;
  }
  if (d && d.zone) {
    const [x0, z0] = d.start, [x1, z1] = d.end || d.start;
    if (Math.abs(x1 - x0) >= 1 && Math.abs(z1 - z0) >= 1) {
      const r = { x0: Math.min(x0, x1), x1: Math.max(x0, x1), z0: Math.min(z0, z1), z1: Math.max(z0, z1) };
      if (S.opt.zoneKind === "district") { const z = S.map.zones.find((q) => q.kind === "district" && q.pillar === S.opt.pillar); Object.assign(z, r); S.sel = { type: "zone", id: z.id }; }
      else { const k = S.opt.zoneKind, id = k + "-" + (S.map.zones.filter((q) => q.kind === k).length + 1); S.map.zones.push({ id, kind: k, label: M.ZONE_KINDS[k].n, goal: "", ...r }); S.sel = { type: "zone", id }; }
    }
    clear(G.cursor); commit(S.opt.zoneKind === "district" ? "all" : ["zones"]); inspect(); return;
  }
  if (d) {
    const z = d.hit.type === "zone" || d.hit.type === "corner" ? S.map.zones.find((q) => q.id === d.hit.id) : null;
    if (z && z.id === "airport") M.syncAirport(S.map);
    clear(G.cursor);
    commit(z && M.isViewerZone(z) ? "all" : ["zones", "roads", "rail", "props", "paths"]); inspect();
  }
}
function itemOf(sel) {
  const m = S.map;
  if (sel.type === "zone" || sel.type === "corner") return m.zones.find((q) => q.id === sel.id);
  if (sel.type === "prop") return m.props.find((q) => q.id === sel.id);
  if (sel.type === "edge" || sel.type === "ctrl") return m[sel.net].edges.find((q) => q.id === sel.id);
  if (sel.type === "node") return M.nodeById(m[sel.net], sel.id);
  if (sel.type === "path" || sel.type === "pathpt") return m.paths.find((q) => q.id === sel.id);
  return null;
}
function boxPreview(x0, z0, x1, z1, color = "#ffb400") {
  const w = Math.abs(x1 - x0), d = Math.abs(z1 - z0);
  if (w <= 0 || d <= 0) return;
  const b = new THREE.Mesh(new THREE.BoxGeometry(w, 0.1, d), new THREE.MeshBasicMaterial({ color, transparent: true, opacity: 0.45, depthTest: false }));
  b.position.set((x0 + x1) / 2, 0.12, (z0 + z1) / 2); b.renderOrder = 9; G.cursor.add(b);
}
function updateCellPreview(pt) {
  const d = S.drag; d.end = [Math.round(pt.x), Math.round(pt.z)]; clear(G.cursor);
  for (const k of cellLine(d.start, d.end)) { const [x, z] = k.split(",").map(Number); boxPreview(x - 0.5, z - 0.5, x + 0.5, z + 0.5); }
}
function dragTo(pt) {
  const d = S.drag, h = d.hit;
  if (d.zone) { d.end = [Math.round(pt.x), Math.round(pt.z)]; clear(G.cursor); boxPreview(d.start[0], d.start[1], d.end[0], d.end[1]); return; }
  const it = itemOf(h); if (!it) return;
  const dx = pt.x - d.start.x, dz = pt.z - d.start.z;
  const whole = (z) => M.isViewerZone(z);
  if (h.type === "zone") {
    if (it.id === "airport-station") return;
    const o = d.orig, s = whole(it) || S.guided ? 1 : 0.5, sx = Math.round(dx / s) * s, sz = Math.round(dz / s) * s;
    Object.assign(it, { x0: o.x0 + sx, x1: o.x1 + sx, z0: o.z0 + sz, z1: o.z1 + sz });
    clear(G.cursor); const p = whole(it) ? 0.5 : 0; boxPreview(it.x0 - p, it.z0 - p, it.x1 + p, it.z1 + p);
    if (!whole(it)) buildZones();
  } else if (h.type === "corner") {
    const c = h.corner, s = whole(it) ? 1 : 0.5, x = Math.round(pt.x / s) * s, z = Math.round(pt.z / s) * s;
    if (c.includes("x0")) it.x0 = Math.min(x, it.x1 - 1); else it.x1 = Math.max(x, it.x0 + 1);
    if (c.includes("z0")) it.z0 = Math.min(z, it.z1 - 1); else it.z1 = Math.max(z, it.z0 + 1);
    clear(G.cursor); boxPreview(it.x0 - 0.5, it.z0 - 0.5, it.x1 + 0.5, it.z1 + 0.5);
    if (!whole(it)) buildZones();
  } else if (h.type === "prop") { it.x = snap(d.orig.x + dx, 0.5); it.z = snap(d.orig.z + dz, 0.5); buildProps(); }
  else if (h.type === "node") { it.x = snap(pt.x, 0.5); it.z = snap(pt.z, 0.5); buildGraph(h.net); buildPaths(); }
  else if (h.type === "ctrl") { it.c = [snap(pt.x, 0.5), snap(pt.z, 0.5)]; buildGraph(h.net); buildPaths(); }
  else if (h.type === "pathpt") { const q = it.points[h.i]; q[0] = snap(pt.x, 0.5); q[2] = snap(pt.z, 0.5); buildPaths(); }
  buildHandles();
}
function updateCursor() {
  if (!G.cursor || S.drag) return;
  clear(G.cursor); const pt = S.cursor; if (!pt) return;
  const ringAt = (r, color) => { const ring = new THREE.Mesh(new THREE.RingGeometry(r - 0.08, r, 48), new THREE.MeshBasicMaterial({ color, side: THREE.DoubleSide, depthTest: false, transparent: true, opacity: 0.9 })); ring.rotation.x = -Math.PI / 2; ring.position.set(S.guided ? Math.round(pt.x) : pt.x, hAt(pt.x, pt.z) + 0.1, S.guided ? Math.round(pt.z) : pt.z); ring.renderOrder = 9; G.cursor.add(ring); };
  if (S.tool === "terrain") ringAt(S.opt.radius, "#ffb400");
  if (S.tool === "trees") ringAt(S.opt.treeRadius, S.opt.treeMode === "erase" ? "#b3261e" : "#3f8f3a");
  if (S.tool === "road" && S.opt.roadMode === "tiles") { const x = Math.round(pt.x), z = Math.round(pt.z); boxPreview(x - 0.5, z - 0.5, x + 0.5, z + 0.5); }
  if ((S.tool === "road" || S.tool === "rail") && S.chain && S.chain.last) {
    const g = S.map[S.chain.net], a = M.nodeById(g, S.chain.last), [x, z] = S.guided ? snapAngle(a, snap(pt.x, 0.5), snap(pt.z, 0.5)) : [pt.x, pt.z];
    const line = new THREE.Line(new THREE.BufferGeometry().setFromPoints([new THREE.Vector3(a.x, hAt(a.x, a.z) + 0.2, a.z), new THREE.Vector3(x, hAt(x, z) + 0.2, z)]), new THREE.LineBasicMaterial({ color: "#ffb400", depthTest: false }));
    line.renderOrder = 9; G.cursor.add(line);
  }
  if (S.tool === "prop" && host.assets[S.opt.asset]) { const o = placeAsset(S.opt.asset); o.position.set(snap(pt.x, 0.5), hAt(pt.x, pt.z), snap(pt.z, 0.5)); o.rotation.y = (S.opt.rot * Math.PI) / 180; o.scale.setScalar(S.opt.scale); o.traverse((m) => { if (m.isMesh) { m.material = m.material.clone(); m.material.transparent = true; m.material.opacity = 0.55; } }); G.cursor.add(o); }
}

// ---------- panels ----------
const h = (tag, attrs = {}, kids = []) => { const e = document.createElement(tag); for (const [k, v] of Object.entries(attrs)) { if (k === "on") for (const [ev, fn] of Object.entries(v)) e.addEventListener(ev, fn); else if (k === "text") e.textContent = v; else if (v !== undefined && v !== false) e.setAttribute(k, v === true ? "" : v); } for (const c of [].concat(kids)) if (c) e.append(c); return e; };
function field(lbl, input) { return h("div", { class: "row" }, [h("label", { text: lbl, for: input.id }), input]); }
function num(id, value, step, onInput, min, max) { const i = h("input", { id, type: "number", step, value, min, max }); i.addEventListener("input", () => { const v = Number(i.value); if (Number.isFinite(v)) onInput(v); }); return i; }
function sel(id, value, options, onChange) { const s = h("select", { id }); for (const [v, t] of options) s.append(h("option", { value: v, text: t, selected: v === value })); s.addEventListener("change", () => onChange(s.value)); return s; }
function check(id, value, text, onChange) { const i = h("input", { id, type: "checkbox", checked: value }); i.addEventListener("change", () => onChange(i.checked)); return h("div", { class: "row chk" }, [i, h("label", { for: id, text })]); }
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
    box.append(check("o-avoid", o.avoid, "Keep out of zones and districts", (v) => (o.avoid = v)));
    for (const k of ["tree-pine", "tree-oak", "tree-fat", "bush", "bush-large"]) box.append(check("o-k-" + k, o.kinds.includes(k), k, (v) => { o.kinds = v ? [...new Set([...o.kinds, k])] : o.kinds.filter((x) => x !== k); }));
  }
  if (S.tool === "road") {
    box.append(field("Mode", sel("o-rmode", o.roadMode, [["tiles", "Road tiles (viewer)"], ["free", "Free (any angle)"]], (v) => { finishChain(); o.roadMode = v; renderOpts(); buildHandles(); updateCursor(); })));
    if (o.roadMode === "free") {
      box.append(field("Kind", sel("o-rkind", o.roadKind, [["street", "Street"], ["highway", "Highway"]], (v) => { o.roadKind = v; o.lanes = v === "highway" ? 6 : 2; renderOpts(); })));
      box.append(field("Lanes", num("o-lanes", o.lanes, 1, (v) => (o.lanes = Math.max(1, Math.round(v))), 1, 8)));
    } else box.append(h("p", { class: "small", text: "The viewer picks straight, corner, T and cross tiles and street lamps from the neighbours. Erase removes tiles." }));
  }
  if ((S.tool === "road" && o.roadMode === "free") || S.tool === "rail") box.append(check("o-curve", o.curve, "Curve (smooth bends between points)", (v) => (o.curve = v)));
  if (S.tool === "zone") {
    box.append(field("Kind", sel("o-zkind", o.zoneKind, [["district", "District (pillar)"], ...Object.entries(M.ZONE_KINDS).filter(([k]) => k !== "airport" && k !== "station").map(([k, v]) => [k, v.n])], (v) => { o.zoneKind = v; renderOpts(); })));
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
  if (S.tool === "select" || S.tool === "erase") box.append(h("p", { class: "small", text: TOOLS.find((x) => x[0] === S.tool)[3] }));
}
function inspect() {
  const box = $("insp"); box.replaceChildren();
  const it = S.sel && itemOf(S.sel);
  if (!it) { box.append(h("p", { class: "small", text: "Nothing selected. Use Select and click an object." })); return; }
  const set = (parts, fn) => change(parts, fn);
  const t = S.sel.type;
  if (t === "zone") {
    const viewer = M.isViewerZone(it), parts = viewer ? "all" : ["zones"];
    if (it.kind === "district") box.append(h("p", { class: "small", text: `District for the pillar ${M.PILLAR[it.pillar].n}, drawn by the viewer. Its level comes from the audit (here the demo city), never from the editor.` }));
    else if (it.id === "airport") box.append(h("p", { class: "small", text: "The infrastructure overlay, drawn by the viewer. It moves by whole cells, with its station." }));
    else if (it.id === "airport-station") box.append(h("p", { class: "small", text: "Moves together with the airport." }));
    else box.append(field("Kind", sel("i-kind", it.kind, Object.entries(M.ZONE_KINDS).map(([k, v]) => [k, v.n]), (v) => set(parts, () => (it.kind = v)))));
    const lab = h("input", { id: "i-label", type: "text", value: it.label || "" }); lab.addEventListener("change", () => set(parts, () => (it.label = lab.value)));
    const goal = h("input", { id: "i-goal", type: "text", value: it.goal || "" }); goal.addEventListener("change", () => set(parts, () => (it.goal = goal.value)));
    box.append(field("Label", lab), field("Main goal", goal));
    if (!it.id.startsWith("airport")) for (const k of ["x0", "x1", "z0", "z1"]) box.append(field(k, num("i-" + k, it[k], viewer ? 1 : 0.5, (v) => set(parts, () => (it[k] = v)))));
  }
  if (t === "prop") {
    box.append(field("Model", sel("i-asset", it.asset, Object.keys(host.assets).sort().map((k) => [k, k]), (v) => set(["props"], () => (it.asset = v)))));
    for (const [k, st] of [["x", 0.5], ["z", 0.5], ["rot", 15], ["scale", 0.1]]) box.append(field(k, num("i-" + k, it[k] ?? (k === "scale" ? 1 : 0), st, (v) => set(["props"], () => (it[k] = v)))));
  }
  if (t === "edge") {
    box.append(h("p", { class: "small", text: `${S.sel.net === "rail" ? "Extra track" : "Free road"} segment ${it.id}` }));
    if (S.sel.net === "roads") {
      box.append(field("Kind", sel("i-ekind", it.kind || "street", [["street", "Street"], ["highway", "Highway"]], (v) => set(["roads"], () => (it.kind = v)))));
      box.append(field("Lanes", num("i-lanes", it.lanes || 2, 1, (v) => set(["roads"], () => (it.lanes = v)), 1, 8)));
      box.append(field("Width", num("i-width", it.width || 1, 0.25, (v) => set(["roads"], () => (it.width = v)), 0.5, 10)));
      box.append(check("i-oneway", !!it.oneway, "One way (a to b)", (v) => set(["roads", "paths"], () => (it.oneway = v || undefined))));
    }
    box.append(check("i-bridge", !!it.bridge, "Bridge on pillars", (v) => set([S.sel.net], () => (it.bridge = v || undefined))));
    box.append(check("i-tunnel", !!it.tunnel, "Tunnel", (v) => set([S.sel.net], () => (it.tunnel = v || undefined))));
    box.append(check("i-curve", !!it.c, "Curved (drag the diamond)", (v) => set([S.sel.net], () => { if (v) { const a = M.nodeById(S.map[S.sel.net], it.a), b = M.nodeById(S.map[S.sel.net], it.b); it.c = [(a.x + b.x) / 2 + (b.z - a.z) * 0.25, (a.z + b.z) / 2 - (b.x - a.x) * 0.25]; } else delete it.c; })));
  }
  if (t === "path") {
    box.append(field("Vehicle", sel("i-veh", it.vehicle, Object.entries(M.VEHICLES).filter(([, v]) => (v.net === "free") === (it.mode === "free") && (it.mode !== "rail" || v.net === "rail")).map(([k, v]) => [k, v.n]), (v) => set(["paths"], () => (it.vehicle = v)))));
    box.append(field("Speed", num("i-speed", it.speed, 0.1, (v) => set(["paths"], () => (it.speed = v)), 0.1, 20)));
    box.append(check("i-loop", it.loop !== false, "Return trip", (v) => set(["paths"], () => (it.loop = v))));
    box.append(h("p", { class: "small", text: it.mode === "free" ? `${it.points.length} free points` : `Stops: ${it.stops.join(" → ")}` }));
  }
  if (t === "node") box.append(h("p", { class: "small", text: `Junction ${it.id} at ${it.x}, ${it.z}` }));
  box.append(h("button", { id: "i-delete", text: "Delete", on: { click: () => deleteSel() } }));
}
function renderPalette() {
  const box = $("pal"); box.replaceChildren();
  const used = new Set(), ids = Object.keys(host.assets).sort();
  for (const [name, test] of PALETTE) {
    const group = ids.filter((id) => !used.has(id) && test(id)); if (!group.length) continue;
    box.append(h("h3", { text: `${name} (${group.length})` }));
    for (const id of group) { used.add(id); box.append(h("button", { "data-asset": id, title: id, "aria-pressed": String(S.opt.asset === id), text: id, on: { click: () => { S.opt.asset = id; setTool("prop"); renderPalette(); } } })); }
  }
  box.append(h("p", { class: "small", text: "The viewer's models. Other CC0 kits appear here after they are imported with a NOTICE entry." }));
}

// ---------- keyboard and buttons ----------
function onKey(ev) {
  if (ev.target.closest && ev.target.closest("input,select,textarea")) return;
  if (!host) return;
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
}
function onKeyUp(ev) { if (ev.key === " ") S.space = false; }
addEventListener("keydown", onKey); addEventListener("keyup", onKeyUp);
function toggleGuided() { S.guided = !S.guided; $("guided").setAttribute("aria-pressed", String(S.guided)); updateCursor(); }
function togglePlan() { view.plan = !view.plan; $("plan").setAttribute("aria-pressed", String(view.plan)); place(); }
$("labels").onclick = () => { const off = host.stage.classList.toggle("hide-labels"); $("labels").setAttribute("aria-pressed", String(!off)); };
$("guided").onclick = toggleGuided; $("plan").onclick = togglePlan;
$("rotL").onclick = () => rotate(-90); $("rotR").onclick = () => rotate(90);
$("undo").onclick = () => undoRedo(S.undo, S.redo); $("redo").onclick = () => undoRedo(S.redo, S.undo);
$("play").onclick = () => { S.play = !S.play; $("play").setAttribute("aria-pressed", String(S.play)); };
$("new").onclick = async () => { S.undo.push(snapshot()); S.redo.length = 0; await loadMap(M.PRESETS[$("preset").value]()); msg("Started from: " + S.map.name); };
$("city").onchange = async () => { S.undo.push(snapshot()); S.map.view.city = $("city").value; await loadMap(S.map, true); };
$("airport").onclick = async () => { S.undo.push(snapshot()); S.map.view.airport = !S.map.view.airport; await loadMap(S.map, true); };
$("import").onclick = () => $("file").click();
$("file").onchange = async () => { const f = $("file").files[0]; if (!f) return; try { const m = M.deserialize(await f.text()); S.undo.push(snapshot()); await loadMap(m); msg("Imported " + f.name); } catch (e) { msg(e.message, true); } $("file").value = ""; };
$("exJson").onclick = exportJson; $("exGlb").onclick = () => exportGlb().catch(() => {}); $("exPng").onclick = exportPng;
for (const [id, name, key] of TOOLS) $("tools").append(h("button", { "data-tool": id, "aria-pressed": "false", on: { click: () => setTool(id) } }, [document.createTextNode(name), h("kbd", { text: key })]));

// ---------- start ----------
let last = performance.now(), clock = 0;
function frame(now) {
  const dt = Math.min(0.1, (now - last) / 1000); last = now;
  if (!document.hidden) clock += dt;
  if (host && S.map) { if (S.down && S.tool === "terrain" && S.cursor && !panning) brushStep(S.cursor, dt); runVehicles(clock); }
  requestAnimationFrame(frame);
}
async function start() {
  const q = new URLSearchParams(location.search);
  let m = null;
  if (q.get("map")) { try { m = M.deserialize(await (await fetch(q.get("map"))).text()); } catch (e) { msg(e.message, true); } }
  if (!m && q.get("preset") && M.PRESETS[q.get("preset")]) m = M.PRESETS[q.get("preset")]();
  if (!m && !q.has("fresh")) { try { const s = localStorage.getItem(STORE); if (s) m = M.deserialize(s); } catch { m = null; } }
  if (!m) m = M.presetCurrent();
  $("preset").value = q.get("preset") || "current";
  await loadMap(m); renderPalette(); setTool("select");
  requestAnimationFrame(frame);
}
window.__editor = {
  ready: start(),
  get map() { return S.map; }, get state() { return S; }, get host() { return host; }, view,
  serialize: () => M.serialize(S.map), load: (text) => loadMap(M.deserialize(text)),
  setTool, rotate, exportJson, exportGlb, exportPng, toggleGuided, togglePlan, finishChain,
  undo: () => undoRedo(S.undo, S.redo), redo: () => undoRedo(S.redo, S.undo),
  screenOf: (x, z) => {
    const v = new THREE.Vector3(x, hAt(x, z), z).project(host.camera), r = canvas.getBoundingClientRect(), f = $("view").getBoundingClientRect();
    return { x: f.left + r.left + ((v.x + 1) / 2) * r.width, y: f.top + r.top + ((1 - v.y) / 2) * r.height };
  },
};
