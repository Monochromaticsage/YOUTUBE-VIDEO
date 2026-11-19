"""Blocky R6-style characters built from code, with swappable face expressions.

Every character is an Empty (the "root") with six parts parented under it.
Each limb's origin sits on its joint (shoulder / hip / neck) so rotating it
swings the limb naturally. Faces live on one plane per character that shows
one cell of a face "atlas" image; changing expression = moving the UV window.

If you drop a PNG at assets/faces/<expression>.png (transparent background,
square), it is used instead of the generated face for every character.
"""
import math
import os

import bpy
import numpy as np

# Expression names usable in episode JSON ("face": "shocked").
FACES = ["neutral", "happy", "smug", "angry", "sad", "shocked",
         "scared", "sus", "cry", "dead", "evil", "love"]
ATLAS_COLS, ATLAS_ROWS, CELL = 6, 4, 256  # 24 cells = 12 faces x (closed, open)


def hex_rgba(h, a=1.0):
    h = h.lstrip("#")
    r, g, b = (int(h[i:i + 2], 16) / 255.0 for i in (0, 2, 4))
    # sRGB -> linear so the colour in JSON matches what you see on screen
    lin = [c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4 for c in (r, g, b)]
    return (*lin, a)


def make_material(name, color, roughness=0.55):
    mat = bpy.data.materials.new(name)
    mat.use_nodes = True
    bsdf = mat.node_tree.nodes.get("Principled BSDF")
    rgba = hex_rgba(color) if isinstance(color, str) else color
    bsdf.inputs["Base Color"].default_value = rgba
    bsdf.inputs["Roughness"].default_value = roughness
    mat.diffuse_color = rgba  # used by the Workbench engine
    return mat


def metal_material(name, color):
    mat = make_material(name, color, roughness=0.25)
    mat.node_tree.nodes.get("Principled BSDF").inputs["Metallic"].default_value = 1.0
    return mat


def box_mesh(name, size, pivot=(0, 0, 0)):
    """Box of `size` whose origin is offset by `pivot` (in box-local coords).
    pivot=(0,0,h/2) puts the origin at the top face (good for limbs)."""
    sx, sy, sz = (s / 2 for s in size)
    px, py, pz = pivot
    v = [(x - px, y - py, z - pz) for x in (-sx, sx) for y in (-sy, sy) for z in (-sz, sz)]
    f = [(0, 1, 3, 2), (4, 6, 7, 5), (0, 4, 5, 1), (2, 3, 7, 6), (0, 2, 6, 4), (1, 5, 7, 3)]
    me = bpy.data.meshes.new(name)
    me.from_pydata(v, [], f)
    me.update()
    return me


def add_obj(name, mesh, parent=None, loc=(0, 0, 0), mat=None, bevel=0.08, segments=2):
    ob = bpy.data.objects.new(name, mesh)
    bpy.context.scene.collection.objects.link(ob)
    ob.location = loc
    if parent:
        ob.parent = parent
    if mat:
        mesh.materials.append(mat)
    if bevel:
        m = ob.modifiers.new("bevel", "BEVEL")
        m.width = bevel
        m.segments = segments
        m.limit_method = "NONE"
    for p in mesh.polygons:
        p.use_smooth = bevel > 0.1
    return ob


# --------------------------------------------------------------------- faces
def _yy_xx(n=CELL):
    return np.mgrid[0:n, 0:n].astype(np.float32)


def _ellipse(cx, cy, rx, ry):
    yy, xx = _yy_xx()
    return ((xx - cx) / rx) ** 2 + ((yy - cy) / ry) ** 2 <= 1.0


def _segment(x0, y0, x1, y1, w):
    yy, xx = _yy_xx()
    dx, dy = x1 - x0, y1 - y0
    t = np.clip(((xx - x0) * dx + (yy - y0) * dy) / (dx * dx + dy * dy + 1e-6), 0, 1)
    return (xx - (x0 + t * dx)) ** 2 + (yy - (y0 + t * dy)) ** 2 <= (w / 2) ** 2


