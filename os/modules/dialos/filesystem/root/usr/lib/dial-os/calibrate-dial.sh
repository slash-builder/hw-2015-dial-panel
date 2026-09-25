#!/usr/bin/env bash
# Measure how many events one full turn of the dial produces.
#
# Why this exists: a KY-040 may be 20-detent/20-pulse or 30-detent/15-pulse,
# and nothing printed on the part tells you which one you bought. The device's
# own config.txt says as much — "steps-per-period=1 suits 20-detent/20-pulse
# KY-040s; use 2 if yours is 30 detent / 15 pulse" — which is a fine note for
# someone who already knows, and a trap for everyone else. A dial that moves
# two tiles per click feels broken, and most people will assume they soldered
# it wrong.
#
# So measure it instead of asking. The result goes in dial.toml and the
# dashboard scales by it, which means no reboot: changing steps-per-period in
# config.txt would work too, but it is a device-tree parameter and would cost a
# restart in the middle of someone's first five minutes with the thing.
#
# Usable on its own over SSH, and callable by the dashboard's first-run wizard.

set -euo pipefail

CONFIG=${DIAL_CONFIG:-/etc/dial-os/dial.toml}
SECONDS_TO_WATCH=${DIAL_CALIBRATE_SECONDS:-6}

die() { echo "calibrate-dial: $*" >&2; exit 1; }

command -v evtest >/dev/null 2>&1 || die "evtest is not installed"

# The rotary-encoder overlay names its device after the overlay, so find it by
# name rather than by guessing at an event number that moves between boots.
find_dial() {
    local dev name handlers
    while read -r line; do
        case "${line}" in
            N:*) name="${line#N: Name=}" ;;
            H:*)
                handlers="${line#H: Handlers=}"
                case "${name}" in
                    *rotary*|*Rotary*|*encoder*|*Encoder*)
                        for h in ${handlers}; do
                            case "${h}" in
                                event*) echo "/dev/input/${h}"; return 0 ;;
                            esac
                        done
                        ;;
                esac
                ;;
        esac
    done < /proc/bus/input/devices
    return 1
}

dev="$(find_dial)" || die "no rotary encoder found — check dtoverlay=rotary-encoder in /boot/firmware/config.txt"
echo "calibrate-dial: watching ${dev}"
echo
echo "  Turn the dial ONE FULL TURN, steadily, in either direction."
echo "  You have ${SECONDS_TO_WATCH} seconds."
echo

# Count relative-axis reports. evtest prints one line per event; the timeout is
# what ends the run, so a non-zero exit from it is expected and not a failure.
count=$(timeout "${SECONDS_TO_WATCH}" evtest "${dev}" 2>/dev/null \
        | grep -c "type 2 (EV_REL)" || true)

if [ "${count}" -eq 0 ]; then
    die "saw no movement — is this the right device, and did the dial turn?"
fi

echo "calibrate-dial: ${count} events in one turn"

# Snap to the two shapes this hardware actually comes in, and say so when the
# reading is neither: a number in between usually means the turn was not a
# clean single revolution, and silently writing it would bake in the mistake.
case "${count}" in
    1[5-9]|2[0-5]) detents=20; note="20-detent / 20-pulse" ;;
    2[6-9]|3[0-5]) detents=30; note="30-detent / 15-pulse" ;;
    *)
        echo "calibrate-dial: ${count} is not close to either 20 or 30."
        echo "calibrate-dial: recording it as measured; re-run if the dial feels wrong."
        detents="${count}"; note="measured, unrecognised"
        ;;
esac

echo "calibrate-dial: recording detents_per_turn = ${detents} (${note})"

if [ -w "${CONFIG}" ] || [ -w "$(dirname "${CONFIG}")" ]; then
    tmp="$(mktemp)"
    sed "s/^detents_per_turn = .*/detents_per_turn = ${detents}/" "${CONFIG}" > "${tmp}"
    cat "${tmp}" > "${CONFIG}"
    rm -f "${tmp}"
    echo "calibrate-dial: wrote ${CONFIG}"
else
    echo "calibrate-dial: ${CONFIG} is not writable; run with sudo to record it" >&2
    exit 1
fi
