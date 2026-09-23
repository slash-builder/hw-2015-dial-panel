"""
Generate the assembly step drawings in docs/assembly/.

Each step is projected from the real CAD (cad/step/*.step placed by
cad/assembly_placements.json), so the drawings match the parts exactly:
parts already fitted are drawn dim, the part going on in this step is drawn
bright, and an arrow shows which way it goes.

Every drawing states its viewpoint, so a photo can be shot to match and swap
in later.

    /Applications/FreeCAD.app/Contents/Resources/bin/freecadcmd docs/assembly/build_steps.py
"""
import importlib.util
import json
import math
import os

import FreeCAD as App
import Part
import TechDraw

HERE = os.path.dirname(os.path.abspath(__file__))
DOCS = os.path.dirname(HERE)
REPO = os.path.dirname(DOCS)
CAD = os.path.join(REPO, "cad", "step")
PLACEMENTS = os.path.join(REPO, "cad", "assembly_placements.json")
_spec = importlib.util.spec_from_file_location("kit", os.path.join(DOCS, "drawings", "xxx5_drawing_kit.py"))
K = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(K)
f = K.f

# viewpoints: name -> (right, up, toward-viewer). The name is printed on the
# drawing so a photo can be taken from the same place.
S2, S3, S6 = math.sqrt(2), math.sqrt(3), math.sqrt(6)
VIEWS = {
    "front-right 3/4": ((1 / S2, 1 / S2, 0), (-1 / S6, 1 / S6, 2 / S6), (1 / S3, -1 / S3, 1 / S3)),
    "front-left 3/4": ((1 / S2, -1 / S2, 0), (1 / S6, 1 / S6, 2 / S6), (-1 / S3, -1 / S3, 1 / S3)),
    "rear-right 3/4": ((-1 / S2, 1 / S2, 0), (-1 / S6, -1 / S6, 2 / S6), (1 / S3, 1 / S3, 1 / S3)),
    "front": ((1, 0, 0), (0, 0, 1), (0, -1, 0)),
}