def _arc(cx, cy, r, w, up=True, span=0.85):
    """Smile (up=False -> frown). y grows downward in this drawing space."""
    yy, xx = _yy_xx()
    d = np.sqrt((xx - cx) ** 2 + (yy - cy) ** 2)
    ring = np.abs(d - r) <= w / 2
    half = (yy >= cy + r * (1 - span)) if up else (yy <= cy - r * (1 - span))
    return ring & half


def draw_face(expr, mouth_open):
    """Returns a CELL x CELL boolean 'ink' mask plus optional extra colour layers.
    Drawing coords: x right, y DOWN, canvas 256."""
    ink = np.zeros((CELL, CELL), bool)
    white = np.zeros_like(ink)
    pink = np.zeros_like(ink)   # mouth interior / blush
    blue = np.zeros_like(ink)   # tears
    red = np.zeros_like(ink)

    L, R, EY = 92, 164, 108  # eye centres
    def eyes(rx=13, ry=22):
        nonlocal ink
        ink |= _ellipse(L, EY, rx, ry) | _ellipse(R, EY, rx, ry)

    if expr == "neutral":
        eyes()
        mouth = _segment(104, 178, 152, 178, 9)
    elif expr == "happy":
        eyes()
        mouth = _arc(128, 150, 36, 10, up=True)
    elif expr == "smug":
        ink |= _ellipse(L, EY + 6, 14, 12) | _ellipse(R, EY + 6, 14, 12)
        ink |= _segment(70, 92, 112, 98, 9) | _segment(144, 98, 186, 92, 9)
        mouth = _segment(110, 182, 160, 170, 9)
    elif expr == "angry":
        eyes(12, 16)
        ink |= _segment(66, 76, 114, 98, 11) | _segment(142, 98, 190, 76, 11)
        mouth = _arc(128, 205, 32, 10, up=False)
    elif expr == "sad":
        eyes(12, 18)
        ink |= _segment(70, 88, 110, 78, 8) | _segment(146, 78, 186, 88, 8)
        mouth = _arc(128, 210, 30, 9, up=False)
    elif expr == "shocked":
        white |= _ellipse(L, EY, 22, 26) | _ellipse(R, EY, 22, 26)
        ink |= _ellipse(L, EY, 8, 9) | _ellipse(R, EY, 8, 9)
        ink |= _segment(68, 66, 112, 62, 8) | _segment(144, 62, 188, 66, 8)
        mouth_open = True
        mouth = _ellipse(128, 186, 20, 26)
    elif expr == "scared":
        white |= _ellipse(L, EY, 20, 24) | _ellipse(R, EY, 20, 24)
        ink |= _ellipse(L, EY + 4, 6, 7) | _ellipse(R, EY + 4, 6, 7)
        ink |= _segment(72, 74, 110, 66, 8) | _segment(146, 66, 184, 74, 8)
        # wobbly mouth
        mouth = np.zeros_like(ink)
        for i in range(6):
            x = 98 + i * 12
            mouth |= _segment(x, 182 + (6 if i % 2 else -6), x + 12, 182 + (-6 if i % 2 else 6), 7)
    elif expr == "sus":
        ink |= _segment(70, EY, 114, EY, 12) | _segment(142, EY, 186, EY, 12)
        ink |= _segment(70, 90, 114, 94, 8) | _segment(142, 84, 186, 80, 8)
        mouth = _segment(110, 180, 150, 180, 9)
    elif expr == "cry":
        eyes(12, 8)
        blue |= _segment(L, EY + 8, L - 4, 200, 14) | _segment(R, EY + 8, R + 4, 200, 14)
        mouth = _arc(128, 212, 30, 10, up=False)
        mouth_open = True
    elif expr == "dead":
        for cx in (L, R):
            ink |= _segment(cx - 16, EY - 16, cx + 16, EY + 16, 9) | _segment(cx - 16, EY + 16, cx + 16, EY - 16, 9)
        mouth = _segment(104, 180, 152, 180, 9)
    elif expr == "evil":
        red |= _ellipse(L, EY, 14, 14) | _ellipse(R, EY, 14, 14)
        ink |= _segment(64, 82, 116, 104, 11) | _segment(140, 104, 192, 82, 11)
        mouth = _arc(128, 140, 46, 10, up=True)
    elif expr == "love":
        for cx in (L, R):  # heart eyes
            red |= _ellipse(cx - 8, EY - 4, 11, 11) | _ellipse(cx + 8, EY - 4, 11, 11)
            for dy in range(0, 22):
                red |= _segment(cx - 18 + dy * 0.8, EY + dy, cx + 18 - dy * 0.8, EY + dy, 2)
        mouth = _arc(128, 150, 32, 10, up=True)
    else:
        raise ValueError(f"unknown face '{expr}'. Use one of {FACES}")

    if mouth_open:
        # replace the mouth line with an open mouth shape at the same spot
        ys, xs = np.nonzero(mouth)
        cx, cy = xs.mean(), ys.mean()
        w = max(16, (xs.max() - xs.min()) / 2 + 4)
        inner = _ellipse(cx, cy + 4, w * 0.8, 15)
        ink |= _ellipse(cx, cy + 4, w * 0.8 + 6, 21) & ~inner
        pink |= inner
    else:
        ink |= mouth
    return ink, white, pink, blue, red


