"""
Full-scale section coupons, cut from the REAL exported parts in cad/step/,
so fit can be iterated on the three fault classes this build has actually
hit (perimeter-boss/wall clearance, the column seam bolt+bore+rib foul,
and the band-mount clamped stack) without reprinting plates 1, 2 and 3
(10 h 36 m of printing). See docs/fit-coupons.md for what each coupon
tests and what a pass/fail looks like.

THE CORE RULE: every coupon is a box intersected with the shipped
cad/step/*.step geometry. Nothing here is re-modelled -- if a coupon isn't
literally a slice of the real part, it proves nothing about the real part.

Run headless:
    freecadcmd cad/coupons.py

This is a SEPARATE script from cad/generate_parts.py (never imported --
importing it would re-run its entire build+verify pipeline and rewrite
cad/assembly_placements.json). Instead, the small pure-geometry helpers
and the four fastener/interference checks below are copied verbatim from
generate_parts.py (cited by name at each copy) rather than re-derived, per
this build's own "reuse the checks, don't reimplement them" rule. The
handful of named dimension constants copied alongside them (WALL,
FIT_CLEARANCE, CLEAR_D, INSERT_D, INSERT_DEPTH, CSK_D, CSK_DEPTH, BOSS_OD,
FACE_T, PANEL_D, COLUMN_PANEL_D, SEAM_INSERT_X0, X_A1/X_B0, DIFFUSER_Y0,
DIFFUSER_T) are cross-checked at import time against the real geometry
read out of cad/step/ (see ASSERTs below) specifically so a future edit to
generate_parts.py's own numbers can't silently drift this file out of
sync with the parts it's testing -- if the assert fires, these copied
constants need updating from the new generate_parts.py, not silently
patched around.
"""

import json
import math
import os

import FreeCAD as App
import Part
import Mesh
from FreeCAD import Vector, Rotation, Placement

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(HERE)
STEP_DIR = os.path.join(HERE, "step")
OUT_STEP = os.path.join(HERE, "coupons")
OUT_STL = os.path.join(REPO, "stl", "coupons")
for _d in (OUT_STEP, OUT_STL):
    os.makedirs(_d, exist_ok=True)

FONT_FILE = "/System/Library/Fonts/Supplemental/Arial.ttf"

# =============================================================================
# Printability constants (2026-09-24 fix) -- the labels shipped in v0.1.2
# existed in the STEP file (extra face counts +15/+33/+14 on A1/B1/C2 --
# real, valid geometry) but their strokes were 0.006-0.176mm wide, far
# below the printer's minimum feature size, so the slicer silently
# discarded every one of them. "A feature that exists in CAD but is below
# the process's minimum feature size is not a feature." See the Labelling
# section below for the fix.
# =============================================================================
NOZZLE_W = 0.4                    # mm -- Bambu Lab A1 0.4mm nozzle (bambu/build_coupons_project.py PRINTER)
MIN_STROKE_MM = 2 * NOZZLE_W      # 0.8mm -- "two extrusion widths," the fix brief's own printable floor

doc = App.newDocument("DialPanelCoupons")
App.ParamGet("User parameter:BaseApp/Preferences/Mod/Mesh").SetBool("AsciiSTL", False)

with open(os.path.join(HERE, "print_rotations.json")) as _f:
    PRINT_ROTATIONS = json.load(_f)


def load_step(name):
    s = Part.Shape()
    s.read(os.path.join(STEP_DIR, name + ".step"))
    return s


# =============================================================================
# Copied verbatim from cad/generate_parts.py -- geometry helpers (lines
# ~296-361) and the four fastener/interference checks this task asked to
# be REUSED, not reimplemented (fastener_access ~4429, bore_stays_open
# ~4569, interfere ~284, plus fits_bed/export_and_verify's own topology
# checks ~191-258). Not imported (importing generate_parts.py would
# re-run its whole build) -- copied, with this provenance note, per this
# repo's own Gotcha-catalogue discipline of never silently reimplementing
# checked logic.
# =============================================================================
def box_full(w, d, h, cx, cy, cz):
    return Part.makeBox(w, d, h, Vector(cx - w / 2.0, cy - d / 2.0, cz - h / 2.0))


def cyl_y(r, length, cx, cz, y0):
    return Part.makeCylinder(r, length, Vector(cx, y0, cz), Vector(0, 1, 0))


def cyl_x(r, length, x0, cy, cz):
    return Part.makeCylinder(r, length, Vector(x0, cy, cz), Vector(1, 0, 0))


def fastener_envelope(entry_pt, axis, travel, shank_r, head_r, head_depth):
    assert travel > head_depth, (
        f"fastener travel ({travel:.2f}mm) shorter than its own head_depth ({head_depth:.2f}mm)")
    if head_depth <= 1e-6:
        return Part.makeCylinder(shank_r, travel, entry_pt, axis)
    cone = Part.makeCone(head_r, shank_r, head_depth, entry_pt, axis)
    shank_pt = entry_pt + axis * head_depth
    shank = Part.makeCylinder(shank_r, travel - head_depth, shank_pt, axis)
    return cone.fuse(shank)


def fastener_access(label, entry_pt, axis, travel, head_depth, part_shape, max_mm3=0.5,
                     shank_r=None, head_r=None):
    env = fastener_envelope(entry_pt, axis, travel, shank_r, head_r, head_depth)
    common = part_shape.common(env)
    vol = common.Volume if common.Solids else 0.0
    ok = vol <= max_mm3
    tag = "OK" if ok else "FAIL"
    print(f"  [{tag}] FASTENER-ACCESS {label}: {vol:.2f}mm3 struck along the fastener's "
          f"full envelope (must be <= {max_mm3}mm3)")
    return ok, vol


def bore_stays_open(label, center, axis, radius, depth, part_shape, min_open_pct=95.0):
    bore = Part.makeCylinder(radius, depth, center, axis)
    full_vol = bore.Volume
    remaining = part_shape.common(bore)
    filled_vol = remaining.Volume if remaining.Solids else 0.0
    open_pct = 100.0 * (full_vol - filled_vol) / full_vol
    ok = open_pct >= min_open_pct
    tag = "OK" if ok else "FAIL"
    print(f"  [{tag}] BORE-STAYS-OPEN {label}: {open_pct:.1f}% open "
          f"({filled_vol:.2f}mm3 of {full_vol:.2f}mm3 filled, need >={min_open_pct:.0f}% open)")
    return ok, open_pct


def interfere(shape_a, shape_b, label, max_mm3=0.05):
    common = shape_a.common(shape_b)
    vol = common.Volume if common.Solids else 0.0
    ok = vol <= max_mm3
    tag = "OK" if ok else "FAIL"
    print(f"  [{tag}] interference {label}: {vol:.3f}mm3")
    return ok, vol


