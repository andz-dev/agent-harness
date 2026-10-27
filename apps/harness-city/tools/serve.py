#!/usr/bin/env python3
"""Serve the package locally (browsers block fetch() on file:// pages).
   python3 tools/serve.py [port]   ->  http://localhost:8000/"""
import http.server, os, sys
os.chdir(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
port = int(sys.argv[1]) if len(sys.argv) > 1 else 8000
class H(http.server.SimpleHTTPRequestHandler):
    extensions_map = {**http.server.SimpleHTTPRequestHandler.extensions_map, ".js": "text/javascript", ".mjs": "text/javascript", ".glb": "model/gltf-binary"}
print(f"Harness City: http://localhost:{port}/  (Ctrl+C to stop)")
http.server.ThreadingHTTPServer(("127.0.0.1", port), H).serve_forever()
