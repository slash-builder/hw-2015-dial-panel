"""
Dial Panel -- release drawing sheets, one per team, projected from the
verified CAD (cad/step/ in this repo).

Every line is FreeCAD hidden-line projection (TechDraw.projectEx) of the real
parts in their installed positions; the only drawn-on fills are the screen
(Horizon content, illustrative), the backlit band, the silver-silk knob and
the gold tab, each placed from the parts' own geometry. The Raspberry Pi
display STEP is not used here at all.

    /Applications/FreeCAD.app/Contents/Resources/bin/freecadcmd build_sheets.py
"""
import importlib.util
import math
import os

import FreeCAD as App
import Part
import TechDraw

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, "..", ".."))
CAD = os.path.join(REPO, "cad", "step")
# xxx5_drawing_kit.py: the shared palette / chrome / Horizon-screen helpers
_spec = importlib.util.spec_from_file_location(
    "board", os.path.join(HERE, "xxx5_drawing_kit.py"))
B = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(B)
f = B.f

TEAMS = {
    "ignition": dict(key="A", insert="04a-band-insert-ignition.step", name="A · IGNITION", label=B.FLARE500,
                     hero=B.TORCH500, dots=B.TORCH400, line="It's a sunrise. For the entryway or the kitchen: it greets you."),
    "nightfall": dict(key="B", insert="04b-band-insert-nightfall.step", name="B · NIGHTFALL", label=B.VIOLET400,
                      hero=B.VIOLET500, dots=B.VIOLET400, line="It's a starfield. For the hallway at night: it holds and watches."),
}

S3, S2, S6 = math.sqrt(3), math.sqrt(2), math.sqrt(6)
VIEWS = {
    "front": ((1, 0, 0), (0, 0, 1), (0, -1, 0)),
    "side": ((0, 1, 0), (0, 0, 1), (1, 0, 0)),
    "iso": ((1 / S2, 1 / S2, 0), (-1 / S6, 1 / S6, 2 / S6), (1 / S3, -1 / S3, 1 / S3)),
}


def load(name):
    s = Part.Shape()
    s.read(os.path.join(CAD, name))
    return s


def pt(view, p):
    r = VIEWS[view]
    return (sum(r[0][i] * p[i] for i in range(3)), sum(r[1][i] * p[i] for i in range(3)))


def project(shapes, view):
    r = VIEWS[view]
    m = App.Matrix(*r[0], 0, *r[1], 0, *r[2], 0, 0, 0, 0, 1)
    comp = Part.makeCompound([s.copy() for s in shapes])
    comp.transformShape(m)
    g = TechDraw.projectEx(comp, App.Vector(0, 0, 1))
    lines = []
    for gi in (0, 1, 3):
        if g[gi] is None or g[gi].isNull():
            continue
        for e in g[gi].Edges:
            n = 2 if e.Curve.TypeId == "Part::GeomLine" else max(6, int(e.Length / 1.2))
            lines.append([(p.x, p.y) for p in e.discretize(n)])
    return lines


def assembly_for(team):
    """The reference assembly with the band insert swapped for this team's."""
    asm = load("assembly-reference.step")
    ins = load(TEAMS[team]["insert"])
    ib = ins.BoundBox
    keep = []
    for so in asm.Solids:
        b = so.BoundBox
        same_slot = (abs(b.XMin - ib.XMin) < 0.2 and abs(b.YMin - ib.YMin) < 0.2 and abs(b.ZMin - ib.ZMin) < 0.2
                     and abs(b.YLength - ib.YLength) < 0.2)
        if not same_slot:
            keep.append(so)
    assert len(keep) == len(asm.Solids) - 1, "expected to replace exactly one insert solid"
    return keep + [ins.Solids[0]]


def screen_window(trim):
    """Inner opening of the silver trim ring, from its largest front face."""
    face = max((fc for fc in trim.Faces if abs(fc.normalAt(0, 0).y) > 0.99), key=lambda fc: fc.Area)
    inner = [w for w in face.Wires if not w.isSame(face.OuterWire)]
    bb = max(inner, key=lambda w: w.BoundBox.DiagonalLength).BoundBox
    return bb.XMin, bb.XMax, bb.ZMin, bb.ZMax


