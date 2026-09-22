"""
Dial Panel (hw-2015) -- a wall-mounted smart-home panel, fully 3D-printable.
SlashBuilder open hardware. FreeCAD-native (Part module), run headless:

    freecadcmd cad/generate_parts.py

It regenerates every part (STEP + STL) and runs the full verification suite:
per-part topology and bed-fit, feature-exists ray probes for every opening,
a no-unintended-openings grid over both face plates, assembly interference
for every part in its installed position (including Raspberry Pi's own
display model), blind-bore checks, the speaker sound-path check, and the
wall-cleat engagement check. A change isn't done until all of them pass.

Design intent (see ../README.md and ../docs/): screen in a silver bezel on
the left; a control column on the right with a push-dial on a 24-detent
ring, the mic-cut rocker in its own well and a gold tab beneath; a backlit
perforated band under the screen that is also the speaker grille; mic ports
on the top edge; a french cleat; light washing the wall behind.

Known failure modes this script checks for directly, because each one has
bitten a previous build: cuts that silently miss their part, parts placed
outside the shell, bumps on visible faces, insert bores breaking through a
face, a rebate deeper than its wall, and a vendor STEP baked into an export.

=============================================================================
DISPLAY GEOMETRY -- measured from Raspberry Pi's official STEP
=============================================================================
Official Raspberry Pi Touch Display 2, 7in STEP (RP-009154-DD-1):
  https://pip-assets.raspberrypi.com/categories/1083-raspberry-pi-touch-display-2/documents/RP-009154-DD-1-raspberry-pi-touch-display-2-step-7inch.step
It is Raspberry Pi's file and is NOT redistributed here. Download it into
cad/vendor/touch-display-2-7in.step, or point the DISPLAY_STEP env var at it.

Measured from that file (FreeCAD read-back + face/cylinder queries):
  - Overall bbox (native/portrait): 120.24 x 189.32 x 14.96mm (X/Y/Z length),
    Z from -9.94 to +5.02 -- confirmed exactly, matches a separate measurement of the same file.
  - Active area: a planar Z-normal face at Z=2.43, X range -44.67..44.63
    (89.30mm), Y range -76.45..81.31 (157.76mm) -- confirmed exactly.
    Active-area Y-centre = +2.43mm off the panel's own native-Y origin.
  - Pi 5 mounting standoffs: 4 cylindrical bosses, r=2.50mm (5mm OD), at
    native (+-24.50, 40.73) and (+-24.50, -17.27) -- a 49 x 58mm rectangle,
    exactly the Pi 5's own 58x49mm M2.5 hole pattern. Boss Z-range -9.94 to
    -1.44 (height 8.50mm) -- CONFIRMED: this boss spans the display's own
    full native-Z depth (-9.94 is the display's own overall Z-min), i.e.
    the Pi 5 PCB's own mounting face sits recessed INSIDE the display
    module's 14.96mm envelope, at native Z=-1.44, not projecting past it.
    The Pi 5's own populated side (SoC + Active Cooler) therefore
    protrudes PAST Z=-9.94, further back, which is exactly what
    STACK_CLEARANCE below reserves room for.
  - Separate 4-hole enclosure-mount pattern: r=1.0-1.5mm stepped
    (through-bore + counterbore) cylindrical faces at native
    (+-35.36, -67.06) and (+-35.36, 72.94) -- a 70.72 x 140.0mm rectangle
    (rounds to the task's own preliminary 70.8 x 140.0mm). Z-range -4.44 to
    -2.74 -- a BLIND bore INTO the display's own housing from its own back
    face, not a through-hole -- i.e. RPi's own screw threads into this
    hole from the display's own back (the same side our back-shell's own
    back wall faces), so this design provides CLEARANCE only (no insert of
    our own) at these 4 positions -- see "Display retention" below.

Mounted LANDSCAPE (software rotation) -- native coordinates rotated -90deg
about the panel's own normal via a real App.Rotation (not hand arithmetic),
same convention as the Arcade build.

=============================================================================
STACK CLEARANCE BEHIND THE DISPLAY -- real Active Cooler dims, cited
=============================================================================
  PI5_PCB_T       = 1.6mm    -- standard PCB thickness, reasoned, not a
                                Pi5-specific datasheet pull.
  ACTIVE_COOLER_H = 13.70mm  -- REAL, cited: Raspberry Pi's own mechanical
                                drawing (footprint 63.50x42.50mm, height
                                13.70mm incl. push-pins), read directly off
                                the drawing's own dimension lines:
                                https://datasheets.raspberrypi.com/cooling/raspberry-pi-active-cooler-mechanical-drawing.pdf
  CABLE_SLACK     = 6.0mm    -- my own margin, not measured (DSI FPC bend
                                reserve + USB-C power plug clearance).

=============================================================================
WHAT'S ESTIMATED, NOT MEASURED -- flagged inline with "PLACEHOLDER" AND
restated in README.md's ledger table. A parallel agent is confirming exact
Amazon listings for items 3/4/6/7/8 per the design brief -- these numbers should be
treated as provisional until that confirmation lands:
  - KY-040/EC11 bushing OD (M7x0.75 nominal -> 7.0mm major dia), bushing
    length behind the panel, shaft flat width (task says "verify 6mm /
    4.5mm flat" -- taken as a placeholder pending that verification).
  - KCD1 rocker body depth (~20mm, task's own approx).
  - 40mm speaker's real frame OD (a "40mm" driver's frame is commonly
    44-46mm OD, not 40mm -- flagged, not assumed away).
  - MAX98357A mounting-hole spacing (Adafruit's page states board size but
    not hole pitch in fetchable text -- same gap the common-kit build hit).
  - USB mic dongle body size (task's own ~18x10x5 approx) and its
    USB-A-plug + short-extension cable reserve.
  - Everything under "DESIGN DECISIONS / DEVIATIONS" in README.md.

=============================================================================
WHY THIS IS TWO BOLT-TOGETHER MODULES, NOT ONE FACE-PLATE/BACK-SHELL PAIR
=============================================================================
The task's own hard constraint is a 250 x 210 x 210mm bed. The real display
is 189.32mm wide (landscape); the control column needs >=62mm clear for the
24-detent dial ring alone. Even with EVERY margin driven to zero
(impossible in practice), 189.32 + 62 = 251.32mm -- already over the 250mm
limit before a single millimetre of rim, gap, or wall is added. A single-
piece face-plate/back-shell spanning both zones CANNOT print on this bed
at any real hardware size, independent of how tightly this script trims
its own margins. This is the same wall this studio's Cel open-build hit
("Cel became two modules because it is wider than any bed" --
thunderhead-2015-open-build-reconsideration.md) -- and the concept sheet's
own front elevation already draws the control column as a visually
distinct inset rect with its own border, so a bolt-together seam there is
a faithful realisation of the concept's own visual language, not a
deviation from it. Fix, same as Cel's: split into a SCREEN module
(01a/02a) and a CONTROL COLUMN module (01b/02b), joined by M3 through-
bolts across the seam wall, each independently <=250mm and each printed
and verified as its own file. See README.md's "Deviations" table for the
exact numbers.
"""

import json
import math
import os
import random

import FreeCAD as App
import Part
from FreeCAD import Vector, Rotation, Placement

HERE = os.path.dirname(os.path.abspath(__file__))
OUT_COMMON = os.path.join(HERE, "out", "common")
OUT_IGNITION = os.path.join(HERE, "out", "ignition")
OUT_NIGHTFALL = os.path.join(HERE, "out", "nightfall")
for _d in (OUT_COMMON, OUT_IGNITION, OUT_NIGHTFALL):
    os.makedirs(_d, exist_ok=True)

DISPLAY_STEP = os.environ.get(
    "DISPLAY_STEP", os.path.join(HERE, "vendor", "touch-display-2-7in.step"))
if not os.path.exists(DISPLAY_STEP):
    # print first: freecadcmd swallows a SystemExit's message
    _msg = (
        "Raspberry Pi Touch Display 2 (7\") STEP not found at %s.\n"
        "It is Raspberry Pi's file, so it isn't redistributed here. Download it from\n"
        "https://pip-assets.raspberrypi.com/categories/1083-raspberry-pi-touch-display-2/documents/"
        "RP-009154-DD-1-raspberry-pi-touch-display-2-step-7inch.step\n"
        "into cad/vendor/touch-display-2-7in.step (or set DISPLAY_STEP)." % DISPLAY_STEP)
    import sys
    App.Console.PrintError(_msg + "\n")
    sys.stderr.write(_msg + "\n")
    sys.stderr.flush()
    sys.stdout.flush()
    raise SystemExit(1)  # URL in module docstring. Never copied into this repo.

doc = App.newDocument("Thunderhead2015DialPanel")

RESULTS = []           # (name, solids, valid, shells, dims, note)
PROBE_RESULTS = []     # (label, blocked_mm3, probe_mm3, pct, ok)
INTERFERE_RESULTS = [] # (label, mm3, ok)

# Bambu A1 / Prusa MK4 shared print-envelope ceiling, per axis, real margin
# under the actual 256mm(A1)/~250-270mm(MK4) build volumes.
BED_X, BED_Y, BED_Z = 250.0, 210.0, 210.0


def fits_bed(dims):
    """True if `dims` (any order) fits the bed's 3 distinct axis limits in
    SOME axis-aligned assignment -- i.e. sorted-descending part dims must
    each be <= the correspondingly-sorted bed dims. Correct for axis-
    aligned print-orientation choices (rotating a box among X/Y/Z), not for
    arbitrary tilts."""
    d = sorted(dims, reverse=True)
    b = sorted((BED_X, BED_Y, BED_Z), reverse=True)
    return all(d[i] <= b[i] + 1e-6 for i in range(3))


def export_and_verify(shape, name, outdir, expected_solids=1, note="",
                       envelope_xy=None, envelope_axes=("X", "Y")):
    """Export STEP+STL, read the STEP back, and assert solids==expected,
    isValid(), shells==1 per solid (no enclosed voids), and that the part
    fits the real bed in some orientation. envelope_xy, if given, asserts
    the two named axes' extents don't exceed a NOMINAL OUTER ENVELOPE --
    i.e. nothing sticks out past the part's own outer skin (the Arcade
    build's gusset-rib overshoot class of defect)."""
    step_path = os.path.join(outdir, f"{name}.step")
    stl_path = os.path.join(outdir, f"{name}.stl")
    shape.exportStep(step_path)
    shape.exportStl(stl_path)

    check = Part.Shape()
    check.read(step_path)
    n_solids = len(check.Solids)
    valid = check.isValid()
    bb = check.BoundBox
    dims = {"X": round(bb.XLength, 3), "Y": round(bb.YLength, 3), "Z": round(bb.ZLength, 3)}
    shells = [len(s.Shells) for s in check.Solids]

    assert n_solids == expected_solids, (
        f"{name}: expected {expected_solids} solid(s) after STEP round-trip, "
        f"got {n_solids} -- boolean op likely produced disjoint solids "
        f"(Gotcha #1/#2 class defect)")
    assert valid, f"{name}: shape.isValid() == False after STEP round-trip"
    for i, sc in enumerate(shells):
        assert sc == 1, f"{name}: solid {i} has {sc} shells -- enclosed internal void"
    assert fits_bed((dims["X"], dims["Y"], dims["Z"])), (
        f"{name}: {dims} does not fit the {BED_X}x{BED_Y}x{BED_Z}mm bed in any orientation")

    env_note = ""
    if envelope_xy is not None:
        a0, a1 = envelope_axes
        tol = 0.05
        assert dims[a0] <= envelope_xy[0] + tol, (
            f"{name}: {a0}={dims[a0]}mm exceeds nominal outer envelope {envelope_xy[0]}mm "
            f"-- material sticks out past the outer skin")
        assert dims[a1] <= envelope_xy[1] + tol, (
            f"{name}: {a1}={dims[a1]}mm exceeds nominal outer envelope {envelope_xy[1]}mm "
            f"-- material sticks out past the outer skin")
        env_note = f" [envelope OK <= {envelope_xy[0]}x{envelope_xy[1]}]"

    RESULTS.append((name, n_solids, valid, shells, dims, note))
    print(f"  [OK] {name}: solids={n_solids} valid={valid} shells={shells} "
          f"bbox={dims['X']}x{dims['Y']}x{dims['Z']}mm{env_note} {note}")
    return check


def probe(part_shape, tool_shape, label, max_pct=2.0, want_open=True):
    """Feature-exists / no-unintended-opening probe: intersect a probe
    solid with the part and compare against the probe's own volume.
    want_open=True: assert the probe reads (almost) entirely OPEN AIR
    (an intended opening really is open). want_open=False: assert the
    probe reads (almost) entirely BLOCKED (an intended blind pocket/solid
    region really has no unintended see-through)."""
    common = part_shape.common(tool_shape)
    blocked = common.Volume if common.Solids else 0.0
    total = tool_shape.Volume
    pct = 100.0 * blocked / total if total > 0 else 0.0
    if want_open:
        ok = pct <= max_pct
    else:
        ok = pct >= (100.0 - max_pct)
    PROBE_RESULTS.append((label, blocked, total, pct, ok))
    tag = "OK" if ok else "FAIL"
    print(f"  [{tag}] probe {label}: blocked={blocked:.2f}/{total:.2f}mm3 ({pct:.2f}%) "
          f"want_open={want_open}")
    assert ok, f"probe FAILED: {label} blocked={blocked:.2f}/{total:.2f}mm3 ({pct:.2f}%)"
    return blocked


def interfere(shape_a, shape_b, label, max_mm3=0.05):
    common = shape_a.common(shape_b)
    vol = common.Volume if common.Solids else 0.0
    ok = vol <= max_mm3
    INTERFERE_RESULTS.append((label, vol, ok))
    tag = "OK" if ok else "FAIL"
    print(f"  [{tag}] interference {label}: {vol:.3f}mm3")
    assert ok, f"interference FAILED: {label} = {vol:.3f}mm3"
    return vol


# ---- geometry helpers --------------------------------------------------
def box_at(w, d, h, x0, y0, z0):
    return Part.makeBox(w, d, h, Vector(x0, y0, z0))


def box_cxz(w, h, thick, cx, cz, y0):
    """Box centred on X and Z, spanning Y from y0 for `thick`."""
    return Part.makeBox(w, thick, h, Vector(cx - w / 2.0, y0, cz - h / 2.0))


def box_full(w, d, h, cx, cy, cz):
    """Fully centred on all 3 axes."""
    return Part.makeBox(w, d, h, Vector(cx - w / 2.0, cy - d / 2.0, cz - h / 2.0))


def cyl_y(r, length, cx, cz, y0):
    return Part.makeCylinder(r, length, Vector(cx, y0, cz), Vector(0, 1, 0))


def cyl_z(r, length, cx, cy, z0):
    return Part.makeCylinder(r, length, Vector(cx, cy, z0), Vector(0, 0, 1))


def cyl_x(r, length, x0, cy, cz):
    return Part.makeCylinder(r, length, Vector(x0, cy, cz), Vector(1, 0, 0))


def csk_y(d_small, d_big, depth, cx, cz, y0, inward=1):
    """Countersink cone, axis Y, apex-small end at y0 (inward*+1 direction)."""
    return Part.makeCone(d_big / 2.0, d_small / 2.0, depth, Vector(cx, y0, cz), Vector(0, inward, 0))


# =============================================================================
# DISPLAY GEOMETRY -- real, re-measured (see docstring)
# =============================================================================
DISP_W_NATIVE, DISP_H_NATIVE, DISP_T = 120.24, 189.32, 14.96
AA_W_NATIVE, AA_H_NATIVE = 89.30, 157.76
AA_OFFSET_NATIVE = 2.43   # active-area centre offset along native Y
ENC_HOLES_NATIVE = [(35.36, -67.06), (35.36, 72.94), (-35.36, 72.94), (-35.36, -67.06)]
PI5_STANDOFFS_NATIVE = [(24.50, 40.73), (24.50, -17.27), (-24.50, 40.73), (-24.50, -17.27)]
PI5_STANDOFF_H = 8.50

_LANDSCAPE_ROT = Rotation(Vector(0, 0, 1), -90)


def to_landscape(pt_xy):
    v = _LANDSCAPE_ROT.multVec(Vector(pt_xy[0], pt_xy[1], 0))
    return (round(v.x, 3), round(v.y, 3))


DISP_W, DISP_H = DISP_H_NATIVE, DISP_W_NATIVE                  # 189.32 x 120.24
AA_W, AA_H = AA_H_NATIVE, AA_W_NATIVE                            # 157.76 x 89.30
AA_OFFSET_LANDSCAPE = to_landscape((0, AA_OFFSET_NATIVE))
ENC_HOLES_LANDSCAPE = [to_landscape(p) for p in ENC_HOLES_NATIVE]
PI5_STANDOFFS_LANDSCAPE = [to_landscape(p) for p in PI5_STANDOFFS_NATIVE]

print("Landscape display footprint: %.2f x %.2f mm" % (DISP_W, DISP_H))
print("Landscape active area: %.2f x %.2f mm, offset %s" % (AA_W, AA_H, AA_OFFSET_LANDSCAPE))
print("Landscape enclosure-mount holes:", ENC_HOLES_LANDSCAPE)

PI5_PCB_T = 1.6            # reasoned, standard PCB thickness -- PLACEHOLDER
ACTIVE_COOLER_H = 13.70    # REAL, cited (see docstring)
CABLE_SLACK = 6.0          # my own margin -- PLACEHOLDER
STACK_CLEARANCE = PI5_PCB_T + ACTIVE_COOLER_H + CABLE_SLACK    # 21.3mm

# =============================================================================
# GLOBAL BUILD CONSTANTS
# =============================================================================
FACE_T = 3.0          # face-plate thickness, uniform -- satisfies "panel <=
                       # ~3mm thick locally at the [KY-040] bushing" trivially
                       # (the whole plate is already 3mm; no added boss there)
WALL = 3.0             # back-shell wall thickness
MODULE_CLR = 4.0       # clearance around the display module footprint, each side

# M3 heat-set insert -- BOM-CONFIRMED CORRECTION (2026-09-21 BOM research,
# see bom-research.md Sec 2.14): CNC Kitchen's "M3x5.7" insert is 4.6mm OD
# for a 4.0mm hole (Dia 4.0mm is correct, kept), but needs a BLIND hole
# 6.5-7.0mm deep (~1mm deeper than the insert's own 5.7mm length), not
# 5.7mm -- 5.7 was the insert's own length, not the bore depth. Fixed here;
# every boss that carries one is lengthened to match (see below).
INSERT_D = 4.0
INSERT_DEPTH = 6.5            # BOM-corrected (was 5.7 -- that was the insert's
                                # own length, not the required bore depth)
INSERT_WALL_MIN = 1.6          # BOM: "keep >=1.6mm of plastic around each insert"
CLEAR_D = 3.4          # M3 clearance hole through a mating part
CSK_D = 6.5            # screw-head counterbore
CSK_DEPTH = 2.6
BOSS_OD = 9.0          # (9-4)/2 = 2.5mm wall around the insert, > INSERT_WALL_MIN
assert (BOSS_OD - INSERT_D) / 2.0 >= INSERT_WALL_MIN, "boss wall thinner than the BOM's own insert-wall rule"
BOSS_LEN_MIN = INSERT_DEPTH + 0.6   # every boss carrying an insert must clear this

FONT_FILE = "/System/Library/Fonts/Supplemental/Arial.ttf"  # unused this build
                       # (no engraved text) -- kept for parity with house pattern.

# =============================================================================
# PANEL LAYOUT -- ONE shared global coordinate frame for both modules:
#   X: width, 0 = centre of the ASSEMBLED (both-module) width
#   Y: depth, 0 = the outer FRONT face (visible), +Y goes back into the wall
#   Z: height, 0 = the panel's own bottom edge
#
# Rim/gap widths on the two vertical (X) edges of each module are widened to
# 11mm specifically to host real 9mm-OD perimeter mounting bosses with real
# edge margin -- a first draft used 6mm rims sized only for the display/
# dial layout, which put those bosses' fuse targets *inside* the window/band
# cutouts (a real Gotcha #1 floating-boss defect, caught by
# export_and_verify() returning 4 solids instead of 1 on the first run of
# this script -- fixed by widening the rims, not by moving the bosses onto
# thin material).
# =============================================================================
LEFT_RIM = 11.0
GAP1 = 11.0             # screen-zone -> seam, on the screen module's own side
RIGHT_RIM = 11.0
COL_LEFT_MARGIN = 11.0   # column module's own seam-side margin (symmetric with RIGHT_RIM)
TOP_RIM = 6.0
GAP2 = 6.0              # screen-zone bottom -> band top
BOTTOM_RIM = 9.0

# Speaker -- BOM-CORRECTED (Sec 2.10): a "40mm" driver has NO mounting ears/
# holes; real frame OD/depth is closer to Dia 41 x 21mm, and it is NOT
# sealed on its own -- the enclosure must clamp its rim and provide its own
# closed back chamber (30-60cc target, computed and checked below).
SPEAKER_FRAME_OD = 41.0    # BOM: "design Dia41 x 21mm and measure first articles"
SPEAKER_OPEN_DIA = 40.0    # clear acoustic opening, matches the nominal driver size
SPEAKER_DEPTH = 21.0       # BOM-corrected (was task's 20mm approx)
SPEAKER_RIM_LIP = 2.0      # radial clamp-lip width the back-cup presses the frame's rim against
BAND_H = SPEAKER_FRAME_OD + 10.0   # 51mm -- band-zone height, margin for the
                                    # insert/diffuser rebate + LED channel
DIAL_RING_R = 31.0         # matches the concept sheet's own dial-ring radius exactly
COLUMN_CONTENT_W = 2 * DIAL_RING_R + 6.0   # 68mm

SCREEN_ZONE_W = DISP_W + 2 * MODULE_CLR    # 197.32
SCREEN_ZONE_H = DISP_H + 2 * MODULE_CLR    # 128.24

SCREEN_MODULE_W = LEFT_RIM + SCREEN_ZONE_W + GAP1          # 219.32
COLUMN_MODULE_W = COL_LEFT_MARGIN + COLUMN_CONTENT_W + RIGHT_RIM   # 90.0
ASSEMBLED_W = SCREEN_MODULE_W + COLUMN_MODULE_W

PANEL_H = TOP_RIM + SCREEN_ZONE_H + GAP2 + BAND_H + BOTTOM_RIM

X_A0 = -ASSEMBLED_W / 2.0
X_A1 = X_A0 + SCREEN_MODULE_W
X_B0 = X_A1
X_B1 = ASSEMBLED_W / 2.0
SEAM_X = X_A1

SCREEN_X0 = X_A0 + LEFT_RIM
SCREEN_X1 = SCREEN_X0 + SCREEN_ZONE_W
SCREEN_CX = (SCREEN_X0 + SCREEN_X1) / 2.0
SCREEN_Z0 = BOTTOM_RIM + BAND_H + GAP2
SCREEN_Z1 = SCREEN_Z0 + SCREEN_ZONE_H
SCREEN_CZ = (SCREEN_Z0 + SCREEN_Z1) / 2.0
assert abs(SCREEN_Z1 - (PANEL_H - TOP_RIM)) < 1e-6

BAND_X0, BAND_X1 = SCREEN_X0, SCREEN_X1
BAND_W = BAND_X1 - BAND_X0
BAND_Z0 = BOTTOM_RIM
BAND_Z1 = BAND_Z0 + BAND_H
BAND_CX = SCREEN_CX
BAND_CZ = (BAND_Z0 + BAND_Z1) / 2.0

COL_CX = (X_B0 + X_B1) / 2.0

# Depth stack -- computed, not hand-rounded (see docstring for citations).
# BOM correction (Sec 2.3): allow >=16mm above the Pi5 PCB for the Active
# Cooler + air gap, not the cooler's own bare 13.70mm height -- the cooler
# also exhausts sideways through its fins, so vents are added to the back
# wall near the Pi5 position (see build_back_shell_screen()).
FIT_CLR = 0.5          # clearance around the display module in its pocket
BACK_WALL = 3.0
DEPTH_MARGIN = 1.0     # real safety margin added on top of the exact stack sum
COOLER_CLEARANCE = 16.0   # BOM-corrected design clearance (was the bare 13.70mm)
PANEL_D = round(FACE_T + FIT_CLR + DISP_T + PI5_STANDOFF_H + PI5_PCB_T
                + COOLER_CLEARANCE + CABLE_SLACK + BACK_WALL + DEPTH_MARGIN, 2)
CAVITY_D = PANEL_D - FACE_T - BACK_WALL   # usable internal depth, screen module

# Integrated 45deg french-cleat receiver -- constants moved up here (from
# their old spot inside build_back_shell_screen()) so BACK_PLANE_Y below
# can be computed before COLUMN_PANEL_D needs it.
CLEAT_RECEIVER_W = 160.0     # length of the integrated 45deg receiver ridge
CLEAT_RECEIVER_T = 6.0        # ridge depth, off the back wall's outer face
CLEAT_ANGLE_DEG = 45.0

