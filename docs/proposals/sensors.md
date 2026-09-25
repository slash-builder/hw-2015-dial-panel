# Proposal — ambient sensors on the free I2C bus

> **Status: PROPOSAL. Awaiting review. Nothing here is built.**
> No CAD, BOM, `config.txt` or wiring file is changed by this branch. Every
> code block below is a *proposed* diff, shown so it can be argued with, not
> applied. Reviewer list and open questions are at the bottom.

**Asked by DJ, 2026-09-24:** *"couldn't we include some sensors in the package
via the remaining open GPIO pins? Maybe temp and humidity at minimal."*

---

## Recommendation in one paragraph

Yes. Add an **SHT4x** temperature/humidity sensor, and — argued separately
below — a **BH1750** ambient light sensor, both on the untouched primary I2C
bus (GPIO2/GPIO3, header pins 3 and 5). Each is a single stock-overlay line, so
the build keeps its "four stock drivers, nothing to compile" promise. The pin
budget is not the constraint and never was. **The constraint is thermal:** a Pi
5, an Active Cooler and a 7" display inside a near-sealed PLA box on a wall
will make internal air run well above room temperature, and a sensor that
reads the box instead of the room is worse than no sensor at all. The fix is a
**dedicated sensor well in the control column** — a small plenum, isolated
from the main cavity by a printed baffle, breathing outside air through a
down-facing intake in the bottom wall and a low louver row in the outer side
wall. (Not the rear wall: `02b`'s rear face is the wall-bearing surface, so a
rear opening would vent into drywall — see §3.) That is a real CAD change to `02b` (and, for the light sensor, to `01b`),
which reopens the verification suite and needs those plates reprinted. It is
cheap now and expensive after the repo goes public.

---

## 1 · The pin budget is not the constraint

`docs/wiring.md` currently commits these header pins:

| Used | Pin | Function |
|---|---|---|
| GPIO17 / GPIO27 / GPIO22 | 11 / 13 / 15 | dial A, dial B, dial push |
| GPIO18 / GPIO19 / GPIO21 | 12 / 35 / 40 | I2S BCLK, LRCLK, DIN |
| GPIO10 | 19 | WS2812 data |
| power / ground | 1, 2, 4, 6, 9, 34, 39 | 3V3, 5V ×2, GND ×4 |

**GPIO2 and GPIO3 — pins 3 and 5, `i2c_arm` / `i2c-1` — are completely
unused**, and the Pi already carries the bus's 1.8 kΩ pull-ups on board. GPIO4
is also still free (`no-sdmode` was chosen in `config.txt` specifically to keep
it), as are the UART pins and a dozen others.

The important part: **I2C is a bus, not a pin pair per device.** Two pins carry
every sensor discussed here, and would carry several more. Nothing in this
proposal spends a GPIO that a future feature might want.

### No address or bus conflict with the display

The Touch Display 2's touch controller sits on the **DSI connector's own I2C**,
not the 40-pin header bus. `i2c-1` is ours alone. Proposed addresses:

| Device | Address | Clash? |
|---|---|---|
| SHT4x | `0x44` | none |
| BH1750 | `0x23` | none |

### The overlays already exist

Checked against `raspberrypi/firmware` `boot/overlays/README` on 2026-09-24 —
the `i2c-sensor` overlay carries, among ~60 others:

```
sht4x    Select the Sensirion SHT4x temperature and humidity sensors.
         Valid addresses 0x44-0x45, default 0x44
aht20    Select the Aosong AHT20 temperature and humidity sensor
bme280   Select the Bosch Sensortronic BME280. Valid addresses 0x76-0x77
bh1750   Select the Rohm BH1750 ambient light sensor.
         Valid addresses 0x23 or 0x5c, default 0x23
scd4x    Select the Sensirion SCD40/41 CO2 sensors.
```

So this is a kernel IIO device, no Python library, no `pip`, nothing to
compile — the same standard this build already holds itself to.

> **One thing to verify on the bench, not assume:** loading `i2c-sensor` twice
> for two *different* sensors is normal practice, but it should be confirmed
> with `i2cdetect -y 1` and two live IIO nodes before it goes in a build doc.
> This proposal does not claim it works; it claims it is expected to and must
> be tested.

---

## 2 · The thermal problem is the whole design

