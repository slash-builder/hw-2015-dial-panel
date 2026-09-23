# Print log

Real prints, what they showed, and what changed because of them. Add yours:
printer, filament, plate, what fit and what didn't. Fit reports are the most
useful contribution this project can get right now.

## 2026-09-22 · first prints · Bambu Lab A1, 0.20 mm, matte black PLA, supports off

### Plate 1 · 01a face plate — FAILED, fixed
Good overall, but the recessed lip around the screen window left **stringing
and deformed edges**.

**Cause.** That recess was the seat for the silver trim ring, cut into the
front face. 01a prints front-face down, so the recess was a pocket in the bed
face, and its ledge printed over air. Bambu's slicer did not warn, and the
first-layer check passed it at 84.5%.

**Fixed** (`1e4215f`): the rebate is gone, the front is one flat plane, and
first-layer contact is 100%. The trim ring now sits on top, proud by 1.5 mm,
still fastened from behind.

### Plate 2 · 02a back shell — printed on the pre-fix design, as predicted
Printed before the fix landed. **Stringing on the bottom edge at the cable
slot opening**, exactly where the new check reported a 16 mm unsupported
ledge (at z = 47.6 mm, about 4 mm below the top of the part).

**Fixed** (`1e4215f`): the cable slot now runs to the front rim, so there is
no ledge. The same commit splits the band-LED channel's 44 mm ceiling into
segments of 10 mm or less with gussets.

Still usable if you already printed it: both are print-quality defects in
those two spots, not fit or function.

### What these two taught the project
A slicer warning is not proof a part prints cleanly, and neither is a
first-layer contact percentage. `cad/generate_parts.py` now checks every part
for downward-facing surfaces with only air beneath them: anything spanning
more than 10 mm fails the build, shorter spans are reported with numbers. It
is proven against the old geometry — it flags the exact ledge that failed.

### Plate 3 · 01b + 02b, and the assembly that followed — FAILED to seat, fixed
Plate 3 printed with minor stringing at the light opening on the bottom.
Then **neither face plate would seat into its shell**: "the screw base bumps
the edge of the body."

**Cause, measured in the CAD:** the face plates' perimeter screw bosses
genuinely overlapped the shells' side walls — 448 mm³ on the screen module
(6 bosses, 2 mm into each wall) and 527 mm³ on the column (4 bosses, two of
them ~9 mm deep). Not a tolerance problem: the parts intersected.

**Why no check caught it:** the interference list was written by hand and
**never paired a face plate with its own shell**. It checked the display, the
pod, the cleat and the screws against the shells, but not the two biggest
parts that bolt together.

**Fixed:**
- the overlap is gone, and every nesting fit now clears by a real 0.4 mm
  printing allowance (PLA prints slightly oversized; a nominal 0 mm fit
  means "does not fit")
- the interference check is now generated from **all pairs** of placed parts
  (276 pairs, 1 named skip: the two interchangeable band inserts), so a pair
  cannot be missed by forgetting it
- a separate fit-clearance check classifies each pair: intended contact
  (seating faces, the knob and gold-tab press fits, the cleat hook) may touch
  at ~0; anything that nests or slides must clear by 0.4 mm

**Reprint after this fix:** 01a face plate, 02a back shell, 02b back shell,
03 screen trim. **01b (column face plate), the knob, gold tab, speaker cup,
cleat, rail and both band inserts are unchanged** — parts already printed
are still good.

## 2026-09-23 · Bambu Lab A1, 0.20 mm, matte black PLA, supports off

### Plates 8 and 9 · both band inserts — printed clean
Plate 8 (IGNITION, `04a`) and plate 9 (NIGHTFALL, `04b`) both printed with no
defects. The perforated grille came out well at 0.20 mm.

**They still have to be reprinted** — not because of print quality, but
because of what fitting them revealed.

### The band insert and diffuser had no mounting features at all — FAILED, fixed
First fit of the diffuser against the face plate showed it would not go into
the band window. It was never going to: the parts are meant to sit *behind*
the window and overlap its edge, and the window is 177.5 × 30.5 mm while the
parts were 185.32 × 39.00 mm.