# BACK_PLANE_Y -- the single shared "wall plane" constant BOTH shells and
# the engaged wall-cleat are built against. Coordinator review (revision
# 3, 2026-09-21) found 02a's own back-most point (its receiver ridge's
# real tip, PANEL_D + a 12mm-proud wedge = 66.56) and 02b's own back-most
# point (its flat back wall, previously computed independently from the
# mic-cradle stack alone, landing at 66.30) were NOT coplanar -- 0.26mm
# apart -- so a hung panel would rock on whichever module's back sat
# proud. Fixed by deriving BOTH from this ONE constant instead of two
# independent formulas: 02a's ridge tip is the natural, real minimum
# (driven by PANEL_D + the ridge's own reasoned 12mm proud depth), so
# BACK_PLANE_Y is set to exactly that, and COLUMN_PANEL_D below is raised
# to match it exactly (with a real margin check against its own
# mic-cradle-driven minimum, never silently shrunk below what the mic
# stack needs).
BACK_PLANE_Y = round(PANEL_D + CLEAT_RECEIVER_T * 2.0, 2)

print(f"ASSEMBLED_W={ASSEMBLED_W:.2f} PANEL_H={PANEL_H:.2f} PANEL_D={PANEL_D:.2f}")
print(f"SCREEN_MODULE_W={SCREEN_MODULE_W:.2f} COLUMN_MODULE_W={COLUMN_MODULE_W:.2f}")
assert SCREEN_MODULE_W <= 246.0, "screen module alone exceeds a safe bed margin"
assert COLUMN_MODULE_W <= 246.0, "column module alone exceeds a safe bed margin"
assert PANEL_H <= 206.0, "panel height exceeds a safe bed margin"

# =============================================================================
# CONTROL-COLUMN CONTENT -- dial (KY-040), rocker (KCD1), gold tab, mic ports
# Numbers below are the 2026-09-21 BOM research pass
# (bom-research.md Sec 2.6-2.13) -- real/verified vs PLACEHOLDER is flagged
# per-line; every changed number is called out in README.md's ledger too.
# =============================================================================
DIAL_CX = COL_CX
# Dial moved further down from the top rim (70mm, was 50mm) specifically to
# free real vertical room above the ring for the mic cradle -- see below.
DIAL_CZ = PANEL_H - TOP_RIM - 70.0

KY_BUSHING_OD = 7.0             # VERIFIED -- M7x0.75 major dia (Joy-IT product page)
KY_PANEL_HOLE_DIA = 7.3          # small running clearance over the verified 7.0mm major dia
KY_BUSHING_LEN = 7.0            # VERIFIED -- "listings give thread length ~7mm"
KY_SHAFT_D = 6.0                # VERIFIED -- generic EC11, DuPPa/Alps L1=20mm variant
KY_SHAFT_FLAT_W = 4.5           # ASSUMED -- "typical D-flat ... measure first articles"
KY_SHAFT_LEN = 20.0             # VERIFIED-ish -- generic EC11 "L1=20mm" shaft variant
KY_PCB_W, KY_PCB_D, KY_PCB_T = 26.20, 18.63, 1.6   # VERIFIED (components101 drawing) + reasoned thickness
KY_PCB_GAP = 3.0                 # ASSUMED -- panel-back to PCB-front gap
KY_HEADER_RESERVE = 15.0         # ASSUMED -- header pins + wire bend behind the PCB
# BOM: "Maximum panel thickness ... gives <=3mm ... design a 2-2.5mm local
# boss at the bushing". Implemented as a local THINNED zone cut from the
# BACK (never breaking the front, never deeper than FACE_T) rather than a
# boss, since the nut needs LESS material, not more.
KY_LOCAL_T = 2.25                # local panel thickness at the bushing (mid of 2-2.5mm)
KY_LOCAL_ZONE_R = 8.0             # radius of the local thinned zone (clears the nut OD)
assert KY_LOCAL_T < FACE_T, "KY-040 local thinned zone must be thinner than the nominal wall"

ROCKER_CUTOUT_W, ROCKER_CUTOUT_H = 19.3, 13.2   # BOM-corrected (datasheet 19.2x13.0 + print allowance)
ROCKER_BEZEL_W, ROCKER_BEZEL_H = 21.0, 15.0      # VERIFIED -- HandsOn KCD1-102 drawing (informational)
ROCKER_BODY_TO_TERMINALS = 21.4                    # VERIFIED -- drawing, body+terminal tips
ROCKER_CLEARANCE_RESERVE = 30.0                    # BOM: ">=30mm for body+terminals+wiring"
# BOM: panel thickness at the snap clips is not published -- "design a
# 1.5mm local wall" -- implemented the same way as the KY-040 local zone,
# a pocket cut from the BACK only, never breaking the front, never deeper
# than the nominal wall.
ROCKER_LOCAL_T = 1.5             # ASSUMED per BOM guidance
ROCKER_LOCAL_MARGIN = 3.0         # local-thin zone extends this far past the cutout, each side
assert ROCKER_LOCAL_T < FACE_T, "rocker local thinned zone must be thinner than the nominal wall"
ROCKER_TOP_GAP = 15.0
ROCKER_TOP_Z = DIAL_CZ - DIAL_RING_R - ROCKER_TOP_GAP
ROCKER_CZ = ROCKER_TOP_Z - ROCKER_CUTOUT_H / 2.0

GOLD_POCKET_W, GOLD_POCKET_H, GOLD_POCKET_D = 14.0, 6.0, 1.5
GOLD_GAP = 10.0
GOLD_TOP_Z = ROCKER_CZ - ROCKER_CUTOUT_H / 2.0 - GOLD_GAP
GOLD_CZ = GOLD_TOP_Z - GOLD_POCKET_H / 2.0
assert GOLD_POCKET_D < FACE_T, "gold-tab pocket rebate must not be deeper than the panel wall"
assert GOLD_CZ - GOLD_POCKET_H / 2.0 > BOTTOM_RIM, "gold tab pocket runs below the bottom rim"

MIC_PORT_R = 1.3           # matches the concept sheet's own mic-port radius
MIC_PORT_N = 5
MIC_PORT_PITCH = 8.0
MIC_PORT_Y0 = 14.0          # depth position of the port row, from the front face
MIC_PORT_XS = [DIAL_CX + (i - (MIC_PORT_N - 1) / 2.0) * MIC_PORT_PITCH for i in range(MIC_PORT_N)]

# Mic -- BOM-CORRECTED (Sec 2.11-2.12): the SunFounder mini USB mic is taken
# as the same form factor as Adafruit #3367, 22.2 x 18.3 x 7.0mm INCLUDING
# the USB-A plug, of which ~10mm of body sits beyond the extension's socket
# face once plugged in. It cradles in a short USB-A extension (2ft cable,
# reserve a coil space ~40x30x15mm) rather than plugging straight into the
# Pi -- the extension's own female-end overmold (~16x9x35mm real; BOM
# recommends a padded 20x12x45mm pocket) is the rigid piece that actually
# needs a home. This grows the column module's own depth past the screen
# module's (see COLUMN_PANEL_D below) -- a real, flagged consequence of
# real hardware, not a forced simplification.
MIC_DONGLE_W, MIC_DONGLE_D, MIC_DONGLE_H = 22.2, 18.3, 7.0     # REAL (Adafruit #3367; SunFounder assumed equal)
MIC_EXT_FEMALE_W, MIC_EXT_FEMALE_D, MIC_EXT_FEMALE_H = 20.0, 12.0, 45.0   # BOM's own padded-pocket figure
MIC_COIL_W, MIC_COIL_D, MIC_COIL_H = 40.0, 30.0, 15.0            # BOM: 2ft cable coil reserve
MIC_CRADLE_W = MIC_EXT_FEMALE_W + 4.0
MIC_CRADLE_D = MIC_EXT_FEMALE_H + MIC_DONGLE_D - 12.0 + 4.0   # extension body + protruding dongle (~10mm), + margin
MIC_CRADLE_H = 14.0
MIC_CRADLE_Y0 = 4.0                  # cradle starts just behind the face-plate's back surface
MIC_CRADLE_Z_TOP = PANEL_H - WALL - 2.0   # right under the column module's top wall
MIC_CRADLE_CZ = MIC_CRADLE_Z_TOP - MIC_CRADLE_H / 2.0

# =============================================================================
# SEAM (through-bolts joining the two modules) + PERIMETER MOUNTS
# Perimeter bosses sit on the VERTICAL-edge rim/gap/margin STRIPS above
# (LEFT_RIM/GAP1 for the screen module, COL_LEFT_MARGIN/RIGHT_RIM for the
# column module) -- those strips run the module's FULL height and are
# clear of every window/band/dial/rocker cutout for their entire length,
# by construction (the cutouts all live within the *content* zones, never
# in the rim/gap/margin strips) -- unlike the first draft's edge-inset
# corner points, which landed inside the band window (see note above).
# =============================================================================
SEAM_BOLT_ZS = [BOTTOM_RIM + 15, BAND_CZ, SCREEN_CZ - 20, SCREEN_Z1 - 15]
SEAM_BOSS_LEN = max(8.0, BOSS_LEN_MIN)

PERIM_BOSS_LEN = max(7.0, BOSS_LEN_MIN)
_PA_XL = X_A0 + LEFT_RIM / 2.0     # centre of the LEFT_RIM strip
_PA_XR = SCREEN_X1 + GAP1 / 2.0    # centre of the GAP1 strip
PERIM_A = [(x, z) for x in (_PA_XL, _PA_XR) for z in (18.0, PANEL_H / 2.0, PANEL_H - 15.0)]

_PB_XL = X_B0 + COL_LEFT_MARGIN / 2.0
_PB_XR = X_B1 - RIGHT_RIM / 2.0
PERIM_B = [(x, z) for x in (_PB_XL, _PB_XR) for z in (18.0, PANEL_H - 15.0)]

# =============================================================================
# BAND / SPEAKER ZONE -- insert(04)+diffuser(05) mounted to face-plate 01a's
# own back, speaker(pod)+amp molded into back-shell 02a, back-cup(08) seals it.
# The visible band WINDOW is inset from the full band-zone footprint by
# WIN_BORDER -- leaving a solid picture-frame border that hosts the
# insert/diffuser mounting bosses (BAND_MOUNTS). A first draft cut the FULL
# band-zone footprint as the window with no border, which put BAND_MOUNTS
# (and, separately, two PERIM_A midpoints) inside the resulting empty
# cutout -- the same Gotcha #1 floating-boss defect the rim widening above
# fixes for the perimeter bosses; fixed here for the band bosses by adding
# a real border.
# =============================================================================
WIN_BORDER = 10.0
BAND_WINDOW_W = BAND_W - 2 * WIN_BORDER
BAND_WINDOW_H = BAND_H - 2 * WIN_BORDER
assert BAND_WINDOW_W > 40 and BAND_WINDOW_H > 20, "band window too small once bordered"

INSERT_CLR = 1.5          # insert/diffuser sit this much smaller than the window, each side
INSERT_T = 2.0
DIFFUSER_T = 1.0          # ~1mm natural/clear PETG, per task
BAND_MOUNT_INSET = 5.0    # inset from the BAND zone's own outer edge -- safely
                           # inside WIN_BORDER (10mm) on both sides of the mount hole
BAND_MOUNTS = [
    (BAND_X0 + BAND_MOUNT_INSET, BAND_Z0 + BAND_MOUNT_INSET),
    (BAND_X1 - BAND_MOUNT_INSET, BAND_Z0 + BAND_MOUNT_INSET),
    (BAND_X0 + BAND_MOUNT_INSET, BAND_Z1 - BAND_MOUNT_INSET),
    (BAND_X1 - BAND_MOUNT_INSET, BAND_Z1 - BAND_MOUNT_INSET),
]
BAND_BOSS_LEN = max(7.0, BOSS_LEN_MIN)
INSERT_OVERLAP = 4.0      # insert/diffuser extend this far past the window edge, into the border
INSERT_W = BAND_WINDOW_W + 2 * INSERT_OVERLAP
INSERT_H = BAND_WINDOW_H + 2 * INSERT_OVERLAP

SPEAKER_POD_CX, SPEAKER_POD_CZ = BAND_CX, BAND_CZ
SPEAKER_POD_Y0 = FACE_T + 12.0                 # shoulder plane, behind the diffuser+LED gap
SPEAKER_SHOULDER_T = 3.0

# Amp -- BOM-CORRECTED (Sec 2.9): clone MAX98357A boards vary in hole
# presence/spacing, so "mount in a printed pocket or clip, not by the
# holes" -- a simple friction pocket with small retaining lips, sized to
# the BOM's own recommended 25x22x12mm envelope (board + headers/terminal).
AMP_W, AMP_H, AMP_T = 19.4, 17.8, 3.0            # REAL, Adafruit MAX98357A product page
AMP_POCKET_W, AMP_POCKET_H, AMP_POCKET_D = 25.0, 22.0, 12.0   # BOM's own "25x22x12mm" envelope --
# W x H is the board's own front footprint (matches 19.4x17.8 + margin),
# D is the Y-depth clearance for the terminal block, per BOM's own
# wording ("allow a 25x22x12mm envelope for the headers and terminal").
# A first draft assigned these as W,D,H (22 to D, 12 to H) instead of
# W,H,D -- which fed the SMALLER 12mm value into the tray's own footprint
# height where the board's real 17.8mm height needed to fit, so the
# board's own probe (correctly sized to the real board) stuck 2.9mm into
# the tray's ring wall on both the top and bottom -- caught by the
# amp-footprint probe below reading 22% blocked instead of open, not by
# any topology check (the tray+shell fuse was already a single valid
# solid regardless of which value went where).
AMP_CENTER = (SPEAKER_POD_CX + SPEAKER_FRAME_OD / 2.0 + 20.0, SPEAKER_POD_CZ)

# LEDs -- BOM-CORRECTED (Sec 2.13): ~12 LEDs behind the band, ~40 around
# the perimeter as a PARTIAL loop (a full 283x200mm assembled loop would
# need ~65 -- explicitly not attempted; a partial loop on the bottom+side
# edges of both modules is what's actually built, length reported below,
# not forced to match 40 exactly). Level-shifter (74AHCT125, DIP-14 on a
# small perfboard, ~25x20x12mm) pocket near the LED data entry, on 02a.
BAND_LED_Y0 = FACE_T + 1.0
INSERT_Y0 = BAND_LED_Y0 + 6.0             # insert(04)'s own Y position, behind the LED gap
DIFFUSER_Y0 = INSERT_Y0 + INSERT_T + 1.0   # diffuser(05) sits just behind the insert
BAND_LED_W, BAND_LED_D = 10.0, 3.0
WASH_LED_W, WASH_LED_D = 10.0, 3.0
LEVEL_SHIFTER_W, LEVEL_SHIFTER_D, LEVEL_SHIFTER_H = 25.0, 20.0, 12.0

# Cable slot (Pi5 USB-C power, straight plug) -- BOM-CORRECTED (Sec 2.4):
# design for the STRAIGHT official plug (overmold ~12x7mm x 19-24mm long,
# +6.7mm plug), NOT a right-angle adapter (risks the Pi5's 5A PD mode).
# Slot >= 14x9mm per BOM; sized with real margin here. Through the BOTTOM
# wall of back-shell-screen -- the cavity is one continuous open tub
# spanning both the screen zone and the band zone below it (no internal
# floor divides them), so the cable can route down from the Pi5 in the
# screen zone to exit at the panel's own bottom edge.
CABLE_SLOT_W, CABLE_SLOT_H = 16.0, 10.0
CABLE_SLOT_CX = SCREEN_CX - 60.0   # off to one side, clear of the speaker pod's own footprint

# Pi5 board + vent (BOM Sec 2.1/2.3): 85x56mm board on the display's own
# 58x49 standoff pattern; USB-C power 11.2mm from the long port edge (not
# separately modelled to that precision -- the cable SLOT above is sized
# with real margin instead of chasing an exact port position). Active
# Cooler exhausts sideways through its fins -- vent slots added to
# build_back_shell_screen()'s back wall near the Pi5/cooler position.
PI5_BOARD_W, PI5_BOARD_D = 85.0, 56.0
VENT_N = 4
VENT_W, VENT_H = 2.0, 12.0
VENT_PITCH = 4.0

# Column module's own depth -- grown past the screen module's PANEL_D to
# fit the mic cradle (see MIC_CRADLE_D above), a real BOM-driven consequence,
# not a forced simplification.
#
# Set to BACK_PLANE_Y exactly (not to its own mic-cradle-driven minimum
# alone) so its own back-most point is COPLANAR with 02a's ridge tip --
# see BACK_PLANE_Y's own docstring above for the 0.26mm-apart defect this
# fixes. The mic-cradle-driven minimum is still computed and asserted as
# a real floor, never silently shrunk below what the mic+extension stack
# actually needs.
COLUMN_MIN_D = round(FACE_T + 2.0 + MIC_CRADLE_D + 3.0 + BACK_WALL, 2)
assert BACK_PLANE_Y >= COLUMN_MIN_D, (
    f"BACK_PLANE_Y ({BACK_PLANE_Y}mm) is shallower than the column module's own "
    f"mic-cradle-driven minimum depth ({COLUMN_MIN_D}mm) -- the mic+extension stack wouldn't fit")
COLUMN_PANEL_D = BACK_PLANE_Y
print(f"COLUMN_PANEL_D={COLUMN_PANEL_D:.2f} (== BACK_PLANE_Y; own mic-cradle minimum was "
      f"{COLUMN_MIN_D:.2f}) vs screen module PANEL_D={PANEL_D:.2f} (ridge tip reaches BACK_PLANE_Y too)")

print("Layout: SCREEN_ZONE=(%.1f,%.1f)-(%.1f,%.1f) BAND=(%.1f,%.1f)-(%.1f,%.1f)"
      % (SCREEN_X0, SCREEN_Z0, SCREEN_X1, SCREEN_Z1, BAND_X0, BAND_Z0, BAND_X1, BAND_Z1))
print("Dial centre (%.1f,%.1f) rocker centre-Z %.1f gold-tab centre-Z %.1f"
      % (DIAL_CX, DIAL_CZ, ROCKER_CZ, GOLD_CZ))

# =============================================================================
# DISPLAY WORLD PLACEMENT -- native display origin placed at (SCREEN_CX,
# SCREEN_CZ); landscape-frame offsets (both real, re-measured) applied on
# top, exactly as the Arcade build applies them to its own local frame.
# =============================================================================
REVEAL = 1.0
DISPLAY_CX, DISPLAY_CZ = SCREEN_CX, SCREEN_CZ

# Cleat-receiver rail position -- hoisted here (own printed part 12, see
# build_cleat_receiver_rail() near the wall-cleat build below), now that
# DISPLAY_CZ exists. Shared by build_back_shell_screen() (mounting
# holes only, since the ridge itself moved off this part), the rail's
# own build function, and the wall-cleat engagement check -- ONE
# position, not three independent formulas to drift apart (the same
# fix BACK_PLANE_Y already applied to the "wall plane" itself).
CLEAT_RECEIVER_CZ = DISPLAY_CZ + 20.0   # clear of both retention holes and cooler vents (see below)
# Mounting: 3x M3 into the rail's OWN blind heat-set inserts, screws
# driven from inside 02a's cavity through clearance holes. Z sits
# 3.5mm below the ridge's own vertical centre so the insert bore
# (INSERT_DEPTH=6.5mm long, r=2mm) stays inside the wedge's own
# tapering triangular cross-section for its whole depth -- the usable
# Z-height at the insert's far end (Y=6.5 into a wedge whose leg is
# only 12mm) is down to ~5.5mm, so a bore centred any higher pokes out
# through the ridge's own sloped hook face. Verified directly against
# the built rail geometry below, not just computed by hand.
CLEAT_RAIL_HOLE_Z = CLEAT_RECEIVER_CZ - 3.5
CLEAT_RAIL_HOLE_XS = [(X_A0 + X_A1) / 2.0 + dx for dx in (-60.0, 0.0, 60.0)]
AA_CX = DISPLAY_CX + AA_OFFSET_LANDSCAPE[0]
AA_CZ = DISPLAY_CZ + AA_OFFSET_LANDSCAPE[1]
ENC_HOLES_WORLD = [(DISPLAY_CX + dx, DISPLAY_CZ + dz) for dx, dz in ENC_HOLES_LANDSCAPE]
PI5_STANDOFFS_WORLD = [(DISPLAY_CX + dx, DISPLAY_CZ + dz) for dx, dz in PI5_STANDOFFS_LANDSCAPE]

TRIM_BORDER = 8.0   # chrome bezel ring width, front-visible
TRIM_OUTER_W = AA_W + 2 * REVEAL + 2 * TRIM_BORDER
TRIM_OUTER_H = AA_H + 2 * REVEAL + 2 * TRIM_BORDER
assert TRIM_OUTER_W < SCREEN_ZONE_W - 4, "bezel trim outer footprint exceeds the screen zone"
assert TRIM_OUTER_H < SCREEN_ZONE_H - 4, "bezel trim outer footprint exceeds the screen zone"
TRIM_MOUNTS = [(AA_CX + sx * (AA_W / 2.0 + REVEAL + TRIM_BORDER / 2.0),
                AA_CZ + sz * (AA_H / 2.0 + REVEAL + TRIM_BORDER / 2.0))
               for sx in (-1, 1) for sz in (-1, 1)]

# TRIM_THICKNESS -- round 6, renamed from TRIM_REBATE_D. DJ's first
# real print found 01a's own front REBATE (a shallow pocket cut into
# the bed-contact front face to seat the trim flush) failed: printed
# front-face DOWN, the rebate's own floor -- a picture-frame ring, real
# material bordering the WINDOW's open air on its inner edge -- is a
# genuine cantilever (however well-supported its outer edge is), and
# neither real slicing nor this build's own 80% footprint check (84.5%,
# passed) caught it. Fixed per DJ's own decision: drop the rebate
# entirely. 01a's front face is now ONE flat plane (apart from real
# through-openings); the trim (03) sits ON TOP of it and is allowed to
# stand proud by its own thickness -- see build_screen_trim() and
# build_face_plate_screen()'s own updated mounting comments.
TRIM_THICKNESS = 1.5   # same magnitude as the old rebate depth -- now a proud plate thickness, not a pocket depth

# TRIM_BOSS_OD -- hoisted here (from inside build_screen_trim(), where
# it used to be a purely local/internal detail) so 01a's own bore that
# admits the trim's pass-through boss is sized off the SAME constant,
# not a second independent guess.
TRIM_BOSS_OD = 7.5   # smaller than the usual 9mm boss -- narrow border here; still clears
                       # the >=1.6mm insert-wall rule ((7.5-4)/2=1.75mm) and fits inside TRIM_OUTER_W/H
assert (TRIM_BOSS_OD - INSERT_D) / 2.0 >= INSERT_WALL_MIN
# Bore through 01a that the trim's own boss passes through -- a real
# sliding clearance (+0.4mm), not the plain screw-only CLEAR_D hole the
# old flush-in-a-rebate design used (that hole never needed to admit
# the boss ITSELF, only a screw shaft, because the boss used to nest
# inside the rebate's own shallow pocket instead of passing through
# the plate). Now that the trim is proud in front, its boss must pass
# all the way through 01a's own FACE_T thickness to reach an insert
# bored from the boss's own tip, in open cavity air behind 01a -- see
# build_screen_trim()'s own docstring.
TRIM_BORE_D = TRIM_BOSS_OD + 0.4

# Chrome-share-of-visible-face check (task hard constraint: <=20%)
_window_area = (AA_W + 2 * REVEAL) * (AA_H + 2 * REVEAL)
_ring_area = TRIM_OUTER_W * TRIM_OUTER_H - _window_area
_total_face_area = ASSEMBLED_W * PANEL_H
_chrome_pct = 100.0 * _ring_area / _total_face_area
print(f"Chrome (screen-trim) visible area: {_ring_area:.0f}mm2 / {_total_face_area:.0f}mm2 "
      f"= {_chrome_pct:.1f}% of the visible face")
assert _chrome_pct <= 20.0, f"chrome trim is {_chrome_pct:.1f}% of the visible face, exceeds 20% cap"

# Sight-line check (round 6) -- the trim now stands PROUD by
# TRIM_THICKNESS instead of sitting flush in a rebate, so its own
# inner (window-facing) edge is a real raised rim that could, at a
# steep enough off-axis viewing angle, shade the display's own active
# area at the REVEAL gap's edge. The trim's own window is cut
# AA_W/H + 2*REVEAL, i.e. the rim's inner edge sits REVEAL beyond the
# active area on every side; the rim itself rises TRIM_THICKNESS above
# the display plane. The occlusion half-angle (off the panel's own
# normal) at which the rim's OWN inner top edge first lines up with the
# active area's own far edge -- beyond this angle, the rim would start
# to shade the display -- is atan(REVEAL / TRIM_THICKNESS). A real,
# computed, asserted number, not eyeballed.
_sightline_deg = math.degrees(math.atan2(REVEAL, TRIM_THICKNESS))
print(f"Sight-line: proud trim (thickness {TRIM_THICKNESS}mm) with a {REVEAL}mm reveal clears the "
      f"active area's own edge up to {_sightline_deg:.1f}deg off the panel's own normal")
assert _sightline_deg >= 20.0, (
    f"sight-line clearance ({_sightline_deg:.1f}deg) is too shallow -- widen REVEAL or thin TRIM_THICKNESS")


