# Fit coupons

Three small test pieces, cut straight out of the real printed parts, so you
can check the fits that have actually gone wrong on this build **without**
printing the full plates 1, 2 and 3 (10 h 36 m combined on a Bambu Lab A1).
Print `bambu/dial-panel-coupons.3mf` instead — two plates, about 1 h 20 m
total — before you commit a full print run to a body part you haven't
fitted yet.

**These are test pieces, not printed parts of the finished panel.** They
don't go in the assembly. Throw them away (or keep them as a fit-check kit)
once the real plates have printed and fitted.

## Why coupons instead of a smaller scale model

If you've built one of these before, printing a 25% scale model to check
fit quickly is the obvious move — except it doesn't work here. Every
failure this build has actually had came from a clearance that was too
tight, and clearances don't scale: shrink the whole part to 25% and
`FIT_CLEARANCE` (0.4 mm) becomes 0.10 mm, the wall thickness (3.0 mm)
becomes 0.75 mm, and the M3 clearance hole (Ø3.4 mm) becomes Ø0.85 mm — well
under what any FDM printer can resolve reliably, and nowhere near what a
real M3 screw needs. A quarter-scale model would tell you the *shape* is
right and say nothing true about whether it *fits*, which is the one
question these coupons exist to answer.

A coupon fixes this by staying at 1:1 and being cut, not redrawn, from the
exact STEP files that ship in `cad/step/` — the same geometry that goes to
the real plates. If a coupon fits, the real part fits that spot. If a
coupon doesn't, the real part won't either, and you've found out in
80 minutes instead of 10+ hours.

## What "cut from the real part" means

Each coupon is a small box, intersected with the actual exported part —
never a fresh sketch of what that corner is *supposed* to look like. Where
two parts meet (a screw boss and the wall it sits inside; the two halves
of the seam), both halves are cut with the exact same box, so the
interface between them survives the cut exactly as it is in the real
parts. Regenerate all three any time the real parts change:

```
freecadcmd cad/coupons.py
python3 bambu/build_coupons_project.py
```

## The three coupons

### A — Screen corner (`A1` + `A2`)

**Tests:** a perimeter screw boss nested right up against the shell's own
side wall, right at a corner — the tightest clearance spot on the whole
panel. `A1` is the face-plate corner (`01a`, with its screw boss); `A2` is
the matching back-shell corner (`02a`, with the wall it has to clear).

**This is the fault that cost plates 1, 2 and 3 the first time** (2026-09-22
log entry, "the screw base bumps the edge of the body"): the perimeter
bosses overlapped their shell's wall by up to 2 mm, so the two halves
physically could not close. `A1`/`A2` are cut at the single tightest boss
on the whole panel — the one narrow enough that this build gives it its
own smaller boss diameter (`PERIM_BOSS_OD_TIGHT`) instead of the standard
one, because there isn't room for the standard size there.

**Pass:** press `A1`'s boss into `A2`'s wall opening by hand. It should
seat flush with a firm push, no sanding, no visible gap. A washer or the
flat of an M3 screw head should sit flat against the boss face once seated.

**Fail:** the boss won't seat, or seats only after removing material —
meaning the real face plate and shell won't close either, and you should
hold off printing plates 1 and 2 until the CAD is adjusted (and this coupon
reprinted and re-checked) rather than find out after a 10-hour print.

### B — Column seam (`B1` + `B2` + `B3`)

**Tests:** two faults at once, both from the fix that shipped as PR #12 —
the seam bolt's own path and bore, and a perimeter screw that used to run
straight into the seam's internal support rib. `B1` is the back shell,
column half (`02b`); `B2` is the face plate, column half (`01b`); `B3` is a
matching strip cut from the screen-side back shell (`02a`), carrying the
other half of the seam bolt holes.

