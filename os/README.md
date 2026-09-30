# Dial OS

A Raspberry Pi OS image with the Dial Panel already set up. Flash it, and the
dial, screen, speaker and lights work on first boot.

```sh
./os/build.sh
```

That is the method. The rest of this file explains what it does and why it is
built this way.

## The idea

**Dial OS is not an operating system we maintain.** It is the official
Raspberry Pi OS release, with a short patch applied: four device-tree overlays
that the device's own `docs/config.txt` already specifies, a user with the
right groups, two systemd units, and the dashboard binary.

That framing is the whole design. Every hour we would spend maintaining a
distribution is an hour not spent on the device. So the build takes an image
Raspberry Pi has already built and tested, unpacks it, changes about twenty
things, and packs it back up. When Raspberry Pi ships a new release, we bump
one checksum and rebuild.

## Why CustomPiOS, and not the two obvious alternatives

| | What it does | Why not here |
|---|---|---|
| **pi-gen** | Builds Raspberry Pi OS from scratch with `debootstrap`. It is the tool Raspberry Pi builds the real thing with. | We would be rebuilding an entire OS to add four config lines. All of the cost of building from scratch, almost none of the benefit — right if we needed to *remove* a lot or change the base, and we do not. |
| **rpi-image-gen** | Raspberry Pi's own newer, declarative layer/config/hook builder. Structurally the nicer tool. | Its supported hosts are **arm64 Debian**, so it needs a Pi or an arm64 builder we do not have free — and it is explicitly under active development, which is a poor foundation under a device we want strangers to flash. Worth revisiting; see "When to switch". |
| **CustomPiOS** ✅ | Opens a released image, modifies it in a chroot, repacks it. | Builds on x86_64 in Docker, so it runs on the build fleet we already have. Minutes, not an hour. And it is the proven path for exactly this shape of product — OctoPi, MainsailOS and FluiddPi are all appliance distributions for printed hardware, all built this way. |

The decisive argument is not the first build, it is the tenth. Starting from
the released image means we inherit Raspberry Pi's firmware, kernel, overlays
and testing for free, forever, instead of re-deriving them.

## What the build actually does

1. **Fetches a pinned base image** and verifies its SHA-256 — every run, not
   just after downloading, because a truncated file from an interrupted run
   looks exactly like a good one.
2. **Stages the generated pieces.** The boot overlays are copied from
   `docs/config.txt`, the device's own source of truth for how it is wired. They
   are never retyped here; a second copy of the pin assignments would be wrong
   the first time a pin moved.
3. **Runs CustomPiOS**, which unpacks the image, runs
   `modules/dialos/start_chroot_script` inside it, and repacks it.

`start_chroot_script` is worth reading directly — it is the clearest
description anywhere of what Dial OS is.

## Setting one up

This is the part that has to be easy, because the people flashing it have just
spent two days printing an enclosure and do not want a second project.

**Everything that needs a keyboard happens before the card is written.**
Raspberry Pi Imager already asks for Wi-Fi, hostname, user and SSH, on a real
keyboard, and writes them into the image. Dial OS leaves that mechanism
completely untouched. Asking again on a device whose only input is one knob
would be a worse version of a solved problem.

**Everything else happens on the dial**, because it is a question about a thing
you are holding:

- **Which team.** IGNITION or NIGHTFALL — turn, push, done. One image ships
  both, matching a release that ships both printed band inserts. One device,
  one team, for its life; the software never offers to change it afterwards.
- **Dial calibration.** A KY-040 may be 20-detent/20-pulse or 30-detent/15-pulse
  and *nothing on the part says which*. Guess wrong and the dial moves two
  tiles per click, which feels broken — and most people will assume they
  soldered it wrong. So `calibrate-dial.sh` measures it: turn the dial one full
  turn, and the count goes in `dial.toml`. The dashboard scales by it, so there
  is no reboot; setting `steps-per-period` in `config.txt` would work equally
  well but costs a restart in someone's first five minutes with the thing.

So the whole setup is: flash, boot, pick a team, turn the dial once.

### Getting it into Raspberry Pi Imager

CustomPiOS generates an `os_list` entry from the `RPI_IMAGER_*` values in
[`config`](config). Published alongside a release, that lets a builder point
Imager's **Content Repository** at SlashBuilder and pick "Dial OS" from the
same list as Raspberry Pi OS itself — no separate installer, nothing to follow.

Until that is published, **Use Custom** with the downloaded `.img.xz` works and
needs no infrastructure at all.

## Two ways in

`start_chroot_script` is ordinary shell that happens to run in a chroot.
Nothing in it assumes it is running inside a build. That is deliberate: the
same script can run on a live Raspberry Pi to convert a working Pi OS install
into a Dial Panel, which is what you want when someone already has a card they
like, or when you are bringing up the bench unit and do not want to reflash to
change one thing.

The image is the front door. The script is the side door. There is only one
set of instructions to keep correct.

## Bumping the base image

Edit [`base-image.conf`](base-image.conf): release date, filename, URL,
SHA-256. Take the checksum from the `.sha256` file Raspberry Pi publishes next
to the image, not from a mirror.

It is pinned rather than tracking latest because a build that silently follows
`latest` is a build you cannot reproduce when someone reports a bug against an
image you shipped three months ago.

## Verified, and not

**Verified:** every script passes `shellcheck` and `bash -n`; the pinned URL
resolves (HTTP 200, 541 MB, correct `xz` magic bytes) and its checksum matches
the one Raspberry Pi publishes.

**Not yet verified: a real image has not been built from this.** That needs a
Linux host with Docker and privileged loopback mounts — a build agent, not a
laptop — and the first real run is where the remaining unknowns live: the
`.img.xz` variant handling, whether `set_config_var` behaves on Trixie's
`config.txt`, and whether disabling `getty@tty1` leaves a usable recovery path.
None of it is exotic, but none of it is proven, and this file will not claim
otherwise until an image has booted a Pi.

## Open: Bookworm or Trixie?

This builds on **Trixie**, because that is what Raspberry Pi OS is now — the
2026-09-15 release is `raspios-trixie-arm64-lite`. The device's
`docs/config.txt` still says Bookworm in its header.

Starting a new device on the *previous* base is the same mistake as building on
an end-of-life Yocto branch, which this studio is already paying for elsewhere.
So: Trixie, unless someone objects. What would justify Bookworm is evidence that
a specific overlay this device needs — most likely `ws2812-pio`, which is
RP1-era and new — behaves differently there. That is a bench test, not an
opinion, and it belongs in the first-boot story.

## When to switch to rpi-image-gen

Not now, but the trigger is worth naming so the decision gets made rather than
drifted past: if Dial OS ever needs to *subtract* substantially from Pi OS —
strip the package set hard, change the init, produce an A/B-updatable root —
then modifying a released image stops being the cheap option and a declarative
builder starts being worth an arm64 build host. Until then, the cheapest
correct thing is to patch what Raspberry Pi already ships.