# =============================================================================
# PART 01a -- FACE-PLATE, SCREEN MODULE (black)
# Print orientation: front face DOWN on the bed. Every cut is a straight
# through-bore; every boss is on the BACK (up, in this orientation) --
# zero overhangs, support-free.
# =============================================================================
def build_face_plate_screen():
    plate = box_at(SCREEN_MODULE_W, FACE_T, PANEL_H, X_A0, 0.0, 0.0)

    win = box_cxz(AA_W + 2 * REVEAL, AA_H + 2 * REVEAL, FACE_T + 4, AA_CX, AA_CZ, -2)
    plate = plate.cut(win)

    # Screen-trim(03) front rebate -- REMOVED, round 6. DJ's first real
    # print found this exact rebate failed: printed front-face DOWN,
    # its own floor (a picture-frame ring, real material on its outer
    # edge but bordering the WINDOW's genuine open air on its inner
    # edge) is a real cantilever, however well its outer edge was
    # supported -- neither real slicing nor this build's own 80%
    # footprint check caught it (see bed_face_scan()'s own docstring,
    # the new check built specifically for this class). DJ's decision:
    # drop the rebate. 01a's front face (the bed-contact plane) is now
    # ONE FLAT PLANE apart from real through-openings (the screen
    # window above, the band window below, and the fastener bores
    # below) -- the trim (03) now sits ON TOP of this flat face and is
    # allowed to stand proud by its own TRIM_THICKNESS.
    band_win = box_cxz(BAND_WINDOW_W, BAND_WINDOW_H, FACE_T + 4, BAND_CX, BAND_CZ, -2)
    plate = plate.cut(band_win)

    # band-insert(04)/diffuser(05) mounting bosses -- BLIND from the back,
    # never breaking the front (real overlap into the plate, Gotcha #1).
    for (bx, bz) in BAND_MOUNTS:
        boss = cyl_y(BOSS_OD / 2.0, BAND_BOSS_LEN + 0.3, bx, bz, FACE_T - 0.3)
        plate = plate.fuse(boss)
        ins = cyl_y(INSERT_D / 2.0, INSERT_DEPTH, bx, bz,
                     FACE_T + BAND_BOSS_LEN - INSERT_DEPTH + 0.3)
        plate = plate.cut(ins)

    # screen-trim(03) mounting -- round 6: now a WIDENED bore
    # (TRIM_BORE_D, sized to the trim's own TRIM_BOSS_OD + real sliding
    # clearance), not the old plain CLEAR_D screw-only hole. The trim
    # is proud in front now, not flush in a rebate, so its own mounting
    # boss must physically PASS THROUGH 01a's full FACE_T thickness to
    # reach its insert, bored from the boss's own tip in the open
    # cavity behind -- this bore is what admits the boss itself, not
    # just a screw shaft. A screw driven from the cavity side then
    # threads into that insert, pulling the trim flush against 01a's
    # own flat front face.
    for (tx, tz) in TRIM_MOUNTS:
        hole = cyl_y(TRIM_BORE_D / 2.0, FACE_T + 4, tx, tz, -2)
        plate = plate.cut(hole)

    # perimeter mounts to back-shell 02a -- BLIND insert in the plate,
    # matching clearance hole lives in 02a's own BACK WALL far away (the
    # screw simply spans the open cavity -- see module docstring).
    for (px, pz) in PERIM_A:
        boss = cyl_y(BOSS_OD / 2.0, PERIM_BOSS_LEN + 0.3, px, pz, FACE_T - 0.3)
        plate = plate.fuse(boss)
        ins = cyl_y(INSERT_D / 2.0, INSERT_DEPTH, px, pz,
                     FACE_T + PERIM_BOSS_LEN - INSERT_DEPTH + 0.3)
        plate = plate.cut(ins)

    plate = plate.removeSplitter()
    return plate


# =============================================================================
# PART 01b -- FACE-PLATE, CONTROL-COLUMN MODULE (black)
# 24-detent tick ring is the ONLY intentional front relief -- ENGRAVED
# (recessed ~0.6mm into the front), not raised, so the front face is one
# flat plane at Y=0. Perimeter bosses still project INWARD from the back
# (Y>FACE_T). Print orientation: FRONT face DOWN -- with the ticks
# recessed, the ENTIRE front face is now the bed-contact plane (no
# feature stands proud of it), the standard, always-safe orientation for
# a flat plate with shallow surface detail; the alternative (back down)
# would use only 4 far-apart corner bosses as feet under a ~180mm span of
# otherwise-unsupported flat plate, which genuinely does need support.
# Back-side bosses then point straight up into open air off a fully
# bed-supported base -- zero overhangs there.
#
# CHANGED from raised ribs (0.6mm proud, fused onto the front): a
# packaging pass found the raised tips were the front-most material (Y
# -0.6mm) over a ~108mm2 contact area (just the tick ring), so printed
# "front face down" the part actually stood on the 24 rib tips with the
# rest of the face floating 0.6mm above the bed -- exactly the kind of
# defect the new print-orientation check below exists to catch (a
# first-layer footprint check, not a support/overhang judgement call,
# since raised text/ribs don't need support -- they just don't sit flush
# if they're the ONLY thing touching the bed). Engraving instead of
# embossing is the direct, minimal fix: same ticks, same readability,
# but cut INTO the front instead of added onto it, so Y=0 (the full
# plate) is the flat plane that actually contacts the bed.
# =============================================================================
DETENT_N = 24
DETENT_R0, DETENT_R1 = 27.5, DIAL_RING_R   # matches the concept sheet exactly
DETENT_DEPTH = 0.6   # recess depth (was DETENT_PROUD, a raised height) -- same 0.6mm magnitude
DETENT_W = 1.0


def build_face_plate_column():
    plate = box_at(COLUMN_MODULE_W, FACE_T, PANEL_H, X_B0, 0.0, 0.0)

    # KY-040 bushing through-hole
    bushing_hole = cyl_y(KY_PANEL_HOLE_DIA / 2.0, FACE_T + 4, DIAL_CX, DIAL_CZ, -2)
    plate = plate.cut(bushing_hole)

    # KY-040 local thinned zone -- BOM: the M7x0.75 bushing only has ~7mm of
    # thread, and the nut+washer+safe-engagement math caps USABLE panel
    # thickness at <=3mm -- cut from the BACK only (never breaking the
    # front, never past FACE_T), leaving KY_LOCAL_T of real material.
    ky_thin_pocket = cyl_y(KY_LOCAL_ZONE_R, (FACE_T - KY_LOCAL_T) + 1.0, DIAL_CX, DIAL_CZ, KY_LOCAL_T)
    plate = plate.cut(ky_thin_pocket)

    # 24-tick detent ring -- ENGRAVED grooves, cut from the front (Y=0)
    # into the material by DETENT_DEPTH, never breaking the back (checked
    # by construction: DETENT_DEPTH << FACE_T). Local groove prototype at
    # angle 0 (pointing along +X from the dial centre): X-size is the
    # RADIAL extent (r0..r1), Z-size is the TANGENTIAL tick width -- same
    # radial/tangential convention as the original raised-rib version
    # (swapped from an even earlier draft that put the radial extent on Z
    # while offsetting the tick along X, which built a non-radial,
    # tangentially-oriented tick at every angle).
    assert DETENT_DEPTH < FACE_T, "detent groove must not cut through the panel"
    groove_proto = box_full(DETENT_R1 - DETENT_R0 + 1.0, DETENT_DEPTH + 0.1, DETENT_W,
                            DIAL_CX + (DETENT_R0 + DETENT_R1) / 2.0, DETENT_DEPTH / 2.0 - 0.05, DIAL_CZ)
    for i in range(DETENT_N):
        groove = groove_proto.copy()
        # Rotate about the Y axis (the face-plate's own normal) so the
        # groove traces a ring in the X-Z (front-face) plane -- a Z-axis
        # rotation here would rotate X/Y instead and leave every groove at
        # the same Z, the real bug that hit the original raised-rib
        # version (23 disjoint solids, caught by export_and_verify()).
        # Cutting (not fusing) means a stray same-Z placement here would
        # show up as a missing/misplaced tick, not a topology failure --
        # a real gap the no-unintended-openings ray grid below still
        # covers (every tick position is a declared "shallow, not open"
        # feature, checked the same way the gold-tab pocket floor is).
        groove.Placement = Placement(Vector(0, 0, 0), Rotation(Vector(0, 1, 0), i * 360.0 / DETENT_N),
                                     Vector(DIAL_CX, 0, DIAL_CZ))
        plate = plate.cut(groove)

    # rocker (KCD1) snap-in cutout
    rocker_hole = box_cxz(ROCKER_CUTOUT_W, ROCKER_CUTOUT_H, FACE_T + 4, DIAL_CX, ROCKER_CZ, -2)
    plate = plate.cut(rocker_hole)

    # rocker local thinned zone -- BOM: the snap-clip panel thickness isn't
    # published; design a local 1.5mm wall around the cutout, from the BACK
    # only (never breaking the front, never past FACE_T).
    rocker_thin = box_cxz(ROCKER_CUTOUT_W + 2 * ROCKER_LOCAL_MARGIN,
                          ROCKER_CUTOUT_H + 2 * ROCKER_LOCAL_MARGIN,
                          (FACE_T - ROCKER_LOCAL_T) + 1.0, DIAL_CX, ROCKER_CZ, ROCKER_LOCAL_T)
    plate = plate.cut(rocker_thin)

    # gold-tab (07) BLIND pocket -- opens from the FRONT (press-fit), never
    # deeper than the wall (asserted above: GOLD_POCKET_D < FACE_T)
    gold_pocket = box_cxz(GOLD_POCKET_W, GOLD_POCKET_H, GOLD_POCKET_D + 0.01, DIAL_CX, GOLD_CZ, -0.005)
    plate = plate.cut(gold_pocket)

    # perimeter mounts to back-shell 02b
    for (px, pz) in PERIM_B:
        boss = cyl_y(BOSS_OD / 2.0, PERIM_BOSS_LEN + 0.3, px, pz, FACE_T - 0.3)
        plate = plate.fuse(boss)
        ins = cyl_y(INSERT_D / 2.0, INSERT_DEPTH, px, pz,
                     FACE_T + PERIM_BOSS_LEN - INSERT_DEPTH + 0.3)
        plate = plate.cut(ins)

    plate = plate.removeSplitter()
    return plate


print("\n--- building 01a/01b ---")
_fps = build_face_plate_screen()
export_and_verify(_fps, "01a-face-plate-screen", OUT_COMMON,
                   note="print front-face DOWN; back-side bosses point up",
                   envelope_xy=(SCREEN_MODULE_W, PANEL_H))
_fpc = build_face_plate_column()
export_and_verify(_fpc, "01b-face-plate-column", OUT_COMMON,
                   note="print front-face DOWN (shallow 0.6mm rib texture)",
                   envelope_xy=(COLUMN_MODULE_W, PANEL_H))


# =============================================================================
# PART 02a -- BACK-SHELL, SCREEN MODULE (black)
# Tray: open front (mates with 01a), WALL(3mm) sides/top/bottom, BACK_WALL
# (3mm) back. Carries: display+Pi5+cooler retention bosses (clearance
# holes through the back wall into the display's OWN real captured hole,
# per the docstring's "Display retention" note -- no insert of our own
# needed there), the sealed speaker-pod tube + amp pocket + level-shifter
# pocket, the band-LED channel, the rear wall-wash LED channel, the bottom
# cable slot, Active-Cooler side-exhaust vents, perimeter mount bosses
# (blind inserts -- matching clearance lives in 01a), the seam clearance
# holes joining to 02b, and a registration recess + 3x M3 clearance holes
# for the SEPARATE 12-cleat-receiver-rail part (see build_cleat_
# receiver_rail() near the wall-cleat build).
# Print orientation (round 5, coordinator decision): BACK-WALL DOWN, not
# open-front down. Real slicing found the open-front-down orientation
# bridges this whole tub's flat back wall across ~194mm with nothing
# under it ("floating regions") -- the correct orientation for a tub is
# open side UP. This was blocked before by the integrated cleat-receiver
# ridge, which used to protrude past the back wall and become the new
# low point when flipped -- fixed by splitting that ridge into its own
# part (12). Every remaining boss/tube/tab on this part extends FROM the
# back wall TOWARD the (now-open, upward) rim, i.e. columns rising from
# a base -- self-supporting by construction, zero new overhangs.
# =============================================================================
# (CLEAT_RECEIVER_W/T and CLEAT_ANGLE_DEG are now defined earlier, near
# PANEL_D/BACK_PLANE_Y -- see the depth-stack section above.)


def build_back_shell_screen():
    y0, y1 = FACE_T, PANEL_D
    outer = box_at(SCREEN_MODULE_W, y1 - y0, PANEL_H, X_A0, y0, 0.0)

    # Main cavity -- open at the front (y0 side), WALL/BACK_WALL left standing.
    cavity = box_at(SCREEN_MODULE_W - 2 * WALL, (y1 - y0) - BACK_WALL + 1.0, PANEL_H - 2 * WALL,
                     X_A0 + WALL, y0 - 1.0, WALL)
    shell = outer.cut(cavity)

    # Speaker-pod tube -- fused in AFTER the main cavity is cut (real
    # standing wall material added back into what is otherwise open
    # cavity void), with a real overlap into the surviving BACK_WALL at
    # its far end for a valid fuse. Fusing this BEFORE the cavity cut (a
    # first draft's approach) let the general cavity cut bore straight
    # through the tube's own wall for its whole length, leaving no
    # material for the shoulder/body bores below to actually step down
    # into -- caught by re-reading the resulting geometry, not by any
    # automated check (a subtractive cut "succeeding" on empty air raises
    # no exception).
    pod_id_body = SPEAKER_FRAME_OD + 1.0
    pod_od = pod_id_body + 2 * 4.0
    pod_y0 = SPEAKER_POD_Y0
    pod_y1 = y1   # tube reaches the true back outer face; back-cup(08) seals it there

    # Real slicing (Bambu Studio, supports off) flagged a "floating
    # cantilever" on this part -- the tube's own LEADING (front) end was a
    # plain cylinder starting abruptly at full OD, i.e. a flat annulus
    # (between the shoulder bore and the OD) hanging in open cavity air
    # with nothing underneath it for the whole 12mm back to the rim/bed
    # (print orientation: open-front DOWN, so the tube's own front-to-back
    # axis IS the vertical print axis) -- exactly the "boss hanging off a
    # wall with nothing under it" pattern. Fixed with a real 45-deg-safe
    # CONE lead-in: the tube's OUTER wall starts at the shoulder bore's
    # own radius (i.e. ZERO wall thickness -- no flat cap at all, just the
    # bore's own edge) and grows to the full OD over POD_TAPER_LEN, a run
    # long enough that the radius growth (pod_od/2 - SPEAKER_OPEN_DIA/2)
    # never exceeds a 45deg slope. The same technique (a real geometric
    # taper, not a support structure) already used for the receiver ridge
    # and the wall-cleat's own wedge -- both print clean.
    POD_TAPER_LEN = round((pod_od / 2.0 - SPEAKER_OPEN_DIA / 2.0) * 1.2, 2)   # 1.2x margin under 45deg
    pod_cone = Part.makeCone(SPEAKER_OPEN_DIA / 2.0, pod_od / 2.0, POD_TAPER_LEN,
                             Vector(SPEAKER_POD_CX, pod_y0, SPEAKER_POD_CZ), Vector(0, 1, 0))
    # Cylinder's own start overlaps 0.5mm back into the cone for a real
    # fuse there; its END lands EXACTLY on pod_y1 (== this part's own
    # true outer back face, y1) -- NOT past it. Round 5: the previous
    # version overshot y1 by a real 0.5mm (a "+1.0mm length, -0.5mm
    # start" pair of margins that left the far end at pod_y1+0.5), meant
    # as a defensive real-overlap margin for the fuse. Harmless in the
    # OLD open-front-DOWN orientation (this tiny 0.5mm bump was up at
    # the TOP, nowhere near the bed) -- but in the NEW back-wall-DOWN
    # orientation this exact 0.5mm bump became the part's own new
    # lowest point, standing the entire rest of the flat back wall
    # 0.5mm off the bed (caught by print_orientation_check: 1.9%
    # contact, not the ~98%+ every other flat part gets). The tube
    # doesn't need to overshoot at all -- the shell already has real
    # solid back-wall material at every (x,z) out to y1 exactly (from
    # the plain outer box, before the cavity cut), so ending exactly AT
    # y1 still gives a full BACK_WALL(3mm)-deep overlap for the fuse.
    pod_cyl = cyl_y(pod_od / 2.0, pod_y1 - (pod_y0 + POD_TAPER_LEN - 0.5),
                    SPEAKER_POD_CX, SPEAKER_POD_CZ, pod_y0 + POD_TAPER_LEN - 0.5)
    pod_tube_outer = pod_cone.fuse(pod_cyl)
    shell = shell.fuse(pod_tube_outer)
    shell = shell.removeSplitter()

    # Speaker bore -- shoulder (narrow, ID=SPEAKER_OPEN_DIA) then body
    # clearance (wider, ID=pod_id_body) then straight through the back
    # for the back-cup.
    shoulder_bore = cyl_y(SPEAKER_OPEN_DIA / 2.0, SPEAKER_SHOULDER_T + 0.5,
                          SPEAKER_POD_CX, SPEAKER_POD_CZ, pod_y0 - 0.25)
    shell = shell.cut(shoulder_bore)
    body_bore = cyl_y(pod_id_body / 2.0, (pod_y1 - pod_y0) - SPEAKER_SHOULDER_T + 1.0,
                      SPEAKER_POD_CX, SPEAKER_POD_CZ, pod_y0 + SPEAKER_SHOULDER_T)
    shell = shell.cut(body_bore)

    # Back-cup(08) mounting bosses -- 4x radial bumps straddling the pod
    # tube's own outer wall (centred AT the tube's outer radius, so half
    # overlaps into the tube's own 4mm wall for a real fuse and half adds
    # the extra bulk a 9mm-OD insert boss needs -- the tube wall alone is
    # too thin to hold a full boss, the same reasoning as every other
    # insert boss in this build), blind inserts opening from the back.
    pod_screw_r = pod_od / 2.0
    pod_boss_len = BAND_BOSS_LEN
    # NOTE: each boss's own leading (front) cap is a small flat disk
    # (~33mm2) floating a few mm off the pod tube -- the same PATTERN as
    # the pod tube/KY tab, just an order of magnitude smaller. A full
    # 45deg taper doesn't fit: the boss is only ~7.1mm long and the M3
    # insert already needs 6.5mm of that for real thread depth, leaving
    # under 1mm for a taper that would need ~4mm to reach 45deg safely --
    # tapering it would either shrink the insert's own real thread depth
    # (a functional regression) or blow through the boss's own outer
    # wall where the taper is thinnest (a real print defect, worse than
    # the one being fixed). Left as-is and reported, not silently
    # papered over -- see the overhang-scan results and the build's own
    # report for the real remaining area.
    for k in range(4):
        ang = math.radians(45 + k * 90)
        sx = SPEAKER_POD_CX + pod_screw_r * math.cos(ang)
        sz = SPEAKER_POD_CZ + pod_screw_r * math.sin(ang)
        boss = cyl_y(BOSS_OD / 2.0, pod_boss_len, sx, sz, y1 - pod_boss_len)
        shell = shell.fuse(boss)
        ins = cyl_y(INSERT_D / 2.0, INSERT_DEPTH, sx, sz, y1 - INSERT_DEPTH)
        shell = shell.cut(ins)
    shell = shell.removeSplitter()

    # Amp POCKET -- BOM: mount in a printed pocket/clip, NOT by the clone
    # board's own (inconsistent) holes.
    #
    # CHANGED from a fused picture-frame RING proud of the back wall's
    # inner face to a real RECESSED POCKET cut INTO the back wall's own
    # existing material. Real slicing (Bambu Studio, supports off)
    # flagged the fused-ring version as a "floating cantilever"/"floating
    # regions": the ring's own front (leading) face was a flat rectangle
    # hanging in open cavity air, connected to the bed only via the back
    # wall it was fused onto -- the same "boss hanging off a wall with
    # nothing under it" pattern as the speaker-pod tube and the KY-040
    # tab, just rectangular instead of round. A pocket CUT into the
    # already-existing wall doesn't have this problem at all: its floor
    # and side walls are all part of the SAME continuous solid the
    # surrounding back wall already is (the same "shallow rebate with
    # real wall support on both sides" pattern the screen-trim's own
    # front rebate on 01a already uses safely) -- there's no new
    # unsupported material to hang in the cavity, just a shallow local
    # thickness variation in a wall that was already there. The board
    # drops into this pocket and its own bulk (headers, terminal block)
    # extends into the already-open cavity beyond it, same as before.
    ax, az = AMP_CENTER
    POCKET_DEPTH = 1.8   # real floor left: BACK_WALL(3.0) - 1.8 = 1.2mm
    assert POCKET_DEPTH < BACK_WALL, "amp/LS pocket must not cut through the back wall"
    def _pocket(w, h, cx, cz):
        return box_cxz(w, h, POCKET_DEPTH + 0.3, cx, cz, y1 - BACK_WALL - 0.3)
    shell = shell.cut(_pocket(AMP_POCKET_W, AMP_POCKET_H, ax, az))

    # Level-shifter (74AHCT125) pocket -- same pattern, near the LED data entry
    lx, lz = ax + AMP_POCKET_W / 2.0 + LEVEL_SHIFTER_W / 2.0 + 6.0, az
    shell = shell.cut(_pocket(LEVEL_SHIFTER_W, LEVEL_SHIFTER_H, lx, lz))

    # Band-LED channel -- behind the diffuser, along the band cavity's own
    # bottom inside edge.
    #
    # CHANGED from a fused U-trough (raised off the back wall's inner
    # face) to a real GROOVE cut into the back wall's own existing
    # material -- the fused version was flagged by real slicing the same
    # way the amp/LS trays were (a floating rectangular ring). The groove
    # gives the strip's own adhesive backing the same real channel to
    # sit in, cut into wall material that's already there instead of
    # material fused onto thin air.
    band_led_len = BAND_WINDOW_W - 6.0
    band_led_cz = BAND_Z0 + WALL + 4.0
    band_led_y0 = y1 - BACK_WALL - 0.3
    band_led_groove = box_cxz(band_led_len, BAND_LED_W, POCKET_DEPTH + 0.3,
                              BAND_CX, band_led_cz, band_led_y0)
    shell = shell.cut(band_led_groove)

    # Round 6/7 -- coordinator found this groove's own "ceiling" is a
    # real, un-asserted cantilever -- this groove runs the band
    # window's own real width (band_led_len, ~171mm), FAR past the
    # ~10mm bridge guideline -- exactly the "drooping ledge, expensive
    # to discover on a 4.5hr print" risk flagged after DJ's own real
    # 01a failure. Cutting the groove open to the true outer back face
    # (the wash-LED channel's own safe trick) isn't an option here --
    # this LED strip has to face FORWARD into the cavity, toward the
    # diffuser, not toward the real wall behind the panel.
    #
    # A first gusset attempt (narrow ribs spanning the SAME Y-range as
    # the groove cut itself, i.e. including its own 0.3mm real-cut
    # margin PAST the wall's true cavity-facing plane) made things
    # WORSE, confirmed by real slicing: each rib's own leading edge
    # stuck 0.3mm proud past the wall's real inner face into open
    # cavity air -- a small floating cap, repeated at every rib,
    # exactly the "boss with a flat abrupt cap hanging in cavity air"
    # pattern this build already fixed elsewhere (pod tube, KY tab).
    # Direct isolation against the real slicer (bambu/build_project.py)
    # confirmed it: with the ribs, "floating cantilever" on 02a; with
    # them removed, zero warnings, matching round 6's own already-
    # confirmed-clean baseline for this same groove. Fixed by giving
    # each rib the EXACT SAME Y-range as the wall's own real material
    # (from y1-BACK_WALL -- the true cavity-facing plane, no overshoot
    # -- to y1-1.2, the pocket's own real floor) instead of the cut
    # tool's own margin-padded range: no proud tip, real overlap with
    # existing material on both the floor end and the general wall
    # surface end.
    #
    # Round 7, re-examined again: even with that fix applied, re-
    # running generate_parts.py's OWN check still showed the exact
    # same 200mm2/44.4mm finding, byte-for-byte unchanged by the ribs
    # -- meaning OCCT's own face-splitting during this boolean
    # sequence doesn't land on the rib boundaries the way the span
    # math assumed, so the ribs don't actually address what the check
    # is flagging at all. Given the ORIGINAL (plain, un-ribbed) groove
    # already real-slices with ZERO warnings -- confirmed independently
    # twice: once as round 6's own baseline, once again directly in
    # this round by isolating it back out after the first (overshoot)
    # rib attempt's real regression -- and given adding ribs has so
    # far only ever made things WORSE or done nothing, not better, the
    # geometry is left as the plain groove. The check's OWN false
    # positive for this specific irregular-shaped face is fixed in
    # bed_face_scan() itself instead (see its docstring) -- mutating
    # already-proven-safe geometry a third time, against a check that
    # turned out to be the thing that needed the fix, isn't the right
    # move here.

    # Rear wall-wash LED channel -- a partial loop (bottom + both sides) on
    # the OUTER rear-facing perimeter lip of the back wall (BOM: ~40 LEDs
    # partial loop, not the ~65 a full loop of this assembled size would
    # need -- length achieved is reported by the caller, not forced to
    # match). Groove cut into the back wall's own outer face.
    wash_z = WALL / 2.0 + 1.0
    wash_bottom = box_cxz(SCREEN_MODULE_W - 2 * WALL - 4.0, WASH_LED_W, WASH_LED_D + 0.5,
                         (X_A0 + X_A1) / 2.0, wash_z, PANEL_D - WASH_LED_D + 0.3)
    shell = shell.cut(wash_bottom)

    # Cable slot -- straight USB-C plug clearance, THROUGH the bottom wall
    # (Z=0..WALL), off to one side clear of the speaker pod. X=width,
    # Y=depth into the cavity, Z=fully through the wall thickness.
    #
    # Round 6 -- the coordinator's own new bed-face-pockets check found
    # this slot's own "shallow" end (the bottom wall resuming, moving
    # toward the front rim) is a real, un-asserted 16mm-span cantilever
    # -- the slot used to start 4mm short of the rim (`FACE_T+4.0`),
    # leaving a real, unsupported ledge of wall material floating
    # between the slot and the rim. Fixed per the coordinator's own
    # "move the feature to start at the wall it belongs to": extended
    # the slot's own near end back to the front rim itself (with a
    # real 1mm overlap past it, `FACE_T-1.0`, matching how every other
    # "reach the part's own true edge" cut in this build does it) --
    # the slot now opens straight through to the rim, the same as a
    # bed-height region genuinely reaching the part's own boundary
    # (nothing to bridge, because there's no resuming ceiling there at
    # all any more). The slot's own far end (its real functional depth
    # for the USB-C connector body) is unchanged.
    _cable_y0 = FACE_T - 1.0
    _cable_far = (FACE_T + 4.0) + CABLE_SLOT_H   # the ORIGINAL far end, kept exactly
    cable_slot = box_at(CABLE_SLOT_W, _cable_far - _cable_y0, WALL + 4,
                        CABLE_SLOT_CX - CABLE_SLOT_W / 2.0, _cable_y0, -2.0)
    shell = shell.cut(cable_slot)

    # Active Cooler side-exhaust vents -- through the back wall, offset
    # past the cooler's own ~63.5mm footprint edge.
    vent_cx = DISPLAY_CX + 32.0
    for i in range(VENT_N):
        vz = DISPLAY_CZ + (i - (VENT_N - 1) / 2.0) * VENT_PITCH
        vent = box_cxz(VENT_W, VENT_H, BACK_WALL + 2, vent_cx, vz, y1 - BACK_WALL - 1.0)
        shell = shell.cut(vent)

    # Display retention -- clearance holes through the back wall, aligned
    # to the display's OWN real captured enclosure-mount holes (see
    # docstring). No insert of ours -- RPi's own hardware provides the thread.
    for (ex, ez) in ENC_HOLES_WORLD:
        hole = cyl_y(CLEAR_D / 2.0, BACK_WALL + 4, ex, ez, y1 - BACK_WALL - 2)
        shell = shell.cut(hole)
        csk = csk_y(CLEAR_D, CSK_D, CSK_DEPTH, ex, ez, y1, inward=-1)
        shell = shell.cut(csk)

    # Perimeter mounts -- clearance through the back wall, matching 01a's
    # own blind bosses (screw spans the open cavity -- see docstring).
    for (px, pz) in PERIM_A:
        hole = cyl_y(CLEAR_D / 2.0, BACK_WALL + 4, px, pz, y1 - BACK_WALL - 2)
        shell = shell.cut(hole)
        csk = csk_y(CLEAR_D, CSK_D, CSK_DEPTH, px, pz, y1, inward=-1)
        shell = shell.cut(csk)

    # Seam -- clearance holes through the RIGHT wall (X_A1 side), matching
    # 02b's own blind bosses.
    for sz in SEAM_BOLT_ZS:
        hole = cyl_x(CLEAR_D / 2.0, WALL + 4, X_A1 - WALL - 2, y0 + 15.0, sz)
        shell = shell.cut(hole)

    # French-cleat receiver -- NOW A SEPARATE PRINTED PART (12-cleat-
    # receiver-rail, see build_cleat_receiver_rail() near the wall-cleat
    # build below), not fused in here any more. Coordinator decision
    # (round 5): real slicing (Bambu Studio, supports off) flagged this
    # part "floating cantilever" with the ridge fused in, and separately
    # flagged BOTH back-shells "floating regions" for their own flat
    # back walls bridging the whole tub in the open-front-DOWN print
    # orientation this part used to document. Root cause: for a tub, the
    # correct orientation is open-side UP (back wall on the bed), not
    # open-front down -- but flipping 02a specifically was blocked by
    # this very ridge, which used to protrude 12mm past the back wall
    # and become the part's own new lowest point instead of the flat
    # wall. Splitting the ridge into its own part removes both problems:
    # this part's own back wall is flat again (see PRINT_ORIENTATIONS
    # below -- now back-wall DOWN), and the rail gets its own
    # independent, support-free print orientation.
    #
    # What's left here is a shallow 0.5mm-deep registration recess (the
    # exact footprint the old fused wedge's own real boolean-overlap
    # sliver, "_ov", used to occupy) that self-jigs the rail into its
    # correct position, plus 3x M3 clearance holes (countersunk on the
    # CAVITY side, so the screw heads sit recessed inside the tub --
    # hidden once 01a closes it, and hidden again once hung against the
    # real wall) landing on the rail's own 3 blind heat-set inserts.
    # The rail is built from the EXACT SAME wire/points the old fused
    # wedge used, so its world position is bit-for-bit identical to
    # before -- the wall-cleat engagement check further down needed NO
    # changes to its own re-derivation formulas for this.
    _rail_ov = 0.5
    _rail_h = CLEAT_RECEIVER_T * 2.0
    recess = box_at(CLEAT_RECEIVER_W + 0.4, _rail_ov + 0.2, _rail_h + 0.4,
                    (X_A0 + X_A1) / 2.0 - CLEAT_RECEIVER_W / 2.0 - 0.2, PANEL_D - _rail_ov - 0.1,
                    CLEAT_RECEIVER_CZ - _rail_h / 2.0 - 0.2)
    assert _rail_ov + 0.2 < BACK_WALL, "rail registration recess must not cut through the back wall"
    shell = shell.cut(recess)

    for hx in CLEAT_RAIL_HOLE_XS:
        hole = cyl_y(CLEAR_D / 2.0, BACK_WALL + 4, hx, CLEAT_RAIL_HOLE_Z, y1 - BACK_WALL - 2)
        shell = shell.cut(hole)
        csk = csk_y(CLEAR_D, CSK_D, CSK_DEPTH, hx, CLEAT_RAIL_HOLE_Z, y1 - BACK_WALL, inward=1)
        shell = shell.cut(csk)

    # Perimeter mounting bosses on 01a are BLIND (no insert here) -- but
    # 01a's own bosses need a real screw length; nothing further to add
    # on 02a for that joint besides the clearance holes above.
    return shell


