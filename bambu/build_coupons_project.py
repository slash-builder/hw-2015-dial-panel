"""
Build the Bambu Studio TEST project for the fit coupons
(bambu/dial-panel-coupons.3mf) -- a SEPARATE file from the release
project (bambu/dial-panel-hw-2015.3mf), which is what strangers print.
Nothing here touches that file or its plates.

Coupons A1/A2, B1/B2/B3 and C1 are the same black PLA as the real body
parts; C3 (05-band-diffuser) is clear PETG and cannot share a plate with
PLA (different bed-adhesion/temperature profile, same reasoning
build_project.py already uses for plate 7 of the release project) --
C2 (04a-band-insert-ignition) is black PLA per the BOM, same as the rest.

Every coupon STL under stl/coupons/ is already print-oriented and
bed-centred (cad/coupons.py's own export_coupon() applies the exact same
rotate+translate recipe as build_project.py's own ORIENT_SCRIPT), so this
script skips the orient step entirely and places them directly.

Pipeline (needs Bambu Studio installed):
  1. flatten Bambu's A1 system profiles (same as build_project.py)
  2. build the plates with Bambu Studio's --load-assemble-list
  3. finish: filament colours, Textured PEI plate, clean names, metadata
  4. slice every plate as a check; any plate that fails or warns fails the build

    python3 bambu/build_coupons_project.py
    python3 bambu/build_coupons_project.py --no-slice

Environment overrides: BAMBU_STUDIO, BAMBU_PROFILES.
"""
import argparse
import io
import json
import os
import re
import subprocess
import sys
import tempfile
import zipfile

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(HERE)
COUPON_STL_DIR = os.path.join(REPO, "stl", "coupons")
OUT = os.path.join(HERE, "dial-panel-coupons.3mf")

BAMBU = os.environ.get("BAMBU_STUDIO", "/Applications/BambuStudio.app/Contents/MacOS/BambuStudio")
PROFILES = os.environ.get("BAMBU_PROFILES", "/Applications/BambuStudio.app/Contents/Resources/profiles/BBL")

PRINTER = "Bambu Lab A1 0.4 nozzle"
PROCESS = "0.20mm Standard @BBL A1"
FILAMENTS = [
    ("Bambu PLA Matte @BBL A1", "#1B1B1D"),   # 1 matte black: every coupon except the diffuser
    ("Bambu PETG HF @BBL A1", "#E6EEF2"),     # 2 clear PETG: C3, the diffuser corner
]
BED_TYPE = "Textured PEI Plate"

PLATES = [
    ("1 . Coupons A+B+C1+C2 . black PLA", [
        ("A1-face-plate-screen-corner", 1),
        ("A2-back-shell-screen-corner", 1),
        ("B1-back-shell-column-seam", 1),
        ("B2-face-plate-column-seam", 1),
        ("B3-back-shell-screen-seam-strip", 1),
        ("C1-face-plate-screen-band-mount", 1),
        ("C2-band-insert-ignition-band-mount", 1),
    ]),
    ("2 . Coupon C3 (diffuser corner) . clear PETG", [
        ("C3-band-diffuser-band-mount", 2),
    ]),
]

META = {
    "Title": "Dial Panel (hw-2015) -- fit coupons",
    "Designer": "SlashBuilder",
    "License": "CC-BY-4.0",
    "Description": "Full-scale section coupons cut from the real hw-2015-dial-panel parts, for iterating "
                   "fit without reprinting plates 1-3 (10h36m). See docs/fit-coupons.md. TEST ARTEFACTS -- "
                   "not the release build; see bambu/dial-panel-hw-2015.3mf for that.",
}


def run(cmd, **kw):
    return subprocess.run(cmd, capture_output=True, text=True, **kw)


def flatten(kind, name):
    def find(n):
        for root, _, files in os.walk(os.path.join(PROFILES, kind)):
            if n + ".json" in files:
                return os.path.join(root, n + ".json")
        sys.exit(f"Bambu profile not found: {kind}/{n}")

    def resolve(n):
        d = json.load(open(find(n)))
        base = resolve(d["inherits"]) if d.get("inherits") else {}
        base.update(d)
        base.pop("inherits", None)
        return base
    d = resolve(name)
    d["name"], d["from"] = name, "system"
    return d


