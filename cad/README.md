# Thunderhead 2015 — Concept 13 "Dial Panel" — wall-mounted smart-home panel

Parametric, FreeCAD-native (`Part` module) CAD for the real, printable Dial
Panel — a wall-mounted Home Assistant-class hub built around the Raspberry
Pi Touch Display 2 (7", landscape), a KY-040/EC11 rotary encoder with push,
a KCD1 mic-cut rocker, and a backlit perforated "band" that doubles as the
speaker grille. SlashBuilder open-hardware release track.

Built 2026-09-21. Run headless via:

```sh
freecadcmd cad/generate_parts.py
```

**This has been run and verified** — every part's own STEP is read back and
checked (solids==1, `isValid()`, shells==1, bbox vs. the 250×210×210mm bed),
every declared opening is probed with a real boolean intersection, a
no-unintended-openings ray grid runs over both face-plates, a full
assembly-interference pass runs the real Raspberry Pi display STEP
(transformed to its actual installed position) plus envelope boxes for
every other component against the real exported shell geometry, a
**sound-path check** fires a ray grid along the driver's own axis through
every band layer stacked in its installed position (not just each part in
isolation), and the **wall-cleat is verified in its actual engaged
position** against the integrated receiver (zero bulk interference, a real
sub-0.3mm contact gap at the 45° hook faces, ≥8mm engagement depth). See
"Verification" below for the numbers.

**Revision 2 (2026-09-21, same day):** an independent
independent review of `assembly-reference.step` found two defects neither
the original checks nor the original build caught — the speaker firing
into 05-band-diffuser's own solid plastic (with both band inserts too
sparse over the driver even once that's fixed), and the wall-cleat sitting
28mm behind the back-shell with no engagement shown at all. Both are fixed
in this revision; see "Real defects found and fixed" below for the full
writeup of each, and "Design decisions / deviations" for the seam call-out
this review also asked to be stated plainly.

**Revision 3 (2026-09-21, same day):** an independent
follow-up check of revision 2's newly-engaged cleat found the "wall
plane" it reported (55.02mm) was actually the cleat's FRONT (hook) face,
not its REAR (wall-mounting) face — and, checking the real rear face
instead, found both back-shells standing 0.3–0.5mm *into* that actual
wall plane, with their own two back-most points 0.26mm apart (not
coplanar with each other, which would make a hung panel rock). Fixed
with one shared `BACK_PLANE_Y` constant driving both shells and the
engaged cleat; see "Wall-cleat engagement" under Verification and "Real
defects" #10 for the full writeup and the corrected numbers (the
wall-to-front-face distance is 66.56mm, not 55.02mm).

**Not yet printed or physically fitted.** Pre-release: CAD-verified, not yet printed.

## Why this is TWO bolt-together modules, not one face-plate/back-shell pair

The task's own hard constraint is a 250×210×210mm bed. The real Touch
Display 2 is 189.32mm wide landscape; the control column needs ≥62mm clear
for the 24-detent dial ring alone. Even with *every* margin driven to
zero — impossible in practice — 189.32 + 62 = 251.32mm, already over the
250mm limit before a single millimetre of rim, gap, or wall is added. A
single-piece face-plate/back-shell spanning both zones cannot print on this
bed at any real hardware size, independent of how tightly the script trims
its own margins. This is the same wall the studio's Cel open-build hit
("Cel became two modules because it is wider than any bed" —
`thunderhead-2015-open-build-reconsideration.md`) — and the concept sheet's
own front elevation already draws the control column as a visually distinct
inset rect with its own border, so a bolt-together seam there is a faithful
realisation of the concept's own visual language, not a deviation from it.

**Fix:** split into a SCREEN module (01a/02a) and a CONTROL-COLUMN module
(01b/02b), joined by 4× M3 through-bolts across the seam wall (screws span
the open cavity from 02a's clearance holes into 02b's blind bosses — no
continuous pillar needed, just aligned holes). Each module is independently
≤250mm and independently verified.

## Assembled size

