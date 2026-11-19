"""Builds an episode in Blender from its JSON file and renders PNG frames.

Run with Blender (headless):
  blender -b -P pipeline/blender/render_episode.py -- --episode episodes/shorts/short_001.json \
      --timing build/short_001/timing.json --out build/short_001/frames

You normally don't call this directly - use pipeline/make_episode.py.
"""
import argparse
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
import sets  # noqa: E402

SCENE_SPACING = 400.0  # each scene's set is built this far apart on X

FORMATS = {"short": (1080, 1920), "long": (1920, 1080)}


def parse_args():
    argv = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else sys.argv[1:]
    p = argparse.ArgumentParser()
    p.add_argument("--episode", required=True)
    p.add_argument("--timing", required=True)
    p.add_argument("--out", required=True)
    p.add_argument("--engine", default="eevee", choices=["eevee", "cycles", "workbench"])
    p.add_argument("--samples", type=int, default=0, help="0 = engine default")
    p.add_argument("--scale", type=int, default=100, help="resolution percentage (50 = fast preview)")
    p.add_argument("--frames", default="", help="optional START:END to render a slice")
    p.add_argument("--step", type=int, default=1, help="render every Nth frame (quick checks)")
    p.add_argument("--save-blend", default="", help="also save the built .blend here (to inspect/tweak)")
    return p.parse_args(argv)


def load_episode(path):
    with open(path, encoding="utf-8") as f:
        ep = json.load(f)
    cast_path = os.path.join(ROOT, "episodes", "cast.json")
    cast = {}
    if os.path.exists(cast_path):
        with open(cast_path, encoding="utf-8") as f:
            cast = json.load(f)
    chars = {}
    used = set()
    for sc in ep["scenes"]:
        used.update(sc["cast"].keys())
    for name in used:
        spec = dict(cast.get(name, {}))
        spec.update(ep.get("characters", {}).get(name, {}))
        chars[name] = spec
    ep["_chars"] = chars
    return ep


# ---------------------------------------------------------------------- moods
# Lighting + fog presets. "golden" / "dusk" / "night" give the cinematic hazy look.
MOODS = {
    "day":    dict(sky="#cfe6ff", zenith="#5ea4ec", sky_strength=0.9, sun=3.2, sun_color="#fff6e8", sun_elev=40, sun_az=-30,
                   fill=0.8, fill_color="#cfe0ff", fog="#bcd8f5", fog_start=25, fog_end=140, fog_max=0.55),
    "golden": dict(sky="#f0b487", zenith="#5f86c4", sky_strength=0.7, sun=4.2, sun_color="#ffc48e", sun_elev=16,
                   sun_az=-55, fill=1.0, fill_color="#5d8fd8", fog="#e8b48a", fog_start=30, fog_end=130,
                   fog_max=0.7),
    "dusk":   dict(sky="#e08a6e", zenith="#3b3f78", sky_strength=0.55, sun=3.0, sun_color="#ff8a5c", sun_elev=6, sun_az=-60,
                   fill=0.9, fill_color="#5b78c9", fog="#8a6e9e", fog_start=8, fog_end=70, fog_max=0.8),
    "night":  dict(sky="#26305a", zenith="#0a0e1f", sky_strength=0.35, sun=0.8, sun_color="#9fb4ff", sun_elev=35, sun_az=20,
                   fill=0.35, fill_color="#3a4f8f", fog="#1d2747", fog_start=6, fog_end=55, fog_max=0.85),
    "indoor": dict(sky="#d9c7a8", sky_strength=0.8, sun=2.6, sun_color="#ffd9a8", sun_elev=35, sun_az=-40,
                   fill=0.9, fill_color="#bcd0ff", fog="#d9c2a0", fog_start=14, fog_end=90, fog_max=0.4),
}