STEPS = [
    dict(n=1, file="step-01-inserts.svg", view="rear-right 3/4",
         title="Heat-set the inserts",
         dim=[], hi=["01a-face-plate-screen", "01b-face-plate-column", "02a-back-shell-screen",
                     "02b-back-shell-column", "03-screen-trim", "12-cleat-receiver-rail"],
         explode={"01a-face-plate-screen": (0, -170, 0), "01b-face-plate-column": (150, -170, 0),
                  "02b-back-shell-column": (150, 0, 0), "03-screen-trim": (0, -300, 0),
                  "12-cleat-receiver-rail": (0, 150, 0)},
         caption="Every boss on the backs of the face plates, the shells' perimeter and seam bosses, the trim ring and the rail."),
    dict(n=2, file="step-02-rail.svg", view="rear-right 3/4",
         title="Receiver rail onto the back shell",
         dim=["02a-back-shell-screen"], hi=["12-cleat-receiver-rail"],
         explode={"12-cleat-receiver-rail": (0, 90, 0)}, arrow=("12-cleat-receiver-rail", (0, -1, 0)),
         caption="3 × M3 × 8 from inside the cavity. It must go on before the face plate closes."),
    dict(n=3, file="step-03-display.svg", view="front-right 3/4",
         title="Display and Pi into the shell",
         dim=["02a-back-shell-screen", "12-cleat-receiver-rail"], hi=[], hw=["display", "pi5-cooler"],
         caption="Lower the display module in through the open front; 4 × M2.5 from outside the back."),
    dict(n=4, file="step-04-audio.svg", view="front-right 3/4",
         title="Speaker, amp, level shifter",
         dim=["02a-back-shell-screen", "12-cleat-receiver-rail"], hi=["08-speaker-back-cup"], hw=["speaker", "amp"],
         caption="Speaker in from the front through the band opening, back-cup from outside; boards into their trays."),
    dict(n=5, file="step-05-leds.svg", view="front-right 3/4",
         title="LED strips",
         dim=["02a-back-shell-screen", "12-cleat-receiver-rail"], hi=[], hw=["band-led-run", "wash-led-run-screen"],
         caption="About 12 LEDs in the band groove facing forward, about 40 in the rear channel facing the wall."),
    dict(n=6, file="step-06-mic.svg", view="front-left 3/4",
         title="Microphone and the mic cut",
         dim=["02b-back-shell-column"], hi=[], hw=["mic-dongle"],
         caption="Mic in the cradle under the top ports. Cut only the red wire of the extension through the rocker."),
    dict(n=8, file="step-08-faceplate.svg", view="front-right 3/4",
         title="Dress the face plate",
         dim=["01a-face-plate-screen"], hi=["03-screen-trim", "04a-band-insert-ignition", "05-band-diffuser"],
         explode={"03-screen-trim": (0, -110, 0), "04a-band-insert-ignition": (0, 90, 0),
                  "05-band-diffuser": (0, 130, 0)},
         caption="Trim ring on the front, standing proud; band insert and diffuser behind the window."),
    dict(n=9, file="step-09-close-screen.svg", view="front-right 3/4",
         title="Close the screen module",
         dim=["02a-back-shell-screen", "12-cleat-receiver-rail", "03-screen-trim", "04a-band-insert-ignition",
              "05-band-diffuser"],
         hi=["01a-face-plate-screen"], explode={"01a-face-plate-screen": (0, -150, 0)},
         arrow=("01a-face-plate-screen", (0, 1, 0)),
         caption="6 × M3 × 12 from the back. Watch for pinched wires at the rim."),
    dict(n=10, file="step-10-column.svg", view="front-right 3/4",
         title="Build the control column",
         dim=["02b-back-shell-column"], hi=["01b-face-plate-column", "07-gold-tab"], hw=["ky040-module", "rocker-body"],
         explode={"01b-face-plate-column": (0, -150, 0), "07-gold-tab": (0, -190, 0)},
         arrow=("01b-face-plate-column", (0, 1, 0)),
         caption="Dial through its bushing hole, rocker snapped in, gold tab press-fit; 4 × M3 × 12 from the back."),
    dict(n=11, file="step-11-seam.svg", view="front-right 3/4",
         title="Join the two modules",
         dim=["01a-face-plate-screen", "02a-back-shell-screen", "03-screen-trim", "04a-band-insert-ignition",
              "05-band-diffuser", "12-cleat-receiver-rail"],
         hi=["01b-face-plate-column", "02b-back-shell-column", "07-gold-tab"],
         explode={"01b-face-plate-column": (120, 0, 0), "02b-back-shell-column": (120, 0, 0),
                  "07-gold-tab": (120, 0, 0)},
         arrow=("01b-face-plate-column", (-1, 0, 0)),
         caption="4 × M3 × 16 through the screen module into the column. Keep the fronts flush."),
    dict(n=12, file="step-12-knob.svg", view="front-right 3/4",
         title="Knob",
         dim=["01b-face-plate-column", "02b-back-shell-column", "07-gold-tab"], hi=["06-knob"],
         explode={"06-knob": (0, -70, 0)}, arrow=("06-knob", (0, 1, 0)),
         caption="Push it onto the D-shaft, pointer at the flat."),
    dict(n=13, file="step-13-hang.svg", view="rear-right 3/4",
         title="Hang it",
         dim=["02a-back-shell-screen", "02b-back-shell-column", "12-cleat-receiver-rail"], hi=["11-wall-cleat"],
         explode={"11-wall-cleat": (0, 120, 60)}, arrow=("11-wall-cleat", (0, -1, -0.5)),
         caption="Cleat to the wall, 45° face up and toward the wall; hook the rail over it. 66.6 mm off the wall."),
]

INK, DIMM, HI, ACCENT = K.V100, K.V400, K.V050, K.FLARE400