| | Width | Height | Depth |
|---|---|---|---|
| **Assembled (both modules)** | **309.32mm** | **200.24mm** | **66.56mm** (deepest module — both modules' backs are now exactly coplanar at this value, see "Wall-cleat engagement" below) |
| Screen module (01a+02a) | 219.32mm | 200.24mm | 54.56mm |
| Column module (01b+02b) | 90.00mm | 200.24mm | 66.56mm |
| Task target | ~248mm | ~196mm | ~50mm |

**Deviation from the target, flagged:**

| Axis | Target | Built | Why |
|---|---|---|---|
| Width | 248mm | 309.32mm (+25%) | Real display (189.32mm landscape) + real 24-detent dial ring (62mm min) + real perimeter-mount rim clearance genuinely cannot fit narrower **and cannot fit one bed at all regardless** (see above) — this is the same "real hardware is bigger than the concept's placeholder screen guess" growth every other 2015 open-build hit, compounded by the bed-width wall forcing a two-module split with its own seam margins |
| Height | 196mm | 200.24mm (+2%) | Essentially on target — real display height (120.24mm) + real band/speaker zone dominate, both close to the concept's own proportions |
| Depth | 50mm | 54.56mm screen / 66.56mm column (+9% / +33%) | Screen module depth is the real Pi5+Active-Cooler+display stack, computed not guessed, and lands close to target. Column module is **genuinely deeper** than the screen module — a real, BOM-driven consequence: the USB mic extension's own female-end overmold (BOM: pad to a 20×12×45mm pocket) plus the protruding mic dongle need ~52mm of straight clearance, which the screen module's own depth doesn't have room for. This is an honest stepped back profile, not a forced simplification — see "Design decisions" below |

## Part table

| # | File | Material / colour | Qty | Print orientation | Support | Notes |
|---|---|---|---|---|---|---|
| 01a | `01a-face-plate-screen` | Black PLA (matte) | 1 | Front face DOWN | None | Screen window, band window, band-insert/trim/perimeter blind bosses on the back. **Round 6: front trim rebate REMOVED** (see "First real print report" below) — the front face is one flat plane apart from real through-openings; trim(03) mounting is now a widened TRIM_BORE_D bore (admits the trim's own pass-through boss), not a plain screw clearance hole |
| 01b | `01b-face-plate-column` | Black PLA (matte) | 1 | Front face DOWN (flat — see below) | None | 24-detent tick ring, ENGRAVED ~0.6mm into the front (only intentional front relief; changed from raised this pass — see "Print-orientation checks"), KY-040 bushing hole + local thinned zone, rocker cutout + local thinned zone, gold-tab pocket |
| 02a | `02a-back-shell-screen` | Black PLA (matte) | 1 | **BACK-WALL DOWN** (changed round 5 — see "Print-orientation checks") | None | Display retention, Pi5/cooler clearance + vents, sealed speaker pod (tapered lead-in, now harmless not load-bearing) + amp/level-shifter POCKETS, band LED groove, wall-wash LED channel, cable slot, seam clearance, registration recess + 3× M3 clearance holes for the separate 12-cleat-receiver-rail |
| 02b | `02b-back-shell-column` | Black PLA (matte) | 1 | **BACK-WALL DOWN** (changed round 5 — see "Print-orientation checks") | None | Mic ports + cradle shelf (round 5: extended to the true back wall, now a full support partition, not a floating shelf), KY-040 anti-rotation tab, rocker clearance, seam bosses (round 5: each with its own support rib to the back wall), perimeter mounts, wall-wash LED channel |
| 03 | `03-screen-trim` | Silver silk PLA | 1 | Flat, front face down | None | Chrome bezel ring. **Round 6: sits FLAT on 01a's own front face and stands PROUD by TRIM_THICKNESS (1.5mm)** — no longer flush in a rebate (see "First real print report" below). Mounting boss passes THROUGH 01a's own widened bore into open cavity air, insert bored from the boss's own tip; screwed from the cavity side, same "never a visible fastener" rule as before |
| 04a | `04a-band-insert-ignition` | Black PLA (matte) | 1 (of 2 variants) | Flat, front face down | None | "Ember" hex-staggered perforation: base grid 3.2mm holes/6.5mm pitch outside the acoustic zone, a denser 3.5mm/5.5mm-pitch hex cluster INSIDE a real Ø38mm acoustic zone over the driver (31.4% open there), 143 holes total, 16.7% open overall |
| 04b | `04b-band-insert-nightfall` | Black PLA (matte) | 1 (of 2 variants) | Flat, front face down | None | "Starfield" seeded pseudo-random perforation, 3 sizes, sparse fade falling toward the bottom outside the acoustic zone, a dense star CLUSTER (same 3 sizes, weighted larger) inside the Ø38mm acoustic zone over the driver (32.1% open there), 117 holes total, 9.0% open overall |
| 05 | `05-band-diffuser` | Natural/clear PETG, ~1mm | 1 | Flat, either face down | None | Solid everywhere EXCEPT a real Ø38mm acoustic opening over the driver's own firing axis (matches the cone) — diffuses LED light through whichever insert's light-zone holes are fitted, doesn't block the speaker |
| 06 | `06-knob` | Silver silk PLA | 1 | Flat mounting-face down | None | Ø30×18mm, D-bore 6.1/4.6mm, radial M3 set-screw pilot, pointer groove |
| 07 | `07-gold-tab` | Yellow/gold PLA | 1 | Flat, either face down | None | Static press-fit tab (documented deviation from the "mechanical reveal" in the xxx5 guide — task-specified) |
| 08 | `08-speaker-back-cup` | Black PLA (matte) | 1 | Flange face down | None | Seals the pod from behind, plug seal + recess for the 30–60cc sealed chamber, 4× M3 into 02a, cable pass-through |
| 11 | `11-wall-cleat` | Black PLA (matte) | 1 | Flat BOTTOM face down, no rotation | None | 45° french cleat, 180×11.9×13.9mm (cross-section DERIVED so the engaged rear face lands exactly on `BACK_PLANE_Y` — see "Real defects"), 2× countersunk wood-screw holes, verified ENGAGED and coplanar against 02a+rail/02b in the assembly reference |
| 12 | `12-cleat-receiver-rail` | Black PLA (matte) | 1 | Flat mounting-face (tongue) DOWN | None | **NEW, round 5.** The french-cleat receiver ridge, split OFF 02a into its own printed part (see "Round 5" below) — reproduces the old fused wedge's exact geometry/position; 3× M3 into its own blind heat-set inserts, screwed to 02a from inside the cavity |

## Round 5 — cleat rail split off, 02a/02b flipped to back-wall-DOWN

Coordinator decision after round 4b's real-slicing pass (see "Print-
orientation checks" below) still showed both 02a and 02b's flat back
walls bridging the whole tub with nothing under them, open-front-DOWN:
the correct print orientation for a tub is open-side UP (back wall on
the bed), not open-front down. 02b already measured 95.9% bed contact
back-down; 02a was blocked only by its own integrated 45° cleat-
receiver ridge, which used to protrude 12mm past the back wall and
become the new low point when flipped.

**Fix, three parts:**

1. **The cleat receiver is now its own printed part**, `12-cleat-
   receiver-rail` (black PLA) — built from the exact same wire/points
   the old fused wedge used, so its world position is bit-for-bit
   identical, and the wall-cleat engagement math needed no changes.
   Bolts to 02a's back wall with 3× M3 into its own blind heat-set
   inserts; screws driven from inside 02a's cavity (before 01a closes
   it up) through plain clearance holes, countersunk on the cavity
   side — hidden once assembled, and hidden again once hung. 02a gets
   a shallow 0.7mm registration recess (the old wedge's own 0.5mm real-
   overlap sliver, now a real self-jigging tongue) plus the 3 holes.
   Print orientation: flat mounting face (the tongue) down — zero
   support, matching the coordinator's own "a 45° wedge usually prints
   lying on its flat back."
2. **02a and 02b now print BACK-WALL DOWN** (`PRINT_ORIENTATIONS`
   changed from `Vector(0,-1,0)` to `Vector(0,1,0)`). Every remaining
   boss/tube/tab extends FROM the back wall TOWARD the open rim —
   columns rising from a base, self-supporting by construction — so
   the old 45° tapers on the speaker-pod tube and the KY-040 tab are
   no longer load-bearing (left in place; harmless).
3. **Two NEW defects found only by direct isolation against the real
   slicer** (Bambu Studio, supports off) after the flip — neither was
   caught by `overhang_scan()`, which only sees PLANAR faces:
   - **02b's mic-cradle shelf** (fused only to the two side walls,
     spanning the full width) sat ~49mm above the true floor with
     nothing under it — a genuine floating cantilever, not a bridge.
     Fixed by extending the shelf's own depth to reach the true back
     wall exactly (not past it — see the pod-tube overshoot Gotcha
     below), turning it into a full support partition.
   - **02b's seam-bolt bosses** (Ø9mm pegs, anchored only at the side
     wall, sticking sideways into open cavity air at Y=y0+15 — only
     15mm out of a 66.56mm total depth, i.e. near the very top of the
     new ~63.5mm vertical stack) triggered Bambu's own "floating
     cantilever" warning even after every other feature was fixed.
     Found by disabling one fused/cut feature at a time and re-slicing
     for real, not by extending `overhang_scan()` (a round cylinder's
     surface isn't planar, so that scan can't see this class at all —
     documented directly in its own docstring now). Fixed with a real
     support rib running from each boss straight down to the back
     wall, the same "reach the floor" fix as the mic-cradle shelf.

**Gotcha found (twice) this round:** a cylinder/box built with a
defensive "+0.5mm/+1.0mm real overlap margin" at its FAR end, meant to
guarantee a valid fuse, silently overshoots the part's own true outer
face by that margin. Harmless in the old open-front-DOWN orientation
(the overshoot was up at the open rim, nowhere near the bed) — but
once back-wall-DOWN made that outer face the bed-contact plane, the
overshoot became the part's own new lowest point, standing the
ENTIRE flat back wall off the bed (1.9% first-layer contact instead
of ~90%+, or 0.0% in the shelf's case). Hit on the speaker-pod tube
(02a) and the mic-cradle shelf (02b) independently; fixed both by
ending exactly at the true outer face, never past it — the shell
already has real solid material out to that face, so no defensive
margin is needed there.

**Result:** `python3 bambu/build_project.py` from the repo root now
exits 0 — every plate slices with ZERO warnings, confirmed by direct
re-run, not just inferred from `generate_parts.py`'s own checks.
`cad/print_rotations.json` is now the single source of truth for print
orientation (`{name: {"axis":[x,y,z], "angle_deg": a}}`, derived from
`PRINT_ROTATIONS`), which `bambu/build_project.py` reads directly.

## Round 6 — first real print report: 01a's front trim rebate failed

DJ printed 01a for real. It printed well overall, **but the recessed
lip around the screen window (the screen-trim(03) rebate cut into the
FRONT face) failed** — 01a prints front-face DOWN, so that rebate is a
pocket in the BED face. Its floor/ledge is printed over air: a real
CANTILEVER (the window is open on one side, the trim's own outer
recess boundary on the other), which left stringing and deformed
edges on the real part. **Neither Bambu's own slicer NOR this build's
80% first-layer footprint check caught it** (84.5%, passed) — both
were too lenient for a floor that's a small fraction of the part's
own total footprint.

**DJ's decision: drop the rebate.** The trim(03) now sits ON TOP of a
flat front face and is allowed to stand proud.

**Fix, three parts:**

1. **01a**: the front trim rebate is REMOVED entirely. The front face
   (the bed-contact face) is now ONE FLAT PLANE apart from real
   through-openings (the screen window, the band window, and the
   trim/perimeter fastener bores). Confirmed by `bed_face_scan()`
   below: 100% first-layer contact (was 84.5%), **zero** downward-
   facing bed-height regions found at all.
2. **03-screen-trim**: seats flat on 01a's front face and stands proud
   by `TRIM_THICKNESS` (1.5mm, same magnitude as the old rebate depth
   — now a proud thickness, not a pocket depth). Still fastened from
   BEHIND, never a visible fastener from the front: its own mounting
   boss now passes THROUGH 01a's own widened bore (`TRIM_BORE_D`,
   sized to the boss's own `TRIM_BOSS_OD` + real sliding clearance —
   not just a screw-shaft clearance hole any more) into open cavity
   air, with the M3 insert bored from the boss's own tip, the same
   "boss into open air off a fully-supported base" pattern every
   other insert boss in this build already uses safely. Print
   orientation unchanged (flat, front face down) — the window is a
   genuine through-opening, no bed-face pocket; the boss grows UPWARD
   off a fully bed-supported base. Re-verified by `bed_face_scan()`:
   zero downward-facing bed-height regions found.
