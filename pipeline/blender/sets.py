"""Reusable sets. Each builder places its props around `origin` and returns
named "marks" (where characters stand), relative to the origin.

To use a real map exported from Roblox Studio instead, save it as
assets/sets/<name>.fbx or .obj and set "set": "<name>" in the episode;
the generic loader below imports it and uses the default marks.
"""
import os
import random

import bpy

from rig import add_obj, box_mesh, make_material

DEFAULT_MARKS = {
    "far_left": (-5, 0, 0), "left": (-2.6, 0, 0), "center": (0, 0, 0), "right": (2.6, 0, 0),
    "far_right": (5, 0, 0), "back_left": (-2.5, 4, 0), "back_right": (2.5, 4, 0), "back": (0, 4, 0),
}

_mats = {}


def M(color):
    if color not in _mats:
        _mats[color] = make_material(f"set_{color}", color, roughness=0.7)
    return _mats[color]


def block(o, name, size, loc, color, bevel=0.04):
    return add_obj(name, box_mesh(name, size), None, (o[0] + loc[0], o[1] + loc[1], o[2] + loc[2]),
                   M(color), bevel=bevel)


def _room(o, floor, wall, depth=14, width=34):
    block(o, "floor", (width, depth + 20, 0.4), (0, depth / 2 - 6, -0.2), floor, bevel=0)
    block(o, "wall_back", (width, 0.6, 16), (0, depth - 2, 8), wall, bevel=0)
    block(o, "wall_l", (0.6, depth + 8, 16), (-width / 2, depth / 2 - 4, 8), wall, bevel=0)
    block(o, "wall_r", (0.6, depth + 8, 16), (width / 2, depth / 2 - 4, 8), wall, bevel=0)


def desk(o, x, y):
    block(o, "desk_top", (3, 2, 0.25), (x, y, 2.6), "#a0703f")
    for dx in (-1.3, 1.3):
        for dy in (-0.8, 0.8):
            block(o, "desk_leg", (0.2, 0.2, 2.5), (x + dx, y + dy, 1.25), "#3a3a3a", bevel=0)


def classroom(o):
    _room(o, floor="#c9b48a", wall="#e8e2cf")
    block(o, "board", (12, 0.2, 5), (0, 11.6, 7.5), "#22412f")
    block(o, "board_frame", (12.6, 0.15, 5.6), (0, 11.7, 7.5), "#8a5a2b")
    block(o, "teacher_desk", (5, 2.5, 2.6), (8, 9, 1.3), "#8a5a2b")
    for x in (-10, -5.5, 5.5, 10):
        desk(o, x, 2.8)
    for x in (-14, 14):
        block(o, "window", (0.2, 5, 5), (x * 1.19, 4, 8), "#9fd3ff", bevel=0)
    block(o, "clock", (1.4, 0.2, 1.4), (-9, 11.5, 11), "#ffffff")
    return dict(DEFAULT_MARKS, teacher=(0, 6.5, 0), board=(0, 9, 0))


def _checker_material(name, c1, c2, scale=0.5, rough=0.35):
    from rig import hex_rgba
    mat = bpy.data.materials.new(name)
    mat.use_nodes = True
    nt = mat.node_tree
    bsdf = nt.nodes.get("Principled BSDF")
    tc = nt.nodes.new("ShaderNodeTexCoord")
    ch = nt.nodes.new("ShaderNodeTexChecker")
    ch.inputs["Color1"].default_value = hex_rgba(c1)
    ch.inputs["Color2"].default_value = hex_rgba(c2)
    ch.inputs["Scale"].default_value = scale
    nt.links.new(tc.outputs["Object"], ch.inputs["Vector"])
    nt.links.new(ch.outputs["Color"], bsdf.inputs["Base Color"])
    bsdf.inputs["Roughness"].default_value = rough
    mat.diffuse_color = hex_rgba(c1)
    return mat


def _wall_text(o, text, loc, size, color, extrude=0.08):
    from rig import hex_rgba
    cu = bpy.data.curves.new("walltxt", "FONT")
    cu.body = text
    cu.align_x, cu.align_y = "CENTER", "CENTER"
    cu.size = size
    cu.extrude = extrude
    for fp in ("/usr/share/fonts/opentype/inter/InterDisplay-Black.otf", "C:/Windows/Fonts/ariblk.ttf"):
        if os.path.exists(fp):
            cu.font = bpy.data.fonts.load(fp)
            break
    ob = bpy.data.objects.new("walltxt", cu)
    bpy.context.scene.collection.objects.link(ob)
    ob.location = (o[0] + loc[0], o[1] + loc[1], o[2] + loc[2])
    ob.rotation_euler = (1.5708, 0, 0)
    ob.data.materials.append(make_material(f"txt_{color}", color, roughness=0.4, texture=False))
    return ob