def stylize_face(expr, mouth_open, layers, style):
    """Personal face details layered on top of an expression.
    style keys: lashes, teeth, brows ("arched"), blush, sparkle, lips ("#hex")."""
    ink, white, pink, blue, red = layers
    extra = {"blush": np.zeros_like(ink), "lips": np.zeros_like(ink)}
    L, R, EY = 92, 164, 108
    yy, xx = _yy_xx()
    if style.get("teeth") and expr in ("happy", "love"):
        # replace the line smile with a big open smile showing teeth
        ink[yy > 140] = False
        pink[yy > 140] = False
        ry = 44 if mouth_open else 34
        mouth = _ellipse(128, 156, 44, ry) & (yy >= 156)
        lips = _ellipse(128, 156, 51, ry + 7) & (yy >= 150) & ~mouth
        teeth = mouth & (yy <= 156 + ry * 0.45)
        pink |= mouth & ~teeth
        white |= teeth
        extra["lips"] |= lips
    if style.get("brows") == "arched" and expr in ("neutral", "happy", "love", "cry"):
        for cx in (L, R):
            ink |= _arc(cx, EY + 10, 36, 7, up=False, span=0.55) & (yy < EY - 18)
    if style.get("lashes") and expr not in ("dead", "sus", "smug"):
        for cx, d in ((L, -1), (R, 1)):
            for (ax, ay, bx, by) in ((9, -17, 22, -25), (3, -21, 11, -31)):
                ink |= _segment(cx + d * ax, EY + ay, cx + d * bx, EY + by, 4)
    if style.get("sparkle") and expr not in ("dead", "sus", "evil", "love", "cry"):
        for cx in (L, R):
            white |= _ellipse(cx + 4, EY - 9, 4.5, 4.5) & ink
    if style.get("blush"):
        for cx in (L - 8, R + 8):
            extra["blush"] |= _ellipse(cx, EY + 40, 18, 9) & ~ink
    return (ink, white, pink, blue, red), extra