def apply_fog(mood):
    """Distance haze baked into every material: surfaces fade toward the fog colour
    with distance from the camera. Cheap in both Cycles and EEVEE (no volumetrics)."""
    fog = rigmod.hex_rgba(mood["fog"])
    for mat in bpy.data.materials:
        nt = mat.node_tree if mat.use_nodes else None
        if not nt:
            continue
        out = next((n for n in nt.nodes if n.type == "OUTPUT_MATERIAL"), None)
        if not out or not out.inputs["Surface"].links:
            continue
        src = out.inputs["Surface"].links[0].from_socket
        cam = nt.nodes.new("ShaderNodeCameraData")
        rng = nt.nodes.new("ShaderNodeMapRange")
        rng.inputs["From Min"].default_value = mood["fog_start"]
        rng.inputs["From Max"].default_value = mood["fog_end"]
        rng.inputs["To Max"].default_value = mood["fog_max"]
        emit = nt.nodes.new("ShaderNodeEmission")
        emit.inputs["Color"].default_value = fog
        emit.inputs["Strength"].default_value = 1.0
        mix = nt.nodes.new("ShaderNodeMixShader")
        nt.links.new(cam.outputs["View Distance"], rng.inputs["Value"])
        nt.links.new(rng.outputs["Result"], mix.inputs["Fac"])
        nt.links.new(src, mix.inputs[1])
        nt.links.new(emit.outputs["Emission"], mix.inputs[2])
        nt.links.new(mix.outputs["Shader"], out.inputs["Surface"])


# --------------------------------------------------------------------- setup
def setup_scene(ep, args):
    bpy.ops.wm.read_factory_settings(use_empty=True)
    scn = bpy.context.scene
    fps = ep.get("fps", 30)
    scn.render.fps = fps
    w, h = FORMATS[ep.get("format", "short")]
    scn.render.resolution_x, scn.render.resolution_y = w, h
    scn.render.resolution_percentage = args.scale
    scn.render.image_settings.file_format = "PNG"
    scn.render.image_settings.color_mode = "RGB"

    engines = [i.identifier for i in bpy.types.RenderSettings.bl_rna.properties["engine"].enum_items]
    if args.engine == "cycles":
        scn.render.engine = "CYCLES"
        scn.cycles.device = "CPU"
        scn.cycles.samples = args.samples or 48
        scn.cycles.use_denoising = True
        try:  # use the GPU if this machine has one
            prefs = bpy.context.preferences.addons["cycles"].preferences
            for kind in ("OPTIX", "CUDA", "HIP", "METAL", "ONEAPI"):
                try:
                    prefs.compute_device_type = kind
                    prefs.get_devices()
                    if any(d.type == kind for d in prefs.devices):
                        for d in prefs.devices:
                            d.use = True
                        scn.cycles.device = "GPU"
                        break
                except TypeError:
                    continue
        except Exception:
            pass
    elif args.engine == "workbench":
        scn.render.engine = "BLENDER_WORKBENCH"
        sh = scn.display.shading
        sh.light = "STUDIO"
        sh.color_type = "TEXTURE"
        sh.show_shadows = True
        sh.show_cavity = True
    else:
        scn.render.engine = "BLENDER_EEVEE_NEXT" if "BLENDER_EEVEE_NEXT" in engines else "BLENDER_EEVEE"
        ee = scn.eevee
        if args.samples:
            ee.taa_render_samples = args.samples
        for attr, val in (("use_shadows", True), ("use_raytracing", True), ("use_gtao", True)):
            if hasattr(ee, attr):
                setattr(ee, attr, val)

    try:
        scn.view_settings.view_transform = "Standard"  # punchy Roblox colours (AgX looks washed out)
    except TypeError:
        pass

    mood = MOODS[ep.get("mood", "day")]
    world = bpy.data.worlds.new("world")
    scn.world = world
    if not world.node_tree:
        world.use_nodes = True
    bg = world.node_tree.nodes.get("Background")
    bg.inputs["Color"].default_value = rigmod.hex_rgba(ep.get("sky", mood["sky"]))
    bg.inputs["Strength"].default_value = mood["sky_strength"]
    world.color = bg.inputs["Color"].default_value[:3]
    if mood.get("zenith"):  # vertical gradient: horizon colour -> zenith colour
        wn = world.node_tree
        tc = wn.nodes.new("ShaderNodeTexCoord")
        sep = wn.nodes.new("ShaderNodeSeparateXYZ")
        rng = wn.nodes.new("ShaderNodeMapRange")
        rng.inputs["From Min"].default_value = -0.02
        rng.inputs["From Max"].default_value = 0.55
        ramp = wn.nodes.new("ShaderNodeValToRGB")
        ramp.color_ramp.elements[0].color = rigmod.hex_rgba(ep.get("sky", mood["sky"]))
        ramp.color_ramp.elements[1].color = rigmod.hex_rgba(mood["zenith"])
        wn.links.new(tc.outputs["Generated"], sep.inputs["Vector"])
        wn.links.new(sep.outputs["Z"], rng.inputs["Value"])
        wn.links.new(rng.outputs["Result"], ramp.inputs["Fac"])
        wn.links.new(ramp.outputs["Color"], bg.inputs["Color"])

    sun_data = bpy.data.lights.new("sun", "SUN")
    sun_data.energy = mood["sun"]
    sun_data.color = rigmod.hex_rgba(mood["sun_color"])[:3]
    sun_data.angle = math.radians(6)
    sun = bpy.data.objects.new("sun", sun_data)
    scn.collection.objects.link(sun)
    sun.rotation_euler = (math.radians(90 - mood["sun_elev"]), math.radians(-8), math.radians(mood["sun_az"]))

    fill_data = bpy.data.lights.new("fill", "SUN")
    fill_data.energy = mood["fill"]
    fill_data.color = rigmod.hex_rgba(mood["fill_color"])[:3]
    fill_data.use_shadow = False
    fill = bpy.data.objects.new("fill", fill_data)
    scn.collection.objects.link(fill)
    fill.rotation_euler = (math.radians(70), 0, math.radians(mood["sun_az"] + 170))

    cam_data = bpy.data.cameras.new("cam")
    cam_data.lens = 30 if ep.get("format", "short") == "short" else 35
    cam_data.dof.use_dof = ep.get("dof", True)
    cam = bpy.data.objects.new("cam", cam_data)
    scn.collection.objects.link(cam)
    scn.camera = cam
    return scn, cam