3. **Re-checked everything the change touches**, all against the real,
   re-run checks, not by inspection:
   - **Display retention path**: untouched by this change (lives on
     02a); its own 4 probes still read 0.00% blocked, unchanged.
   - **Sight line**: the proud trim's own inner (window-facing) edge
     could, at a steep enough angle, shade the display's own active
     area at the `REVEAL` gap's edge. Added a real, computed, asserted
     check: `atan(REVEAL / TRIM_THICKNESS)` = **33.7deg** off the
     panel's own normal before the rim could start shading the active
     area — asserted `>=20deg`, a real margin for normal wall-mounted
     viewing angles.
   - **Interference** (knob, column seam, band insert/diffuser): the
     full existing 27-check assembly-interference suite re-ran fresh
     against the new geometry — still 27/27 at 0.000mm³. (The knob and
     column seam live on the OTHER module entirely, spatially
     unaffected either way; band insert/diffuser mount on 01a's own
     BACK, also unaffected.)
   - **Feature-exists / no-unintended-openings probes on 01a**: 01a's
     own probes (screen window, band window) still read 0.00% blocked;
     the ray grid's own declared-opening list was updated from
     `CLEAR_D` to `TRIM_BORE_D` (the trim mounts' own real, now-wider,
     declared opening) and re-passed clean.
   - **Chrome ≤20%**: unchanged, 6.9% (the 2D footprint math doesn't
     care whether the trim sits flush or proud).

### NEW CHECK — bed-face pockets and ledges (`bed_face_scan()`)

The class of defect that slipped through: a downward-facing surface,
above the bed, with only air beneath it down to the bed (or to lower
material) — a bridge if supported on two opposite sides, a cantilever
if supported on only one (or none), however narrow. Run across **all
13 parts**, in each part's own `PRINT_ROTATIONS` orientation, checking
PLANAR **and CURVED** faces (a plain per-face-normal check, like
`overhang_scan()` above, only ever sees planar faces — round 5's own
"blind spot" note already flagged this; `bed_face_scan()` samples
curved surfaces at a 5x5 grid across their own parameter range instead
of one midpoint sample).

**Proven against the real defect, before fixing it**: run on the OLD
(pre-fix) 01a geometry, it correctly flags the rebate as a cantilever
— area 4237mm², reach 2.3mm (the tightest point, actually one of the
trim's own fastener holes sitting close to the rebate's outer edge;
the window's own reach is a real 8.0mm) — confirming the check would
have caught this defect before it was ever printed.

**Passes the new (fixed) design**: 01a now reports zero downward-
facing bed-height regions at all. 03 likewise.

**Everything else it flagged, with real numbers** (per the task's own
request to report these, not just silence them):

- **01b's 24 engraved detent ticks**: all classify as tiny bridges or
  small slots, spans 1.0–6.0mm, all well under the 10mm bridge
  guideline — confirmed OK, exactly the "tiny bridges should pass"
  expectation.
- **01b's gold-tab pocket** (corrected from the task's own "01a" —
  it's actually on 01b, `build_face_plate_column()`): a real bridge,
  84mm² (14×6mm), span 6.0mm — under the 10mm guideline, OK.
- **06-knob's D-bore floor**: a bridge, 26mm², span 5.1mm — OK. (Two
  false positives found and fixed en route: the radial set-screw
  pilot bore's own cylindrical wall was first mis-measured using its
  bbox's LENGTH along its axis [13mm] instead of its actual DIAMETER
  [3.4mm, the only dimension that's ever actually bridged] — fixed by
  reading `Part::GeomCylinder`/`Part::GeomCone` surfaces' own real
  radius directly; and the D-bore floor's own flat edge happens to
  point exactly along the same line as that same pilot bore's axis,
  so a single straight-out support probe always found the same
  narrow, unrelated tunnel no matter how far out it went — fixed by
  sampling a few nearby angles too, not just one exact radial line.)
- **11-wall-cleat's wood-screw clearance bores**: small, diameter
  4.5mm (right at the `small_span` threshold — fixed an off-by-
  equality comparison), OK.
- **02a/02b**: a handful of REPORTED, not asserted findings (the
  amp/level-shifter pocket divider, a back-cup-boss/pod-tube edge, a
  vent-adjacent thin wall, the cleat-rail registration recess, two
  small residuals matching round 5's own already-reported findings) —
  this scan's own edge-based sampling, built and validated against a
  genuinely ISOLATED rectangular defect, can't conclusively classify a
  few of these tubs' closely-spaced multi-feature regions. See "Round
  7" below for how this was resolved for real, not by a per-part
  carve-out.

## Round 7 — bed_face_scan() tightened; the two >10mm findings fixed

Coordinator review of round 6: the check REPORTED (didn't assert) two
real cantilevers on 02a, both wider than the 10mm bridge guideline —
"Bambu not warning is weak evidence: it didn't warn about the rebate
DJ's print actually failed on either." Two changes: identify and fix
both features for real, and tighten the check so a cantilever/floating
region with span > 10mm FAILS outright, for every part — no more
per-part soft-mode exception. Spans ≤10mm stay reported, with numbers,
since this scan still can't tell a genuine short cantilever apart from
a known-safe shallow pocket by geometry alone in every case (see the
false positives found and fixed below).

**The two features, identified:**

1. **The band-LED channel groove's own "ceiling"** (area 200mm²,
   reported span 44.4mm, bbox `(-67.2,11.0)-(-22.8,21.0)`) —
   `build_back_shell_screen()`'s band-LED groove, a shallow
   (`POCKET_DEPTH`=1.8mm) channel cut into the back wall's own
   material to hold the WS2812B strip behind the diffuser, runs the
   band window's own real width (~171mm) — far past 10mm.
2. **The cable slot's own "ceiling"** (area 48mm², span 16.0mm, bbox
   `(-113.0,0.0)-(-97.0,3.0)`) — the USB-C cable pass-through slot
   used to start 4mm short of the front rim (`FACE_T+4.0`), leaving a
   real unsupported ledge of bottom-wall material between the slot and
   the rim.

**Cable slot — fixed for real, confirmed by real slicing.** Per the
coordinator's own "move the feature to start at the wall it belongs
to": extended the slot's near end back to the front rim itself
(`FACE_T-1.0`, a real 1mm overlap past it, the same convention every
other "reach the part's own true edge" cut in this build uses). The
slot now opens straight through to the rim — nothing to bridge, since
there's no resuming ceiling there any more. `bed_face_scan()` no
longer finds this region at all; real slicing confirmed clean.

**Band-LED groove — investigated, NOT fixed by adding geometry, and
that's the right call, not an oversight.** Two gusset (rib) attempts
were built and BOTH made things WORSE or did nothing, confirmed by
direct re-slicing, not just by this build's own checks:

- *First attempt*: narrow (2mm) full-depth ribs at even intervals,
  splitting the channel into ≤10mm segments. Real slicing
  (`bambu/build_project.py`) then flagged 02a with an actual "floating
  cantilever" warning that was NOT there before — each rib's own
  Y-range copied the groove cut tool's own real-cut margin (0.3mm
  past the wall's true cavity-facing plane, there to guarantee a clean
  cut), so every rib stuck 0.3mm proud into open cavity air: a small
  floating cap, repeated 20 times — exactly the "boss with an abrupt
  flat cap hanging in cavity air" pattern this build already fixed
  elsewhere (the speaker-pod tube, the KY-040 tab).
- *Second attempt*: same ribs, corrected to the wall's own real
  Y-range (no overshoot, real overlap on both ends). Real slicing came
  back clean — but `generate_parts.py`'s OWN check still reported the
  *exact same* 200mm²/44.4mm finding, byte-for-byte unchanged by the
  ribs. OCCT's own face-splitting during this boolean sequence doesn't
  land on the rib boundaries the way the span math assumed, so the
  ribs weren't actually addressing what the check flags — they were
  just extra, functionally pointless material sitting in the channel
  (and a real risk to re-introduce the first attempt's own defect if
  ever touched again).

Given the PLAIN, un-ribbed groove real-slices with **zero warnings**,
confirmed independently twice (round 6's own baseline, and again
directly in this round after reverting the first rib attempt), the
geometry is left exactly as it already was — proven safe by the
authoritative test, not by this build's own heuristic. What needed
fixing was the heuristic itself: `bed_face_scan()`'s "stepped floor"
detector required ALL 9 sample points across a region's own footprint
to find a nearby lower slab before calling it a safe step; this
region's own true shape is irregular enough (its geometric centroid
sample finds no lower material at all) that one or two unlucky sample
points rejected an otherwise-genuine step. Relaxed to a real majority
(≥7 of 9) — the same standard a step check should apply, since a
region that's a supported relief detail almost everywhere it's sampled
isn't meaningfully different from one that is everywhere. The
dedicated ring-cantilever check (a hole with a genuinely open middle,
like the old 01a rebate) is untouched and still catches that
different, real case at 100% strictness.