def _locker_bank(o, x0, count, y, colors, P):
    for i in range(count):
        x = x0 + i * 2.0
        col = colors[i % len(colors)]
        P.put(o, "locker", box_mesh("lk", (1.9, 1.3, 6.4), (0, 0, -3.2)), (x, y, 0.5), P.M(col, 0.35, scale=3), bevel=0.05)
        for k in range(3):
            P.put(o, "vent", box_mesh("lv", (1.0, 0.08, 0.12)), (x, y - 0.66, 5.9 - k * 0.25), P.M("#1b2a44", 0.5), bevel=0)
        P.put(o, "handle", box_mesh("lh", (0.12, 0.12, 0.6)), (x + 0.6, y - 0.7, 3.4), P.M("#c9ced6", 0.25), bevel=0.03)
        P.put(o, "lnum", box_mesh("ln", (0.5, 0.06, 0.25)), (x, y - 0.67, 5.05), P.M("#e8e3d5", 0.5), bevel=0)
    P.put(o, "locker_base", box_mesh("lb", (count * 2.0, 1.32, 0.5), (0, 0, -0.25)),
          (x0 + (count - 1), y, 0), P.M("#22262b", 0.6), bevel=0.02)
    P.put(o, "locker_top", box_mesh("lt", (count * 2.0, 1.4, 0.25), (0, 0, -0.125)),
          (x0 + (count - 1), y, 6.9), P.M("#22262b", 0.6), bevel=0.02)


def _door(o, x, y, P, color="#9a6234"):
    P.put(o, "door_frame", box_mesh("df", (4.0, 0.5, 8.4), (0, 0, -4.2)), (x, y, 0), P.M("#e8e3d5", 0.5), bevel=0.05)
    P.put(o, "door", box_mesh("dr", (3.2, 0.5, 7.8), (0, 0, -3.9)), (x, y - 0.12, 0), P.M(color, 0.6, scale=5), bevel=0.05)
    P.put(o, "door_win", box_mesh("dw", (1.1, 0.5, 2.2)), (x - 0.6, y - 0.16, 5.5), P.glow("#bfe6ff", 1.4), bevel=0.03)
    P.put(o, "door_knob", box_mesh("dk", (0.3, 0.3, 0.3)), (x + 1.1, y - 0.5, 3.6), P.M("#d4a62a", 0.2), bevel=0.1)
    P.put(o, "door_plaque", box_mesh("dp", (1.6, 0.1, 0.5)), (x, y - 0.3, 8.9), P.M("#1f3b73", 0.4), bevel=0.03)


