"""
xxx5 drawing kit -- palette, chrome, Horizon-screen and part helpers used by build_sheets.py.
(Originally the Thunderhead 2015 concept-board v2 generator; its main() still draws that board.)

Re-draws the twelve 2026-09-18 concepts leaning fully into the xxx5
xxx5 visual style guide
instead of the older Stone-body / gold-only-accent lock the first pass was
drawn under:

  - dark-native sheet on void-950; bodies in the VOID ramp (sec. 4.1, 13)
  - chrome by the required recipe, hard horizon flip at 50% (sec. 4.2),
    and held to trim/structure (law 6, <=20% of visible surface)
  - one team per device, for life (law 1): A/IGNITION or B/NIGHTFALL
  - team colour only as LIGHT -- screen content, backlit vents, washes on
    the surface below -- never as pigment on a body (law 5, ruling H1)
  - screens per the Horizon spec (sec. 11): horizon at 33%, 24 verticals,
    horizontals receding at ratio 1.34, one VP glow; A has a banded sun,
    B has stars and a cyan grid over deep violet
  - exactly one Golden Tab per device, in a void pocket at the mic's LIVE
    point, never touching chrome (sec. 3, law 4)
  - type: Archivo (expanded) display, Space Grotesk body, Space Mono labels

All twelve are front elevations at ONE common scale (0.9 px per mm), so
relative size on the sheet is real. Sketch fidelity: not CAD, not a spec.

    python3 thunderhead-2015-concept-board-v2-build.py
"""
import math
import os
import random

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "thunderhead-2015-concept-board-v2.svg")

# ---- tokens (hex values copied from the style guide's tables) ----------
V950, V900, V800, V700, V600, V500, V400, V300, V200, V100, V050 = (
    "#05060C", "#0A0C16", "#101426", "#171C33", "#222842", "#333A57",
    "#4C5573", "#6E7894", "#9AA3BA", "#C6CCDB", "#E6E9F1")
C_HI, C_FACE, C_MID, C_LOW, C_SHADOW = "#FFFFFF", "#DDE3EC", "#A9B2C3", "#6A7488", "#2E3545"
GOLD, GOLD_DARK = "#F5C842", "#C9A020"
FLARE500, FLARE400 = "#FF2A3C", "#FF6069"
TORCH500, TORCH400, TORCH300 = "#FF7A1A", "#FFA052", "#FFC694"
GRID_WARM = "#FFD7A8"
VIOLET700, VIOLET500, VIOLET400 = "#3B1180", "#7B2FF7", "#9E6BFF"
PULSE500 = "#FF2EC4"
CYAN = "#22E8E0"

TEAM = {
    "A": dict(name="A · IGNITION", hero=TORCH500, label=FLARE500, grid=TORCH500, glow=TORCH500),
    "B": dict(name="B · NIGHTFALL", hero=VIOLET500, label=VIOLET400, grid=CYAN, glow=VIOLET500),
}

DISPLAY = "'Archivo', 'Archivo Black', 'Helvetica Neue', Arial, sans-serif"
BODY = "'Space Grotesk', 'Helvetica Neue', Arial, sans-serif"
MONO = "'Space Mono', Menlo, monospace"

_uid = [0]


def uid(p):
    _uid[0] += 1
    return f"{p}{_uid[0]}"


def f(v):
    return f"{v:.2f}".rstrip("0").rstrip(".")


# ---- primitives (all in device millimetres; y up is negative) -----------
def rect(x, y, w, h, fill, rx=0, stroke=None, sw=1.0, extra=""):
    s = f' stroke="{stroke}" stroke-width="{f(sw)}"' if stroke else ""
    return f'<rect x="{f(x)}" y="{f(y)}" width="{f(w)}" height="{f(h)}" rx="{f(rx)}" fill="{fill}"{s} {extra}/>'


def body(x, y, w, h, rx=6):
    """A Void body: raised-surface gradient, void-600 edge, 1px top catch."""
    return (rect(x, y, w, h, "url(#voidBody)", rx, V600, 1.1)
            + f'<line x1="{f(x + rx)}" y1="{f(y + 0.8)}" x2="{f(x + w - rx)}" y2="{f(y + 0.8)}" '
              f'stroke="{V500}" stroke-width="0.9"/>')


def chrome(x, y, w, h, rx=2, horizontal=False):
    g = "chromeH" if horizontal else "chromeV"
    return (rect(x, y, w, h, f"url(#{g})", rx)
            + f'<line x1="{f(x + rx)}" y1="{f(y + 0.5)}" x2="{f(x + w - rx)}" y2="{f(y + 0.5)}" stroke="{C_HI}" stroke-width="0.9"/>'
            + f'<line x1="{f(x + rx)}" y1="{f(y + h - 0.5)}" x2="{f(x + w - rx)}" y2="{f(y + h - 0.5)}" stroke="{C_SHADOW}" stroke-width="0.9"/>')


