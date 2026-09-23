"""
Generate the wiring diagrams in docs/wiring/.

  header-map.svg   every pin of the Pi 5 header, with the ones we use called out
  encoder.svg      KY-040 dial -> Pi
  audio.svg        MAX98357A amp -> Pi, and the speaker
  leds.svg         WS2812B strips -> level shifter -> Pi
  mic-cut.svg      the one soldered splice: the rocker in the mic's USB power
  overview.svg     what connects to what, at a glance

Hand-drawn data, not projected from CAD: pin numbers and module pinouts are
transcribed from the sources listed in docs/wiring.md. Colours match the
recommended Dupont wire colours so a photo of a finished build looks like
the diagram.

    python3 docs/wiring/build_diagrams.py
"""
import os

HERE = os.path.dirname(os.path.abspath(__file__))

# palette (xxx5): dark ground, legible ink, one accent per signal class
V950, V900, V800, V700, V600, V400, V300, V200, V100, V050 = (
    "#05060C", "#0A0C16", "#101426", "#171C33", "#222842", "#4C5573", "#6E7894", "#9AA3BA", "#C6CCDB", "#E6E9F1")
RED, ORANGE, BLACK_W, CYAN, VIOLET, GOLD, GREEN, WHITE_W = (
    "#FF2A3C", "#FF7A1A", "#6E7894", "#22E8E0", "#9E6BFF", "#F5C842", "#3FD07A", "#E6E9F1")
MONO = "'IBM Plex Mono', Menlo, monospace"
SANS = "'Space Grotesk', 'Helvetica Neue', Arial, sans-serif"
DISPLAY = "'Archivo', 'Archivo Black', Arial, sans-serif"

# Raspberry Pi 40-pin header (Pi 5 = the standard 40-pin map)
PINS = [
    (1, "3V3"), (2, "5V"), (3, "GPIO2"), (4, "5V"), (5, "GPIO3"), (6, "GND"),
    (7, "GPIO4"), (8, "GPIO14"), (9, "GND"), (10, "GPIO15"), (11, "GPIO17"), (12, "GPIO18"),
    (13, "GPIO27"), (14, "GND"), (15, "GPIO22"), (16, "GPIO23"), (17, "3V3"), (18, "GPIO24"),
    (19, "GPIO10"), (20, "GND"), (21, "GPIO9"), (22, "GPIO25"), (23, "GPIO11"), (24, "GPIO8"),
    (25, "GND"), (26, "GPIO7"), (27, "ID_SD"), (28, "ID_SC"), (29, "GPIO5"), (30, "GND"),
    (31, "GPIO6"), (32, "GPIO12"), (33, "GPIO13"), (34, "GND"), (35, "GPIO19"), (36, "GPIO16"),
    (37, "GPIO26"), (38, "GPIO20"), (39, "GND"), (40, "GPIO21"),
]
# pin -> (wire colour, what it goes to)
USED = {
    1: (ORANGE, "Dial + — 3.3 V ONLY"),
    2: (RED, "Display power, red"),
    4: (RED, "5 V: LEDs + amp"),
    6: (BLACK_W, "Display power, black"),
    9: (BLACK_W, "Dial GND"),
    11: (CYAN, "Dial CLK (A)"),
    12: (VIOLET, "Amp BCLK"),
    13: (CYAN, "Dial DT (B)"),
    15: (GOLD, "Dial SW (push)"),
    19: (GREEN, "LED data -> shifter 1A"),
    34: (BLACK_W, "LED + shifter GND"),
    35: (VIOLET, "Amp LRC"),
    39: (BLACK_W, "Amp GND"),
    40: (VIOLET, "Amp DIN"),
}
FREE = {7: "Leave GPIO4 free"}


def esc(t):
    return t.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