def hallway(o):
    """School hallway: checker floor, two-tone walls, locker banks, doors, trophy case,
    bulletin board, banner, clock, plants and foreground pillars that blur with depth of field."""
    import props as P
    floor = _checker_material("hall_floor", "#e9e2d0", "#b9b2a2", scale=0.25, rough=0.3)
    add_obj("hall_floor", box_mesh("hf", (140, 70, 0.4)), None, (o[0], o[1] + 5, o[2] - 0.2), floor, bevel=0)
    wy = 9.4
    add_obj("wall_low", box_mesh("wl", (140, 0.6, 4.2)), None, (o[0], o[1] + wy, o[2] + 2.1),
            make_material("hall_wall_low", "#2f5fa8", roughness=0.5, tex_scale=2), bevel=0)
    add_obj("wall_trim", box_mesh("wt", (140, 0.8, 0.3)), None, (o[0], o[1] + wy - 0.1, o[2] + 4.25),
            make_material("hall_trim", "#f2c94c", roughness=0.4, texture=False), bevel=0.02)
    add_obj("wall_up", box_mesh("wu", (140, 0.6, 14)), None, (o[0], o[1] + wy, o[2] + 11.2),
            make_material("hall_wall_up", "#efe7d6", roughness=0.7, tex_scale=2), bevel=0)
    add_obj("wall_crown", box_mesh("wc", (140, 1.2, 0.6)), None, (o[0], o[1] + wy - 0.3, o[2] + 15.2),
            make_material("hall_crown", "#d9cfb8", roughness=0.6, texture=False), bevel=0.02)
    ly = wy - 0.95
    _locker_bank(o, -21, 8, ly, ["#2e6fd1", "#2a63bd"], P)
    _door(o, -2.5, wy - 0.2, P)
    _locker_bank(o, 2, 7, ly, ["#c0392b", "#b03426"], P)
    _locker_bank(o, 24, 6, ly, ["#2e6fd1", "#2a63bd"], P)
    _door(o, 21, wy - 0.2, P, color="#7a4b2e")
    # trophy case (glowing shelves)
    P.put(o, "case", box_mesh("tc", (6.0, 1.2, 5.4), (0, 0, -2.7)), (-30, ly, 1.0), P.M("#6e4723", 0.5, scale=5))
    P.put(o, "case_glass", box_mesh("tg", (5.4, 0.2, 4.6)), (-30, ly - 0.62, 3.7), P.glow("#fff1c9", 0.9), bevel=0)
    for k, tx in enumerate((-31.8, -30.6, -29.4, -28.2)):
        P.put(o, "trophy", P.cyl_mesh("tr", 0.28, 1.0 + 0.3 * (k % 2), 10, 0.45), (tx, ly - 0.75, 2.2 + 1.6 * (k % 2)),
              P.M("#e0b13a", 0.2), bevel=0)
    # bulletin board with posters
    P.put(o, "board", box_mesh("bb", (7.0, 0.2, 3.6)), (11.5, wy - 0.45, 9.0), P.M("#b98a55", 0.9, scale=9))
    P.put(o, "board_frame", box_mesh("bf", (7.4, 0.15, 4.0)), (11.5, wy - 0.38, 9.0), P.M("#6e4723", 0.6))
    for k, (px, col, acc) in enumerate(((9.4, "#fff3b0", "#e76f51"), (11.5, "#cde7ff", "#2a9d8f"), (13.6, "#ffd6e0", "#7b2cbf"))):
        P.put(o, "flyer", box_mesh("fl", (1.6, 0.05, 2.2)), (px, wy - 0.58, 9.0 + (0.2 if k % 2 else -0.1)),
              P.M(col, 0.9), (0, 0.06 * (k - 1), 0), bevel=0)
        P.put(o, "flyer_art", box_mesh("fa", (1.1, 0.06, 0.8)), (px, wy - 0.62, 9.4 + (0.2 if k % 2 else -0.1)),
              P.M(acc, 0.8), bevel=0)
    # banner + school name
    P.put(o, "banner", box_mesh("bn", (17, 0.15, 2.0)), (-12, wy - 0.4, 12.6), P.M("#7b2cbf", 0.6, scale=3))
    _wall_text(o, "PLUTONEX HIGH", (-12, wy - 0.55, 12.55), 1.25, "#ffd23f")
    P.put(o, "pennant1", P.prism_mesh("pn", 2.2, 0.08, 1.4), (6.5, wy - 0.4, 13.0), P.M("#2a9d8f", 0.6), (0, 0, 0), bevel=0)
    # clock
    P.put(o, "clock", P.cyl_mesh("ck", 0.9, 0.2, 20), (3.2, wy - 0.4, 12.4), P.M("#ffffff", 0.4), (1.5708, 0, 0), bevel=0.04)
    P.put(o, "clock_rim", P.cyl_mesh("cr", 1.0, 0.15, 20), (3.2, wy - 0.35, 12.4), P.M("#22262b", 0.4), (1.5708, 0, 0), bevel=0)
    # exit sign
    P.put(o, "exit", box_mesh("ex", (2.2, 0.3, 0.9)), (21, wy - 0.6, 10.2), P.glow("#2bd96b", 3.0))
    # water fountain, bins, plants
    P.put(o, "fountain", box_mesh("wf", (1.6, 1.0, 0.7)), (16.2, wy - 0.9, 3.0), P.M("#c9ced6", 0.25))
    P.put(o, "fountain_leg", box_mesh("wfl", (0.4, 0.4, 2.7), (0, 0, -1.35)), (16.2, wy - 0.7, 0), P.M("#9aa3ad", 0.3))
    P.trash_can(o, -23.5, wy - 1.6, color="#2b4f7a")
    P.trash_can(o, 18.6, wy - 1.6, color="#2f6b3f")
    for px in (-34.5, 34.5, -25.3):
        P.put(o, "pot", P.cyl_mesh("pt", 0.8, 1.4, 12, 1.0), (px, wy - 1.8, 0), P.M("#b5543a", 0.6), bevel=0.03)
        P.bush(o, px, wy - 1.8, s=1.0, seed=int(abs(px)))
    # stuff on the floor
    P.put(o, "backpack", box_mesh("bp", (1.2, 0.8, 1.4), (0, 0, -0.7)), (12.6, wy - 2.3, 0), P.M("#e76f51", 0.7), bevel=0.2)
    P.put(o, "books", box_mesh("bk", (1.2, 0.9, 0.35), (0, 0, -0.17)), (-15.6, wy - 2.2, 0), P.M("#3a86ff", 0.6), (0, 0, 0.3))
    # foreground pillars (out of focus, give depth like a real camera)
    for px in (-17, 17):
        P.put(o, "pillar", box_mesh("pl", (1.8, 1.8, 16), (0, 0, -8)), (px, -9, 0), P.M("#e2d9c4", 0.6, scale=2))
        P.put(o, "pillar_base", box_mesh("pb", (2.2, 2.2, 0.8), (0, 0, -0.4)), (px, -9, 0), P.M("#2f5fa8", 0.5))
    P.put(o, "wet_sign", P.prism_mesh("ws", 1.3, 1.0, 1.9), (-11.5, -6.5, 0), P.M("#ffd23f", 0.5), (0, 0, 1.5708), bevel=0)
    return dict(DEFAULT_MARKS)


def bedroom(o):
    _room(o, floor="#7a5233", wall="#b9d7f0", depth=12)
    block(o, "bed", (5, 8, 1.6), (-9, 5, 0.8), "#d64545")
    block(o, "pillow", (4, 1.5, 0.6), (-9, 8, 1.9), "#ffffff")
    block(o, "headboard", (5.4, 0.4, 4), (-9, 9.2, 2), "#5a3a1e")
    block(o, "desk_pc", (5, 2.5, 2.8), (9, 8, 1.4), "#ffffff")
    block(o, "monitor", (3, 0.3, 2), (9, 8.5, 4), "#111111")
    block(o, "screen", (2.6, 0.05, 1.6), (9, 8.32, 4), "#4fc3f7", bevel=0)
    block(o, "rug", (8, 6, 0.05), (0, 2, 0.03), "#6a4c93", bevel=0)
    block(o, "window", (5, 0.2, 4), (0, 9.7, 8), "#9fd3ff", bevel=0)
    return dict(DEFAULT_MARKS)