def load_placed():
    doc = json.load(open(PLACEMENTS))
    pl = doc["parts"] if "parts" in doc else doc
    parts = {}
    for fn in sorted(os.listdir(CAD)):
        if not fn.endswith(".step") or fn.startswith("assembly"):
            continue
        name = fn[:-5]
        s = Part.Shape()
        s.read(os.path.join(CAD, fn))
        m = pl.get(name, {}).get("matrix")
        if m:
            s = s.copy()
            s.transformShape(App.Matrix(*m))
        parts[name] = s
    hw = {}
    for key, spec in (doc.get("hardware") or {}).items():
        if "size" in spec:
            w, d, h = spec["size"]
            b = Part.makeBox(w, d, h, App.Vector(-w / 2, -d / 2, -h / 2))
        else:
            continue
        b.transformShape(App.Matrix(*spec["matrix"]))
        hw[key] = b
    return parts, hw


def project(shapes, view):
    r = VIEWS[view]
    comp = Part.makeCompound([s.copy() for s in shapes])
    comp.transformShape(App.Matrix(*r[0], 0, *r[1], 0, *r[2], 0, 0, 0, 0, 1))
    g = TechDraw.projectEx(comp, App.Vector(0, 0, 1))
    out = []
    for gi in (0, 1, 3):
        if g[gi] is None or g[gi].isNull():
            continue
        for e in g[gi].Edges:
            n = 2 if e.Curve.TypeId == "Part::GeomLine" else max(6, int(e.Length / 1.5))
            out.append([(p.x, p.y) for p in e.discretize(n)])
    return out


def pt(view, p):
    r = VIEWS[view]
    return (sum(r[0][i] * p[i] for i in range(3)), sum(r[1][i] * p[i] for i in range(3)))


