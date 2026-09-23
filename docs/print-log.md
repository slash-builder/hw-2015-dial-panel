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

## Still to print
Plates 3–9, and re-prints of 1, 2 and 5 from `main`. Worth checking on each:

- **Plate 1:** is the window edge clean, and does the raised trim ring look right?
- **Plate 2:** does the USB-C plug pass through the cable slot? Does the 10 mm LED strip seat fully in the band groove?
- **Plate 3:** the engraved dial ticks, and whether the KY-040 bushing and the KCD1 rocker fit their openings (both unconfirmed dimensions from listings).
- **Plate 4:** does the cleat hang flat, with the rail engaged?
- **Plate 5:** does the knob's D-bore fit your encoder's shaft (the flat width is an assumed dimension)?
- **Plate 7:** does the speaker sit in the pod, and does the diffuser clear the cone?