class Sheet:
    def __init__(self, w, h, title, desc):
        self.w, self.h, self.o = w, h, []
        self.title, self.desc = title, desc

    def add(self, s):
        self.o.append(s)

    def rect(self, x, y, w, h, fill, rx=0, stroke=None, sw=1.2, dash=None):
        s = f' stroke="{stroke}" stroke-width="{sw}"' if stroke else ""
        d = f' stroke-dasharray="{dash}"' if dash else ""
        self.add(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{rx}" fill="{fill}"{s}{d}/>')

    def text(self, x, y, t, size=13, fill=V100, family=MONO, anchor="start", weight=400, ls=0):
        self.add(f'<text x="{x}" y="{y}" font-family="{family}" font-size="{size}" fill="{fill}" '
                 f'text-anchor="{anchor}" font-weight="{weight}" letter-spacing="{ls}">{esc(t)}</text>')

    def wire(self, pts, colour, width=3.2, dash=None):
        d = "M" + " L".join(f"{x} {y}" for x, y in pts)
        da = f' stroke-dasharray="{dash}"' if dash else ""
        self.add(f'<path d="{d}" fill="none" stroke="{colour}" stroke-width="{width}" stroke-linecap="round" '
                 f'stroke-linejoin="round"{da}/>')

    def dot(self, x, y, colour, r=5):
        self.add(f'<circle cx="{x}" cy="{y}" r="{r}" fill="{colour}" stroke="{V950}" stroke-width="1.5"/>')

    def header(self, kicker, title):
        self.text(40, 46, kicker, 12, V300, MONO, ls=2)
        self.text(40, 80, title, 26, V050, DISPLAY, weight=800)

    def note(self, x, y, w, lines, colour=GOLD, title="NOTE"):
        h = 30 + len(lines) * 20
        self.rect(x, y, w, h, V900, 8, colour, 1.2)
        self.text(x + 14, y + 22, title, 11.5, colour, MONO, ls=1.5)
        for i, ln in enumerate(lines):
            self.text(x + 14, y + 42 + i * 20, ln, 13.5, V100, SANS)
        return h

    def save(self, name):
        body = (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {self.w} {self.h}" role="img" '
                f'aria-labelledby="t d"><title id="t">{esc(self.title)}</title><desc id="d">{esc(self.desc)}</desc>'
                f'<rect width="{self.w}" height="{self.h}" fill="{V950}"/>' + "".join(self.o) + "</svg>")
        open(os.path.join(HERE, name), "w").write(body)
        print("wrote docs/wiring/" + name)


def header_map():
    s = Sheet(1500, 1180, "Raspberry Pi 5 header map",
              "Every pin of the Raspberry Pi 40-pin header, with the pins this build uses highlighted and labelled.")
    s.header("DIAL PANEL · WIRING", "RASPBERRY PI 5 · 40-PIN HEADER")
    s.text(40, 106, "Pin 1 is the corner nearest the USB-C power socket. Hold the board with the header on the right "
                    "and pin 1 at the top.", 14.5, V200, SANS)
    x0, y0, dy = 600, 150, 24
    box_l, box_r = x0 - 62, x0 + 96 + 62
    s.rect(box_l, y0 - 20, box_r - box_l, 20 * dy + 24, V900, 10, V700, 1.2)
    for i, (pin, name) in enumerate(PINS):
        col, row = i % 2, i // 2
        px = x0 + col * 96
        py = y0 + row * dy
        used = USED.get(pin)
        colour = used[0] if used else (GOLD if pin in FREE else V600)
        s.dot(px, py, colour, 6 if used else 3.5)
        # pin number and name sit ABOVE the wire line, so nothing is struck through
        s.text(px + (-12 if col == 0 else 12), py - 5, str(pin), 11, V050 if used else V400, MONO,
               anchor="end" if col == 0 else "start")
        s.text(px + (-12 if col == 0 else 12), py - 18, name, 10.5, V100 if used else V600, MONO,
               anchor="end" if col == 0 else "start")
        if used or pin in FREE:
            edge = box_l if col == 0 else box_r
            lx = 230 if col == 0 else s.w - 330
            dash = "4 4" if pin in FREE else None
            s.wire([(px, py), (edge, py), (lx, py)], colour, 2.2, dash=dash)
            s.text(lx + (-12 if col == 0 else 12), py + 4, (used[1] if used else FREE[pin]),
                   13, V100 if used else GOLD, SANS, anchor="end" if col == 0 else "start")
    y = y0 + 21 * dy
    s.note(40, y, 520, [
        "The dial's + goes to pin 1 (3.3 V), never to 5 V —",
        "its pull-ups would put 5 V onto a GPIO and damage the Pi.",
    ], RED, "READ THIS FIRST")
    s.note(640, y, 600, [
        "Grounds: pin 9 (dial), 34 (LEDs), 39 (amp).",
        "Any GND pin works electrically; these keep the runs short.",
        "Solder the 5 V split on pin 4 rather than stacking Dupont ends.",
    ], V300, "GROUNDS AND 5 V")
    s.save("header-map.svg")


def module(s, x, y, w, h, name, sub, pins, side="right", colour=V600):
    """A module box with labelled pads down one side. Returns {pad: (x, y)}."""
    s.rect(x, y, w, h, V800, 8, colour, 1.4)
    s.text(x + 14, y + 26, name, 15, V050, DISPLAY, weight=800)
    if sub:
        s.text(x + 14, y + 46, sub, 12, V300, MONO)
    spots = {}
    top = y + (64 if sub else 48)
    step = min(30, (y + h - 14 - top) / max(len(pins), 1))
    for i, p in enumerate(pins):
        py = top + i * step + 8
        px = x + w if side == "right" else x
        s.dot(px, py, V400, 4.5)
        s.text(px + (-14 if side == "right" else 14), py + 4, p, 12.5, V100, MONO,
               anchor="end" if side == "right" else "start")
        spots[p] = (px, py)
    return spots


def pi_stub(s, x, y, h, pins):
    """A stub of the Pi header showing just the pins used in this diagram."""
    w = 150
    s.rect(x, y, w, h, V800, 8, V600, 1.4)
    s.text(x + 14, y + 26, "PI 5 HEADER", 15, V050, DISPLAY, weight=800)
    spots = {}
    for i, (pin, label, colour) in enumerate(pins):
        py = y + 60 + i * 34
        s.dot(x + w, py, colour, 5.5)
        s.text(x + w - 16, py + 4, f"{pin}  {label}", 12.5, V100, MONO, anchor="end")
        spots[pin] = (x + w, py)
    return spots


def route(s, a, b, colour, mid=None):
    """Orthogonal wire from a to b, turning at mid x."""
    mx = mid if mid is not None else (a[0] + b[0]) / 2
    s.wire([a, (mx, a[1]), (mx, b[1]), b], colour)


def encoder():
    s = Sheet(1100, 620, "Dial wiring", "How the KY-040 rotary encoder connects to the Raspberry Pi header.")
    s.header("DIAL PANEL · WIRING", "1 · THE DIAL (KY-040)")
    pi = pi_stub(s, 60, 150, 250, [(1, "3V3", ORANGE), (9, "GND", BLACK_W), (11, "GPIO17", CYAN),
                                    (13, "GPIO27", CYAN), (15, "GPIO22", GOLD)])
    mod = module(s, 700, 150, 250, 250, "KY-040", "rotary encoder + push", ["+", "GND", "CLK", "DT", "SW"], side="left")
    for pin, pad, colour in ((1, "+", ORANGE), (9, "GND", BLACK_W), (11, "CLK", CYAN), (13, "DT", CYAN), (15, "SW", GOLD)):
        route(s, pi[pin], mod[pad], colour, mid=500)
    y = 430
    s.note(60, y, 480, ["+ goes to pin 1 (3.3 V). Never 5 V.",
                        "Five female-female jumpers, no soldering."], RED)
    s.note(580, y, 460, ["Turning sends steps; pressing sends Enter.",
                         "CLK/DT swapped just reverses direction —",
                         "swap the two wires, or the pins in config.txt."], V300, "IF IT FEELS BACKWARDS")
    s.save("encoder.svg")


def audio():
    s = Sheet(1100, 680, "Audio wiring", "How the MAX98357A amplifier and the speaker connect to the Raspberry Pi.")
    s.header("DIAL PANEL · WIRING", "2 · AMP AND SPEAKER (MAX98357A)")
    pi = pi_stub(s, 60, 150, 220, [(4, "5V", RED), (39, "GND", BLACK_W), (12, "GPIO18", VIOLET),
                                    (35, "GPIO19", VIOLET), (40, "GPIO21", VIOLET)])
    mod = module(s, 640, 150, 230, 260, "MAX98357A", "I2S mono amp",
                 ["Vin", "GND", "BCLK", "LRC", "DIN", "SD", "GAIN"], side="left")
    for pin, pad, colour in ((4, "Vin", RED), (39, "GND", BLACK_W), (12, "BCLK", VIOLET),
                             (35, "LRC", VIOLET), (40, "DIN", VIOLET)):
        route(s, pi[pin], mod[pad], colour, mid=470)
    # speaker
    s.rect(900, 250, 150, 110, V800, 8, V600, 1.4)
    s.text(914, 276, "SPEAKER", 15, V050, DISPLAY, weight=800)
    s.text(914, 296, "40 mm · 4 Ω", 12, V300, MONO)
    s.wire([(870, 300), (900, 300)], WHITE_W)
    s.wire([(870, 330), (900, 330)], BLACK_W)
    s.text(884, 292, "+", 12, V100, MONO)
    s.text(884, 346, "−", 12, V100, MONO)
    y = 440
    s.note(60, y, 520, ["Leave SD and GAIN unconnected.",
                        "SD is held high on the board by a 1 MΩ resistor, so wiring it",
                        "to a GPIO is a common way to end up with silence. GAIN",
                        "unconnected = 9 dB, which is right for this speaker."], GOLD, "DO NOT WIRE THESE")
    s.note(620, y, 430, ["The amp needs headers soldered on,",
                         "unless you bought a pre-soldered one.",
                         "Speaker polarity doesn't matter for one speaker."], V300, "NOTES")
    s.save("audio.svg")


def leds():
    s = Sheet(1240, 800, "LED wiring", "How the WS2812B strips connect through a level shifter to the Raspberry Pi.")
    s.header("DIAL PANEL · WIRING", "3 · THE LIGHT (WS2812B)")
    pi = pi_stub(s, 60, 160, 180, [(4, "5V", RED), (34, "GND", BLACK_W), (19, "GPIO10", GREEN)])
    sh = module(s, 430, 160, 250, 230, "74AHCT125", "3.3 V -> 5 V buffer",
                ["14 VCC", "7 GND", "1 OE1 -> GND", "2 1A (in)", "3 1Y (out)"], side="right")
    band = module(s, 940, 150, 230, 120, "BAND STRIP", "~12 LEDs, forward", ["DIN", "5V", "GND"], side="left")
    wash = module(s, 940, 320, 230, 120, "WALL WASH", "~40 LEDs, rearward", ["DIN", "5V", "GND"], side="left")

    # data: Pi -> shifter in, shifter out -> resistor -> band DIN, band DOUT -> wash DIN
    s.wire([pi[19], (330, pi[19][1]), (330, sh["2 1A (in)"][1]), sh["2 1A (in)"]], GREEN)
    rx, ry = 760, sh["3 1Y (out)"][1]
    s.wire([sh["3 1Y (out)"], (rx, ry)], GREEN)
    s.rect(rx, ry - 15, 84, 30, V800, 6, V600, 1.2)
    s.text(rx + 42, ry + 5, "330 Ω", 12.5, V100, MONO, anchor="middle")
    s.wire([(rx + 84, ry), (890, ry), (890, band["DIN"][1]), band["DIN"]], GREEN)
    s.wire([(890, band["DIN"][1]), (890, wash["DIN"][1]), wash["DIN"]], GREEN, 2.2, dash="5 4")
    s.text(700, wash["DIN"][1] + 4, "band DOUT -> wash DIN", 12, V300, MONO)

    # OE1 tied to ground, at the shifter
    s.wire([sh["1 OE1 -> GND"], (712, sh["1 OE1 -> GND"][1]), (712, sh["7 GND"][1]), sh["7 GND"]], BLACK_W, 2.2)

    # power: down from the Pi, along a clear corridor, straight up into the strips
    corr_v, corr_g = 560, 600
    riser_v, riser_g = 906, 924
    s.wire([pi[4], (250, pi[4][1]), (250, corr_v), (riser_v, corr_v), (riser_v, band["5V"][1]), band["5V"]], RED, 2.8)
    s.wire([(riser_v, corr_v), (riser_v, wash["5V"][1]), wash["5V"]], RED, 2.8)
    s.wire([pi[34], (215, pi[34][1]), (215, corr_g), (riser_g, corr_g), (riser_g, band["GND"][1]), band["GND"]],
           BLACK_W, 2.8)
    s.wire([(riser_g, corr_g), (riser_g, wash["GND"][1]), wash["GND"]], BLACK_W, 2.8)
    route(s, pi[4], sh["14 VCC"], RED, mid=300)
    route(s, pi[34], sh["7 GND"], BLACK_W, mid=272)
    s.text(300, corr_v - 8, "5 V to both strips", 12, RED, MONO)
    s.text(300, corr_g + 18, "GND to both strips", 12, V200, MONO)

    y = 640
    s.note(60, y, 560, ["Strips have a direction: wire into the DIN end.",
                        "Chain them: band DOUT -> wash DIN. Cut only on pads."], V300, "DIRECTION MATTERS")
    s.note(650, y, 530, ["Brightness stays capped (config.txt: 64/255).",
                         "52 LEDs at full white would pull ~3 A, more than the",
                         "Pi's 5 V pins can give. Solder the 5 V split."], RED, "POWER")
    s.note(60, y + 110, 1120, ["The shifter is recommended, not required: WS2812Bs want a data high near 5 V and the Pi gives 3.3 V.",
                               "Try without it (GPIO10 straight to the resistor); add it if the LEDs flicker or show wrong colours."],
           GOLD, "OPTIONAL")
    s.save("leds.svg")


def mic_cut():
    s = Sheet(1100, 700, "Mic cut wiring", "How the rocker switch is spliced into the microphone's USB power wire.")
    s.header("DIAL PANEL · WIRING", "4 · THE MIC CUT (ONE SPLICE)")
    s.text(40, 112, "The rocker breaks the microphone's power. Off means the Pi cannot see the mic at all — "
                    "no software can turn it back on.", 14.5, V200, SANS)
    # the cable
    yc = 260
    s.rect(60, yc - 34, 980, 150, V900, 10, V700, 1.2)
    s.text(78, yc - 12, "USB-A EXTENSION, JACKET OPENED ABOUT 10 CM FROM THE FEMALE END", 11.5, V300, MONO, ls=1.2)
    s.text(78, yc + 132, "MALE END -> PI USB PORT", 11.5, V300, MONO)
    s.text(1022, yc + 132, "FEMALE END -> MIC", 11.5, V300, MONO, anchor="end")
    for i, (name, colour, cut) in enumerate((("RED  +5 V (VBUS)", RED, True), ("WHITE  D−", WHITE_W, False),
                                              ("GREEN  D+", GREEN, False), ("BLACK  GND", BLACK_W, False))):
        y = yc + 14 + i * 22
        if cut:
            s.wire([(100, y), (470, y)], colour)
            s.wire([(630, y), (1000, y)], colour)
            s.text(550, y - 14, "CUT HERE", 12, RED, MONO, anchor="middle")
        else:
            s.wire([(100, y), (1000, y)], colour, 2.4)
        s.text(110, y - 8, name, 11, V200, MONO)
    # the rocker
    s.rect(480, 420, 140, 90, V800, 8, V600, 1.4)
    s.text(550, 452, "ROCKER", 14, V050, DISPLAY, anchor="middle", weight=800)
    s.text(550, 472, "KCD1 · 2 pin", 11.5, V300, MONO, anchor="middle")
    s.wire([(470, yc + 14), (470, 360), (505, 360), (505, 420)], RED)
    s.wire([(630, yc + 14), (630, 360), (595, 360), (595, 420)], RED)
    y = 545
    s.note(60, y, 470, ["1. Cut ONLY the red wire.",
                        "2. Strip both ends about 5 mm.",
                        "3. Slide heat-shrink on BEFORE soldering.",
                        "4. Solder one end to each rocker terminal.",
                        "5. Shrink the tubing over each joint."], V300, "STEPS")
    s.note(570, y, 470, ["Leave white, green and black untouched.",
                         "Cutting a data wire kills the microphone;",
                         "cutting the shield can cause noise.",
                         "Check with the Pi off, then boot and run",
                         "arecord -l with the rocker on and off."], RED, "CAREFUL")
    s.save("mic-cut.svg")


def overview():
    s = Sheet(1180, 720, "Wiring overview", "What connects to what in the Dial Panel.")
    s.header("DIAL PANEL · WIRING", "OVERVIEW")
    cx, cy = 470, 300
    s.rect(cx, cy, 240, 180, V800, 10, V600, 1.6)
    s.text(cx + 120, cy + 40, "RASPBERRY PI 5", 17, V050, DISPLAY, anchor="middle", weight=800)
    s.text(cx + 120, cy + 64, "40-pin header", 12.5, V300, MONO, anchor="middle")
    s.text(cx + 120, cy + 96, "+ USB-C power in", 12.5, V200, MONO, anchor="middle")
    s.text(cx + 120, cy + 118, "+ display ribbon", 12.5, V200, MONO, anchor="middle")
    blocks = [
        (110, 150, "TOUCH DISPLAY 2", "ribbon + 5 V/GND on pins 2, 6", RED),
        (110, 300, "DIAL (KY-040)", "3V3, GND, GPIO17/27/22", CYAN),
        (110, 450, "MIC + ROCKER", "USB, with the rocker in VBUS", GOLD),
        (830, 150, "AMP + SPEAKER", "5 V, GND, GPIO18/19/21", VIOLET),
        (830, 300, "LED STRIPS", "5 V, GND, GPIO10 via buffer", GREEN),
        (830, 450, "USB-C POWER", "27 W supply, straight plug", RED),
    ]
    for x, y, name, sub, colour in blocks:
        s.rect(x, y, 240, 90, V900, 10, colour, 1.4)
        s.text(x + 16, y + 34, name, 15, V050, DISPLAY, weight=800)
        s.text(x + 16, y + 58, sub, 12, V200, MONO)
        a = (x + 240, y + 45) if x < cx else (x, y + 45)
        b = (cx, cy + 60) if x < cx else (cx + 240, cy + 60)
        route(s, a, b, colour, mid=(cx - 60) if x < cx else (cx + 300))
    s.note(110, 570, 960, ["Everything runs from the Pi's own 27 W supply. Nothing else needs power.",
                           "Full pin list: header-map.svg. Then wire each subsystem: encoder, audio, leds, mic-cut."],
           V300, "AT A GLANCE")
    s.save("overview.svg")


for fn in (overview, header_map, encoder, audio, leds, mic_cut):
    fn()