def chrome_frame(x, y, w, h, t, rx=4, facets=True):
    """Chrome bezel ring of thickness t around an opening (evenodd)."""
    ox, oy, ow, oh = x + t, y + t, w - 2 * t, h - 2 * t
    d = (f"M{f(x + rx)} {f(y)} H{f(x + w - rx)} Q{f(x + w)} {f(y)} {f(x + w)} {f(y + rx)} V{f(y + h - rx)} "
         f"Q{f(x + w)} {f(y + h)} {f(x + w - rx)} {f(y + h)} H{f(x + rx)} Q{f(x)} {f(y + h)} {f(x)} {f(y + h - rx)} "
         f"V{f(y + rx)} Q{f(x)} {f(y)} {f(x + rx)} {f(y)} Z "
         f"M{f(ox)} {f(oy)} V{f(oy + oh)} H{f(ox + ow)} V{f(oy)} Z")
    s = f'<path d="{d}" fill="url(#chromeV)" fill-rule="evenodd" stroke="{C_SHADOW}" stroke-width="0.8"/>'
    if facets:  # grid-faceted corners: mitre lines catch the horizon
        for (ax, ay, bx, by) in ((x, y, ox, oy), (x + w, y, ox + ow, oy),
                                 (x, y + h, ox, oy + oh), (x + w, y + h, ox + ow, oy + oh)):
            s += f'<line x1="{f(ax)}" y1="{f(ay)}" x2="{f(bx)}" y2="{f(by)}" stroke="{C_LOW}" stroke-width="0.8"/>'
    return s


def screw(x, y, r=2.2):
    return (f'<circle cx="{f(x)}" cy="{f(y)}" r="{f(r)}" fill="url(#chromeV)" stroke="{C_SHADOW}" stroke-width="0.5"/>'
            f'<line x1="{f(x - r * 0.6)}" y1="{f(y)}" x2="{f(x + r * 0.6)}" y2="{f(y)}" stroke="{C_SHADOW}" stroke-width="0.6"/>')


def gold_tab(x, y, w=12, h=5):
    """The one Golden Tab: always seated in a Void pocket, never on chrome."""
    p = 3
    return (rect(x - p, y - p, w + 2 * p, h + 2 * p, V950, 1.5, V700, 0.8)
            + rect(x, y, w, h, GOLD, 1)
            + f'<line x1="{f(x + 1)}" y1="{f(y + h - 0.4)}" x2="{f(x + w - 1)}" y2="{f(y + h - 0.4)}" stroke="{GOLD_DARK}" stroke-width="0.8"/>')


def bat(x, y, angle=-18, length=24):
    """Chrome bat toggle: collar + bat, bat rotated to its thrown position."""
    return (f'<ellipse cx="{f(x)}" cy="{f(y)}" rx="7.5" ry="3.2" fill="url(#chromeV)" stroke="{C_SHADOW}" stroke-width="0.6"/>'
            f'<g transform="rotate({angle} {f(x)} {f(y)})">'
            f'{rect(x - 2.6, y - length, 5.2, length, "url(#chromeH)", 2.6, C_SHADOW, 0.6)}'
            f'<circle cx="{f(x)}" cy="{f(y - length)}" r="3.4" fill="url(#chromeV)" stroke="{C_SHADOW}" stroke-width="0.6"/></g>')


def engrave(x, y, text, size=5.5, anchor="start"):
    return (f'<text x="{f(x)}" y="{f(y)}" font-family="{MONO}" font-size="{f(size)}" fill="{V400}" '
            f'letter-spacing="0.6" text-anchor="{anchor}">{text}</text>')


def glow(cx, cy, rx, ry, color, op=0.22):
    return f'<ellipse cx="{f(cx)}" cy="{f(cy)}" rx="{f(rx)}" ry="{f(ry)}" fill="{color}" opacity="{op}" filter="url(#blur)"/>'


def vent(x, y, w, h, team, rx=3):
    pat = "ventB" if team == "B" else "ventA"
    return rect(x, y, w, h, V950, rx, V700, 0.8) + rect(x, y, w, h, f"url(#{pat})", rx)


