# Dial Panel software

Two crates. One is the device's behaviour; the other is a way to look at it
without a Raspberry Pi in front of you.

```
dial-nav/   the interaction model, as pure logic — no I/O, no clock, no hardware
dial-sim/   a desktop harness: the same logic, drawn in a window on your laptop
```

## Why it is split this way

The panel's behaviour is the part worth getting right, and it is the part that
is painful to iterate on if every change means flashing a card and walking over
to a bench. So `dial-nav` contains **no device at all**:

- input arrives as events — `Turn(detents)`, `Push`
- time arrives as `Tick(duration)`; the crate never reads a clock
- output is a `Frame` a host draws however it likes, plus a list of `Effect`s
  the host may act on — light an LED, play a tone, switch a relay

Nothing in it touches GPIO, opens a file, or knows what it is running on. That
is what lets the same state machine run under the harness and on the panel
unchanged — and it is why the eight-second idle reset can be tested in
microseconds instead of eight seconds.

It also means this logic can be lifted into a shared Kit later without a
rewrite, which is the intent.

## The interaction model

Turn to move focus. Push to open. Turn to adjust inside a tile. **There is no
back button** — you leave a tile by pushing, or by letting it time out and go
home on its own after about eight seconds, which the screen shows as a draining
line and the words "HOME IN n".

Tiles come in four kinds, because not everything wants a screen:

| Kind | Push | Turn inside |
|---|---|---|
| `Range` | opens it | adjusts the value live |
| `Toggle` | flips it, stays home | — |
| `Action` | fires it, stays home | — |
| `Info` | opens it to be read | nothing |

Adjustment is **live**, not a dialog you confirm: turning a dimmer dims the
lamp. So leaving a tile — deliberately or by timeout — keeps what you set.
There is nothing to cancel, which is what makes a device with no back button
safe to walk away from.

## Run the harness

```sh
cargo run -p dial-sim                      # IGNITION
cargo run -p dial-sim -- nightfall         # NIGHTFALL
```

```
← →  or scroll     turn the dial
Enter / Space      push
Esc                quit
```

The window is the panel's real geometry: the 7" Touch Display 2 is a 720×1280
portrait panel mounted landscape, so 1280×720.

There is deliberately **no key that acts as "back"**. The device does not have
one, and a harness that quietly added one would be testing a device nobody is
building.

## Render without a display

```sh
cargo run -p dial-sim -- nightfall --shots /tmp/shots
```

Writes a PNG per state — home, a toggle switched on, a tile open, a tile
mid-countdown — with no window and no display. This is how the renderer gets
checked on a build machine, and it is the difference between "it compiled" and
knowing what it actually draws.

## Test

```sh
cargo test -p dial-nav
```

Twenty-three tests, no hardware. Each one is a line from the concept sheet
stated as an assertion — that an open tile goes home at eight seconds and not at
7.999, that any touch of the dial restarts the countdown, that the home screen
never counts down because it has nowhere to go, that pushing out of a tile lands
all the way home with no intermediate level.

## What this is not

**It is not a decision about the shipped shell.** Which framework the device's
real dashboard is built on — Flutter Embedded Linux, Slint, or Rust drawing
straight to the framebuffer — is an open question with a benchmark of its own
(THUN-24). `dial-sim` uses `winit` + `softbuffer` + `tiny-skia` because they are
small, pure Rust and run anywhere; that choice binds the harness and nothing
else.

**It is not the dashboard.** There is no Hearth client here, no home-automation
integration, no LED or audio output — those are separate pieces of work, and
this one deliberately stops at the seam so they can be written against a
behaviour that is already proven.

## Two things left open on purpose

Both are exposed as configuration rather than settled in code, because they are
`ux-engineer`'s and DJ's calls, not the state machine's:

- **`idle_timeout`** — the concept says "about 8 seconds". Whether it is
  adjustable, and by whom, is undecided.
- **`idle_resets_focus`** — when the panel goes home on its own, should focus
  return to the first tile? Default is no: going home is about leaving a tile,
  not forgetting where you were standing. A wall panel that always greets you at
  the same tile is a defensible other answer.

Still unanswered elsewhere, and deliberately not invented here: hold-screens, a
long-press escape hatch, and whether the panel accepts touch at all or is
dial-only.