**This is the fault found on 2026-09-24**, right after plate 3 was
reprinted for the *first* fix and finally seated: three of the four column
screws ran straight into the seam's own support boss/rib block (measured
at the time as 49.5 mm of solid material blocking the screw), and — a
separate, worse problem found while fixing that — **all four seam bolt
holes were completely filled in**, with no bore at all, so the two modules
could not be bolted together no matter what. Both faults are inside this
one coupon.

**Pass:** thread an M3 screw through `B2`'s perimeter hole into `B1`'s
boss — it should turn freely all the way to the boss, no resistance
partway in (that resistance is exactly what "running into the rib"
felt like on the real print). Separately, pass an M3 bolt through `B3`'s
clearance hole and into `B1`'s seam boss — it should also thread in
freely, and you should be able to see daylight through the bore from the
back before you do (the bore existing at all was the second fault).

**Fail:** either screw binds, stalls, or won't start — meaning the real
column module has the same fault, and printing plate 3 (or the screen
module's plate 2, for the seam bore) again would be reprinting a known bad
fit.

### C — Band mount (`C1` + `C2` + `C3`)

**Tests:** the clamped stack that holds the backlit band together — one
M3 screw through the diffuser, then the insert, then into a boss on the
face plate, with all three meant to sit flush with **zero** gap, not just
close. `C1` is the face-plate corner with the boss (`01a`); `C2` is the
matching corner of the ignition-variant band insert (`04a`); `C3` is the
matching corner of the band diffuser (`05`).

**This is the fault found on 2026-09-23**: the band insert and diffuser
originally had no working mounting features at all. The four mounting
holes landed 1.0 mm outside the parts' own outline (so the "hole" removed
0.00 mm³ — just a corner nick, not a hole), and even once holes existed,
the insert floated 0.4 mm behind the boss it bolted to and the diffuser a
further 1.0 mm behind that — a screw could only bow the stack, not clamp
it.

**Pass:** stack `C3` on `C2` on `C1` (diffuser, then insert, then face
plate, in that order — this is a "one screw through everything" test, not
three loose fits) and drive one M3 screw through all three. The stack
should pull down flat with normal screw torque — no visible gap between
any two layers, and the screw shouldn't bottom out or spin freely before
the stack is tight.

**Fail:** a gap remains between any two layers even at full screw
tightness, or the screw doesn't reach thread in the boss — meaning the
real band assembly (plates 7, 8/9) has the same problem, and the insert or
diffuser needs another CAD pass before reprinting them.

## What each coupon is made of, and why the label is where it is

Every coupon has a small debossed label (`A1`, `B2`, `C3`, ...) cut into
one flat side, so pieces can't get mixed up on the bench once there are
eight of them loose in a box. The label is always on a face the box-cut
itself created, well away from the screw hole, boss, or bore the coupon
exists to test, and away from the face that sits on the print bed — it's
there to identify the piece, not to be felt or seen in the fit test itself.

## Filament and plates

`bambu/dial-panel-coupons.3mf` — **not** the release project
(`bambu/dial-panel-hw-2015.3mf`, which is what everyone else prints):

| Plate | Coupons | Filament |
|---|---|---|
| 1 | A1, A2, B1, B2, B3, C1, C2 | black PLA (same as the real body parts) |
| 2 | C3 | clear PETG (same as the real diffuser — it can't share a plate with PLA) |

Every coupon keeps its parent part's own print orientation (from
`cad/print_rotations.json`) — the same face-down-on-the-bed logic the real
parts use, so a coupon's overhangs and first layer are the same test as the
real print, not a different one.

Measured: **1 h 20 m** total for both coupon plates, against **10 h 36 m**
for plates 1 + 2 + 3 — about 8x faster to find out whether a fix actually
worked.

## If a coupon fails

Don't reprint the coupon with the same CAD and expect a different result —
it's cut from the same STEP file the real part uses, so the same fault is
in both. Fix the geometry in `cad/generate_parts.py`, regenerate everything
(`freecadcmd cad/generate_parts.py`), regenerate the coupons
(`freecadcmd cad/coupons.py`), and reprint the coupon plate before
committing to the full plate. That loop is the entire point of these
existing.