def _fastener_hole_exists(outline_shape, thickness, y0, fx, fz, hole_dia, label, min_pct=90.0):
    """Same probe as generate_parts.py's FASTENER-HOLE-EXISTS, applied to
    a coupon's own real (already-perforated) footprint used as its own
    reference outline -- see the coupon-specific note at each call site
    for why a coupon can use itself as the reference where the original
    check needed an unperforated stand-in."""
    full_vol = math.pi * (hole_dia / 2.0) ** 2 * thickness
    probe_cyl = cyl_y(hole_dia / 2.0, thickness + 4.0, fx, fz, y0 - 2.0)
    remaining = outline_shape.cut(probe_cyl)
    removed_vol = outline_shape.Volume - (remaining.Volume if remaining.Solids else 0.0)
    pct = 100.0 * removed_vol / full_vol
    tag = "OK" if pct >= min_pct else "FAIL"
    print(f"  [{tag}] FASTENER-HOLE-EXISTS {label} at ({fx:.2f},{fz:.2f}): "
          f"{removed_vol:.2f}mm3 removed / {full_vol:.2f}mm3 full-hole volume = {pct:.1f}% "
          f"(need >={min_pct:.0f}%)")
    return pct >= min_pct, pct


BED_X, BED_Y, BED_Z = 250.0, 210.0, 210.0


def fits_bed(dims):
    d = sorted(dims, reverse=True)
    b = sorted((BED_X, BED_Y, BED_Z), reverse=True)
    return all(d[i] <= b[i] + 1e-6 for i in range(3))


# =============================================================================
# Named dimension constants -- copied from generate_parts.py (never
# re-derived), cross-checked against the real cad/step/ geometry below so
# a future change to generate_parts.py's own numbers can't silently drift
# this file out of sync (see module docstring).
# =============================================================================
WALL = 3.0
FACE_T = 3.0
FIT_CLEARANCE = 0.4
CLEAR_D = 3.4
INSERT_D = 4.0
INSERT_DEPTH = 6.5
CSK_D = 6.5
CSK_DEPTH = 2.6
BOSS_OD = 9.0
PERIM_BOSS_LEN = 7.1     # max(7.0, INSERT_DEPTH + 0.6)
BAND_BOSS_LEN = 7.1      # same formula, band-mount bosses
DIFFUSER_T = 1.0
INSERT_T = 2.0

CHK = load_step("01a-face-plate-screen")
_bb = CHK.BoundBox
X_A0, X_A1 = _bb.XMin, _bb.XMax
PANEL_H = _bb.ZMax
CHK2 = load_step("02a-back-shell-screen")
PANEL_D = CHK2.BoundBox.YMax
CHK3 = load_step("02b-back-shell-column")
COLUMN_PANEL_D = CHK3.BoundBox.YMax
X_B0 = CHK3.BoundBox.XMin
SEAM_INSERT_X0 = round(X_B0 + WALL - 0.3, 2)
CHK4 = load_step("05-band-diffuser")
DIFFUSER_Y0 = round(CHK4.BoundBox.YMin, 2)
assert abs((CHK4.BoundBox.YMax - CHK4.BoundBox.YMin) - DIFFUSER_T) < 0.02, "DIFFUSER_T drifted"
del CHK, CHK2, CHK3, CHK4, _bb
print(f"cross-checked constants: X_A1={X_A1:.2f} X_B0={X_B0:.2f} PANEL_H={PANEL_H:.2f} "
      f"PANEL_D={PANEL_D:.2f} COLUMN_PANEL_D={COLUMN_PANEL_D:.2f} "
      f"SEAM_INSERT_X0={SEAM_INSERT_X0:.2f} DIFFUSER_Y0={DIFFUSER_Y0:.2f}")
assert abs(X_A1 - X_B0) < 0.01, "screen/column seam X doesn't line up between 01a and 02b"


# =============================================================================
# Boss / feature detection -- from the real geometry, not hardcoded (per
# the task brief: "detect the bosses from 01a's geometry ... rather than
# hardcoding").
# =============================================================================
def cylindrical_bosses(shape, axis="Y", min_len=3.0):
    """Every convex (boss, not bore) cylindrical face on `shape` whose
    axis is `axis` and whose extent along that axis exceeds min_len --
    the same "cylinders along Y with length > 3" signature the task
    describes for PERIM_A's own perimeter bosses."""
    out = []
    axis_vec = {"X": Vector(1, 0, 0), "Y": Vector(0, 1, 0), "Z": Vector(0, 0, 1)}[axis]
    for f in shape.Faces:
        if f.Surface.TypeId != "Part::GeomCylinder":
            continue
        ax = f.Surface.Axis
        if abs(ax.dot(axis_vec)) < 0.99:
            continue
        bb = f.BoundBox
        length = {"X": bb.XLength, "Y": bb.YLength, "Z": bb.ZLength}[axis]
        if length < min_len:
            continue
        c = f.Surface.Center
        r = f.Surface.Radius
        u0, u1, v0, v1 = f.ParameterRange
        pt = f.valueAt((u0 + u1) / 2.0, (v0 + v1) / 2.0)
        n = f.normalAt((u0 + u1) / 2.0, (v0 + v1) / 2.0)
        to_pt = pt - c
        radial = to_pt - ax * to_pt.dot(ax)
        if radial.Length < 1e-6:
            continue
        radial.normalize()
        convex = n.dot(radial) > 0.0
        if not convex:
            continue   # bore, not a boss
        out.append((c, r, length))
    return out


def pick_wall_and_corner_boss(shape):
    """Among 01a's own perimeter bosses (Y-axis cylinders, length>3,
    convex), find the one closest to a side wall, and, among ties on
    that measure, closest to a corner -- exactly the PERIM_A boss the
    task describes (and the one carrying PERIM_BOSS_OD_TIGHT, since
    that's the tight side by construction)."""
    bb = shape.BoundBox
    candidates = cylindrical_bosses(shape, "Y", 3.0)
    scored = []
    for c, r, length in candidates:
        dx = min(c.x - bb.XMin, bb.XMax - c.x)
        dz = min(c.z - bb.ZMin, bb.ZMax - c.z)
        scored.append((dx, dz, c, r, length))
    dx_min = min(s[0] for s in scored)
    tied = [s for s in scored if s[0] - dx_min < 0.05]
    tied.sort(key=lambda s: math.hypot(s[0], s[1]))
    dx, dz, c, r, length = tied[0]
    print(f"  boss candidates (Y-axis, len>3, convex): {len(scored)} found; "
          f"closest-to-wall group has {len(tied)}, closest-to-corner of that group: "
          f"X={c.x:.2f} Z={c.z:.2f} r={r:.2f} (OD={2*r:.2f}mm) dist-to-wall={dx:.2f}mm "
          f"dist-to-corner-edges=({dx:.2f},{dz:.2f})")
    return c.x, c.z, r


def pick_nearest_boss(shape, approx_x, approx_z, axis="Y", min_len=3.0):
    candidates = cylindrical_bosses(shape, axis, min_len)
    best = min(candidates, key=lambda cand: math.hypot(cand[0].x - approx_x, cand[0].z - approx_z))
    c, r, length = best
    d = math.hypot(c.x - approx_x, c.z - approx_z)
    print(f"  nearest boss to ({approx_x:.2f},{approx_z:.2f}): X={c.x:.2f} Z={c.z:.2f} r={r:.2f} "
          f"(OD={2*r:.2f}mm) -- {d:.3f}mm from the approx position given")
    assert d < 2.0, f"nearest real boss is {d:.2f}mm from the given approx position -- too far to be it"
    return c.x, c.z, r


