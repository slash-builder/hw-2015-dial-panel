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

**Printing plate 3 is how this was found**, and it condemned plates 1, 2 and 3
together — the same boss geometry is wrong on the screen module and the column,
so the parts already printed from plates 1 and 2 were stale the moment plate 3
came off the bed.

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

### Plate 5 · 03 screen trim ×2 + 06 knob ×2, silver silk PLA — printed clean
Printed from `main` after the trim-rebate fix, and good. This is the first
confirmation that dropping the rebate worked: the trim ring is now a flat
part that sits proud on the face, with nothing printing over air.

**Still unconfirmed on these parts**, so don't read this as a fit pass:

- **The trim ring against 01a.** 01a has not been reprinted since the fix, so
  the ring has not yet been offered up to the plate it screws to.
- **The knob's D-bore against a real encoder.** `KNOB_BORE_FLAT = 4.6 mm` is
  0.1 mm clearance over an **assumed** 4.5 mm shaft flat (`KY_SHAFT_FLAT_W`,
  marked ASSUMED in the CAD — the 6.0 mm round diameter is verified, the flat
  is not). If your encoder's flat is wider than 4.5 mm the knob will not seat;
  if it is narrower the knob goes on but rotates on the flat until the radial
  M3 set screw bites, which is recoverable.

The encoder had not arrived at the time of this print, so **the flat is still
unmeasured**. If you have a KY-040 in hand before we do, measure across the
flat and report the number — it is the last dimension in this build taken from
a listing rather than a datasheet, and one measurement closes it for everyone.

### Plate 4 · 08 speaker cup + 11 wall cleat + 12 receiver rail — printed, looks right
### Plate 6 · 07 gold tab ×3 — printed, looks right
Both printed and correct on inspection. Neither has been **fitted** yet: the
cup, cleat, rail and tab all mate with body parts that are mid-reprint, so the
real checks — does the cleat hang flat with the rail engaged, does the speaker
seat in the pod, does the tab press into its pocket — are still open.

None of these parts has changed since they were printed, so they will not need
reprinting.

## 2026-09-24 · plate 3 reprinted · Bambu Lab A1, 0.20 mm, matte black PLA

### The column closes now — but three of four screws foul, and the seam had no holes

The reprinted plate 3 **seats and closes correctly**, so the perimeter-boss
fix worked. Fitting it then found the screws and screw bosses fouling the
shell's internal structure. Two separate faults came out of that, one of them
far more serious than the thing being reported.

#### Fault 1 · three of four column screws run into the seam ribs

Measured on the exported CAD, sweeping each screw axis through the shell:

| Screw | On-axis obstruction |
|---|---|
| X 72.56, Z 18.00 | **49.50 mm of solid**, Y 12.50→62.00 |
| X 72.56, Z 185.24 | **49.50 mm of solid**, same span |
| X 146.76, Z 18.00 | clears the shank, fouls at head diameter |
| X 146.76, Z 185.24 | clear |

Three foul, one is clean — exactly what the builder reported.

The obstruction is the **seam bosses and their support ribs** (X 65.00–77.00,
Y 12.50–62.00). Those ribs were added in an earlier round to cure a slicer
warning about a boss cantilevered in mid-air, and nothing re-checked them
against the perimeter screws already sharing that space.

**Why nothing caught it:** `01b` against `02b` measures **0.00 mm³ overlap,
0.0000 mm minimum distance**. The two solids genuinely do not touch — the
*fastener that passes between them* does. No check modelled the fastener.

**Fixed** by relieving the screw's real swept envelope out of the seam
material. No screw or seam-bolt position moved.

#### Fault 2 · all four seam bolts had no hole at all

Found while verifying the first fix. The shell contained **zero cylindrical
features running along X** — no seam bore anywhere in the part. Probing each
bolt position:

```
material inside the bore = 81.68 mm³ of 81.68 mm³   — completely filled, all four
```

A bolt would have met **12.25 mm of continuous solid**. As printed, **the
column module could not be bolted to the screen module at all.**

The cause was boolean ordering: the code cut the insert bore, then fused the
support rib over the same region, filling it straight back in. The bore was
cut correctly and then destroyed by a later operation.

**Fixed** by restructuring the build so every fuse happens before every cut,
which makes the ordering safe by construction rather than by getting it right
once. The insert also moved to the boss's near face and a clearance bore now
runs through the shell wall to reach it, so the bolt has a continuous path.
Verified through both shells: bore 0.00 mm³ obstructed at all four positions,
approach clear, with the expected 3 mm of blind material behind each insert.

#### New checks, both proven to fail on the old geometry first

- **fastener-access** — sweeps each fastener's real envelope (thin shank the
  whole travel, widening to the countersink only at the entry) through every
  part it should pass clear of. Covers all 20 fastener positions.
- **bore-stays-open** — asserts on the *finished* part that each insert bore
  is actually open. This is the one that catches a hole cut correctly and then
  refilled by a later operation, which is invisible to every other check.

That makes four fastener checks, and they are not redundant: one proves the
hole exists, one proves there is material around it, one proves you can reach
it, and one proves nothing filled it back in afterwards.

#### Reprint

**`02b` back shell, column (plate 3) only** — volume changed by −995.64 mm³.
`01b` on the same plate is untouched, as is every other part in the build,
verified part by part on volume and bounding box. All nine plates slice with
no warnings.

## 2026-09-25 · first fit coupons printed, and what they found

### Coupons A and C — both PASS