# -------------------------------------------------------------------- camera
HEAD_Z = 4.6
CHEST_Z = 3.4


def camera_pose(spec, rigs, scene_origin, fmt):
    """Returns (location, look_at, lens) for a camera spec string.

    Specs:  wide | medium:<name> | closeup:<name> | extreme:<name>
            two:<a>,<b> | ots:<over>,<at> (over-the-shoulder) | low:<name> | high:<name>
    """
    kind, _, arg = spec.partition(":")
    names = [n.strip() for n in arg.split(",") if n.strip()]
    tall = fmt == "short"

    def pos(n):
        if n not in rigs:
            raise ValueError(f"camera target '{n}' is not in this scene's cast")
        return Vector(rigs[n].base)

    def front(n, off):
        # rotate a camera offset so single-character shots face the character
        from mathutils import Matrix
        yaw = math.radians(rigs[n].base_yaw * 0.8)
        return Matrix.Rotation(yaw, 3, "Z") @ Vector(off)

    o = Vector(scene_origin)
    if kind == "wide":
        c = sum((pos(n) for n in rigs), Vector()) / max(1, len(rigs)) if rigs else o
        return c + Vector((0, -22 if tall else -18, 7)), c + Vector((0, 0, 3)), 28
    if kind == "medium":
        p = pos(names[0])
        return p + front(names[0], (0, -10 if tall else -9, 4.2)), p + Vector((0, 0, CHEST_Z)), 35
    if kind == "closeup":
        p = pos(names[0])
        return p + front(names[0], (0, -6.5, HEAD_Z + 0.4)), p + Vector((0, 0, HEAD_Z - 0.4)), 40
    if kind == "extreme":
        p = pos(names[0])
        return p + front(names[0], (0, -4.2, HEAD_Z + 0.1)), p + Vector((0, 0, HEAD_Z)), 50
    if kind == "two":
        a, b = pos(names[0]), pos(names[1])
        mid = (a + b) / 2
        gap = (a - b).length
        dist = max(9.0, 1.6 * (gap + 4)) if tall else 9 + gap * 0.9  # fit both bodies in frame
        return mid + Vector((0, -dist, 4.5)), mid + Vector((0, 0, CHEST_Z)), 32
    if kind == "ots":
        over, at = pos(names[0]), pos(names[1])
        d = (at - over)
        d.z = 0
        d = d.normalized() if d.length else Vector((1, 0, 0))
        side = Vector((-d.y, d.x, 0))
        loc = over - d * 3.0 + side * 1.4 + Vector((0, -2.5, HEAD_Z + 0.6))
        return loc, at + Vector((0, 0, HEAD_Z - 0.4)), 38
    if kind == "low":
        p = pos(names[0])
        return p + front(names[0], (0, -7, 0.8)), p + Vector((0, 0, HEAD_Z - 0.5)), 26
    if kind == "high":
        p = pos(names[0])
        return p + Vector((0, -6, 12)), p + Vector((0, 0, 2.5)), 32
    raise ValueError(f"unknown camera '{spec}'")