def build_face_atlas(name, skin_hex, faces_dir, glasses=False, style=None):
    skin = np.array(hex_rgba(skin_hex), np.float32)
    if style and style.get("detailed") is not None:
        from face_detailed import N as DN, draw_face_detailed
        px = np.zeros((ATLAS_ROWS * DN, ATLAS_COLS * DN, 4), np.float32)
        for i, expr in enumerate(FACES):
            for open_ in (0, 1):
                idx = i * 2 + open_
                col, row = idx % ATLAS_COLS, idx // ATLAS_COLS
                cell = draw_face_detailed(expr, bool(open_), skin, style["detailed"])
                px[row * DN:(row + 1) * DN, col * DN:(col + 1) * DN] = cell[::-1]
        img = bpy.data.images.new(f"{name}_faces", px.shape[1], px.shape[0], alpha=True, float_buffer=True)
        img.colorspace_settings.name = "Non-Color"
        img.pixels.foreach_set(px.ravel())
        img.pack()
        return img
    W, H = ATLAS_COLS * CELL, ATLAS_ROWS * CELL
    px = np.zeros((H, W, 4), np.float32)
    px[:] = skin
    colors = {"ink": (0.02, 0.02, 0.02, 1), "white": (1, 1, 1, 1), "pink": (0.55, 0.08, 0.12, 1),
              "blue": (0.25, 0.55, 1.0, 1), "red": (0.85, 0.05, 0.08, 1)}
    for i, expr in enumerate(FACES):
        for open_ in (0, 1):
            idx = i * 2 + open_
            col, row = idx % ATLAS_COLS, idx // ATLAS_COLS
            cell = np.empty((CELL, CELL, 4), np.float32)
            cell[:] = skin
            custom = os.path.join(faces_dir, f"{expr}{'_open' if open_ else ''}.png")
            if not os.path.exists(custom):
                custom = os.path.join(faces_dir, f"{expr}.png")
            if os.path.exists(custom):
                img = bpy.data.images.load(custom)
                img.scale(CELL, CELL)
                c = np.array(img.pixels[:], np.float32).reshape(CELL, CELL, 4)[::-1]
                rgb = c[..., :3]
                c[..., :3] = np.where(rgb <= 0.04045, rgb / 12.92, ((rgb + 0.055) / 1.055) ** 2.4)
                a = c[..., 3:4]
                cell = cell * (1 - a) + np.concatenate([c[..., :3], np.ones_like(a)], -1) * a
                bpy.data.images.remove(img)
            else:
                layers = draw_face(expr, bool(open_))
                extra = {}
                if style:
                    layers, extra = stylize_face(expr, bool(open_), layers, style)
                ink, white, pink, blue, red = layers
                if "blush" in extra:
                    cell[extra["blush"]] = cell[extra["blush"]] * 0.55 + np.array(hex_rgba("#ff7f9a")) * 0.45
                for mask, key in ((white, "white"), (pink, "pink"), (blue, "blue"), (red, "red"), (ink, "ink")):
                    cell[mask] = colors[key]
                if "lips" in extra:
                    cell[extra["lips"]] = hex_rgba(style.get("lips", "#c75b6e"))
            if glasses:
                rim = np.zeros((CELL, CELL), bool)
                for cx in (92, 164):
                    rim |= _ellipse(cx, 108, 32, 28) & ~_ellipse(cx, 108, 26, 22)
                rim |= _segment(118, 104, 138, 104, 6)
                cell[rim[::1]] = colors["ink"]
            # Blender images are stored bottom row first -> flip, and atlas row 0 is at the bottom
            px[row * CELL:(row + 1) * CELL, col * CELL:(col + 1) * CELL] = cell[::-1]
    img = bpy.data.images.new(f"{name}_faces", W, H, alpha=True, float_buffer=True)
    img.colorspace_settings.name = "Non-Color"  # pixels below are already linear
    img.pixels.foreach_set(px.ravel())
    img.pack()
    return img


