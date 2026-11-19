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
        vis = [n for n in rigs if not getattr(rigs[n], "hidden_now", False)] or list(rigs)
        c = sum((pos(n) for n in vis), Vector()) / max(1, len(vis)) if rigs else o
        return c + Vector((0, -24 if tall else -18, 10 if tall else 7)), c + Vector((0, 0, 2.2)), 30
    if kind == "medium":
        p = pos(names[0])
        return p + front(names[0], (0, -10 if tall else -9, 4.2)), p + Vector((0, 0, CHEST_Z)), 35
    if kind == "closeup":
        p = pos(names[0])
        return p + front(names[0], (0, -6.5, HEAD_Z + 0.4)), p + Vector((0, 0, HEAD_Z - 0.4)), 40
    if kind == "extreme":
        p = pos(names[0])
        return p + front(names[0], (0, -5.4, HEAD_Z + 0.2)), p + Vector((0, 0, HEAD_Z + 0.05)), 50
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
        # camera in front of the line, a little behind the near character's shoulder,
        # so the near character frames the edge and we see the far character's face
        loc = over - d * 3.2 + Vector((0, -4.8, HEAD_Z + 0.3))
        return loc, at + Vector((0, 0, HEAD_Z - 0.7)), 45
    if kind == "tag":  # head + the price tag floating above it
        p = pos(names[0])
        return p + front(names[0], (0, -8.5, HEAD_Z + 1.2)), p + Vector((0, 0, HEAD_Z + 0.75)), 40
    if kind == "low":
        p = pos(names[0])
        return p + front(names[0], (0, -7, 0.8)), p + Vector((0, 0, HEAD_Z - 0.5)), 26
    if kind == "high":
        p = pos(names[0])
        return p + Vector((0, -6, 12)), p + Vector((0, 0, 2.5)), 32
    raise ValueError(f"unknown camera '{spec}'")


def _ease(t):
    return t * t * (3 - 2 * t)