The real fault was underneath that. **Nothing held them in place.**

**Measured in the exported CAD:**
- All four mounting bosses sat **exactly 1.0 mm outside the parts' outline**,
  in both axes. So the four M3 clearance holes did not exist — the cut removed
  **0.00 mm³**, leaving a 0.29 mm nick in each corner instead of a hole.
- The insert floated **0.4 mm behind** the boss tips it was bolted to, and the
  diffuser a further 1.0 mm behind that, across open air. A screw could only
  bow them.
- The diffuser's nearest neighbour in any direction was **3.4 mm away**. It
  was unlocated in X, Y and Z.

Meanwhile the assembly doc told builders to "screw both into the same bosses,
4 × M3 × 8" — which was impossible as drawn.

**Cause.** An earlier round widened the window border to stop those same
bosses printing in mid-air. The insert and diffuser are *sized off that
window*, and were never re-derived, so the fix moved one reference and broke
the other. Same root cause as the plate-3 seating failure: **a number moved
and everything derived from it stayed put.**

**Fixed:** the overlap is now computed from the border rather than restated,
giving a 3.0 mm wall around every hole. The parts grow from 185.32 × 39.00 to
**196.72 × 50.40 mm**, the insert seats flush on the boss tips and the
diffuser flush on the insert — both gaps now 0.0000 mm. M3 × 8 still reaches,
with 5.0 mm of thread engagement, so no BOM change.

**A second defect the first fix created**, caught before printing: once the
inserts grew, NIGHTFALL's perforation pattern ran into two of its own screw
holes, leaving walls of **0.08 mm and 0.96 mm**. At a 0.4 mm nozzle that
prints as a merged slot and tears on the first turn of a screw. Perforations
are now suppressed within 2.0 mm of any mounting hole, in both variants.

**Three new checks**, each proven to fail on the old geometry first:
- **fastener-hole-exists** — compares the volume a hole boolean actually
  removed against the cylinder it was asked for. A hole that removes 0.00 mm³
  is now the loudest failure in the run.
- **clamped-stack contact** — bolted faces must touch, not float.
- **no floating part** — nothing may have a nearest neighbour greater than zero.
- **minimum feature wall** — measured on the *finished* part, every pair of
  holes, because the first check deliberately probes the reference outline and
  so cannot see material eaten away from the side.

That last pair is worth understanding if you contribute CAD here: one check
proves the hole is there, the other proves there is still material around it.
Neither one is sufficient alone.

**Reprint after this fix:** `04a` band insert (plate 8), `04b` band insert
(plate 9), `05` band diffuser (plate 7). **Every other part is geometrically
identical to the previous version** — verified part by part against volume and
bounding box, not assumed. All nine plates slice with no warnings.

Two known cosmetic notes, both pre-existing and both flagged rather than
silently exempted: 04a has two grille perforations that merge by 0.35 mm where
the sparse outer grid meets the dense acoustic cluster (present in the version
that printed clean above, so it is proven printable), and the cleat receiver
rail is declared as touching the back shell but measures a deliberate 0.100 mm
registration clearance.

## Still to print
Plates 3–7, and re-prints of 1, 2, 5, and now 7, 8 and 9 from `main`. Worth
checking on each:

- **Plate 1:** is the window edge clean, and does the raised trim ring look right?
- **Plate 2:** does the USB-C plug pass through the cable slot? Does the 10 mm LED strip seat fully in the band groove?
- **Plate 3:** the engraved dial ticks, and whether the KY-040 bushing and the KCD1 rocker fit their openings (both unconfirmed dimensions from listings).
- **Plate 4:** does the cleat hang flat, with the rail engaged?
- **Plate 5:** does the knob's D-bore fit your encoder's shaft (the flat width is an assumed dimension)?
- **Plate 7:** does the speaker sit in the pod, and does the diffuser clear the cone?