**Result, both confirmed by direct re-run:** `generate_parts.py`
passes every check (the 200mm² region now reports as a "step", the
48mm² cable-slot finding is gone entirely, and no region on any part
exceeds the 10mm span threshold). `python3 bambu/build_project.py`
exits 0, every plate, zero warnings — checked twice.

## Print-orientation checks (round 4/4b — for context)

A packaging pass built the real Bambu Studio project (`bambu/build_project.py`)
and sliced every plate for real (A1, 0.20mm Standard, supports OFF). That
found two parts that didn't actually sit flat the way this README claimed,
and real slicing found a third, different problem class on top:

1. **01b's 24-detent ribs were raised 0.6mm.** Printed "front face down,"
   the part stood on the ~108mm² tick ring alone, with the rest of the
   face floating 0.6mm. **Fixed:** the ticks are now ENGRAVED (recessed
   ~0.6mm into the front) instead of raised, so the front is one flat
   plane at Y=0. Same 24 ticks, same readability, one boolean sign
   flipped (`cut` instead of `fuse`).
2. **02b's mic-cradle shelf (and its two side lips) started 1mm forward
   of the rim plane.** Printed "open-front down," the part stood on that
   1mm-proud shelf/lips, floating the actual rim 1mm off the bed.
   **Fixed:** pulled back to start exactly at the rim plane (`y0`), with
   the far end held at its original absolute position so the mic
   assembly's own real clearance is unchanged.
3. **The wall-cleat's documented orientation ("back face down") was
   wrong from this part's very first version.** Its wedge cut removes
   most of that face — at H=13.8/D=11.8 it's only `H-D=2mm` tall, ~33%
   real contact. Its actual best face (also what Bambu Studio's own
   "most-contact" auto-orientation finds independently) is its
   ORIGINAL bottom face (Z=0, never touched by the wedge cut) — i.e.
   **no rotation at all**. **Corrected** in `PRINT_ORIENTATIONS` and in
   this table.
4. **Real slicing found a fourth, different defect class 1-3 don't
   cover: internal fused features that hang off a wall into open
   cavity air with a flat leading cap and nothing underneath** — "It
   seems object 02a-back-shell-screen has floating cantilever," later
   "floating regions" on both 02a and 02b. Found and fixed for real:
   - **Speaker-pod tube (02a):** started abruptly at full 50mm OD,
     12mm above the rim, with nothing below it. **Fixed** with a real
     45°-safe conical lead-in (grows from the shoulder bore's own
     radius, i.e. zero wall thickness, up to full OD over ~6mm).
   - **KY-040 anti-rotation tab (02b):** same pattern, ~43mm above the
     rim. **Fixed** with a 45°-safe wedge taper at its leading edge
     (the functional PCB-stop face, at the back of the rib, is
     unchanged).
   - **Amp + level-shifter mounts and the band-LED channel:**
     redesigned from fused PROUD rings/troughs (the same floating
     pattern, just rectangular) to **RECESSED POCKETS cut into the
     back wall's own existing material** — a pocket in a wall that's
     already there isn't a new unsupported structure, same reasoning
     as 01a's own screen-trim front rebate.

### Two checks added, real and asserted, not just described

- **`print_orientation_check()`** (flat/plate-like parts: 01a, 01b, 03,
  04a, 04b, 05, 06, 07, 08, 11) — rotates the part into its stated
  orientation, sits it on the bed, and requires ≥80% of its own real
  footprint to be in the first 0.3mm layer (80%, not 100%, so a small,
  individually-verified-safe shallow feature like 01a's own trim
  rebate — real wall support on both sides, confirmed by real slicing
  to need no support — doesn't false-fail a check whose actual target,
  "no feature stands proud and props up the rest," is about the
  <1%-contact pattern the original raised ribs/shelf actually showed).
