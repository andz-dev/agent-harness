"""Draw the Harness City L3 grid from one coordinate table: an ASCII block for DESIGN.md and an SVG plan.

Coordinates follow index.html: x east, z south, integers are cell centres. Ranges are inclusive.
  python3 tools/city_grid.py --ascii          print the DESIGN.md map block
  python3 tools/city_grid.py --write          write the SVG plan
  python3 tools/city_grid.py --check          fail on overlaps or a stale DESIGN.md block or SVG
"""

import argparse
import sys
from html import escape
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DESIGN = ROOT / "apps/harness-city/DESIGN.md"
SVG = ROOT / "apps/harness-city/assets/grid-map.svg"
X0, X1, Z0, Z1 = -24, 78, -30, 42
HIGHWAY = (63, 69)
WATER_Z, MOUNTAIN_Z, PORTAL_Z = 31, -21, -22

# name, ascii symbol, x0, x1, z0, z1, existing; plots must not overlap each other
PLOTS = [
    ("City core", ",", -4, 33, -4, 19, True),
    ("Bank", "B", -20, -15, 1, 6, False),
    ("Court", "J", -13, -8, 1, 6, False),
    ("Archive", "A", -20, -11, 9, 15, False),
    ("Airport station", "s", 37, 43, 1, 7, True),
    ("Airport", "P", 45, 61, 1, 7, True),
    ("Goods industry", "I", 48, 62, -18, -8, False),
    ("Shopping Mall", "M", 50, 58, 11, 17, False),
    ("Harbor quay", "H", 6, 32, 24, 30, False),
]
# ascii digit, label, colour from PILLARS in index.html, x0, x1, z0, z1
DISTRICTS = [
    ("1", "Verification", "#d64545", 10, 19, 1, 7),
    ("2", "Orientation", "#2f86c9", 21, 28, 1, 7),
    ("3", "Static guardrails", "#33489c", 1, 8, 9, 15),
    ("4", "Workflow entry", "#24946a", 1, 8, 1, 7),
    ("5", "Triggers", "#e0672b", 10, 15, 9, 15),
    ("6", "Parity", "#d9a42a", 17, 23, 9, 15),
    ("7", "Docs", "#8a5bb5", 25, 28, 9, 15),
]
CORE_ROADS = (
    [(x, z) for z in (0, 8, 16) for x in range(-4, 34)]
    + [(x, z) for x in (0, 9, 20, 29) for z in range(1, 8)]
    + [(x, z) for x in (0, 9, 16, 24, 29) for z in range(9, 16)]
    + [(x, z) for x in (9, 24) for z in range(17, 20)]
)
# name, cells, existing
ROADS = [
    ("airport roads", [(x, 0) for x in range(34, 45)] + [(44, z) for z in range(1, 8)], True),
    ("core connector z 8", [(x, 8) for x in range(34, 63)], True),
    ("industry land road z -6", [(x, -6) for x in range(48, 63)] + [(55, -7)], False),
    ("mall entry z 14", [(x, 14) for x in range(59, 63)], False),
    ("harbor spur z 30", [(x, 30) for x in range(33, 63)], False),
]
POWER = [
    ("today: pipeline parity", [(x, 17) for x in range(-2, 23)], True),
    ("west-east", [(x, 20) for x in range(-14, 45)] + [(22, z) for z in range(21, 24)], False),
    ("spur to airport and industry", [(44, z) for z in range(-9, 20)] + [(x, -9) for x in range(45, 48)], False),
]
RAIL = [(x, z) for z in (-3, -2) for x in range(-10, 44)]
# label, polyline of cell centres, label position
ROUTES = [
    ("goods truck", [(55, -8), (55, -6), (66, -6), (66, 14), (58, 14)], (57, -4)),
    ("core car", [(33, 8), (66, 8)], (35, 9.7)),
    ("airport car", [(53, 8), (53, 7)], (54, 6.3)),
    ("harbor truck", [(66, 14), (66, 30), (32, 30)], (45, 28.8)),
]
# id, x, z, short note, note side (full text in the DESIGN.md conflict table)
CONFLICTS = [
    ("C6", 48, 9.5, "one road at z 8", "start"),
    ("C8", 44, 11.5, "power spur x 44", "end"),
    ("C9", 66, -20, "portal and industry", "start"),
    ("C10", 51, -1, "airport moves dx -2", "start"),
    ("C11", 46, -3.5, "rail ends at x 43.5", "start"),
    ("C12", 58, 20, "tree keep-out", "start"),
    ("C13", 66, 2, "highway meaning", "start"),
    ("C14", 30, 22, "power line meaning", "start"),
]