def kitchen(o):
    _room(o, floor="#f0f0f0", wall="#ffe8b5", depth=12)
    block(o, "counter", (14, 2.5, 3), (0, 8.5, 1.5), "#6d4c41")
    block(o, "countertop", (14.2, 2.7, 0.3), (0, 8.5, 3.1), "#eeeeee")
    block(o, "fridge", (3, 2.5, 7), (10, 8.5, 3.5), "#cfd8dc")
    block(o, "table", (6, 4, 0.3), (-6, 1, 2.7), "#a1887f")
    for dx in (-2.6, 2.6):
        block(o, "table_leg", (0.3, 0.3, 2.6), (-6 + dx, 1, 1.3), "#5d4037", bevel=0)
    return dict(DEFAULT_MARKS)


def outdoors(o):
    block(o, "baseplate", (200, 200, 0.4), (0, 30, -0.2), "#4b974b", bevel=0)
    rnd = random.Random(7)
    for i in range(14):
        x = rnd.uniform(-40, 40)
        y = rnd.uniform(10, 60)
        if abs(x) < 8 and y < 18:
            continue
        block(o, f"trunk{i}", (1, 1, 4), (x, y, 2), "#6b4226")
        block(o, f"leaves{i}", (4, 4, 4), (x, y, 5.5), "#2f7d32", bevel=0.3)
    block(o, "path", (5, 80, 0.06), (0, 20, 0.03), "#c2b280", bevel=0)
    block(o, "house", (12, 10, 8), (16, 22, 4), "#e57373")
    block(o, "roof", (13, 11, 1.5), (16, 22, 8.75), "#5d4037")
    return dict(DEFAULT_MARKS)


def stage(o):
    """Plain coloured studio - good for memes / reaction shots."""
    block(o, "floor", (60, 60, 0.4), (0, 10, -0.2), "#3d3d6b", bevel=0)
    block(o, "backdrop", (60, 0.5, 30), (0, 10, 15), "#5a5aa0", bevel=0)
    return dict(DEFAULT_MARKS)


def playground(o):
    """Detailed park / playground at the edge of a neighbourhood."""
    import props as P
    grass = make_material("pg_grass", "#4f8f3f", roughness=0.95, tex_scale=1.2, bump=0.3)
    add_obj("ground", box_mesh("ground", (260, 260, 0.4)), None, (o[0], o[1] + 60, o[2] - 0.2), grass, bevel=0)
    path = make_material("pg_path", "#c9b48a", roughness=0.95, tex_scale=3, bump=0.25)
    add_obj("path", box_mesh("path", (6, 120, 0.06)), None, (o[0], o[1] + 30, o[2] + 0.03), path, bevel=0)
    add_obj("path2", box_mesh("path2", (90, 5, 0.06)), None, (o[0], o[1] + 2, o[2] + 0.025), path, bevel=0)
    sand = make_material("pg_sand", "#e0c68f", roughness=1.0, tex_scale=6, bump=0.4)
    add_obj("sandpit", box_mesh("sandpit", (14, 9, 0.12)), None, (o[0] - 13, o[1] + 12, o[2] + 0.05), sand, bevel=0.05)
    P.swings(o, -13, 12)
    P.slide(o, 13, 13)
    for x in (-30, -18, 18, 30):
        P.lamp_post(o, x, 5)
    P.bench(o, -22, 7, rot=0.15)
    P.bench(o, 23, 7.5, rot=-0.15)
    P.trash_can(o, -25.5, 6.5)
    P.trash_can(o, 26.5, 6.5, color="#2b4f7a")
    P.sign_post(o, 7, 9, color="#2e86c1")
    P.fence(o, -44, -4, 24)
    P.fence(o, 4, 44, 24)
    for i, x in enumerate((-36, -22, 22, 36)):
        P.house(o, x, 42 + (i % 2) * 4, wall=["#e9d8c4", "#cfe0e8", "#f2d0c0", "#e6e1b8"][i],
                roof=["#7b3b2c", "#3d4f6b", "#6b3b5a", "#4f6b3b"][i], seed=i)
    P.house(o, 0, 58, w=14, wall="#d8c9e8", roof="#5b3b7b", seed=9)
    P.scatter(o, P.tree, 16, (-60, 60), (20, 80), seed=3, keep_out=(-9, 9, 0, 70))
    P.scatter(o, P.bush, 14, (-45, 45), (14, 26), seed=4, keep_out=(-8, 8, 0, 40))
    P.scatter(o, P.rock, 8, (-40, 40), (6, 22), seed=5, keep_out=(-9, 9, -5, 30))
    # foreground framing pieces (they blur nicely with depth of field)
    P.bush(o, -16, -6, s=1.3, seed=11)
    P.bush(o, 17, -7, s=1.2, seed=12)
    P.tree(o, -24, -10, s=1.1, seed=13)
    P.tree(o, 25, -12, s=1.2, seed=14)
    P.barrel(o, 19, -3, color="#2e6b8a")
    P.crate(o, -19, -2.5, rot=0.4)
    P.cone(o, 9, -4)
    return dict(DEFAULT_MARKS)


