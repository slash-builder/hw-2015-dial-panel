#!/usr/bin/env bash
# Build a Dial OS image.
#
#   ./os/build.sh                  build in Docker (works on any x86_64 Linux)
#   ./os/build.sh --native         build directly (Linux host, needs root)
#   ./os/build.sh --fetch-only     just get and verify the base image
#
# The whole method in one place: fetch a pinned Raspberry Pi OS release, verify
# it, stage the few things that make it a Dial Panel, and let CustomPiOS do the
# unpack/chroot/repack. We are not building an operating system — we are
# applying a short patch to the one Raspberry Pi already tests.

set -euo pipefail

HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO="$(cd "${HERE}/.." && pwd)"

# Pinned rather than tracked. See the file for why.
# shellcheck source=base-image.conf
source "${HERE}/base-image.conf"

CUSTOMPIOS_REF="${CUSTOMPIOS_REF:-devel}"
WORK="${HERE}/.work"
BASE_DIR="${HERE}/image-raspios_lite_arm64"
STAGE="${HERE}/modules/dialos/filesystem/root/usr/lib/dial-os"

MODE=docker
case "${1:-}" in
    --native)     MODE=native ;;
    --fetch-only) MODE=fetch ;;
    --docker|"")  MODE=docker ;;
    -h|--help)    sed -n '2,12p' "$0" | sed 's/^# \{0,1\}//'; exit 0 ;;
    *)            echo "unknown argument: $1" >&2; exit 2 ;;
esac

say() { printf '\n\033[1m==> %s\033[0m\n' "$*"; }

# ── The base image ──────────────────────────────────────────────────────────

say "Base: Raspberry Pi OS Lite arm64, ${BASE_SUITE}, ${BASE_RELEASE}"
mkdir -p "${BASE_DIR}"
base="${BASE_DIR}/${BASE_IMAGE_FILE}"

if [ -f "${base}" ]; then
    echo "already downloaded"
else
    echo "fetching ${BASE_IMAGE_URL}"
    curl -fL --progress-bar -o "${base}.part" "${BASE_IMAGE_URL}"
    mv "${base}.part" "${base}"
fi

# Verify every time, not just after downloading: a truncated file from an
# interrupted earlier run looks exactly like a good one to `[ -f ]`.
say "Verifying checksum"
if command -v sha256sum >/dev/null 2>&1; then
    actual="$(sha256sum "${base}" | cut -d' ' -f1)"
else
    actual="$(shasum -a 256 "${base}" | cut -d' ' -f1)"
fi
if [ "${actual}" != "${BASE_IMAGE_SHA256}" ]; then
    echo "checksum mismatch for ${BASE_IMAGE_FILE}" >&2
    echo "  expected ${BASE_IMAGE_SHA256}" >&2
    echo "  actual   ${actual}" >&2
    echo "Delete it and re-run, or update os/base-image.conf if this is a deliberate bump." >&2
    exit 1
fi
echo "ok"

[ "${MODE}" = fetch ] && exit 0

# ── Stage the generated pieces ──────────────────────────────────────────────
#
# Generated, never hand-copied. The device's own docs are the source of truth
# for how this hardware is wired, and a second copy of the pin assignments
# would be wrong the first time a pin moved.

say "Staging"
mkdir -p "${STAGE}"

cp "${REPO}/docs/config.txt" "${STAGE}/config.txt.append"
echo "boot overlays  <- docs/config.txt"

# The dashboard, if there is a build of it. There deliberately does not have to
# be: an image without it still boots and still brings the hardware up, and it
# says so rather than pretending.
if [ -n "${DIAL_DASHBOARD_BIN:-}" ] && [ -f "${DIAL_DASHBOARD_BIN}" ]; then
    cp "${DIAL_DASHBOARD_BIN}" "${STAGE}/dial-dashboard"
    echo "dashboard      <- ${DIAL_DASHBOARD_BIN}"
else
    rm -f "${STAGE}/dial-dashboard"
    echo "dashboard      <- none (peripherals-only image)"
fi

# Version from the tag the repo already puts on every commit to main.
DIST_VERSION="$(git -C "${REPO}" describe --tags --always --dirty 2>/dev/null || echo 0.0.0-dev)"
export DIST_VERSION
echo "version        <- ${DIST_VERSION}"

# ── CustomPiOS ──────────────────────────────────────────────────────────────

say "CustomPiOS (${CUSTOMPIOS_REF})"
mkdir -p "${WORK}"
if [ -d "${WORK}/CustomPiOS/.git" ]; then
    git -C "${WORK}/CustomPiOS" fetch --quiet origin
    git -C "${WORK}/CustomPiOS" checkout --quiet "${CUSTOMPIOS_REF}"
    git -C "${WORK}/CustomPiOS" pull --quiet --ff-only || true
else
    git clone --quiet --branch "${CUSTOMPIOS_REF}" \
        https://github.com/guysoft/CustomPiOS.git "${WORK}/CustomPiOS"
fi
echo "${WORK}/CustomPiOS/src" > "${HERE}/custompios_path"

if [ "${MODE}" = native ]; then
    say "Building natively"
    [ "$(id -u)" -eq 0 ] || { echo "--native needs root (loopback mounts)" >&2; exit 1; }
    "${HERE}/build_dist"
else
    say "Building in Docker"
    command -v docker >/dev/null 2>&1 || { echo "docker not found; try --native on a Linux host" >&2; exit 1; }

    docker build --quiet --tag dial-os-builder \
        -f "${WORK}/CustomPiOS/src/docker/Dockerfile" "${WORK}/CustomPiOS/src/docker"

    # Privileged because the build mounts the image over loopback devices.
    # This is the one genuinely awkward requirement of image building, and it
    # is why this runs on a build host rather than on a laptop by habit.
    docker run --rm --privileged \
        -v /dev:/dev \
        -v "${REPO}:/repo" \
        -e DIST_VERSION="${DIST_VERSION}" \
        -w /repo/os \
        dial-os-builder \
        /repo/os/build_dist
fi

say "Done"
ls -lh "${HERE}"/*.img.xz "${HERE}"/*.img 2>/dev/null || true
