#!/usr/bin/env bash
# Dial OS first run.
#
# What this does NOT do: ask for Wi-Fi, a hostname, a username or an SSH key.
# Raspberry Pi Imager already asked for those, on a real keyboard, before the
# card was ever written. Asking again on a device whose only input is one knob
# would be a worse version of a solved problem.
#
# What is left is genuinely device-specific, and the panel can ask for it with
# the control it has: which team's light it carries, and how its dial is
# actually wired.

set -euo pipefail

STATE_DIR=/var/lib/dial
SENTINEL="${STATE_DIR}/.firstrun-complete"
CONFIG=/etc/dial-os/dial.toml

log() { echo "dial-os/firstrun: $*"; }

if [ -e "${SENTINEL}" ]; then
    log "already complete"
    exit 0
fi

install -d -o dial -g dial -m 0755 "${STATE_DIR}"

# ── Report what the hardware is actually doing ──────────────────────────────
#
# Written to the journal so that a panel which does not light up can be
# diagnosed by a person who has never seen this repo, with one command.

log "kernel: $(uname -sr)"
log "model: $(tr -d '\0' < /proc/device-tree/model 2>/dev/null || echo unknown)"

for node in /dev/dri/card0 /dev/leds0; do
    if [ -e "${node}" ]; then
        log "found ${node}"
    else
        log "MISSING ${node} — check the overlays in /boot/firmware/config.txt"
    fi
done

if [ -d /dev/input ]; then
    log "input devices: $(find /dev/input -maxdepth 1 -name 'event*' | wc -l | tr -d ' ')"
fi

if aplay -l 2>/dev/null | grep -qi max98357; then
    log "found the I2S amplifier"
else
    log "MISSING the I2S amplifier — check dtoverlay=max98357a"
fi

if [ -f "${CONFIG}" ]; then
    team="$(sed -n 's/^team = "\(.*\)"/\1/p' "${CONFIG}")"
    if [ -n "${team}" ]; then
        log "team: ${team}"
    else
        log "team: not chosen yet — the panel will ask on the dial"
    fi
else
    log "MISSING ${CONFIG}"
fi

# ── Hand over to the panel itself ───────────────────────────────────────────
#
# The remaining questions are asked on the dial, by the dashboard, because
# they are questions about a thing you are holding. If the dashboard is not
# installed yet, say so plainly rather than marking setup complete — an image
# that quietly claims to be finished is the failure this project keeps
# correcting.

if [ -x /usr/local/bin/dial-dashboard ]; then
    log "handing off to the dashboard for team selection and dial calibration"
    touch "${SENTINEL}"
    chown dial:dial "${SENTINEL}"
else
    log "no dashboard installed — this is a peripherals-only image."
    log "the hardware above is configured and ready; the panel software is not"
    log "installed yet. Not marking first run complete."
fi

log "done"