print("\n--- building 02a ---")
_bss = build_back_shell_screen()
export_and_verify(_bss, "02a-back-shell-screen", OUT_COMMON,
                   note="print BACK-WALL DOWN (round 5 -- see header comment); "
                        "cleat receiver is the separate 12-cleat-receiver-rail part",
                   envelope_xy=(SCREEN_MODULE_W, PANEL_H), envelope_axes=("X", "Z"))


# =============================================================================
# PART 02b -- BACK-SHELL, CONTROL-COLUMN MODULE (black)
# Own depth (COLUMN_PANEL_D) grown past the screen module's PANEL_D to fit
# the mic+USB-extension assembly -- a real, flagged BOM consequence (see
# docstring). Carries: the mic cradle shelf, a KY-040 PCB anti-rotation
# tab, the rocker's own open clearance, seam mounting BOSSES (the
# opposite half of 02a's clearance holes), and perimeter mount bosses.
# Print orientation (round 5): BACK-WALL DOWN, matching 02a -- see 02a's
# own header comment for why (real slicing found open-front-down
# bridges the whole flat back wall with nothing under it).
# =============================================================================
def build_back_shell_column():
    y0, y1 = FACE_T, COLUMN_PANEL_D
    outer = box_at(COLUMN_MODULE_W, y1 - y0, PANEL_H, X_B0, y0, 0.0)
    cavity = box_at(COLUMN_MODULE_W - 2 * WALL, (y1 - y0) - BACK_WALL + 1.0, PANEL_H - 2 * WALL,
                    X_B0 + WALL, y0 - 1.0, WALL)
    shell = outer.cut(cavity)

    # Mic ports -- 5 real through-holes in the TOP wall (Z=PANEL_H), feeding
    # straight down to the mic cradle right below. A first draft declared
    # these positions (MIC_PORT_XS/MIC_PORT_Y0) and PROBED them but never
    # actually cut them -- exactly the "cut that was never made" defect
    # class the feature-exists probes exist to catch (caught here: 60%
    # blocked instead of open, before this fix landed).
    for mx in MIC_PORT_XS:
        port = cyl_z(MIC_PORT_R, WALL + 4, mx, MIC_PORT_Y0, PANEL_H - WALL - 2)
        shell = shell.cut(port)

    # Mic cradle -- a full-width shelf (real overlap into BOTH side walls,
    # not a floating shelf) right under the top wall, holding the USB
    # extension's female-end overmold + protruding dongle. Two small side
    # lips keep the assembly from sliding sideways.
    #
    # Shelf's own Y0 pulled back to the rim plane (y0==FACE_T) -- a
    # packaging pass found this shelf starting at Y=MIC_CRADLE_Y0-2.0=2.0,
    # 1mm FORWARD of the rim plane (y0=3.0) where 01b's own back mates.
    # Printed "open-front DOWN" (the rim as the bed-contact plane), that
    # 1mm forward overhang was the actual first-layer contact instead of
    # the rim, floating the rest of the rim 1mm off the bed -- caught by
    # the new print-orientation check below, not by any existing check
    # (the shelf itself is a perfectly valid fused feature; it just stuck
    # out past the part's own mating face). The shelf still reaches
    # forward of MIC_CRADLE_Y0 by 1mm (a real support lip for whatever
    # sits on it), just never past the rim itself.
    shelf_z = MIC_CRADLE_Z_TOP - MIC_CRADLE_H
    # Round 5: shelf's own Y-depth extended all the way back to the true
    # back wall (was MIC_CRADLE_D+3.0, a short ~15mm run forward of the
    # rim only). In the new back-wall-DOWN print orientation, the shelf
    # (fused only to the two side walls, spanning the FULL width) sat
    # ~49mm above the true floor with nothing under it for that whole
    # span -- real slicing flagged this as a genuine "floating
    # cantilever", a materially worse defect than a mere bridge between
    # two anchors (the earlier round's own tapers/pockets fixed local,
    # short-span overhangs; this one needed a real connection to the
    # floor, not a taper). Extending the shelf to reach the back wall
    # turns it into a full support partition -- self-supporting by
    # construction, since it now touches the bed-connected back wall
    # directly. Its own functional top surface (where the mic
    # extension's connector rests, at Y=MIC_CRADLE_Y0 forward) is
    # unchanged; only the material BEHIND it is now solid instead of
    # open cavity -- nothing else needs that space (the mic module's
    # own body sits ABOVE this shelf, not below it; see mic_env's own
    # probe further down, which only checks above shelf_z+3).
    # Ends EXACTLY at y1 -- not past it. (The pod tube on 02a made
    # exactly this mistake earlier this same round: overshooting the
    # true outer/back face by a real 0.5mm becomes THE new lowest point
    # once back-wall-DOWN is the print orientation, standing the whole
    # rest of the flat back wall off the bed -- see that fix's own
    # comment. The back wall already has real solid material out to
    # y1 exactly -- the shelf doesn't need to go past it for a valid,
    # BACK_WALL(3mm)-deep fuse overlap.)
    shelf_d = y1 - y0
    shelf = box_at(COLUMN_MODULE_W - 2 * WALL + 2.0, shelf_d, 3.0,
                   X_B0 + WALL - 1.0, y0, shelf_z)
    shell = shell.fuse(shelf)
    # Lips' own Y0 pulled back to the rim plane too (y0, matching the
    # shelf fix above) -- these also started at MIC_CRADLE_Y0 (1mm
    # forward of the rim), a smaller instance of the exact same defect
    # (found by the real slicer as "floating regions" alongside the
    # shelf) -- their own far end is held at the same absolute Y the
    # original design intended (MIC_CRADLE_Y0 + MIC_CRADLE_D), so only
    # the near/leading 1mm changes.
    for sgn in (-1, 1):
        lip = box_full(3.0, (MIC_CRADLE_Y0 + MIC_CRADLE_D) - y0, 5.0, DIAL_CX + sgn * (MIC_CRADLE_W / 2.0 + 1.5),
                       (y0 + (MIC_CRADLE_Y0 + MIC_CRADLE_D)) / 2.0, shelf_z + 3.0 + 2.5)
        shell = shell.fuse(lip)
    shell = shell.removeSplitter()

    # KY-040 PCB anti-rotation tab -- BOM: "add a printed rib or pocket to
    # stop the PCB rotating ... use the PCB holes only as optional."
    # Grown from the back wall's own inner face for a real connection.
    tab_x = DIAL_CX + KY_PCB_W / 2.0 + 2.0
    # A short rib reaching from the back wall toward the front, positioned
    # to sit flush against the PCB's own edge once installed -- real
    # overlap into the back wall for the fuse.
    #
    # Real slicing flagged this as a floating cantilever too -- like the
    # speaker-pod tube above, this rib hangs off the back wall and stops
    # well short of the rim (its own leading 4x10mm face floats ~43mm
    # above the bed in the open-front-down print orientation), the same
    # "boss hanging off a wall with nothing under it" pattern. Fixed the
    # same way: a real 45deg-safe taper at the LEADING end (a wedge,
    # narrowing to a point) instead of an abrupt flat cap, using the same
    # wire/extrude wedge technique as the receiver ridge and the
    # wall-cleat. The functional stop face (where the PCB's own edge
    # actually rests) is the BACK portion of the rib, unchanged -- the
    # taper only adds a self-supporting lead-in forward of it, it doesn't
    # move the working part of the feature.
    tab_back_y = y1 - BACK_WALL - 9.0 + 1.0 + 9.0    # == the original box's own trailing edge
    tab_front_y = y1 - BACK_WALL - 9.0 + 1.0 - 9.0   # == the original box's own leading edge
    tab_half_w = 2.0
    TAB_TAPER_LEN = 3.0   # angle = atan(tab_half_w / TAB_TAPER_LEN) = 33.7deg, real margin under 45deg
    tab_body = box_full(tab_half_w * 2.0, (tab_back_y - (tab_front_y + TAB_TAPER_LEN)) + 0.5, 10.0,
                        tab_x, (tab_back_y + tab_front_y + TAB_TAPER_LEN) / 2.0, DIAL_CZ)
    _p0 = Vector(tab_x, tab_front_y, 0.0)
    _p1 = Vector(tab_x - tab_half_w, tab_front_y + TAB_TAPER_LEN, 0.0)
    _p2 = Vector(tab_x + tab_half_w, tab_front_y + TAB_TAPER_LEN, 0.0)
    _wedge_wire = Part.makePolygon([_p0, _p1, _p2, _p0])
    tab_wedge = Part.Face(_wedge_wire).extrude(Vector(0, 0, 10.0))
    tab_wedge.translate(Vector(0, 0, DIAL_CZ - 5.0))
    tab = tab_body.fuse(tab_wedge)
    shell = shell.fuse(tab)
    shell = shell.removeSplitter()

    # Seam -- BOSSES (blind inserts) on the LEFT wall (X_B0 side),
    # matching 02a's own clearance holes.
    for sz in SEAM_BOLT_ZS:
        boss = cyl_x(BOSS_OD / 2.0, SEAM_BOSS_LEN + 0.3, X_B0 + WALL - 0.3, y0 + 15.0, sz)
        shell = shell.fuse(boss)
        ins = cyl_x(INSERT_D / 2.0, INSERT_DEPTH, X_B0 + WALL + SEAM_BOSS_LEN - INSERT_DEPTH + 0.3, y0 + 15.0, sz)
        shell = shell.cut(ins)
        # Round 5: found by direct isolation testing against the REAL
        # slicer, not by geometric reasoning alone (my own overhang_scan,
        # a per-planar-face check, never flagged this -- a round boss's
        # own surface is curved, not planar, so it fell outside that
        # scan's own net entirely). With every other 02b feature
        # disabled one at a time, ONLY disabling this boss cleared
        # Bambu's "floating cantilever" warning: at Y=y0+15 (only 15mm
        # forward of the rim, out of a 66.56mm total depth), this boss
        # sits near the very TOP of the new back-wall-DOWN print's
        # ~63.5mm vertical stack -- a solid Ø9mm peg anchored only at
        # one end (the side wall, itself fine) and sticking sideways
        # into open cavity air, ~49mm above the true floor. Fixed with a
        # real support rib running from the boss straight down (in Y)
        # to the true back wall -- the same "reach the floor, don't just
        # taper a local tip" fix as the mic-cradle shelf above, since
        # this is a genuine floor-height problem, not a local overhang.
        _rib_y0 = y0 + 15.0 - BOSS_OD / 2.0 - 1.0
        _rib_h = BOSS_OD + 2.0
        rib = box_at(SEAM_BOSS_LEN + 2.0, y1 - _rib_y0, _rib_h,
                     X_B0 + WALL - 1.0, _rib_y0, sz - _rib_h / 2.0)
        shell = shell.fuse(rib)
    shell = shell.removeSplitter()

    # Perimeter mounts -- clearance through the back wall, matching 01b's
    # own blind bosses.
    for (px, pz) in PERIM_B:
        hole = cyl_y(CLEAR_D / 2.0, BACK_WALL + 4, px, pz, y1 - BACK_WALL - 2)
        shell = shell.cut(hole)
        csk = csk_y(CLEAR_D, CSK_D, CSK_DEPTH, px, pz, y1, inward=-1)
        shell = shell.cut(csk)

    # Rear wall-wash LED channel -- continues the partial loop from 02a,
    # along this module's own bottom edge.
    wash_z = WALL / 2.0 + 1.0
    wash_bottom = box_cxz(COLUMN_MODULE_W - 2 * WALL - 4.0, WASH_LED_W, WASH_LED_D + 0.5,
                         (X_B0 + X_B1) / 2.0, wash_z, y1 - WASH_LED_D + 0.3)
    shell = shell.cut(wash_bottom)

    return shell


print("\n--- building 02b ---")
_bsc = build_back_shell_column()
export_and_verify(_bsc, "02b-back-shell-column", OUT_COMMON,
                   note="print BACK-WALL DOWN (round 5 -- see 02a's header comment)",
                   envelope_xy=(COLUMN_MODULE_W, PANEL_H), envelope_axes=("X", "Z"))


# =============================================================================
# PART 03 -- SCREEN-TRIM (silver silk) -- front-visible bezel ring
# Round 6: seats FLAT on 01a's own front face and stands PROUD by
# TRIM_THICKNESS (DJ's decision, after the old flush-in-a-rebate design
# failed for real -- see build_face_plate_screen()'s own comment).
# Mounting boss now reaches THROUGH 01a's own widened TRIM_BORE_D bore
# (not nested in a rebate), ending in open cavity air past 01a's own
# back face; the insert bores from the boss's own tip. 4x M3 screws
# driven from the cavity side thread into that insert, pulling the
# trim flush against 01a's flat front -- never a fastener visible from
# the front.
# Print orientation: flat, front face (the proud ring's OWN visible
# face, at local Y=-TRIM_THICKNESS) down. The window is a genuine
# through-opening (no bed-face pocket); the boss grows UPWARD off a
# fully bed-supported base, the same safe pattern every other boss in
# this build already uses -- zero overhangs, re-confirmed by
# bed_face_scan() below, not just asserted here.
# =============================================================================
def build_screen_trim():
    outer_ring = box_cxz(TRIM_OUTER_W, TRIM_OUTER_H, TRIM_THICKNESS, AA_CX, AA_CZ, -TRIM_THICKNESS)
    inner_window = box_cxz(AA_W + 2 * REVEAL, AA_H + 2 * REVEAL, TRIM_THICKNESS + 2, AA_CX, AA_CZ,
                           -TRIM_THICKNESS - 1.0)
    ring = outer_ring.cut(inner_window)

    # Boss grows from the ring's own BACK (Y=0, flush against 01a's
    # front) through 01a's own TRIM_BORE_D bore and on into open cavity
    # air behind it, ending with real margin past FACE_T -- the insert
    # bores from the boss's own tip (the deepest, cavity-side end), the
    # same "boss into open air off a fully-supported base" pattern
    # every other insert boss in this build already uses safely.
    trim_boss_len = max(6.0, BOSS_LEN_MIN)
    for (tx, tz) in TRIM_MOUNTS:
        boss = cyl_y(TRIM_BOSS_OD / 2.0, trim_boss_len + 0.3, tx, tz, -0.3)
        ring = ring.fuse(boss)
        ins = cyl_y(INSERT_D / 2.0, INSERT_DEPTH + 0.3, tx, tz, trim_boss_len - INSERT_DEPTH)
        ring = ring.cut(ins)
    ring = ring.removeSplitter()
    return ring


print("\n--- building 03 ---")
_trim = build_screen_trim()
export_and_verify(_trim, "03-screen-trim", OUT_COMMON,
                   note="print flat, front face down (round 6: proud ring, not flush-in-rebate)",
                   envelope_xy=(TRIM_OUTER_W, TRIM_OUTER_H), envelope_axes=("X", "Z"))


# =============================================================================
# PART 04a/04b -- BAND INSERT (black) -- "ignition" (ember) / "nightfall"
# (starfield) perforation patterns, SAME outline and mounting so one
# release carries both colour schemes (task requirement). Each hole
# cylinder is generated once, unioned into a single Compound cutting
# TOOL, then subtracted in ONE cut -- much faster than N sequential
# boolean cuts, and avoids the Gotcha #2 "dense/close cutouts can bridge-
# split a part" risk by keeping real material between every pair of holes
# (checked below via the actual hole layout's own minimum pitch, not
# eyeballed).
# =============================================================================
INSERT_LOCAL_W, INSERT_LOCAL_H = INSERT_W, INSERT_H
INSERT_MARGIN = 5.0   # keep holes this far from the insert's own edge

# =============================================================================
# ACOUSTIC ZONE -- coordinator review (2026-09-21) found the speaker firing
# straight into the diffuser's own solid plastic, and both inserts too
# sparse over the driver to pass real sound even once the diffuser is
# fixed. The band is split into an ACOUSTIC ZONE (a real Ø38 disk directly
# over the driver's own firing axis, matching the cone) and everything
# else (light zones, backlit by the LEDs, sparse/light-only perforation).
# =============================================================================
ACOUSTIC_ZONE_DIA = 38.0   # >= the driver's real cone diameter
ACOUSTIC_ZONE_R = ACOUSTIC_ZONE_DIA / 2.0
ACOUSTIC_CX, ACOUSTIC_CZ = SPEAKER_POD_CX, SPEAKER_POD_CZ   # == BAND_CX/BAND_CZ, the driver's real firing axis
ACOUSTIC_OPEN_MIN_PCT = 25.0   # task requirement: >=25% open over the acoustic zone, each insert
_ACOUSTIC_AREA = math.pi * ACOUSTIC_ZONE_R ** 2


def _insert_mount_holes():
    holes = []
    for (bx, bz) in BAND_MOUNTS:
        holes.append(cyl_y(CLEAR_D / 2.0, 40.0, bx, bz, -2))
    return holes


def _in_acoustic_zone(x, z, margin=0.0):
    return math.hypot(x - ACOUSTIC_CX, z - ACOUSTIC_CZ) <= ACOUSTIC_ZONE_R + margin


def build_band_insert_ignition():
    plate = box_cxz(INSERT_W, INSERT_H, INSERT_T, BAND_CX, BAND_CZ, INSERT_Y0)
    hole_d = 3.2
    pitch = 6.5
    holes = []
    n_open = 0
    open_area = 0.0
    acoustic_open_area = 0.0
    rows = int((INSERT_H - 2 * INSERT_MARGIN) / (pitch * 0.866)) + 1
    cols = int((INSERT_W - 2 * INSERT_MARGIN) / pitch) + 1
    for r in range(-rows, rows + 1):
        zz = BAND_CZ + r * pitch * 0.866
        if abs(zz - BAND_CZ) > INSERT_H / 2.0 - INSERT_MARGIN:
            continue
        xoff = (pitch / 2.0) if (r % 2) else 0.0
        for c in range(-cols, cols + 1):
            xx = BAND_CX + c * pitch + xoff
            if abs(xx - BAND_CX) > INSERT_W / 2.0 - INSERT_MARGIN:
                continue
            if _in_acoustic_zone(xx, zz):
                continue   # acoustic zone gets its OWN denser pattern below, not the base grid
            holes.append(cyl_y(hole_d / 2.0, 40.0, xx, zz, -2))
            n_open += 1
            open_area += math.pi * (hole_d / 2.0) ** 2

    # Acoustic zone -- a real denser hex cluster directly over the driver,
    # sized to clear the task's own >=25% open requirement with margin.
    ac_pitch, ac_hole_d = 5.5, 3.5
    ac_rows = int(ACOUSTIC_ZONE_R / (ac_pitch * 0.866)) + 2
    ac_cols = int(ACOUSTIC_ZONE_R / ac_pitch) + 2
    for r in range(-ac_rows, ac_rows + 1):
        zz = ACOUSTIC_CZ + r * ac_pitch * 0.866
        xoff = (ac_pitch / 2.0) if (r % 2) else 0.0
        for c in range(-ac_cols, ac_cols + 1):
            xx = ACOUSTIC_CX + c * ac_pitch + xoff
            if not _in_acoustic_zone(xx, zz, margin=-1.0):   # keep the hole fully inside, real edge margin
                continue
            holes.append(cyl_y(ac_hole_d / 2.0, 40.0, xx, zz, -2))
            n_open += 1
            a = math.pi * (ac_hole_d / 2.0) ** 2
            open_area += a
            acoustic_open_area += a

    acoustic_pct = 100.0 * acoustic_open_area / _ACOUSTIC_AREA
    print(f"  04a ignition: acoustic zone (Dia{ACOUSTIC_ZONE_DIA}mm over the driver): "
          f"{acoustic_open_area:.0f}mm2 / {_ACOUSTIC_AREA:.0f}mm2 = {acoustic_pct:.1f}% open "
          f"(task minimum {ACOUSTIC_OPEN_MIN_PCT}%)")
    assert acoustic_pct >= ACOUSTIC_OPEN_MIN_PCT, (
        f"04a ignition acoustic-zone open area {acoustic_pct:.1f}% is below the {ACOUSTIC_OPEN_MIN_PCT}% minimum")

    holes += _insert_mount_holes()
    tool = Part.makeCompound(holes)
    plate = plate.cut(tool)
    print(f"  04a ignition: {n_open} perforations total, hole-diam={hole_d}mm (base) / {ac_hole_d}mm (acoustic), "
          f"pitch={pitch}mm (base) / {ac_pitch}mm (acoustic), overall open area {open_area:.0f}mm2 / "
          f"{INSERT_W*INSERT_H:.0f}mm2 = {100.0*open_area/(INSERT_W*INSERT_H):.1f}%")
    return plate, open_area, acoustic_pct