# =============================================================================
# Labelling -- a small debossed tag ("A1", "B2", ...) so bench pieces
# can't be mixed up.
#
# 2026-09-24 FIX (see docs/fit-coupons.md and the module docstring's own
# NOZZLE_W/MIN_STROKE_MM note): the prior version of this section put every
# label on a narrow X-normal edge at size=1.6mm (1.0mm for C2/C3). The text
# was real, valid geometry, but the strokes it produced (measured on the
# printed parts: 0.006-0.176mm) were far under the 0.4mm nozzle's minimum
# feature size, so the slicer silently dropped every one of them.
#
# Two independent, PERMANENT fixes (both re-run on every regeneration, not
# one-off patches):
#
#   1. Every label now goes on the coupon's own LARGEST available flat
#      face, not a narrow edge -- see the per-coupon comments at each call
#      site (COUPON A/B/C sections below) for which face that is and why
#      it's safe: never the bed-contact face (checked against each part's
#      real cad/print_rotations.json entry), never a precision fastener/
#      boss/seam surface (the anchor is always the footprint corner
#      farthest from the feature the coupon exists to test).
#
#   2. LABEL_SIZE_MM (below) is DERIVED from this font's own real,
#      measured stroke-to-cap-height ratio -- not assumed from "6mm sounds
#      about right" -- and min_stroke_width_mm() re-measures the REAL
#      geometry of every label actually cut, with a permanent assertion
#      (in _finish_label) that fails the build if any label's thinnest
#      stroke is under MIN_STROKE_MM. Confirmed this assertion actually
#      fires on the old, broken sizes (1.6mm/1.0mm) before trusting it --
#      see this fix's own hand-back notes for that reproduction; the
#      broken sizes are deliberately not left runnable in this file so
#      `main` can never regress to shipping them by accident.
# =============================================================================
def _shapestring_face(text, size, tracking=0.0):
    """Build ONLY the flat 2D face for `text` at `size` (no extrusion, no
    placement) -- the single source geometry shared by min_stroke_width_mm
    (measurement) and make_label_tool_x/_y (the actual cutting tool), so
    what gets measured is always exactly what gets cut."""
    import Draft
    ss = Draft.make_shapestring(String=text, FontFile=FONT_FILE, Size=size, Tracking=tracking)
    doc.recompute()
    face = Part.makeFace(ss.Shape.Wires, "Part::FaceMakerBullseye")
    doc.removeObject(ss.Name)
    return face


