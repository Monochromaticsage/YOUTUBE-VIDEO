"""Prop library for dressing sets. Every function places one prop at world position
(x, y) relative to an origin and returns nothing. Blocky, Roblox-like proportions.

Lights: lamps and lit windows add real point lights / emissive glass, so dusk and
night scenes glow.
"""
import math
import random

import bpy

from rig import add_obj, box_mesh, hex_rgba, make_material

_mats = {}


def M(color, rough=0.7, tex=True, scale=4.0):
    key = (color, rough, tex, scale)
    if key not in _mats:
        _mats[key] = make_material(f"p_{color}_{rough}", color, roughness=rough, texture=tex, tex_scale=scale)
    return _mats[key]


def glow(color, strength=6.0):
    key = ("glow", color, strength)
    if key not in _mats:
        mat = bpy.data.materials.new(f"glow_{color}")
        mat.use_nodes = True
        nt = mat.node_tree
        for n in list(nt.nodes):
            if n.type != "OUTPUT_MATERIAL":
                nt.nodes.remove(n)
        em = nt.nodes.new("ShaderNodeEmission")
        em.inputs["Color"].default_value = hex_rgba(color)
        em.inputs["Strength"].default_value = strength
        nt.links.new(em.outputs["Emission"], nt.nodes.get("Material Output").inputs["Surface"])
        mat.diffuse_color = hex_rgba(color)
        _mats[key] = mat
    return _mats[key]


def cyl_mesh(name, r, h, segs=12, r_top=None):
    r_top = r if r_top is None else r_top
    v, f = [], []
    for i in range(segs):
        a = 2 * math.pi * i / segs
        v.append((r * math.cos(a), r * math.sin(a), 0))
        v.append((r_top * math.cos(a), r_top * math.sin(a), h))
    for i in range(segs):
        j = (i + 1) % segs
        f.append((2 * i, 2 * j, 2 * j + 1, 2 * i + 1))
    f.append(tuple(2 * i for i in reversed(range(segs))))
    f.append(tuple(2 * i + 1 for i in range(segs)))
    me = bpy.data.meshes.new(name)
    me.from_pydata(v, [], f)
    me.update()
    return me


def prism_mesh(name, w, d, h):
    """Gable roof: triangle profile along Y."""
    x, y = w / 2, d / 2
    v = [(-x, -y, 0), (x, -y, 0), (0, -y, h), (-x, y, 0), (x, y, 0), (0, y, h)]
    f = [(0, 1, 2), (3, 5, 4), (0, 3, 4, 1), (1, 4, 5, 2), (0, 2, 5, 3)]
    me = bpy.data.meshes.new(name)
    me.from_pydata(v, [], f)
    me.update()
    return me


def put(o, name, mesh, loc, mat, rot=(0, 0, 0), bevel=0.04, segments=2):
    ob = add_obj(name, mesh, None, (o[0] + loc[0], o[1] + loc[1], o[2] + loc[2]), mat, bevel=bevel,
                 segments=segments)
    ob.rotation_euler = rot
    return ob


def point_light(o, loc, color="#ffcf8a", watts=150, radius=0.3):
    ld = bpy.data.lights.new("lamp", "POINT")
    ld.energy = watts
    ld.color = hex_rgba(color)[:3]
    ld.shadow_soft_size = radius
    ob = bpy.data.objects.new("lamp", ld)
    bpy.context.scene.collection.objects.link(ob)
    ob.location = (o[0] + loc[0], o[1] + loc[1], o[2] + loc[2])
    return ob


# -------------------------------------------------------------------- props
def crate(o, x, y, s=1.0, rot=0.0):
    wood = M("#9a6b3c", 0.8, scale=6)
    edge = M("#6e4723", 0.8)
    put(o, "crate", box_mesh("c", (1.6 * s, 1.6 * s, 1.6 * s), (0, 0, -0.8 * s)), (x, y, 0), wood, (0, 0, rot))
    for dz in (0.08, 1.52):
        put(o, "crate_band", box_mesh("cb", (1.66 * s, 1.66 * s, 0.14 * s)), (x, y, dz * s), edge, (0, 0, rot))


def barrel(o, x, y, color="#7a4b2e", rot=0.0):
    put(o, "barrel", cyl_mesh("b", 0.7, 1.8, 14), (x, y, 0), M(color, 0.6, scale=8), (0, 0, rot), bevel=0.05)
    for z in (0.3, 1.4):
        put(o, "barrel_band", cyl_mesh("bb", 0.73, 0.12, 14), (x, y, z), M("#3b3b3b", 0.4), bevel=0)


def lamp_post(o, x, y, light=True, color="#ffcf8a"):
    dark = M("#2d2f36", 0.45)
    put(o, "lamp_pole", cyl_mesh("lp", 0.13, 7.0, 10), (x, y, 0), dark, bevel=0)
    put(o, "lamp_base", cyl_mesh("lb", 0.3, 0.6, 10), (x, y, 0), dark, bevel=0)
    put(o, "lamp_head", box_mesh("lh", (0.8, 0.8, 0.5)), (x, y, 7.15), dark)
    put(o, "lamp_glass", box_mesh("lg", (0.62, 0.62, 0.4)), (x, y, 6.75), glow(color, 8))
    if light:
        point_light(o, (x, y, 6.4), color, watts=220, radius=0.4)


def bench(o, x, y, rot=0.0, color="#8a5a32"):
    wood, metal = M(color, 0.8, scale=7), M("#2d2f36", 0.45)
    c, sn = math.cos(rot), math.sin(rot)

    def at(dx, dy, z):
        return (x + dx * c - dy * sn, y + dx * sn + dy * c, z)
    for dy in (-0.3, 0.05, 0.4):
        put(o, "bench_plank", box_mesh("bp", (3.4, 0.3, 0.12)), at(0, dy, 1.0), wood, (0, 0, rot))
    put(o, "bench_back", box_mesh("bk", (3.4, 0.12, 0.7)), at(0, 0.62, 1.6), wood, (0, 0, rot))
    for dx in (-1.5, 1.5):
        put(o, "bench_leg", box_mesh("bl", (0.15, 1.0, 1.0), (0, 0, -0.5)), at(dx, 0.05, 0), metal, (0, 0, rot))


def fence(o, x0, x1, y, color="#efe6d6", h=2.2):
    mat = M(color, 0.75, scale=6)
    n = max(1, int(abs(x1 - x0) / 2.2))
    for i in range(n + 1):
        x = x0 + (x1 - x0) * i / n
        put(o, "fence_post", box_mesh("fp", (0.28, 0.28, h), (0, 0, -h / 2)), (x, y, 0), mat)
    for z in (0.75, 1.6):
        put(o, "fence_rail", box_mesh("fr", (abs(x1 - x0), 0.16, 0.22)), ((x0 + x1) / 2, y, z), mat)


