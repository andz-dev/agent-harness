#!/usr/bin/env python3
"""Build ONE self-contained html file (data + 3D models inlined, three.js from jsDelivr CDN).
It opens by double-click (file://) and can be uploaded anywhere or published as a web page.
   python3 tools/build_standalone.py [-o dist/harness-city.html] [--offline]
--offline inlines three.js too (adds ~1.3 MB, no network needed)."""
import argparse, json, re, base64
from pathlib import Path
root = Path(__file__).resolve().parent.parent
ap = argparse.ArgumentParser(); ap.add_argument("-o", default=str(root / "dist/harness-city.html")); ap.add_argument("--offline", action="store_true"); ap.add_argument("--airport", action="store_true", help="enable the airport prototype overlay")
a = ap.parse_args()
html = (root / "index.html").read_text()
data = json.loads((root / "data/cities.json").read_text())
assets = (root / "assets/assets.json").read_text()
cdn = '<script type="importmap">{"imports":{"three":"https://cdn.jsdelivr.net/npm/three@0.160.0/build/three.module.js","three/addons/":"https://cdn.jsdelivr.net/npm/three@0.160.0/examples/jsm/"}}</script>'
if a.offline:
    def mod(p): return "data:text/javascript;base64," + base64.b64encode((root / "vendor" / p).read_bytes()).decode()
    # GLTFLoader imports 'three' and ../utils/BufferGeometryUtils.js; rewrite both to data URLs
    util = mod("jsm/utils/BufferGeometryUtils.js").replace("data:", "data:")
    three = mod("three.module.js")
    gl = (root / "vendor/jsm/loaders/GLTFLoader.js").read_text().replace("'../utils/BufferGeometryUtils.js'", "'three-utils'")
    util_src = (root / "vendor/jsm/utils/BufferGeometryUtils.js").read_text()
    imap = {"three": three,
            "three-utils": "data:text/javascript;base64," + base64.b64encode(util_src.encode()).decode(),
            "three/addons/loaders/GLTFLoader.js": "data:text/javascript;base64," + base64.b64encode(gl.encode()).decode()}
    cdn = '<script type="importmap">' + json.dumps({"imports": imap}) + "</script>"
inline = ("<script>window.HARNESS_AIRPORT=true</script>" if a.airport else "") + "<script>window.HARNESS_CITY_DATA=" + json.dumps(data, separators=(",", ":")) + ";window.HARNESS_CITY_ASSETS=" + assets + ";</script>"
html = re.sub(r'<script type="importmap">.*?</script>', lambda m: cdn + inline, html, count=1, flags=re.S)
out = Path(a.o); out.parent.mkdir(parents=True, exist_ok=True); out.write_text(html)
print(f"wrote {out} ({out.stat().st_size/1e6:.1f} MB)")