The screen module (`02a`) holds the Pi 5, the Active Cooler and the display.
Its only openings to outside air are the four cooler side-exhaust vents:

```
VENT_N=4, VENT_W=2.0, VENT_H=12.0  ->  96 mm² total open area
```

That is a near-sealed box around roughly 7–15 W of continuous dissipation,
hung flat against a wall so one whole face is in a thermal boundary layer.
Internal air will sit substantially above room temperature.

Put an SHT4x on a short jumper anywhere in that module and the device reports
the inside of itself. A panel that is wrong about the room by a wide margin
would sit badly next to the mic cut, which this build deliberately made a
**real VBUS disconnect** rather than a software mute. The same honesty standard
applies to a number on a screen.

**Do not quote a rise figure until it is measured.** This proposal deliberately
does not put an estimate in a build document. Measuring it is a new
verification item (§7).

### The column module is the right home, and mostly for free

The control column (`02b`) contains no heat source at all — the KY-040, the
rocker, and the USB mic dongle. Everything below the rocker is empty. From the
repo's own `cad/assembly_placements.json` (assembly coordinates, mm):

| Envelope | X | Y (depth) | Z (height) |
|---|---|---|---|
| `ky040-module` | 94.56 … 124.76 | 6.00 … 22.60 | 112.93 … 135.56 |
| `rocker-body` (incl. terminals + wiring reserve) | 99.01 … 120.31 | 3.00 … 33.00 | 64.04 … 79.24 |
| `mic-dongle` | 99.66 … 119.66 | 5.00 … 58.30 | 184.54 … 194.54 |
| `wash-led-run-column` | 69.66 … 149.66 | 63.86 … 67.36 | −2.50 … 7.50 |
| `pi5-cooler` (**other module**) | −87.50 … −2.50 | 18.46 … 39.76 | 102.12 … 158.12 |

**Free lower cavity in `02b`:** X 67.66 … 151.66 (84 mm) · Y 3.00 … 63.56
(60.6 mm) · Z 3.00 … 64.04 (61 mm). The wall-wash channel is a pocket in the
*outer* rear face, so it does not intrude on that volume — but it does
constrain where a rear cut may go (§3).

A sensor sited at roughly X 110, Z 25 sits about **136 mm** from the nearest
corner of the Pi 5 cooler envelope, **in a different printed module**, across a
bolted seam. That is real separation, obtained for free from a split the bed
width already forced.

### But the column is not a working chimney as built

The five mic ports in the column's top wall are the only outside-air opening
it has:

```
MIC_PORT_N=5, MIC_PORT_R=1.3  ->  26.5 mm² total open area
```

26.5 mm² will not drive useful convection through a 190 mm column, and those
ports cannot simply be enlarged: they are the microphone's acoustic path and
they are a deliberate element of the concept sheet's front.

So **do not rely on a whole-column chimney.** Give the sensor a small plenum of
its own instead.

---

## 3 · Proposed mechanical change — a sensor well in `02b`

A **sensor well**: a printed pocket in the lower column, separated from the
main cavity by a thin baffle, open to outside air at two points. The sensor
then sits in what is effectively room air, touching the enclosure only through
a thin wall — which is what a decent wall thermostat does.

### First, a correction worth recording: there is no gap behind the column

An earlier draft of this proposal vented the well backwards into the french
cleat's standoff gap. **That is wrong, and the repo's own numbers say so.**
`BACK_PLANE_Y = 66.56 mm` *is* the wall plane, and `cad/README.md`'s
wall-cleat engagement table records:

| Surface | World Y | |
|---|---|---|
| Cleat rear (wall-mounting) face | **66.56** | `== BACK_PLANE_Y` |
| `02a` bare shell, back-most | 54.56 | recessed — a real 12 mm standoff |
| `02a` + rail, back-most | 66.56 | `== BACK_PLANE_Y` |
| **`02b` back-most (`COLUMN_PANEL_D`)** | **66.56** | **`== BACK_PLANE_Y` — flush** |

So the **column module's rear wall is the wall-bearing surface.** Only the
screen module has an air gap behind it, and that gap is behind the hot module,
which is the last place to vent a sensor. Any rear opening in `02b` vents into
drywall. The well breathes through the bottom and the side instead.

