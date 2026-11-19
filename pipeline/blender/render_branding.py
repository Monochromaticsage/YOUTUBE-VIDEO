"""Renders channel branding with the same characters as the videos.

  blender -b -P pipeline/blender/render_branding.py -- --name BLOCKTALES --mascot ziggy --out branding

Outputs: logo.png (800x800), watermark.png (150x150), banner.png (2560x1440),
thumbnail_template.png (1280x720). Change --name / --mascot / --color and re-run.
"""
import argparse
import glob
import json
import math
import os
import sys

import bpy
from mathutils import Vector

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))

import anims  # noqa: E402
import rig as rigmod  # noqa: E402


def parse():
    argv = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else sys.argv[1:]
    p = argparse.ArgumentParser()
    p.add_argument("--name", default="BLOCKTOPIA TALES")
    p.add_argument("--mascot", default="ziggy")
    p.add_argument("--color", default="#6c3ce0", help="brand background colour")
    p.add_argument("--accent", default="#ffd23f", help="title text colour")
    p.add_argument("--out", default=os.path.join(ROOT, "branding"))
    p.add_argument("--engine", default="cycles", choices=["cycles", "eevee"])
    p.add_argument("--samples", type=int, default=24)
    p.add_argument("--only", default="", help="comma list: logo,banner,thumb")
    return p.parse_args(argv)


def find_font():
    cands = glob.glob(os.path.join(ROOT, "assets", "fonts", "*.[ot]tf"))
    cands += [r"C:\Windows\Fonts\ariblk.ttf", r"C:\Windows\Fonts\impact.ttf",
              "/usr/share/fonts/opentype/inter/Inter-Black.otf",
              "/Library/Fonts/Arial Black.ttf", "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"]
    for c in cands:
        if os.path.exists(c):
            return bpy.data.fonts.load(c)
    return None


def reset(args, w, h, bg):
    bpy.ops.wm.read_factory_settings(use_empty=True)
    scn = bpy.context.scene
    scn.render.resolution_x, scn.render.resolution_y = w, h
    scn.render.resolution_percentage = 100
    scn.render.image_settings.file_format = "PNG"
    if args.engine == "cycles":
        scn.render.engine = "CYCLES"
        scn.cycles.samples = args.samples
        scn.cycles.use_denoising = True
    else:
        engines = [i.identifier for i in bpy.types.RenderSettings.bl_rna.properties["engine"].enum_items]
        scn.render.engine = "BLENDER_EEVEE_NEXT" if "BLENDER_EEVEE_NEXT" in engines else "BLENDER_EEVEE"
    try:
        scn.view_settings.view_transform = "Standard"
    except TypeError:
        pass
    world = bpy.data.worlds.new("w")
    scn.world = world
    if not world.node_tree:
        world.use_nodes = True
    nt = world.node_tree
    bgn = nt.nodes.get("Background")
    bgn.inputs["Strength"].default_value = 1.0
    # camera rays see the flat brand colour, lighting comes from a soft white
    lp = nt.nodes.new("ShaderNodeLightPath")
    mix = nt.nodes.new("ShaderNodeMixShader")
    flat = nt.nodes.new("ShaderNodeBackground")
    flat.inputs["Color"].default_value = rigmod.hex_rgba(bg)
    bgn.inputs["Color"].default_value = (0.8, 0.8, 0.85, 1)
    out = nt.nodes.get("World Output")
    nt.links.new(lp.outputs["Is Camera Ray"], mix.inputs["Fac"])
    nt.links.new(bgn.outputs["Background"], mix.inputs[1])
    nt.links.new(flat.outputs["Background"], mix.inputs[2])
    nt.links.new(mix.outputs["Shader"], out.inputs["Surface"])

    sun = bpy.data.objects.new("sun", bpy.data.lights.new("sun", "SUN"))
    sun.data.energy = 3.0
    sun.data.angle = math.radians(10)
    sun.rotation_euler = (math.radians(45), math.radians(-15), math.radians(-35))
    scn.collection.objects.link(sun)
    cam = bpy.data.objects.new("cam", bpy.data.cameras.new("cam"))
    scn.collection.objects.link(cam)
    scn.camera = cam
    return scn, cam


