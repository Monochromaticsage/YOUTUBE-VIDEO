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


def hallway(o):
    _room(o, floor="#9aa3ad", wall="#d8dde3", depth=10)
    for i, x in enumerate(range(-15, 16, 2)):
        block(o, f"locker{i}", (1.9, 1.2, 6), (x, 6.9, 3), "#2e6fd1" if i % 2 else "#2a63bd")
        block(o, f"locker_vent{i}", (1.2, 0.1, 0.5), (x, 6.25, 5.2), "#1d4a8f", bevel=0)
    block(o, "trophy", (4, 1, 3), (-11, 7.2, 8), "#c9a227")
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


BUILDERS = {f.__name__: f for f in [classroom, hallway, bedroom, kitchen, outdoors, stage, playground]}


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