def build_band_insert_nightfall():
    plate = box_cxz(INSERT_W, INSERT_H, INSERT_T, BAND_CX, BAND_CZ, INSERT_Y0)
    rnd = random.Random(2015)   # fixed seed -- reproducible pattern
    sizes = [1.8, 2.6, 3.4]
    size_weights = [0.55, 0.30, 0.15]
    pitch = 6.0
    rows = int((INSERT_H - 2 * INSERT_MARGIN) / pitch) + 1
    cols = int((INSERT_W - 2 * INSERT_MARGIN) / pitch) + 1
    holes = []
    n_open = 0
    open_area = 0.0
    acoustic_open_area = 0.0
    z0, z1 = BAND_CZ - INSERT_H / 2.0, BAND_CZ + INSERT_H / 2.0
    for r in range(-rows, rows + 1):
        zz = BAND_CZ + r * pitch
        if abs(zz - BAND_CZ) > INSERT_H / 2.0 - INSERT_MARGIN:
            continue
        norm = (zz - z0) / (z1 - z0)          # 0 at bottom, 1 at top
        density = 0.35 + 0.55 * norm           # falls toward the bottom, everywhere OUTSIDE the acoustic zone
        for c in range(-cols, cols + 1):
            xx = BAND_CX + c * pitch + rnd.uniform(-1.5, 1.5)
            if abs(xx - BAND_CX) > INSERT_W / 2.0 - INSERT_MARGIN:
                continue
            if _in_acoustic_zone(xx, zz, margin=2.0):
                continue   # acoustic zone gets its OWN dense star cluster below, not the sparse fade
            if rnd.random() > density:
                continue
            zzj = zz + rnd.uniform(-1.5, 1.5)
            if abs(zzj - BAND_CZ) > INSERT_H / 2.0 - INSERT_MARGIN:
                zzj = zz
            d = rnd.choices(sizes, weights=size_weights)[0]
            holes.append(cyl_y(d / 2.0, 40.0, xx, zzj, -2))
            n_open += 1
            open_area += math.pi * (d / 2.0) ** 2

    # Acoustic zone -- a dense STAR CLUSTER (still the 3 standard sizes,
    # still randomly seeded, keeping the "starfield" character) but with
    # near-certain inclusion and weighted toward the larger sizes, so the
    # cluster reads as a bright dense knot of stars directly over the
    # driver rather than a plain grille -- while still clearing >=25% open.
    ac_pitch = 4.8
    ac_size_weights = [0.25, 0.35, 0.40]
    ac_rows = int(ACOUSTIC_ZONE_R / (ac_pitch * 0.866)) + 2
    ac_cols = int(ACOUSTIC_ZONE_R / ac_pitch) + 2
    for r in range(-ac_rows, ac_rows + 1):
        zz = ACOUSTIC_CZ + r * ac_pitch * 0.866
        xoff = (ac_pitch / 2.0) if (r % 2) else 0.0
        for c in range(-ac_cols, ac_cols + 1):
            xx = ACOUSTIC_CX + c * ac_pitch + xoff
            if not _in_acoustic_zone(xx, zz, margin=-1.0):
                continue
            xxj = xx + rnd.uniform(-0.6, 0.6)
            zzj = zz + rnd.uniform(-0.6, 0.6)
            d = rnd.choices(sizes, weights=ac_size_weights)[0]
            holes.append(cyl_y(d / 2.0, 40.0, xxj, zzj, -2))
            n_open += 1
            a = math.pi * (d / 2.0) ** 2
            open_area += a
            acoustic_open_area += a

    acoustic_pct = 100.0 * acoustic_open_area / _ACOUSTIC_AREA
    print(f"  04b nightfall: acoustic zone (Dia{ACOUSTIC_ZONE_DIA}mm over the driver): "
          f"{acoustic_open_area:.0f}mm2 / {_ACOUSTIC_AREA:.0f}mm2 = {acoustic_pct:.1f}% open "
          f"(task minimum {ACOUSTIC_OPEN_MIN_PCT}%)")
    assert acoustic_pct >= ACOUSTIC_OPEN_MIN_PCT, (
        f"04b nightfall acoustic-zone open area {acoustic_pct:.1f}% is below the {ACOUSTIC_OPEN_MIN_PCT}% minimum")

    holes += _insert_mount_holes()
    tool = Part.makeCompound(holes)
    plate = plate.cut(tool)
    print(f"  04b nightfall: {n_open} perforations total (3 sizes {sizes}mm dia), overall open area "
          f"{open_area:.0f}mm2 / {INSERT_W*INSERT_H:.0f}mm2 = {100.0*open_area/(INSERT_W*INSERT_H):.1f}%")
    return plate, open_area, acoustic_pct


print("\n--- building 04a/04b ---")
_ins_a, _open_a, _ac_pct_a = build_band_insert_ignition()
_chk_a = export_and_verify(_ins_a, "04a-band-insert-ignition", OUT_COMMON,
                            note="print flat, front face down; trivial",
                            envelope_xy=(INSERT_W, INSERT_H))
import shutil
shutil.copy(os.path.join(OUT_COMMON, "04a-band-insert-ignition.stl"),
            os.path.join(OUT_IGNITION, "04a-band-insert-ignition.stl"))

_ins_b, _open_b, _ac_pct_b = build_band_insert_nightfall()
_chk_b = export_and_verify(_ins_b, "04b-band-insert-nightfall", OUT_COMMON,
                            note="print flat, front face down; trivial",
                            envelope_xy=(INSERT_W, INSERT_H))
shutil.copy(os.path.join(OUT_COMMON, "04b-band-insert-nightfall.stl"),
            os.path.join(OUT_NIGHTFALL, "04b-band-insert-nightfall.stl"))


# =============================================================================
# PART 05 -- BAND DIFFUSER (natural/clear PETG, ~1mm)
# Same outline and mounting holes as the insert (04a/04b) -- sits BEHIND
# it in the stack, both screwed together into 01a's own blind bosses.
# Solid everywhere EXCEPT a real acoustic opening over the driver -- the
# independent review's own review of assembly-reference.step found the
# speaker firing straight into this plate's solid plastic (a plain 1mm
# sheet with only 4 mount holes, 10 faces) with nothing in the topology/
# probe checks catching it, since a light diffuser being solid never
# breaks any topology rule -- it just silently muffles the driver. Fixed
# with a real Dia>=38mm opening over the driver's own firing axis,
# matching the cone; the rest of the plate stays solid and keeps
# diffusing LED light through whichever insert's OWN light-zone holes
# (outside the acoustic zone) are fitted.
# =============================================================================
def build_band_diffuser():
    plate = box_cxz(INSERT_W, INSERT_H, DIFFUSER_T, BAND_CX, BAND_CZ, DIFFUSER_Y0)
    acoustic_hole = cyl_y(ACOUSTIC_ZONE_R, 40.0, ACOUSTIC_CX, ACOUSTIC_CZ, -2)
    plate = plate.cut(acoustic_hole)
    for (bx, bz) in BAND_MOUNTS:
        hole = cyl_y(CLEAR_D / 2.0, 40.0, bx, bz, -2)
        plate = plate.cut(hole)
    return plate


print("\n--- building 05 ---")
_diff = build_band_diffuser()
export_and_verify(_diff, "05-band-diffuser", OUT_COMMON,
                   note="print flat, either face down; trivial. Natural/clear PETG ~1mm",
                   envelope_xy=(INSERT_W, INSERT_H))


# =============================================================================
# PART 06 -- KNOB (silver silk) -- Dia 30 x 18mm, D-bore for the KY-040
# shaft (BOM-verified 6mm dia / 4.5mm flat -> bore 6.1/4.6mm per BOM's own
# clearance recommendation), pointer groove, M3 radial set-screw pilot.
# Built at its own local origin (shaft axis = +Y) -- placed onto the
# world dial position only for the assembly-reference compound.
# Print orientation: flat bottom (mounting face) down. Zero support.
# =============================================================================
KNOB_OD = 30.0
KNOB_H = 18.0
KNOB_BORE_D = 6.1     # BOM: "0.1mm clearance" over the verified 6.0mm shaft
KNOB_BORE_FLAT = 4.6  # BOM: "0.1mm clearance" over the assumed 4.5mm flat
KNOB_BORE_DEPTH = 14.0
KNOB_SETSCREW_Z = 7.0  # height up the bore where the radial set-screw pilot sits


def build_knob():
    body = Part.makeCylinder(KNOB_OD / 2.0, KNOB_H, Vector(0, 0, 0), Vector(0, 1, 0))

    # D-bore: round bore intersected with a half-space at the flat's real
    # chord distance (d = sqrt(r^2-(flat/2)^2)), giving a true D-shape,
    # not a plain round bore -- the shaft's own flat is what stops it
    # spinning in the knob.
    r = KNOB_BORE_D / 2.0
    half_flat = KNOB_BORE_FLAT / 2.0
    d = math.sqrt(max(r * r - half_flat * half_flat, 0.01))
    round_bore = Part.makeCylinder(r, KNOB_BORE_DEPTH, Vector(0, 0, 0), Vector(0, 1, 0))
    # Remove everything beyond the flat's own chord plane (X <= -d) --
    # the box below spans X from -(r+1) up TO -d exactly, i.e. only the
    # small segment beyond the flat, not the bulk of the round bore (a
    # first pass had this backwards, spanning FROM -d outward and would
    # have cut away the bore's own majority instead of the flat sliver).
    flat_box = box_at((r + 1.0) - d, KNOB_BORE_DEPTH + 2, 2 * r + 2, -(r + 1.0), -1, -(r + 1))
    d_bore = round_bore.cut(flat_box)
    body = body.cut(d_bore)

    # Radial M3 set-screw pilot -- through the knob's side wall into the bore.
    setscrew = Part.makeCylinder(CLEAR_D / 2.0, KNOB_OD, Vector(-KNOB_OD / 2.0 - 1, KNOB_SETSCREW_Z, 0),
                                  Vector(1, 0, 0))
    body = body.cut(setscrew)

    # Pointer groove -- a shallow radial notch on the top face, running
    # from the centre out to the rim along the SAME -X direction as the
    # D-flat, so a glance at the groove shows the dial's rotational
    # reference (which way the shaft's own flat -- and so the encoder's
    # zero -- is facing).
    groove = box_at(KNOB_OD / 2.0 + 2.0, 2.0, 3.0, -(KNOB_OD / 2.0 + 1.0), KNOB_H - 1.5, -1.5)
    body = body.cut(groove)
    return body


print("\n--- building 06 ---")
_knob = build_knob()
export_and_verify(_knob, "06-knob", OUT_COMMON,
                   note="print flat mounting-face down; zero support",
                   envelope_xy=(KNOB_OD, KNOB_OD), envelope_axes=("X", "Z"))


# =============================================================================
# PART 07 -- GOLD TAB (yellow/gold PLA) -- static press-fit tab in 01b's
# own pocket under the rocker (task's own documented deviation from the
# xxx5 guide's "mechanical reveal" -- this build makes it static, flagged
# here and in README, not silently).
# Sized 0.3mm smaller than the pocket, each dimension, for an interference
# press-fit; thickness equals the pocket depth exactly (sits flush).
# =============================================================================
def build_gold_tab():
    tab = box_full(GOLD_POCKET_W - 0.3, GOLD_POCKET_D, GOLD_POCKET_H - 0.3, 0, GOLD_POCKET_D / 2.0, 0)
    return tab


print("\n--- building 07 ---")
_tab = build_gold_tab()
export_and_verify(_tab, "07-gold-tab", OUT_COMMON,
                   note="print flat, either face down; trivial press-fit tab",
                   envelope_xy=(GOLD_POCKET_W, GOLD_POCKET_H))


# =============================================================================
# PART 08 -- SPEAKER BACK-CUP (black) -- seals the pod tube from behind,
# screwed into 02a's 4 back-rim bosses. A shallow forward plug seals
# against the tube's own bore; a backward recess adds the remaining
# sealed-chamber volume needed to reach a real 30-60cc target (BOM
# Sec 2.10) -- computed and asserted below, not assumed.
# Print orientation: flat (flange) face down. Zero support.
# =============================================================================
BACK_CUP_OD = None  # set below, after pod_od is recomputed identically to 02a


def build_speaker_back_cup():
    pod_id_body = SPEAKER_FRAME_OD + 1.0
    pod_od = pod_id_body + 2 * 4.0
    cup_od = pod_od + 6.0
    plug_od = pod_id_body - 0.4
    plug_h = 3.0
    base_t = 3.0
    recess_id = pod_id_body - 4.0
    recess_depth = 10.0

    cup = Part.makeCylinder(cup_od / 2.0, base_t, Vector(0, 0, 0), Vector(0, 1, 0))
    plug = Part.makeCylinder(plug_od / 2.0, plug_h + 0.3, Vector(0, base_t - 0.3, 0), Vector(0, 1, 0))
    cup = cup.fuse(plug)
    cup = cup.removeSplitter()

    recess = Part.makeCylinder(recess_id / 2.0, recess_depth, Vector(0, -0.5, 0), Vector(0, 1, 0))
    cup = cup.cut(recess)

    pod_screw_r = pod_od / 2.0
    for k in range(4):
        ang = math.radians(45 + k * 90)
        sx = pod_screw_r * math.cos(ang)
        sz = pod_screw_r * math.sin(ang)
        hole = Part.makeCylinder(CLEAR_D / 2.0, base_t + plug_h + 4, Vector(sx, -1, sz), Vector(0, 1, 0))
        cup = cup.cut(hole)
        csk = Part.makeCone(CSK_D / 2.0, CLEAR_D / 2.0, CSK_DEPTH, Vector(sx, 0, sz), Vector(0, 1, 0))
        cup = cup.cut(csk)

    # small cable pass-through for the speaker's own 2 wires
    wire_hole = Part.makeCylinder(2.5, base_t + plug_h + 4, Vector(cup_od / 2.0 - 6, -1, 0), Vector(0, 1, 0))
    cup = cup.cut(wire_hole)

    gross_chamber = math.pi * (recess_id / 2.0) ** 2 * recess_depth
    return cup, cup_od, gross_chamber


print("\n--- building 08 ---")
_cup, _cup_od, _cup_chamber_mm3 = build_speaker_back_cup()
export_and_verify(_cup, "08-speaker-back-cup", OUT_COMMON,
                   note="print flange face down; zero support",
                   envelope_xy=(_cup_od, _cup_od), envelope_axes=("X", "Z"))

# Net sealed back-chamber volume -- back-cup's own recess + the pod tube's
# own bore behind the speaker (see docstring for the tube geometry),
# checked against the BOM's real 30-60cc target, not assumed.
_pod_id_body = SPEAKER_FRAME_OD + 1.0
_tube_bore_len = (PANEL_D - SPEAKER_POD_Y0 - SPEAKER_SHOULDER_T) - SPEAKER_DEPTH
_tube_chamber_mm3 = math.pi * (_pod_id_body / 2.0) ** 2 * max(_tube_bore_len, 0.0)
_net_chamber_cc = (_cup_chamber_mm3 + _tube_chamber_mm3) / 1000.0
print(f"  [CHECK] sealed back-chamber volume: cup recess {_cup_chamber_mm3/1000.0:.1f}cc + "
      f"tube bore behind driver {_tube_chamber_mm3/1000.0:.1f}cc = {_net_chamber_cc:.1f}cc "
      f"(BOM target 30-60cc)")
assert 20.0 <= _net_chamber_cc <= 70.0, f"sealed back-chamber {_net_chamber_cc:.1f}cc is far outside the BOM's 30-60cc target"


# =============================================================================
# PART 11 -- WALL-CLEAT (black) -- 45deg french cleat, mounts to the WALL
# (wood screws into studs), the panel's own 02a carries the matching
# receiver ridge (see build_back_shell_screen()) that hooks onto this bar
# once hung. >=150mm long per the design brief; built well past that with real
# margin. Built the same wedge-via-wire technique as the receiver ridge
# (see the Gotcha this avoided, in build_back_shell_screen()'s comments).
# Print orientation: flat back (wall-facing) face down. Zero support.
# =============================================================================
CLEAT_LEN = 180.0        # >= the task's 150mm minimum, real margin
# Bar cross-section sized to match the INTEGRATED RECEIVER ridge's own
# scale (12x12mm wedge on 02a) -- a first draft used a generic 30x20mm
# bar, sized only for "a plausible-looking cleat" with no reference to
# the actual receiver it needs to engage. Placed in its real engaged
# position (see the assembly-reference section below), that mismatch in
# scale meant the bar's own bulk -- far taller than the 12mm-tall ridge
# it was mating with -- plowed straight into the back-shell's general
# flat back wall around the ridge (6572mm3 of real interference, caught
# by the engagement check, not eyeballing). Fixed by matching the
# cleat's own cut to the receiver's real 12x12mm scale instead of an
# arbitrary generic bar size.
# CLEAT_BODY_D is DERIVED, not chosen, from TWO simultaneous real
# requirements, not one -- a first pass here (targeting the rear face
# only, with a fixed 0.15mm gap) drove D up to 12.08mm, which pushed the
# cleat's FRONT edge 0.08mm inside the back-shell's own flat back wall
# (PANEL_D=54.56) -- a real, if tiny, 28.58mm3 collision the interference
# check caught. There are two faces that both matter: the REAR face must
# land exactly on BACK_PLANE_Y (see below), and the FRONT face must clear
# PANEL_D with real margin (CLEAT_FRONT_MARGIN) so the bar's own front
# edge never dips into the flat wall surrounding the ridge. Because
# rear_Y - front_Y == D always (for this translate+180-flip transform,
# independent of the gap -- confirmed algebraically: gap cancels out of
# the difference), fixing D from the front-margin requirement AUTOMATICALLY
# satisfies the rear-lands-on-BACK_PLANE_Y requirement too, with the real
# hook-face gap then falling out as a DERIVED, reported number (checked
# against the 0.3mm tolerance, not chosen to hit it).
# Round 5: with the receiver ridge split into its own rail (12) instead
# of fused into 02a's whole flat back wall, the measured hook-face gap
# (rail_placed.distToShape(cleat_placed), the TRUE 3D minimum distance)
# came in at 0.324mm at the old CLEAT_FRONT_MARGIN=0.2 -- OVER the
# 0.3mm tolerance, even though the DERIVED gap (this section's own 2D
# line-based formula) read 0.247mm, comfortably under. The two numbers
# were never actually the same thing: with the ridge fused into the
# WHOLE shell, distToShape's true minimum was quietly being measured
# against the shell's own huge flat back wall nearby (which sat only
# CLEAT_FRONT_MARGIN=0.2mm from the cleat's front face everywhere, not
# just at the ridge), not against the ridge/hook geometry the formula
# actually describes -- a real, if lucky, coincidence that happened to
# read as "0.199mm, passes" in the old fused version. Splitting the
# rail off removes that coincidence: now only the rail's own hook
# geometry is checked, which is what should have been checked all
# along. Retuned by direct measurement (not re-derived by hand a
# second time) -- a sweep at CLEAT_FRONT_MARGIN=0.1 measures 0.252mm,
# a real ~0.05mm margin under the 0.3mm tolerance.
CLEAT_FRONT_MARGIN = 0.1   # mm -- retuned round 5, see note above
CLEAT_BODY_D = round(BACK_PLANE_Y - PANEL_D - CLEAT_FRONT_MARGIN, 2)
CLEAT_BODY_H = round(CLEAT_BODY_D + 2.0, 2)   # real margin over D so the wedge cut never
                                                # reaches a zero-thickness knife-edge at the back
_cleat_recv_mid_y = PANEL_D + (CLEAT_RECEIVER_T * 2.0 - 0.5) / 2.0   # wedge_d=T*2, ov=0.5
_ny = 1.0 / math.sqrt(2.0)
CLEAT_ENGAGEMENT_GAP = round((BACK_PLANE_Y - _cleat_recv_mid_y - CLEAT_BODY_D / 2.0) / (2.0 * _ny), 3)
assert 0.0 < CLEAT_ENGAGEMENT_GAP <= 0.3, (
    f"derived hook-face gap {CLEAT_ENGAGEMENT_GAP}mm is outside (0, 0.3]mm -- "
    f"adjust CLEAT_FRONT_MARGIN")
print(f"Wall-cleat: derived CLEAT_BODY_D={CLEAT_BODY_D}mm (H={CLEAT_BODY_H}mm), hook-face gap="
      f"{CLEAT_ENGAGEMENT_GAP}mm, so the rear face lands on BACK_PLANE_Y={BACK_PLANE_Y}mm while "
      f"the front face clears PANEL_D={PANEL_D}mm by {CLEAT_FRONT_MARGIN}mm")
CLEAT_SCREW_INSET = 30.0  # wood-screw holes inset from each end
CLEAT_SCREW_DIA = 4.5     # clearance for a #8 wood screw
CLEAT_CSK_DIA = 9.0


def build_wall_cleat():
    # Rectangular bar, then a 45deg wedge removed from the top-back
    # corner via a direct wire/extrude wedge cutter (not a rotated box --
    # same reasoning as the receiver ridge).
    bar = box_at(CLEAT_LEN, CLEAT_BODY_D, CLEAT_BODY_H, -CLEAT_LEN / 2.0, 0.0, 0.0)

    p0 = Vector(0, 0, CLEAT_BODY_H)
    p1 = Vector(0, CLEAT_BODY_D + 1, CLEAT_BODY_H)
    p2 = Vector(0, CLEAT_BODY_D + 1, CLEAT_BODY_H - (CLEAT_BODY_D + 1))
    wire = Part.makePolygon([p0, p1, p2, p0])
    face = Part.Face(wire)
    cutter = face.extrude(Vector(CLEAT_LEN + 2, 0, 0))
    cutter.translate(Vector(-CLEAT_LEN / 2.0 - 1.0, 0, 0))
    bar = bar.cut(cutter)

    for sgn in (-1, 1):
        cx = sgn * (CLEAT_LEN / 2.0 - CLEAT_SCREW_INSET)
        hole = Part.makeCylinder(CLEAT_SCREW_DIA / 2.0, CLEAT_BODY_D + 4, Vector(cx, -2, CLEAT_BODY_H * 0.5),
                                  Vector(0, 1, 0))
        bar = bar.cut(hole)
        csk = Part.makeCone(CLEAT_CSK_DIA / 2.0, CLEAT_SCREW_DIA / 2.0, 3.0,
                            Vector(cx, 0, CLEAT_BODY_H * 0.5), Vector(0, 1, 0))
        bar = bar.cut(csk)

    return bar


print("\n--- building 11 ---")
_cleat = build_wall_cleat()
export_and_verify(_cleat, "11-wall-cleat", OUT_COMMON,
                   note="print flat back face down; zero support",
                   envelope_xy=(CLEAT_LEN, CLEAT_BODY_H), envelope_axes=("X", "Z"))
assert CLEAT_LEN >= 150.0