# ------------------------------------------------------- bright story sets
def _window(o, P, x, y, z, w=5.0, h=4.2, curtain="#ff8fab", rot=False):
    size = (0.25, w, h) if rot else (w, 0.25, h)
    P.put(o, "win_glass", box_mesh("wg", size), (x, y, z), P.glow("#e6f5ff", 1.6), bevel=0)
    fs = (0.35, w + 0.5, 0.3) if rot else (w + 0.5, 0.35, 0.3)
    for dz in (-h / 2, h / 2):
        P.put(o, "win_frame", box_mesh("wf", fs), (x, y, z + dz), P.M("#ffffff", 0.4, tex=False), bevel=0.05)
    if curtain:
        for side in (-1, 1):
            cs = (0.4, 1.3, h + 1.2) if rot else (1.3, 0.4, h + 1.2)
            cx, cy = (x, y + side * (w / 2 + 0.5)) if rot else (x + side * (w / 2 + 0.5), y - 0.25)
            if rot:
                cx += 0.25 if x < 0 else -0.25
            P.put(o, "curtain", box_mesh("ct", cs), (cx, cy, z - 0.3), P.M(curtain, 0.9, scale=8), bevel=0.15)


def _frame_pic(o, P, x, y, z, w, h, color):
    P.put(o, "pic_frame", box_mesh("pf", (w + 0.3, 0.15, h + 0.3)), (x, y, z), P.M("#3b2a1e", 0.4), bevel=0.04)
    P.put(o, "pic", box_mesh("pc", (w, 0.17, h)), (x, y - 0.02, z), P.M(color, 0.6, tex=False), bevel=0)


def living_room_window(o):
    """Living room whose window is a real opening onto the front yard (someone can stand outside it)."""
    return living_room(o, hole=True)


