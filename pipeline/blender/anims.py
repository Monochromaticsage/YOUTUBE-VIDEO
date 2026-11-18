"""Animation library. Each animation keys a character between frames f0..f1.

Rules that keep cuts clean:
  * every animation keys a full pose at f0 and at f1 - 1
  * angles are degrees; joints not given default to 0 (neutral)

Joint conventions (character faces -Y, toward the camera):
  arm rotation X < 0  -> arm swings forward (toward camera)
  arm_r rotation Y > 0 / arm_l rotation Y < 0 -> arm raises out to the side
  head rotation X < 0 -> look down,  Z -> turn head
Add new moves by writing a function and registering it in ANIMS.
"""
import math

JOINTS = ("torso", "head", "arm_l", "arm_r", "leg_l", "leg_r")


def _rad(v):
    return tuple(math.radians(a) for a in v)


def pose(rig, frame, offset=(0, 0, 0), yaw=0.0, tilt=(0, 0), **joints):
    """Key a full pose. offset = root location offset from the mark."""
    bx, by, bz = rig.base
    rig.root.location = (bx + offset[0], by + offset[1], bz + offset[2])
    rig.root.rotation_euler = (math.radians(tilt[0]), math.radians(tilt[1]), math.radians(rig.base_yaw + yaw))
    rig.root.keyframe_insert("location", frame=frame)
    rig.root.keyframe_insert("rotation_euler", frame=frame)
    for j in JOINTS:
        ob = rig.parts[j]
        ob.rotation_euler = _rad(joints.get(j, (0, 0, 0)))
        ob.keyframe_insert("rotation_euler", frame=frame)


def _loop(f0, f1, step):
    f = f0
    i = 0
    while f < f1 - 1:
        yield i, f
        f += step
        i += 1


# ---------------------------------------------------------------- the moves
def idle(rig, f0, f1, fps):
    for i, f in _loop(f0, f1, fps):
        s = 1 if i % 2 else -1
        pose(rig, f, arm_l=(0, -4 + s, 0), arm_r=(0, 4 - s, 0), head=(s * 2, 0, 0), torso=(s * 0.6, 0, 0))
    pose(rig, f1 - 1, arm_l=(0, -4, 0), arm_r=(0, 4, 0))