def sign_post(o, x, y, color="#c0392b", board="#f2e3c6", rot=0.0):
    put(o, "sign_pole", box_mesh("sp", (0.22, 0.22, 4.2), (0, 0, -2.1)), (x, y, 0), M("#5b3a1f"))
    put(o, "sign_board", box_mesh("sb", (2.6, 0.16, 1.3)), (x, y, 3.5), M(board, 0.8), (0, 0, rot))
    put(o, "sign_stripe", box_mesh("ss", (2.3, 0.18, 0.28)), (x, y - 0.01, 3.85), M(color, 0.6), (0, 0, rot))


def trash_can(o, x, y, color="#2f6b3f"):
    put(o, "bin", cyl_mesh("tb", 0.55, 1.5, 12), (x, y, 0), M(color, 0.5), bevel=0.03)
    put(o, "bin_lid", cyl_mesh("tl", 0.62, 0.15, 12), (x, y, 1.5), M("#22262b", 0.5), bevel=0.03)


def cone(o, x, y):
    put(o, "cone", cyl_mesh("cn", 0.4, 1.0, 10, 0.06), (x, y, 0.08), M("#ff6a1a", 0.5), bevel=0)
    put(o, "cone_base", box_mesh("cb", (0.9, 0.9, 0.08), (0, 0, -0.04)), (x, y, 0), M("#ff6a1a", 0.5), bevel=0)


def rock(o, x, y, s=1.0, seed=0):
    r = random.Random(seed)
    ob = put(o, "rock", box_mesh("rk", (1.6 * s, 1.3 * s, 1.0 * s), (0, 0, -0.4 * s)), (x, y, 0),
             M("#7d7f86", 0.9, scale=3), (r.uniform(-0.2, 0.2), r.uniform(-0.2, 0.2), r.uniform(0, 3)),
             bevel=0.35 * s, segments=3)
    return ob


def bush(o, x, y, s=1.0, color="#3f8a3a", seed=0):
    r = random.Random(seed)
    for i in range(3):
        dx, dy = r.uniform(-0.6, 0.6) * s, r.uniform(-0.4, 0.4) * s
        sz = r.uniform(1.0, 1.5) * s
        put(o, "bush", box_mesh("bu", (sz, sz, sz * 0.85), (0, 0, -sz * 0.4)), (x + dx, y + dy, 0),
            M(color, 0.9, scale=2.5), (0, 0, r.uniform(0, 1)), bevel=0.32 * sz, segments=3)


def tree(o, x, y, s=1.0, seed=0, palette=("#2f7d32", "#3e9440", "#276b2a")):
    r = random.Random(seed)
    put(o, "trunk", cyl_mesh("tt", 0.45 * s, 4.5 * s, 8, 0.35 * s), (x, y, 0), M("#6b4226", 0.9, scale=8), bevel=0)
    for i, (z, w) in enumerate(((4.2, 4.2), (5.9, 3.4), (7.2, 2.2))):
        col = palette[i % len(palette)]
        put(o, "leaves", box_mesh("lv", (w * s, w * s, 1.9 * s), (0, 0, -0.9 * s)), (x, y, z * s), M(col, 0.85, scale=2),
            (0, 0, r.uniform(0, 1.5)), bevel=0.45 * s, segments=3)


def house(o, x, y, w=10, d=8, h=7, wall="#e9d8c4", roof="#7b3b2c", lit=True, rot=0.0, seed=0):
    r = random.Random(seed)
    put(o, "house", box_mesh("hs", (w, d, h), (0, 0, -h / 2)), (x, y, 0), M(wall, 0.85, scale=3), (0, 0, rot), bevel=0.06)
    put(o, "roof", prism_mesh("rf", w + 1.2, d + 1.2, h * 0.45), (x, y, h), M(roof, 0.7, scale=5), (0, 0, rot), bevel=0)
    win = glow("#ffcb7a", 3.5) if lit else M("#8fb3cc", 0.2)
    for wx in (-w * 0.28, w * 0.28):
        for wz in (h * 0.3, h * 0.68):
            if r.random() < 0.85:
                put(o, "window", box_mesh("wn", (1.4, 0.12, 1.4)), (x + wx, y - d / 2 - 0.04, wz), win, (0, 0, rot), bevel=0)
    put(o, "door", box_mesh("dr", (1.6, 0.14, 2.8), (0, 0, -1.4)), (x, y - d / 2 - 0.05, 0), M("#5b3a1f", 0.7), (0, 0, rot))


def swings(o, x, y):
    frame = M("#c0392b", 0.5)
    for dx in (-3.2, 3.2):
        for dy in (-1.2, 1.2):
            put(o, "swing_leg", cyl_mesh("sl", 0.14, 6.4, 8), (x + dx, y + dy * 1.0, 0), frame,
                (math.radians(-dy * 9), 0, 0), bevel=0)
    put(o, "swing_bar", box_mesh("sb", (6.8, 0.3, 0.3)), (x, y, 6.25), frame)
    for sx in (-1.5, 1.5):
        for cx in (-0.45, 0.45):
            put(o, "chain", box_mesh("ch", (0.05, 0.05, 4.4)), (x + sx + cx, y, 4.0), M("#8c8c8c", 0.3), bevel=0)
        put(o, "seat", box_mesh("se", (1.2, 0.55, 0.12)), (x + sx, y, 1.8), M("#2d2f36", 0.5))


def slide(o, x, y):
    put(o, "slide_tower", box_mesh("st", (2.4, 2.4, 0.3)), (x, y, 4.0), M("#f1c40f", 0.5))
    for dx in (-1.0, 1.0):
        for dy in (-1.0, 1.0):
            put(o, "slide_post", box_mesh("spo", (0.25, 0.25, 4.0), (0, 0, -2.0)), (x + dx, y + dy, 0), M("#2980b9", 0.5))
    put(o, "slide_ramp", box_mesh("sr", (1.6, 6.5, 0.2)), (x, y - 3.9, 2.1), M("#e74c3c", 0.35),
        (math.radians(-38), 0, 0), bevel=0.05)
    for i in range(6):
        put(o, "ladder", box_mesh("ld", (1.6, 0.15, 0.12)), (x, y + 1.35, 0.6 + i * 0.6), M("#2980b9", 0.5), bevel=0)


def poster(o, x, y, z, color="#f2e3c6", accent="#c0392b", rot=0.0):
    put(o, "poster", box_mesh("po", (1.6, 0.05, 2.1)), (x, y, z), M(color, 0.9), (0, 0, rot), bevel=0)
    put(o, "poster_art", box_mesh("pa", (1.1, 0.06, 0.9)), (x, y - 0.01, z + 0.3), M(accent, 0.8), (0, 0, rot), bevel=0)