def sheet(team):
    T = TEAMS[team]
    parts = assembly_for(team)
    trim = load("03-screen-trim.step")
    wx0, wx1, wz0, wz1 = screen_window(trim)
    ins = load(T["insert"]).BoundBox
    # locate knob / gold tab in the assembly by their known sizes
    knob = next(s for s in parts if abs(s.BoundBox.XLength - 30) < 0.5 and abs(s.BoundBox.YLength - 18) < 0.5)
    tab = next(s for s in parts if abs(s.BoundBox.XLength - 13.7) < 0.3 and abs(s.BoundBox.YLength - 1.5) < 0.2)
    shell_parts = [s for s in parts if s.BoundBox.YMax > 20]
    front_parts = [s for s in parts if s.BoundBox.YMax <= 20]
    bb = Part.makeCompound(parts).BoundBox

    views = {v: project(parts, v) for v in VIEWS}
    ext = {}
    for v, ls in views.items():
        xs = [p[0] for l in ls for p in l]
        ys = [p[1] for l in ls for p in l]
        ext[v] = (min(xs), max(xs), min(ys), max(ys))

    W, H = 1700, 1200
    sc = 2.3
    out = [f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" role="img" aria-labelledby="t d">',
           f'<title id="t">Dial Panel · {T["name"]} · release drawing</title>',
           f'<desc id="d">Front, side and three-quarter views of the printable Dial Panel in the {T["name"]} scheme, '
           f'projected from the verified CAD, with dimensions, callouts and the printed parts list.</desc>',
           B.defs(), f'<rect width="{W}" height="{H}" fill="{B.V950}"/>']
    out.append(f'<text x="60" y="62" font-family="{B.MONO}" font-size="14" fill="{B.V300}" letter-spacing="2.2">'
               f'SLASHBUILDER · OPEN HARDWARE · DIAL PANEL · RELEASE DRAWING · PROJECTED FROM THE VERIFIED CAD · 2026-09-21</text>')
    out.append(f'<text x="60" y="122" font-family="{B.DISPLAY}" font-stretch="125%" font-weight="800" font-size="52" '
               f'fill="{B.V050}" letter-spacing="2">DIAL PANEL</text>')
    out.append(f'<text x="{W - 60}" y="122" font-family="{B.MONO}" font-size="18" fill="{T["label"]}" '
               f'letter-spacing="2.5" text-anchor="end">{T["name"]}</text>')
    out.append(f'<text x="60" y="152" font-family="{B.BODY}" font-size="17" fill="{B.V200}">{T["line"]}</text>')

    # layout: front large on the left, side + iso stacked right
    card = lambda x, y, w, h: B.rect(x, y, w, h, "url(#cardFloor)", 12, B.V700, 1)
    fx, fy, fw, fh = 40, 180, 1000, 600
    out.append(card(fx, fy, fw, fh))
    out.append(card(1060, 180, 600, 290))
    out.append(card(1060, 490, 600, 290))

    def place(v, cx, cy, s):
        x0, x1, y0, y1 = ext[v]
        return cx - (x0 + x1) / 2 * s, cy + (y0 + y1) / 2 * s

    origins = {"front": (place("front", fx + fw / 2, fy + fh / 2 + 10, sc), sc),
               "side": (place("side", 1060 + 300, 180 + 145, 1.15), 1.15),
               "iso": (place("iso", 1060 + 300, 490 + 145, 0.95), 0.95)}

    def P(v, x, y):
        (ox, oy), s = origins[v]
        return ox + x * s, oy - y * s

    # fills under the linework (front view only; everything else is line)
    (ox, oy), s = origins["front"]
    # wall wash: light AROUND the panel, clipped to the card, then the body's own
    # void face on top -- the light never paints the body (law 5)
    gclip = B.uid("wash")
    out.append(f'<clipPath id="{gclip}"><rect x="{fx}" y="{fy}" width="{fw}" height="{fh}" rx="12"/></clipPath>')
    out.append(f'<g clip-path="url(#{gclip})">'
               f'{B.glow(ox + ((bb.XMin + bb.XMax) / 2) * s, oy - ((bb.ZMin + bb.ZMax) / 2) * s, (bb.XLength / 2 + 45) * s, (bb.ZLength / 2 + 35) * s, T["hero"], 0.30)}</g>')
    bx_, bz_ = P("front", bb.XMin, bb.ZMax)
    out.append(B.rect(bx_, bz_, bb.XLength * s, bb.ZLength * s, "url(#voidBody)", 4))
    tr = trim.BoundBox
    tx0_, ty0_ = P("front", tr.XMin, tr.ZMax)
    out.append(B.rect(tx0_, ty0_, tr.XLength * s, tr.ZLength * s, "url(#chromeV)", 3))   # silver-silk trim
    bx0, by0 = P("front", ins.XMin, ins.ZMax)
    out.append(B.rect(bx0, by0, (ins.XMax - ins.XMin) * s, (ins.ZMax - ins.ZMin) * s, B.V950, 3))
    out.append(B.rect(bx0, by0, (ins.XMax - ins.XMin) * s, (ins.ZMax - ins.ZMin) * s, T["dots"], 3,
                      extra='opacity="0.55" filter="url(#blurXS)"'))
    kb = knob.BoundBox
    kx, ky = P("front", (kb.XMin + kb.XMax) / 2, (kb.ZMin + kb.ZMax) / 2)
    out.append(f'<circle cx="{f(kx)}" cy="{f(ky)}" r="{f(kb.XLength / 2 * s)}" fill="url(#chromeV)"/>')
    tb = tab.BoundBox
    tx, ty = P("front", tb.XMin, tb.ZMax)
    out.append(B.rect(tx, ty, tb.XLength * s, tb.ZLength * s, B.GOLD, 1))

    for v in VIEWS:
        segs = []
        for l in views[v]:
            q = [P(v, x, y) for x, y in l]
            segs.append("M" + " L".join(f"{f(a)} {f(b)}" for a, b in q))
        out.append(f'<path d="{" ".join(segs)}" fill="none" stroke="{B.V100}" stroke-width="0.9" '
                   f'stroke-linejoin="round" stroke-linecap="round" opacity="0.9"/>')

    # the screen goes on top: the display isn't in the assembly, so the
    # projection shows interior edges through the open window
    sx0, sy0 = P("front", wx0, wz1)
    out.append(f'<g transform="translate({f(sx0)} {f(sy0)}) scale({f(s)})">'
               f'{B.screen(0, 0, wx1 - wx0, wz1 - wz0, T["key"], 2, "23:05", seed=31)}</g>')

    # dimensions
    def dim(x1, y1, x2, y2, text, vertical=False):
        out.append(f'<g stroke="{B.V300}" stroke-width="1"><line x1="{f(x1)}" y1="{f(y1)}" x2="{f(x2)}" y2="{f(y2)}"/>')
        if vertical:
            out.append(f'<line x1="{f(x1 - 5)}" y1="{f(y1)}" x2="{f(x1 + 5)}" y2="{f(y1)}"/><line x1="{f(x2 - 5)}" y1="{f(y2)}" x2="{f(x2 + 5)}" y2="{f(y2)}"/></g>')
            my = (y1 + y2) / 2
            out.append(f'<text x="{f(x1 - 12)}" y="{f(my)}" font-family="{B.MONO}" font-size="13" fill="{B.V100}" '
                       f'text-anchor="middle" transform="rotate(-90 {f(x1 - 12)} {f(my)})">{text}</text>')
        else:
            out.append(f'<line x1="{f(x1)}" y1="{f(y1 - 5)}" x2="{f(x1)}" y2="{f(y1 + 5)}"/><line x1="{f(x2)}" y1="{f(y2 - 5)}" x2="{f(x2)}" y2="{f(y2 + 5)}"/></g>')
            out.append(f'<text x="{f((x1 + x2) / 2)}" y="{f(y1 + 20)}" font-family="{B.MONO}" font-size="13" fill="{B.V100}" '
                       f'text-anchor="middle">{text}</text>')

    x0, x1, y0, y1 = ext["front"]
    a, ya = P("front", x0, y0)
    b_, _ = P("front", x1, y0)
    dim(a, ya + 22, b_, ya + 22, f"{bb.XLength:.0f} W")
    _, yb = P("front", x0, y1)
    dim(a - 24, ya, a - 24, yb, f"{bb.ZLength:.0f} H", vertical=True)
    sx0_, sx1_, sy0_, sy1_ = ext["side"]
    c, yc = P("side", sx0_, sy0_)
    d, _ = P("side", sx1_, sy0_)
    dim(c, yc + 18, d, yc + 18, f"{bb.YLength:.0f} D (knob to wall)")

    for (v, lab, x, y) in (("front", "FRONT", fx + 24, fy + fh - 18), ("side", "SIDE · WALL AT RIGHT", 1084, 180 + 272),
                           ("iso", "3/4", 1084, 490 + 272)):
        out.append(f'<text x="{x}" y="{y}" font-family="{B.MONO}" font-size="12.5" fill="{B.V300}" letter-spacing="1.5">{lab}</text>')

    # parts + notes
    py = 830
    out.append(f'<text x="60" y="{py}" font-family="{B.MONO}" font-size="13" fill="{B.V300}" letter-spacing="2">PRINT</text>')
    rows = [("01a / 01b", "face plates, screen + column", "matte black PLA"),
            ("02a / 02b", "back shells, screen + column", "matte black PLA"),
            ("03", "screen trim", "silver silk PLA"),
            ("04" + ("a" if T["key"] == "A" else "b"), "band insert, " + ("ember" if T["key"] == "A" else "starfield"), "matte black PLA"),
            ("05", "band diffuser (speaker opening)", "clear PETG"),
            ("06", "knob", "silver silk PLA"),
            ("07", "gold tab", "yellow PLA"),
            ("08 / 11 / 12", "speaker cup · wall cleat · receiver rail", "matte black PLA")]
    for k, (n, what, mat) in enumerate(rows):
        yy = py + 28 + k * 23
        out.append(f'<text x="60" y="{yy}" font-family="{B.MONO}" font-size="13" fill="{B.V050}">{n}</text>'
                   f'<text x="170" y="{yy}" font-family="{B.BODY}" font-size="15" fill="{B.V100}">{what}</text>'
                   f'<text x="470" y="{yy}" font-family="{B.MONO}" font-size="12.5" fill="{B.V200}">{mat.upper()}</text>')
    notes = [("EVERY PART", "fits a 250 × 210 bed and prints without supports; two modules bolt together"),
             ("DRIVEN BY", "one dial: turn to move, push to open; home again after ~8 s idle"),
             ("MIC CUT", "the rocker breaks the mic's USB power; the gold tab sits beneath it"),
             ("TEAM", "set by the band insert you print and one setting; the body is the same"),
             ("STATUS", "CAD-verified, not yet printed or fitted; software not written yet")]
    for k, (h, t) in enumerate(notes):
        yy = py + 28 + k * 36
        out.append(f'<text x="860" y="{yy}" font-family="{B.MONO}" font-size="12.5" fill="{T["label"] if k == 0 else B.V300}" '
                   f'letter-spacing="1.5">{h}</text><text x="1000" y="{yy}" font-family="{B.BODY}" font-size="15" fill="{B.V100}">{t}</text>')
    out.append(f'<text x="60" y="{H - 24}" font-family="{B.MONO}" font-size="11.5" fill="{B.V400}" letter-spacing="1.3">'
               f'LINEWORK PROJECTED FROM THE STEP FILES · SCREEN IMAGE, BAND GLOW AND WALL WASH ARE ILLUSTRATIVE · '
               f'ONE TEAM PER DEVICE, FOR LIFE</text>')
    out.append("</svg>")
    path = os.path.join(HERE, f"dial-panel-{team}.svg")
    open(path, "w").write("\n".join(out))
    print("wrote", path, f"{bb.XLength:.1f} x {bb.YLength:.1f} x {bb.ZLength:.1f}")


for t in TEAMS:
    sheet(t)