def talk(rig, f0, f1, fps):
    step = max(6, fps // 3)
    for i, f in _loop(f0, f1, step):
        g = [(-25, 8, 0), (-10, 18, 0), (-35, 5, 0), (-5, 10, 0)][i % 4]
        pose(rig, f, head=(4 if i % 2 else -3, 0, 6 if i % 3 == 0 else -4, ),
             arm_r=(g[0], g[1], 0), arm_l=(0, -5, 0), torso=(2 if i % 2 else 0, 0, 0))
    pose(rig, f1 - 1, arm_l=(0, -4, 0), arm_r=(0, 4, 0))


def shocked(rig, f0, f1, fps):
    up = dict(arm_l=(0, -150, 0), arm_r=(0, 150, 0), head=(8, 0, 0), leg_l=(0, -10, 0), leg_r=(0, 10, 0))
    pose(rig, f0)
    pose(rig, min(f0 + 4, f1 - 1), offset=(0, 0, 1.1), **up)
    pose(rig, min(f0 + 9, f1 - 1), offset=(0, 0, 0), **up)
    for i, f in _loop(f0 + 12, f1, 4):  # tremble
        pose(rig, f, offset=(0.05 if i % 2 else -0.05, 0, 0), **up)
    pose(rig, f1 - 1, **up)


def scared(rig, f0, f1, fps):
    cower = dict(arm_l=(-70, -30, 0), arm_r=(-70, 30, 0), head=(-12, 0, 0), torso=(-8, 0, 0))
    pose(rig, f0)
    for i, f in _loop(f0 + 3, f1, 3):
        pose(rig, f, offset=(0.07 if i % 2 else -0.07, 0.3, -0.1), **cower)
    pose(rig, f1 - 1, offset=(0, 0.3, -0.1), **cower)


def angry(rig, f0, f1, fps):
    fists = dict(arm_l=(-20, -25, 0), arm_r=(-20, 25, 0))
    for i, f in _loop(f0, f1, 5):
        stomp = (i % 4 == 0)
        pose(rig, f, offset=(0, 0, 0.25 if stomp else 0), head=(-6, 0, 5 if i % 2 else -5),
             leg_l=(-20 if stomp else 0, 0, 0), torso=(-5, 0, 0), **fists)
    pose(rig, f1 - 1, head=(-6, 0, 0), torso=(-5, 0, 0), **fists)


def laugh(rig, f0, f1, fps):
    for i, f in _loop(f0, f1, 4):
        back = 12 if i % 2 else 4
        pose(rig, f, torso=(back, 0, 0), head=(back, 0, 0), arm_l=(-50, -10, 20), arm_r=(-50, 10, -20),
             offset=(0, 0, 0.12 if i % 2 else 0))
    pose(rig, f1 - 1, torso=(6, 0, 0), arm_l=(-50, -10, 20), arm_r=(-50, 10, -20))


def sad(rig, f0, f1, fps):
    slump = dict(head=(-22, 0, 0), torso=(-8, 0, 0), arm_l=(5, -2, 0), arm_r=(5, 2, 0))
    pose(rig, f0)
    pose(rig, min(f0 + 10, f1 - 1), **slump)
    pose(rig, f1 - 1, **slump)


def cry(rig, f0, f1, fps):
    hands = dict(arm_l=(-140, 20, 0), arm_r=(-140, -20, 0), head=(-18, 0, 0))
    pose(rig, f0)
    for i, f in _loop(f0 + 5, f1, 6):
        pose(rig, f, torso=(-6 if i % 2 else -2, 0, 0), offset=(0, 0, 0.05 if i % 2 else 0), **hands)
    pose(rig, f1 - 1, torso=(-4, 0, 0), **hands)


def wave(rig, f0, f1, fps):
    for i, f in _loop(f0, f1, 5):
        pose(rig, f, arm_r=(0, 155 if i % 2 else 125, 0), head=(0, 0, 4 if i % 2 else -4))
    pose(rig, f1 - 1, arm_r=(0, 140, 0))


def point(rig, f0, f1, fps):
    pt = dict(arm_r=(-90, 0, 0), head=(0, 0, -6))
    pose(rig, f0)
    pose(rig, min(f0 + 5, f1 - 1), **pt)
    pose(rig, f1 - 1, **pt)


def facepalm(rig, f0, f1, fps):
    fp = dict(arm_r=(-150, -25, 0), head=(-20, 0, 0))
    pose(rig, f0)
    pose(rig, min(f0 + 6, f1 - 1), **fp)
    for i, f in _loop(f0 + 10, f1, 10):
        pose(rig, f, head=(-20, 0, 6 if i % 2 else -6), arm_r=(-150, -25, 0))
    pose(rig, f1 - 1, **fp)


def think(rig, f0, f1, fps):
    th = dict(arm_r=(-120, -35, 0), arm_l=(-40, 25, 0), head=(6, 0, 12))
    pose(rig, f0)
    pose(rig, min(f0 + 6, f1 - 1), **th)
    pose(rig, f1 - 1, **th)


def dance(rig, f0, f1, fps):
    for i, f in _loop(f0, f1, 6):
        s = 1 if i % 2 else -1
        pose(rig, f, offset=(0.3 * s, 0, 0.2 if i % 2 else 0), yaw=12 * s,
             arm_l=(0, -130 if s > 0 else -40, 0), arm_r=(0, 40 if s > 0 else 130, 0),
             leg_l=(0, -15 * s, 0), leg_r=(0, -15 * s, 0), head=(0, 10 * s, 0))
    pose(rig, f1 - 1)


def jump(rig, f0, f1, fps):
    pose(rig, f0)
    for i, f in _loop(f0 + 2, f1, 14):
        pose(rig, f, arm_l=(0, -20, 0), arm_r=(0, 20, 0))
        pose(rig, min(f + 7, f1 - 1), offset=(0, 0, 2), arm_l=(0, -160, 0), arm_r=(0, 160, 0),
             leg_l=(-25, 0, 0), leg_r=(25, 0, 0))
    pose(rig, f1 - 1)


def fall(rig, f0, f1, fps):
    pose(rig, f0)
    pose(rig, min(f0 + 6, f1 - 1), tilt=(25, 0), arm_l=(0, -120, 0), arm_r=(0, 120, 0))
    pose(rig, min(f0 + 12, f1 - 1), tilt=(88, 0), offset=(0, 1.6, 0.5), arm_l=(0, -90, 0), arm_r=(0, 90, 0))
    pose(rig, f1 - 1, tilt=(90, 0), offset=(0, 1.8, 0.5), arm_l=(0, -90, 0), arm_r=(0, 90, 0))


def lie(rig, f0, f1, fps):
    flat = dict(tilt=(90, 0), offset=(0, 1.8, 0.5), arm_l=(0, -90, 0), arm_r=(0, 90, 0))
    pose(rig, f0, **flat)
    pose(rig, f1 - 1, **flat)


def sit(rig, f0, f1, fps):
    s = dict(offset=(0, 0.4, -0.95), leg_l=(-90, 0, 0), leg_r=(-90, 0, 0), arm_l=(-40, 0, 0), arm_r=(-40, 0, 0))
    pose(rig, f0, **s)
    for i, f in _loop(f0 + fps, f1, fps):
        pose(rig, f, head=(3 if i % 2 else -2, 0, 0), **s)
    pose(rig, f1 - 1, **s)


def run_in_place(rig, f0, f1, fps):
    for i, f in _loop(f0, f1, 4):
        s = 1 if i % 2 else -1
        pose(rig, f, leg_l=(45 * s, 0, 0), leg_r=(-45 * s, 0, 0), arm_l=(-50 * s, 0, 0), arm_r=(50 * s, 0, 0),
             torso=(-10, 0, 0), offset=(0, 0, 0.15 if i % 2 else 0))
    pose(rig, f1 - 1, torso=(-10, 0, 0))


def _walk(rig, f0, f1, fps, start, end, speed_frames=6, run=False):
    """Walk from offset `start` to offset `end` (relative to the mark)."""
    amp = 50 if run else 32
    n = max(1, (f1 - 1 - f0))
    for i, f in _loop(f0, f1, speed_frames):
        t = (f - f0) / n
        off = tuple(a + (b - a) * t for a, b in zip(start, end))
        s = 1 if i % 2 else -1
        pose(rig, f, offset=(off[0], off[1], 0.12 if (i % 2 and run) else 0),
             yaw=-90 if end[0] > start[0] else (90 if end[0] < start[0] else 0),
             leg_l=(amp * s, 0, 0), leg_r=(-amp * s, 0, 0), arm_l=(-amp * s, 0, 0), arm_r=(amp * s, 0, 0),
             torso=(-8 if run else 0, 0, 0))
    pose(rig, f1 - 1, offset=end)


def walk_in_left(rig, f0, f1, fps):
    _walk(rig, f0, f1, fps, (-14, 0, 0), (0, 0, 0))


def walk_in_right(rig, f0, f1, fps):
    _walk(rig, f0, f1, fps, (14, 0, 0), (0, 0, 0))


def walk_out_left(rig, f0, f1, fps):
    _walk(rig, f0, f1, fps, (0, 0, 0), (-16, 0, 0))


def walk_out_right(rig, f0, f1, fps):
    _walk(rig, f0, f1, fps, (0, 0, 0), (16, 0, 0))


def run_out_left(rig, f0, f1, fps):
    _walk(rig, f0, f1, fps, (0, 0, 0), (-22, 0, 0), speed_frames=4, run=True)


def run_out_right(rig, f0, f1, fps):
    _walk(rig, f0, f1, fps, (0, 0, 0), (22, 0, 0), speed_frames=4, run=True)


def hidden(rig, f0, f1, fps):
    """Character is off-stage for this shot."""
    pose(rig, f0, offset=(0, 0, -500))
    pose(rig, f1 - 1, offset=(0, 0, -500))


ANIMS = {f.__name__: f for f in [
    idle, talk, shocked, scared, angry, laugh, sad, cry, wave, point, facepalm, think, dance, jump,
    fall, lie, sit, run_in_place, walk_in_left, walk_in_right, walk_out_left, walk_out_right,
    run_out_left, run_out_right, hidden]}