def scatter(o, fn, n, xr, yr, seed=1, keep_out=None, **kw):
    """Place n copies of prop fn randomly; keep_out = (x0, x1, y0, y1) stays clear (the stage)."""
    r = random.Random(seed)
    placed = 0
    tries = 0
    while placed < n and tries < n * 30:
        tries += 1
        x, y = r.uniform(*xr), r.uniform(*yr)
        if keep_out and keep_out[0] < x < keep_out[1] and keep_out[2] < y < keep_out[3]:
            continue
        fn(o, x, y, seed=r.randint(0, 9999), **kw) if "seed" in fn.__code__.co_varnames else fn(o, x, y, **kw)
        placed += 1


# ------------------------------------------------------------- story props
# Props that a story needs to show, hide or move. scene_prop() builds one under an empty
# "root" so render_episode can pop it in/out (scale) and animate it (location/rotation).
def _kid(root, name, mesh, loc, mat, bevel=0.04, rot=(0, 0, 0)):
    ob = add_obj(name, mesh, root, loc, mat, bevel=bevel)
    ob.rotation_euler = tuple(math.radians(r) for r in rot)
    return ob


def _vase(root, n):
    blue = M("#3f7fe0", rough=0.25, tex=False)
    white = M("#ffffff", rough=0.3, tex=False)
    _kid(root, f"{n}_body", cyl_mesh("vb", 0.42, 0.9, 16, 0.5), (0, 0, 0), blue, bevel=0)
    _kid(root, f"{n}_band", cyl_mesh("vband", 0.51, 0.14, 16), (0, 0, 0.62), white, bevel=0)
    _kid(root, f"{n}_neck", cyl_mesh("vn", 0.26, 0.55, 16, 0.34), (0, 0, 0.9), blue, bevel=0)
    for i, (dx, dz) in enumerate([(-0.12, 0.25), (0.1, 0.2), (0.0, 0.35)]):  # flowers
        _kid(root, f"{n}_stem{i}", box_mesh("st", (0.05, 0.05, 0.7)), (dx, 0, 1.3), M("#3e8e41"), bevel=0)
        _kid(root, f"{n}_fl{i}", box_mesh("fl", (0.28, 0.28, 0.28)), (dx * 1.6, 0, 1.6 + dz),
             M(("#ff5d8f", "#ffd23f", "#ff8a3d")[i], tex=False), bevel=0.1)
    return 1.3, 4.5


def _shards(root, n):
    blue = M("#3f7fe0", rough=0.25, tex=False)
    for i, (x, y, r) in enumerate([(-0.5, 0.1, 20), (0.35, -0.2, -35), (0.1, 0.4, 70), (-0.15, -0.35, 5),
                                   (0.6, 0.3, 45)]):
        _kid(root, f"{n}_sh{i}", box_mesh("sh", (0.36, 0.28, 0.08)), (x, y, 0.04), blue, bevel=0.02, rot=(8, -6, r))
    for i, (x, y) in enumerate([(-0.3, -0.1), (0.45, 0.05)]):
        _kid(root, f"{n}_fl{i}", box_mesh("fl", (0.25, 0.25, 0.25)), (x, y, 0.12),
             M(("#ff5d8f", "#ffd23f")[i], tex=False), bevel=0.08)
    return 0.3, 3.0


def _piece(root, n):
    _kid(root, f"{n}_p", box_mesh("pc", (0.45, 0.32, 0.09)), (0, 0, 0.05), M("#3f7fe0", rough=0.25, tex=False),
         bevel=0.02, rot=(0, 0, 25))
    return 0.1, 2.2


def _paper_stack(root, n):
    for i in range(14):
        _kid(root, f"{n}_pp{i}", box_mesh("pp", (1.6, 1.2, 0.22)), ((i % 3 - 1) * 0.06, (i % 2) * 0.05, 0.11 + i * 0.23),
             M("#fafafa" if i % 4 else "#ffe9a8", tex=False), bevel=0.02, rot=(0, 0, (i % 5 - 2) * 3))
    return 1.7, 6.0


def _dustpan(root, n):
    red = M("#e53935", rough=0.4, tex=False)
    _kid(root, f"{n}_pan", box_mesh("dp", (1.4, 1.0, 0.08)), (0, 0, 0.04), red, bevel=0.02)
    _kid(root, f"{n}_lip", box_mesh("dl", (1.4, 0.1, 0.35)), (0, 0.5, 0.18), red, bevel=0.02)
    _kid(root, f"{n}_handle", box_mesh("dh", (0.2, 1.1, 0.15)), (0, 1.05, 0.25), red, bevel=0.04)
    return 0.2, 3.0


def _lemon_tree(root, n):
    _kid(root, f"{n}_trunk", box_mesh("tt", (0.8, 0.8, 5)), (0, 0, 2.5), M("#7b4a2a"), bevel=0.1)
    for i, (x, z, s) in enumerate([(0, 6.2, 4.2), (-1.6, 5.4, 2.8), (1.7, 5.5, 2.9), (0, 7.6, 2.6)]):
        _kid(root, f"{n}_leaf{i}", box_mesh("lf", (s, s * 0.9, s * 0.8)), (x, 0, z), M("#43a047"), bevel=0.4)
    rnd = random.Random(4)
    for i in range(14):
        _kid(root, f"{n}_lemon{i}", box_mesh("lm", (0.55, 0.45, 0.45)),
             (rnd.uniform(-2.6, 2.6), -1.9, rnd.uniform(4.6, 8.0)), M("#ffe03a", rough=0.35, tex=False), bevel=0.2)
    return 6.0, 12.0


def _plate(root, n):
    _kid(root, f"{n}_pl", cyl_mesh("pl", 0.75, 0.08, 18), (0, 0, 0), M("#ffffff", rough=0.2, tex=False), bevel=0)
    _kid(root, f"{n}_food", box_mesh("fd", (0.7, 0.5, 0.22)), (0, 0, 0.18), M("#e8a33d"), bevel=0.12)
    _kid(root, f"{n}_peas", box_mesh("pe", (0.4, 0.3, 0.14)), (0.25, 0.25, 0.14), M("#5cb85c"), bevel=0.06)
    return 0.3, 3.0


STORY_PROPS = {"vase": _vase, "shards": _shards, "piece": _piece, "paper_stack": _paper_stack,
               "dustpan": _dustpan, "lemon_tree": _lemon_tree, "plate": _plate}


def _text_obj(root, n, text, size, color, loc, extrude=0.04):
    import os
    cu = bpy.data.curves.new(f"{n}_txt", "FONT")
    cu.body = text
    cu.align_x, cu.align_y = "CENTER", "CENTER"
    cu.size = size
    cu.extrude = extrude
    fp = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "assets", "fonts", "InterDisplay-Black.otf")
    if os.path.exists(fp):
        cu.font = bpy.data.fonts.load(fp, check_existing=True)
    ob = bpy.data.objects.new(f"{n}_txt", cu)
    bpy.context.scene.collection.objects.link(ob)
    ob.parent = root
    ob.location = loc
    ob.rotation_euler = (math.radians(90), 0, 0)
    ob.data.materials.append(M(color, rough=0.4, tex=False))
    return ob