def key_camera(cam, f0, f1, spec, rigs, origin, fmt, move, roll_deg=0.0):
    loc, at, lens = camera_pose(spec, rigs, origin, fmt)
    end_loc = Vector(loc)
    if move == "push":       # slow push-in (default, feels cinematic)
        end_loc = loc + (at - loc) * 0.10
    elif move == "pull":
        end_loc = loc - (at - loc) * 0.12
    elif move == "pan":
        end_loc = loc + Vector((1.5, 0, 0))
    elif move == "zoom":     # fast meme zoom
        end_loc = loc + (at - loc) * 0.55
    kind = spec.partition(":")[0]
    fstop = {"extreme": 1.4, "closeup": 1.8, "low": 2.2, "ots": 2.2, "medium": 2.8, "two": 4.0,
             "high": 4.0, "wide": 7.0}.get(kind, 2.8)
    roll = math.radians(roll_deg)
    for frame, l in ((f0, loc), (f1 - 1, end_loc)):
        cam.location = l
        q = (at - l).to_track_quat("-Z", "Y")
        e = q.to_euler()
        if roll:
            from mathutils import Quaternion
            e = (q @ Quaternion((0, 0, 1), roll)).to_euler()
        cam.rotation_euler = e
        cam.data.lens = lens
        cam.data.dof.focus_distance = (at - l).length
        cam.data.dof.aperture_fstop = fstop
        cam.keyframe_insert("location", frame=frame)
        cam.keyframe_insert("rotation_euler", frame=frame)
        cam.data.keyframe_insert("lens", frame=frame)
        cam.data.keyframe_insert("dof.focus_distance", frame=frame)
        cam.data.keyframe_insert("dof.aperture_fstop", frame=frame)
    if move == "shake":
        for i, f in enumerate(range(f0 + 1, f1 - 1, 2)):
            cam.location = loc + Vector(((-0.15, 0.15)[i % 2], 0, (0.1, -0.1)[(i // 2) % 2]))
            cam.keyframe_insert("location", frame=f)


# --------------------------------------------------------------------- faces
def key_face(r, frame, expr, mouth_open):
    x, y = rigmod.face_offset(expr, mouth_open)
    sock = r.face_mapping.inputs["Location"]
    sock.default_value = (x, y, 0)
    sock.keyframe_insert("default_value", frame=frame)


def key_faces_for_shot(r, f0, f1, expr, speaking, mouth_track):
    key_face(r, f0, expr, False)
    if speaking:
        if mouth_track:
            prev = None
            for i, m in enumerate(mouth_track):
                f = f0 + i
                if f >= f1 - 1:
                    break
                if m != prev:
                    key_face(r, f, expr, bool(m))
                    prev = m
        else:  # no audio: generic flap
            for i, f in enumerate(range(f0, f1 - 4, 4)):
                key_face(r, f, expr, i % 2 == 0)
    key_face(r, f1 - 1, expr, False)


# ---------------------------------------------------------------------- cuts
def fcurves_of(idblock):
    ad = idblock.animation_data
    if not ad or not ad.action:
        return []
    act = ad.action
    if hasattr(act, "layers") and len(act.layers):  # Blender 4.4+ layered actions
        out = []
        for layer in act.layers:
            for strip in layer.strips:
                cb = strip.channelbag(ad.action_slot)
                if cb:
                    out.extend(cb.fcurves)
        return out
    return list(getattr(act, "fcurves", []))


def harden_cuts(cut_frames):
    """Make the jump between the last frame of a shot and the first of the next a hard
    cut, and stop the big jump from bending the motion inside the shot."""
    ids = list(bpy.data.objects) + list(bpy.data.cameras) + list(bpy.data.materials)
    ids += [m.node_tree for m in bpy.data.materials if m.node_tree]
    for nt in [m.node_tree for m in bpy.data.materials if m.node_tree]:
        for fc in fcurves_of(nt):  # face swaps must snap, never slide
            for kp in fc.keyframe_points:
                kp.interpolation = "CONSTANT"
    for idb in ids:
        for fc in fcurves_of(idb):
            if idb in [m.node_tree for m in bpy.data.materials]:
                continue
            for kp in fc.keyframe_points:
                f = round(kp.co[0])
                if f in cut_frames:
                    kp.interpolation = "CONSTANT"
                    kp.handle_left_type = kp.handle_right_type = "VECTOR"
                elif f - 1 in cut_frames:
                    kp.handle_left_type = kp.handle_right_type = "VECTOR"
            fc.update()


# ---------------------------------------------------------------------- main
def main():
    args = parse_args()
    ep = load_episode(args.episode)
    with open(args.timing, encoding="utf-8") as f:
        timing = json.load(f)
    fmt = ep.get("format", "short")
    scn, cam = setup_scene(ep, args)
    fps = scn.render.fps
    faces_dir = os.path.join(ROOT, "assets", "faces")

    prefs = bpy.context.preferences.edit
    prefs.keyframe_new_interpolation_type = "BEZIER"
    rigs_all = {n: rigmod.build_character(n, spec, faces_dir) for n, spec in ep["_chars"].items()}

    frame = 1
    shot_i = 0
    cut_frames = set()
    for si, sc in enumerate(ep["scenes"]):
        origin = (si * SCENE_SPACING, 0, 0)
        marks = sets.build_set(sc.get("set", "stage"), origin, os.path.join(ROOT, "assets"))
        scene_rigs = {}
        for name, mark in sc["cast"].items():
            r = rigs_all[name]
            m = marks.get(mark) if isinstance(mark, str) else tuple(mark)
            if m is None:
                raise ValueError(f"unknown mark '{mark}'. Marks for this set: {sorted(marks)}")
            r.base = (origin[0] + m[0], origin[1] + m[1], origin[2] + m[2])
            scene_rigs[name] = r
        # turn characters slightly toward each other
        cx = sum(r.base[0] for r in scene_rigs.values()) / max(1, len(scene_rigs))
        for r in scene_rigs.values():
            r.base_yaw = max(-30.0, min(30.0, -(r.base[0] - cx) * 9.0))

        for shot in sc["shots"]:
            t = timing["shots"][shot_i]
            n_frames = max(2, round(t["duration"] * fps))
            f0, f1 = frame, frame + n_frames
            speaker = shot.get("speaker")
            shot_anims = shot.get("anims", {})
            faces = shot.get("faces", {})

            prefs.keyframe_new_interpolation_type = "BEZIER"
            for name, r in rigs_all.items():
                if name not in scene_rigs:
                    anims.hidden(r, f0, f1, fps)
                    continue
                default = "talk" if name == speaker else "idle"
                anim_name = shot_anims.get(name, default)
                if anim_name not in anims.ANIMS:
                    raise ValueError(f"unknown anim '{anim_name}'. Available: {sorted(anims.ANIMS)}")
                anims.ANIMS[anim_name](r, f0, f1, fps)

            key_camera(cam, f0, f1, shot.get("camera", f"medium:{speaker}" if speaker else "wide"),
                       scene_rigs, origin, fmt, shot.get("move", "push"))

            prefs.keyframe_new_interpolation_type = "CONSTANT"
            for name, r in scene_rigs.items():
                expr = shot.get("face", "neutral") if name == speaker else faces.get(name, "neutral")
                if name == speaker and "face" not in shot:
                    expr = faces.get(name, "neutral")
                key_faces_for_shot(r, f0, f1, expr, name == speaker and bool(shot.get("line")),
                                   t.get("mouth"))
            prefs.keyframe_new_interpolation_type = "BEZIER"
            cut_frames.add(f1 - 1)
            frame = f1
            shot_i += 1

    scn.frame_start = 1
    scn.frame_end = frame - 1
    if args.frames:
        a, b = args.frames.split(":")
        scn.frame_start, scn.frame_end = int(a), int(b)
    scn.frame_step = args.step
    if ep.get("fog", True):
        apply_fog(MOODS[ep.get("mood", "day")])
    harden_cuts(cut_frames)
    os.makedirs(args.out, exist_ok=True)
    if args.save_blend:
        bpy.ops.wm.save_as_mainfile(filepath=os.path.abspath(args.save_blend))
    scn.render.filepath = os.path.join(os.path.abspath(args.out), "frame_")
    print(f"[render] {scn.frame_end - scn.frame_start + 1} frames, engine={scn.render.engine}", flush=True)
    bpy.ops.render.render(animation=True)
    print("[render] done", flush=True)


if __name__ == "__main__":
    main()