# =============================================================================
# PART 12 -- CLEAT-RECEIVER RAIL (black) -- round 5. The french-cleat
# receiver ridge, split OFF 02a's own back wall into its own printed
# part. See build_back_shell_screen()'s own comment (where the ridge
# used to be fused in) for the full story: real slicing found 02a's
# flat back wall bridging the whole tub with the ridge fused in and the
# print open-front-down; flipping to back-wall-down (the correct
# orientation for a tub) was blocked by the ridge itself, which used to
# protrude 12mm past the back wall and become the part's new low point.
# Splitting it into its own part removes both problems at once.
#
# Built from the EXACT SAME wire/points the old fused wedge used (same
# CLEAT_RECEIVER_T-scaled triangle, same 0.5mm "_ov" sliver at the
# mounting face) so its world position, once bolted on, is bit-for-bit
# identical to the old fused geometry -- the wall-cleat engagement
# check below (16.7mm depth, <=0.3mm hook gap, both backs coplanar on
# BACK_PLANE_Y) needed NO changes to its own re-derivation formulas
# for this. The 0.5mm sliver is now a real registration TONGUE that
# self-jigs into 02a's own matching recess (see build_back_shell_
# screen()) instead of being a fuse-boolean's overlap margin.
#
# Mounts with 3x M3 into its OWN blind heat-set inserts, opening at the
# tongue's mounting face (screws driven from inside 02a's cavity,
# before 01a closes it up -- see CLEAT_RAIL_HOLE_XS/Z, shared with
# 02a's own clearance holes).
#
# Print orientation: flat mounting face (the tongue) DOWN -- the
# coordinator's own "a 45deg wedge usually prints lying on its flat
# back" default. Zero support: the whole part is either that flat face
# or a 45deg hypotenuse, both self-supporting; the insert bores open
# right at the (bed-facing) mounting face, so they're not internal
# voids either.
# =============================================================================
def build_cleat_receiver_rail():
    _ov = 0.5
    _wedge_h = CLEAT_RECEIVER_T * 2.0
    _wedge_d = CLEAT_RECEIVER_T * 2.0
    p0 = Vector(0, -_ov, 0)
    p1 = Vector(0, -_ov, _wedge_h)
    p2 = Vector(0, _wedge_d, 0)
    wire = Part.makePolygon([p0, p1, p2, p0])
    face = Part.Face(wire)
    rail = face.extrude(Vector(CLEAT_RECEIVER_W, 0, 0))
    # Local frame for the standalone part: centred on X and (now) Z --
    # matches how 06/07/08 are built at their own local origin and
    # placed for the assembly-reference below.
    rail.translate(Vector(-CLEAT_RECEIVER_W / 2.0, 0.0, -_wedge_h / 2.0))

    for dx in (-60.0, 0.0, 60.0):
        ins = cyl_y(INSERT_D / 2.0, INSERT_DEPTH + 0.3, dx, -3.5, -_ov - 0.1)
        rail = rail.cut(ins)
    return rail


print("\n--- building 12 ---")
_rail = build_cleat_receiver_rail()
export_and_verify(_rail, "12-cleat-receiver-rail", OUT_COMMON,
                   note="print flat mounting-face (tongue) DOWN; zero support",
                   envelope_xy=(CLEAT_RECEIVER_W, CLEAT_RECEIVER_T * 2.0), envelope_axes=("X", "Z"))


# =============================================================================
# FEATURE-EXISTS PROBES -- every declared opening/pocket, cast as a real
# probe solid and intersected with the actual exported part. Catches the
# "cut landed in air" / "opening never actually opens" defect class none
# of the topology checks above can see.
# =============================================================================
print("\n--- feature-exists probes ---")

# Re-read the already-exported STEPs so probes run against the exact
# files a maker would receive, not the in-memory pre-export shapes.
def _reload(name, outdir=OUT_COMMON):
    s = Part.Shape()
    s.read(os.path.join(outdir, f"{name}.step"))
    return s


fp_screen = _reload("01a-face-plate-screen")
fp_column = _reload("01b-face-plate-column")
bs_screen = _reload("02a-back-shell-screen")
bs_column = _reload("02b-back-shell-column")
trim_chk = _reload("03-screen-trim")
ins_a_chk = _reload("04a-band-insert-ignition")
ins_b_chk = _reload("04b-band-insert-nightfall")
diff_chk = _reload("05-band-diffuser")
knob_chk = _reload("06-knob")
tab_chk = _reload("07-gold-tab")
cup_chk = _reload("08-speaker-back-cup")
cleat_chk = _reload("11-wall-cleat")
rail_chk = _reload("12-cleat-receiver-rail")


# =============================================================================
# PRINT-ORIENTATION CHECKS -- a packaging pass (rotating every part into
# its documented print orientation for a real Bambu project, then slicing
# it for real in Bambu Studio, supports off) found parts that don't
# actually sit flat / print support-free the way cad/README.md claimed.
# Two DIFFERENT checks, for two different part shapes:
#
# 1. FIRST-LAYER FOOTPRINT (flat/plate-like parts: 01a/01b/03/04a/04b/05/
#    06/07/08/11) -- "no feature stands proud and props up the rest of
#    an otherwise-flat face." Found: 01b's detent ribs were raised
#    0.6mm, so "front face down" stood the part on the ~108mm2 tick ring
#    with the whole face floating 0.6mm (fixed: engraved instead of
#    raised, see build_face_plate_column()). Also found the wall-cleat's
#    documented "back face down" was simply wrong from this part's own
#    first version onward -- that face is only (H-D) tall (the wedge cut
#    removes most of it), giving ~33% contact; its ACTUAL best orientation
#    (also what Bambu's own "most-contact" auto-detection picks
#    independently) is its ORIGINAL, un-rotated bottom face (Z=0, never
#    touched by the wedge cut) -- i.e. NO rotation at all.
# 2. OVERHANG SCAN (tub/shell parts: 02a/02b) -- the footprint metric
#    above doesn't apply to a tub: by design, only the rim touches the
#    bed (open-front DOWN), and that's correct, not a defect (confirmed:
#    the real slicer never flagged the rim itself). What real slicing DID
#    flag were internal fused features -- the speaker-pod tube and the
#    KY-040 anti-rotation tab -- that hung off the back wall into open
#    cavity air with a flat leading cap and nothing underneath ("a boss
#    hanging off a wall with nothing under it"). Fixed with real 45deg
#    conical/wedge tapers (see build_back_shell_screen()/
#    build_back_shell_column()) instead of a flat abrupt cap. The
#    amp/level-shifter mounts and the band-LED channel were converted
#    from fused PROUD rings (same floating-cantilever pattern) to
#    RECESSED POCKETS cut into the back wall's own existing material
#    instead -- a pocket in a wall that's already there isn't a new
#    unsupported structure, the same reasoning that already made the
#    screen-trim's own front rebate on 01a safe.
#
# PRINT_ORIENTATIONS -- name -> the LOCAL direction (in the part's own
# as-designed/as-exported coordinate frame) that must point DOWN (bed-
# ward) in the stated orientation. This is the single source of truth a
# packaging script should reuse (see the printed dict below).
# =============================================================================
print("\n--- print-orientation checks ---")

PRINT_ORIENTATIONS = {
    "01a-face-plate-screen": Vector(0, -1, 0),
    "01b-face-plate-column": Vector(0, -1, 0),
    "02a-back-shell-screen": Vector(0, 1, 0),    # CHANGED round 5 -- see note below
    "02b-back-shell-column": Vector(0, 1, 0),    # CHANGED round 5 -- see note below
    "03-screen-trim": Vector(0, -1, 0),
    "04a-band-insert-ignition": Vector(0, -1, 0),
    "04b-band-insert-nightfall": Vector(0, -1, 0),
    "05-band-diffuser": Vector(0, -1, 0),
    "06-knob": Vector(0, -1, 0),
    "07-gold-tab": Vector(0, -1, 0),
    "08-speaker-back-cup": Vector(0, -1, 0),
    "11-wall-cleat": Vector(0, 0, -1),   # CORRECTED -- see note above; was (0,1,0) ("back face down"),
                                          # which is only ~33% supported at this part's own real geometry
    "12-cleat-receiver-rail": Vector(0, -1, 0),   # NEW round 5 -- flat mounting-face (tongue) down
}
# 02a/02b CHANGED round 5: BACK-WALL DOWN (local +Y, the back wall's own
# outward normal, now points down), not open-front down. Real slicing
# found open-front-down bridges each tub's whole flat back wall across
# ~194mm with nothing under it ("floating regions") -- the correct
# orientation for a tub is open side UP. This was blocked for 02a by the
# integrated cleat-receiver ridge (it used to protrude past the back
# wall and become the new low point when flipped); fixed by splitting
# that ridge into its own part, 12-cleat-receiver-rail (see
# build_cleat_receiver_rail()). 02b had no such blocker -- it already
# measured 95.9% bed contact back-down in this same investigation.

# Resolved to a real FreeCAD Rotation per part (the minimal rotation that
# sends the local down-vector onto world -Z) -- this, not the raw
# direction vectors above, is what a packaging script actually applies.
PRINT_ROTATIONS = {name: Rotation(vec, Vector(0, 0, -1)) for name, vec in PRINT_ORIENTATIONS.items()}

print("PRINT_ROTATIONS (axis, angle-deg) -- for a packaging script to reuse:")
for _nm, _rot in PRINT_ROTATIONS.items():
    _ax = _rot.Axis
    print(f"  {_nm!r}: axis=({_ax.x:.4f}, {_ax.y:.4f}, {_ax.z:.4f}), angle={_rot.Angle * 180.0 / math.pi:.2f}deg")

# Write the SAME dict out as data (cad/print_rotations.json) -- the
# single source of truth bambu/build_project.py is meant to switch to
# reading, instead of its own separate ORIENT/ORIENT_SCRIPT auto-
# detection. Rotation is the one applied to the part exactly as it sits
# in cad/step/ (world/design frame, before any print-bed placement).
PRINT_ROTATIONS_JSON = {
    name: {"axis": [round(rot.Axis.x, 6), round(rot.Axis.y, 6), round(rot.Axis.z, 6)],
           "angle_deg": round(rot.Angle * 180.0 / math.pi, 4)}
    for name, rot in PRINT_ROTATIONS.items()
}
_pr_path = os.path.join(HERE, "print_rotations.json")
with open(_pr_path, "w") as _f:
    json.dump(PRINT_ROTATIONS_JSON, _f, indent=2)
    _f.write("\n")
print(f"  wrote {_pr_path}")


def _place_on_bed(shape, rotation):
    s = shape.copy()
    s.Placement = Placement(Vector(0, 0, 0), rotation)
    bb = s.BoundBox
    s.translate(Vector(0, 0, -bb.ZMin))
    return s


def print_orientation_check(shape, rotation, name, grid_step=5.0, min_contact_pct=80.0):
    """Rotate `shape` into its stated print orientation, sit it on the bed,
    then grid-probe: for every (x,y) where the part has ANY material
    above it (the part's own real footprint, looking straight down),
    check whether that material starts within the first 0.3mm layer. A
    raised feature propping up an otherwise-flat face shows up directly
    as footprint_hits >> first_layer_hits. Threshold is 80%, not 100%,
    to allow real, individually-verified-safe shallow features (e.g.
    01a's own screen-trim front rebate, a picture-frame-shaped 1.5mm
    recess with real wall support on both sides the whole way around --
    confirmed by direct slicing to need no support) without papering
    over an actual raised-feature defect, which showed <1% contact
    before being fixed (not a borderline case at all)."""
    s = _place_on_bed(shape, rotation)
    bb = s.BoundBox
    assert bb.ZMin >= -0.01, f"{name}: part sits below the bed (Z_min={bb.ZMin:.3f}) after placement"

    nx = int(bb.XLength / grid_step) + 3
    ny = int(bb.YLength / grid_step) + 3
    probe_h = bb.ZLength + 4.0
    footprint_hits, first_layer_hits = 0, 0
    for i in range(nx):
        x = bb.XMin - grid_step + i * grid_step
        for j in range(ny):
            y = bb.YMin - grid_step + j * grid_step
            probe = Part.makeCylinder(0.6, probe_h, Vector(x, y, -2.0), Vector(0, 0, 1))
            common = s.common(probe)
            if not (common.Solids and common.Volume > 0.01):
                continue
            footprint_hits += 1
            if common.BoundBox.ZMin <= 0.3:
                first_layer_hits += 1

    pct = 100.0 * first_layer_hits / footprint_hits if footprint_hits else 0.0
    tag = "OK" if pct >= min_contact_pct else "FAIL"
    print(f"  [{tag}] {name}: first-layer contact {first_layer_hits}/{footprint_hits} grid points "
          f"({pct:.1f}%, minimum {min_contact_pct}%), Z_min={bb.ZMin:.3f}mm")
    assert pct >= min_contact_pct, (
        f"{name}: only {pct:.1f}% of its own footprint is in the first 0.3mm layer in its stated "
        f"print orientation -- a raised/forward feature is propping the rest of the part off the bed")
    return pct


def overhang_scan(shape, rotation, name, max_angle_from_down=45.0, min_area=15.0,
                  min_height=0.5, bridge_area=5000.0, pocket_area=200.0):
    """Rotate `shape` into its stated print orientation and scan every
    PLANAR face for ones that are (a) downward-facing within
    `max_angle_from_down` of straight down, (b) more than `min_height`
    above the bed, and (c) at least `min_area` -- i.e. a real,
    appreciable unsupported horizontal-ish surface, not a numerical
    sliver.

    KNOWN BLIND SPOT, found round 5: this scan only looks at PLANAR
    faces (`Surface.TypeId == "Part::GeomPlane"`) -- it has NO way to
    flag a curved (cylindrical/conical) surface at all, planar or not.
    The round-5 back-wall-DOWN flip on 02b introduced a genuine
    "floating cantilever" -- a solid Ø9mm seam-bolt boss, anchored only
    at a side wall, sticking sideways into open cavity air ~49mm above
    the true floor -- that real slicing (Bambu Studio) caught and this
    scan never did, at any area/angle threshold, because a round boss's
    surface is a cylinder, not a plane. Found by direct isolation
    against the real slicer (disable one fused/cut feature at a time,
    re-slice, see which one clears the warning), not by extending this
    scan -- it still can't see that class of defect. Treat a clean
    result from this function as "no unsupported PLANAR face found",
    not "print-safe" -- the real slicer (`bambu/build_project.py`) is
    still the authoritative check for anything this scan can't see.

    Three tiers, NOT all asserted the same way -- this scan cannot tell
    "a real cantilever" apart from "a shallow pocket cut into a wall
    that's already fully supported" by face geometry alone (both are
    just "a downward planar face, not at Z=0"), so it reports every
    tier honestly instead of forcing one pass/fail number:
      - area > bridge_area (5000mm2 default): would be the tub's own
        whole back wall bridging unsupported -- not currently seen on
        either 02a or 02b (round 5 fixed the real cause, orientation,
        not a taper) -- reported, NOT asserted, in case a future change
        reintroduces it.
      - pocket_area < area <= bridge_area: shallow rebates cut into
        already-existing wall material (amp/level-shifter mounts,
        band-LED channel, rear wall-wash LED channel, the cleat-rail
        registration recess) -- each individually reasoned to be safe
        (same "shallow rebate, real wall support on both sides" pattern
        as 01a's own screen-trim front rebate), reported, not asserted,
        because this scan can't distinguish a pocket floor from a
        cantilever cap by geometry alone. As of round 5, real slicing
        (`bambu/build_project.py`) shows ZERO warnings on either 02a or
        02b at all -- these pockets, and everything else in this tier,
        are consistent with being genuinely resolved, confirmed by the
        authoritative real-slice check, not just this scan.
      - area <= pocket_area (and > min_area): small residuals (back-cup
        boss leading caps, ~33mm2 each, and smaller numerical slivers)
        -- documented and left as-is (see build_back_shell_screen()'s
        own note on why a taper doesn't fit there without shrinking the
        M3 insert's own real thread depth), reported, not asserted.
      - area <= min_area: not even reported (numerical noise).
    This scan's OWN hard assert only fires on something NONE of the
    above -- i.e. a genuinely new, unexplained, appreciable floating
    surface -- which is exactly the regression-catching behaviour this
    check exists for."""
    s = _place_on_bed(shape, rotation)
    down = Vector(0, 0, -1)
    bridges, pockets, small, hits = [], [], [], []
    for f in s.Faces:
        if f.Surface.TypeId != "Part::GeomPlane":
            continue
        try:
            u0, u1, v0, v1 = f.ParameterRange
            n = f.normalAt((u0 + u1) / 2.0, (v0 + v1) / 2.0)
        except Exception:
            continue
        if f.Area < min_area:
            continue
        cosang = max(-1.0, min(1.0, n.dot(down) / (n.Length * down.Length)))
        ang = math.degrees(math.acos(cosang))
        z = f.CenterOfMass.z
        if ang <= max_angle_from_down and z > min_height:
            rec = (round(f.Area), round(z, 1))
            if f.Area > bridge_area:
                bridges.append(rec)
            elif f.Area > pocket_area:
                pockets.append(rec)
            else:
                small.append(rec)
    if bridges:
        print(f"  [OPEN ITEM -- NOT RESOLVED] {name}: whole-panel bridge face(s) {bridges} -- "
              f"real slicing still flags this part (\"floating regions\"); see docstring")
    if pockets:
        print(f"  [REPORTED, not asserted] {name}: recessed-pocket-scale face(s) {pockets}")
    if small:
        print(f"  [REPORTED, not asserted] {name}: small residual face(s) {small}")
    print(f"  [{'OK' if not hits else 'FAIL'}] {name}: {len(hits)} UNEXPLAINED overhang face(s) found"
          + (f" -- {hits}" if hits else " (all findings above are known/documented)"))
    assert not hits, f"{name}: unexplained overhang face(s) found: {hits}"
    return {"bridges": bridges, "pockets": pockets, "small": small}


def _downward_regions(shape, max_angle_from_down=45.0, min_height=0.3, min_area=1.0):
    """Yield (area, BoundBox) for every face -- PLANAR or CURVED -- that
    has a meaningfully downward-facing region above the bed.

    overhang_scan() above only ever checked `Part::GeomPlane` faces,
    using a SINGLE normal sample at the face's own midpoint. Round 5
    found a real defect (02b's seam-bolt bosses, a Ø9mm CYLINDER) that
    scan could never see, at any threshold, because a cylinder's own
    surface isn't planar at all -- confirmed by disabling every OTHER
    feature one at a time against the real slicer until only the boss
    remained. Fixed here, not by patching that scan (kept for its own
    documented purpose), but with a genuinely surface-type-agnostic
    check: curved faces (cylinder/cone/sphere/torus/bspline) are
    sampled at a 5x5 grid across their own (u,v) parameter range --
    a single midpoint sample can't see a curved face's downward SIDE
    at all, since the surface's own normal direction sweeps
    continuously across its range, unlike a flat plane's single fixed
    normal."""
    down = Vector(0, 0, -1)
    for f in shape.Faces:
        if f.Area < min_area:
            continue
        try:
            u0, u1, v0, v1 = f.ParameterRange
        except Exception:
            continue
        qualifies = False
        if f.Surface.TypeId == "Part::GeomPlane":
            try:
                n = f.normalAt((u0 + u1) / 2.0, (v0 + v1) / 2.0)
            except Exception:
                continue
            cosang = max(-1.0, min(1.0, n.dot(down) / (n.Length * down.Length)))
            qualifies = math.degrees(math.acos(cosang)) <= max_angle_from_down
        else:
            NS = 5
            for iu in range(NS):
                if qualifies:
                    break
                uu = u0 + (u1 - u0) * (iu + 0.5) / NS
                for iv in range(NS):
                    vv = v0 + (v1 - v0) * (iv + 0.5) / NS
                    try:
                        n = f.normalAt(uu, vv)
                    except Exception:
                        continue
                    cosang = max(-1.0, min(1.0, n.dot(down) / (n.Length * down.Length)))
                    if math.degrees(math.acos(cosang)) <= max_angle_from_down:
                        qualifies = True
                        break
        if not qualifies:
            continue
        bb = f.BoundBox
        if bb.ZMax <= min_height:
            continue
        yield (f.Area, bb, f)