def draw(step, parts, hw):
    view = step["view"]
    ex = step.get("explode", {})

    def placed(name):
        sh = parts[name]
        if name in ex:
            sh = sh.copy()
            sh.translate(App.Vector(*ex[name]))
        return sh

    dim_shapes = [placed(n) for n in step.get("dim", []) if n in parts]
    hi_shapes = [placed(n) for n in step.get("hi", []) if n in parts]
    hw_shapes = [hw[k] for k in step.get("hw", []) if k in hw]
    lines_dim = project(dim_shapes, view) if dim_shapes else []
    lines_hi = project(hi_shapes, view) if hi_shapes else []
    lines_hw = project(hw_shapes, view) if hw_shapes else []
    allpts = [p for group in (lines_dim, lines_hi, lines_hw) for l in group for p in l]
    if not allpts:
        raise SystemExit(f"step {step['n']}: nothing to draw")
    x0 = min(p[0] for p in allpts); x1 = max(p[0] for p in allpts)
    y0 = min(p[1] for p in allpts); y1 = max(p[1] for p in allpts)

    W, H = 1000, 640
    top, bottom = 96, 120
    s = min((W - 120) / max(x1 - x0, 1), (H - top - bottom) / max(y1 - y0, 1))
    ox = W / 2 - (x0 + x1) / 2 * s
    oy = top + (H - top - bottom) / 2 + (y0 + y1) / 2 * s

    def P(x, y):
        return ox + x * s, oy - y * s

    def path(lines, colour, width, opacity=1.0):
        if not lines:
            return ""
        segs = []
        for l in lines:
            q = [P(x, y) for x, y in l]
            segs.append("M" + " L".join(f"{f(a)} {f(b)}" for a, b in q))
        return (f'<path d="{" ".join(segs)}" fill="none" stroke="{colour}" stroke-width="{width}" '
                f'stroke-linejoin="round" stroke-linecap="round" opacity="{opacity}"/>')

    out = [f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" role="img" aria-labelledby="t d">',
           f'<title id="t">Step {step["n"]} · {step["title"]}</title>',
           f'<desc id="d">{step["caption"]} Viewpoint: {view}.</desc>',
           K.defs(), f'<rect width="{W}" height="{H}" fill="{K.V950}"/>',
           K.rect(16, 16, W - 32, H - 32, "url(#cardFloor)", 12, K.V700, 1)]
    out.append(f'<text x="44" y="56" font-family="{K.MONO}" font-size="13" fill="{K.V300}" letter-spacing="2">'
               f'STEP {step["n"]}</text>')
    out.append(f'<text x="44" y="84" font-family="{K.DISPLAY}" font-stretch="125%" font-weight="800" font-size="26" '
               f'fill="{K.V050}">{step["title"].upper()}</text>')
    out.append(f'<text x="{W - 44}" y="56" font-family="{K.MONO}" font-size="12" fill="{K.V400}" letter-spacing="1.5" '
               f'text-anchor="end">VIEW · {view.upper()}</text>')
    out.append(path(lines_dim, DIMM, 1.1, 1.0))          # already fitted
    out.append(path(lines_hw, ACCENT, 1.0, 0.5))          # bought parts, as proxies
    out.append(path(lines_hi, HI, 1.6))                   # this step's part

    if step.get("arrow"):
        name, direction = step["arrow"]
        if name in parts:
            c = placed(name).BoundBox.Center
            d = App.Vector(*direction).normalize()
            # from just behind the part, pointing the way it travels into place
            tail = P(*pt(view, (c.x - d.x * 14, c.y - d.y * 14, c.z - d.z * 14)))
            head = P(*pt(view, (c.x + d.x * 78, c.y + d.y * 78, c.z + d.z * 78)))
            ang = math.atan2(head[1] - tail[1], head[0] - tail[0])
            wing = [(head[0] - 16 * math.cos(ang - 0.4), head[1] - 16 * math.sin(ang - 0.4)),
                    (head[0] - 16 * math.cos(ang + 0.4), head[1] - 16 * math.sin(ang + 0.4))]
            out.append(f'<line x1="{f(tail[0])}" y1="{f(tail[1])}" x2="{f(head[0])}" y2="{f(head[1])}" '
                       f'stroke="{ACCENT}" stroke-width="2.4" stroke-linecap="round"/>')
            out.append(f'<polygon points="{f(head[0])},{f(head[1])} {f(wing[0][0])},{f(wing[0][1])} '
                       f'{f(wing[1][0])},{f(wing[1][1])}" fill="{ACCENT}"/>')

    out.append(f'<text x="44" y="{H - 62}" font-family="{K.BODY}" font-size="17" fill="{K.V100}">{step["caption"]}</text>')
    legend = []
    if lines_hi:
        legend.append(("this step", HI))
    if lines_dim:
        legend.append(("already fitted", DIMM))
    if lines_hw:
        legend.append(("bought part (illustrative)", ACCENT))
    x = 44
    for label, colour in legend:
        out.append(f'<line x1="{x}" y1="{H - 36}" x2="{x + 22}" y2="{H - 36}" stroke="{colour}" stroke-width="2.4"/>')
        out.append(f'<text x="{x + 30}" y="{H - 31}" font-family="{K.MONO}" font-size="11.5" fill="{K.V300}" '
                   f'letter-spacing="1">{label.upper()}</text>')
        x += 42 + len(label) * 7.4
    out.append("</svg>")
    path_out = os.path.join(HERE, step["file"])
    open(path_out, "w").write("\n".join(out))
    return path_out


def main():
    if not os.path.exists(PLACEMENTS):
        raise SystemExit("cad/assembly_placements.json not found: run cad/generate_parts.py first")
    parts, hw = load_placed()
    for step in STEPS:
        missing = [n for n in step.get("dim", []) + step.get("hi", []) if n not in parts]
        if missing:
            raise SystemExit(f"step {step['n']}: no such part {missing}")
        print("wrote", os.path.relpath(draw(step, parts, hw), REPO))


main()