Plate 1 of the coupon project printed all seven black-PLA pieces.

- **A (screen corner) passed.** The boss presses into the wall opening and
  seats flush by hand. Worth noting A deliberately tests the *worst* case: the
  one boss narrow enough to need a reduced diameter because the standard 9 mm
  would not fit there. **Validates the 2026-09-22 boss/wall fix.**
- **C (band mount) passed.** The stack clamps flat. **Validates the
  2026-09-23 fix**, where the mounting holes had removed 0.00 mm³ and the
  hardware floated with nothing to clamp against.
- **B could not be tested** — no screw long enough. The holes line up
  visually, which does confirm the seam bores exist and are coaxial.

That last point turned out to matter far more than it sounded.

### The screws were never checked for length — none of them

There is no screw long enough because **no real screw would work**. Measured
on the exported CAD:

| Joint | Specified | Reality |
|---|---|---|
| Face plate → shell (screen) | M3 × 12 | needs ~49 mm — **32 mm short** |
| Face plate → shell (column) | M3 × 12 | needs ~61 mm — **44 mm short** |
| Seam bolts | M3 × 16 | max usable **12.21 mm** — bottoms out, head **3.79 mm proud** |
| Trim ring | M3 × 8 | pilot only **2.90 mm** — bottoms out |

**18 of 25 fasteners were specified wrong.** The face plate's boss ended
10.1 mm in, the shell's back wall sat 45–56 mm further back, and between them
was *nothing* — the screw was expected to cross open air.

**Why nothing caught it:** every check modelled the **hole**. None modelled
the **screw** as an object with a length. Feature-exists, access, bore-open,
minimum-wall — all correct, all passing, all blind to the one property that
made the joint impossible.

**Fixed:** the face-plate bosses now run the real depth of the shell
(48.56 mm screen, 60.56 mm column, both derived from the shell depth rather
than restated), with the insert recessed 3.6 mm from the clamping tip so an
M3 × 12 gets 5.30 mm of engagement instead of bottoming out. Each boss carries
a printed gusset, because a bare Ø9 column 50–60 mm tall is the floating
cantilever this project has already fixed four times, and slicer supports
cannot be cleared out of a blind bore.

Seam bolts become **M3 × 12** and trim screws **M3 × 3** — documentation and
BOM changes only, no geometry.

**New check — fastener length.** Models every fastener as a real object and
asserts the specified screw reaches and engages. It fails on the old geometry
reporting all four faults above.

**Also fixed: the check runner could never fail.** `freecadcmd` exits 0 even
when an assertion fires — it prints the error and returns success. Every
"exit 0, all checks passed" in this project's history was reading a number
that could not report failure. All 72 assertions now exit non-zero properly,
verified by forcing a failure.

### One more, found while fixing the above

The speaker back-cup's countersink was cut on the face that mates against the
shell, instead of the outward face. Its **volume and bounding box are
completely unchanged** — only the countersink moved, 77.18 mm³ of material.
A reprint list derived from volume and bounding box would have missed it
entirely. It needs reprinting.

### Reprint after this fix

**01a, 01b, 02b and 08.** Plates 1 and 3 get longer: plate 1 goes from
1 h 31 m to **2 h 06 m**, plate 3 from 4 h 34 m to **4 h 57 m**. All nine
plates slice with no warnings.

### Still open

The seam bolt's head bears on the screen shell's *cavity-side* wall, so it
must be driven **before** that module is closed — but the assembly order
closes the screen module at step 9 and drives the seam bolts at step 11. That
ordering needs resolving before anyone follows the instructions literally.

## Where the build stands

**All nine plates have now been printed at least once.** What is current and
what is stale:

| Plate | Parts | State |
|---|---|---|
| 1 | 01a face plate, screen | **reprint** — long perimeter bosses (now 2 h 06 m) |
| 2 | 02a back shell, screen | **reprint** — cable slot + boss fix |
| 3 | 01b + 02b column | **reprint both** — 01b long bosses, 02b screw access + seam bores |
| 4 | 08 cup, 11 cleat, 12 rail | **reprint 08** — countersink was on the mating face (11 and 12 are current) |
| 5 | 03 trim ×2, 06 knob ×2 | current — coupon C passed |
| 6 | 07 gold tab ×3 | current, fitting pending |
| 7 | 05 band diffuser | **reprint** — new mounting geometry |
| 8 | 04a IGNITION insert | **reprint** — new mounting geometry |
| 9 | 04b NIGHTFALL insert | **reprint** — new mounting geometry |

Six plates to re-run, three good. **A full fitting is deliberately deferred
until the body parts are reprinted** — most of the remaining unknowns are
fits between a body part and something that bolts to it, and there is no
point testing those against superseded geometry.

Still worth checking as they come off:

- **Plate 1:** is the window edge clean, and does the raised trim ring look right?
- **Plate 2:** does the USB-C plug pass through the cable slot? Does the 10 mm LED strip seat fully in the band groove?
- **Plate 3:** the engraved dial ticks, and whether the KY-040 bushing and the KCD1 rocker fit their openings (both unconfirmed dimensions from listings).
- **Plate 4:** does the cleat hang flat, with the rail engaged?
- **Plate 7:** does the speaker sit in the pod, and does the diffuser clear the cone?
- **Plates 7–9 together:** do the insert and diffuser now actually bolt to the
  four bosses, flush, with the screws reaching? That is the whole point of the
  last fix and it is the one thing no check can settle.