def finish(src, dst):
    zin, buf = zipfile.ZipFile(src), io.BytesIO()
    zout = zipfile.ZipFile(buf, "w", zipfile.ZIP_DEFLATED)
    for item in zin.infolist():
        data = zin.read(item.filename)
        if item.filename == "Metadata/project_settings.config":
            ps = json.loads(data)
            assert len(ps["filament_settings_id"]) == len(FILAMENTS)
            ps["filament_colour"] = [c for _, c in FILAMENTS]
            ps["curr_bed_type"] = BED_TYPE
            data = json.dumps(ps, indent=4).encode()
        elif item.filename == "Metadata/model_settings.config":
            data = re.sub(r'(<metadata key="name" value="[^"]+?)_1"', r'\1"', data.decode()).encode()
        elif item.filename == "3D/3dmodel.model":
            s = data.decode()
            for k, v in META.items():
                s = re.sub(rf'<metadata name="{k}">[^<]*</metadata>',
                           lambda _m, k=k, v=v: f'<metadata name="{k}">{v.replace("&", "&amp;")}</metadata>', s)
            data = s.encode()
        zout.writestr(item, data)
    zout.close()
    open(dst, "wb").write(buf.getvalue())


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--no-slice", action="store_true", help="skip the slice-every-plate check")
    args = ap.parse_args()
    if not os.path.exists(BAMBU):
        sys.exit(f"not found: {BAMBU} (set BAMBU_STUDIO)")
    all_names = [n for _, objs in PLATES for n, _ in objs]
    missing = [n for n in all_names if not os.path.exists(os.path.join(COUPON_STL_DIR, n + ".stl"))]
    if missing:
        sys.exit(f"missing coupon STL(s), run freecadcmd cad/coupons.py first: {missing}")

    work = tempfile.mkdtemp(prefix="dial-panel-coupons-3mf-")
    try:
        # 1. profiles
        paths = {}
        colour_of = dict(FILAMENTS)
        for kind, name in [("machine", PRINTER), ("process", PROCESS)] + [("filament", f) for f, _ in FILAMENTS]:
            p = os.path.join(work, f"{kind}-{name}.json")
            d = flatten(kind, name)
            if kind == "filament":
                d["filament_colour"] = [colour_of[name]]
            json.dump(d, open(p, "w"), indent=1)
            paths.setdefault(kind, []).append(p)

        # 2. plates -- coupon STLs are already print-oriented + bed-centred
        # (cad/coupons.py's own export_coupon()), so no orient step here.
        assemble = {"plates": [{"plate_name": pname, "need_arrange": True, "plate_params": {},
                                "objects": [{"path": os.path.join(COUPON_STL_DIR, n + ".stl"), "count": 1,
                                             "filaments": [slot], "pos_x": [0.0], "pos_y": [0.0], "pos_z": [0.0]}
                                            for n, slot in objs]}
                               for pname, objs in PLATES]}
        alist = os.path.join(work, "assemble.json")
        json.dump(assemble, open(alist, "w"), indent=1)
        raw = os.path.join(work, "raw.3mf")
        r = run([BAMBU, "--load-settings", ";".join(paths["machine"] + paths["process"]),
                 "--load-filaments", ";".join(paths["filament"]), "--load-assemble-list", alist,
                 "--outputdir", work, "--export-3mf", "raw.3mf"], cwd=work)
        res = json.load(open(os.path.join(work, "result.json")))
        if res.get("return_code") != 0 or not os.path.exists(raw):
            sys.exit(f"Bambu Studio could not build the plates: {res.get('error_string')}\n{r.stdout}\n{r.stderr}")

        # 3. finish
        finish(raw, OUT)
        print(f"wrote {os.path.relpath(OUT, REPO)} ({os.path.getsize(OUT) / 1e6:.2f} MB, {len(PLATES)} plates)")

        # 4. slice check
        total_seconds = 0.0
        if not args.no_slice:
            sl = os.path.join(work, "slice")
            os.makedirs(sl)
            r = run([BAMBU, "--debug", "2", "--slice", "0", "--outputdir", sl, OUT], cwd=work)
            res = json.load(open(os.path.join(sl, "result.json")))
            warns = sorted(set(re.findall(r"plate \d+: found \w+ slicing warnings: ([^\n]+)", r.stdout + r.stderr)))
            for f in sorted(os.listdir(sl), key=lambda s: [int(t) if t.isdigit() else t for t in re.split(r"(\d+)", s)]):
                if f.endswith(".gcode"):
                    txt = open(os.path.join(sl, f), errors="ignore").read(200000)
                    t = re.search(r"total estimated time: ([^\n;]+)", txt)
                    tstr = t.group(1).strip() if t else "?"
                    print(f"  {f:14s} {tstr}")
                    secs = 0
                    for num, unit in re.findall(r"(\d+)\s*(h|m|s)", tstr):
                        secs += int(num) * {"h": 3600, "m": 60, "s": 1}[unit]
                    total_seconds += secs
            if res.get("return_code") != 0:
                sys.exit(f"slicing failed: {res.get('error_string')}")
            if warns:
                sys.exit("slicing warnings:\n  " + "\n  ".join(warns))
            hh = int(total_seconds // 3600)
            mm = int((total_seconds % 3600) // 60)
            print(f"slice check: every plate sliced, no warnings")
            print(f"total coupon print time: {hh}h {mm:02d}m (vs 10h 36m for plates 1+2+3)")
    finally:
        import shutil
        shutil.rmtree(work, ignore_errors=True)


if __name__ == "__main__":
    main()