def overlaps():
    found = []
    for i, (n1, _, a1, b1, c1, d1, _) in enumerate(PLOTS):
        for n2, _, a2, b2, c2, d2, _ in PLOTS[i + 1 :]:
            if a1 <= b2 and a2 <= b1 and c1 <= d2 and c2 <= d1:
                found.append(f"{n1} / {n2}")
    cells = [c for _, cs, _ in ROADS for c in cs] + RAIL
    for name, _, a, b, c, d, _ in PLOTS[1:]:
        if any(a <= x <= b and c <= z <= d for x, z in cells):
            found.append(f"road or rail inside {name}")
    return found


def ascii_map():
    grid = {(x, z): "~" if z >= WATER_Z else "^" if z <= MOUNTAIN_Z else "." for x in range(X0, X1 + 1) for z in range(Z0, Z1 + 1)}
    for _, sym, a, b, c, d, _ in PLOTS:
        grid.update({(x, z): sym for x in range(a, b + 1) for z in range(c, d + 1)})
    grid.update({cell: ":" for _, cells, _ in POWER for cell in cells})
    for sym, _, _, a, b, c, d in DISTRICTS:
        grid.update({(x, z): sym for x in range(a, b + 1) for z in range(c, d + 1)})
    grid.update({cell: "r" for cell in RAIL})
    grid.update({cell: "+" for cell in CORE_ROADS})
    grid.update({cell: "=" for _, cells, _ in ROADS for cell in cells})
    for z in range(Z0, Z1 + 1):
        for x in range(HIGHWAY[0], HIGHWAY[1] + 1):
            grid[x, z] = "T" if z < PORTAL_Z else "b" if z >= WATER_Z else "#"
    grid.update({(x, PORTAL_Z): "O" for x in range(HIGHWAY[0] - 1, HIGHWAY[1] + 2)})
    labels = [" "] * (X1 - X0 + 1)
    for x in range(X0, X1 + 1, 1):
        if x % 10 == 0:
            for k, ch in enumerate(f"x{x}"):
                if x - X0 + k < len(labels):
                    labels[x - X0 + k] = ch
    lines = ["      " + "".join(labels).rstrip(), "      " + "".join("|" if x % 10 == 0 else " " for x in range(X0, X1 + 1)).rstrip()]
    for z in range(Z0, Z1 + 1):
        head = f"z{z}" if z % 5 == 0 else ""
        lines.append(f"{head:<6}" + "".join(grid[x, z] for x in range(X0, X1 + 1)))
    return "\n".join(lines)


S, LEFT, TOP = 10, 44, 92
EXIST, PLAN = ("#2a9a66", "#dff1e6"), ("#e0782b", "#fdebdc")


def px(x):
    return LEFT + (x - X0 + 0.5) * S


def pz(z):
    return TOP + (z - Z0 + 0.5) * S


def rect(a, b, c, d, fill, stroke, extra=""):
    return f'<rect x="{px(a) - S / 2:g}" y="{pz(c) - S / 2:g}" width="{(b - a + 1) * S:g}" height="{(d - c + 1) * S:g}" fill="{fill}" stroke="{stroke}" {extra}/>'


def text(x, y, body, size=10, anchor="middle", fill="#1f2328", weight="normal"):
    return f'<text x="{x:g}" y="{y:g}" font-size="{size}" text-anchor="{anchor}" fill="{fill}" font-weight="{weight}">{escape(body)}</text>'


def line(cells, stroke, width, dash=""):
    pts = " ".join(f"{px(x):g},{pz(z):g}" for x, z in cells)
    return f'<polyline points="{pts}" fill="none" stroke="{stroke}" stroke-width="{width}" stroke-linejoin="round" {dash}/>'


def tint(colour, share=0.25):
    """Mix with white explicitly; some SVG renderers ignore fill-opacity."""
    rgb = [int(colour[i : i + 2], 16) for i in (1, 3, 5)]
    return "#" + "".join(f"{round(c * share + 255 * (1 - share)):02x}" for c in rgb)