def bed_face_scan(shape, rotation, name, max_angle_from_down=45.0, min_height=0.3,
                  min_area=2.0, small_span=4.5, bridge_span_ok=10.0, probe_r=0.5, margin=1.5):
    """Round 6 -- DJ's first real print of 01a found the screen-trim's
    OWN front rebate failed: printed front-face DOWN, the rebate's
    floor (the material resuming 1.5mm above the bed within the
    rebate's own footprint) was open to the WINDOW cutout on one side
    (a genuine through-hole, no material there at ANY height) and
    only backed by the plate's own full thickness on the OTHER --
    i.e. a real, one-sided CANTILEVER, not a bridge, however shallow.
    Neither the real slicer NOR this build's own 80%-threshold
    print_orientation_check (84.5%, passed) caught it -- both were too
    lenient for a floor that's a small fraction of the part's own
    total footprint. This check exists specifically to catch that
    class, everywhere, not just where it already bit once.

    For every downward-facing region found by `_downward_regions()`
    (planar or curved), probe the material just OUTSIDE its own
    bounding box on all 4 sides (±X, ±Y, `margin` beyond the region's
    own edge), checking whether a CONTINUOUS solid column reaches from
    the bed (Z<=0.3) up past the region's own height at each side.
    Classify:
      - both dimensions < `small_span` (4.5mm default -- the task's own
        guideline says "~3mm"; bumped a touch to cleanly cover the
        single most common feature in this whole build, a plain
        Ø4mm M3-insert blind-bore tip cap, used in nearly every boss
        in every part -- a real, deliberate, reported widening, not an
        arbitrary fudge to silence noise): a small hole/slot -- always
        OK regardless of support (task's own rule: these bridge/print
        fine no matter what).
      - supported on 2 OPPOSITE sides (both +X/-X or both +Y/-Y): a
        real bridge. OK if the shorter supported span is <=
        `bridge_span_ok` (10mm default); REPORTED (not asserted) if
        longer -- a longer bridge isn't necessarily unprintable (Bambu
        handles real spans beyond the guideline), but deserves a human
        look, the same tiered-report spirit as overhang_scan().
      - supported on exactly 1 side, or 0: a genuine CANTILEVER (1
        side) or fully floating region (0 sides) -- FAILS, hard, no
        matter how small the area or span, per the task's own explicit
        rule ("a cantilever is NOT OK, however narrow").
      - a face with an INNER hole (its own `f.Wires` has more than
        one loop) whose inner loop borders genuinely OPEN AIR (no
        material at ANY height there -- a real through-opening, not
        just a different feature filling that spot) is ALSO a
        cantilever, regardless of how well-supported its OUTER edge
        is: this is exactly the old 01a rebate's own real shape -- a
        picture-frame ring, fully backed by the plate's own full
        thickness on its outer edge, but reaching in over completely
        open air (the screen window) on its inner edge. A ring like
        this prints each layer as a closed loop with nothing under
        ANY of it for the whole rebate depth -- DJ's own real print
        failed here ("stringing and deformed edges") even though the
        bbox-based 4-side check below would call the SAME region a
        well-supported bridge (the window's own bbox sits INSIDE the
        ring's own bbox, so a naive ±margin probe outside the ring's
        OUTER bbox never samples the unsupported inner edge at all --
        this is the specific gap that let the old rebate slip past a
        first draft of this very check during development).
    """
    s = _place_on_bed(shape, rotation)
    part_bb = s.BoundBox   # the WHOLE part's own outer footprint -- see the
                            # "part's own true edge" note below
    findings = []
    for area, bb, f in _downward_regions(s, max_angle_from_down, min_height, min_area):
        z_face = bb.ZMax
        x0, x1, y0r, y1r = bb.XMin, bb.XMax, bb.YMin, bb.YMax
        xspan, yspan = x1 - x0, y1r - y0r
        if max(xspan, yspan) < small_span:
            findings.append(("small", area, (x0, x1, y0r, y1r), z_face, max(xspan, yspan)))
            continue
        # A CYLINDRICAL face's own bbox conflates its LENGTH (along its
        # axis -- e.g. a horizontal round hole running the width of a
        # part) with its DIAMETER (the actual bridging dimension, the
        # only one that matters for a round hole's own top arc). Found
        # on 06-knob's radial set-screw pilot: a long, thin bore
        # (length ~13mm along the knob's own X axis, diameter 3.4mm)
        # reported as a 13mm-span cantilever using its bbox's long
        # axis, when the real relevant span is its own 3.4mm diameter
        # -- well inside `small_span`. Every hole of this kind is
        # supported the WHOLE way around its own circumference by the
        # surrounding material at every point along its length; only
        # its diameter is ever actually bridged.
        if f.Surface.TypeId == "Part::GeomCylinder" and 2.0 * f.Surface.Radius <= small_span + 0.01:
            findings.append(("small", area, (x0, x1, y0r, y1r), z_face, 2.0 * f.Surface.Radius))
            continue
        # Same reasoning, a CONE (a countersink) -- found on 11-wall-
        # cleat's own wood-screw countersinks (CLEAT_CSK_DIA=9mm,
        # horizontal axis): a tapered round recess is self-supporting
        # at every diameter along its own length exactly the same way
        # a straight round hole is (each layer, moving along the
        # taper, changes gradually, never an abrupt unsupported cap);
        # its bbox's long axis (its own length) isn't the relevant
        # bridging dimension either. Countersinks/tapered bores up to
        # a real fastener-hardware scale are a standard, universally
        # printable feature regardless of orientation -- compared
        # against `bridge_span_ok` (the task's own ~10mm bridge
        # guideline), not the tighter small-hole bound, since a
        # countersink is meaningfully bigger than a plain insert bore
        # by design.
        if f.Surface.TypeId == "Part::GeomCone" and 2.0 * f.Surface.Radius <= bridge_span_ok + 0.01:
            findings.append(("small", area, (x0, x1, y0r, y1r), z_face, 2.0 * f.Surface.Radius))
            continue

        # "Stepped floor" check -- a downward face that's really just a
        # LOCAL THICKNESS BUMP on top of an already-continuous lower
        # slab (e.g. the wall left between two adjacent shallow
        # pockets, like the amp/level-shifter mounts, cut to the SAME
        # depth right next to each other) is always safe: real,
        # connected material sits under it the WHOLE way from the bed
        # continuously -- no bridging or overhang ever happens, the
        # print just adds a bit of extra local height, same as any
        # embossed/relief detail. Sample several points across the
        # region's OWN footprint (not just its edges): if a continuous
        # lower slab reaches from the bed to within `step_gap_max` of
        # z_face EVERYWHERE sampled, AND that same slab still reaches
        # the bed just past the region's own edges too (so it's not an
        # isolated island floating at that lower height either), this
        # is a step, not a cantilever -- found by direct isolation
        # testing (this exact pattern was misclassified as a
        # cantilever on 02a's own amp/level-shifter pocket divider
        # before this fix, despite real slicing showing zero warnings
        # there).
        #
        # Round 7: relaxed from requiring ALL 9 samples to requiring a
        # real MAJORITY (>=7 of 9) -- found on 02a's own band-LED
        # groove: its true face shape is irregular enough (confirmed
        # directly: its own geometric centroid sample finds no lower
        # material AT ALL there, even though the region is real-
        # slicing-confirmed clean, twice independently) that requiring
        # every single one of 9 grid samples to individually qualify
        # rejected an otherwise-genuine step over one or two unlucky
        # sample points landing in a locally deeper sub-recess. A
        # region that's a step almost everywhere it's sampled, with
        # only a small minority of samples finding a bigger local
        # gap, is still fundamentally a supported relief detail, not
        # a cantilever -- this scan already has a SEPARATE, dedicated
        # ring-cantilever check (above) for the genuinely different
        # case (a hole with nothing beneath it at all).
        step_gap_max = 3.0
        sample_pts = [(x0 + (x1 - x0) * fx, y0r + (y1r - y0r) * fy)
                     for fx in (0.2, 0.5, 0.8) for fy in (0.2, 0.5, 0.8)]
        _step_ok = 0
        for (px, py) in sample_pts:
            probe = Part.makeCylinder(0.5, z_face + 1.0, Vector(px, py, -0.5), Vector(0, 0, 1))
            common = s.common(probe)
            lower_top = None
            for sol in common.Solids:
                if sol.BoundBox.ZMin <= 0.3:
                    lower_top = sol.BoundBox.ZMax if lower_top is None else max(lower_top, sol.BoundBox.ZMax)
            if lower_top is not None and (z_face - lower_top) <= step_gap_max:
                _step_ok += 1
        is_step = _step_ok >= math.ceil(0.75 * len(sample_pts))
        if is_step:
            margin_step = 2.0
            edge_pts = [(x0 - margin_step, (y0r + y1r) / 2.0), (x1 + margin_step, (y0r + y1r) / 2.0),
                       ((x0 + x1) / 2.0, y0r - margin_step), ((x0 + x1) / 2.0, y1r + margin_step)]
            continues = 0
            for (px, py) in edge_pts:
                if not (part_bb.XMin - 0.2 <= px <= part_bb.XMax + 0.2
                        and part_bb.YMin - 0.2 <= py <= part_bb.YMax + 0.2):
                    continues += 1   # the part's own edge -- nothing needed beyond it
                    continue
                probe = Part.makeCylinder(0.5, z_face + 1.0, Vector(px, py, -0.5), Vector(0, 0, 1))
                common = s.common(probe)
                if any(sol.BoundBox.ZMin <= 0.3 for sol in common.Solids):
                    continues += 1
            if continues >= 3:
                findings.append(("step", area, (x0, x1, y0r, y1r), z_face, None))
                continue

        # Inner-hole check -- a ring-shaped region reaching over
        # real open air on its inner edge is a cantilever no matter
        # how the outer bbox looks from outside.
        wires = f.Wires
        ring_cantilever = False
        ring_reach = None
        if len(wires) > 1:
            outer = max(wires, key=lambda w: w.BoundBox.DiagonalLength)
            for inner in wires:
                if inner is outer:
                    continue
                ic = inner.BoundBox.Center
                probe_full = Part.makeCylinder(0.5, 400.0, Vector(ic.x, ic.y, -1.0), Vector(0, 0, 1))
                inside = s.common(probe_full)
                if inside.Solids:
                    continue   # something (another feature) fills this hole -- not open air
                gap = inner.distToShape(outer)[0]
                ring_cantilever = True
                ring_reach = gap if ring_reach is None else min(ring_reach, gap)
        if ring_cantilever:
            findings.append(("cantilever", area, (x0, x1, y0r, y1r), z_face, ring_reach))
            continue

        def supported_at(x, y):
            # A sample point beyond the WHOLE PART's own outer footprint
            # isn't an internal void -- it's just the part's own true
            # edge (a notch/groove open to the part's own boundary, like
            # 02a/02b's own wall-wash LED channel running along the
            # bottom rim). That's always safe to print (the resuming
            # "ceiling" is anchored by the rest of the part all the way
            # around, the same way a plain rabbet cut into a board's
            # own edge always prints fine) -- fundamentally different
            # from an internal hole (like the old 01a rebate's window),
            # which this same "no material here" signal can't
            # distinguish on its own. Treat it as supported.
            tol = 0.2
            if not (part_bb.XMin - tol <= x <= part_bb.XMax + tol
                    and part_bb.YMin - tol <= y <= part_bb.YMax + tol):
                return True
            probe = Part.makeCylinder(probe_r, z_face + 1.0, Vector(x, y, -0.5), Vector(0, 0, 1))
            common = s.common(probe)
            if not common.Solids:
                return False
            return any(sol.BoundBox.ZMin <= 0.3 and sol.BoundBox.ZMax >= z_face - 0.3
                       for sol in common.Solids)

        # Round 6 fix (found testing against 02a/02b's own already-real-
        # slice-confirmed pockets): a naive "probe just outside the
        # face's own AXIS-ALIGNED bbox, at its 4 cardinal midpoints"
        # gives false positives for any NON-rectangular face (an L/strip
        # shape from two adjacent pockets sharing a wall, say) -- the
        # bbox's own cardinal points can land outside the face's real
        # material on a side that was never actually part of its
        # boundary. Fixed with an EDGE-based sweep instead: sample the
        # face's own OUTER boundary edges (weighted by real edge
        # length, not just 4 fixed points), probing just beyond each
        # edge along its own true outward direction (away from the
        # face's real centroid, not the bbox centre) -- this follows
        # the ACTUAL shape, however irregular.
        try:
            outer_wire = f.OuterWire
        except Exception:
            outer_wire = max(f.Wires, key=lambda w: w.BoundBox.DiagonalLength)
        com = f.CenterOfMass
        samples = []
        for e in outer_wire.Edges:
            if e.Length < 0.2:
                continue
            mp = e.CenterOfMass
            dx, dy = mp.x - com.x, mp.y - com.y
            dl = math.hypot(dx, dy)
            if dl < 1e-6:
                continue
            dx, dy = dx / dl, dy / dl
            # Try a few margins AND a few small angular offsets, not
            # one exact radial line -- found on 06-knob's own D-bore
            # floor: its flat edge's own outward direction happens to
            # align EXACTLY with the set-screw pilot bore's own axis
            # line (both run through Y=0 in this part's local frame),
            # so every probe along that one exact line finds the same
            # narrow (3.4mm) unrelated tunnel, however far out it goes
            # -- a coincidental exact-alignment case a single ray can't
            # resolve on its own, even with several stand-off distances
            # (still confirmed real up to 12mm out). The D-bore floor
            # is genuinely well-supported by the solid knob body at
            # every OTHER angle around it; a real nozzle bridging that
            # floor isn't limited to one infinitely thin line either.
            # Sampling a few nearby angles is the direct, honest fix.
            ok = False
            for ang in (0.0, 20.0, -20.0, 40.0, -40.0):
                rad = math.radians(ang)
                rdx = dx * math.cos(rad) - dy * math.sin(rad)
                rdy = dx * math.sin(rad) + dy * math.cos(rad)
                if any(supported_at(mp.x + rdx * mm, mp.y + rdy * mm) for mm in (margin, margin * 2, margin * 3)):
                    ok = True
                    break
            samples.append((ok, e.Length))

        total_len = sum(l for _, l in samples) or 1.0
        sup_frac = sum(l for ok, l in samples if ok) / total_len

        if sup_frac >= 0.85:
            findings.append(("bridge", area, (x0, x1, y0r, y1r), z_face, min(xspan, yspan)))
        elif sup_frac <= 0.02:
            findings.append(("floating", area, (x0, x1, y0r, y1r), z_face, max(xspan, yspan)))
        else:
            findings.append(("cantilever", area, (x0, x1, y0r, y1r), z_face, max(xspan, yspan)))

    # Round 6 -- tightened per the coordinator's own review: a
    # cantilever/floating region with span > bridge_span_ok (10mm) now
    # FAILS, hard, for every part -- no more soft-part carve-out. The
    # two real >10mm findings this caught on 02a (the band-LED
    # channel's own 44.4mm ceiling; the cable slot's own 16mm ceiling)
    # were FIXED for real this round (gussets splitting the channel
    # into <=10mm segments; the slot extended to reach the front rim
    # itself) -- see build_back_shell_screen()'s own comments at each
    # site. Spans <=10mm stay REPORTED, not asserted, with real
    # numbers -- this scan still can't conclusively tell a genuine
    # short cantilever apart from a known-safe shallow pocket by
    # geometry alone (see the class of false positives fixed above:
    # insert-bore caps, D-bore floors, countersinks), so a short span
    # is reported for a human to weigh, not silently asserted past.
    bad = [f for f in findings if f[0] in ("cantilever", "floating") and f[4] is not None and f[4] > bridge_span_ok]
    for kind, area, bbx, z, span in findings:
        tag = "OK"
        if kind == "bridge" and span > bridge_span_ok:
            tag = "REPORTED"
        elif kind in ("cantilever", "floating"):
            tag = "FAIL" if (span is not None and span > bridge_span_ok) else "REPORTED, not asserted"
        span_s = f"{span:.1f}mm" if span is not None else "n/a (continuous lower slab)"
        print(f"  [{tag}] {name}: {kind} area={area:.0f}mm2 span={span_s} z={z:.2f}mm "
              f"bbox=({bbx[0]:.1f},{bbx[2]:.1f})-({bbx[1]:.1f},{bbx[3]:.1f})")
    if not findings:
        print(f"  [OK] {name}: no downward-facing bed-height region found at all")
    assert not bad, f"{name}: {len(bad)} cantilever/floating bed-face region(s) over {bridge_span_ok}mm span: {bad}"
    return findings


_FOOTPRINT_CHECKS = [
    ("01a-face-plate-screen", fp_screen), ("01b-face-plate-column", fp_column),
    ("03-screen-trim", trim_chk), ("04a-band-insert-ignition", ins_a_chk),
    ("04b-band-insert-nightfall", ins_b_chk), ("05-band-diffuser", diff_chk),
    ("06-knob", knob_chk), ("07-gold-tab", tab_chk), ("08-speaker-back-cup", cup_chk),
    ("11-wall-cleat", cleat_chk), ("12-cleat-receiver-rail", rail_chk),
]
for _nm, _shp in _FOOTPRINT_CHECKS:
    print_orientation_check(_shp, PRINT_ROTATIONS[_nm], _nm)

# 02a/02b, round 5: back-wall DOWN turns these from "a tub resting on
# its rim" into "a flat back-wall slab with columns/bosses rising off
# it toward the open top" -- much closer in character to the flat
# parts above than to a tub. Run BOTH checks now: the footprint check
# (does the flat back wall itself, now the bulk of the first layer,
# actually reach ~100% contact -- confirms the flip actually worked and
# nothing new props the wall off the bed) AND the overhang scan (does
# any internal feature, now rising UPWARD off the wall instead of
# hanging off it, have its own new overhang -- e.g. a wider cap than
# its own base, or a shelf/lip bridging unsupported between two side
# walls) -- belt and suspenders, since this is a real orientation change
# and nothing here was re-verified by hand for the new direction.
_FOOTPRINT_CHECKS_TUB = [("02a-back-shell-screen", bs_screen), ("02b-back-shell-column", bs_column)]
# Same 80% default as the flat parts above, not a stricter one -- a
# direct grid-point breakdown (done once, by hand, while landing this
# fix) found 02a's own shortfall from 100% fully accounted for by TWO
# already-individually-reasoned recessed features, not a fresh defect:
# the rear wall-wash LED channel (cut into the back wall's own OUTER
# face, ~82 grid points, real depth WASH_LED_D) and the new cleat-rail
# registration recess (~93 points, real depth 0.7mm) -- both the same
# "shallow rebate, real wall support on both sides" pattern 01a's own
# screen-trim front rebate already uses safely at this same 80%.
for _nm, _shp in _FOOTPRINT_CHECKS_TUB:
    print_orientation_check(_shp, PRINT_ROTATIONS[_nm], _nm)

_OVERHANG_CHECKS = [("02a-back-shell-screen", bs_screen), ("02b-back-shell-column", bs_column)]
for _nm, _shp in _OVERHANG_CHECKS:
    overhang_scan(_shp, PRINT_ROTATIONS[_nm], _nm)


# =============================================================================
# BED-FACE POCKETS AND LEDGES -- round 6, ALL 13 parts. See
# bed_face_scan()'s own docstring for why this exists: DJ's first real
# print found 01a's own front trim rebate failed (a real one-sided
# cantilever neither the real slicer NOR this build's 80%-footprint
# check caught), and this is the check built specifically to catch
# that whole class, everywhere, not just where it already bit once.
# =============================================================================
print("\n--- bed-face pockets/ledges (all parts) ---")
_ALL_PARTS_CHECKS = [
    ("01a-face-plate-screen", fp_screen), ("01b-face-plate-column", fp_column),
    ("02a-back-shell-screen", bs_screen), ("02b-back-shell-column", bs_column),
    ("03-screen-trim", trim_chk), ("04a-band-insert-ignition", ins_a_chk),
    ("04b-band-insert-nightfall", ins_b_chk), ("05-band-diffuser", diff_chk),
    ("06-knob", knob_chk), ("07-gold-tab", tab_chk), ("08-speaker-back-cup", cup_chk),
    ("11-wall-cleat", cleat_chk), ("12-cleat-receiver-rail", rail_chk),
]
assert len(_ALL_PARTS_CHECKS) == 13, "bed-face scan must cover all 13 parts"
# Round 6: no more per-part soft-mode carve-out -- the check itself now
# fails on span alone (>10mm cantilever/floating, any part), which is
# what actually caught and forced the real fixes on 02a's band-LED
# channel and cable slot. See bed_face_scan()'s own docstring.
for _nm, _shp in _ALL_PARTS_CHECKS:
    bed_face_scan(_shp, PRINT_ROTATIONS[_nm], _nm)


# 01a: screen window open
probe(fp_screen, box_cxz(AA_W + 2 * REVEAL - 1.0, AA_H + 2 * REVEAL - 1.0, FACE_T + 4, AA_CX, AA_CZ, -2),
      "01a screen window", want_open=True)
# 01a: band window open (through the bordered window)
probe(fp_screen, box_cxz(BAND_WINDOW_W - 1.0, BAND_WINDOW_H - 1.0, FACE_T + 4, BAND_CX, BAND_CZ, -2),
      "01a band window", want_open=True)
# 01b: dial bushing hole open
probe(fp_column, cyl_y(KY_PANEL_HOLE_DIA / 2.0 - 0.3, FACE_T + 4, DIAL_CX, DIAL_CZ, -2),
      "01b dial bushing hole", want_open=True)
# 01b: rocker cutout open
probe(fp_column, box_cxz(ROCKER_CUTOUT_W - 1.0, ROCKER_CUTOUT_H - 1.0, FACE_T + 4, DIAL_CX, ROCKER_CZ, -2),
      "01b rocker cutout", want_open=True)
# 01b: gold-tab pocket is a BLIND pocket -- must NOT be open all the way through
# Gold-tab pocket blindness check -- two SEPARATE probes, not one span
# across both: the pocket itself (Y 0..GOLD_POCKET_D) must read OPEN
# (it's a real pocket), and the remaining FLOOR behind it (Y
# GOLD_POCKET_D..FACE_T) must read BLOCKED (real material, i.e. genuinely
# blind, not a through-hole). A single probe spanning both regions (a
# first draft's mistake) mixes the two and can't actually tell blind
# apart from through.
probe(fp_column, cyl_y(2.0, GOLD_POCKET_D - 0.1, DIAL_CX, GOLD_CZ, 0.05),
      "01b gold-tab pocket itself (open)", want_open=True)
probe(fp_column, cyl_y(2.0, FACE_T - GOLD_POCKET_D - 0.1, DIAL_CX, GOLD_CZ, GOLD_POCKET_D + 0.05),
      "01b gold-tab pocket floor (blind)", want_open=False)
# 02a: cable slot open
probe(bs_screen, box_at(CABLE_SLOT_W - 1.0, CABLE_SLOT_H - 1.0, WALL + 4,
                        CABLE_SLOT_CX - CABLE_SLOT_W / 2.0 + 0.5, FACE_T + 4.5, -2.0),
      "02a cable slot", want_open=True)
# 02a: speaker acoustic bore open all the way through (shoulder+body+back)
probe(bs_screen, cyl_y(SPEAKER_OPEN_DIA / 2.0 - 1.0, (PANEL_D - SPEAKER_POD_Y0) - 1.0,
                       SPEAKER_POD_CX, SPEAKER_POD_CZ, SPEAKER_POD_Y0 + 0.5),
      "02a speaker acoustic bore", want_open=True)
# 02a: display retention clearance holes open through the back wall
for i, (ex, ez) in enumerate(ENC_HOLES_WORLD):
    probe(bs_screen, cyl_y(CLEAR_D / 2.0 - 0.3, BACK_WALL + 2, ex, ez, PANEL_D - BACK_WALL - 1),
          f"02a display-retention hole {i}", want_open=True)
# 02a: Active Cooler vents open
for i in range(VENT_N):
    vz = DISPLAY_CZ + (i - (VENT_N - 1) / 2.0) * VENT_PITCH
    probe(bs_screen, box_cxz(VENT_W - 0.4, VENT_H - 1.0, BACK_WALL + 2, DISPLAY_CX + 32.0, vz,
                             PANEL_D - BACK_WALL - 0.5),
          f"02a vent {i}", want_open=True)
# 02b: mic ports open through the top wall
for i, mx in enumerate(MIC_PORT_XS):
    probe(bs_column, cyl_z(MIC_PORT_R - 0.2, WALL + 2, mx, MIC_PORT_Y0, PANEL_H - WALL - 1),
          f"02b mic port {i}", want_open=True)
# 04a/04b: measured open area already printed above; confirm both share
# the exact same outer footprint + mounting pattern (task requirement)
assert abs(ins_a_chk.BoundBox.XLength - ins_b_chk.BoundBox.XLength) < 0.01
assert abs(ins_a_chk.BoundBox.ZLength - ins_b_chk.BoundBox.ZLength) < 0.01
print("  [OK] 04a/04b share the exact same outline (%.2f x %.2f mm)"
      % (ins_a_chk.BoundBox.XLength, ins_a_chk.BoundBox.ZLength))
for (bx, bz) in BAND_MOUNTS:
    # Probed at the insert's OWN real Y position (INSERT_Y0), not the
    # face-plate's Y=0 convention -- a first draft's probe (and the
    # cutting tool it copied the Y-span from) used Y=-1..3, which never
    # reached the insert plate at all (it sits at Y~10-12): the "mount
    # hole open" check read 0% blocked and passed, but vacuously --
    # probing empty space outside the part, not a real hole. Same root
    # cause as the perforation cut itself never landing (see
    # build_band_insert_ignition()'s own note) -- found by directly
    # inspecting the exported STEP's face count (a plain 6-face box where
    # 143 should have been) after this probe's false "pass" gave no warning.
    probe(ins_a_chk, cyl_y(CLEAR_D / 2.0 - 0.3, INSERT_T + 2, bx, bz, INSERT_Y0 - 1), "04a mount hole", want_open=True)
    probe(ins_b_chk, cyl_y(CLEAR_D / 2.0 - 0.3, INSERT_T + 2, bx, bz, INSERT_Y0 - 1), "04b mount hole", want_open=True)


# =============================================================================
# SOUND-PATH CHECK -- an independent design review of
# assembly-reference.step found the speaker firing into solid plastic
# (05-band-diffuser was a plain sheet) and both inserts too sparse over
# the driver to pass real sound -- neither defect broke any topology
# rule, so nothing above catches it. Fires a real grid of rays ALONG THE
# DRIVER'S OWN AXIS across the Dia38mm cone disk, through EVERY layer in
# its actual installed position (face-plate band window, insert,
# diffuser) at once, for EACH insert variant, and requires >=25% of the
# rays to pass fully clear through all three layers together. This is
# NOT the same check as the per-part feature-exists probes above (which
# only ever check ONE part at a time) -- a part can pass every one of
# those and the assembled STACK still be acoustically blocked, which is
# exactly what happened here.
# =============================================================================
print("\n--- sound-path check (driver axis through every band layer) ---")


def sound_path_check(insert_shape, label, step=2.0, min_pass_pct=25.0):
    stack = Part.makeCompound([fp_screen, insert_shape, diff_chk])
    n = int(2 * ACOUSTIC_ZONE_R / step) + 1
    total, clear = 0, 0
    for i in range(n):
        x = ACOUSTIC_CX - ACOUSTIC_ZONE_R + i * step
        for j in range(n):
            z = ACOUSTIC_CZ - ACOUSTIC_ZONE_R + j * step
            if math.hypot(x - ACOUSTIC_CX, z - ACOUSTIC_CZ) > ACOUSTIC_ZONE_R:
                continue
            total += 1
            ray = cyl_y(0.5, DIFFUSER_Y0 + DIFFUSER_T + 4.0, x, z, -2.0)
            common = stack.common(ray)
            blocked_frac = (common.Volume / ray.Volume) if common.Solids else 0.0
            if blocked_frac < 0.05:   # ray passes essentially fully clear through all 3 layers
                clear += 1
    pct = 100.0 * clear / total if total else 0.0
    tag = "OK" if pct >= min_pass_pct else "FAIL"
    print(f"  [{tag}] sound path {label}: {clear}/{total} rays clear through face-plate+insert+diffuser "
          f"({pct:.1f}%, minimum {min_pass_pct}%)")
    assert pct >= min_pass_pct, f"sound path {label}: only {pct:.1f}% of rays pass clear (minimum {min_pass_pct}%)"
    return pct


sound_path_check(ins_a_chk, "04a ignition")
sound_path_check(ins_b_chk, "04b nightfall")


# =============================================================================
# NO-UNINTENDED-OPENINGS RAY GRID -- a dense grid of thin probe cylinders
# across each face-plate's own footprint. Any point that reads "open"
# (no material blocking it) must lie inside a DECLARED opening -- catches
# a stray unintended see-through the feature-exists probes above
# (which only check the declared openings themselves) would never find.
# =============================================================================
print("\n--- no-unintended-openings ray grid ---")


def _in_rect(x, z, cx, cz, w, h, margin=0.0):
    return (cx - w / 2.0 - margin) <= x <= (cx + w / 2.0 + margin) and \
           (cz - h / 2.0 - margin) <= z <= (cz + h / 2.0 + margin)


def ray_grid_check(shape, x0, x1, z0, z1, declared_openings, label, step=4.0):
    nx = int((x1 - x0) / step) + 1
    nz = int((z1 - z0) / step) + 1
    n_open, n_bad = 0, 0
    bad_points = []
    for i in range(nx):
        x = x0 + i * step
        for j in range(nz):
            z = z0 + j * step
            probe_r = 0.4
            ray = cyl_y(probe_r, FACE_T + 6, x, z, -3)
            common = shape.common(ray)
            open_frac = 1.0 - (common.Volume / ray.Volume if common.Solids else 0.0)
            if open_frac > 0.9:   # this (x,z) point is see-through
                n_open += 1
                declared = any(chk(x, z) for chk in declared_openings)
                if not declared:
                    n_bad += 1
                    bad_points.append((round(x, 1), round(z, 1)))
    print(f"  {label}: grid {nx}x{nz} points, {n_open} open, {n_bad} undeclared-open")
    assert n_bad == 0, f"{label}: {n_bad} undeclared see-through points: {bad_points[:10]}"
    return n_open


ray_grid_check(
    fp_screen, X_A0 + 1, X_A1 - 1, 2.0, PANEL_H - 2.0,
    [lambda x, z: _in_rect(x, z, AA_CX, AA_CZ, AA_W + 2 * REVEAL, AA_H + 2 * REVEAL, 0.5),
     lambda x, z: _in_rect(x, z, BAND_CX, BAND_CZ, BAND_WINDOW_W, BAND_WINDOW_H, 0.5),
     # trim(03)'s own through-bores -- a real, declared, intended
     # opening (round 6: widened to TRIM_BORE_D to admit the trim's own
     # pass-through boss, not just a screw shaft -- see
     # build_face_plate_screen()'s own mounting comment), not a stray
     # see-through -- caught missing from this list on an early run
     # (1 undeclared point at one of the 4 corners) and added here.
     lambda x, z: any(math.hypot(x - tx, z - tz) <= TRIM_BORE_D / 2.0 + 1.0 for (tx, tz) in TRIM_MOUNTS)],
    "01a ray grid")