def living_room(o, hole=False):
    """Bright family living room: sofa, rug, side table (vase spot), TV, window with curtains, plants, photos."""
    import props as P
    wall, wy = "#fff1dc", 9.6
    block(o, "floor", (60, 40, 0.4), (0, 6, -0.2), "#e2b47c", bevel=0)
    for i in range(-14, 15, 2):  # plank lines
        block(o, "plank", (0.06, 40, 0.02), (i * 1.0, 6, 0.01), "#c99a62", bevel=0)
    if hole:  # window opening x -12.25..-6.75, z 3.4..7.6, with the yard behind it
        wx, ww, z0, z1 = -9.5, 5.5, 3.4, 7.6
        l, r = wx - ww / 2, wx + ww / 2
        block(o, "wall_bl", (l + 30, 0.6, 16), ((l - 30) / 2, wy + 0.3, 8), wall, bevel=0)
        block(o, "wall_br", (30 - r, 0.6, 16), ((r + 30) / 2, wy + 0.3, 8), wall, bevel=0)
        block(o, "wall_top", (ww, 0.6, 16 - z1), (wx, wy + 0.3, (z1 + 16) / 2), wall, bevel=0)
        block(o, "wall_bot", (ww, 0.6, z0), (wx, wy + 0.3, z0 / 2), wall, bevel=0)
        for dz in (z0, z1):
            block(o, "win_sill", (ww + 0.6, 1.0, 0.3), (wx, wy + 0.3, dz), "#ffffff", bevel=0.05)
        for dx in (l, r):
            block(o, "win_side", (0.3, 1.0, z1 - z0), (dx, wy + 0.3, (z0 + z1) / 2), "#ffffff", bevel=0.05)
        for side in (-1, 1):
            P.put(o, "curtain", box_mesh("ct", (1.3, 0.4, z1 - z0 + 1.6)), (wx + side * (ww / 2 + 0.5), wy - 0.25, (z0 + z1) / 2 + 0.3),
                  P.M("#ff8fab", 0.9, scale=8), bevel=0.15)
        block(o, "yard", (60, 40, 0.4), (0, wy + 20.6, -0.2), "#6cc04a", bevel=0)
        block(o, "path_out", (4, 40, 0.06), (wx, wy + 20.6, 0.03), "#d8c7a3", bevel=0)
        for i, x in enumerate(range(-24, 25, 3)):
            block(o, f"fence{i}", (0.5, 0.4, 3.0), (x, wy + 9, 1.5), "#ffffff", bevel=0.08)
        block(o, "fence_rail", (50, 0.3, 0.4), (0, wy + 9, 2.2), "#ffffff", bevel=0)
        for x, y in ((-15, wy + 6), (-4, wy + 5), (-20, wy + 12)):
            block(o, "bush", (3.2, 3.2, 2.6), (x, y, 1.3), "#3f9d3a", bevel=0.6)
        block(o, "tree_t", (1.0, 1.0, 7), (-1, wy + 14, 3.5), "#7a5233")
        block(o, "tree_l", (6, 6, 5), (-1, wy + 14, 8.5), "#4caf50", bevel=0.8)
        P.put(o, "sky", box_mesh("sky", (120, 0.2, 60)), (0, wy + 30, 20), P.glow("#bfe6ff", 1.4), bevel=0)
    else:
        block(o, "wall_back", (60, 0.6, 16), (0, wy + 0.3, 8), wall, bevel=0)
    block(o, "wainscot", (60, 0.7, 3.2), (0, wy, 1.6), "#ffffff", bevel=0)
    block(o, "rail", (60, 0.8, 0.25), (0, wy, 3.25), "#e8d3b0", bevel=0)
    block(o, "wall_l", (0.6, 30, 16), (-18, 0, 8), wall, bevel=0)
    block(o, "wall_r", (0.6, 30, 16), (18, 0, 8), wall, bevel=0)
    block(o, "rug", (13, 7, 0.06), (0, 2.5, 0.04), "#b39ddb", bevel=0)
    block(o, "rug_border", (13.6, 7.6, 0.04), (0, 2.5, 0.02), "#ffffff", bevel=0)
    # sofa
    block(o, "sofa_base", (9, 3.2, 1.7), (0, 7.4, 0.85), "#26a69a", bevel=0.2)
    block(o, "sofa_back", (9, 1.0, 2.8), (0, 8.7, 2.3), "#26a69a", bevel=0.25)
    for x in (-4.9, 4.9):
        block(o, "sofa_arm", (1.0, 3.4, 2.4), (x, 7.4, 1.4), "#1f8f84", bevel=0.25)
    for i, (x, c) in enumerate([(-2.7, "#ffd166"), (0, "#ff8fab"), (2.7, "#ffd166")]):
        block(o, f"cushion{i}", (2.2, 0.7, 1.7), (x, 8.0, 2.7), c, bevel=0.3)
    # coffee table + mug + books
    block(o, "ctable", (4.5, 2.2, 0.3), (2.5, 4.4, 1.3), "#8d6e63", bevel=0.08)
    for dx in (-1.9, 1.9):
        block(o, "ctleg", (0.3, 1.8, 1.15), (2.5 + dx, 4.4, 0.6), "#6d4c41", bevel=0.04)
    block(o, "book1", (1.4, 1.0, 0.25), (1.6, 4.4, 1.6), "#ef5350", bevel=0.03)
    block(o, "book2", (1.2, 0.9, 0.22), (1.6, 4.4, 1.85), "#42a5f5", bevel=0.03)
    block(o, "mug", (0.45, 0.45, 0.55), (3.6, 4.2, 1.72), "#ffffff", bevel=0.1)
    # side table for the vase (left of centre)
    if hole:
        pass
    else:
      block(o, "stable_top", (2.2, 2.2, 0.25), (-4.8, 1.8, 2.5), "#ffffff", bevel=0.06)
      block(o, "stable_leg", (0.5, 0.5, 2.4), (-4.8, 1.8, 1.2), "#d7ccc8", bevel=0.05)
      block(o, "stable_foot", (1.4, 1.4, 0.15), (-4.8, 1.8, 0.08), "#d7ccc8", bevel=0.04)
    # TV unit
    block(o, "tv_unit", (7, 1.8, 1.8), (11.5, 8.5, 0.9), "#f5f5f5", bevel=0.08)
    block(o, "tv", (6, 0.3, 3.4), (11.5, 9.0, 3.8), "#151515", bevel=0.06)
    P.put(o, "tv_screen", box_mesh("ts", (5.6, 0.1, 3.0)), (11.5, 8.83, 3.8), P.glow("#7cc7ff", 0.9), bevel=0)
    if not hole:
        _window(o, P, -9.5, wy - 0.05, 7.6, w=5.5, h=4.5, curtain="#ff8fab")
    for x, z, w, h, c in [(-1.5, 11.2, 2.2, 1.6, "#81d4fa"), (1.2, 11.6, 1.6, 2.2, "#ffcc80"), (3.8, 11.0, 2.4, 1.6, "#c5e1a5")]:
        _frame_pic(o, P, x, wy - 0.05, z, w, h, c)
    for x in (-15, 15.5):
        P.put(o, "pot", P.cyl_mesh("pot", 0.8, 1.4, 14, 1.0), (x, 7.5, 0), P.M("#ffffff", 0.4, tex=False), bevel=0)
        P.put(o, "plant", box_mesh("pl", (2.2, 2.2, 3.0)), (x, 7.5, 2.9), P.M("#43a047"), bevel=0.5)
    lx = -15.5 if hole else -13
    block(o, "lamp_pole", (0.2, 0.2, 6), (lx, 6, 3), "#cfcfcf", bevel=0)
    block(o, "lamp_shade", (1.6, 1.6, 1.2), (lx, 6, 6.4), "#fff8e1", bevel=0.2)
    block(o, "clock", (1.6, 0.2, 1.6), (7.5, wy - 0.05, 12), "#ffffff", bevel=0.3)
    return dict(DEFAULT_MARKS, vase_top=(-4.8, 1.8, 2.63))