def face_offset(expr, mouth_open):
    idx = FACES.index(expr) * 2 + (1 if mouth_open else 0)
    return (idx % ATLAS_COLS) / ATLAS_COLS, (idx // ATLAS_COLS) / ATLAS_ROWS


# ----------------------------------------------------------------- character
class Rig:
    def __init__(self, name, root, parts, face_mapping):
        self.name, self.root, self.parts, self.face_mapping = name, root, parts, face_mapping
        self.base = (0.0, 0.0, 0.0)  # current mark position
        self.base_yaw = 0.0


def build_character(name, spec, faces_dir):
    """spec: {"skin": "#hex", "shirt": "#hex", "pants": "#hex", "hair": {...}}"""
    skin = make_material(f"{name}_skin", spec.get("skin", "#f5cd30"))
    shirt = make_material(f"{name}_shirt", spec.get("shirt", "#0d69ac"))
    pants = make_material(f"{name}_pants", spec.get("pants", "#a2c48b"))
    arm_mat = shirt if spec.get("sleeves", False) else skin

    root = bpy.data.objects.new(f"{name}_root", None)
    bpy.context.scene.collection.objects.link(root)
    sc = float(spec.get("scale", 1.0))  # e.g. 0.75 for a little kid
    root.scale = (sc, sc, sc)

    # Torso 2x1x2 studs, sitting on legs of height 2
    torso = add_obj(f"{name}_torso", box_mesh("t", (2, 1, 2), (0, 0, -1)), root, (0, 0, 2), shirt)
    head = add_obj(f"{name}_head", box_mesh("h", (1.25, 1.2, 1.2), (0, 0, -0.6)), torso, (0, 0, 2), skin,
                   bevel=0.22, segments=4)
    # Shoulder joint like Roblox R6: at the torso edge, 0.5 below the top of the arm
    arm_l = add_obj(f"{name}_arm_l", box_mesh("al", (1, 1, 2), (-0.5, 0, 0.5)), torso, (1.0, 0, 1.5), arm_mat)
    arm_r = add_obj(f"{name}_arm_r", box_mesh("ar", (1, 1, 2), (0.5, 0, 0.5)), torso, (-1.0, 0, 1.5), arm_mat)
    leg_l = add_obj(f"{name}_leg_l", box_mesh("ll", (1, 1, 2), (0, 0, 1)), root, (0.5, 0, 2), pants)
    leg_r = add_obj(f"{name}_leg_r", box_mesh("lr", (1, 1, 2), (0, 0, 1)), root, (-0.5, 0, 2), pants)

    # Face plane on the front of the head (faces -Y, the default camera side)
    me = bpy.data.meshes.new(f"{name}_face")
    s = 0.46
    me.from_pydata([(-s, 0, -s), (s, 0, -s), (s, 0, s), (-s, 0, s)], [], [(0, 1, 2, 3)])
    uv = me.uv_layers.new()
    for li, co in zip(range(4), [(0, 0), (1, 0), (1, 1), (0, 1)]):
        uv.data[li].uv = co
    face = bpy.data.objects.new(f"{name}_face", me)
    bpy.context.scene.collection.objects.link(face)
    face.parent = head
    face.location = (0, -0.605, 0.58)

    atlas = build_face_atlas(name, spec.get("skin", "#f5cd30"), faces_dir, bool(spec.get("glasses")),
                             spec.get("face_style"))
    fm = bpy.data.materials.new(f"{name}_face_mat")
    fm.use_nodes = True
    nt = fm.node_tree
    bsdf = nt.nodes.get("Principled BSDF")
    bsdf.inputs["Roughness"].default_value = 0.6
    tex = nt.nodes.new("ShaderNodeTexImage")
    tex.image = atlas
    tex.interpolation = "Closest" if spec.get("pixel_faces") else "Linear"
    mapping = nt.nodes.new("ShaderNodeMapping")
    coord = nt.nodes.new("ShaderNodeTexCoord")
    mapping.inputs["Scale"].default_value = (1 / ATLAS_COLS, 1 / ATLAS_ROWS, 1)
    nt.links.new(coord.outputs["UV"], mapping.inputs["Vector"])
    nt.links.new(mapping.outputs["Vector"], tex.inputs["Vector"])
    nt.links.new(tex.outputs["Color"], bsdf.inputs["Base Color"])
    me.materials.append(fm)

    hair = spec.get("hair")
    if hair:
        hm = make_material(f"{name}_hair", hair.get("color", "#5a3a1e"))
        style = hair.get("style", "block")
        if style == "cap":
            add_obj(f"{name}_cap", box_mesh("c", (1.35, 1.3, 0.45)), head, (0, 0, 1.25), hm, bevel=0.15, segments=3)
            add_obj(f"{name}_brim", box_mesh("b", (1.2, 0.7, 0.1)), head, (0, -0.85, 1.07), hm)
        elif style == "bacon":
            for i, (x, z) in enumerate([(-0.45, 1.3), (0, 1.38), (0.45, 1.3), (-0.6, 1.0), (0.6, 1.0)]):
                add_obj(f"{name}_hair{i}", box_mesh("hb", (0.55, 1.25, 0.5)), head, (x, 0.1, z), hm,
                        bevel=0.2, segments=3)
        elif style == "long":
            add_obj(f"{name}_hairtop", box_mesh("ht", (1.4, 1.35, 0.4)), head, (0, 0.05, 1.28), hm, bevel=0.15)
            add_obj(f"{name}_hairback", box_mesh("hk", (1.4, 0.35, 1.7)), head, (0, 0.6, 0.55), hm, bevel=0.12)
        elif style == "sideswept":
            # long wavy hair, deep side part, swept over the character's left shoulder (+X)
            add_obj(f"{name}_hairtop", box_mesh("ht", (1.42, 1.36, 0.34)), head, (0, 0.04, 1.27), hm,
                    bevel=0.15, segments=3)
            add_obj(f"{name}_swoop", box_mesh("hs", (0.95, 0.32, 0.42)), head, (0.22, -0.6, 1.08), hm,
                    bevel=0.16, segments=3).rotation_euler = (0, math.radians(-12), 0)
            add_obj(f"{name}_hairback", box_mesh("hk", (1.5, 0.42, 2.4)), head, (0, 0.62, 0.05), hm,
                    bevel=0.18, segments=3)
            for i in range(5):  # big wavy curtain over the shoulder down to the chest
                z = 0.95 - i * 0.55
                x = 0.88 + (0.12 if i % 2 else 0.0)
                add_obj(f"{name}_wave{i}", box_mesh("hw", (0.78, 0.9, 0.78)), head, (x, -0.18, z),
                        hm, bevel=0.2, segments=4)
            for i in range(3):  # shorter side tucked behind the other ear
                add_obj(f"{name}_side{i}", box_mesh("hd", (0.42, 0.6, 0.55)), head,
                        (-0.75 + (0.06 if i % 2 else 0), 0.15, 0.95 - i * 0.45), hm, bevel=0.2, segments=3)
        else:  # block
            add_obj(f"{name}_hairtop", box_mesh("ht", (1.35, 1.3, 0.4)), head, (0, 0.05, 1.28), hm, bevel=0.15)

    if spec.get("crop_top"):
        # bare midriff band between the top and high-waisted pants, plus a waistband
        add_obj(f"{name}_midriff", box_mesh("md", (2.03, 1.03, 0.4)), torso, (0, 0, 0.5), skin, bevel=0.05)
        add_obj(f"{name}_waist", box_mesh("wb", (2.07, 1.07, 0.32)), torso, (0, 0, 0.15), pants, bevel=0.05)
        trim = make_material(f"{name}_trim", spec["crop_top"])
        add_obj(f"{name}_hem", box_mesh("hm", (2.07, 1.07, 0.1)), torso, (0, 0, 0.74), trim, bevel=0.03)
        for x in (-0.6, 0.6):  # thin straps over the shoulders
            add_obj(f"{name}_strap{x}", box_mesh("st", (0.22, 1.04, 0.08)), torso, (x, 0, 2.0), trim, bevel=0.02)
    if spec.get("turtleneck"):
        add_obj(f"{name}_collar", box_mesh("tn", (1.2, 1.08, 0.34)), torso, (0, 0, 2.02), shirt,
                bevel=0.14, segments=3)
    if spec.get("knit"):
        rib = make_material(f"{name}_rib", spec["knit"])
        for x in (-0.55, -0.18, 0.18, 0.55):
            add_obj(f"{name}_rib{x}", box_mesh("rb", (0.14, 0.04, 1.75)), torso, (x, -0.515, 0.95), rib, bevel=0.03)
    if spec.get("necklace"):
        gold = metal_material(f"{name}_gold", spec["necklace"])
        for side in (-1, 1):
            add_obj(f"{name}_chain{side}", box_mesh("ch", (0.045, 0.03, 0.76)), torso,
                    (side * 0.18, -0.53, 1.52), gold, bevel=0).rotation_euler = (0, math.radians(side * 28), 0)
        add_obj(f"{name}_pendant", box_mesh("pd", (0.1, 0.06, 0.3)), torso, (0, -0.54, 1.05), gold, bevel=0.03)
    if spec.get("earrings"):
        gold = metal_material(f"{name}_ear_gold", spec["earrings"])
        for x in (-0.66, 0.66):
            add_obj(f"{name}_earring{x}", box_mesh("er", (0.13, 0.13, 0.13)), head, (x, -0.05, 0.4), gold,
                    bevel=0.06, segments=3)

    parts = {"torso": torso, "head": head, "arm_l": arm_l, "arm_r": arm_r, "leg_l": leg_l, "leg_r": leg_r}
    for ob in parts.values():
        ob.rotation_mode = "XYZ"
    return Rig(name, root, parts, mapping)