def _sign(root, n, pd):
    """Text on an optional backing board: {"text": "VOTE NOOB", "size": 1.2, "color": "#fff", "board": "#e53935"}"""
    text = pd.get("text", "SIGN")
    size = float(pd.get("size", 1.0))
    if pd.get("board"):
        w = max(1.5, len(text) * size * 0.62 + size)
        h = size * 1.6 * (text.count("\n") + 1)
        _kid(root, f"{n}_board", box_mesh("sb", (w, 0.15, h)), (0, 0.1, 0), M(pd["board"], rough=0.6, tex=False), bevel=0.05)
    _text_obj(root, n, text, size, pd.get("color", "#ffffff"), (0, -0.05, 0))
    return 0.5, 6.0


def _lunchbox(root, n, pd):
    pink = M("#ff6fb5", rough=0.25, tex=False)
    _kid(root, f"{n}_box", box_mesh("lb", (2.0, 1.0, 1.4)), (0, 0, 0.7), pink, bevel=0.12)
    _kid(root, f"{n}_handle", box_mesh("lh", (0.9, 0.2, 0.35)), (0, 0, 1.55), M("#ffd23f", tex=False), bevel=0.08)
    rnd = random.Random(2)
    for i in range(26):  # glitter
        _kid(root, f"{n}_gl{i}", box_mesh("gl", (0.08, 0.04, 0.08)), (rnd.uniform(-0.95, 0.95), -0.52, rnd.uniform(0.1, 1.35)),
             glow(("#fff6b0", "#ffffff", "#ffd1f0")[i % 3], 3.0), bevel=0)
    _text_obj(root, n, "MOMMY'S\nLITTLE STAR", 0.24, "#ffffff", (0, -0.53, 0.72), extrude=0.01)
    return 1.4, 4.0


def _screen(root, n, pd):
    """Pull-down projector screen showing an image file (pd["image"], relative to assets/)."""
    import os
    w, h = float(pd.get("w", 9.0)), float(pd.get("h", 6.0))
    _kid(root, f"{n}_case", box_mesh("sc", (w + 0.6, 0.6, 0.5)), (0, 0, h / 2 + 0.4), M("#eceff1", tex=False), bevel=0.1)
    me = bpy.data.meshes.new(f"{n}_img")
    me.from_pydata([(-w / 2, 0, -h / 2), (w / 2, 0, -h / 2), (w / 2, 0, h / 2), (-w / 2, 0, h / 2)], [], [(0, 1, 2, 3)])
    uv = me.uv_layers.new()
    for li, co in zip(range(4), [(0, 0), (1, 0), (1, 1), (0, 1)]):
        uv.data[li].uv = co
    ob = bpy.data.objects.new(f"{n}_img", me)
    bpy.context.scene.collection.objects.link(ob)
    ob.parent = root
    mat = bpy.data.materials.new(f"{n}_imgmat")
    mat.use_nodes = True
    nt = mat.node_tree
    for nd in list(nt.nodes):
        if nd.type != "OUTPUT_MATERIAL":
            nt.nodes.remove(nd)
    em = nt.nodes.new("ShaderNodeEmission")
    em.inputs["Strength"].default_value = 1.0
    path = os.path.join(os.path.dirname(__file__), "..", "..", "assets", pd.get("image", ""))
    if pd.get("image") and os.path.exists(path):
        tex = nt.nodes.new("ShaderNodeTexImage")
        tex.image = bpy.data.images.load(os.path.abspath(path))
        nt.links.new(tex.outputs["Color"], em.inputs["Color"])
    else:
        em.inputs["Color"].default_value = hex_rgba("#ffffff")
    nt.links.new(em.outputs["Emission"], nt.nodes.get("Material Output").inputs["Surface"])
    me.materials.append(mat)
    _kid(root, f"{n}_bar", box_mesh("sbr", (w + 0.2, 0.25, 0.25)), (0, 0, -h / 2 - 0.1), M("#90a4ae", tex=False), bevel=0.05)
    return 0.0, h * 1.3  # image is centred on the root


def _potato(root, n, pd):
    _kid(root, f"{n}_stand", box_mesh("ps", (2.0, 1.6, 0.25)), (0, 0, 0.12), M("#ffffff", tex=False), bevel=0.05)
    _kid(root, f"{n}_pot", box_mesh("pt", (1.3, 0.85, 0.8)), (0, 0, 0.7), M("#c8a165", rough=0.85, scale=8), bevel=0.35)
    blue = M("#1e63e9", rough=0.4, tex=False)
    _kid(root, f"{n}_rib", cyl_mesh("rb", 0.42, 0.06, 16), (0.55, -0.48, 1.05), blue, bevel=0, rot=(90, 0, 0))
    for side in (-1, 1):
        _kid(root, f"{n}_tail{side}", box_mesh("rt", (0.16, 0.05, 0.6)), (0.55 + side * 0.15, -0.5, 0.65), blue, bevel=0,
             rot=(0, side * 15, 0))
    _text_obj(root, n, "1st", 0.28, "#ffd23f", (0.55, -0.53, 1.05), extrude=0.01)
    return 1.2, 4.0


def _podium(root, n, pd):
    wood = M("#8d6e63", rough=0.5)
    _kid(root, f"{n}_body", box_mesh("pd", (2.6, 1.6, 3.4)), (0, 0, 1.7), wood, bevel=0.08)
    _kid(root, f"{n}_top", box_mesh("pt", (3.0, 1.9, 0.25)), (0, 0, 3.5), M("#6d4c41"), bevel=0.06)
    if pd.get("mic", True):
        _kid(root, f"{n}_mic", box_mesh("mc", (0.08, 0.08, 1.1)), (0, -0.5, 4.1), M("#222222", rough=0.3, tex=False),
             bevel=0, rot=(-25, 0, 0))
        _kid(root, f"{n}_mhead", box_mesh("mh", (0.3, 0.3, 0.35)), (0, -0.75, 4.6), M("#333333", rough=0.3, tex=False),
             bevel=0.12)
    if pd.get("text"):
        _text_obj(root, n, pd["text"], 0.45, "#ffd23f", (0, -0.82, 2.2), extrude=0.02)
    return 3.6, 7.0


def _basket(root, n, pd):
    weave = M("#e0c48c", rough=0.9, scale=10)
    _kid(root, f"{n}_base", box_mesh("bb", (3.4, 2.6, 0.2)), (0, 0, 0.1), weave, bevel=0.05)
    for x, y, sx, sy in [(0, -1.25, 3.4, 0.15), (0, 1.25, 3.4, 0.15), (-1.65, 0, 0.15, 2.6), (1.65, 0, 0.15, 2.6)]:
        _kid(root, f"{n}_w", box_mesh("bw", (sx, sy, 1.4)), (x, y, 0.75), weave, bevel=0.04)
    for i in range(3):
        _kid(root, f"{n}_sock{i}", box_mesh("bs", (0.9, 0.5, 0.25)), (-1.0 + i * 1.0, 0.6, 0.4),
             M(("#ffffff", "#81d4fa", "#ff8fab")[i], tex=False), bevel=0.1)
    return 1.4, 6.0