def dining_room(o):
    """Bright kitchen-diner: cabinets, fridge, window over the sink, long table with seats facing camera."""
    import props as P
    wy = 10.0
    floor = _checker_material("dine_floor", "#ffffff", "#dfe6ea", scale=0.3, rough=0.3)
    add_obj("floor", box_mesh("df", (60, 40, 0.4)), None, (o[0], o[1] + 6, o[2] - 0.2), floor, bevel=0)
    block(o, "wall_back", (60, 0.6, 16), (0, wy + 0.3, 8), "#d6f2e6", bevel=0)
    block(o, "wall_l", (0.6, 30, 16), (-18, 0, 8), "#d6f2e6", bevel=0)
    block(o, "wall_r", (0.6, 30, 16), (18, 0, 8), "#d6f2e6", bevel=0)
    for i in range(6):  # lower cabinets + counter
        x = -11 + i * 3.2
        block(o, f"cab{i}", (3.1, 2.2, 3.0), (x, wy - 1.3, 1.5), "#ffffff", bevel=0.06)
        block(o, f"cabh{i}", (0.8, 0.12, 0.18), (x, wy - 2.45, 2.5), "#b0bec5", bevel=0.03)
        if i not in (2, 3):
            block(o, f"ucab{i}", (3.1, 1.4, 2.6), (x, wy - 0.4, 10.2), "#ffffff", bevel=0.06)
    block(o, "counter", (19.5, 2.5, 0.3), (-3, wy - 1.3, 3.15), "#90a4ae", bevel=0.04)
    block(o, "backsplash", (19.5, 0.2, 3.0), (-3, wy - 0.15, 4.8), "#ffe082", bevel=0)
    block(o, "sink", (2.4, 1.6, 0.2), (-2.6, wy - 1.3, 3.31), "#cfd8dc", bevel=0.05)
    block(o, "tap", (0.25, 0.25, 1.2), (-2.6, wy - 0.4, 3.9), "#b0bec5", bevel=0.05)
    _window(o, P, -2.6, wy - 0.05, 8.2, w=5.0, h=3.4, curtain="#ffd166")
    block(o, "fridge", (3.4, 2.6, 8.0), (12, wy - 1.4, 4.0), "#eceff1", bevel=0.12)
    block(o, "fridge_line", (3.42, 0.05, 0.08), (12, wy - 2.72, 5.4), "#b0bec5", bevel=0)
    for z in (3.4, 7.0):
        block(o, "fridge_h", (0.15, 0.2, 1.2), (10.6, wy - 2.8, z), "#90a4ae", bevel=0.04)
    for i, c in enumerate(["#ef5350", "#42a5f5", "#ffca28"]):  # fridge magnets / drawing
        block(o, f"mag{i}", (0.6, 0.06, 0.6), (11.4 + i * 0.6, wy - 2.75, 6.4 - i * 0.3), c, bevel=0.02)
    # long dining table between camera and the seats
    block(o, "table_top", (11, 3.6, 0.3), (0, 2.0, 1.95), "#a1887f", bevel=0.08)
    block(o, "table_cloth", (11.2, 1.4, 0.06), (0, 2.0, 2.13), "#ffffff", bevel=0)
    for dx in (-5, 5):
        for dy in (-1.4, 1.4):
            block(o, "table_leg", (0.35, 0.35, 1.8), (dx, 2.0 + dy, 0.9), "#6d4c41", bevel=0.04)
    for x in (-3.4, 0.2, 3.8):  # chairs behind the seats
        block(o, "chair_seat", (2.0, 2.0, 0.25), (x, 4.3, 1.0), "#ffb74d", bevel=0.06)
        block(o, "chair_back", (2.0, 0.25, 2.6), (x, 5.25, 2.3), "#ffb74d", bevel=0.06)
        for dx in (-0.8, 0.8):
            block(o, "chair_leg", (0.2, 0.2, 1.0), (x + dx, 4.3, 0.5), "#8d6e63", bevel=0)
    for x in (-3, 3):  # pendant lamps
        block(o, "pend_cord", (0.06, 0.06, 4), (x, 2.0, 14), "#333333", bevel=0)
        P.put(o, "pend_shade", P.cyl_mesh("ps", 1.0, 0.9, 14, 0.4), (x, 2.0, 11.4), P.M("#263238", 0.4, tex=False), bevel=0)
        P.put(o, "pend_bulb", box_mesh("pb", (0.5, 0.5, 0.4)), (x, 2.0, 11.3), P.glow("#fff3c4", 4), bevel=0.1)
    return dict(DEFAULT_MARKS, seat_l=(-3.4, 3.9, 0), seat_c=(0.2, 3.9, 0), seat_r=(3.8, 3.9, 0),
                head=(7.2, 3.2, 0), table=(0, 2.0, 2.16))