def runs(cells):
    """Split a cell list into straight horizontal or vertical runs for drawing."""
    out, seen = [], set(cells)
    for x, z in sorted(seen, key=lambda c: (c[1], c[0])):
        if (x - 1, z) not in seen and (x + 1, z) in seen:
            end = x
            while (end + 1, z) in seen:
                end += 1
            out.append([(x, z), (end, z)])
    for x, z in sorted(seen):
        if (x, z - 1) not in seen and (x, z + 1) in seen:
            end = z
            while (x, end + 1) in seen:
                end += 1
            out.append([(x, z), (x, end)])
    return out


def svg_map():
    width, height = LEFT + (X1 - X0 + 1) * S + 16, TOP + (Z1 - Z0 + 1) * S + 24
    out = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}" font-family="sans-serif">',
        f'<rect width="{width}" height="{height}" fill="#ffffff"/>',
        text(LEFT, 22, "Harness City at level 3: grid plan", 16, "start", weight="bold"),
        text(
            LEFT,
            40,
            "Top-down, 1 cell = 1 unit, north up. Generated by tools/city_grid.py; conflicts C6-C14 are explained in DESIGN.md. ~ marks approximate.",
            11,
            "start",
            "#57606a",
        ),
    ]
    legend = [
        ("Existing", EXIST),
        ("Planned", PLAN),
        ("Highway", ("#6e7781", "#d0d7de")),
        ("Rail", ("#57606a", "none")),
        ("Power line", ("#bf8700", "none")),
        ("Traffic route", ("#8250df", "none")),
        ("Conflict", ("#cf222e", "#ffebe9")),
    ]
    for i, (name, (stroke, fill)) in enumerate(legend):
        x = LEFT + i * 128
        out.append(f'<rect x="{x}" y="54" width="16" height="12" fill="{fill}" stroke="{stroke}" stroke-width="2"/>')
        out.append(text(x + 22, 64, name, 11, "start"))
    out.append(rect(X0, X1, Z0, Z1, "#f6f8f1", "#d0d7de"))
    out.append(rect(X0, X1, Z0, MOUNTAIN_Z, "#e7ddd0", "none"))
    out.append(text(px(-10), pz(-26), "mountain range (planned)", 11, fill="#6f5b45"))
    out.append(rect(X0, X1, WATER_Z, Z1, "#d6ecfa", "none"))
    out.append(text(px(20), pz(37), "harbor water (planned)", 11, fill="#2f6f9f"))
    gx = [x for x in range(X0, X1 + 1) if x % 10 == 0]
    gz = [z for z in range(Z0, Z1 + 1) if z % 5 == 0]
    for x in gx:
        out.append(f'<line x1="{px(x):g}" y1="{TOP}" x2="{px(x):g}" y2="{pz(Z1) + S / 2:g}" stroke="#e1e4e8"/>')
        out.append(text(px(x), TOP - 6, f"x{x}", 9, fill="#57606a"))
    for z in gz:
        out.append(f'<line x1="{LEFT}" y1="{pz(z):g}" x2="{px(X1) + S / 2:g}" y2="{pz(z):g}" stroke="#e1e4e8"/>')
        out.append(text(LEFT - 6, pz(z) + 3, f"z{z}", 9, "end", "#57606a"))
    for name, _, a, b, c, d, existing in PLOTS:
        stroke, fill = EXIST if existing else PLAN
        out.append(rect(a, b, c, d, fill, stroke, 'stroke-width="1.5"' + ("" if existing else ' stroke-dasharray="5 3"')))
        if name != "City core":
            out.append(
                text(
                    (px(a) + px(b)) / 2,
                    (pz(c) + pz(d)) / 2 + 4,
                    name + ("" if existing else " (~)" if name in ("Bank", "Court", "Archive") else ""),
                    11,
                )
            )
    out.append(rect(47, 63, 1, 7, "none", "#cf222e", 'stroke-width="1" stroke-dasharray="2 3"'))
    out.append(text(px(55), pz(1) + 3, "airport in code today (x 47..63)", 9, fill="#cf222e"))
    for _, label, colour, a, b, c, d in DISTRICTS:
        out.append(rect(a, b, c, d, tint(colour, 0.3), colour, 'stroke-width="1.5"'))
        out.append(text((px(a) + px(b)) / 2, (pz(c) + pz(d)) / 2 + 4, label, 10))
    out.append(rect(HIGHWAY[0], HIGHWAY[1], PORTAL_Z, WATER_Z - 1, "#d0d7de", "#6e7781", 'stroke-dasharray="5 3"'))
    out.append(rect(HIGHWAY[0], HIGHWAY[1], Z0, PORTAL_Z - 1, "#e4e8ec", "#6e7781", 'stroke-dasharray="2 3"'))
    out.append(rect(HIGHWAY[0], HIGHWAY[1], WATER_Z, Z1, "#d0d7de", "#6e7781", 'stroke-dasharray="5 3"'))
    out.append(rect(HIGHWAY[0] - 1, HIGHWAY[1] + 1, PORTAL_Z, PORTAL_Z, "#8c959f", "#57606a"))
    out.append(text(px(74), pz(PORTAL_Z) + 4, "tunnel portal", 10, "start"))
    out.append(text(px(66), pz(-26), "tunnel", 10))
    out.append(text(px(66), pz(36), "bridge", 10))
    out.append(
        f'<text transform="translate({px(68):g},{pz(20):g}) rotate(90)" font-size="11" text-anchor="middle" fill="#1f2328">highway (planned)</text>'
    )
    for cells in runs(CORE_ROADS):
        out.append(line(cells, "#8c959f", 4))
    for _, cells, existing in ROADS:
        for seg in runs(cells):
            out.append(line(seg, EXIST[0] if existing else PLAN[0], 4, "" if existing else 'stroke-dasharray="6 3"'))
    for z in (-3, -2):
        out.append(line([(-10, z), (43, z)], "#57606a", 2))
    out.append(text(px(-14), pz(-2) + 3, "rail", 10, "end", "#57606a"))
    for _, cells, existing in POWER:
        for seg in runs(cells):
            out.append(line(seg, "#bf8700", 2, 'stroke-dasharray="1 4" stroke-linecap="round"' if not existing else ""))
    out.append(text(px(-14), pz(20) + 14, "power line west-east: harbor, airport, industry", 10, "start", "#9a6700"))
    for label, cells, (lx, lz) in ROUTES:
        out.append(line(cells, "#8250df", 1.5, 'stroke-dasharray="4 3" marker-end="url(#arrow)"'))
        out.append(text(px(lx), pz(lz), label, 9, "start", "#8250df"))
    out.insert(
        1,
        '<defs><marker id="arrow" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="6" markerHeight="6" orient="auto"><path d="M0 0 10 5 0 10z" fill="#8250df"/></marker></defs>',
    )
    for cid, x, z, note, side in CONFLICTS:
        out.append(f'<circle cx="{px(x):g}" cy="{pz(z):g}" r="9" fill="#ffebe9" stroke="#cf222e" stroke-width="1.5"/>')
        out.append(text(px(x), pz(z) + 3, cid, 8, fill="#cf222e", weight="bold"))
        out.append(text(px(x) + (12 if side == "start" else -12), pz(z) + 3, note, 9, side, "#cf222e"))
    out.append("</svg>")
    return "\n".join(out) + "\n"


def design_block():
    text_ = DESIGN.read_text(encoding="utf-8")
    start = text_.index("```text\n", text_.index("Grid map, one character per cell")) + len("```text\n")
    return text_[start : text_.index("\n```", start)]


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--ascii", action="store_true")
    group.add_argument("--write", action="store_true")
    group.add_argument("--check", action="store_true")
    args = parser.parse_args()
    if args.ascii:
        print(ascii_map())
        return 0
    if args.write:
        SVG.write_text(svg_map(), encoding="utf-8")
        print(f"wrote {SVG.relative_to(ROOT)}")
        return 0
    problems = overlaps()
    if design_block() != ascii_map():
        problems.append("DESIGN.md grid block is stale: python3 tools/city_grid.py --ascii")
    if not SVG.is_file() or SVG.read_text(encoding="utf-8") != svg_map():
        problems.append("grid SVG is stale: python3 tools/city_grid.py --write")
    for problem in problems:
        print("FAIL:", problem)
    if not problems:
        print("PASS: city grid")
    return 1 if problems else 0


if __name__ == "__main__":
    sys.exit(main())