def key_camera(cam, f0, f1, spec, rigs, origin, fmt, move, roll_deg=0.0, handheld=1.0):
    """Keys the camera for frames f0..f1-1.

    Moves: push (default slow push-in) | pull | pan | zoom (fast meme zoom) | shake |
           punch (snaps in fast on the first frames, then drifts) | whip (whip-pans into the shot) | none
    Every move also gets a gentle handheld drift (set "handheld": 0 on the episode to turn off)."""
    loc, at, lens = camera_pose(spec, rigs, origin, fmt)
    end_loc = Vector(loc)
    if move == "push":
        end_loc = loc + (at - loc) * 0.14
    elif move == "pull":
        end_loc = loc - (at - loc) * 0.14
    elif move == "pan":
        end_loc = loc + Vector((1.8, 0, 0))
    elif move == "zoom":
        end_loc = loc + (at - loc) * 0.55
    elif move in ("punch", "whip"):
        end_loc = loc + (at - loc) * 0.06
    kind = spec.partition(":")[0]
    fstop = {"extreme": 1.4, "closeup": 1.8, "tag": 2.0, "low": 2.2, "ots": 2.2, "medium": 2.8, "two": 4.0,
             "high": 4.0, "wide": 7.0}.get(kind, 2.8)
    n = max(1, f1 - 1 - f0)
    seed = (f0 * 7919) % 1000
    amp = 0.05 * handheld * (1.6 if kind in ("wide", "two", "medium") else 1.0)

    def place(frame):
        t = (frame - f0) / n
        if move == "punch":
            k = min(1.0, (frame - f0) / 5.0)
            start = loc - (at - loc) * 0.35
            l = start.lerp(loc, _ease(k)).lerp(end_loc, _ease(t))
        elif move == "whip":
            k = min(1.0, (frame - f0) / 6.0)
            l = loc.lerp(end_loc, _ease(t))
        else:
            l = loc.lerp(end_loc, _ease(t) if move != "zoom" else 1 - (1 - t) ** 3)
        jitter = Vector((math.sin(frame * 0.21 + seed) + 0.5 * math.sin(frame * 0.53 + seed * 2),
                         0.4 * math.sin(frame * 0.17 + seed * 3),
                         math.sin(frame * 0.27 + seed * 5) + 0.4 * math.sin(frame * 0.61 + seed)))
        l = l + jitter * amp
        tgt = Vector(at)
        r = roll_deg + 0.6 * handheld * math.sin(frame * 0.13 + seed)
        if move == "whip":
            side = 1 if (f0 // 7) % 2 else -1
            off = (1 - _ease(k)) * 9.0 * side
            tgt = tgt + Vector((off, 0, 0))
            r += (1 - _ease(k)) * 12 * side
        return l, tgt, r

    frames = sorted(set([f0, f1 - 1] + list(range(f0, f1 - 1, 4 if move in ("punch", "whip") else 6))))
    if move in ("punch", "whip"):
        frames = sorted(set(frames + list(range(f0, min(f1 - 1, f0 + 7)))))
    from mathutils import Quaternion
    for frame in frames:
        l, tgt, r = place(frame)
        cam.location = l
        q = (tgt - l).to_track_quat("-Z", "Y")
        cam.rotation_euler = (q @ Quaternion((0, 0, 1), math.radians(r))).to_euler()
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
            l, _, _ = place(f)
            cam.location = l + Vector(((-0.15, 0.15)[i % 2], 0, (0.1, -0.1)[(i // 2) % 2]))
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


def auto_second_angle(first, speaker, rigs, i):
    """Pick a contrasting second camera so long lines cut like an edited film."""
    others = [n for n in rigs if n != speaker]
    near = min(others, key=lambda n: (Vector(rigs[n].base) - Vector(rigs[speaker].base)).length) if others else None
    kind = first.partition(":")[0]
    options = []
    if near:
        options.append(f"ots:{near},{speaker}")
    options += [f"low:{speaker}@-8", f"closeup:{speaker}@10" if kind != "closeup" else f"medium:{speaker}"]
    return options[i % len(options)]


def harden_cuts(cut_frames, cam_cuts=()):
    """Make the jump between the last frame of a shot and the first of the next a hard
    cut, and stop the big jump from bending the motion inside the shot."""
    ids = list(bpy.data.objects) + list(bpy.data.cameras) + list(bpy.data.materials)
    ids += [m.node_tree for m in bpy.data.materials if m.node_tree]
    for nt in [m.node_tree for m in bpy.data.materials if m.node_tree]:
        for fc in fcurves_of(nt):  # face swaps must snap, never slide
            for kp in fc.keyframe_points:
                kp.interpolation = "CONSTANT"
    cam_ids = {bpy.context.scene.camera, bpy.context.scene.camera.data}
    for idb in ids:
        cuts = (cut_frames | set(cam_cuts)) if idb in cam_ids else cut_frames
        for fc in fcurves_of(idb):
            if idb in [m.node_tree for m in bpy.data.materials]:
                continue
            for kp in fc.keyframe_points:
                f = round(kp.co[0])
                if f in cuts:
                    kp.interpolation = "CONSTANT"
                    kp.handle_left_type = kp.handle_right_type = "VECTOR"
                elif f - 1 in cuts:
                    kp.handle_left_type = kp.handle_right_type = "VECTOR"
            fc.update()


# ---------------------------------------------------------------- price tags
def build_tags(ep, rigs):
    """Floating tags above heads: "tags": {"sage": "$0", ...} on the episode.
    Each tag is a white card with a gold string loop and bold text, parented to the character
    so it follows them. Shots control them with:
      "tags_show": true        tags pop in at the start of this shot (hidden before the first one)
      "tag_flash": "goldie"    that tag pulses big (e.g. with a cash sound)
      "tag_rip": "goldie"      that character rips it off (pairs with the rip_tag anim)
    """
    spec = ep.get("tags") or {}
    out = {}
    if not spec:
        return out
    card = rigmod.make_material("tag_card", "#fffaf0", roughness=0.4, texture=False)
    edge = rigmod.make_material("tag_edge", "#e2b23a", roughness=0.35, texture=False)
    ink = bpy.data.materials.new("tag_ink")
    ink.use_nodes = True
    bsdf = ink.node_tree.nodes.get("Principled BSDF")
    bsdf.inputs["Base Color"].default_value = rigmod.hex_rgba("#1b7a34")
    zero = bpy.data.materials.new("tag_ink_zero")
    zero.use_nodes = True
    zero.node_tree.nodes.get("Principled BSDF").inputs["Base Color"].default_value = rigmod.hex_rgba("#c0392b")
    font = None
    for fp in ("/usr/share/fonts/opentype/inter/InterDisplay-Black.otf",
               "C:/Windows/Fonts/ariblk.ttf", "/System/Library/Fonts/Supplemental/Arial Black.ttf"):
        if os.path.exists(fp):
            font = bpy.data.fonts.load(fp)
            break
    for name, text in spec.items():
        if name not in rigs:
            continue
        r = rigs[name]
        holder = bpy.data.objects.new(f"{name}_tag", None)
        bpy.context.scene.collection.objects.link(holder)
        holder.parent = r.root
        holder.location = (0, -0.1, 6.55)
        w = max(1.6, 0.42 * len(text) + 0.6)
        rigmod.add_obj(f"{name}_tag_card", rigmod.box_mesh("tc", (w, 0.1, 0.85)), holder, (0, 0, 0), card, bevel=0.12)
        rigmod.add_obj(f"{name}_tag_rim", rigmod.box_mesh("tr", (w + 0.14, 0.06, 0.99)), holder, (0, 0.04, 0), edge,
                       bevel=0.14)
        rigmod.add_obj(f"{name}_tag_hole", rigmod.box_mesh("th", (0.16, 0.12, 0.16)), holder,
                       (-w / 2 + 0.25, -0.02, 0.22), edge, bevel=0.06)
        rigmod.add_obj(f"{name}_tag_str", rigmod.box_mesh("ts", (0.05, 0.05, 0.9)), holder,
                       (-w / 2 + 0.25, 0, 0.62), edge, bevel=0)
        cu = bpy.data.curves.new(f"{name}_tag_txt", "FONT")
        cu.body = text
        cu.align_x, cu.align_y = "CENTER", "CENTER"
        cu.size = 0.62
        cu.extrude = 0.02
        if font:
            cu.font = font
        to = bpy.data.objects.new(f"{name}_tag_txt", cu)
        bpy.context.scene.collection.objects.link(to)
        to.parent = holder
        to.location = (0.08, -0.07, -0.02)
        to.rotation_euler = (math.radians(90), 0, 0)
        to.data.materials.append(zero if text.strip() in ("$0", "$0.00") else ink)
        holder.scale = (0, 0, 0)
        holder.keyframe_insert("scale", frame=1)
        out[name] = dict(holder=holder, shown=False, ripped=False, phase=len(name))
    return out


def key_tags(tags, shot, f0, f1, scene_rigs):
    if not tags:
        return
    if shot.get("tags_show"):
        for i, t in enumerate(tags.values()):
            if not t["shown"]:
                h, d = t["holder"], 4 + i * 3
                for fr, sc in ((f0, 0), (f0 + d, 0), (f0 + d + 4, 1.25), (f0 + d + 8, 1.0)):
                    h.scale = (sc, sc, sc)
                    h.keyframe_insert("scale", frame=min(fr, f1 - 1))
                t["shown"] = True
    for name, t in tags.items():
        h = t["holder"]
        if not t["shown"] or t["ripped"] or name not in scene_rigs:
            continue
        # gentle float + sway
        for fr in ([] if shot.get("tag_rip") == name else range(f0, f1, 10)):
            h.location = (0, -0.1, 6.55 + 0.08 * math.sin((fr + t["phase"] * 7) * 0.12))
            h.rotation_euler = (0, math.radians(3 * math.sin((fr + t["phase"] * 5) * 0.09)), 0)
            h.keyframe_insert("location", frame=fr)
            h.keyframe_insert("rotation_euler", frame=fr)
        if shot.get("tag_flash") == name:
            for k, sc in enumerate((1.0, 1.5, 1.15, 1.45, 1.2, 1.3, 1.0)):
                h.scale = (sc, sc, sc)
                h.keyframe_insert("scale", frame=min(f0 + k * 4, f1 - 1))
        if shot.get("tag_rip") == name:
            h.scale = (1, 1, 1)
            h.keyframe_insert("scale", frame=f0)
            h.keyframe_insert("location", frame=f0 + 8)
            h.location = (0.6, -0.6, 3.6)
            h.scale = (0.35, 0.35, 0.35)
            h.keyframe_insert("location", frame=min(f0 + 16, f1 - 1))
            h.keyframe_insert("scale", frame=min(f0 + 16, f1 - 1))
            h.scale = (0, 0, 0)
            h.keyframe_insert("scale", frame=min(f0 + 30, f1 - 1))
            t["ripped"] = True


# ------------------------------------------------------------ background kids
EXTRA_LOOKS = [
    dict(skin="#f2c9a0", shirt="#e63946", pants="#1d3557", hair={"style": "spiky", "color": "#2b2b2b"}, sleeves=True),
    dict(skin="#8d5524", shirt="#ffb703", pants="#3a3a3a", hair={"style": "block", "color": "#1a1a1a"}),
    dict(skin="#e8bd96", shirt="#8338ec", pants="#264653", hair={"style": "long", "color": "#c97b2a"}, sleeves=True),
    dict(skin="#c68a5e", shirt="#06d6a0", pants="#22223b", hair={"style": "cap", "color": "#ef476f"}),
    dict(skin="#f5d0b0", shirt="#3a86ff", pants="#e9c46a", hair={"style": "bacon", "color": "#5a3a1e"}),
    dict(skin="#a0673f", shirt="#ff006e", pants="#2b2d42", hair={"style": "long", "color": "#111111"}),
]


def build_extras(ep, faces_dir):
    """"extras": 4 on the episode adds background students who walk up and down behind the cast."""
    n = int(ep.get("extras", 0))
    out = []
    for i in range(n):
        spec = dict(EXTRA_LOOKS[i % len(EXTRA_LOOKS)])
        spec["scale"] = 0.95 + 0.05 * (i % 3)
        r = rigmod.build_character(f"extra{i}", spec, faces_dir)
        out.append(r)
    return out


def animate_extras(extras, ep, last_frame, fps):
    lanes = ep.get("extras_lanes", [4.6, 6.0, 5.2, 3.8, 6.6, 4.2])
    span = float(ep.get("extras_span", 34))
    for i, r in enumerate(extras):
        y = lanes[i % len(lanes)]
        speed = 3.6 + 0.5 * (i % 3)
        direction = 1 if i % 2 == 0 else -1
        x = -span + (2 * span) * ((i * 0.37) % 1.0)
        r.base_yaw = 90.0 if direction > 0 else -90.0
        step = 6
        f = 1
        k = 0
        while f <= last_frame:
            s = 1 if k % 2 else -1
            r.base = (x, y, 0.0)
            anims.pose(r, f, offset=(0, 0, 0.06 * (k % 2)), leg_l=(30 * s, 0, 0), leg_r=(-30 * s, 0, 0),
                       arm_l=(-28 * s, 0, 0), arm_r=(28 * s, 0, 0), head=(0, 0, 10 * math.sin(k * 0.3 + i)))
            x += direction * speed * step / fps
            if abs(x) > span:  # turn around off-screen and walk back
                direction = -direction
                r.base_yaw = 90.0 if direction > 0 else -90.0
            f += step
            k += 1


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

    tags = build_tags(ep, rigs_all)
    extras = build_extras(ep, faces_dir)
    frame = 1
    shot_i = 0
    cut_frames = set()
    cam_cuts = set()  # extra cuts inside a shot (camera only)
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
            focus = shot.get("focus") or (speaker if speaker in scene_rigs and not shot.get("vo") else None)
            anims.CTX["focus"] = tuple(scene_rigs[focus].base[:2]) if focus in scene_rigs else None
            walks = shot.get("walk", {})  # {"name": [x, y]} or {"name": {"to": [x, y], "at": 0.3, "run": true}}
            for name, r in rigs_all.items():
                if name not in scene_rigs:
                    anims.hidden(r, f0, f1, fps)
                    continue
                default = "talk" if (name == speaker and not shot.get("vo")) else "idle"
                anim_name = shot_anims.get(name, default)
                if anim_name not in anims.ANIMS:
                    raise ValueError(f"unknown anim '{anim_name}'. Available: {sorted(anims.ANIMS)}")
                a0 = f0
                if name in walks:
                    w = walks[name] if isinstance(walks[name], dict) else {"to": walks[name]}
                    dest = (origin[0] + w["to"][0], origin[1] + w["to"][1], r.base[2])
                    ws = f0 + round(float(w.get("at", 0)) * fps)
                    if ws > f0:  # stand (or do the shot's anim) until the walk starts
                        anims.ANIMS[anim_name if anim_name != "talk" else "idle"](r, f0, ws, fps)
                    a0 = anims.walk_to(r, ws, r.base[:2], dest[:2], fps, run=bool(w.get("run")), max_frames=f1 - ws)
                    r.base = dest
                    if a0 >= f1 - 2:
                        a0 = f1 - 2
                anims.ANIMS[anim_name](r, a0, f1, fps)
                r.hidden_now = anim_name == "hidden"

            cams = shot.get("cameras") or [shot.get("camera", f"medium:{speaker}" if speaker and
                                                    speaker in scene_rigs else "wide")]
            if (len(cams) == 1 and ep.get("auto_cuts") and n_frames > fps * 2.6 and speaker in scene_rigs
                    and not shot.get("vo")):
                cams = cams + [auto_second_angle(cams[0], speaker, scene_rigs, shot_i)]
            seg = n_frames / len(cams)
            for ci, cspec in enumerate(cams):
                a = f0 + round(ci * seg)
                b = f0 + round((ci + 1) * seg)
                spec, _, roll = cspec.partition("@")
                moves = shot.get("moves") or [shot.get("move", "push")] + ["push"] * (len(cams) - 1)
                key_camera(cam, a, b, spec, scene_rigs, origin, fmt, moves[min(ci, len(moves) - 1)],
                           float(roll or 0), float(ep.get("handheld", 1.0)))
                if b < f1:
                    cam_cuts.add(b - 1)

            prefs.keyframe_new_interpolation_type = "CONSTANT"
            for name, r in scene_rigs.items():
                expr = shot.get("face", "neutral") if name == speaker else faces.get(name, "neutral")
                if name == speaker and "face" not in shot:
                    expr = faces.get(name, "neutral")
                key_faces_for_shot(r, f0, f1, expr,
                                   name == speaker and bool(shot.get("line")) and not shot.get("vo"),
                                   t.get("mouth"))
            prefs.keyframe_new_interpolation_type = "BEZIER"
            key_tags(tags, shot, f0, f1, scene_rigs)
            cut_frames.add(f1 - 1)
            frame = f1
            shot_i += 1

    animate_extras(extras, ep, frame - 1, fps)
    scn.frame_start = 1
    scn.frame_end = frame - 1
    if args.frames:
        a, b = args.frames.split(":")
        scn.frame_start, scn.frame_end = int(a), int(b)
    scn.frame_step = args.step
    if ep.get("fog", True):
        apply_fog(MOODS[ep.get("mood", "day")])
    harden_cuts(cut_frames, cam_cuts)
    os.makedirs(args.out, exist_ok=True)
    if args.save_blend:
        bpy.ops.wm.save_as_mainfile(filepath=os.path.abspath(args.save_blend))
    scn.render.filepath = os.path.join(os.path.abspath(args.out), "frame_")
    print(f"[render] {scn.frame_end - scn.frame_start + 1} frames, engine={scn.render.engine}", flush=True)
    bpy.ops.render.render(animation=True)
    print("[render] done", flush=True)


if __name__ == "__main__":
    main()
