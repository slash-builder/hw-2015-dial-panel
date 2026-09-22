# Wiring

Everything plugs into the Raspberry Pi 5. One splice (the mic cut) and a few
solder joints (amp headers, the optional level shifter, the LED feed) are the
only soldering.

## Pi 5 40-pin header

| Pin | Signal | Goes to |
|---|---|---|
| 1 | 3V3 | Dial (KY-040) **+** — **3.3 V only**; its pull-ups would put 5 V on a GPIO |
| 2 | 5V | Touch Display 2 power, red (cable in the display box) |
| 4 | 5V | Y-splice: LED strip 5 V + amp Vin (+ level-shifter VCC) |
| 6 | GND | Touch Display 2 power, black |
| 9 | GND | Dial GND |
| 11 | GPIO17 | Dial **CLK (A)** |
| 13 | GPIO27 | Dial **DT (B)** |
| 15 | GPIO22 | Dial **SW** (the push) |
| 12 | GPIO18 | Amp **BCLK** |
| 35 | GPIO19 | Amp **LRC** |
| 40 | GPIO21 | Amp **DIN** |
| 39 | GND | Amp GND |
| 19 | GPIO10 | Level shifter 1A → 1Y → 330–470 Ω → LED **DIN** (or straight to DIN without the shifter) |
| 34 | GND | LED GND + level-shifter GND |
| 7 | GPIO4 | **Leave free** |

- **Cooler:** the Pi's FAN header, not the 40-pin header.
- **Display data:** the standard-to-mini FPC from the display box, into a Pi 5 MIPI connector.
- **Speaker:** amp + / − terminals.

## The mic cut

The mic's power runs through the rocker, so **OFF physically removes the
microphone** — the Pi can't see it, and no software can turn it back on.

1. Cut the USB extension about 10 cm from the female end and strip the jacket.
2. Cut **only the red wire (VBUS)**. Leave black, white, green and the shield continuous.
3. Solder the two red ends to the rocker's two blades; heat-shrink each joint.
4. Male end → a Pi USB port. Female end → the mic cradle behind the top-edge ports. Mic → female end.

## Power budget

The Pi 5's 5 V pins carry the display (~0.3–0.6 A), the LEDs and the amp.
52 LEDs at full white would draw ~3 A — too much — so `config.txt` caps them
at `brightness=64` (~0.8 A worst case). Keep that cap. Use 22 AWG for the LED
feed and solder the Y-splice rather than trusting one Dupont contact. Nothing
else goes on the 5 V pins.