```
              column module 02b, front view (schematic)
        seam ─┐                                     ┌─ outer right edge
              │        ░░░ main cavity ░░░          │
      Z≈45    ├──────────── baffle ────────────────┬┤
              │      [ SHT4x on 2 bosses ]         ││◄─ (b) exhaust louvers,
      Z≈12    │            sensor well             ││   outer SIDE wall, Z≈30-45
              └──┬───┬───┬───┬─────────────────────┴┘
                 ▼   ▼   ▼   ▼  (a) down-facing intake, bottom wall
```

**(a) Intake — down-facing louvers in the bottom wall.** Invisible on a
wall-hung panel, dust-shedding, and the coolest air available. Sited at
Y ≈ 8 … 30, which keeps them clear of the wash-LED channel's pocket at
Y 63.86 … 67.36.

**(b) Exhaust — a louver row in the outer (right) side wall** at X = 154.66,
Z ≈ 30 … 45. That gives roughly 30–40 mm of stack height above the intake,
enough for a small plenum to turn over passively. It is invisible from the
front and reads only as fine slots on the panel's right edge.

> **Fallback if design says no to a visible side louver:** put *both* openings
> in the bottom wall, separated in Y. Stack effect then drops to almost
> nothing and exchange is diffusion- and room-draught-driven — probably still
> adequate at the response times a wall panel needs (minutes, not seconds),
> but that is exactly what the soak test in §7 has to settle. Do not assume it.

**Sensor mount:** two bosses at X ≈ 110, Z ≈ 12 … 40, rising from the rear
wall. Envelope reserved **30 × 25 × 15 mm**, which covers the common SHT4x
breakouts; the BOM must pin one exact part before CAD is cut.

### It complies with the print-orientation rules already learned here

`02b` prints **back-wall down** (round 5). Under that orientation, both
openings land in walls that are *vertical* during printing — which is the
easy case, and avoids the bed-face question entirely:

| Feature | Prints as | Verdict |
|---|---|---|
| Sensor bosses + baffle | columns rising from the bed | self-supporting by construction — the round-5 convention exactly |
| Bottom-wall intake louvers | small holes in a vertical wall | ~2 mm bridges, far inside the >10 mm unsupported-ledge limit |
| Side-wall exhaust louvers | small holes in a vertical wall | same |

> **No feature in this proposal may be a pocket in the bed face.** That is what
> failed on plate 1 (the trim rebate printing over air) and what still causes
> the wash channel's reported stringing. Staying out of the rear wall removes
> the temptation entirely.

## 4 · Sensor selection

| Sensor | Part | ~Cost | Why |
|---|---|---|---|
| **Temp + RH** | **SHT4x** (SHT40/41/45) | $7–10 | Best accuracy per dollar, very low self-heating, stock overlay. |
| Temp + RH (budget swap) | AHT20 | $4–6 | Also stock overlay. Lower accuracy; acceptable fallback. |
| **Ambient light** | **BH1750** | $5–8 | Same two pins, same overlay. Argued in §5. |

**Rejected, with reasons:**

| Rejected | Why not |
|---|---|
| **BME280** | Pressure earns nothing on a wall panel, its RH channel drifts, and it self-heats more than an SHT4x. Being a 3-in-1 is not a reason. |
| **SCD40/41 (CO2)** | ~$50, and needs genuine air exchange. In this enclosure it would produce numbers nobody should trust. Breaks the one-accessible-cart promise on its own. |
| **SPS30 (PM2.5)** | ~$45 plus a fan and a duct. Not this device. |
| **VOC / gas (SGP30, CCS811)** | Uncalibrated indices that people over-trust. |
| **LD2410 mmWave presence** | Genuinely attractive — wake-on-approach, and the UART pins are free. But whether the panel watches the room is an interaction-model and privacy decision, not a BOM line. **Explicitly out of scope here**; raise it separately with DJ and `creative-director`. |

---

## 5 · The light sensor, argued separately

Ambient light arguably earns its place more than temperature does. A 7" panel
at fixed brightness in a hallway or bedroom is the first complaint this device
will get, and auto-dim is what makes hardware feel finished. It is the same two
pins, the same overlay, and about $7.

**It costs more than the temp sensor does, though, because it needs a hole in
the face.** A light aperture in `01b` (the column face plate, at X ≈ 110, low,
below the rocker) is a **visible change to the xxx5 front** and therefore needs
industrial-design sign-off, not just engineering.

Constraints if it goes ahead:

- **Plain through-hole only, plug retained from behind.** A front rebate for a
  clear PETG plug is precisely the plate-1 failure. Retain it with a
  cavity-side boss or clip.
- **Optical contamination must be bench-checked.** The band LEDs are in the
  *other* module (X −130.66 … 40.66), so a column aperture is clear of them by
  construction. The column's own wall-wash LEDs fire rearward at the wall, but
  bounce could still reach a front aperture. If it does, sample with the wash
  LEDs briefly off — and if that is unacceptable, defer the light sensor.

**If the face cannot take a hole, drop the BH1750 and ship temp/RH alone.** The
temperature sensor needs no change to any visible surface, and that asymmetry
should decide the argument if design says no.

---

## 6 · Proposed diffs — NOT APPLIED

### `docs/config.txt` would gain

```
# Ambient sensors on the primary I2C bus (GPIO2/GPIO3, header pins 3/5).
# Optional: omit both lines if the sensor well is left unpopulated.
dtparam=i2c_arm=on
dtoverlay=i2c-sensor,sht4x        # temp + humidity, 0x44
dtoverlay=i2c-sensor,bh1750       # ambient light, 0x23
```

(`dtparam=i2c_arm=on` is belt-and-braces — the overlay is expected to bring the
bus up on its own. Confirm on the bench; drop the line if redundant.)

### `docs/wiring.md` would gain a section

Four female-to-female jumpers for the first sensor; the second daisy-chains
3V3/GND off the first, or takes pin 17 (3V3, free) and pin 25 (GND, free).

| Sensor pad | Pi pin | Pi name | Colour |
|---|---|---|---|
| `VIN`/`3V3` | **17** | 3V3 | orange |
| `GND` | **25** | GND | black |
| `SDA` | **3** | GPIO2 | cyan |
| `SCL` | **5** | GPIO3 | cyan |

Plus the test step, matching the existing per-section pattern:

```
i2cdetect -y 1                    # expect 0x44 (and 0x23)
cat /sys/bus/iio/devices/iio:device*/name
```

> Breakouts generally ship with loose headers — same soldering note the amp
> already carries.

### `bom/bom.csv` would gain

Two rows, **with the multi-source treatment DJ required on 2026-09-21** so the
BOM does not read as an Amazon ad (Adafruit direct is the natural second
source, and is often the better part):

```
19,Temp/humidity sensor,SHT4x (SHT40/41/45) I2C breakout,1,1,...,~8.00,1,8.00,TO RESEARCH,"Optional. 0x44. Mounts in the 02b sensor well. Adafruit SHT41 STEMMA QT as second source."
20,Ambient light sensor,BH1750 I2C breakout,1,1,...,~7.00,1,7.00,TO RESEARCH,"Optional, pending face-aperture sign-off. 0x23."
```

Both rows are **`TO RESEARCH`** — no part is pinned and no price is verified.
Pinning them is work for after sign-off, and CAD cannot cut the well envelope
until the SHT4x breakout is chosen.

### The BOM gains its first *optional* tier

That needs a convention decided, not invented in a commit: does a builder who
skips the sensors get a different `config.txt`, or the same one with the lines
commented? Does `stl/` ship a blanking plug for the intake? **Open question
(§9).**

---

## 7 · Verification impact

The build's standard is verified, not asserted — 31/31 feature probes, 27/27
interference pairs, sound path, cleat engagement, print-orientation and
bed-face scans, nine plates slicing warning-free. This change reopens that.

**Must be re-run:**

- feature probes for both louver rows, the baffle and the bosses
- **exhaustive all-pairs interference**, specifically the sensor envelope
  against: the rocker body + terminals + wiring reserve (Y 3 … 33,
  Z 64.04 … 79.24), the coiled mic extension, the seam bosses, the perimeter
  mounts, the wash-LED channel pocket, and the outer side wall's own
  perimeter-mount bosses
- bed-face / downward-facing-surface scan on `02b` (and `01b` if the aperture
  goes in) — the >10 mm rule
- slice check on the affected plates, then **reprint them**

**New verification item — a class this repo does not yet have:**

- **Thermal soak.** Assembled, wall-mounted, idle and under load, logged
  against a reference thermometer and hygrometer in the same room, for long
  enough to reach steady state. This produces the offset in §8 and it is the
  measurement that decides whether the feature ships at all.