def aim(cam, loc, at):
    cam.location = Vector(loc)
    cam.rotation_euler = (Vector(at) - Vector(loc)).to_track_quat("-Z", "Y").to_euler()


def cast():
    with open(os.path.join(ROOT, "episodes", "cast.json"), encoding="utf-8") as f:
        return json.load(f)


def character(name, spec, loc, yaw, anim, face, frame=1):
    r = rigmod.build_character(name, spec, os.path.join(ROOT, "assets", "faces"))
    r.base, r.base_yaw = loc, yaw
    anims.ANIMS[anim](r, 1, 60, 30)
    s = r.face_mapping.inputs["Location"]
    x, y = rigmod.face_offset(face, False)
    s.default_value = (x, y, 0)
    return r


def text3d(name, body, font, color, size, loc, extrude=0.25, outline=True, spacing=1.0):
    cu = bpy.data.curves.new(name, "FONT")
    cu.body = body
    if font:
        cu.font = font
    cu.size = size
    cu.extrude = extrude
    cu.bevel_depth = 0.04
    cu.align_x = "CENTER"
    cu.align_y = "CENTER"
    cu.space_character = spacing
    ob = bpy.data.objects.new(name, cu)
    bpy.context.scene.collection.objects.link(ob)
    ob.location = loc
    ob.rotation_euler = (math.radians(90), 0, 0)
    ob.data.materials.append(rigmod.make_material(name + "_m", color, 0.35))
    if not outline:
        return ob
    # dark outline copy behind
    sh = ob.copy()
    sh.data = cu.copy()
    sh.scale = (1.035, 1.0, 1.06)
    sh.data.materials.clear()
    sh.data.materials.append(rigmod.make_material(name + "_o", "#1a1033", 0.5))
    sh.location = (loc[0], loc[1] + 0.12, loc[2])
    bpy.context.scene.collection.objects.link(sh)
    return ob


def bricks(color, area, n, seed=3):
    import random
    rnd = random.Random(seed)
    mats = [rigmod.make_material(f"brick{i}", c, 0.5) for i, c in enumerate(
        ["#ffd23f", "#ff5d8f", "#3ddc97", "#4cc9f0", "#ff7a1a"])]
    for i in range(n):
        x = rnd.uniform(*area[0])
        z = rnd.uniform(*area[1])
        me = rigmod.box_mesh(f"br{i}", (rnd.choice([1, 2, 2, 4]), 1, 0.6))
        ob = rigmod.add_obj(f"br{i}", me, None, (x, rnd.uniform(6, 12), z), rnd.choice(mats), bevel=0.06)
        ob.rotation_euler = (rnd.uniform(-0.6, 0.6), rnd.uniform(-0.6, 0.6), rnd.uniform(-0.9, 0.9))


def render(scn, path):
    scn.frame_set(15)  # mid-pose, not the neutral first frame
    scn.render.filepath = path
    bpy.ops.render.render(write_still=True)
    print("[branding] wrote", path, flush=True)


def logo(args, c):
    scn, cam = reset(args, 800, 800, args.color)
    character(args.mascot, c[args.mascot], (0, 0, 0), 14, "idle", "happy")
    cam.data.lens = 50
    aim(cam, (0.9, -5.8, 5.0), (0.05, 0, 4.55))
    path = os.path.join(args.out, "logo.png")
    render(scn, path)
    img = bpy.data.images.load(path)
    img.scale(150, 150)
    img.filepath_raw = os.path.join(args.out, "watermark.png")
    img.file_format = "PNG"
    img.save()
    print("[branding] wrote watermark.png", flush=True)