STORY_PROPS.update({"lunchbox": _lunchbox, "screen": _screen, "potato": _potato, "podium": _podium,
                    "basket": _basket, "sign": _sign})


def _feather(root, n, pd):
    """A big fluffy feather standing upright (held / propped by a character): {"color": "#ffffff"}"""
    col = M(pd.get("color", "#ffffff"), rough=0.9, tex=False)
    _kid(root, f"{n}_quill", cyl_mesh("fq", 0.05, 2.4, 8), (0, 0, 0), M("#d9c9a8", tex=False), bevel=0)
    for i in range(7):
        z = 0.7 + i * 0.32
        w = 0.5 + 0.45 * math.sin(math.pi * (i + 0.5) / 7)
        _kid(root, f"{n}_vane{i}", box_mesh("fv", (w, 0.08, 0.36)), (0, 0, z), col, bevel=0.12, rot=(0, (i % 2) * 6 - 3, 0))
    return 3.0, 4.0


STORY_PROPS["feather"] = _feather


def _broccoli(root, n, pd):
    """A little pile of broccoli florets (sits on a plate)."""
    g = M("#3e9b3a", rough=0.8, tex=False)
    for i, (x, y) in enumerate([(-0.3, 0), (0.25, 0.1), (0, -0.25), (0.05, 0.3)]):
        _kid(root, f"{n}_st{i}", cyl_mesh("bs", 0.09, 0.3, 8), (x, y, 0), M("#9ccc65", tex=False), bevel=0)
        _kid(root, f"{n}_fl{i}", box_mesh("bf", (0.38, 0.38, 0.3)), (x, y, 0.38), g, bevel=0.14)
    return 0.6, 3.0


def _juice(root, n, pd):
    """A glass of red juice."""
    glass = M("#e8f4ff", rough=0.1, tex=False)
    _kid(root, f"{n}_glass", cyl_mesh("jg", 0.32, 0.95, 16), (0, 0, 0), glass, bevel=0)
    _kid(root, f"{n}_juice", cyl_mesh("jj", 0.335, 0.8, 16), (0, 0, 0.04), M("#e0263a", rough=0.3, tex=False), bevel=0)
    return 1.0, 3.0


def _img_quad(root, n, image, w, h, loc, horizontal=False, glow=1.0):
    """A flat picture (emissive) from assets/<image>. Upright facing -Y, or lying flat facing up."""
    import os
    me = bpy.data.meshes.new(f"{n}_img")
    if horizontal:
        me.from_pydata([(-w / 2, -h / 2, 0), (w / 2, -h / 2, 0), (w / 2, h / 2, 0), (-w / 2, h / 2, 0)], [], [(0, 1, 2, 3)])
    else:
        me.from_pydata([(-w / 2, 0, -h / 2), (w / 2, 0, -h / 2), (w / 2, 0, h / 2), (-w / 2, 0, h / 2)], [], [(0, 1, 2, 3)])
    uv = me.uv_layers.new()
    for li, co in zip(range(4), [(0, 0), (1, 0), (1, 1), (0, 1)]):
        uv.data[li].uv = co
    ob = bpy.data.objects.new(f"{n}_img", me)
    bpy.context.scene.collection.objects.link(ob)
    ob.parent = root
    ob.location = loc
    mat = bpy.data.materials.new(f"{n}_imgmat")
    mat.use_nodes = True
    nt = mat.node_tree
    for nd in list(nt.nodes):
        if nd.type != "OUTPUT_MATERIAL":
            nt.nodes.remove(nd)
    em = nt.nodes.new("ShaderNodeEmission")
    em.inputs["Strength"].default_value = glow
    path = os.path.join(os.path.dirname(__file__), "..", "..", "assets", image or "")
    if image and os.path.exists(path):
        tex = nt.nodes.new("ShaderNodeTexImage")
        tex.image = bpy.data.images.load(os.path.abspath(path))
        nt.links.new(tex.outputs["Color"], em.inputs["Color"])
    else:
        em.inputs["Color"].default_value = hex_rgba("#ffffff")
    nt.links.new(em.outputs["Emission"], nt.nodes.get("Material Output").inputs["Surface"])
    me.materials.append(mat)
    return ob


def _laptop(root, n, pd):
    """Open laptop; the screen shows pd["image"]."""
    dark = M("#2b2f36", rough=0.4, tex=False)
    _kid(root, f"{n}_base", box_mesh("lb", (2.4, 1.6, 0.14)), (0, 0, 0.07), dark, bevel=0.04)
    _kid(root, f"{n}_lid", box_mesh("ll", (2.4, 0.1, 1.6)), (0, 0.78, 0.94), dark, bevel=0.04)
    _img_quad(root, n, pd.get("image"), 2.15, 1.38, (0, 0.72, 0.95))
    return 1.7, 4.0


def _slip(root, n, pd):
    """A detention slip lying flat (image from pd["image"])."""
    _kid(root, f"{n}_paper", box_mesh("sp", (1.5, 1.05, 0.02)), (0, 0, 0.01), M("#fffbe6", tex=False), bevel=0)
    _img_quad(root, n, pd.get("image"), 1.44, 1.0, (0, 0, 0.025), horizontal=True, glow=0.9)
    return 0.1, 3.0


STORY_PROPS.update({"broccoli": _broccoli, "juice": _juice, "laptop": _laptop, "slip": _slip})


def _cookie(root, n, x, y, z, r=0.32):
    _kid(root, n, cyl_mesh("ck", r, 0.12, 14), (x, y, z), M("#c98d4b", rough=0.8, tex=False), bevel=0)
    for k in range(3):
        a = k * 2.1
        _kid(root, f"{n}_chip{k}", box_mesh("cc", (0.08, 0.08, 0.04)), (x + r * 0.5 * math.cos(a), y + r * 0.5 * math.sin(a), z + 0.12),
             M("#3e2414", tex=False), bevel=0)


def _cookie_jar(root, n, pd):
    """Glass cookie jar with a red lid, full of cookies."""
    _kid(root, f"{n}_jar", cyl_mesh("cj", 0.75, 1.5, 18), (0, 0, 0), M("#dff1ff", rough=0.15, tex=False), bevel=0)
    _kid(root, f"{n}_lid", cyl_mesh("cl", 0.8, 0.22, 18), (0, 0, 1.5), M("#e53935", rough=0.4, tex=False), bevel=0)
    _kid(root, f"{n}_knob", box_mesh("kn", (0.3, 0.3, 0.22)), (0, 0, 1.8), M("#e53935", tex=False), bevel=0.08)
    for i in range(4):
        _cookie(root, f"{n}_c{i}", 0, -0.62, 0.25 + i * 0.3, r=0.28)
    return 2.0, 3.6