- **Optical check** for the light aperture, if it goes in (§5).

---

## 8 · The accuracy claim, and the calibration that earns it

**A documented offset is mandatory, not optional.** Even with the well done
properly, some rise is unavoidable: the sensor is bolted to a warm object.
Every commercial wall thermostat ships with an offset for exactly this reason.

This proposal also adds `docs/sensors.md` at merge time, containing:

1. the calibration procedure (reference instrument, soak time, logging, where
   to put the resulting offset)
2. **the honest accuracy claim the enclosure can actually support** — something
   of the form *room-indicative, ±1 °C after calibration* once soak data
   exists. **Never the SHT4x's datasheet ±0.2 °C / ±1.8 % RH**, which is a
   figure for a sensor in free air and which this box destroys.
3. the note that **relative humidity inherits the temperature error**: RH
   measured in air warmer than the room reads low against the room's true RH.
   The well fixes both or neither.

Quoting a datasheet number a device cannot deliver is the same failure as a
mic switch that only mutes in software. The number goes in the docs with its
real error bar, or the feature does not ship.

---

## 9 · Open questions and who signs off

None of this proceeds on engineering's word alone. Buy-in needed from:

| Who | Question |
|---|---|
| **DJ** | Go/no-go, and whether the light sensor is in or out of the first release. |
| `industrial-designer` / `creative-director` | **Can `01b`'s front face take a light aperture?** Do down-facing intake louvers and a low louver row on the outer right edge affect the xxx5 read? (The intake is invisible; the side louvers are not, though they sit on an edge, not the face.) |
| `open-hardware-release-engineer` | Owns the pipeline: brief the CAD, re-run verification, re-print, sequence it against the pending round-two prints. Also owns the new thermal-soak verification item. |
| `mechanical-cad-engineer` | Implements the well, louvers, slot, bosses and the `01b` aperture; verifies by reading exported geometry back, not by the script exiting cleanly. |
| `quickring-pm` / `messaging-architect` | **Where do the readings go?** This turns the Dial from a control surface into a sensor endpoint on the household fabric. Does it publish a Hearth feed? Does the gateway consume it? Does Courier surface it? Not decided here, and the answer may change the firmware scope more than the hardware. |
| `thunderhead-pm` | Does an ambient-sensing wall panel set a precedent the device ladder should follow, or is this Dial-specific? |
| `brand-architect` | Does "it senses the room" change what the device may be *called* or claimed to do in public copy? |
| `revenue-architect` | Only if sensing is ever framed as a paid or tiered capability. Probably not applicable; listed so it is consciously skipped. |

**Unresolved regardless of sign-off:**

1. The exact SHT4x breakout — CAD cannot cut the well envelope until one is
   pinned, and the two BOM rows stay `TO RESEARCH` until then.
2. The optional-BOM convention (§6).
3. Whether two `i2c-sensor` overlay lines coexist cleanly — bench, not
   assumption (§1).
4. The real offset, which only the soak test produces (§7, §8).

---

## 10 · Sequencing — why this is a now-or-never-cheap change

The repo is still **private**, plate 1 and plate 2's fixes are in, and round
two of prints has not happened. Software has not started.

Folding a sensor well into `02b` at this moment costs one more CAD pass on
plates that are **already going to be reprinted anyway**. Adding it after the
STLs are public means every early builder is holding an obsolete `02b`, and an
open hardware project's worst failure mode is a silent breaking revision to a
part people have already printed.

If sensors are going in at all, they go in **before the repo goes public**. If
the answer is no, this file gets deleted with a line saying so, and that is a
perfectly good outcome — it cost one branch.

---

## Provenance

- Pin assignments and the "four stock drivers" standard: this repo's
  `docs/wiring.md` and `docs/config.txt`.
- Overlay parameters: `raspberrypi/firmware` `boot/overlays/README`, the
  `i2c-sensor` section, read 2026-09-24 — the same source `docs/wiring.md`
  already cites.
- Every dimension and envelope: computed from this repo's own
  `cad/generate_parts.py` constants and `cad/assembly_placements.json`, not
  estimated.
- Print-orientation and bed-face rules: `cad/README.md` rounds 5, 6 and 8, and
  `docs/print-log.md`.
- Thermal rise: **deliberately unquantified.** It is a measurement, not an
  estimate, and §7 files it as a verification item.