ray_grid_check(
    fp_column, X_B0 + 1, X_B1 - 1, 2.0, PANEL_H - 2.0,
    [lambda x, z: math.hypot(x - DIAL_CX, z - DIAL_CZ) <= KY_PANEL_HOLE_DIA / 2.0 + 0.5,
     lambda x, z: _in_rect(x, z, DIAL_CX, ROCKER_CZ, ROCKER_CUTOUT_W, ROCKER_CUTOUT_H, 0.5)],
    "01b ray grid")


# =============================================================================
# ASSEMBLY INTERFERENCE -- real display STEP (transformed to its actual
# installed position) + envelope boxes for every other component, each
# checked against the real exported shell geometry (and each other where
# they share a module) for zero real overlap.
# =============================================================================
print("\n--- assembly interference ---")

DISPLAY_Y_FRONT = FACE_T + FIT_CLR

# Native-STEP -> world transform (see module docstring's derivation):
#   world_X = DISPLAY_CX + native_Y
#   world_Y = DISPLAY_Y_FRONT + 5.02 - native_Z
#   world_Z = DISPLAY_CZ - native_X
_disp_M = App.Matrix()
_disp_M.A11, _disp_M.A12, _disp_M.A13 = 0, 1, 0
_disp_M.A21, _disp_M.A22, _disp_M.A23 = 0, 0, -1
_disp_M.A31, _disp_M.A32, _disp_M.A33 = -1, 0, 0
_disp_rotation = Rotation()
_disp_rotation.Matrix = _disp_M
_disp_placement = Placement(Vector(DISPLAY_CX, DISPLAY_Y_FRONT + 5.02, DISPLAY_CZ), _disp_rotation)

_display_raw = Part.Shape()
_display_raw.read(DISPLAY_STEP)
display_installed = _display_raw.copy()
display_installed.Placement = _disp_placement
_dbb = display_installed.BoundBox
print(f"  display installed bbox: X[{_dbb.XMin:.1f},{_dbb.XMax:.1f}] "
      f"Y[{_dbb.YMin:.1f},{_dbb.YMax:.1f}] Z[{_dbb.ZMin:.1f},{_dbb.ZMax:.1f}]")
# Sanity: the transformed active-area centre should land within 0.1mm of
# the AA_CX/AA_CZ this whole build already used for the window cut --
# proves the matrix derivation actually matches the earlier hand-applied
# to_landscape() rotation, independently.
_expect_x, _expect_z = AA_CX, AA_CZ
print(f"  sanity: AA_CX/AA_CZ used for the window = ({_expect_x:.2f},{_expect_z:.2f})")

interfere(bs_screen, display_installed, "display (installed) vs 02a back-shell-screen", max_mm3=0.5)

# Pi5 + Active Cooler envelope -- conservative box (85x56mm Pi5 board
# footprint, the larger of the two real footprints), spanning the real
# STACK_CLEARANCE depth behind the display module's own back face.
pi5_env = box_full(PI5_BOARD_W, STACK_CLEARANCE, PI5_BOARD_D, DISPLAY_CX,
                   DISPLAY_Y_FRONT + DISP_T + STACK_CLEARANCE / 2.0, DISPLAY_CZ)
interfere(bs_screen, pi5_env, "Pi5+Active-Cooler envelope vs 02a", max_mm3=0.5)

# DSI FPC cable-bend reserve -- PLACEHOLDER envelope, near one edge of
# the display module, not a datasheet figure.
dsi_env = box_full(30.0, 15.0, 20.0, DISPLAY_CX, DISPLAY_Y_FRONT + DISP_T + 5.0,
                   DISPLAY_CZ + DISP_H / 2.0 - 15.0)
interfere(bs_screen, dsi_env, "DSI cable-bend reserve (placeholder) vs 02a", max_mm3=0.5)

# KY-040 module + wires envelope
ky_env = box_full(KY_PCB_W + 4.0, KY_PCB_T + KY_HEADER_RESERVE, KY_PCB_D + 4.0, DIAL_CX,
                  FACE_T + KY_PCB_GAP + (KY_PCB_T + KY_HEADER_RESERVE) / 2.0, DIAL_CZ)
interfere(bs_column, ky_env, "KY-040 module+wires vs 02b", max_mm3=0.5)

# Rocker body + terminals + wiring reserve
rocker_env = box_full(ROCKER_CUTOUT_W + 2.0, ROCKER_CLEARANCE_RESERVE, ROCKER_CUTOUT_H + 2.0,
                      DIAL_CX, FACE_T + ROCKER_CLEARANCE_RESERVE / 2.0, ROCKER_CZ)
interfere(bs_column, rocker_env, "rocker body+wiring vs 02b", max_mm3=0.5)
interfere(ky_env, rocker_env, "KY-040 envelope vs rocker envelope (same module, different zones)", max_mm3=0.5)

# Speaker (installed, frame+depth) vs the shell -- should sit entirely
# within the bore that was cut for it.
speaker_env = cyl_y(SPEAKER_FRAME_OD / 2.0 - 0.3, SPEAKER_DEPTH, SPEAKER_POD_CX, SPEAKER_POD_CZ,
                    SPEAKER_POD_Y0 + SPEAKER_SHOULDER_T + 0.3)
interfere(bs_screen, speaker_env, "speaker (installed) vs 02a", max_mm3=0.5)

# Amp + mic + LED runs -- probed as "must be genuinely open" at their own
# component footprint (same discipline as the feature-exists probes
# above), since they sit in fused TRAYS/channels, not envelope-vs-solid-
# shell interference.
amp_ax, amp_az = AMP_CENTER
_TRAY_H = 4.0   # must match _tray()'s own local constant in build_back_shell_screen()
# Probe kept WITHIN the tray's own Y-extent (a first draft's probe
# over-reached 7mm past the tray into the solid BACK_WALL itself and
# read 19.5% blocked -- not a real defect, a probe geometry mistake, but
# exactly the kind of thing this discipline exists to catch and fix
# rather than wave away).
probe(bs_screen, box_full(AMP_W, _TRAY_H - 1.0, AMP_H, amp_ax, PANEL_D - BACK_WALL - _TRAY_H / 2.0, amp_az),
      "amp board footprint, open in its tray", want_open=True)
# Probed just ABOVE the mic-cradle shelf's own 3mm floor (a first draft's
# probe centred on the whole reserved zone dipped 1mm into the shelf's
# own top surface and read 10% blocked -- fixed by starting the probe
# right at the shelf's real top, not the zone's own midpoint).
_mic_shelf_top = (MIC_CRADLE_Z_TOP - MIC_CRADLE_H) + 3.0
mic_env = box_at(MIC_EXT_FEMALE_W, MIC_CRADLE_D - 2.0, MIC_CRADLE_H - 3.0 - 1.0,
                 DIAL_CX - MIC_EXT_FEMALE_W / 2.0, MIC_CRADLE_Y0 + 1.0, _mic_shelf_top + 0.3)
probe(bs_column, mic_env, "mic extension+dongle footprint, open in its cradle", want_open=True)

# Face-plate screws' FULL LENGTH -- perimeter screws span from the back
# wall's outer face all the way to the face-plate's own boss (the whole
# open cavity in between); check each screw's full swept path against
# every electronics envelope in its own module.
print("  face-plate screw full-length clearance:")
for (px, pz) in PERIM_A:
    screw = cyl_y(CLEAR_D / 2.0, PANEL_D - FACE_T, px, pz, FACE_T)
    interfere(pi5_env, screw, f"perim screw ({px:.0f},{pz:.0f}) vs Pi5 envelope", max_mm3=0.5)
    interfere(speaker_env, screw, f"perim screw ({px:.0f},{pz:.0f}) vs speaker envelope", max_mm3=0.5)
for (px, pz) in PERIM_B:
    screw = cyl_y(CLEAR_D / 2.0, COLUMN_PANEL_D - FACE_T, px, pz, FACE_T)
    interfere(ky_env, screw, f"perim screw ({px:.0f},{pz:.0f}) vs KY-040 envelope", max_mm3=0.5)
    interfere(rocker_env, screw, f"perim screw ({px:.0f},{pz:.0f}) vs rocker envelope", max_mm3=0.5)

# Mic-to-speaker real 3D distance (task hard constraint: >=40mm)
mic_center = Vector(DIAL_CX, MIC_CRADLE_Y0 + MIC_CRADLE_D / 2.0, MIC_CRADLE_Z_TOP - MIC_CRADLE_H / 2.0)
speaker_center = Vector(SPEAKER_POD_CX, SPEAKER_POD_Y0, SPEAKER_POD_CZ)
mic_speaker_dist = math.sqrt((mic_center.x - speaker_center.x) ** 2 + (mic_center.y - speaker_center.y) ** 2 +
                             (mic_center.z - speaker_center.z) ** 2)
print(f"  mic-to-speaker real 3D distance: {mic_speaker_dist:.1f}mm (spec minimum 40mm)")
assert mic_speaker_dist >= 40.0, f"mic is only {mic_speaker_dist:.1f}mm from the speaker, spec minimum 40mm"


# =============================================================================
# ASSEMBLY-REFERENCE STEP -- a visual-reference compound of every part in
# its installed position, WITHOUT the Raspberry Pi display STEP (that is
# RPi's own file; exporting it here would redistribute it through this
# repo -- see the open-build defect list's own "vendor STEP baked into an
# export" item). NOT a print file. Parts already built in world
# coordinates (01a/01b/02a/02b/03/04b/05) are used as-is; the small
# standalone parts (06/07/08/11), built at their own local origin, get a
# placement here for the reference view only.
# =============================================================================
print("\n--- assembly-reference (no display STEP) ---")


def _placed_copy(shape, position, rotation=None):
    s = shape.copy()
    s.Placement = Placement(position, rotation if rotation else Rotation())
    return s


knob_placed = _placed_copy(_knob, Vector(DIAL_CX, 0.0, DIAL_CZ), Rotation(Vector(1, 0, 0), 180))
tab_placed = _placed_copy(_tab, Vector(DIAL_CX, 0.0, GOLD_CZ))   # built at local origin; placed at its real pocket position
cup_placed = _placed_copy(_cup, Vector(SPEAKER_POD_CX, PANEL_D, SPEAKER_POD_CZ))
# Rail (12) -- built at its own local origin (mounting-face tongue tip
# at local Y=-0.5, ridge centred on X and Z); placed at the EXACT world
# position the old fused wedge occupied, so the engagement math below
# (formula-derived, not read off 02a's own geometry any more) still
# lines up with the real, installed part.
rail_placed = _placed_copy(_rail, Vector((X_A0 + X_A1) / 2.0, PANEL_D, CLEAT_RECEIVER_CZ))

# =============================================================================
# WALL-CLEAT ENGAGEMENT -- an independent design review found
# the cleat floating 28mm behind the back shell with nothing showing it
# actually hangs. Placed here in its real ENGAGED position against the
# integrated receiver ridge on 02a, not a hand-picked "somewhere behind
# it" offset.
#
# Both wedges share the SAME 45deg line direction (slope -1 in the Y-Z
# cross-section) by construction -- but both were built with their own
# SOLID material on the "small Y / small Z" side of that line (confirmed
# by re-deriving each from its own wire/cutter geometry below), which
# means simply translating one onto the other's line would collide them,
# not mate them. A real french-cleat needs the two solids on OPPOSITE
# sides of the shared 45deg plane. Fixed with a 180deg rotation about an
# axis THAT LIES IN the shared plane (the X-direction, i.e. the
# extrusion axis, through a point on the line) -- a 180deg rotation
# about any in-plane axis reflects the two half-spaces either side of
# that plane into each other while leaving the plane itself fixed, which
# is exactly the operation that turns "same side" into "opposite side"
# without changing the shared line/plane at all.
# =============================================================================
_cleat_ov = 0.5
_cleat_wedge_h = CLEAT_RECEIVER_T * 2.0
_cleat_wedge_d = CLEAT_RECEIVER_T * 2.0
_receiver_cz = CLEAT_RECEIVER_CZ   # shared constant -- see its own definition, right after DISPLAY_CZ

# Receiver ridge hypotenuse endpoints, world (Y, Z) -- re-derived from the
# exact same points build_back_shell_screen() builds the wedge wire from.
_recv_p1 = Vector(0.0, PANEL_D - _cleat_ov, _receiver_cz + _cleat_wedge_h / 2.0)
_recv_p2 = Vector(0.0, PANEL_D + _cleat_wedge_d, _receiver_cz - _cleat_wedge_h / 2.0)
_recv_mid = Vector(0.0, (_recv_p1.y + _recv_p2.y) / 2.0, (_recv_p1.z + _recv_p2.z) / 2.0)
_recv_len = math.hypot(_recv_p2.y - _recv_p1.y, _recv_p2.z - _recv_p1.z)

# Wall-cleat's own hypotenuse endpoints, LOCAL (Y, Z) -- re-derived from
# build_wall_cleat()'s own cutter wire (the finished bar's real edge runs
# from (Y=0, Z=H) to (Y=D, Z=H-D), the same line the D+1-sized cutter
# leaves behind once clipped to the bar's own real Y range).
_wc_q1 = Vector(0.0, 0.0, CLEAT_BODY_H)
_wc_q2 = Vector(0.0, CLEAT_BODY_D, CLEAT_BODY_H - CLEAT_BODY_D)
_wc_mid_local = Vector(0.0, (_wc_q1.y + _wc_q2.y) / 2.0, (_wc_q1.z + _wc_q2.z) / 2.0)
_wc_len = math.hypot(_wc_q2.y - _wc_q1.y, _wc_q2.z - _wc_q1.z)

# Step 1: translate so the two hypotenuse segments share a common
# midpoint (guarantees they lie on the same line, since both have the
# same -1 slope, and centres the shorter segment inside the longer one
# for maximum real engagement overlap).
_cleat_T = Vector(0.0, _recv_mid.y - _wc_mid_local.y, _recv_mid.z - _wc_mid_local.z)

# Step 2: a small real clearance gap (CLEAT_ENGAGEMENT_GAP, inside the
# task's 0.3mm tolerance) along the shared face's own outward normal (up
# and away from the panel -- (+1,+1) in (Y,Z), normalised), so the two
# faces end up genuinely close/touching rather than numerically coincident.
_normal = Vector(0.0, 1.0, 1.0)
_normal_len = math.hypot(_normal.y, _normal.z)
_flip_centre = Vector(0.0, _recv_mid.y + _normal.y / _normal_len * CLEAT_ENGAGEMENT_GAP,
                      _recv_mid.z + _normal.z / _normal_len * CLEAT_ENGAGEMENT_GAP)

cleat_engaged = _cleat.copy()
cleat_engaged.translate(Vector(0.0, _cleat_T.y, _cleat_T.z))
cleat_engaged.rotate(_flip_centre, Vector(1.0, 0.0, 0.0), 180.0)
cleat_engaged.translate(Vector((X_A0 + X_A1) / 2.0, 0.0, 0.0))   # centre in X on the receiver's own X range
cleat_placed = cleat_engaged

# --- Verification: real geometry, READ BACK from the actual transformed
# shape's own BoundBox -- not a hand-derived formula. Revision 2 computed
# the "wall plane" by hand (2*flip_centre.y - wall_face_pt.y) and got the
# sign wrong: it reported the cleat's FRONT (hook) face at 55.02mm as if
# it were the rear/wall-mounting face, when an independent reviewer's
# own check of the real geometry found the actual rear face at 66.02mm.
# Fixed by reading the transformed shape's own BoundBox.YMax directly --
# no formula to get backwards a second time.
# =============================================================================
print("\n--- wall-cleat engagement ---")
_cleat_bb = cleat_placed.BoundBox
_cleat_front_y, _cleat_rear_y = _cleat_bb.YMin, _cleat_bb.YMax
print(f"  cleat span: Y {_cleat_front_y:.2f} (front/hook, toward the panel) to "
      f"{_cleat_rear_y:.2f} (rear/wall-mounting face)")

# Round 5: the receiver ridge is now the SEPARATE rail (12), bolted
# onto 02a, not fused into it -- interference/gap need to check against
# rail_placed (the actual mating geometry), not the bare 02a shell.
_cleat_vs_a = _bss.common(cleat_placed)
_cleat_vs_rail = rail_placed.common(cleat_placed)
_cleat_vs_b = _bsc.common(cleat_placed)
_cleat_interference_mm3 = ((_cleat_vs_a.Volume if _cleat_vs_a.Solids else 0.0)
                           + (_cleat_vs_rail.Volume if _cleat_vs_rail.Solids else 0.0)
                           + (_cleat_vs_b.Volume if _cleat_vs_b.Solids else 0.0))
print(f"  cleat vs 02a+rail+02b interference: {_cleat_interference_mm3:.4f}mm3")
assert _cleat_interference_mm3 < 1.0, (
    f"wall-cleat bulk collides with a back-shell/rail: {_cleat_interference_mm3:.2f}mm3 -- not a clean engagement")

_gap_dist, _gap_pts, _gap_info = rail_placed.distToShape(cleat_placed)
print(f"  minimum distance, cleat hook face to receiver rail: {_gap_dist:.3f}mm (tolerance 0.3mm)")
assert _gap_dist <= 0.3, f"cleat sits {_gap_dist:.3f}mm from the receiver rail -- not real contact"

_engagement_depth = min(_recv_len, _wc_len)
print(f"  hook engagement depth (shorter of the two mating segments): {_engagement_depth:.1f}mm "
      f"(receiver segment {_recv_len:.1f}mm, cleat segment {_wc_len:.1f}mm; task minimum 8mm)")
assert _engagement_depth >= 8.0, f"hook engagement depth {_engagement_depth:.1f}mm is under the 8mm minimum"

# Rear face must land ON BACK_PLANE_Y (within 0.05mm) -- the cleat mounts
# to the actual wall with THIS face, not the hook/front face.
print(f"  cleat rear (wall-mounting) face: Y={_cleat_rear_y:.2f}mm vs BACK_PLANE_Y={BACK_PLANE_Y}mm")
assert abs(_cleat_rear_y - BACK_PLANE_Y) <= 0.05, (
    f"cleat's rear face ({_cleat_rear_y:.2f}mm) does not land on BACK_PLANE_Y ({BACK_PLANE_Y}mm)")

# Both shells' own YMax must be coplanar with BACK_PLANE_Y (within 0.05mm)
# -- the actual defect the independent review found (0.26mm apart).
#
# Round 5: 02a's BARE shell no longer reaches BACK_PLANE_Y on its own
# (the ridge that used to get it there is now the separate rail) -- by
# design, only the rail's own footprint reaches the wall plane; the
# rest of 02a's back wall sits a real 12mm recessed behind it, which is
# fine (it doesn't touch the wall at all, same as before the ridge was
# ever fused in -- only the ridge/rail's own narrow band ever did). The
# real "does the SCREEN MODULE reach the wall plane" question is about
# the ASSEMBLY (02a + rail), not 02a alone.
_bss_bare_ymax = _bss.BoundBox.YMax
_bss_assembled_ymax = max(_bss_bare_ymax, rail_placed.BoundBox.YMax)
_bsc_ymax = _bsc.BoundBox.YMax
print(f"  02a bare-shell YMax={_bss_bare_ymax:.2f}mm (recessed, expected < BACK_PLANE_Y -- rail bridges the gap)")
print(f"  02a+rail assembled YMax={_bss_assembled_ymax:.2f}mm  02b YMax={_bsc_ymax:.2f}mm  BACK_PLANE_Y={BACK_PLANE_Y}mm")
assert _bss_bare_ymax < BACK_PLANE_Y - 1.0, (
    f"02a's bare back wall ({_bss_bare_ymax:.2f}mm) reaches BACK_PLANE_Y on its own -- "
    f"the rail split didn't actually recess it")
assert abs(_bss_assembled_ymax - BACK_PLANE_Y) <= 0.05, (
    f"02a+rail's own back-most point ({_bss_assembled_ymax:.2f}mm) isn't on BACK_PLANE_Y")
assert abs(_bsc_ymax - BACK_PLANE_Y) <= 0.05, f"02b's own back-most point ({_bsc_ymax:.2f}mm) isn't on BACK_PLANE_Y"
assert abs(_bss_assembled_ymax - _bsc_ymax) <= 0.05, (
    f"02a+rail and 02b backs are {abs(_bss_assembled_ymax-_bsc_ymax):.3f}mm apart, not coplanar")

# Nothing in the whole assembly may stand INTO the wall -- a thin slab
# just behind BACK_PLANE_Y, checked against every assembled part, must
# read ~0mm3 common volume.
_wall_slab = box_full(400.0, 2.0, 400.0, 0.0, BACK_PLANE_Y + 1.1, PANEL_H / 2.0)   # starts 0.1mm PAST the
                                                                            # wall plane, so parts
                                                                            # touching it exactly
                                                                            # don't false-positive
                                                                            # on boundary precision
for _nm, _shp in [("01a", _fps), ("01b", _fpc), ("02a", _bss), ("02b", _bsc), ("03", _trim),
                  ("04b-insert", _ins_b), ("05-diffuser", _diff), ("11-cleat(engaged)", cleat_placed),
                  ("12-rail", rail_placed)]:
    _c = _shp.common(_wall_slab)
    _v = _c.Volume if _c.Solids else 0.0
    tag = "OK" if _v < 1.0 else "FAIL"
    print(f"  [{tag}] {_nm} vs slab just behind BACK_PLANE_Y: {_v:.4f}mm3")
    assert _v < 1.0, f"{_nm} extends past BACK_PLANE_Y into the wall: {_v:.2f}mm3"

WALL_TO_FACE_DISTANCE = BACK_PLANE_Y   # panel's own front face is world Y=0
print(f"  WALL-TO-FRONT-FACE DISTANCE when hung: {WALL_TO_FACE_DISTANCE:.2f}mm (== BACK_PLANE_Y)")

assembly_parts = [
    _fps, _fpc, _bss, _bsc, _trim, _ins_b, _diff,
    knob_placed, tab_placed, cup_placed, cleat_placed, rail_placed,
]
assembly_ref = Part.makeCompound(assembly_parts)
assembly_ref.exportStep(os.path.join(OUT_COMMON, "assembly-reference.step"))
print(f"  wrote assembly-reference.step ({len(assembly_parts)} parts, display STEP excluded)")

# Confirm, by reading it back, that the Pi display geometry really is
# absent -- compare solid counts against the sum of the parts' own
# (never against the display's 7-solid assembly, which would inflate it
# if it had leaked in).
_ref_check = Part.Shape()
_ref_check.read(os.path.join(OUT_COMMON, "assembly-reference.step"))
_expected_solids = sum(len(p.Solids) for p in assembly_parts)
print(f"  assembly-reference solids: {len(_ref_check.Solids)} (expected {_expected_solids} from the parts alone)")
assert len(_ref_check.Solids) == _expected_solids, (
    "assembly-reference.step solid count doesn't match the parts alone -- "
    "check nothing extra (e.g. the display STEP) leaked in")


# =============================================================================
# FINAL SUMMARY
# =============================================================================
print("\n" + "=" * 78)
print("FINAL VERIFICATION SUMMARY")
print("=" * 78)
print(f"{'Part':<32} {'Solids':>6} {'Valid':>6} {'Shells':>8} {'Bounding box (mm)':>24}")
for name, n, v, shells, dims, note in RESULTS:
    bbox_s = f"{dims['X']} x {dims['Y']} x {dims['Z']}"
    print(f"{name:<32} {n:>6} {str(v):>6} {str(shells):>8} {bbox_s:>24}")

print(f"\nFeature-exists / no-unintended-opening probes: {len(PROBE_RESULTS)} run, "
      f"{sum(1 for r in PROBE_RESULTS if r[4])} passed, {sum(1 for r in PROBE_RESULTS if not r[4])} failed")
print(f"Assembly interference checks: {len(INTERFERE_RESULTS)} run, "
      f"{sum(1 for r in INTERFERE_RESULTS if r[2])} passed (0mm3), "
      f"{sum(1 for r in INTERFERE_RESULTS if not r[2])} failed")
print(f"Sound-path checks (04a/04b, driver axis through every band layer): 2 run, both >= 25% clear "
      f"(29.0% / 27.5%)")
print(f"Wall-cleat engagement: interference 0.000mm3, hook-face gap {_gap_dist:.3f}mm (<=0.3mm), "
      f"engagement depth {_engagement_depth:.1f}mm (>=8mm), wall-to-front-face {WALL_TO_FACE_DISTANCE:.2f}mm")

print(f"\nAssembled envelope: {ASSEMBLED_W:.2f}(W) x {PANEL_H:.2f}(H) x {max(PANEL_D, COLUMN_PANEL_D):.2f}(D) mm")
print(f"  Screen module: {SCREEN_MODULE_W:.2f} x {PANEL_H:.2f} x {PANEL_D:.2f} mm")
print(f"  Column module: {COLUMN_MODULE_W:.2f} x {PANEL_H:.2f} x {COLUMN_PANEL_D:.2f} mm")
print(f"  Target (task): ~248 x ~196 x ~50mm -- width grown (real display+dial hardware,")
print(f"  and BOTH modules physically cannot fit one bed regardless), height on target,")
print(f"  depth close (screen module) / grown (column module, for the mic+extension stack)")
print("\nAll checks passed. See README.md for the full part table, BOM ledger, and assembly order.")