def _chocolate(root, n, pd):
    """A chocolate bar in a red wrapper, standing on its end."""
    _kid(root, f"{n}_bar", box_mesh("ch", (0.7, 0.18, 1.1)), (0, 0, 0.55), M("#5a3220", tex=False), bevel=0.04)
    _kid(root, f"{n}_wrap", box_mesh("cw", (0.74, 0.2, 0.55)), (0, 0, 0.3), M("#d32f2f", tex=False), bevel=0.03)
    return 1.1, 3.0


def _stash(root, n, pd):
    """A huge hidden pile of cookies and chocolate bars."""
    for i in range(14):
        x, y = (i % 5) * 0.75 - 1.5, (i // 5) * 0.6 - 0.6
        if i % 3 == 0:
            _kid(root, f"{n}_bar{i}", box_mesh("sb", (0.7, 0.2, 1.0)), (x, y, 0.5 + (i % 2) * 0.4), M("#d32f2f" if i % 2 else "#5a3220", tex=False),
                 bevel=0.03, rot=(0, 0, i * 17))
        else:
            for k in range(1 + i % 3):
                _cookie(root, f"{n}_ck{i}_{k}", x, y, 0.1 + k * 0.16, r=0.34)
    _kid(root, f"{n}_box", box_mesh("bx", (3.8, 2.0, 0.6)), (0, 0, 0.3), M("#c49a6c", rough=0.9, tex=False), bevel=0.05)
    return 1.6, 5.0


STORY_PROPS.update({"cookie_jar": _cookie_jar, "chocolate": _chocolate, "stash": _stash})


def _pencil(root, n, pd):
    """A pencil pointing along -Z (so it sticks out of a fist); "gold": true for the magic one."""
    gold = pd.get("gold")
    body = M("#ffcf33" if not gold else "#ffd700", rough=0.25 if gold else 0.6, tex=False)
    _kid(root, f"{n}_body", box_mesh("pb", (0.22, 0.22, 1.5)), (0, 0, -0.45), body, bevel=0.03)
    _kid(root, f"{n}_tip", cyl_mesh("pt", 0.12, 0.3, 8, 0.02), (0, 0, -1.5), M("#f1c79a", tex=False), bevel=0, rot=(180, 0, 0))
    _kid(root, f"{n}_lead", box_mesh("pl", (0.06, 0.06, 0.1)), (0, 0, -1.77), M("#333333", tex=False), bevel=0)
    _kid(root, f"{n}_band", box_mesh("pn", (0.24, 0.24, 0.12)), (0, 0, 0.36), M("#c0c0c0", rough=0.3, tex=False), bevel=0.02)
    _kid(root, f"{n}_eraser", box_mesh("pe", (0.23, 0.23, 0.2)), (0, 0, 0.5), M("#ff8fab", tex=False), bevel=0.04)
    if gold:
        for k in range(3):
            _kid(root, f"{n}_spark{k}", box_mesh("sp", (0.12, 0.12, 0.12)), (0.3 * math.cos(k * 2.1), 0.3 * math.sin(k * 2.1), -0.4 + k * 0.3),
                 M("#fff59d", tex=False), bevel=0.04)
    return 0.4, 3.0


def _tri_mesh(name, pts, h):
    """Extruded flat polygon (pts in XY), thickness h."""
    v = [(x, y, 0) for x, y in pts] + [(x, y, h) for x, y in pts]
    n = len(pts)
    f = [tuple(range(n))[::-1], tuple(range(n, 2 * n))]
    for i in range(n):
        j = (i + 1) % n
        f.append((i, j, n + j, n + i))
    me = bpy.data.meshes.new(name)
    me.from_pydata(v, [], f)
    return me


def _flat_pizza(root, n, pd):
    """A big pizza slice as flat as the drawing it came from: crust, cheese, pepperoni."""
    tri = [(-1.1, -0.8), (1.3, 0.0), (-1.1, 0.8)]
    _kid(root, f"{n}_crust", _tri_mesh("pc", [(-1.25, -0.95), (1.45, 0.0), (-1.25, 0.95)], 0.06), (0, 0, 0), M("#d9a25f", rough=0.8, tex=False), bevel=0)
    _kid(root, f"{n}_cheese", _tri_mesh("pz", tri, 0.05), (0, 0, 0.05), M("#ffcf4a", rough=0.6, tex=False), bevel=0)
    _kid(root, f"{n}_edge", box_mesh("pe", (0.28, 1.95, 0.16)), (-1.2, 0, 0.08), M("#c98a45", rough=0.8, tex=False), bevel=0.06)
    for k, (x, y) in enumerate([(-0.55, -0.3), (-0.5, 0.35), (0.1, 0.0), (0.55, 0.12), (-0.05, -0.4)]):
        _kid(root, f"{n}_pep{k}", cyl_mesh("pp", 0.17, 0.04, 14), (x, y, 0.1), M("#b3261e", rough=0.5, tex=False), bevel=0)
    return 0.15, 4.0


def _car_sq(root, n, pd):
    """A shiny cartoon sports car... with SQUARE wheels (because it was drawn that way). Faces +X."""
    red = M(pd.get("color", "#e3262f"), rough=0.4, tex=False)
    dark = M("#1d1d22", rough=0.5, tex=False)
    glass = M("#7fb8e6", rough=0.05, tex=False)
    chrome = M("#d9d9df", rough=0.15, tex=False)
    _kid(root, f"{n}_body", box_mesh("cb", (4.6, 2.1, 0.9)), (0, 0, 1.05), red, bevel=0.35)
    _kid(root, f"{n}_hood", box_mesh("ch", (1.5, 2.0, 0.35)), (1.45, 0, 1.55), red, bevel=0.15)
    _kid(root, f"{n}_cab", box_mesh("cc", (2.1, 1.9, 0.95)), (-0.35, 0, 1.95), red, bevel=0.35)
    _kid(root, f"{n}_wind", box_mesh("cw", (0.12, 1.7, 0.7)), (0.72, 0, 1.98), glass, bevel=0.04, rot=(0, -28, 0))
    for y in (-0.96, 0.96):
        _kid(root, f"{n}_side{y}", box_mesh("cs", (1.6, 0.06, 0.6)), (-0.4, y, 2.0), glass, bevel=0.03)
        _kid(root, f"{n}_mirror{y}", box_mesh("cm", (0.2, 0.25, 0.18)), (0.6, y * 1.12, 1.75), red, bevel=0.05)
        _kid(root, f"{n}_lamp{y}", box_mesh("cl", (0.08, 0.5, 0.25)), (2.3, y * 0.62, 1.2), M("#fff6b0", rough=0.1, tex=False), bevel=0.03)
        _kid(root, f"{n}_tail{y}", box_mesh("ct", (0.08, 0.5, 0.2)), (-2.3, y * 0.62, 1.25), M("#ff3b30", rough=0.2, tex=False), bevel=0.03)
    _kid(root, f"{n}_grille", box_mesh("cg", (0.06, 0.9, 0.3)), (2.32, 0, 0.95), dark, bevel=0.02)
    for x in (2.25, -2.25):
        _kid(root, f"{n}_bumper{x}", box_mesh("cu", (0.25, 2.15, 0.25)), (x, 0, 0.7), chrome, bevel=0.08)
    for k, (x, y) in enumerate([(-1.45, -1.05), (1.45, -1.05), (-1.45, 1.05), (1.45, 1.05)]):
        _kid(root, f"{n}_wheel{k}", box_mesh("cq", (1.0, 0.42, 1.0)), (x, y, 0.5), dark, bevel=0.04)
        _kid(root, f"{n}_hub{k}", box_mesh("hb", (0.42, 0.44, 0.42)), (x, y, 0.5), chrome, bevel=0.04)
    return 2.6, 8.0


def _potato_dog(root, n, pd):
    """A 'puppy' that came out looking like a potato with legs."""
    tan = M("#c8a165", rough=0.85, scale=8)
    _kid(root, f"{n}_body", box_mesh("db", (1.6, 1.0, 0.9)), (0, 0, 0.85), tan, bevel=0.35)
    for k, (x, y) in enumerate([(-0.5, -0.3), (0.5, -0.3), (-0.5, 0.3), (0.5, 0.3)]):
        _kid(root, f"{n}_leg{k}", box_mesh("dl", (0.16, 0.16, 0.5)), (x, y, 0.25), M("#8d6e43", tex=False), bevel=0.03)
    for x in (0.55, 0.85):
        _kid(root, f"{n}_eye{x}", box_mesh("de", (0.16, 0.05, 0.16)), (x - 0.2, -0.5, 1.05), M("#ffffff", tex=False), bevel=0)
        _kid(root, f"{n}_pup{x}", box_mesh("dp", (0.08, 0.06, 0.08)), (x - 0.2, -0.53, 1.03), M("#111111", tex=False), bevel=0)
    _kid(root, f"{n}_tail", box_mesh("dt", (0.4, 0.1, 0.1)), (-0.95, 0, 1.1), M("#8d6e43", tex=False), bevel=0.03, rot=(0, -30, 0))
    _kid(root, f"{n}_ear", box_mesh("dr", (0.2, 0.06, 0.3)), (0.55, -0.1, 1.35), M("#8d6e43", tex=False), bevel=0.03)
    return 1.3, 4.0


def _baby_bottle(root, n, pd):
    """A baby bottle (milk, pink cap and teat)."""
    _kid(root, f"{n}_body", cyl_mesh("bb", 0.28, 0.9, 16), (0, 0, 0), M("#f4fbff", rough=0.15, tex=False), bevel=0)
    _kid(root, f"{n}_milk", cyl_mesh("bm", 0.25, 0.6, 16), (0, 0, 0.02), M("#ffffff", rough=0.5, tex=False), bevel=0)
    _kid(root, f"{n}_cap", cyl_mesh("bc", 0.3, 0.18, 16), (0, 0, 0.9), M("#ff8fb1", rough=0.4, tex=False), bevel=0)
    _kid(root, f"{n}_teat", cyl_mesh("bt", 0.12, 0.25, 12, 0.06), (0, 0, 1.08), M("#ffd8a8", rough=0.5, tex=False), bevel=0)
    return 1.3, 3.0


STORY_PROPS["baby_bottle"] = _baby_bottle


def _cable(root, n, pd):
    """A long charging cable lying along +X with a plug at the end: {"length": 6}."""
    L = float(pd.get("length", 6.0))
    blk = M(pd.get("color", "#1f1f24"), rough=0.5, tex=False)
    _kid(root, f"{n}_wire", box_mesh("cw", (L, 0.12, 0.12)), (L / 2, 0, 0.06), blk, bevel=0.04)
    _kid(root, f"{n}_plug", box_mesh("cp", (0.5, 0.3, 0.3)), (0, 0, 0.15), M("#f5f5f5", tex=False), bevel=0.05)
    _kid(root, f"{n}_bolt", box_mesh("cb", (0.12, 0.31, 0.12)), (0, 0, 0.18), M("#ffd23f", tex=False), bevel=0)
    return 0.3, 4.0


STORY_PROPS["cable"] = _cable


def _phone(root, n, pd):
    """A smartphone lying flat, screen up (pd["image"] for the screen)."""
    _kid(root, f"{n}_body", box_mesh("ph", (0.62, 1.15, 0.08)), (0, 0, 0.04), M("#1c1c22", rough=0.3, tex=False), bevel=0.04)
    _img_quad(root, n, pd.get("image"), 0.54, 1.02, (0, 0, 0.085), horizontal=True, glow=1.2)
    return 0.1, 2.5


def _cake(root, n, pd):
    """A two-layer birthday cake with candles."""
    _kid(root, f"{n}_plate", cyl_mesh("cp", 1.2, 0.08, 20), (0, 0, 0), M("#ffffff", tex=False), bevel=0)
    _kid(root, f"{n}_l1", cyl_mesh("c1", 0.95, 0.6, 20), (0, 0, 0.08), M("#ffb3c7", rough=0.6, tex=False), bevel=0)
    _kid(root, f"{n}_l2", cyl_mesh("c2", 0.65, 0.45, 20), (0, 0, 0.68), M("#fff0f5", rough=0.6, tex=False), bevel=0)
    for k in range(5):
        a = k * 2 * math.pi / 5
        _kid(root, f"{n}_cherry{k}", box_mesh("cc", (0.16, 0.16, 0.16)), (0.8 * math.cos(a), 0.8 * math.sin(a), 0.72), M("#d32f2f", tex=False), bevel=0.06)
    for k in range(3):
        x = (k - 1) * 0.3
        _kid(root, f"{n}_candle{k}", box_mesh("cn", (0.08, 0.08, 0.4)), (x, 0, 1.33), M("#64b5f6", tex=False), bevel=0)
        _kid(root, f"{n}_flame{k}", box_mesh("cf", (0.08, 0.08, 0.14)), (x, 0, 1.6), M("#ffd23f", tex=False), bevel=0.03)
    return 1.7, 4.0


def _marker(root, n, pd):
    """A fat marker pointing along -Z (fits a fist like the pencil)."""
    c = pd.get("color", "#8e24aa")
    _kid(root, f"{n}_body", box_mesh("mb", (0.3, 0.3, 1.2)), (0, 0, -0.35), M("#f5f5f5", tex=False), bevel=0.06)
    _kid(root, f"{n}_cap", box_mesh("mc", (0.32, 0.32, 0.4)), (0, 0, -1.1), M(c, tex=False), bevel=0.06)
    _kid(root, f"{n}_band", box_mesh("mn", (0.31, 0.31, 0.15)), (0, 0, 0.3), M(c, tex=False), bevel=0.03)
    return 0.4, 3.0


def _poster(root, n, pd):
    """A picture stuck flat on a wall, facing -Y (pd["image"], "w", "h")."""
    w, h = float(pd.get("w", 2.0)), float(pd.get("h", 1.5))
    _kid(root, f"{n}_back", box_mesh("pb", (w + 0.12, 0.04, h + 0.12)), (0, 0.03, 0), M(pd.get("frame", "#ffffff"), tex=False), bevel=0)
    _img_quad(root, n, pd.get("image"), w, h, (0, -0.01, 0), glow=0.95)
    return 0.0, max(w, h) * 1.6


STORY_PROPS.update({"phone": _phone, "cake": _cake, "marker": _marker, "poster": _poster})


def _banana(root, n, pd):
    """A banana held like a camera (points along -Z out of a fist), with a tiny red LIVE dot."""
    y = M("#ffd93b", rough=0.5, tex=False)
    for k in range(5):
        a = math.radians(-12 + k * 6)
        _kid(root, f"{n}_seg{k}", box_mesh("bn", (0.34, 0.34, 0.42)), (0.08 * k * k * 0.25, 0, -0.1 - k * 0.38), y, bevel=0.12,
             rot=(0, math.degrees(a), 0))
    _kid(root, f"{n}_tip", box_mesh("bt", (0.16, 0.16, 0.18)), (0.5, 0, -2.0), M("#5d4037", tex=False), bevel=0.04)
    _kid(root, f"{n}_stem", box_mesh("bs", (0.14, 0.14, 0.25)), (0, 0, 0.15), M("#7a5c2e", tex=False), bevel=0.03)
    _kid(root, f"{n}_live", box_mesh("bl", (0.1, 0.06, 0.1)), (0.2, -0.18, -0.6), M("#ff1f1f", rough=0.2, tex=False), bevel=0.02)
    return 0.4, 3.0


STORY_PROPS["banana"] = _banana


def _nose_light(root, n, pd):
    """A glowing red lie-detector nose (attach to "<name>:head")."""
    _kid(root, f"{n}_bulb", box_mesh("nl", (0.32, 0.22, 0.26)), (0, 0, 0), glow(pd.get("color", "#ff2020"), 6.0), bevel=0.08)
    return 0.3, 2.0


def _headband(root, n, pd):
    """A sporty headband (attach to "<name>:head")."""
    _kid(root, f"{n}_band", box_mesh("hb", (1.36, 1.31, 0.26)), (0, 0, 0), M(pd.get("color", "#e53935"), tex=False), bevel=0.06)
    _kid(root, f"{n}_knot", box_mesh("hk", (0.3, 0.2, 0.5)), (0.3, 0.7, -0.15), M(pd.get("color", "#e53935"), tex=False), bevel=0.06,
         rot=(20, 0, 30))
    return 0.3, 2.0


def _rope(root, n, pd):
    """A long tug-of-war rope along +X with a red flag in the middle."""
    L = float(pd.get("length", 14))
    _kid(root, f"{n}_rope", box_mesh("rp", (L, 0.22, 0.22)), (0, 0, 0), M("#c9a46a", rough=0.9, tex=False), bevel=0.06)
    _kid(root, f"{n}_flag", box_mesh("rf", (0.3, 0.1, 0.8)), (0, 0, -0.5), M("#e53935", tex=False), bevel=0.02)
    return 0.3, 8.0


def _baton(root, n, pd):
    _kid(root, f"{n}_b", box_mesh("bt", (0.25, 0.25, 1.1)), (0, 0, -0.4), M(pd.get("color", "#ffd23f"), rough=0.3, tex=False), bevel=0.06)
    return 0.3, 2.0


def _trophy(root, n, pd):
    """A shiny gold trophy."""
    gold = M("#ffcc33", rough=0.2, tex=False)
    _kid(root, f"{n}_base", box_mesh("tb", (0.9, 0.9, 0.35)), (0, 0, 0.18), M("#5d4037", tex=False), bevel=0.05)
    _kid(root, f"{n}_stem", box_mesh("ts", (0.22, 0.22, 0.6)), (0, 0, 0.65), gold, bevel=0.04)
    _kid(root, f"{n}_cup", cyl_mesh("tc", 0.55, 0.8, 16, 0.3), (0, 0, 0.95), gold, bevel=0, rot=(180, 0, 0))
    for x in (-0.65, 0.65):
        _kid(root, f"{n}_h{x}", box_mesh("th", (0.15, 0.12, 0.5)), (x, 0, 1.5), gold, bevel=0.04)
    return 1.8, 4.0


def _medal(root, n, pd):
    """A champion medal on a ribbon, lying flat."""
    _kid(root, f"{n}_rib", box_mesh("mr", (0.3, 1.2, 0.03)), (0, 0.5, 0.02), M("#1e63e9", tex=False), bevel=0)
    _kid(root, f"{n}_disc", cyl_mesh("md", 0.35, 0.06, 18), (0, 0, 0.02), M("#ffcc33", rough=0.2, tex=False), bevel=0)
    return 0.1, 2.5


def _ball(root, n, pd):
    _kid(root, f"{n}_ball", box_mesh("bl", (0.7, 0.7, 0.7)), (0, 0, 0.35), M(pd.get("color", "#e53935"), rough=0.4, tex=False), bevel=0.3)
    return 0.7, 3.0


STORY_PROPS.update({"nose_light": _nose_light, "headband": _headband, "rope": _rope, "baton": _baton, "trophy": _trophy,
                    "medal": _medal, "ball": _ball})


STORY_PROPS.update({"pencil": _pencil, "flat_pizza": _flat_pizza, "car_sq": _car_sq, "potato_dog": _potato_dog})


def scene_prop(pd, origin):
    """pd: {"id": "vase", "type": "vase", "at": [x, y, z], "rot": deg, "scale": 1.0}"""
    from mathutils import Vector
    root = bpy.data.objects.new(f"prop_{pd['id']}", None)
    bpy.context.scene.collection.objects.link(root)
    at = pd.get("at", (0, 0, 0))
    root.location = (origin[0] + at[0], origin[1] + at[1], origin[2] + (at[2] if len(at) > 2 else 0))
    root.rotation_euler = (0, 0, math.radians(pd.get("rot", 0)))
    s = float(pd.get("scale", 1.0))
    root.scale = (s, s, s)
    if pd["type"] not in STORY_PROPS:
        raise ValueError(f"unknown prop type '{pd['type']}'. Available: {sorted(STORY_PROPS)}")
    fn = STORY_PROPS[pd["type"]]
    h, dist = fn(root, pd["id"], pd) if fn.__code__.co_argcount >= 3 else fn(root, pd["id"])
    center = Vector(root.location) + Vector((0, 0, h * 0.5 * s))
    return {"root": root, "center": center, "scale": (s, s, s), "cam_dist": pd.get("cam_dist", dist * s)}