def grille(x, y, w, h, rx=3, lit=None, pitch=6.0, r=1.8):
    """Perforated metal (sec. 13). Holes are drawn as real circles, not an
    SVG <pattern>: some renderers (macOS Quick Look among them) flatten fine
    patterns into a solid fill, and a grille that reads as a chrome slab
    also breaks the <=20% chrome budget. Unlit: chrome plate, void holes.
    Lit: dark plate, holes glowing with the team's emitted light."""
    cid = uid("gr")
    nx, ny = int((w - pitch) // pitch) + 1, int((h - pitch) // pitch) + 1
    ox = x + (w - (nx - 1) * pitch) / 2
    oy = y + (h - (ny - 1) * pitch) / 2
    holes = "".join(f'<circle cx="{f(ox + i * pitch + (pitch / 2 if j % 2 else 0))}" cy="{f(oy + j * pitch)}" r="{f(r)}"/>'
                    for j in range(ny) for i in range(nx - (1 if j % 2 else 0)))
    clip = f'<clipPath id="{cid}"><rect x="{f(x)}" y="{f(y)}" width="{f(w)}" height="{f(h)}" rx="{f(rx)}"/></clipPath>'
    if lit:
        c = TORCH400 if lit == "A" else VIOLET400
        return (clip + rect(x, y, w, h, V950, rx, C_LOW, 0.8)
                + f'<g clip-path="url(#{cid})"><g fill="{c}" opacity="0.55" filter="url(#blurXS)">{holes}</g>'
                  f'<g fill="{c}">{holes}</g></g>')
    return (clip + rect(x, y, w, h, "url(#chromeV)", rx, C_SHADOW, 0.8)
            + f'<g clip-path="url(#{cid})" fill="{V950}">{holes}</g>')


def screen(x, y, w, h, team, rx=3, readout=None, seed=1, vp_dx=0.0):
    """Horizon-spec screen content, clipped to the glass."""
    cid = uid("clip")
    t = TEAM[team]
    hy = y + h * (1 - 0.33)                 # horizon 33% up from the bottom
    vx = x + w / 2 + vp_dx * w              # vanishing point
    s = [f'<clipPath id="{cid}"><rect x="{f(x)}" y="{f(y)}" width="{f(w)}" height="{f(h)}" rx="{f(rx)}"/></clipPath>',
         f'<g clip-path="url(#{cid})">',
         rect(x, y, w, hy - y, "url(#sky)"),
         rect(x, hy, w, y + h - hy, "url(#groundB)" if team == "B" else V900)]
    # the one light source: a radial glow from the VP, team hero at 22%
    s.append(f'<ellipse cx="{f(vx)}" cy="{f(hy)}" rx="{f(0.4 * w)}" ry="{f(0.26 * w)}" fill="{t["hero"]}" '
             f'opacity="0.22" filter="url(#blurS)"/>')
    if team == "A":
        r = min(w, h) * 0.2
        sid = uid("sun")
        s.append(f'<clipPath id="{sid}"><rect x="{f(x)}" y="{f(y)}" width="{f(w)}" height="{f(hy - y)}"/></clipPath>')
        s.append(f'<g clip-path="url(#{sid})"><circle cx="{f(vx)}" cy="{f(hy)}" r="{f(r)}" fill="url(#sunA)"/>')
        for i, frac in enumerate((0.18, 0.36, 0.54, 0.72)):   # four void bands
            bh = r * (0.05 + 0.03 * i)
            s.append(rect(vx - r, hy - r * (1 - frac) * 0.95 + r * 0.02, 2 * r, bh, V900))
        s.append("</g>")
    else:
        rnd = random.Random(seed)
        for _ in range(int(w * h / 90)):
            sx = x + rnd.random() * w
            sy = y + (hy - y) * (rnd.random() ** 1.6)       # density falls toward the horizon
            sz = rnd.choice((0.35, 0.35, 0.35, 0.6, 0.6, 0.95))
            s.append(f'<circle cx="{f(sx)}" cy="{f(sy)}" r="{f(sz)}" fill="{V050}" opacity="{0.55 + rnd.random() * 0.45:.2f}"/>')
    # grid: 24 verticals converging on the VP; horizontals receding at 1.34
    g = [f'<g stroke="{t["grid"]}" stroke-opacity="0.35" stroke-width="0.7" fill="none">']
    for i in range(24):
        bx = x - w * 0.6 + (w * 2.2) * i / 23
        g.append(f'<line x1="{f(vx)}" y1="{f(hy)}" x2="{f(bx)}" y2="{f(y + h)}"/>')
    d = (y + h - hy) * 0.035
    yy = hy + d
    while yy < y + h:
        g.append(f'<line x1="{f(x)}" y1="{f(yy)}" x2="{f(x + w)}" y2="{f(yy)}"/>')
        d *= 1.34
        yy += d
    g.append("</g>")
    s += g
    s.append(f'<line x1="{f(x)}" y1="{f(hy)}" x2="{f(x + w)}" y2="{f(hy)}" stroke="{t["grid"]}" stroke-width="1.6" '
             f'opacity="0.6" filter="url(#blurXS)"/>')
    s.append(f'<line x1="{f(x)}" y1="{f(hy)}" x2="{f(x + w)}" y2="{f(hy)}" stroke="{t["grid"]}" stroke-width="0.6" opacity="0.9"/>')
    if readout:
        fs = max(6.5, h * 0.13)
        s.append(f'<text x="{f(x + w * 0.06)}" y="{f(y + fs * 1.25)}" font-family="{BODY}" font-weight="500" '
                 f'font-size="{f(fs)}" fill="{V050}" letter-spacing="0.4">{readout}</text>')
    s.append("</g>")
    s.append(rect(x, y, w, h, "none", rx, V600, 0.9))
    s.append(f'<path d="M{f(x + 2)} {f(y + 2)} L{f(x + w * 0.35)} {f(y + 2)} L{f(x + w * 0.2)} {f(y + h * 0.3)} Z" '
             f'fill="{V050}" opacity="0.04"/>')   # glass sheen
    return "".join(s)


# ---- the twelve devices (front elevations, mm, origin = ground centre) --
def d01_flight_deck():                                     # 240 W x 200 H
    s = [glow(0, -2, 150, 14, TORCH500, 0.30), body(-120, -200, 240, 200, 8)]
    s.append(chrome_frame(-104, -196, 208, 120, 18))
    s.append(screen(-86, -178, 172, 84, "A", 2, "07:15", vp_dx=0.08))
    for sx in (-97, 97):
        for sy in (-189, -83):
            s.append(screw(sx, sy, 2.0))
    s.append(grille(-92, -66, 184, 44, 4))
    s.append(rect(-110, -12, 220, 3.2, TORCH400, 1.6, extra='opacity="0.9"'))       # horizon light strip
    s.append(rect(-110, -12, 220, 3.2, TORCH500, 1.6, extra='filter="url(#blurXS)"'))
    s.append(bat(88, -200, -22, 26))
    s.append(gold_tab(104, -168, 8, 12))
    s.append(engrave(-110, -18, "2015"))
    return s


def d02_quiet_slate():                                     # 214 W x 185 H
    s = [glow(0, -2, 130, 12, VIOLET500, 0.25), body(-107, -58, 214, 58, 8)]
    s.append(vent(-92, -46, 184, 30, "B"))
    s.append(body(-96, -183, 192, 128, 7))
    s.append(rect(-88, -176, 176, 114, "none", 3, C_MID, 1.0))         # the one thin chrome rule
    s.append(screen(-85, -173, 170, 108, "B", 2, "23:05", seed=2))
    s.append(chrome(-16, -189, 32, 6, 3))                              # mic pod on the frame edge
    s.append(rect(24, -191, 16, 8, V950, 2, V700, 0.8))                # fenced toggle well
    s.append(rect(29.5, -196, 5, 9, "url(#chromeH)", 2))
    s.append(gold_tab(44, -189, 10, 4))
    s.append(engrave(-100, -5, "2015"))
    return s


def d03_sentinel():                                        # 480 H x 180 base
    s = [glow(0, -2, 120, 12, VIOLET500, 0.28)]
    s.append(body(-90, -38, 180, 38, 10))
    s.append(chrome(-80, -42, 160, 6, 3))
    s.append(chrome(-32, -300, 10, 258, 3, horizontal=True))           # chrome armature rails
    s.append(chrome(22, -300, 10, 258, 3, horizontal=True))
    s.append(vent(-18, -292, 36, 244, "B", 4))                         # starfield spine
    s.append(body(-66, -452, 132, 156, 10))
    s.append(screen(-54, -440, 108, 132, "B", 3, "23:05", seed=3))
    s.append(gold_tab(-7, -304, 14, 4))
    s.append(chrome(-40, -462, 80, 9, 4))                              # collar ring = the kill switch
    s.append(f'<path d="M-30 -462 Q-30 -480 0 -480 Q30 -480 30 -462 Z" fill="url(#voidBody)" stroke="{V600}" stroke-width="1"/>')
    for i in range(5):
        s.append(f'<circle cx="{-16 + i * 8}" cy="-469" r="1.2" fill="{V950}"/>')
    s.append(engrave(0, -12, "2015", anchor="middle"))
    return s


def d04_orb():                                             # dia 236
    s = [glow(0, -2, 130, 12, VIOLET500, 0.28)]
    s.append(body(-70, -22, 140, 22, 8))
    s.append(f'<ellipse cx="0" cy="-24" rx="104" ry="13" fill="url(#chromeV)" stroke="{C_SHADOW}" stroke-width="0.8"/>')
    s.append(f'<circle cx="0" cy="-140" r="118" fill="url(#sphere)" stroke="{V600}" stroke-width="1.1"/>')
    oid = uid("orb")
    s.append(f'<clipPath id="{oid}"><circle cx="0" cy="-140" r="114"/></clipPath>')
    s.append(f'<g clip-path="url(#{oid})">{vent(-80, -78, 160, 52, "B", 20)}</g>')     # starfield lower hemisphere
    s.append(screen(-78, -206, 156, 104, "B", 22, "23:05", seed=4))
    s.append(f'<ellipse cx="0" cy="-257" rx="17" ry="6" fill="url(#chromeV)" stroke="{C_SHADOW}" stroke-width="0.7"/>')
    s.append(f'<ellipse cx="0" cy="-258" rx="9" ry="3" fill="{V950}"/>')               # iris open
    s.append(gold_tab(-5, -259.4, 10, 2.8))
    s.append(engrave(0, -8, "2015", anchor="middle"))
    return s


def d05_monolith():                                        # 210 W x 400 H
    s = [glow(0, -2, 125, 12, VIOLET500, 0.26), body(-105, -392, 210, 380, 3)]
    s.append(rect(-115, -12, 230, 12, "url(#voidBody)", 2, V600, 1))
    s.append(chrome(-105, -400, 210, 9, 2))                            # mic bar across the top edge
    s.append(rect(40, -398, 26, 5, V950, 2))
    s.append(rect(44, -399, 8, 7, "url(#chromeH)", 2))                 # recessed kill slider
    s.append(gold_tab(-6, -384, 12, 4))
    s.append(f'<rect x="-96" y="-370" width="192" height="300" rx="2" fill="none" stroke="{CYAN}" '
             f'stroke-width="2.2" opacity="0.5" filter="url(#blurXS)"/>')  # edge glow, a hair past the glass
    s.append(screen(-94, -368, 188, 296, "B", 2, "23:05", seed=5))
    s.append(vent(-60, -58, 120, 24, "B"))
    s.append(engrave(-96, -40, "2015"))
    return s


def d06_assembly():                                        # 345 W x 260 H
    s = [glow(0, -2, 190, 14, TORCH500, 0.28)]
    s.append(chrome(-172, -112, 344, 8, 3))                            # the chromed docking spine
    s.append(body(-70, -102, 140, 96, 8))                              # brain block
    s.append(vent(-56, -88, 112, 40, "A"))
    s.append(rect(-150, -6, 300, 6, "url(#voidBody)", 2, V600, 0.8))
    s.append(body(-172, -258, 226, 144, 7))                            # screen module
    s.append(screen(-160, -246, 202, 120, "A", 2, "07:15", vp_dx=-0.05))
    s.append(body(62, -214, 110, 100, 7))                              # speaker module
    did = uid("disc")
    s.append(f'<clipPath id="{did}"><circle cx="117" cy="-164" r="38"/></clipPath>')
    s.append(f'<g clip-path="url(#{did})">{grille(79, -202, 76, 76, 0)}</g>')
    s.append(f'<circle cx="117" cy="-164" r="38" fill="none" stroke="{C_SHADOW}" stroke-width="0.9"/>')
    s.append(body(76, -258, 82, 38, 6))                                # mic crown module
    s.append(bat(136, -258, -20, 20))
    s.append(gold_tab(86, -246, 12, 5))
    for (x1, x2, y) in ((-172, 54, -112), (62, 172, -112), (-70, 70, -104)):   # dock seams glow
        s.append(f'<line x1="{x1}" y1="{y}" x2="{x2}" y2="{y}" stroke="{TORCH400}" stroke-width="1.4" filter="url(#blurXS)"/>')
    s.append(engrave(-60, -14, "2015"))
    return s


def d07_scout_base():                                      # 280 W x 176 H
    s = [glow(0, -2, 165, 12, TORCH500, 0.26), body(-140, -70, 280, 70, 8)]
    s.append(grille(-126, -58, 170, 44, 4))
    s.append(body(-132, -176, 190, 104, 7))
    s.append(screen(-122, -166, 170, 84, "A", 2, "07:15"))
    s.append(rect(62, -80, 70, 10, V950, 4, V700, 0.8))                # dock cradle
    s.append(rect(66, -79, 62, 2.2, V100, 1, extra='opacity="0.8" filter="url(#blurXS)"'))  # neutral: never colour for state
    s.append(body(72, -112, 50, 34, 10))                               # the scout
    s.append(chrome(70, -102, 54, 6, 3))
    for i in range(5):
        s.append(f'<circle cx="{82 + i * 7.5}" cy="-110" r="1.1" fill="{V950}"/>')
    s.append(bat(113, -112, -24, 16))
    s.append(gold_tab(78, -93, 10, 4))
    s.append(vent(56, -58, 72, 44, "A"))
    s.append(engrave(-126, -6, "2015"))
    return s


def d08_broadcast():                                       # 360 W x 285 H, wall
    s = [f'<rect x="-200" y="-330" width="400" height="330" fill="{V900}" opacity="0.55"/>',
         glow(0, -150, 210, 150, VIOLET500, 0.20)]                     # bounce light on the wall
    s.append(body(-180, -300, 360, 285, 8))
    s.append(chrome_frame(-168, -288, 336, 196, 14))
    s.append(screen(-154, -274, 308, 168, "B", 2, "23:05", seed=8))
    s.append(vent(-160, -80, 320, 50, "B"))
    s.append(rect(-60, -306, 120, 8, V950, 3))                          # mic lip
    s.append(chrome(-54, -305, 108, 5, 2))                              # pull-down cover, half drawn
    s.append(gold_tab(66, -305, 12, 4))
    s.append(engrave(-168, -22, "2015"))
    return s


def d09_jukebox():                                         # 240 W x 330 H
    s = [glow(0, -2, 150, 14, TORCH500, 0.30)]
    d = "M-120 -8 V-250 Q-120 -306 -64 -306 H64 Q120 -306 120 -250 V-8 Z"
    s.append(f'<path d="{d}" fill="url(#voidBody)" stroke="{V600}" stroke-width="1.1"/>')
    arch = "M-96 -150 V-236 Q-96 -284 -48 -284 H48 Q96 -284 96 -236 V-150 Z"
    s.append(f'<path d="{arch}" fill="url(#chromeV)" stroke="{C_SHADOW}" stroke-width="0.8"/>')
    s.append(screen(-80, -268, 160, 108, "A", 12, "07:15"))
    s.append(grille(-96, -136, 192, 104, 6, lit="A"))
    s.append(chrome(-104, -20, 208, 8, 3))
    s.append(f'<path d="M-24 -306 V-318 Q-24 -326 -16 -326 H16 Q24 -326 24 -318 V-306 Z" fill="url(#chromeV)" stroke="{C_SHADOW}" stroke-width="0.7"/>')
    for i in range(4):
        s.append(f'<circle cx="{-9 + i * 6}" cy="-316" r="1.2" fill="{V950}"/>')
    s.append(bat(84, -282, 28, 24))
    s.append(gold_tab(62, -296, 10, 5))
    s.append(rect(-90, -8, 24, 8, "url(#chromeV)", 2))
    s.append(rect(66, -8, 24, 8, "url(#chromeV)", 2))
    s.append(engrave(0, -142, "2015", 5, "middle"))
    return s


def d10_arcade():                                          # 220 W x 293 H
    s = [glow(0, -2, 140, 14, TORCH500, 0.30), body(-110, -62, 220, 62, 6)]
    s.append(rect(-24, -52, 48, 36, V950, 3, V700, 0.9))               # coin door, cracked open
    s.append(gold_tab(-7, -40, 14, 6))
    s.append(f'<path d="M-24 -52 L24 -52 L20 -60 L-20 -60 Z" fill="url(#chromeV)" stroke="{C_SHADOW}" stroke-width="0.7"/>')
    s.append(body(-100, -210, 200, 148, 5))
    s.append(grille(-70, -140, 140, 64, 4))
    s.append(chrome_frame(-96, -236, 192, 118, 14))
    s.append(screen(-82, -222, 164, 90, "A", 2, "07:15"))
    s.append(body(-100, -272, 200, 38, 5))                              # marquee
    s.append(screen(-90, -266, 180, 26, "A", 2, None))
    s.append(chrome(-34, -293, 68, 14, 5))                              # mic crown
    for i in range(6):
        s.append(f'<circle cx="{-20 + i * 8}" cy="-286" r="1.2" fill="{V950}"/>')
    s.append(engrave(0, -6, "2015", anchor="middle"))
    return s


def d11_visor():                                           # 320 W x 110 H
    s = [glow(0, -2, 170, 10, VIOLET500, 0.26), body(-120, -40, 240, 40, 8)]
    s.append(vent(-100, -32, 200, 22, "B"))
    brow = "M-160 -60 Q-160 -110 -120 -110 H120 Q160 -110 160 -60 Q160 -44 140 -44 H-140 Q-160 -44 -160 -60 Z"
    s.append(f'<path d="{brow}" fill="url(#chromeV)" stroke="{C_SHADOW}" stroke-width="0.9"/>')
    s.append(screen(-140, -96, 280, 38, "B", 10, None, seed=11))
    s.append(chrome(58, -97, 82, 40, 10))                               # brow shutter, part-drawn
    s.append(gold_tab(-6, -42, 12, 3.5))
    s.append(engrave(-110, -6, "2015"))
    return s


def d12_cel():                                             # 240 W x 200 H
    s = [glow(0, -2, 150, 13, TORCH500, 0.30), body(-120, -200, 240, 192, 26)]
    s.append(rect(-108, -186, 156, 128, V950, 22, V600, 1))            # deep CRT hood
    s.append(rect(-100, -178, 140, 112, "url(#hood)", 18))
    s.append(screen(-92, -170, 124, 96, "A", 14, "07:15"))
    s.append(f'<circle cx="84" cy="-146" r="27" fill="{V950}" stroke="{V700}" stroke-width="1"/>')
    for i in range(24):                                                # detent ring ticks
        a = math.radians(i * 15)
        s.append(f'<line x1="{f(84 + 24 * math.cos(a))}" y1="{f(-146 + 24 * math.sin(a))}" '
                 f'x2="{f(84 + 27 * math.cos(a))}" y2="{f(-146 + 27 * math.sin(a))}" stroke="{V400}" stroke-width="0.8"/>')
    s.append(f'<circle cx="84" cy="-146" r="20" fill="url(#chromeV)" stroke="{C_SHADOW}" stroke-width="0.8"/>')
    s.append(f'<rect x="82.5" y="-164" width="3" height="10" rx="1.5" fill="{C_SHADOW}"/>')
    s.append(rect(66, -98, 36, 20, V950, 4, V700, 0.8))               # rocker well
    s.append(f'<path d="M69 -95 L99 -91 L99 -81 L69 -85 Z" fill="url(#chromeV)" stroke="{C_SHADOW}" stroke-width="0.6"/>')
    s.append(gold_tab(78, -70, 12, 4))
    s.append(grille(-108, -48, 216, 30, 8))
    s.append(rect(-96, -8, 22, 8, "url(#chromeV)", 2))
    s.append(rect(74, -8, 22, 8, "url(#chromeV)", 2))
    s.append(engrave(-100, -52, "2015"))
    return s


DEVICES = [
    ("01", "FLIGHT DECK", "A", d01_flight_deck, "240 W × 200 H × 175 D",
     ["Grid-faceted chrome bezel with shown fasteners.", "Sunrise horizon; a torch light strip washes the desk.", "Hero chrome bat on the top edge; gold below it."]),
    ("02", "QUIET SLATE", "B", d02_quiet_slate, "214 W × 185 H × 150 D",
     ["Still the quiet one: one chrome rule, nothing else.", "Starfield vent across the plinth, lit from behind.", "Fenced toggle beside the mic pod."]),
    ("03", "SENTINEL", "B", d03_sentinel, "480 H × Ø180",
     ["Twin chrome rails carry a lit starfield spine.", "Portrait starfield face at eye height.", "The collar ring is the cut; gold sits just under it."]),
    ("04", "ORB", "B", d04_orb, "Ø236 on a chrome cradle",
     ["Void sphere, starfield lower hemisphere.", "Curved screen across the front third.", "Iris at the pole: open shows gold, closed hides it."]),
    ("05", "MONOLITH", "B", d05_monolith, "210 W × 400 H × 52 D",
     ["Void slab, near-bezelless starfield face.", "Cyan edge-glow a hair past the glass.", "Chrome mic bar with a recessed kill slider."]),
    ("06", "ASSEMBLY", "A", d06_assembly, "≈345 W × 260 H × 175 D",
     ["Void modules docked to one chrome spine.", "Every dock seam glows torch — real joints, lit.", "The mic crown pops off: a second honest cut."]),
    ("07", "SCOUT & BASE", "A", d07_scout_base, "280 W × 176 H × 155 D",
     ["Chrome-collared scout with its own bat and gold.", "The dock glow stays neutral: light never means state.", "Perforated chrome grille across the plinth."]),
    ("08", "BROADCAST PANEL", "B", d08_broadcast, "360 W × 285 H · wall",
     ["The wall is the canvas: violet bounce behind the panel.", "Starfield band backlit under the screen.", "Chrome cover pulls down over the mic lip."]),
    ("09", "JUKEBOX", "A", d09_jukebox, "240 W × 330 H × 190 D",
     ["Chrome arch dial over a sunrise.", "Perforated grille glows torch from behind.", "Hero bat on the shoulder, gold in its pocket."]),
    ("10", "ARCADE", "A", d10_arcade, "220 W × 293 H × 165 D",
     ["Lit marquee: a second, smaller horizon.", "Grid-faceted chrome bezel, perforated grille.", "Cracked-open coin door reveals the gold."]),
    ("11", "VISOR", "B", d11_visor, "320 W × 110 H × 140 D",
     ["One chrome brow; the screen is a starfield slit.", "The shutter draws across: the device closes its eye.", "Starfield vent in the base."]),
    ("12", "CEL", "A", d12_cel, "240 W × 200 H × 170 D",
     ["Deep void CRT hood around a sunrise.", "Chrome channel dial on a 24-detent ring.", "Chunky rocker for the cut, gold beneath it."]),
]


def defs():
    chrome_stops = ('<stop offset="0" stop-color="#FFFFFF"/><stop offset="0.10" stop-color="#DDE3EC"/>'
                    '<stop offset="0.42" stop-color="#A9B2C3"/><stop offset="0.50" stop-color="#2E3545"/>'
                    '<stop offset="0.50" stop-color="#DDE3EC"/><stop offset="0.58" stop-color="#A9B2C3"/>'
                    '<stop offset="0.82" stop-color="#6A7488"/><stop offset="0.94" stop-color="#DDE3EC"/>'
                    '<stop offset="1" stop-color="#FFFFFF"/>')
    return f"""<defs>
<style>@import url('https://fonts.googleapis.com/css2?family=Archivo:wdth,wght@125,800&amp;family=Space+Grotesk:wght@400;500&amp;family=Space+Mono&amp;display=swap');</style>
<linearGradient id="chromeV" x1="0" y1="0" x2="0" y2="1">{chrome_stops}</linearGradient>
<linearGradient id="chromeH" x1="0" y1="0" x2="1" y2="0">{chrome_stops}</linearGradient>
<linearGradient id="chromeText" gradientUnits="userSpaceOnUse" x1="0" y1="94" x2="0" y2="137">{chrome_stops}</linearGradient>
<linearGradient id="voidBody" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="{V800}"/><stop offset="1" stop-color="{V900}"/></linearGradient>
<linearGradient id="hood" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="{V700}"/><stop offset="1" stop-color="{V950}"/></linearGradient>
<linearGradient id="sky" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="{V950}"/><stop offset="1" stop-color="{V800}"/></linearGradient>
<linearGradient id="groundB" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="{VIOLET700}"/><stop offset="1" stop-color="{V950}"/></linearGradient>
<linearGradient id="sunA" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="{GRID_WARM}"/><stop offset="1" stop-color="{TORCH500}"/></linearGradient>
<radialGradient id="sphere" cx="0.38" cy="0.3" r="0.8"><stop offset="0" stop-color="{V600}"/><stop offset="0.35" stop-color="{V800}"/><stop offset="1" stop-color="{V950}"/></radialGradient>
<radialGradient id="cardFloor" cx="0.5" cy="1" r="0.9"><stop offset="0" stop-color="{V800}"/><stop offset="1" stop-color="{V900}"/></radialGradient>
<filter id="blur" x="-50%" y="-200%" width="200%" height="500%"><feGaussianBlur stdDeviation="9"/></filter>
<filter id="blurS" x="-50%" y="-50%" width="200%" height="200%"><feGaussianBlur stdDeviation="6"/></filter>
<filter id="blurXS" x="-20%" y="-300%" width="140%" height="700%"><feGaussianBlur stdDeviation="1.6"/></filter>
<pattern id="perf" width="6" height="6" patternUnits="userSpaceOnUse"><circle cx="3" cy="3" r="1.9" fill="{V950}"/></pattern>
<pattern id="perfA" width="6" height="6" patternUnits="userSpaceOnUse"><circle cx="3" cy="3" r="1.6" fill="{TORCH400}"/></pattern>
<pattern id="perfB" width="6" height="6" patternUnits="userSpaceOnUse"><circle cx="3" cy="3" r="1.6" fill="{VIOLET400}"/></pattern>
<pattern id="ventB" width="13" height="11" patternUnits="userSpaceOnUse">
  <circle cx="2" cy="2" r="0.9" fill="{V050}"/><circle cx="8.5" cy="5" r="0.6" fill="{CYAN}"/><circle cx="4.5" cy="8.5" r="1.2" fill="{VIOLET400}"/><circle cx="11" cy="9.5" r="0.5" fill="{V100}"/></pattern>
<pattern id="ventA" width="12" height="10" patternUnits="userSpaceOnUse">
  <circle cx="2" cy="2" r="1.0" fill="{TORCH300}"/><circle cx="8" cy="4.5" r="0.7" fill="{TORCH400}"/><circle cx="4.5" cy="8" r="1.2" fill="{TORCH500}"/><circle cx="10.5" cy="8.5" r="0.5" fill="{GRID_WARM}"/></pattern>
</defs>"""


def main():
    SCALE = 0.9
    COLS, ROWS = 4, 3
    CW, CH, GAP, M = 470, 660, 26, 64
    HEAD = 200
    W = 2 * M + COLS * CW + (COLS - 1) * GAP
    H = HEAD + ROWS * CH + (ROWS - 1) * GAP + 250
    out = [f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" role="img" aria-labelledby="t d">',
           '<title id="t">Thunderhead 2015 — concept board v2</title>',
           '<desc id="d">Twelve smart-hub concepts redrawn in the xxx5 style: void bodies, chrome trim, '
           'sunrise or starfield screens, one gold mark each, all at one common scale.</desc>',
           defs(), f'<rect width="{W}" height="{H}" fill="{V950}"/>']

    # header
    out.append(f'<text x="{M}" y="72" font-family="{MONO}" font-size="15" fill="{V300}" letter-spacing="2.4">'
               f'THUNDERHEAD XXX5 · CODE NAME ORRERY · CONCEPT BOARD V2 · 2026-09-21 · INTERNAL</text>')
    out.append(f'<text x="{M}" y="136" font-family="{DISPLAY}" font-stretch="125%" font-weight="800" font-size="58" '
               f'fill="{V050}" letter-spacing="2.3">2015'
               f'  — THE TWELVE, LEANING IN</text>')
    out.append(f'<text x="{M}" y="172" font-family="{BODY}" font-size="19" fill="{V200}">'
               f'Same twelve silhouettes as the first pass, redrawn for the line they belong to: void bodies, chrome as structure, '
               f'one team of light per device, one gold mark each.</text>')
    out.append(f'<text x="{W - M}" y="72" font-family="{MONO}" font-size="13" fill="{V300}" letter-spacing="1.6" '
               f'text-anchor="end">ALL TWELVE TO ONE SCALE · 0.9 PX / MM</text>')

    for i, (num, name, team, fn, dims, lines) in enumerate(DEVICES):
        col, row = i % COLS, i // COLS
        cx = M + col * (CW + GAP)
        cy = HEAD + 24 + row * (CH + GAP)
        t = TEAM[team]
        out.append(rect(cx, cy, CW, CH, "url(#cardFloor)", 10, V700, 1))
        stage_ground = cy + 480
        out.append(f'<line x1="{cx + 18}" y1="{stage_ground}" x2="{cx + CW - 18}" y2="{stage_ground}" stroke="{V600}" stroke-width="1"/>')
        out.append(f'<g transform="translate({cx + CW / 2} {stage_ground}) scale({SCALE})">{"".join(fn())}</g>')
        # labels
        ty = stage_ground + 44
        out.append(f'<text x="{cx + 22}" y="{ty}" font-family="{DISPLAY}" font-stretch="125%" font-weight="800" '
                   f'font-size="24" fill="{V050}" letter-spacing="1">{num} {name.replace("&", "&amp;")}</text>')
        out.append(f'<text x="{cx + CW - 22}" y="{ty}" font-family="{MONO}" font-size="12.5" fill="{t["label"]}" '
                   f'letter-spacing="1.5" text-anchor="end">{t["name"]}</text>')
        out.append(f'<text x="{cx + 22}" y="{ty + 24}" font-family="{MONO}" font-size="12" fill="{V300}" letter-spacing="1">'
                   f'{dims.upper()} MM</text>')
        for k, ln in enumerate(lines):
            out.append(f'<text x="{cx + 22}" y="{ty + 54 + k * 23}" font-family="{BODY}" font-size="15.5" fill="{V100}">'
                       f'{ln.replace("&", "&amp;")}</text>')

    # footer
    fy = HEAD + 24 + ROWS * (CH + GAP) + 20
    out.append(f'<line x1="{M}" y1="{fy}" x2="{W - M}" y2="{fy}" stroke="{V600}" stroke-width="1"/>')
    cols = [
        ("WHAT V2 PUSHES", V300, [
            "Void bodies replace Stone. Chrome follows the recipe, hard horizon at 50%.",
            "Every screen is the Horizon spec: a sunrise for A, a starfield for B.",
            "Team colour works as light: backlit vents, lit grilles, washes on desk and wall."]),
        ("RULES STILL HELD", V300, [
            "One team per device, for life. No A-to-B blends anywhere.",
            "No coloured bodies; chrome is trim and structure, well under 20%.",
            "Exactly one gold mark each, in a void pocket at the mic's LIVE point."]),
        ("READ BEFORE PICKING", FLARE400, [
            "Chrome is not FDM-native: this is the manufactured line, not the open build.",
            "Front elevations at sketch fidelity: no CAD, no acoustics, no program.",
            "Pick favourites; follow-ups go to proportions, materials and CAD."]),
    ]
    colw = (W - 2 * M) / 3
    for j, (head, hc, items) in enumerate(cols):
        x = M + j * colw
        out.append(f'<text x="{x}" y="{fy + 40}" font-family="{MONO}" font-size="13" fill="{hc}" letter-spacing="2">{head}</text>')
        for k, it in enumerate(items):
            out.append(f'<text x="{x}" y="{fy + 72 + k * 26}" font-family="{BODY}" font-size="16" fill="{V100}">{it}</text>')
    out.append(f'<text x="{M}" y="{H - 30}" font-family="{MONO}" font-size="12" fill="{V400}" letter-spacing="1.4">'
               f'A / IGNITION AND B / NIGHTFALL ARE THE ONLY TEAM NAMES THAT SHIP. SOURCE-FILM FACTION MARKS APPEAR NOWHERE.</text>')
    out.append("</svg>")
    open(OUT, "w").write("\n".join(out))
    print("wrote", OUT, f"{W}x{H}")


if __name__ == "__main__":
    main()
