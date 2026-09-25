"""
Build the Bambu Studio multi-plate project (bambu/dial-panel-hw-2015.3mf).

Every part is placed on a named plate, pre-oriented for a support-free print,
with its filament slot assigned, so a maker opens one file and prints plate
by plate:

   1  Face plate, screen            black PLA
   2  Back shell, screen            black PLA
   3  Control column (01b + 02b)    black PLA
   4  Speaker cup, cleat, rail      black PLA
   5  Trim + knob                   silver silk PLA
   6  Gold tab                      yellow PLA
   7  Band diffuser                 clear PETG
   8  IGNITION band insert          black PLA  } print 8 OR 9
   9  NIGHTFALL band insert         black PLA  }

Pipeline (needs FreeCAD and Bambu Studio installed):
  1. flatten Bambu's A1 system profiles (the CLI does not resolve `inherits`)
  2. orient every part from cad/step/ by cad/print_rotations.json (FreeCAD),
     and verify it: on the bed, fits the bed, volume unchanged
  3. build the plates with Bambu Studio's --load-assemble-list
  4. finish: filament colours, Textured PEI plate, clean names, metadata
  5. slice every plate as a check; any plate that fails or warns fails the build

It also writes the same print-oriented meshes to stl/ (common/, ignition/, nightfall/).

    python3 bambu/build_project.py            # from the repo root
    python3 bambu/build_project.py --no-slice # skip the slicing check

Environment overrides: FREECADCMD, BAMBU_STUDIO, BAMBU_PROFILES.
"""
import argparse
import io
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
import zipfile

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(HERE)
STEP_DIR = os.path.join(REPO, "cad", "step")
OUT = os.path.join(HERE, "dial-panel-hw-2015.3mf")

FREECADCMD = os.environ.get("FREECADCMD", "/Applications/FreeCAD.app/Contents/Resources/bin/freecadcmd")
BAMBU = os.environ.get("BAMBU_STUDIO", "/Applications/BambuStudio.app/Contents/MacOS/BambuStudio")
PROFILES = os.environ.get("BAMBU_PROFILES", "/Applications/BambuStudio.app/Contents/Resources/profiles/BBL")

PRINTER = "Bambu Lab A1 0.4 nozzle"
PROCESS = "0.20mm Standard @BBL A1"
# filament slot -> (Bambu system profile, colour)
FILAMENTS = [
    ("Bambu PLA Matte @BBL A1", "#1B1B1D"),   # 1 matte black: body
    ("Bambu PLA Silk @BBL A1", "#C7CACF"),    # 2 silver silk: the "chrome"
    ("Bambu PLA Basic @BBL A1", "#F5C842"),   # 3 yellow: the gold tab
    ("Bambu PETG HF @BBL A1", "#E6EEF2"),     # 4 clear PETG: the diffuser
]
BED_TYPE = "Textured PEI Plate"   # what the A1 ships with; PETG isn't allowed on the Cool Plate

PLATES = [
    ("1 · Face plate, screen · black PLA", [("01a-face-plate-screen", 1)]),
    ("2 · Back shell, screen · black PLA", [("02a-back-shell-screen", 1)]),
    ("3 · Control column · black PLA", [("01b-face-plate-column", 1), ("02b-back-shell-column", 1)]),
    ("4 · Speaker cup, wall cleat, receiver rail · black PLA",
     [("08-speaker-back-cup", 1), ("11-wall-cleat", 1), ("12-cleat-receiver-rail", 1)]),
    ("5 · Trim + knob · silver silk PLA", [("03-screen-trim", 2), ("06-knob", 2)]),
    ("6 · Gold tab · yellow PLA", [("07-gold-tab", 3)]),
    ("7 · Band diffuser · clear PETG", [("05-band-diffuser", 4)]),
    ("8 · IGNITION band insert (print 8 OR 9) · black PLA", [("04a-band-insert-ignition", 1)]),
    ("9 · NIGHTFALL band insert (print 8 OR 9) · black PLA", [("04b-band-insert-nightfall", 1)]),
]

META = {
    "Title": "Dial Panel (hw-2015)",
    "Designer": "SlashBuilder",
    "License": "CC-BY-4.0",
    "Description": "A wall-mounted smart-home panel driven by one push-dial. Every part is pre-oriented for a "
                   "support-free print. Plates 1-7 are common to every build; print EITHER plate 8 (A IGNITION) "
                   "OR plate 9 (B NIGHTFALL). Source, BOM and assembly: github.com/slash-builder/hw-2015-dial-panel",
}

# Print orientations come from the CAD itself (cad/print_rotations.json,
# written by cad/generate_parts.py): one source of truth. Each entry is the
# rotation applied to the part as exported in cad/step/.
ROTATIONS = os.path.join(REPO, "cad", "print_rotations.json")

