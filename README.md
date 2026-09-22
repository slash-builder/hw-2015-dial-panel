# Dial Panel · hw-2015

An open hardware device from [SlashBuilder](https://github.com/slash-builder). One device, one repo.

A wall-mounted smart-home panel you print yourself and drive with one dial.
Turn to move, push to open, and it goes back home on its own after a few
seconds. No back button, no smudged glass. A hardware switch cuts the
microphone's power.

> **Status: pre-release.** The CAD is complete and verified (below), but
> nothing has been printed or fitted yet, and the dashboard software isn't
> written. Don't print this expecting a finished product yet.

![Nightfall](docs/drawings/dial-panel-nightfall.svg)

## Pick a team

One release, two looks. Choose once when you build; a Dial Panel keeps its
team for life. The body, trim, dial and gold tab are identical in both;
only the light changes.

| | **A · IGNITION** | **B · NIGHTFALL** |
|---|---|---|
| It's… | a sunrise | a starfield |
| Print | `stl/ignition/04a-band-insert-ignition.stl` | `stl/nightfall/04b-band-insert-nightfall.stl` |
| Light | warm torch | violet, with a cyan grid |

Drawings: [Ignition](docs/drawings/dial-panel-ignition.svg) ·
[Nightfall](docs/drawings/dial-panel-nightfall.svg). More in
[docs/teams.md](docs/teams.md).

## What you need

**Electronics: one Amazon cart.** [`bom/bom.csv`](bom/bom.csv) lists every
part with a checked listing, pack size and per-build cost: a Raspberry Pi 5,
the official 7" Touch Display 2, a KY-040 push dial, a KCD1 rocker, a
MAX98357A amp, a 40 mm speaker, a USB mini mic and WS2812B LEDs.
Roughly **$320 per build** (≈ $450 cart, with spare parts from multi-packs),
prices as of 2026-09-21. Buying the Pi and display from an approved reseller
is cheaper; the BOM notes where.

<!-- CART-LINK:BEGIN -->
**[Add the full BOM to your Amazon cart](https://www.amazon.com/gp/aws/cart/add.html?ASIN.1=B0G4R8TSLN&Quantity.1=1&ASIN.2=B0DM24QFCF&Quantity.2=1&ASIN.3=B0B7NXBM6P&Quantity.3=1&ASIN.4=B07F26CT6B&Quantity.4=1&ASIN.5=B08683RMVY&Quantity.5=1&ASIN.6=B0DPJRLMDJ&Quantity.6=1&ASIN.7=B01LN8ONG4&Quantity.7=1&ASIN.8=B01KLRBHGM&Quantity.8=1&ASIN.9=B0CDC3KQN1&Quantity.9=1&ASIN.10=B01CDTED80&Quantity.10=2&ASIN.11=B00XW2L39K&Quantity.11=1&ASIN.12=B0DDWS7BTS&Quantity.12=1&ASIN.13=B0GRV5NW7Q&Quantity.13=1&ASIN.14=B01EV70C78&Quantity.14=1&ASIN.15=B01MFA3OFA&Quantity.15=1&ASIN.16=B0D7ZYCVTY&Quantity.16=1&ASIN.17=B0C6QFDQWT&Quantity.17=1&ASIN.18=B0B12W69HT&Quantity.18=1&ASIN.19=B085TGGV3L&Quantity.19=1)** (19 listings, 20 items)
<!-- CART-LINK:END -->

The button adds every Amazon listing in the BOM, including the four filaments,
so remove anything you already own. The Pi kit already includes the power
supply and cooler. Items that are out of stock get skipped, so check the cart
against [`bom/bom.csv`](bom/bom.csv). The link carries **no affiliate tag**.
Regenerate it with `python3 bom/cart_link.py` whenever the BOM changes.

**A printer** with a 250 × 210 mm bed or larger (Prusa MK4, Bambu A1, and
similar). Every part prints **without supports**.

**Filament:** matte black PLA (~500 g), silver silk PLA (~75 g), yellow PLA
(a few grams) and clear PETG (~40 g).

**Tools:** a soldering iron (heat-set inserts, amp headers, one wire splice),
a 2.5 mm hex key, and wire strippers.

## What you print

| File | Part | Material | Qty |
|---|---|---|---|
| 01a, 01b | face plates: screen, column | matte black PLA | 1 each |
| 02a, 02b | back shells: screen, column | matte black PLA | 1 each |
| 03 | screen trim | silver silk PLA | 1 |
| 04a **or** 04b | band insert: ember **or** starfield | matte black PLA | 1 |
| 05 | band diffuser (with speaker opening) | clear PETG | 1 |
| 06 | knob | silver silk PLA | 1 |
| 07 | gold tab | yellow PLA | 1 |
| 08 | speaker back-cup | matte black PLA | 1 |
| 11 | wall cleat | matte black PLA | 1 |

The panel is two modules (screen and control column) that bolt together:
the 7" screen plus the dial is wider than any common print bed.
Assembled it's **309 × 200 mm and 67 mm off the wall** (85 mm to the knob).

## Build

1. **Print** the parts above. Orientation per part is in [`cad/README.md`](cad/README.md).
2. **Inserts:** heat-set the M3 inserts. Every screw goes in from the back, so the face stays clean.
3. **Screen module:** fit the display, with the Pi 5 and cooler on its back, the amp and the speaker (back-cup screwed on behind it).
4. **Column:** fit the dial (held by its own nut), the rocker, the gold tab and the mic cradle.
5. **Wire it:** follow [`docs/wiring.md`](docs/wiring.md), including the one-wire mic-cut splice. Then append [`docs/config.txt`](docs/config.txt) to the Pi's `/boot/firmware/config.txt`.
6. **Close up:** fit your team's band insert and the diffuser, lay in the LED strips, screw the face plates on, and bolt the two modules together.
7. **Hang it:** screw the cleat to the wall and drop the panel onto it.

The full step-by-step, with the fastener count for each joint, is the
"Assembly order" in [`cad/README.md`](cad/README.md).

## How it's checked

The CAD in `cad/` is parametric FreeCAD and regenerates every file. Every run checks:

- **Every part:** one clean solid that fits the bed.
- **Openings:** every opening exists (31/31), and there are no unintended ones.
- **Fit:** nothing collides in the assembled position (27/27 part pairs). That
  includes Raspberry Pi's own display model and every screw's full length.
- **Sound:** the path from the speaker through the band stays at least 25% open,
  for both inserts.
- **Hanging:** the wall cleat engages 16.7 mm, and the panel hangs flat against the wall.

To regenerate, download Raspberry Pi's Touch Display 2 STEP into
`cad/vendor/` (see `cad/vendor/README.txt`; it's their file, so it isn't
included here) and run
`freecadcmd cad/generate_parts.py`.

## Known limits

- **Silver silk isn't chrome.** It reads metallic, not mirror.
- **The gold tab is fixed in place** rather than revealed only when the mic is live. The rocker's position shows the mic state.
- **Unconfirmed part dimensions:** a few sizes come from listings and are marked in `cad/README.md`. They include the dial's shaft flat, the rocker's clip thickness and the speaker's depth. Measure your parts; each is a single parameter.
- **LED brightness is capped at about 25%.** Full brightness would pull more current than the Pi's 5 V pins can supply.

## Repository layout

```
bom/bom.csv          every part, with a checked Amazon listing
cad/                 parametric FreeCAD source + STEP exports + verification notes
cad/vendor/          where Raspberry Pi's display STEP goes (not included)
stl/common/          parts every build prints
stl/ignition/        the A · IGNITION band insert
stl/nightfall/       the B · NIGHTFALL band insert
docs/                wiring, config.txt, choosing a team, release drawings
```

## Contributing

Issues and pull requests are welcome, especially fit reports from real
prints (printer, filament, what fit and what didn't). Geometry changes go in
`cad/generate_parts.py`, then regenerate. A change isn't done until every
check in the run still passes.

## License

Code (`cad/generate_parts.py`, `docs/drawings/*.py`) is **Apache-2.0**. Design
files (CAD, STL, drawings, BOM, docs) are **CC-BY-4.0**. See
[LICENSE](LICENSE). Raspberry Pi's display model is theirs and isn't
included.