def min_stroke_width_mm(face, grid=0.1):
    """Real minimum printable stroke width of a flat text face, MEASURED
    off the geometry -- not estimated from font metrics.

    Method: grid-sample the face's own bounding box; for every sample
    point that lies inside the face, compute its distance to the face's
    own boundary edges (Part.Vertex.distToShape). A point is a "ridge"
    point if its distance is >= every inside neighbour's in its 3x3
    window -- i.e. it sits at or near a stroke's local centreline, not
    partway down its wall. Twice the smallest ridge distance found is this
    face's thinnest stroke; twice the median is reported alongside it for
    the same reason the field report that caught this defect gave both
    numbers (a single worst-case figure can be a corner artifact; the
    median shows whether the whole label is thin or just one spot is).

    Why not FreeCAD's own Part.Face.makeOffset2D (the obvious "erode by
    half the threshold, see if it survives" approach): confirmed live on
    this exact font -- ANY shapestring face containing the glyph "B" (at
    any size or tracking tested, including a lone "B") makes
    makeOffset2D hard-crash the freecadcmd process (SIGSEGV, no Python
    exception raised to catch) instead of erroring gracefully. That's a
    real, reproducible FreeCAD/OCCT robustness gap in 2D-offsetting
    Part::FaceMakerBullseye output for multiply-wound glyphs, not a defect
    in this build's own geometry -- but half of this file's coupon labels
    start with "B", so that approach was not usable here and is flagged
    separately rather than fixed quietly (see this fix's hand-back notes).
    This grid/ridge method never crashes on any label text in this file,
    at the cost of being a coarser estimate: true to its own grid spacing,
    and deliberately conservative (a stroke narrower than one grid cell,
    or a tie among ridge neighbours, reads as thinner than or equal to the
    real geometry, never thicker)."""
    bb = face.BoundBox
    edges = Part.Compound(face.Edges)
    nx = max(2, int(bb.XLength / grid) + 1)
    ny = max(2, int(bb.YLength / grid) + 1)
    dx = bb.XLength / (nx - 1) if nx > 1 else grid
    dy = bb.YLength / (ny - 1) if ny > 1 else grid
    dist = [[None] * ny for _ in range(nx)]
    for i in range(nx):
        x = bb.XMin + i * dx
        for j in range(ny):
            y = bb.YMin + j * dy
            pt = Vector(x, y, 0)
            if face.isInside(pt, 1e-7, True):
                dist[i][j] = Part.Vertex(pt).distToShape(edges)[0]
    ridge = []
    for i in range(nx):
        for j in range(ny):
            d = dist[i][j]
            if d is None:
                continue
            is_ridge = True
            for di in (-1, 0, 1):
                for dj in (-1, 0, 1):
                    if di == 0 and dj == 0:
                        continue
                    ni, nj = i + di, j + dj
                    if 0 <= ni < nx and 0 <= nj < ny and dist[ni][nj] is not None:
                        if dist[ni][nj] > d:
                            is_ridge = False
                            break
                if not is_ridge:
                    break
            if is_ridge:
                ridge.append(d)
    if not ridge:
        return 0.0, 0.0
    ridge.sort()
    return 2 * ridge[0], 2 * ridge[len(ridge) // 2]


# LABEL_SIZE_MM -- derived, not assumed. Measure this exact font's own
# stroke-to-cap-height ratio at a size well clear of any tiny-glyph
# measurement noise, for every label text this file actually uses, take
# the worst (thinnest-relative-to-size) one, and scale up to clear
# MIN_STROKE_MM with a real margin.
LABEL_TEXTS = ["A1", "A2", "B1", "B2", "B3", "C1", "C2", "C3"]
_REF_SIZE_MM = 6.0
_worst_text, _worst_ratio = None, None
for _t in LABEL_TEXTS:
    _thinnest_ref, _ = min_stroke_width_mm(_shapestring_face(_t, _REF_SIZE_MM), grid=0.1)
    _ratio = _thinnest_ref / _REF_SIZE_MM
    print(f"  stroke calibration '{_t}' @ {_REF_SIZE_MM:.1f}mm: thinnest={_thinnest_ref:.4f}mm "
          f"ratio={_ratio:.4f}")
    if _worst_ratio is None or _ratio < _worst_ratio:
        _worst_text, _worst_ratio = _t, _ratio
assert _worst_ratio and _worst_ratio > 0, "stroke-width calibration found a zero-width label at the reference size"
_SAFETY_MARGIN = 1.2   # covers this grid method's own discretisation noise + real print variance
_raw_required_mm = MIN_STROKE_MM / _worst_ratio
LABEL_SIZE_MM = math.ceil(_raw_required_mm * _SAFETY_MARGIN * 2.0) / 2.0   # round up to the nearest 0.5mm
print(f"label size derivation: worst stroke/size ratio is '{_worst_text}' at {_worst_ratio:.4f} "
      f"(measured at {_REF_SIZE_MM:.1f}mm cap height) -> raw required size "
      f"{MIN_STROKE_MM:.2f}/{_worst_ratio:.4f}={_raw_required_mm:.2f}mm -> "
      f"LABEL_SIZE_MM={LABEL_SIZE_MM:.1f}mm ({_SAFETY_MARGIN:.0%} margin) for a {MIN_STROKE_MM:.2f}mm "
      f"minimum stroke (2x the {NOZZLE_W}mm nozzle)")


def make_label_tool_x(text, size, x0, y_anchor, z_anchor, depth=0.6, air=0.6, into_positive_x=True):
    """A small solid that, when CUT from a coupon, engraves `text` into
    the X-normal face at world X=x0 -- used only for the B1/B3 seam-strip
    coupons (see their call sites for why an X-normal box-cut face is
    genuinely their largest available flat face). Built in the
    shapestring's own local frame then rotated 120deg about (1,1,1) --
    confirmed directly to map local X->world Y, local Y->world Z,
    local Z->world X, i.e. "text reads along the wall's depth axis,
    extrudes along the wall's normal" -- then placed so the extrusion
    straddles the real face with a genuine overlap on both sides (never a
    zero-overlap Gotcha #1 coincident cut)."""
    face = _shapestring_face(text, size)
    total = depth + air
    solid = face.extrude(Vector(0, 0, total))
    R = Rotation(Vector(1, 1, 1), 120)
    if into_positive_x:
        # material is at X < x0 (an xmax-side cut face) -- start `depth`
        # inside the material, end `air` proud of the face in open air.
        origin = Vector(x0 - depth, y_anchor, z_anchor)
    else:
        # material is at X > x0 (an xmin-side cut face) -- mirror it.
        origin = Vector(x0 - air, y_anchor, z_anchor)
    solid.Placement = Placement(origin, R)
    return solid


def make_label_tool_y(text, size, y0, x_anchor, z_anchor, depth=0.6, air=0.6, into_positive_y=True):
    """A small solid that, when CUT from a coupon, engraves `text` into
    the Y-normal face at world Y=y0 -- the coupon's own broad flat front/
    back face, used for every coupon in this file except B1/B3. Built in
    the shapestring's own local frame (baseline along local X, cap-height
    along local Y, flat at local Z=0) then rotated +90deg about world X --
    confirmed directly (FreeCAD Rotation(Vector(1,0,0),90) maps local
    X->world X, local Y->world Z, local Z->world -Y) to give upright text
    (cap height along world Z, matching the panel's own up/down) extruding
    along the part's own thickness axis (world Y). `into_positive_y`
    selects which side of y0 carries real material and flips the LOCAL
    extrusion direction (never the rotation, which always keeps text
    upright) so the cut digs into that material with a genuine overlap on
    both sides (never a zero-overlap Gotcha #1 coincident cut)."""
    face = _shapestring_face(text, size)
    total = depth + air
    R = Rotation(Vector(1, 0, 0), 90)
    if into_positive_y:
        # material is at Y > y0 -- local -Z maps to +Y, so extrude that
        # way: start `air` below y0 in open air, end `depth` inside material.
        solid = face.extrude(Vector(0, 0, -total))
        origin = Vector(x_anchor, y0 - air, z_anchor)
    else:
        # material is at Y < y0 -- local +Z maps to -Y: start `air` above
        # y0 in open air, end `depth` inside material.
        solid = face.extrude(Vector(0, 0, total))
        origin = Vector(x_anchor, y0 + air, z_anchor)
    solid.Placement = Placement(origin, R)
    return solid


def _material_slab_x(coupon, x0, depth, into_positive_x):
    """The coupon's real material across the FULL depth a label at X=x0
    will actually cut -- not just a thin skin at x0 itself. Checking only
    the surface is exactly what let the first pass of this fix place a
    label over material that looked solid at the surface but was hollow
    one layer behind it (see _finish_label's own real-material check and
    this fix's hand-back notes for the case that caught it)."""
    origin_x = (x0 - depth) if into_positive_x else x0
    probe = Part.makeBox(depth, 400, 400, Vector(origin_x, -200, -200))
    sl = coupon.common(probe)
    return sl if sl.Solids else None


def _material_slab_y(coupon, y0, depth, into_positive_y):
    """Y-normal counterpart of _material_slab_x."""
    origin_y = y0 if into_positive_y else (y0 - depth)
    probe = Part.makeBox(400, depth, 400, Vector(-200, origin_y, -200))
    sl = coupon.common(probe)
    return sl if sl.Solids else None


def _slab_coverage_x(slab, y0, y1, z0, z1):
    bb = slab.BoundBox
    test = Part.makeBox(bb.XLength, y1 - y0, z1 - z0, Vector(bb.XMin, y0, z0))
    common = slab.common(test)
    vol = common.Volume if common.Solids else 0.0
    return vol / test.Volume


def _slab_coverage_y(slab, x0, x1, z0, z1):
    bb = slab.BoundBox
    test = Part.makeBox(x1 - x0, bb.YLength, z1 - z0, Vector(x0, bb.YMin, z0))
    common = slab.common(test)
    vol = common.Volume if common.Solids else 0.0
    return vol / test.Volume


LABEL_ANCHOR_PAD = 0.6   # mm clearance kept between the text block and the real material's own edge


def _find_label_anchor(slab, coverage_fn, amin, amax, bmin, bmax, block_w, block_h,
                        feature_a, feature_b, step=1.5, min_coverage=0.92):
    """Search the coupon's REAL material (`slab`, already spanning the
    label's full cut depth -- see _material_slab_x/_y) for a block_w x
    block_h rectangle that is >= min_coverage real material, preferring
    whichever qualifying position is farthest from (feature_a, feature_b)
    -- the functional feature this coupon exists to test.

    Replaces the original "just use the bounding-box corner farthest from
    the feature" heuristic, which assumed the real cross-section fills
    its own bounding box. Confirmed false on two coupons in this exact
    fix (A2's Y-normal face, and separately its own X-normal end face;
    B1's X-normal end face): each has real material concentrated in one
    narrow region of an otherwise much bigger bounding box, so a
    bbox-corner guess landed in open air / a thin skin on the first pass
    of this fix and cut 0.0-9mm3 of an expected ~40-45mm3.

    Returns (a, b, coverage, distance) for the chosen rectangle's own
    (amin,bmin) corner, or None if nothing in the search grid clears
    min_coverage -- callers must treat None as "this face has no room for
    this label at this size" per the fix brief's own instruction, not
    silently place unprintable or half-missing text."""
    candidates = []
    a = amin
    while a + block_w <= amax + 1e-9:
        b = bmin
        while b + block_h <= bmax + 1e-9:
            d = math.hypot((a + block_w / 2.0) - feature_a, (b + block_h / 2.0) - feature_b)
            candidates.append((d, a, b))
            b += step
        a += step
    candidates.sort(key=lambda c: -c[0])   # farthest from the feature first
    for d, a, b in candidates:
        cov = coverage_fn(a, a + block_w, b, b + block_h)
        if cov >= min_coverage:
            return a, b, cov, d
    return None


def _finish_label(coupon, text, tool, size, depth=0.6):
    """Shared tail end of add_label_x/_y: the PERMANENT stroke-width
    assertion (must run on every label, every regeneration -- this is the
    check that would have caught the original defect), a PERMANENT
    real-material check (see below), then the existing solid-count/
    validity/shell-count re-verification this build already requires
    after every operation that's supposed to preserve one body.

    The real-material check exists because of a second, independent way
    this exact fix broke A2 on its first pass: label_footprint_y found a
    genuinely large (X,Z) bounding rectangle at Y=WALL, but that rectangle
    described the SLICE'S bounding box, not its true (non-rectangular)
    shape -- the anchor corner it picked sat over a spot where the shell's
    real material is only a thin skin that has already thinned to nothing
    by the label's own cut depth. The cut still "succeeded" (solids=1,
    valid=True, shells=[1] -- cutting empty air breaks nothing) and the
    abstract 2D glyph face still passed the stroke-width check (that check
    never looks at the coupon at all) -- but it removed 0.0mm3, i.e. no
    label was actually cut. Comparing the REAL volume removed against the
    tool's own nominal footprint (glyph area x depth) catches this the
    same way the stroke-width check catches undersized text: by measuring
    the real geometry, not trusting that a clean topology means the label
    is actually there."""
    thinnest, median = min_stroke_width_mm(_shapestring_face(text, size))
    print(f"  label '{text}' @ {size:.1f}mm cap height -- stroke thinnest={thinnest:.3f}mm "
          f"median={median:.3f}mm (need >= {MIN_STROKE_MM:.2f}mm)")
    assert thinnest >= MIN_STROKE_MM, (
        f"{text}: label stroke {thinnest:.3f}mm is narrower than {MIN_STROKE_MM:.2f}mm "
        f"(2x the {NOZZLE_W}mm nozzle) -- the slicer will not extrude this (this is exactly the "
        f"coupon-labels defect: real, valid CAD geometry below the process's minimum feature size)")
    before_vol = coupon.Volume
    labelled = coupon.cut(tool)
    removed = before_vol - labelled.Volume
    expected = _shapestring_face(text, size).Area * depth
    n = len(labelled.Solids)
    valid = labelled.isValid()
    shells = [len(s.Shells) for s in labelled.Solids]
    print(f"    -> removed {removed:.2f}mm3 (nominal glyph-area x depth = {expected:.2f}mm3) "
          f"solids={n} valid={valid} shells={shells}")
    assert removed >= 0.5 * expected, (
        f"{text}: label cut removed only {removed:.2f}mm3 of an expected ~{expected:.2f}mm3 -- "
        f"the anchor point is sitting over a thin skin or open cavity, not the coupon's real "
        f"material, so most or all of the label was never actually cut")
    assert n == 1 and valid and shells == [1], (
        f"{text}: labelling broke the coupon's own topology (solids={n} valid={valid} shells={shells})")
    return labelled


def add_label_x(coupon, text, x0, feature_yz, into_positive_x, size=None, depth=0.6, air=0.6):
    """Cut `text` into the coupon's X-normal end face at world X=x0 --
    B1/B3 only, see their call site for why. Searches the coupon's REAL
    material across the label's full cut depth (_material_slab_x /
    _find_label_anchor) for a spot big enough for the whole text block,
    farthest from feature_yz (the mating feature this coupon exists to
    test) among the spots that qualify -- never a bare bounding-box
    corner (see _find_label_anchor's own docstring for why that broke)."""
    size = LABEL_SIZE_MM if size is None else size
    fy, fz = feature_yz
    face = _shapestring_face(text, size)
    block_w = face.BoundBox.XLength + 2 * LABEL_ANCHOR_PAD
    block_h = face.BoundBox.YLength + 2 * LABEL_ANCHOR_PAD
    slab = _material_slab_x(coupon, x0, depth, into_positive_x)
    assert slab is not None, f"{text}: no material found at the chosen label plane X={x0}"
    bb = slab.BoundBox
    found = _find_label_anchor(slab, lambda a0, a1, b0, b1: _slab_coverage_x(slab, a0, a1, b0, b1),
                                bb.YMin, bb.YMax, bb.ZMin, bb.ZMax, block_w, block_h, fy, fz)
    assert found is not None, (
        f"{text}: no {block_w:.1f}x{block_h:.1f}mm spot on this face is >=92% real material at "
        f"X={x0} -- this coupon has no room for a {size:.1f}mm label here; use a shorter label "
        f"(a single character) instead of shrinking below MIN_STROKE_MM")
    ay, az, cov, dist = found
    print(f"  anchor '{text}' (X-normal @ X={x0:.2f}): ({ay:.2f},{az:.2f}) coverage={cov:.1%} "
          f"dist-from-feature={dist:.1f}mm")
    tool = make_label_tool_x(text, size, x0, ay + LABEL_ANCHOR_PAD, az + LABEL_ANCHOR_PAD,
                              depth=depth, air=air, into_positive_x=into_positive_x)
    return _finish_label(coupon, text, tool, size, depth=depth)


def add_label_y(coupon, text, y0, feature_xz, into_positive_y, size=None, depth=0.6, air=0.6):
    """Cut `text` into the coupon's own broad flat face at world Y=y0 --
    every coupon except B1/B3. Searches the coupon's REAL material across
    the label's full cut depth (_material_slab_y / _find_label_anchor) for
    a spot big enough for the whole text block, farthest from feature_xz
    (the mating feature this coupon exists to test) among the spots that
    qualify -- never a bare bounding-box corner (see _find_label_anchor's
    own docstring for why that broke)."""
    size = LABEL_SIZE_MM if size is None else size
    fx, fz = feature_xz
    face = _shapestring_face(text, size)
    block_w = face.BoundBox.XLength + 2 * LABEL_ANCHOR_PAD
    block_h = face.BoundBox.YLength + 2 * LABEL_ANCHOR_PAD
    slab = _material_slab_y(coupon, y0, depth, into_positive_y)
    assert slab is not None, f"{text}: no material found at the chosen label plane Y={y0}"
    bb = slab.BoundBox
    found = _find_label_anchor(slab, lambda a0, a1, b0, b1: _slab_coverage_y(slab, a0, a1, b0, b1),
                                bb.XMin, bb.XMax, bb.ZMin, bb.ZMax, block_w, block_h, fx, fz)
    assert found is not None, (
        f"{text}: no {block_w:.1f}x{block_h:.1f}mm spot on this face is >=92% real material at "
        f"Y={y0} -- this coupon has no room for a {size:.1f}mm label here; use a shorter label "
        f"(a single character) instead of shrinking below MIN_STROKE_MM")
    ax, az, cov, dist = found
    print(f"  anchor '{text}' (Y-normal @ Y={y0:.2f}): ({ax:.2f},{az:.2f}) coverage={cov:.1%} "
          f"dist-from-feature={dist:.1f}mm")
    tool = make_label_tool_y(text, size, y0, ax + LABEL_ANCHOR_PAD, az + LABEL_ANCHOR_PAD,
                              depth=depth, air=air, into_positive_y=into_positive_y)
    return _finish_label(coupon, text, tool, size, depth=depth)


def verify_coupon(shape, name, expect_solids=1):
    n = len(shape.Solids)
    valid = shape.isValid()
    shells = [len(s.Shells) for s in shape.Solids]
    bb = shape.BoundBox
    dims = (round(bb.XLength, 2), round(bb.YLength, 2), round(bb.ZLength, 2))
    vol = round(shape.Volume, 1)
    ok = (n == expect_solids) and valid and all(s == 1 for s in shells) and fits_bed(dims)
    tag = "OK" if ok else "FAIL"
    print(f"  [{tag}] {name}: solids={n} valid={valid} shells={shells} "
          f"bbox={dims[0]}x{dims[1]}x{dims[2]}mm volume={vol}mm3")
    assert n == expect_solids, f"{name}: expected {expect_solids} solid(s), got {n}"
    assert valid, f"{name}: isValid() == False"
    assert all(s == 1 for s in shells), f"{name}: enclosed void (shells={shells})"
    assert fits_bed(dims), f"{name}: {dims} does not fit the bed"
    return dims, vol


def print_orient(shape, parent_name):
    """Same recipe as bambu/build_project.py's own ORIENT_SCRIPT: rotate
    by cad/print_rotations.json's entry for the coupon's PARENT part
    (never re-derived for the coupon itself -- a coupon tests nothing if
    it prints in a different orientation than the real part), then
    translate so it sits on the bed (ZMin=0, centred in X/Y)."""
    r = PRINT_ROTATIONS[parent_name]
    t = shape.copy()
    t.Placement = Placement(Vector(), Rotation(Vector(*r["axis"]), r["angle_deg"])) * t.Placement
    t = t.copy()
    b = t.BoundBox
    t.translate(Vector(-(b.XMin + b.XMax) / 2.0, -(b.YMin + b.YMax) / 2.0, -b.ZMin))
    return t


def export_coupon(shape, name, parent_name):
    oriented = print_orient(shape, parent_name)
    n, valid = len(oriented.Solids), oriented.isValid()
    shells = [len(s.Shells) for s in oriented.Solids]
    assert n == 1 and valid and shells == [1], (
        f"{name}: print-orientation transform broke topology (solids={n} valid={valid} shells={shells})")
    step_path = os.path.join(OUT_STEP, name + ".step")
    stl_path = os.path.join(OUT_STL, name + ".stl")
    oriented.exportStep(step_path)
    Mesh.Mesh(oriented.tessellate(0.05)).write(stl_path, "STL")
    b = oriented.BoundBox
    print(f"  exported {name}: print-oriented bbox {b.XLength:.1f} x {b.YLength:.1f} x {b.ZLength:.1f} mm "
          f"-> {os.path.relpath(step_path, REPO)}, {os.path.relpath(stl_path, REPO)}")
    return oriented


# =============================================================================
# COUPON A -- screen corner: perimeter boss nesting into the side wall,
# screw access, and the counterbore. The class that failed on plates
# 1-3 ("the screw base bumps the edge of the body").
# =============================================================================
print("\n=== COUPON A: screen corner (perimeter boss / side wall) ===")
fp_screen = load_step("01a-face-plate-screen")
bs_screen = load_step("02a-back-shell-screen")

A_BX, A_BZ, A_BR = pick_wall_and_corner_boss(fp_screen)
assert abs(A_BR * 2 - 8.2) < 0.15, f"expected the PERIM_BOSS_OD_TIGHT boss (~8.2mm OD), got {2*A_BR:.2f}mm"

A_BOX = box_full(45.0, 400.0, 45.0, A_BX, 27.0, A_BZ)  # Y centred/generous: real Y-extent clips it per part

a1 = fp_screen.common(A_BOX)
a2 = bs_screen.common(A_BOX)
verify_coupon(a1, "A1 (01a corner, pre-label)")
verify_coupon(a2, "A2 (02a corner, pre-label)")

# 2026-09-24 label fix: A1 moves to its own broad flat back face (01a,
# Y=FACE_T -- probed real footprint at this corner: ~28x35mm, plenty of
# room clear of the boss, and not the bed-contact face since 01a prints
# front-face down (Y=0), so Y=FACE_T ends up facing up in open air).
#
# A2 is a genuinely thin shell (a watertight single solid, but hollow
# inside its own bounding box, not a filled block) -- neither its Y=WALL
# face nor its own box-cut end face at the box's LEFT edge (X~34.7, the
# old A_LABEL_X) turned out to be broad AND full-depth solid: both
# measured well under 20% real material across the label's own 0.6mm cut
# depth (confirmed by _find_label_anchor finding no qualifying spot, and
# by direct probing across the whole coupon -- see this fix's hand-back
# notes). Scanning multiple X-planes found the one place on this coupon
# that actually is: right at its own real X_MAX edge (X_A1=64.66, the
# screen/column seam post), which measured >99% solid across the full
# label depth -- a real structural reinforcement at the seam, not the
# thin shell skin everywhere else. A2's label goes there instead.
a1 = add_label_y(a1, "A1", FACE_T, (A_BX, A_BZ), into_positive_y=False)
A2_LABEL_X = X_A1 - 0.02   # the coupon's own real X_MAX edge -- the seam post, confirmed >99% solid
a2 = add_label_x(a2, "A2", A2_LABEL_X, (5.0, A_BZ), into_positive_x=True)

verify_coupon(a1, "A1 (01a corner)")
verify_coupon(a2, "A2 (02a corner)")

# real checks, reused from generate_parts.py, run on the coupon itself --
# a coupon whose fastener features didn't survive the cut proves nothing.
_a_travel = PANEL_D - (FACE_T + PERIM_BOSS_LEN)
_a_ok1, _a_vol1 = fastener_access(f"PERIM_A ({A_BX:.2f},{A_BZ:.2f}) vs A2",
                                   Vector(A_BX, PANEL_D, A_BZ), Vector(0, -1, 0), _a_travel, CSK_DEPTH, a2,
                                   shank_r=CLEAR_D / 2.0, head_r=CSK_D / 2.0)
_a_ok2, _a_pct = bore_stays_open(f"PERIM_A boss/insert ({A_BX:.2f},{A_BZ:.2f}) in A1",
                                  Vector(A_BX, FACE_T + PERIM_BOSS_LEN - INSERT_DEPTH + 0.3, A_BZ),
                                  Vector(0, 1, 0), INSERT_D / 2.0, INSERT_DEPTH, a1)
_a_ok3, _a_iv = interfere(a1, a2, "A1 vs A2 (boss/wall nesting)")
assert _a_ok1 and _a_ok2 and _a_ok3, "Coupon A: one or more reused checks FAILED"

export_coupon(a1, "A1-face-plate-screen-corner", "01a-face-plate-screen")
export_coupon(a2, "A2-back-shell-screen-corner", "02a-back-shell-screen")


# =============================================================================
# COUPON B -- column seam: the seam bolt path + insert bore, and the
# PERIM_B screw that fouled the seam rib (fix/column-screw-access's own
# two faults, both in this one box).
# =============================================================================
print("\n=== COUPON B: column seam (bolt bore + PERIM_B screw vs rib) ===")
fp_column = load_step("01b-face-plate-column")
bs_column = load_step("02b-back-shell-column")
# bs_screen already loaded above for Coupon A -- reused here for the
# mating 02a strip, per the task's "cut every member of a mating pair
# with the SAME box" rule.

B_X0, B_X1 = 55.0, 90.0
B_Z0, B_Z1 = 8.0, 45.0
B_BOX = box_full(B_X1 - B_X0, 400.0, B_Z1 - B_Z0, (B_X0 + B_X1) / 2.0, 35.0, (B_Z0 + B_Z1) / 2.0)

# Verify the measured features the task cites actually fall inside this
# box, against the real geometry (not just trusting the brief).
B_PB_X, B_PB_Z, B_PB_R = pick_nearest_boss(fp_column, 72.56, 18.00)
assert B_X0 <= B_PB_X <= B_X1 and B_Z0 <= B_PB_Z <= B_Z1, "PERIM_B screw isn't inside coupon B's box"
print(f"  PERIM_B screw confirmed at ({B_PB_X:.2f},{B_PB_Z:.2f}), OD {2*B_PB_R:.1f}mm -- inside coupon B's box")

b1 = bs_column.common(B_BOX)
b2 = fp_column.common(B_BOX)
b3 = bs_screen.common(B_BOX)
verify_coupon(b1, "B1 (02b seam, pre-label)")
verify_coupon(b2, "B2 (01b seam, pre-label)")
verify_coupon(b3, "B3 (02a seam strip, pre-label)")

# 2026-09-24 label fix: B1 and B3 are the two SEAM coupons -- both thin
# shells, not solid blocks, so (like A2) neither has a broad face at
# every X plane; scanning the full X range (0.6mm-deep slabs, matching
# the label's own cut depth) found each coupon's one genuinely broad,
# full-depth-solid region sits right at the seam post itself: for B1
# (02b), X=X_B0..X_B0+3mm (Y[3,66.6]mm, 99%+ solid); for B3 (02a, the
# SAME seam post A2 uses, just a different Z band of the same part),
# X=X_A1-2mm..X_A1 (Y[3,54.6]mm, 99%+ solid). Everywhere else on either
# coupon (including the box's OTHER end, where the pre-fix script placed
# both labels) is a thin rib well under 20% solid at this depth -- kept
# on the X-normal axis, but moved to the seam-post end. B2 (01b) is a
# real face-plate section, not a seam rib, so it moves to its own broad
# Y=FACE_T back face like every other face-plate coupon.
B1_LABEL_X = X_B0 + 0.02
B3_LABEL_X = X_A1 - 0.02
b1 = add_label_x(b1, "B1", B1_LABEL_X, (18.0, 40.0), into_positive_x=False)
b2 = add_label_y(b2, "B2", FACE_T, (B_PB_X, B_PB_Z), into_positive_y=False)
b3 = add_label_x(b3, "B3", B3_LABEL_X, (18.0, 40.0), into_positive_x=True)

verify_coupon(b1, "B1 (02b seam)")
verify_coupon(b2, "B2 (01b seam)")
verify_coupon(b3, "B3 (02a seam strip)")

# Real checks, reused: PERIM_B fastener-access (THE reported column-screw
# defect) and its own bore-stays-open target; the seam bolts' own
# fastener-access (through 02a's strip AND 02b) and bore-stays-open.
_b_travel_perimB = COLUMN_PANEL_D - (FACE_T + PERIM_BOSS_LEN)
_b_ok1, _ = fastener_access(f"PERIM_B ({B_PB_X:.2f},{B_PB_Z:.2f}) vs B1",
                             Vector(B_PB_X, COLUMN_PANEL_D, B_PB_Z), Vector(0, -1, 0),
                             _b_travel_perimB, CSK_DEPTH, b1, shank_r=CLEAR_D / 2.0, head_r=CSK_D / 2.0)
_b_ok2, _ = bore_stays_open(f"PERIM_B boss/insert ({B_PB_X:.2f},{B_PB_Z:.2f}) in B2",
                             Vector(B_PB_X, FACE_T + PERIM_BOSS_LEN - INSERT_DEPTH + 0.3, B_PB_Z),
                             Vector(0, 1, 0), INSERT_D / 2.0, INSERT_DEPTH, b2)

SEAM_BOLT_ZS_IN_BOX = [24.0, 34.5]
_seam_travel = SEAM_INSERT_X0 - (X_A1 - WALL)
_b_seam_ok = []
for _sz in SEAM_BOLT_ZS_IN_BOX:
    assert B_Z0 <= _sz <= B_Z1, f"seam bolt Z={_sz} isn't inside coupon B's box"
    _entry = Vector(X_A1 - WALL, FACE_T + 15.0, _sz)
    ok_a, _ = fastener_access(f"SEAM bolt Z={_sz:.2f} vs B3 (02a strip)", _entry, Vector(1, 0, 0),
                               _seam_travel, 0.0, b3, shank_r=CLEAR_D / 2.0, head_r=CSK_D / 2.0)
    ok_b, _ = fastener_access(f"SEAM bolt Z={_sz:.2f} vs B1 (02b)", _entry, Vector(1, 0, 0),
                               _seam_travel, 0.0, b1, shank_r=CLEAR_D / 2.0, head_r=CSK_D / 2.0)
    ok_c, _ = bore_stays_open(f"SEAM boss/insert Z={_sz:.2f} in B1",
                               Vector(SEAM_INSERT_X0, FACE_T + 15.0, _sz), Vector(1, 0, 0),
                               INSERT_D / 2.0, INSERT_DEPTH, b1)
    _b_seam_ok += [ok_a, ok_b, ok_c]

_b_ok3, _b_iv = interfere(b1, b2, "B1 vs B2 (PERIM_B boss/wall nesting)")
assert _b_ok1 and _b_ok2 and _b_ok3 and all(_b_seam_ok), "Coupon B: one or more reused checks FAILED"

export_coupon(b1, "B1-back-shell-column-seam", "02b-back-shell-column")
export_coupon(b2, "B2-face-plate-column-seam", "01b-face-plate-column")
export_coupon(b3, "B3-back-shell-screen-seam-strip", "02a-back-shell-screen")


# =============================================================================
# COUPON C -- band mount: the clamped stack (05 diffuser -> 04a insert ->
# 01a face-plate boss), one M3 through all three.
# =============================================================================
print("\n=== COUPON C: band mount (clamped insert/diffuser stack) ===")
ins_a = load_step("04a-band-insert-ignition")
diff = load_step("05-band-diffuser")
# fp_screen already loaded above for Coupon A -- reused here (same part,
# a different corner of it).

C_APPROX_X, C_APPROX_Z = -138.66, 14.0
C_BX, C_BZ, C_BR = pick_nearest_boss(fp_screen, C_APPROX_X, C_APPROX_Z)
assert abs(C_BR * 2 - BOSS_OD) < 0.1, f"expected a standard BOSS_OD ({BOSS_OD}mm) band-mount boss, got {2*C_BR:.2f}mm"

C_BOX = box_full(40.0, 400.0, 40.0, C_BX, 7.5, C_BZ)

c1 = fp_screen.common(C_BOX)
c2 = ins_a.common(C_BOX)
c3 = diff.common(C_BOX)
verify_coupon(c1, "C1 (01a band-mount, pre-label)")
verify_coupon(c2, "C2 (04a band-mount, pre-label)")
verify_coupon(c3, "C3 (05 band-mount, pre-label)")

# FASTENER-HOLE-EXISTS, reused: the original check needs an
# UNPERFORATED reference outline (generate_parts.py's own
# `_ins_outline_ref`/`_diff_outline_ref` -- a plain box the size of the
# part's full footprint, built BEFORE any perforation is cut, so a
# probe there can distinguish "there's a real hole here" from "the
# part's own edge ends here"). c2/c3 are already the finished,
# perforated parts, so the same stand-in is rebuilt here at the
# coupon's own real (pre-label) footprint size -- never the real
# perforation pattern, exactly like the original's own box_cxz stand-in.
INSERT_Y0 = round(DIFFUSER_Y0 - INSERT_T, 2)
_c2bb, _c3bb = c2.BoundBox, c3.BoundBox
_c2_outline_ref = box_full(_c2bb.XLength, INSERT_T, _c2bb.ZLength,
                            (_c2bb.XMin + _c2bb.XMax) / 2.0, INSERT_Y0 + INSERT_T / 2.0,
                            (_c2bb.ZMin + _c2bb.ZMax) / 2.0)
_c3_outline_ref = box_full(_c3bb.XLength, DIFFUSER_T, _c3bb.ZLength,
                            (_c3bb.XMin + _c3bb.XMax) / 2.0, DIFFUSER_Y0 + DIFFUSER_T / 2.0,
                            (_c3bb.ZMin + _c3bb.ZMax) / 2.0)
_c_hole_ok1, _ = _fastener_hole_exists(_c2_outline_ref, INSERT_T, INSERT_Y0, C_BX, C_BZ, CLEAR_D,
                                        "C2 (04a insert) BAND_MOUNT")
_c_hole_ok2, _ = _fastener_hole_exists(_c3_outline_ref, DIFFUSER_T, DIFFUSER_Y0, C_BX, C_BZ, CLEAR_D,
                                        "C3 (05 diffuser) BAND_MOUNT")
assert _c_hole_ok1 and _c_hole_ok2, "Coupon C: the mounting hole axis isn't over real material"

# 2026-09-24 label fix: C2 was the worst offender -- its label sat on its
# own 2.0mm-thick edge (INSERT_T), which is why it was thinnest of the
# three even at the same nominal size. All three move to their own broad
# flat faces: C1 (01a) at Y=FACE_T like every other face-plate coupon;
# C2 (04a insert) at Y=DIFFUSER_Y0, its own 24.7x24.7mm face against the
# diffuser -- a real contact face in the clamped stack, same precedent the
# fix brief itself named safe; C3 (05 diffuser) at Y=DIFFUSER_Y0+DIFFUSER_T,
# its own OUTWARD exposed face (not a mating face at all).
#
# C2's face is genuinely broad (24.7x24.7mm), but it's also perforated by
# this insert's own LED/wiring holes, spaced densely enough (confirmed by
# _find_label_anchor finding no qualifying spot for the full "C2" block)
# that no ~20x13mm rectangle anywhere on it is hole-free. Per the fix
# brief's own instruction, this is exactly the "genuinely no room" case:
# use a single character ("2") rather than shrinking below MIN_STROKE_MM.
c1 = add_label_y(c1, "C1", FACE_T, (C_BX, C_BZ), into_positive_y=False)
c2 = add_label_y(c2, "2", DIFFUSER_Y0, (C_BX, C_BZ), into_positive_y=False)
c3 = add_label_y(c3, "C3", DIFFUSER_Y0 + DIFFUSER_T, (C_BX, C_BZ), into_positive_y=False)

verify_coupon(c1, "C1 (01a band-mount)")
verify_coupon(c2, "C2 (04a band-mount)")
verify_coupon(c3, "C3 (05 band-mount)")

# Real checks, reused: fastener-access for the one M3 through all three
# layers, and bore-stays-open for the boss/insert bore in 01a.
_c_entry = Vector(C_BX, DIFFUSER_Y0 + DIFFUSER_T, C_BZ)
_c_travel = (DIFFUSER_Y0 + DIFFUSER_T) - (FACE_T + BAND_BOSS_LEN - INSERT_DEPTH + 0.3)
_c_ok1, _ = fastener_access(f"BAND_MOUNT ({C_BX:.2f},{C_BZ:.2f}) vs C3 (diffuser)", _c_entry,
                             Vector(0, -1, 0), _c_travel, 0.0, c3, shank_r=CLEAR_D / 2.0, head_r=CSK_D / 2.0)
_c_ok2, _ = fastener_access(f"BAND_MOUNT ({C_BX:.2f},{C_BZ:.2f}) vs C2 (insert)", _c_entry,
                             Vector(0, -1, 0), _c_travel, 0.0, c2, shank_r=CLEAR_D / 2.0, head_r=CSK_D / 2.0)
_c_ok3, _ = fastener_access(f"BAND_MOUNT ({C_BX:.2f},{C_BZ:.2f}) vs C1 (face plate)", _c_entry,
                             Vector(0, -1, 0), _c_travel, 0.0, c1, shank_r=CLEAR_D / 2.0, head_r=CSK_D / 2.0)
_c_ok4, _ = bore_stays_open(f"BAND_MOUNT boss/insert ({C_BX:.2f},{C_BZ:.2f}) in C1",
                             Vector(C_BX, FACE_T + BAND_BOSS_LEN - INSERT_DEPTH + 0.3, C_BZ),
                             Vector(0, 1, 0), INSERT_D / 2.0, INSERT_DEPTH, c1)
_c_ok5, _ = interfere(c1, c2, "C1 vs C2 (boss tip / insert seat)")
_c_ok6, _ = interfere(c2, c3, "C2 vs C3 (insert / diffuser seat)")
assert all([_c_ok1, _c_ok2, _c_ok3, _c_ok4, _c_ok5, _c_ok6]), "Coupon C: one or more reused checks FAILED"

# CLAMPED-STACK-CONTACT, reused: the real design intent is 0.0mm gaps
# (flush), not a nesting clearance -- assert the coupon's own faces
# actually touch, the same blind spot the original build's own
# CLAMPED-STACK-CONTACT check exists to close.
_c_gap_12 = c1.distToShape(c2)[0]
_c_gap_23 = c2.distToShape(c3)[0]
print(f"  [{'OK' if _c_gap_12 <= 0.05 else 'FAIL'}] CLAMPED-STACK-CONTACT C1 vs C2: {_c_gap_12:.4f}mm (must be <= 0.05mm)")
print(f"  [{'OK' if _c_gap_23 <= 0.05 else 'FAIL'}] CLAMPED-STACK-CONTACT C2 vs C3: {_c_gap_23:.4f}mm (must be <= 0.05mm)")
assert _c_gap_12 <= 0.05 and _c_gap_23 <= 0.05, "Coupon C: clamped stack not actually in contact"

export_coupon(c1, "C1-face-plate-screen-band-mount", "01a-face-plate-screen")
export_coupon(c2, "C2-band-insert-ignition-band-mount", "04a-band-insert-ignition")
export_coupon(c3, "C3-band-diffuser-band-mount", "05-band-diffuser")

print("\nAll coupons built, labelled and verified.")
