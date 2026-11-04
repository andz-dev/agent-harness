// Convert selected CC0 models into plain GLBs on one shared scale (1 unit = 1 road tile).
import { NodeIO } from '@gltf-transform/core';
import { ALL_EXTENSIONS, KHRMaterialsUnlit, EXTMeshoptCompression } from '@gltf-transform/extensions';
import { MeshoptDecoder } from 'meshoptimizer';
import { getBounds, dedup, prune, transformMesh, textureCompress } from '@gltf-transform/functions';
import fs from 'node:fs';
import path from 'node:path';

const NF = '../assets_src/netforge/package/library/lowpoly';
const SK = '../assets_src/Starter-Kit-City-Builder/models';
const OUT = '../build/assets';
fs.mkdirSync(OUT, { recursive: true });

// id: [source file, fit rule]  fit: {foot:n} largest footprint side = n, {len:n} longest horizontal side, {h:n} height, {scale:n}
const LIST = {
  // Kenney City Builder starter kit (CC0 models): ground tiles, roads, small buildings
  'road-straight': [`${SK}/road-straight.glb`, { scale: 1 }],
  'road-lamps': [`${SK}/road-straight-lightposts.glb`, { scale: 1 }],
  'road-cross': [`${SK}/road-intersection.glb`, { scale: 1 }],
  'road-t': [`${SK}/road-split.glb`, { scale: 1 }],
  'road-corner': [`${SK}/road-corner.glb`, { scale: 1 }],
  'pavement': [`${SK}/pavement.glb`, { scale: 1 }],
  'fountain': [`${SK}/pavement-fountain.glb`, { scale: 1 }],
  'grass': [`${SK}/grass.glb`, { scale: 1 }],
  'grass-trees': [`${SK}/grass-trees.glb`, { scale: 1 }],
  'grass-trees-tall': [`${SK}/grass-trees-tall.glb`, { scale: 1 }],
  'house-a': [`${SK}/building-small-a.glb`, { scale: 1 }],
  'house-b': [`${SK}/building-small-b.glb`, { scale: 1 }],
  'house-c': [`${SK}/building-small-c.glb`, { scale: 1 }],
  'house-d': [`${SK}/building-small-d.glb`, { scale: 1 }],
  'garage': [`${SK}/building-garage.glb`, { scale: 1 }],
  // Kenney City Kit (Commercial) 2.1 via the netforge CC0 library
  ...Object.fromEntries('abcdefgh'.split('').map(c => [`bld-${c}`, [`${NF}/building_${c}.glb`, { scale: 1.05 }]])),
  ...Object.fromEntries('abc'.split('').map(c => [`tower-${c}`, [`${NF}/skyscraper_${c}.glb`, { scale: 1.05 }]])),
  // Kenney Car Kit
  ...Object.fromEntries(['sedan', 'taxi', 'suv', 'van', 'truck', 'truck_flat', 'police_car', 'ambulance', 'firetruck', 'garbage_truck', 'delivery_van', 'digger', 'tractor'].map(n => [n.replace('_', '-'), [`${NF}/${n}.glb`, { len: n === 'digger' ? 0.75 : n.includes('truck') ? 0.66 : 0.56 }]])),
  // Quaternius (CC0) nature and props
  'tree-oak': [`${NF}/tree_oak.glb`, { h: 0.8 }],
  'tree-fat': [`${NF}/tree_fat.glb`, { h: 0.75 }],
  'tree-pine': [`${NF}/tree_pine.glb`, { h: 0.9 }],
  'bush': [`${NF}/bush.glb`, { h: 0.22 }],
  'bush-large': [`${NF}/bush_large.glb`, { h: 0.32 }],
  'flower': [`${NF}/flower_red.glb`, { h: 0.12 }],
  'rock': [`${NF}/rock_small.glb`, { h: 0.12 }],
  'stump': [`${NF}/stump.glb`, { h: 0.12 }],
  'fence': [`${NF}/fence.glb`, { len: 1 }],
  'crate': [`${NF}/crate.glb`, { h: 0.18 }],
  'barrels': [`${NF}/barrels.glb`, { h: 0.2 }],
  'column': [`${NF}/column.glb`, { h: 0.5 }],
  'column-broken': [`${NF}/column_broken.glb`, { h: 0.35 }],
  'obelisk': [`${NF}/obelisk.glb`, { h: 1.2 }],
  'generator': [`${NF}/generator.glb`, { len: 0.7 }],
  'generator-large': [`${NF}/generator_large.glb`, { len: 1.3 }],
  'hangar': [`${NF}/hangar.glb`, { len: 2.6 }],
  'dish': [`${NF}/satellite_dish.glb`, { h: 0.6 }],
  'tent': [`${NF}/tent.glb`, { h: 0.35 }],
};

await MeshoptDecoder.ready;
const io = new NodeIO().registerExtensions(ALL_EXTENSIONS).registerDependencies({ 'meshopt.decoder': MeshoptDecoder });
const manifest = {};
for (const [id, [src, fit]] of Object.entries(LIST)) {
  if (!fs.existsSync(src)) { console.log('MISSING', id, src); continue; }
  const doc = await io.read(src);
  const root = doc.getRoot();
  // drop meshopt (page needs no decoder) and unlit (models get real sunlight)
  for (const e of root.listExtensionsUsed()) {
    if (e.extensionName === 'EXT_meshopt_compression' || e.extensionName === 'KHR_materials_unlit') e.dispose();
  }
  const scene = root.listScenes()[0];
  const b = getBounds(scene);
  const size = [b.max[0] - b.min[0], b.max[1] - b.min[1], b.max[2] - b.min[2]];
  let s = 1;
  if (fit.scale) s = fit.scale;
  if (fit.h) s = fit.h / size[1];
  if (fit.len) s = fit.len / Math.max(size[0], size[2]);
  if (fit.foot) s = fit.foot / Math.max(size[0], size[2]);
  const cx = (b.min[0] + b.max[0]) / 2, cz = (b.min[2] + b.max[2]) / 2;
  // wrap scene children in one node that recentres and scales
  const wrap = doc.createNode(id).setScale([s, s, s]).setTranslation([-cx * s, -b.min[1] * s, -cz * s]);
  for (const child of scene.listChildren()) { scene.removeChild(child); wrap.addChild(child); }
  scene.addChild(wrap);
  await doc.transform(dedup(), prune());
  const out = path.join(OUT, id + '.glb');
  await io.write(out, doc);
  const st = fs.statSync(out).size;
  manifest[id] = { size: size.map(v => +(v * s).toFixed(3)), bytes: st };
}
fs.writeFileSync(path.join(OUT, '..', 'manifest.json'), JSON.stringify(manifest, null, 1));
let total = 0; for (const v of Object.values(manifest)) total += v.bytes;
console.log(Object.keys(manifest).length, 'assets', (total / 1024).toFixed(0), 'KB');
for (const [k, v] of Object.entries(manifest)) console.log(k.padEnd(18), v.size.join(' x '), v.bytes);
