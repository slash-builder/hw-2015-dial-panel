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

## Still to print
Plates 3–9, and re-prints of 1, 2 and 5 from `main`. Worth checking on each:

- **Plate 1:** is the window edge clean, and does the raised trim ring look right?
- **Plate 2:** does the USB-C plug pass through the cable slot? Does the 10 mm LED strip seat fully in the band groove?
- **Plate 3:** the engraved dial ticks, and whether the KY-040 bushing and the KCD1 rocker fit their openings (both unconfirmed dimensions from listings).
- **Plate 4:** does the cleat hang flat, with the rail engaged?
- **Plate 5:** does the knob's D-bore fit your encoder's shaft (the flat width is an assumed dimension)?
- **Plate 7:** does the speaker sit in the pod, and does the diffuser clear the cone?