def banner(args, c):
    scn, cam = reset(args, 2560, 1440, args.color)
    font = find_font()
    # The phone-safe strip is the centre 1546x423 px -> keep everything important there.
    cam.data.type = "ORTHO"
    cam.data.ortho_scale = 38.0           # 38 units across 2560 px -> safe strip ~23 x 6.3 units
    aim(cam, (0, -40, 2.7), (0, 0, 2.7))
    names = [n for n in c if n != args.mascot][:4]
    words = args.name.split()
    if len(args.name) > 11 and len(words) > 1:  # long name -> two lines so it stays phone-safe
        text3d("title", " ".join(words[:-1]), font, args.accent, 2.0, (0, -1.0, 4.35), extrude=0.3)
        text3d("title2", words[-1], font, "#ffffff", 1.35, (0, -1.0, 2.55), extrude=0.25)
        tag_z = 1.15
    else:
        text3d("title", args.name, font, args.accent, 2.3, (0, -1.0, 3.5), extrude=0.3)
        tag_z = 1.5
    text3d("tag", "NEW STORIES EVERY WEEK!", font, "#ffffff", 0.62, (0, -1.0, tag_z), extrude=0.06,
           outline=False, spacing=1.12)
    character(args.mascot, c[args.mascot], (-9.3, 0, 0.05), 20, "wave", "happy")
    left = [(names[0], -13.6, "laugh", "happy")] if names else []
    right = [(n, x, a, f) for n, x, a, f in zip(names[1:], (9.3, 13.6, 17.6), ("shocked", "point", "dance"),
                                                ("shocked", "smug", "happy"))]
    for n, x, a, f in left + right:
        character(n, c[n], (x, 0.8, 0.05), -20 if x > 0 else 20, a, f)
    # character heads would leave the strip; scale cast to fit 5.6 units tall
    for ob in bpy.data.objects:
        if ob.name.endswith("_root"):
            ob.scale = (0.95, 0.95, 0.95)
    bricks(args.color, ((-17, 17), (-9, 14)), 40)
    # clear the safe strip of decoration
    for ob in list(bpy.data.objects):
        if ob.name.startswith("br") and -19 < ob.location.x < 19 and -1.0 < ob.location.z < 6.8:
            bpy.data.objects.remove(ob)
    render(scn, os.path.join(args.out, "banner.png"))


def thumb(args, c):
    scn, cam = reset(args, 1280, 720, "#ffd23f")
    font = find_font()
    character(args.mascot, c[args.mascot], (1.6, 0, 0), -15, "shocked", "shocked")
    names = [n for n in c if n != args.mascot]
    if names:
        character(names[0], c[names[0]], (-3.4, 3.0, 0), 25, "point", "sus")
    cam.data.lens = 32
    aim(cam, (-0.6, -10.5, 5.0), (-0.6, 0, 4.4))
    text3d("t", "WAIT... WHAT?!", font, "#ffffff", 0.75, (-0.6, -3.0, 6.25), extrude=0.15)
    render(scn, os.path.join(args.out, "thumbnail_template.png"))


def lineup(args, c):
    """Character sheet: the whole cast side by side with names."""
    names = list(c)
    scn, cam = reset(args, 2400, 1000, "#f4efe6")
    font = find_font()
    gap = 4.4
    x0 = -gap * (len(names) - 1) / 2
    faces = ["happy", "neutral", "smug", "smug", "sus", "happy", "happy", "happy", "neutral"]
    for i, n in enumerate(names):
        x = x0 + i * gap
        character(n, c[n], (x, 0, 0), 0, "idle", faces[i % len(faces)])
        text3d(f"name{i}", c[n].get("display", n).upper(), font, "#2b2b2b", 0.55, (x, -1.2, -0.75),
               extrude=0.04, outline=False)
    floor = rigmod.add_obj("floor", rigmod.box_mesh("floor", (80, 10, 0.2), (0, 0, 0.1)), None, (0, 2, 0),
                           rigmod.make_material("floor", "#e2d9c8"), bevel=0)
    cam.data.type = "ORTHO"
    cam.data.ortho_scale = gap * len(names) + 1
    aim(cam, (0, -40, 2.6), (0, 0, 2.6))
    render(scn, os.path.join(args.out, "characters.png"))


def main():
    args = parse()
    os.makedirs(args.out, exist_ok=True)
    c = cast()
    if args.mascot not in c:
        raise SystemExit(f"mascot '{args.mascot}' not in episodes/cast.json")
    only = set(args.only.split(",")) if args.only else {"logo", "banner", "thumb", "lineup"}
    if "logo" in only:
        logo(args, c)
    if "banner" in only:
        banner(args, c)
    if "thumb" in only:
        thumb(args, c)
    if "lineup" in only:
        lineup(args, c)


if __name__ == "__main__":
    main()