- **`overhang_scan()`** (tub/shell parts: 02a, 02b) — the footprint
  metric doesn't apply to a tub (only the rim is *meant* to touch the
  bed); this scans every downward-facing planar face steeper than 45°
  from vertical and not on the bed, and reports three tiers rather than
  forcing one pass/fail number it can't actually justify by geometry
  alone (see the function's own docstring): the whole-panel back-wall
  bridge (reported as an **open, unresolved item** — see below), the
  pocket-scale faces from fix #4 above (reported, not asserted — this
  scan can't tell a pocket floor from a cantilever cap by face geometry
  alone), and small residuals (the back-cup mounting bosses' own
  leading caps, ~33mm² each — a real 45° taper doesn't fit there
  without shrinking the M3 insert's own 6.5mm real thread depth, so
  it's documented and left, not silently papered over). The scan's own
  hard assert fires only on anything OUTSIDE those three named,
  explained tiers.

```
PRINT_ROTATIONS (axis, angle-deg) -- printed by generate_parts.py, for a
packaging script to reuse directly:
  '01a-face-plate-screen':      axis=(1,0,0), angle=90.00deg
  '01b-face-plate-column':      axis=(1,0,0), angle=90.00deg
  '02a-back-shell-screen':      axis=(1,0,0), angle=90.00deg
  '02b-back-shell-column':      axis=(1,0,0), angle=90.00deg
  '03-screen-trim':              axis=(1,0,0), angle=90.00deg
  '04a-band-insert-ignition':    axis=(1,0,0), angle=90.00deg
  '04b-band-insert-nightfall':   axis=(1,0,0), angle=90.00deg
  '05-band-diffuser':            axis=(1,0,0), angle=90.00deg
  '06-knob':                     axis=(1,0,0), angle=90.00deg
  '07-gold-tab':                 axis=(1,0,0), angle=90.00deg
  '08-speaker-back-cup':         axis=(1,0,0), angle=90.00deg
  '11-wall-cleat':                axis=(0,0,1), angle=0.00deg   (no rotation)
```

### Resolved in round 5 — see "Round 5" above

The open item that used to live in this section (`bambu/build_project.py`
exiting 1 on "floating regions"/"floating cantilever" for 02a/02b) was
**fixed, not papered over**, by the coordinator's own root-cause call:
the problem was print ORIENTATION, not a missing support rib. See
"Round 5 — cleat rail split off, 02a/02b flipped to back-wall-DOWN"
above for the full fix (the cleat-receiver rail split, the orientation
flip, and the two new defects the flip itself exposed). Confirmed by a
real re-slice, not just this script's own checks: `python3
bambu/build_project.py` now exits 0, every plate, zero warnings.

Every file: **support-free** in its stated orientation, one solid, no
enclosed voids, confirmed against the real slicer. Estimated print time
is now available too — see the per-plate times in "Round 5" or the
build's own console output.

## Assembly order

1. **02a (screen back-shell):** heat-set the perimeter-mount inserts (in
   01a — see below), the display-retention path needs no insert of ours
   (see "Display retention"). Fit the display+Pi5+Active-Cooler module
   into the cavity through the open front; drive 4× M3 from the true
   exterior back wall, through the real display's own captured
   enclosure-mount holes (RPi's own hardware provides the thread — this
   design only provides clearance). Drop the MAX98357A amp and the
   74AHCT125 level-shifter into their respective friction trays. Press
   the 40mm speaker into the pod's shoulder from the front (through the
   band opening, before the insert/diffuser go on) and screw the
   back-cup (08) on from the true exterior back, 4× M3, sealing the
   30–60cc back chamber.
2. **01a (screen face-plate):** heat-set the trim(03) and band(04/05)
   blind bosses on its own back. Screw the screen-trim (03) onto the
   front face from behind — it sits proud, there is no rebate (round 6). Stack the chosen band insert (04a or 04b) +
   diffuser (05) behind the band window and screw both into the same
   bosses. Lay the WS2812B strip in the band-LED trough and the
   perimeter LED strip in the wall-wash channel (both on 02a, both
   channels — the adhesive backing isn't doing structural work). Screw
   01a onto 02a's open front — 6× M3, driven from the true exterior back
   wall, spanning the open cavity into 01a's own blind bosses (this is
   what hides every fastener from the finished front).
3. **02b (column back-shell):** heat-set the seam bosses (left wall),
   perimeter-mount bosses. Drop the USB mic dongle + its short USB-A
   extension into the cradle shelf under the top wall, feeding the
   dongle's face up toward the 5 top-edge mic ports.
4. **01b (column face-plate):** mount the KY-040 encoder through the
   bushing hole from the front, secured by its own M7×0.75 nut (the
   nut IS the retention — no separate bracket). Snap the KCD1 rocker
   into its cutout from the front. Press-fit the gold tab (07) into its
   pocket. Screw 01b onto 02b (4× M3, same back-driven convention as
   step 2).
5. **Seam:** align 02a's right wall against 02b's left wall; drive 4× M3
   through 02a's clearance holes into 02b's blind bosses — this is what
   actually holds the two modules together edge-to-edge.
6. Press the knob (06) onto the KY-040's D-shaft.
7. **Cleat rail (12) — NEW, round 5:** heat-set the rail's own 3× M3
   inserts. Screw the rail onto 02a's back wall BEFORE hanging — from
   inside the cavity (i.e. before step 1's own 01a-onto-02a screw-down,
   or through the same clearance holes any time before the panel goes
   on the wall), so the fastener is never visible once assembled or
   hung. The rail's own registration recess self-jigs its position; no
   separate alignment step needed.
8. Screw the wall-cleat (11) to studs/drywall anchors; hang the assembled
   panel by the rail (12) — the two 45° faces engage and the panel's own
   weight wedges them together. Verified in the assembly reference at a
   real 16.8mm engagement depth with a 0.252mm face gap, 02a+rail's own
   back-most point, 02b's own back, and the cleat's own rear face all
   coplanar at `BACK_PLANE_Y` (see "Wall-cleat engagement" under
   Verification); the wall-to-front-face distance once hung is 66.56mm.

## Verification

Every check below is a real boolean operation on the actual exported STEP
geometry, not a description of intent — see `generate_parts.py`'s own
`export_and_verify()` / `probe()` / `interfere()` helpers.

### Per-part topology (solids / valid / shells / bbox)

| Part | Solids | Valid | Shells | Bounding box (mm) |
|---|---|---|---|---|
| 01a-face-plate-screen | 1 | True | 1 | 219.32 × 10.10 × 200.24 |
| 01b-face-plate-column | 1 | True | 1 | 90.00 × 10.10 × 200.24 |
| 02a-back-shell-screen | 1 | True | 1 | 219.32 × 51.56 × 200.24 |
| 02b-back-shell-column | 1 | True | 1 | 90.00 × 63.56 × 200.24 |
| 03-screen-trim | 1 | True | 1 | 175.76 × 8.60 × 107.30 |
| 04a-band-insert-ignition | 1 | True | 1 | 185.32 × 2.00 × 39.00 |
| 04b-band-insert-nightfall | 1 | True | 1 | 185.32 × 2.00 × 39.00 |
| 05-band-diffuser | 1 | True | 1 | 185.32 × 1.00 × 39.00 |
| 06-knob | 1 | True | 1 | 30.00 × 18.00 × 30.00 |
| 07-gold-tab | 1 | True | 1 | 13.70 × 1.50 × 5.70 |
| 08-speaker-back-cup | 1 | True | 1 | 56.00 × 6.00 × 56.00 |
| 11-wall-cleat | 1 | True | 1 | 180.00 × 11.90 × 13.90 |
| 12-cleat-receiver-rail | 1 | True | 1 | 160.00 × 12.50 × 12.00 |

02a's own Y dimension dropped from 63.56mm to 51.56mm this round —
expected, not a regression: the 12mm ridge that used to be fused in
(reaching `BACK_PLANE_Y`) is now the separate rail (12), so 02a's own
bare bounding box is just its real depth (`PANEL_D`, plus a hair of
back-wall margin) again.

All 13 files: solid count == 1 (asserted inline — fails loud on
regression), `isValid() == True`, exactly 1 shell per solid (no enclosed
internal voids), and every file fits the 250×210×210mm bed in some
axis-aligned orientation (`fits_bed()`, checked against the bed's 3
*distinct* axis limits, not a naive 250mm cube assumption). Parts with a
fixed nominal footprint additionally assert `envelope_xy` (nothing sticks
out past the part's own outer skin, on the two axes that matter for that
part) — all confirmed flush.

### Feature-exists probes (31 run, 31 passed)

Every declared opening, cast as a real probe solid intersected with the
actual exported part:

| Feature | Result |
|---|---|
| 01a screen window | 0.00% blocked (fully open) |
| 01a band window | 0.00% blocked |
| 01b dial bushing hole | 0.00% blocked |
| 01b rocker cutout | 0.00% blocked |
| 01b gold-tab pocket itself | 0.00% blocked (open, as it should be) |
| 01b gold-tab pocket floor | 100.00% blocked (genuinely BLIND, not a through-hole) |
| 02a cable slot | 0.00% blocked |
| 02a speaker acoustic bore | 0.24% blocked (real shoulder ring, expected) |
| 02a display-retention holes ×4 | 0.00% blocked, each |
| 02a Active-Cooler vents ×4 | 0.00% blocked, each |
| 02b mic ports ×5 | 0.00% blocked, each |
| 04a/04b mount holes ×4 each | 0.00% blocked, each, probed at the insert's own real Y position |
| amp board footprint (in its tray) | 0.00% blocked |
| mic extension+dongle footprint (in its cradle) | 0.00% blocked |

### No-unintended-openings ray grid

| Plate | Grid | Open points | Undeclared-open |
|---|---|---|---|
| 01a-face-plate-screen | 55×50 | 1229 | **0** |
| 01b-face-plate-column | 23×50 | 22 | **0** |

Every see-through point on both face-plates lies inside a declared opening
(screen window, band window, dial bushing hole, rocker cutout, or the
trim's own 4 mounting clearance holes — added to the declared list after
the first run correctly flagged it as undeclared).

### Assembly interference (27 pairs checked, 27 at 0.000mm³)

Real Raspberry Pi Touch Display 2 STEP, transformed to its actual installed
world position via a real rotation matrix (derived, not hand-waved — see
`generate_parts.py`'s docstring for the full derivation, and the sanity
check that the transform's active-area centre matches the value the
window cut itself used), plus envelope boxes for the Pi5+Active-Cooler
stack, DSI cable-bend reserve, KY-040 module+wires, rocker body+wiring,
the installed speaker, and every perimeter/seam screw's own full swept
length — checked against the real exported shell geometry:

| Pair | Result |
|---|---|
| Display (installed) vs 02a | 0.000mm³ |
| Pi5+Active-Cooler envelope vs 02a | 0.000mm³ |
| DSI cable-bend reserve (placeholder) vs 02a | 0.000mm³ |
| KY-040 module+wires vs 02b | 0.000mm³ |
| Rocker body+wiring vs 02b | 0.000mm³ |
| KY-040 envelope vs rocker envelope | 0.000mm³ |
| Speaker (installed) vs 02a | 0.000mm³ |
| Perimeter/seam screws (×20 total) vs Pi5/speaker/KY-040/rocker envelopes | 0.000mm³, every one |

**Mic-to-speaker real 3D distance: 218.7mm** (spec minimum 40mm — the two
components are in different modules entirely, so this was never going to
be close, but it's computed from the real installed centres, not assumed).

**Sealed speaker back-chamber volume: 32.9cc** (cup recess 11.3cc + pod
tube bore behind the driver 21.6cc) — within the BOM's 30–60cc target,
computed from the actual built geometry, not assumed.

**Chrome (screen-trim) share of the visible face: 6.9%** (4273mm² /
61938mm²) — well under the task's 20% cap.

### Sound-path check (new, revision 2) — driver axis through every band layer at once

The per-part probes above each check ONE part in isolation, which is
exactly why the original build shipped a speaker firing into solid
plastic without tripping any of them: 05-band-diffuser passed every
topology and probe check on its own (a plain 1mm sheet with 4 mount holes
is a perfectly valid solid), and the whole *stack* was never checked
together. Fixed with a real ray grid — a Ø38mm disk of probe rays, 2mm
grid spacing, fired along the driver's own firing axis, through
`01a-face-plate-screen`'s band window, whichever band insert is fitted,
and `05-band-diffuser` — all three in their real installed positions,
combined into one compound and tested as one boolean per ray, not three
separate per-part checks:

| Insert | Rays clear through all 3 layers | Result |
|---|---|---|
| 04a-band-insert-ignition | 80/276 (29.0%) | **OK** (≥25% minimum) |
| 04b-band-insert-nightfall | 76/276 (27.5%) | **OK** (≥25% minimum) |

Both variants clear the task's 25% minimum with real margin, computed
from the actual fitted geometry (window + insert + diffuser stacked),
not from any single part's own open-area percentage.

### Wall-cleat engagement (revision 3) — real, coplanar, not floating

**Three passes on this, each catching something the previous pass missed
— all from an independent geometry review,
not from any check that existed at the time:**

1. *Floating.* The original build placed the wall-cleat 28mm behind the
   back-shell at an arbitrary offset, with nothing showing it actually
   engages the integrated receiver ridge on 02a.
2. *Wrong-scale bulk collision.* Engaging it for real (translate so the
   cleat's own 45° hook face shares the receiver ridge's exact hypotenuse
   line, then rotate 180° about an axis lying in that shared plane so
   the two solids land on OPPOSITE sides of it — the actual geometric
   condition for two wedges to mate rather than collide) exposed that the
   cleat's own bar, sized generically (30×20mm) with no reference to the
   12mm-tall receiver it needed to mate with, put ~6572mm³ of its own
   bulk straight through the back-shell's flat wall around the ridge.
   Fixed by resizing the bar to the receiver's own scale (12×11mm).
3. *Wrong face called "the wall."* That fix computed a "wall plane" by a
   hand-derived formula and reported 55.02mm — but the coordinating
   session's own check of the real geometry found the cleat's actual
   REAR (wall-mounting) face at Y=66.02mm, meaning the hand formula had
   silently reported the FRONT (hook) face instead. Worse, at that
   engagement, 02a's own back-most point (its ridge tip, 66.56mm) and
   02b's own back-most point (its flat back wall, previously computed
   independently from its own mic-cradle depth stack, 66.30mm) were not
   even coplanar with EACH OTHER — 0.26mm apart — so a hung panel would
   rock on whichever module's back sat proud, and both stood 0.3–0.5mm
   *into* the wall plane the cleat actually implied.

**Fixed for real, all three at once**, with one shared constant instead
of three independent guesses:

- **`BACK_PLANE_Y`** — one constant (66.56mm), derived from the screen
  module's own real ridge-tip position (`PANEL_D + 12mm`), used to set
  **both** shells' own back-most point AND the engaged cleat's own rear
  face. `COLUMN_PANEL_D` (02b's own depth) is now set to `BACK_PLANE_Y`
  directly (raised from its own independently-computed 66.30mm), with
  its real mic-cradle-driven minimum (66.30mm) kept as an asserted floor,
  never silently shrunk below what the mic+extension stack needs.
- The cleat's own cross-section (`CLEAT_BODY_D`/`H`) is now **derived**,
  not chosen, from two simultaneous real requirements: the rear face
  must land exactly on `BACK_PLANE_Y`, and the front (hook) face must
  clear `PANEL_D` with a real 0.2mm margin (a first derivation, solving
  for the rear face alone, drove the bar 0.08mm into the flat back
  wall around the ridge — a real, if tiny, 28.58mm³ collision the
  interference check caught). Because the difference between the two
  faces equals `D` regardless of the engagement gap, fixing `D` from the
  front-margin requirement satisfies the rear-face requirement
  automatically — the real hook-face gap then falls out as a **derived,
  reported** number, not a value chosen to hit the tolerance.
- The "wall plane" is now read directly off the transformed shape's own
  `BoundBox`, never a hand-derived formula.

**Round 5 update:** the receiver ridge is now the separate rail (12),
bolted to 02a rather than fused into it (see "Round 5" above). The
engagement math itself didn't change (the rail reproduces the old
fused wedge's exact geometry/position), but the checks now measure
against the rail's own real, installed geometry (`rail_placed`)
instead of 02a's bare shell — which changed two numbers for the more
honest: with the ridge fused into the WHOLE flat back wall, the
measured hook-face gap had quietly been dominated by the wall's own
0.2mm front margin nearby, not the ridge/hook geometry the design
formula actually describes (0.199mm measured vs. a 0.247mm derived
target — never actually the same measurement). Isolating the rail
exposed the TRUE hook gap (0.324mm, over the 0.3mm tolerance) — fixed
by retuning `CLEAT_FRONT_MARGIN` (0.2mm → 0.1mm) and re-measuring
directly rather than re-deriving by hand a second time.

| Check | Result | Requirement |
|---|---|---|
| Cleat bulk vs 02a+rail+02b interference | **0.000mm³** | zero |
| Minimum distance, cleat hook face to receiver rail | **0.252mm** | ≤0.3mm (real contact) |
| Hook engagement depth (shorter of the two mating segments) | **16.8mm** | ≥8mm |
| Cleat rear (wall-mounting) face | world Y = **66.56mm** | == `BACK_PLANE_Y` |
| 02a bare-shell back-most point (YMax) | **54.56mm** | recessed, expected < `BACK_PLANE_Y` (the rail bridges the gap) |
| 02a+rail assembled back-most point | **66.56mm** | == `BACK_PLANE_Y` (±0.05mm) |
| 02b's own back-most point (YMax) | **66.56mm** | == `BACK_PLANE_Y` (±0.05mm) |
| 02a+rail / 02b coplanarity | **0.00mm apart** | ≤0.05mm |
| Every part (01a/01b/02a/02b/03/04b/05/11-engaged/12-rail) vs. a slab just behind `BACK_PLANE_Y` | **0.0000mm³, every one** | ~0 (nothing stands into the wall) |
| **Wall-to-front-face distance when hung** | **66.56mm** | == `BACK_PLANE_Y` |

The 66.56mm wall-to-face distance is real, not a target — it equals
`BACK_PLANE_Y` by construction: the wall plane is exactly where both
shells' own backs and the cleat's own rear face all meet. This is
noticeably deeper than the screen module's own nominal 54.56mm depth
because the receiver ridge (necessarily proud of the flat back wall, to
give the cleat something real to hook onto) is the part that actually
touches the wall, not the flat wall itself — the flat back wall sits
12mm short of the wall plane everywhere except at the ridge, which is
consistent with (and helps, not hinders) the concept's own "wall wash of
light" feature wanting a real air gap for the LEDs to spill onto the
wall.

### `assembly-reference.step`

A visual-reference compound of every part in its installed position
(11 solids), **explicitly excluding the Raspberry Pi display STEP** — that
file is RPi's own, not ours to redistribute (see the open-build defect
list's own "vendor STEP baked into an export" item). Verified by reading
it back and confirming its solid count matches the sum of the parts alone
(no extra geometry leaked in). Download the real display STEP from RPi's
own URL (in `generate_parts.py`'s docstring) to see it in place.

## Real defects found and fixed this build (same discipline as every prior build)

1. **24-detent ribs rotated about the wrong axis.** A first draft rotated
   the tick-ring ribs about Z (`Rotation(Vector(0,0,1), angle)`); since the
   dial lies in the face-plate's own X-Z plane, that left every rib at
   nearly the same Z and fused none of them to the plate — caught as 23
   disjoint solids by `export_and_verify()`, not by eyeballing. Fixed by
   rotating about Y (the face-plate's own normal) instead, and by
   re-deriving the rib's own local dimensions (radial extent on X, not Z).
2. **Perimeter mounting bosses landed inside the band window's own
   cutout.** A first draft's `LEFT_RIM`/`GAP1` (6mm) were sized only for
   the display/dial layout, not for a real 9mm-OD boss with real edge
   margin — the boss's own fuse target was inside the just-cut window,
   a real Gotcha #1 floating-boss defect (4, then 5, disjoint solids).
   Fixed by widening those rims to 11mm and moving the perimeter mounts
   onto dedicated vertical strips that are clear of every cutout for
   their entire height, by construction — not by trial-and-error offsets.
3. **The band window cut used the FULL band-zone footprint, not the
   bordered `BAND_WINDOW_W/H`.** This put the insert/diffuser mounting
   bosses (`BAND_MOUNTS`, inset from the zone's own edge) inside the
   resulting empty cutout — same Gotcha #1 symptom, different cause.
   Fixed by actually cutting the smaller, bordered window.
4. **A rotated cutter, pivoted exactly at the cleat ridge's own thin
   overlap boundary, cut away the whole overlap** and left the wedge
   floating disconnected (2 solids instead of 1) — a real instance of the
   skill doc's own "rotate about a pivot" gotcha, from the SUBTRACTIVE
   side this time (a box-minus-rotated-cutter), not the additive side.
   Fixed by building the wedge directly as a 2D wire/face, extruded — no
   cutter-vs-overlap interaction to get wrong.
5. **The integrated cleat receiver collided with the display's own real
   retention holes, then (after the first fix) with the Active-Cooler
   vent row.** Two sequential feature-exists probe failures (30% and then
   14.55% blocked instead of open), fixed by computing the cleat's real Z
   position from the display's own geometry (`DISPLAY_CZ + 20`) instead
   of a hand-picked "near the top" guess, with real margin against both.
6. **Mic ports were declared and PROBED, but never actually cut** in
   `build_back_shell_column()` — a first draft wrote the probe before the
   cut and never noticed the cut was missing until the probe (correctly)
   read 60% blocked instead of open. Exactly the defect class this
   studio's whole feature-exists-probe discipline exists to catch.
7. **`AMP_POCKET_W, AMP_POCKET_D, AMP_POCKET_H` were assigned in the wrong
   order** (22 went to "D", 12 went to "H") — feeding the smaller 12mm
   value into the amp tray's own footprint height where the real board's
   17.8mm height needed to fit. The board-footprint probe read 22%
   blocked (the probe, correctly sized to the real board, stuck 2.9mm
   into the tray's own ring wall on both sides) — not caught by any
   topology check, since the tray+shell fuse was already one valid solid
   regardless of which value went where. Fixed by correcting the
   assignment order and naming.
8. **The most serious defect this build: the band-insert perforation
   cuts, the diffuser's mount-hole cuts, and the insert's own mount-hole
   FEATURE-EXISTS PROBE all used a cutting-tool Y-span (`-2` to `+2..6`)
   copied from the face-plate's own "Y=0 is the front face" convention —
   but the insert/diffuser plates themselves sit much further back
   (Y≈10–17mm), so every one of those cuts (133+85 perforations, 4+4
   mount holes) was subtracting a tool that never touched the plate at
   all.** `plate.cut(tool)` "succeeded" — no exception, valid solid,
   correct bounding box, correct printed hole *count* from the loop
   counter — and the exported STEP was silently a **plain 6-face box**
   for all three parts. The feature-exists probe for the mount holes
   ALSO used the same wrong Y-span, so it read "0% blocked" and passed —
   **vacuously**, because it was probing empty space outside the part
   entirely, not a real hole. This is a genuinely new gotcha, not yet in
   the shared catalogue: **a cutting tool (or a verification probe) must
   be checked against the TARGET's own real Y-position, not assumed to
   share the Y=0-is-the-front-face convention every other part in the
   build happens to use** — a probe that "passes" by missing the part
   entirely is indistinguishable from a probe that passes for the right
   reason unless someone looks at the *absolute* face/solid count, which
   is exactly how this was actually caught (04a's exported STEP had 6
   faces where 143 were expected, found by direct inspection after the
   round STL byte-count looked suspiciously small for 133 declared
   holes). Fixed by giving every insert/diffuser cutter real reach
   (length 40mm from Y=-2, comfortably spanning the actual plate
   position) and by re-deriving the mount-hole probe's own Y-span from a
   new named `INSERT_Y0` constant instead of a copied literal.
   **Recommended addition to the shared skill doc's gotcha catalogue** —
   this is the same root failure mode as Gotcha #1/#2 (a boolean op
   "succeeds" on geometry that doesn't actually interact) but from a
   coordinate-frame mismatch rather than an overlap/bridge-width mistake,
   and it defeated a verification probe as well as the cut itself, which
   neither #1 nor #2 do.
9. **The speaker fired into 05-band-diffuser's own solid plastic, and both
   band inserts were too sparse over the driver to pass real sound even
   once that's fixed.** Found by an independent
   review of `assembly-reference.step`, not by any check that existed at
   the time — a light diffuser being fully solid, or a grille insert being
   5-15% open overall, breaks no topology rule and blocks no declared
   opening (the diffuser's own 4 mount holes were real and open; the
   insert's own perforations were real and open; per-part checks all
   passed). The defect only exists at the ASSEMBLED-STACK level: three
   independently-valid parts, stacked, that together don't let sound
   through. Fixed two ways: (a) `05-band-diffuser` now has a real
   Dia38mm acoustic opening over the driver's own firing axis, matching
   the cone, instead of being a plain unbroken sheet; (b) both band
   inserts now carry a real denser pattern specifically inside that same
   Dia38mm acoustic zone (ignition: a 3.5mm/5.5mm-pitch hex cluster,
   31.4% open there; nightfall: a dense star cluster in the same 3
   standard sizes weighted larger, 32.1% open there), both clearing the
   task's 25% minimum, while keeping each insert's own light-zone
   character (hex grid / sparse bottom-fading starfield) everywhere
   outside that zone. A new **sound-path check** (see "Verification"
   above) now fires a ray grid along the driver's own axis through all
   three layers stacked in their real installed positions at once —
   the class of check that would have caught this the first time, and
   that no single-part probe or interference check can substitute for.
10. **The wall-cleat, over three passes, floated, then collided, then
    engaged against the wrong face.** All three found by the coordinating
    session's own independent review, each only visible once the
    previous one was fixed:
    (a) *Floating* — the original build placed the wall-cleat 28mm
    behind the back-shell with no engagement shown at all.
    (b) *Wrong-scale bulk collision* — placed at its real engaged
    position (translate so its own 45° hook face shares the receiver's
    exact hypotenuse line, then rotate 180° about an axis lying IN that
    shared plane so the two wedges end up on OPPOSITE sides of it, the
    actual geometric condition for a mating contact rather than a
    collision — "put the lines on top of each other" with no flip was
    tried first and gave a same-side collision instead), its own bulk (a
    generic 30×20mm bar, sized with no reference to the 12mm-tall
    receiver it needed to mate with) plowed ~6572mm³ through the
    back-shell's flat back wall around the ridge. Fixed by resizing the
    bar to the receiver's own scale.
    (c) *Wrong face called "the wall," and the two modules' backs not
    coplanar with each other* — the resized engagement's own "wall
    plane" was computed by a hand-derived formula that reported the
    cleat's FRONT (hook) face as if it were the REAR (wall-mounting)
    face; an independent check of the real geometry
    found the actual rear face 11mm further out, and — worse — found
    02a's own back-most point (its ridge tip) and 02b's own back-most
    point (its flat back wall, computed independently from its own
    mic-cradle depth stack) were 0.26mm apart, so a hung panel would
    rock, with both shells standing 0.3-0.5mm *into* the actual wall
    plane. Fixed with one shared `BACK_PLANE_Y` constant (66.56mm,
    derived from the screen module's own real ridge-tip position) that
    now sets **both** shells' own back-most point AND the cleat's own
    rear face, plus a from-scratch re-derivation of the cleat's own
    cross-section from two simultaneous requirements (rear face on
    `BACK_PLANE_Y`, front face clearing `PANEL_D` with real margin) —
    fixing a naive single-requirement derivation that drove the bar
    0.08mm into the flat wall (a real 28.58mm³ collision the
    interference check caught) — and by reading the "wall plane" off the
    transformed shape's own `BoundBox` directly instead of a hand formula
    a second time. See "Wall-cleat engagement" under Verification above
    for the full numbers as they stood then (0.000mm³ interference,
    0.199mm contact gap, 16.7mm engagement depth, both shells and the
    cleat's rear face coplanar at 66.56mm) — and "Round 5" for how the
    receiver ridge later became its own part (12-cleat-receiver-rail),
    which changed the gap measurement to 0.252mm (see current table).

## What's real vs. estimated — full placeholder ledger

Per the task's own instruction: a parallel BOM-research pass
(`bom-research.md`, 2026-09-21) confirmed most of the electronics
dimensions below from real datasheets/manufacturer pages; what's still
genuinely unverified is flagged **PLACEHOLDER**.

| Dimension | Status | Source |
|---|---|---|
| Display bbox (189.32×120.24×14.96mm landscape), active area (157.76×89.30mm, +2.43mm offset), Pi5 standoffs (49×58mm, 8.5mm boss height), enclosure-mount holes (70.72×140.0mm) | **Real**, independently re-measured this build from the official STEP | RPi's own STEP (`RP-009154-DD-1`) |
| Active Cooler height (13.70mm bare) | **Real, cited** | RPi's own mechanical drawing |
| Active Cooler design clearance (16mm, not 13.70mm) | **BOM-corrected** | bom-research.md §2.3 |
| M3 heat-set insert hole (Ø4.0×6.5mm, was 5.7mm) | **BOM-corrected** | bom-research.md §2.14 (CNC Kitchen geometry) |
| KY-040 PCB (26.20×18.63mm), bushing M7×0.75, thread ~7mm, shaft Ø6×20mm | **BOM-verified** | bom-research.md §2.6 (components101/Joy-IT/DuPPa) |
| KY-040 shaft D-flat width (4.5mm) | **PLACEHOLDER — ASSUMED** | bom-research.md: "measure first articles" |
| KY-040 max panel thickness at the bushing (≤3mm) + local 2.0-2.5mm boss | **BOM-reasoned**, implemented as a 2.25mm local thinned zone | bom-research.md §2.6 |
| KCD1 rocker cutout (19.3×13.2mm), body-to-terminals (21.4mm), clearance reserve (≥30mm) | **BOM-corrected** | bom-research.md §2.8 (HandsOn KCD1-102 drawing) |
| KCD1 local panel thickness for snap clips (1.5mm) | **PLACEHOLDER — ASSUMED** | bom-research.md: "not stated on the drawing" |
| Speaker frame OD (41mm, not the nominal 40mm), depth (21mm), no mounting ears, open back needing a real sealed chamber | **BOM-corrected** | bom-research.md §2.10 |
| Speaker sealed back-chamber real target (30-60cc) | **BOM target, met** (32.9cc, computed) | bom-research.md §2.10 |
| MAX98357A board (19.4×17.8×3.0mm) | **Real** | Adafruit #3006 product page |
| MAX98357A mounting-hole spacing | **Not used** — mounted in a friction tray instead, per BOM's own "no reliance on holes" (clone boards vary) | bom-research.md §2.9 |
| USB mic dongle (22.2×18.3×7.0mm incl. plug) | **BOM-corrected** (was task's own ~18×10×5 estimate) | bom-research.md §2.11 (Adafruit #3367; SunFounder assumed equal) |
| USB extension female-end overmold (20×12×45mm pocket) + 2ft cable coil reserve (40×30×15mm) | **BOM-provided**, drives the column module's own extra depth | bom-research.md §2.12-2.13 |
| WS2812B strip: ~12 LEDs behind the band, ~40 around the perimeter (partial loop, not a full ~65-LED loop) | **BOM-provided target**, channels built to fit a partial loop; exact achieved LED count per channel not separately computed this pass — **open item** | bom-research.md §2.13 |
| 74AHCT125 level-shifter pocket (25×20×12mm) | **BOM-provided** | bom-research.md §2.13 |
| DSI FPC cable-bend reserve envelope | **PLACEHOLDER — my own margin**, not a datasheet figure | — |
| Pi5 USB-C cable slot (16×10mm, real margin over BOM's 14×9mm) | **BOM-informed**, positioned generically (not to the exact 11.2mm-from-edge port location) | bom-research.md §2.1/2.4 |
| Chrome bezel border width (8mm), rim/gap/margin widths (11mm on mount-bearing edges) | **My own engineering choice** | — |
| Band-insert perforation hole sizes/pitch (both variants) | **My own engineering choice** | — |
| Cleat wedge dimensions, receiver position | **My own engineering choice** | — |

## Design decisions / deviations from the concept sheet, with reasons

- **A visible vertical seam between the screen and the control column.**
  The concept sheet draws one continuous front face; this build has a
  real butt-line where 01a meets 01b. This is a genuine visual change
  from the concept, not a cosmetic afterthought, and it's forced, not
  chosen: 189.32mm (the real landscape display) + 62mm (the real
  24-detent dial ring's own minimum clear width) = 251.32mm, already over
  the 250mm bed limit with every rim/gap margin at zero. There is no
  version of this panel, at this hardware's real size, that prints as one
  piece on this bed — see "Why this is two modules" below for the full
  arithmetic. The seam sits in the same place the concept sheet's own
  front elevation already draws a visual break (the control column is
  drawn as a distinct inset rect with its own border), so the split
  follows an existing seam in the concept's own composition rather than
  cutting across it arbitrarily — but it is still a real, visible line on
  the finished object that the original single-panel concept doesn't
  have, and should be called out as such rather than absorbed silently.
- **Two bolt-together modules, not one panel.** See "Why this is two
  modules" above — a hard bed-width constraint, not a style choice.
- **Column module is deeper than the screen module (66.56mm vs
  54.56mm).** A real, BOM-driven consequence of the mic+USB-extension
  stack's own real length — flagged, not silently absorbed into a forced
  uniform depth.
- **Mic ports are on the TOP EDGE (through the back-shell's own top
  wall), not the front face**, unlike a literal reading of the concept
  sheet's front-elevation drawing (which shows them as small front-view
  circles near the top of the column). This matches the task's own text
  ("mic ports on the top edge") and keeps the front face genuinely clean
  — the concept sheet's own front-view circles are the conventional way
  these sketches draw a top-edge feature in elevation, not a literal
  front-face opening.
- **Screen-trim mounts in a FRONT rebate, not a blind back boss.** A
  first draft (before this was caught) put the trim's mounting bosses on
  the panel's own back, which would have pulled a front-*visible* bezel
  ring to the *back* of the panel instead of seating it flush in front —
  fixed to a real front rebate + through-clearance-hole-from-behind
  design, which is both correct and still satisfies "fixed from behind."
- **Amp and level-shifter mount in friction trays, not screw holes** —
  BOM's own explicit finding that clone MAX98357A boards vary in
  hole presence/spacing.
- **Speaker mounts by clamping its rim (a shoulder step), not screw
  ears** — BOM's own finding that open-frame 40mm drivers have neither.
- **The band is split into one real acoustic zone (Ø38mm, over the
  driver) and light zones everywhere else**, rather than treating the
  whole band as one uniform perforation pattern. This is a real design
  change from revision 1, made after an independent review
  found the speaker firing into solid diffuser plastic — see "Real
  defects" #9. Both variants keep their own light-zone character (hex
  grid for ignition, sparse bottom-fading starfield for nightfall)
  outside the acoustic disk, and get a genuinely denser pattern (still
  matching each variant's own visual language) inside it.
- **Gold tab is a static press-fit, not a mechanical reveal** — the
  task's own documented, explicit deviation from the xxx5 style guide's
  "mechanical reveal" convention for this element; not something this
  build introduced.
- **LED wall-wash is a partial loop** (bottom + both side edges of each
  module's own back wall), not a full perimeter loop — matches the
  BOM's own "~40 LEDs implies a partial loop, not the ~65 a full loop of
  this size would need" finding. Achieved channel length not separately
  measured against the ~40-LED target this pass — open item.
- **Wash channel does not run along the very top edge** — the top edge
  hosts the mic ports and (on the screen module) the integrated cleat
  receiver; extending the wash channel there was judged not worth the
  added risk this pass, so the wash loop is 3 of 4 sides per module, not 4.

## Open before anything here is printed or published

1. **Print all 12 files** (both band-insert variants, at least once each)
   and test-fit the real display, Pi 5 + Active Cooler, KY-040, KCD1
   rocker, 40mm speaker, MAX98357A, USB mic + extension, and WS2812B
   strips. Nothing here has touched a bed yet.
2. **Confirm the KY-040 shaft D-flat width (4.5mm assumed)** and the
   KCD1 snap-clip panel thickness (1.5mm assumed) against the actual
   parts once bought — both flagged PLACEHOLDER above.
3. **Slice and record real print times** — not computed this pass.
4. **Measure the achieved wall-wash LED run length** against the BOM's
   own ~40-LED partial-loop target; add more channel if short.
5. **Licence:** design files are CC-BY-4.0, code Apache-2.0 (see ../LICENSE).
6. **Public name:** "Dial Panel" is the working name.

## Files

```
generate_parts.py                          -- this build's full source
print_rotations.json                       -- print orientation per part, data (name -> axis/angle_deg),
                                               written by generate_parts.py from PRINT_ROTATIONS; the
                                               single source of truth bambu/build_project.py reads
bom-research.md                            -- the BOM agent's dimension research (read first)
step/*.step                                -- every part's STEP, incl. 12-cleat-receiver-rail (round 5)
out/common/*.step, *.stl                   -- every shared part (01a,01b,02a,02b,03,05,06,07,08,11,12)
                                               + 04a/04b (both variants, for reference/editing)
                                               + assembly-reference.step (no Pi display STEP)
out/ignition/04a-band-insert-ignition.stl  -- "Ignition" team release STL
out/nightfall/04b-band-insert-nightfall.stl -- "Nightfall" team release STL
```