def classroom_bright(o):
    """Bright classroom: pastel walls, whiteboard, two rows of desks with chairs, teacher's desk, posters."""
    import props as P
    wy = 11.8
    floor = _checker_material("class_floor", "#f4efe4", "#e2dccd", scale=0.22, rough=0.35)
    add_obj("floor", box_mesh("cf", (60, 40, 0.4)), None, (o[0], o[1] + 6, o[2] - 0.2), floor, bevel=0)
    block(o, "wall_back", (60, 0.6, 16), (0, wy + 0.3, 8), "#fdf6e3", bevel=0)
    block(o, "wall_low", (60, 0.7, 3.4), (0, wy, 1.7), "#8fd3c1", bevel=0)
    block(o, "wall_l", (0.6, 34, 16), (-18, 2, 8), "#fdf6e3", bevel=0)
    block(o, "wall_r", (0.6, 34, 16), (18, 2, 8), "#fdf6e3", bevel=0)
    block(o, "board_frame", (15, 0.2, 5.8), (-1, wy - 0.1, 7.8), "#b0bec5", bevel=0.05)
    block(o, "board", (14.4, 0.25, 5.2), (-1, wy - 0.15, 7.8), "#ffffff", bevel=0)
    _wall_text(o, "SPELLING TEST FRIDAY!", (-1, wy - 0.32, 8.9), 0.75, "#1e5bd8", extrude=0.02)
    _wall_text(o, "2 + 2 = ?", (-1, wy - 0.32, 7.3), 1.0, "#e53935", extrude=0.02)
    block(o, "tray", (14, 0.6, 0.15), (-1, wy - 0.45, 5.15), "#90a4ae", bevel=0.02)
    for i, (x, c) in enumerate([(-13.5, "#ffd166"), (11.5, "#ff8fab"), (14.5, "#81d4fa")]):
        _frame_pic(o, P, x, wy - 0.05, 8.5 - (i % 2) * 1.2, 2.4, 3.0, c)
    block(o, "clock", (1.6, 0.2, 1.6), (9, wy - 0.05, 12.2), "#ffffff", bevel=0.3)
    _window(o, P, -17.6, 1, 8.0, w=6, h=4.6, curtain=None, rot=True)
    _window(o, P, 17.6, 1, 8.0, w=6, h=4.6, curtain=None, rot=True)
    for x in (-8, -3, 3, 8):
        for y in (0.4, 4.6):
            block(o, "desk_top", (3.4, 2.0, 0.22), (x, y, 1.85), "#ffcc80", bevel=0.04)
            block(o, "desk_box", (3.2, 1.8, 0.45), (x, y, 1.55), "#90a4ae", bevel=0.03)
            for dx in (-1.4, 1.4):
                block(o, "desk_leg", (0.18, 0.18, 1.35), (x + dx, y, 0.67), "#546e7a", bevel=0)
            block(o, "chair_seat", (1.8, 1.6, 0.2), (x, y + 2.2, 1.0), "#4fc3f7", bevel=0.04)
            block(o, "chair_back", (1.8, 0.2, 2.0), (x, y + 3.0, 2.0), "#4fc3f7", bevel=0.04)
            block(o, "chair_leg", (0.15, 0.15, 1.0), (x, y + 2.2, 0.5), "#546e7a", bevel=0)
    block(o, "teacher_desk", (6, 2.6, 2.6), (8.5, 9.0, 1.3), "#8d6e63", bevel=0.06)
    block(o, "apple", (0.5, 0.5, 0.5), (10.6, 8.6, 2.85), "#e53935", bevel=0.2)
    block(o, "shelf", (5, 1.6, 4), (-13, wy - 1.0, 2), "#a1887f", bevel=0.05)
    for i in range(8):
        block(o, f"sbook{i}", (0.45, 1.0, 1.4), (-15 + i * 0.55, wy - 1.1, 4.7), ["#ef5350", "#42a5f5", "#66bb6a", "#ffca28"][i % 4], bevel=0.02)
    return dict(DEFAULT_MARKS, teacher=(7.0, 10.5, 0), board=(0, 9, 0), desk_fl=(-8, 1.6, 0), desk_fcl=(-3, 1.6, 0),
                desk_fcr=(3, 1.6, 0), desk_fr=(8, 1.6, 0), teacher_desk=(8.5, 9.0, 2.6))


BUILDERS = {f.__name__: f for f in [living_room_window, classroom, hallway, bedroom, kitchen, outdoors, stage, playground,
                                     living_room, dining_room, classroom_bright]}


def build_set(name, origin, assets_dir):
    for ext in ("fbx", "obj", "glb"):
        path = os.path.join(assets_dir, "sets", f"{name}.{ext}")
        if os.path.exists(path):
            before = set(bpy.data.objects)
            if ext == "fbx":
                bpy.ops.import_scene.fbx(filepath=path)
            elif ext == "obj":
                bpy.ops.wm.obj_import(filepath=path)
            else:
                bpy.ops.import_scene.gltf(filepath=path)
            for ob in set(bpy.data.objects) - before:
                if ob.parent is None:
                    ob.location = (ob.location[0] + origin[0], ob.location[1] + origin[1], ob.location[2] + origin[2])
            return dict(DEFAULT_MARKS)
    if name not in BUILDERS:
        raise ValueError(f"unknown set '{name}'. Built-in sets: {sorted(BUILDERS)}")
    return BUILDERS[name](origin)
