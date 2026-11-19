"""One command: episode JSON -> finished MP4 in output/.

  python pipeline/make_episode.py episodes/shorts/short_001.json
  python pipeline/make_episode.py episodes/shorts/short_001.json --preview     (fast, half-res)
  python pipeline/make_episode.py episodes/shorts/*.json                       (batch)

Options: --engine eevee|cycles|workbench   --scale 50   --samples 16   --force-voice
         --save-blend   (also saves build/<id>/scene.blend so you can open and tweak it in Blender)

Blender is found from $BLENDER (path to blender.exe), then PATH, then the usual install folders.
"""
import argparse
import glob
import json
import os
import shutil
import subprocess
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, ".."))
sys.path.insert(0, HERE)

import assemble  # noqa: E402
import voice  # noqa: E402


def find_blender():
    cand = [os.environ.get("BLENDER"), shutil.which("blender")]
    cand += sorted(glob.glob(r"C:\Program Files\Blender Foundation\Blender*\blender.exe"), reverse=True)
    cand += ["/Applications/Blender.app/Contents/MacOS/Blender"]
    for c in cand:
        if c and os.path.exists(c):
            return [c, "-b", "-P"]
    try:  # Blender as a Python module (pip install bpy) - used for testing
        import importlib.util
        if importlib.util.find_spec("bpy"):
            return [sys.executable]
    except Exception:
        pass
    raise SystemExit("Blender not found. Install it from blender.org or set BLENDER=<path to blender.exe>")


def validate(ep, cast):
    sys.path.insert(0, os.path.join(HERE, "blender"))
    import anims  # pure python, safe to import without Blender
    known_anims = set(anims.ANIMS)
    faces = {"neutral", "happy", "smug", "angry", "sad", "shocked", "scared", "sus", "cry", "dead", "evil", "love"}
    errs = []
    for si, sc in enumerate(ep["scenes"]):
        for n in sc["cast"]:
            if n not in cast and n not in ep.get("characters", {}):
                errs.append(f"scene {si}: '{n}' is not in episodes/cast.json")
        for hi, sh in enumerate(sc["shots"]):
            where = f"scene {si} shot {hi}"
            if sh.get("speaker") and sh["speaker"] not in sc["cast"] and not sh.get("vo"):
                errs.append(f"{where}: speaker '{sh['speaker']}' not in scene cast")
            for n, a in sh.get("anims", {}).items():
                if a not in known_anims:
                    errs.append(f"{where}: unknown anim '{a}'")
                if n not in sc["cast"]:
                    errs.append(f"{where}: anim for '{n}' who is not in the scene")
            for f in [sh.get("face")] + list(sh.get("faces", {}).values()):
                if f and f not in faces:
                    errs.append(f"{where}: unknown face '{f}'")
    if errs:
        raise SystemExit("Episode has problems:\n  " + "\n  ".join(errs))


def make(path, args):
    t0 = time.time()
    with open(path, encoding="utf-8") as f:
        ep = json.load(f)
    with open(os.path.join(ROOT, "episodes", "cast.json"), encoding="utf-8") as f:
        cast = json.load(f)
    validate(ep, cast)
    eid = ep["id"]
    build_dir = os.path.join(ROOT, "build", eid)
    frames_dir = os.path.join(build_dir, "frames")
    os.makedirs(build_dir, exist_ok=True)
    print(f"=== {eid}: {ep.get('title', '')}")

    timing = voice.build(ep, cast, build_dir, force=args.force_voice)

    shutil.rmtree(frames_dir, ignore_errors=True)
    scale = 50 if args.preview and not args.scale else (args.scale or 100)
    cmd = find_blender() + [os.path.join(HERE, "blender", "render_episode.py"), "--",
                            "--episode", os.path.abspath(path), "--timing", os.path.join(build_dir, "timing.json"),
                            "--out", frames_dir, "--engine", args.engine, "--scale", str(scale),
                            "--samples", str(args.samples or (8 if args.preview else 0))]
    if args.save_blend:
        cmd += ["--save-blend", os.path.join(build_dir, "scene.blend")]
    subprocess.run(cmd, check=True)

    os.makedirs(os.path.join(ROOT, "output"), exist_ok=True)
    out = os.path.join(ROOT, "output", f"{eid}{'_preview' if args.preview else ''}.mp4")
    assemble.assemble(ep, timing, cast, build_dir, out)
    print(f"=== done in {time.time() - t0:.0f}s -> {out}\n")
    return out


def main():
    p = argparse.ArgumentParser()
    p.add_argument("episodes", nargs="+")
    p.add_argument("--engine", default="eevee", choices=["eevee", "cycles", "workbench"])
    p.add_argument("--preview", action="store_true")
    p.add_argument("--scale", type=int, default=0)
    p.add_argument("--samples", type=int, default=0)
    p.add_argument("--force-voice", action="store_true")
    p.add_argument("--save-blend", action="store_true")
    args = p.parse_args()
    paths = []
    for e in args.episodes:
        paths += sorted(glob.glob(e)) or [e]
    for path in paths:
        make(path, args)


if __name__ == "__main__":
    main()