ORIENT_SCRIPT = r'''
import os, json, Part, MeshPart, FreeCAD as App
STEP_DIR, OUT, ROT = os.environ["STEP_DIR"], os.environ["ORIENT_OUT"], json.load(open(os.environ["ROTATIONS"]))
def planar(s): return [f for f in s.Faces if f.Surface.TypeId == "Part::GeomPlane"]
report = {}
for fn in sorted(os.listdir(STEP_DIR)):
    if not fn.endswith(".step") or fn.startswith("assembly"): continue
    name = fn[:-5]
    if name not in ROT: raise SystemExit("no print rotation for " + name + " in cad/print_rotations.json")
    r = ROT[name]
    s = Part.Shape(); s.read(os.path.join(STEP_DIR, fn))
    t = s.copy(); t.Placement = App.Placement(App.Vector(), App.Rotation(App.Vector(*r["axis"]), r["angle_deg"])) * t.Placement; t = t.copy()
    b = t.BoundBox; t.translate(App.Vector(-(b.XMin + b.XMax) / 2, -(b.YMin + b.YMax) / 2, -b.ZMin)); b = t.BoundBox
    contact = sum(f.Area for f in planar(t) if abs(f.BoundBox.ZMax) < 1e-4 and abs(f.BoundBox.ZMin) < 1e-4)
    MeshPart.meshFromShape(Shape=t, LinearDeflection=0.05, AngularDeflection=0.26, Relative=False).write(os.path.join(OUT, name + ".stl"))
    report[name] = {"size": [round(b.XLength, 1), round(b.YLength, 1), round(b.ZLength, 1)],
                    "contact_mm2": round(contact), "volume_ok": abs(t.Volume - s.Volume) < 1e-3 * s.Volume}
json.dump(report, open(os.path.join(OUT, "report.json"), "w"), indent=1)
'''


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
            # Real print, 2026-09-25: stringing across the speaker opening
            # and the light vents on 02a. Both are holes the nozzle has to
            # cross on every layer, and with this off the travel goes
            # straight over the void, dragging a strand each time. Solid
            # areas of the same print are clean, which is the tell.
            ps["reduce_crossing_wall"] = "1"   # "Avoid crossing walls"
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
    if not os.path.exists(ROTATIONS):
        sys.exit("cad/print_rotations.json not found: run cad/generate_parts.py first")
    for tool in (FREECADCMD, BAMBU):
        if not os.path.exists(tool):
            sys.exit(f"not found: {tool} (set FREECADCMD / BAMBU_STUDIO)")
    work = tempfile.mkdtemp(prefix="dial-panel-3mf-")
    try:
        # 1. profiles
        paths = {}
        colour_of = dict(FILAMENTS)
        for kind, name in [("machine", PRINTER), ("process", PROCESS)] + [("filament", f) for f, _ in FILAMENTS]:
            p = os.path.join(work, f"{kind}-{name}.json")
            d = flatten(kind, name)
            if kind == "filament":   # colour set before the build, so Bambu renders the plate thumbnails in it
                d["filament_colour"] = [colour_of[name]]
            json.dump(d, open(p, "w"), indent=1)
            paths.setdefault(kind, []).append(p)

        # 2. orient
        oriented = os.path.join(work, "oriented")
        os.makedirs(oriented)
        script = os.path.join(work, "orient.py")
        open(script, "w").write(ORIENT_SCRIPT)
        r = run([FREECADCMD, script], env={**os.environ, "STEP_DIR": STEP_DIR, "ORIENT_OUT": oriented,
                                            "ROTATIONS": ROTATIONS})
        rep_path = os.path.join(oriented, "report.json")
        if not os.path.exists(rep_path):
            sys.exit("orientation step failed:\n" + r.stdout[-2000:] + r.stderr[-2000:])
        report = json.load(open(rep_path))
        bed = [int(v) for v in flatten("machine", PRINTER)["printable_area"][2].split("x")]
        bad = []
        print("orientation:")
        for name, rr in report.items():
            x, y, z = rr["size"]
            ok = rr["volume_ok"] and x <= bed[0] and y <= bed[1] and rr["contact_mm2"] > 0
            print(f"  {name:28s} {x:6.1f} x {y:6.1f} x {z:5.1f}  bed contact {rr['contact_mm2']:6d} mm2  {'ok' if ok else 'FAIL'}")
            if not ok:
                bad.append(name)
        if bad:
            sys.exit(f"orientation check failed: {bad}")

        # the release STLs are the same print-oriented meshes, so every slicer
        # gets parts that are ready to print, and they can't drift from the 3MF
        teams = {"04a-band-insert-ignition": "ignition", "04b-band-insert-nightfall": "nightfall"}
        for name in report:
            dest = os.path.join(REPO, "stl", teams.get(name, "common"))
            os.makedirs(dest, exist_ok=True)
            shutil.copyfile(os.path.join(oriented, name + ".stl"), os.path.join(dest, name + ".stl"))
        print(f"updated stl/ with {len(report)} print-oriented parts")

        # 3. plates
        assemble = {"plates": [{"plate_name": pname, "need_arrange": True, "plate_params": {},
                                "objects": [{"path": os.path.join(oriented, n + ".stl"), "count": 1, "filaments": [slot],
                                             "pos_x": [0.0], "pos_y": [0.0], "pos_z": [0.0]} for n, slot in objs]}
                               for pname, objs in PLATES]}
        alist = os.path.join(work, "assemble.json")
        json.dump(assemble, open(alist, "w"), indent=1)
        raw = os.path.join(work, "raw.3mf")
        r = run([BAMBU, "--load-settings", ";".join(paths["machine"] + paths["process"]),
                 "--load-filaments", ";".join(paths["filament"]), "--load-assemble-list", alist,
                 "--outputdir", work, "--export-3mf", "raw.3mf"], cwd=work)
        res = json.load(open(os.path.join(work, "result.json")))
        if res.get("return_code") != 0 or not os.path.exists(raw):
            sys.exit(f"Bambu Studio could not build the plates: {res.get('error_string')}")

        # 4. finish
        finish(raw, OUT)
        print(f"wrote {os.path.relpath(OUT, REPO)} ({os.path.getsize(OUT) / 1e6:.2f} MB, {len(PLATES)} plates)")

        # 5. slice check
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
                    print(f"  {f:14s} {t.group(1).strip() if t else '?'}")
            if res.get("return_code") != 0:
                sys.exit(f"slicing failed: {res.get('error_string')}")
            if warns:
                sys.exit("slicing warnings:\n  " + "\n  ".join(warns))
            print("slice check: every plate sliced, no warnings")
    finally:
        shutil.rmtree(work, ignore_errors=True)


if __name__ == "__main__":
    main()
