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
CTX = {"focus": None}  # set per shot by render_episode: world (x, y) of whoever is speaking


def _seed(rig):
    return sum(ord(c) for c in rig.name) % 97


def _glance(rig):
    """Head yaw (degrees) that makes this character look at the current speaker."""
    fx = CTX.get("focus")
    if not fx:
        return 0.0
    dx = fx[0] - rig.base[0]
    if abs(dx) < 0.5:
        return 0.0
    ang = math.degrees(math.atan2(dx, 3.0)) - rig.base_yaw
    return max(-38.0, min(38.0, ang * 0.8))


def idle(rig, f0, f1, fps):
    """Alive idle: breathing, weight shifts, looks at whoever is talking, small fidgets."""
    sd = _seed(rig)
    look = _glance(rig)
    step = max(8, fps // 2)
    fidgets = [(0, 0), (-12, 6), (0, 0), (8, -4), (0, 0), (-20, 10)]
    for i, f in _loop(f0, f1, step):
        ph = (i + sd) % 4
        sway = (-1, 0, 1, 0)[ph]
        fa, fb = fidgets[(i + sd) % len(fidgets)]
        tilt_head = 5 * math.sin((i + sd) * 1.3)
        pose(rig, f, offset=(0.06 * sway, 0, 0.03 * (ph % 2)), yaw=2.5 * sway,
             head=(3 * math.sin((i + sd) * 0.9), tilt_head * 0.4, look + tilt_head),
             torso=(1.0 * (ph % 2), 1.5 * sway, 0),
             arm_l=(fa * 0.5, -5 - (ph % 2) * 2, 0), arm_r=(fb * 0.5, 5 + (ph % 2) * 2, 0),
             leg_l=(0, -2 * max(0, sway), 0), leg_r=(0, 2 * max(0, -sway), 0))
    pose(rig, f1 - 1, head=(0, 0, look), arm_l=(0, -5, 0), arm_r=(0, 5, 0))


def talk(rig, f0, f1, fps):
    """Expressive talking: both hands gesture, body bounces on the beat, head nods and turns."""
    sd = _seed(rig)
    step = max(6, fps // 4)
    gestures = [((-40, 10, 20), (-10, -8, 0)), ((-15, 25, 0), (-45, -15, -20)), ((-60, 5, 30), (-60, -5, -30)),
                ((-25, 15, 10), (0, -6, 0)), ((-10, 8, 0), (-35, -22, -10)), ((-70, 30, 0), (-20, -10, 0))]
    for i, f in _loop(f0, f1, step):
        ar, al = gestures[(i + sd) % len(gestures)]
        beat = i % 2
        pose(rig, f, offset=(0, -0.05 * beat, 0.07 * beat), yaw=4 * math.sin(i * 0.8 + sd),
             head=(5 if beat else -4, 3 * math.sin(i * 1.7), 7 * math.sin(i * 0.9 + sd)),
             torso=(4 if beat else 1, 2 * math.sin(i * 1.1), 3 * math.sin(i * 0.6)),
             arm_r=ar, arm_l=al)
    pose(rig, f1 - 1, arm_l=(0, -5, 0), arm_r=(0, 5, 0))


def nod(rig, f0, f1, fps):
    look = _glance(rig)
    for i, f in _loop(f0, f1, 6):
        pose(rig, f, head=(-10 if i % 2 else 4, 0, look), arm_l=(0, -5, 0), arm_r=(0, 5, 0),
             offset=(0, 0, 0.03 * (i % 2)))
    pose(rig, f1 - 1, head=(0, 0, look))


def shrug(rig, f0, f1, fps):
    up = dict(arm_l=(-30, -55, 40), arm_r=(-30, 55, -40), torso=(0, 0, 0))
    pose(rig, f0)
    pose(rig, min(f0 + 5, f1 - 1), offset=(0, 0, 0.12), head=(0, 12, 0), **up)
    for i, f in _loop(f0 + 10, f1, 10):
        pose(rig, f, head=(0, 12 if i % 2 else -10, 0), **up)
    pose(rig, f1 - 1, head=(0, 12, 0), **up)


def brag(rig, f0, f1, fps):
    """Show-off: hands on hips, chest out, chin up, little bounce."""
    hips = dict(arm_l=(0, -35, -60), arm_r=(0, 35, 60), torso=(6, 0, 0))
    pose(rig, f0)
    for i, f in _loop(f0 + 4, f1, 8):
        s = 1 if i % 2 else -1
        pose(rig, f, offset=(0, 0, 0.1 if i % 2 else 0), yaw=8 * s, head=(12, 4 * s, 10 * s), **hips)
    pose(rig, f1 - 1, head=(12, 0, 0), **hips)


def cross_arms(rig, f0, f1, fps):
    ca = dict(arm_l=(-85, 0, -55), arm_r=(-85, 0, 55))
    look = _glance(rig)
    pose(rig, f0)
    for i, f in _loop(f0 + 5, f1, 12):
        pose(rig, f, head=(4, 5 if i % 2 else -3, look), offset=(0.04 * (1 if i % 2 else -1), 0, 0), **ca)
    pose(rig, f1 - 1, head=(4, 0, look), **ca)


def look_up(rig, f0, f1, fps):
    """Looks up at something above their head (e.g. their price tag)."""
    pose(rig, f0)
    for i, f in _loop(f0 + 5, f1, 10):
        pose(rig, f, head=(28, 4 if i % 2 else -4, 6 if i % 2 else -6), torso=(4, 0, 0),
             arm_l=(0, -8, 0), arm_r=(-30 if i % 3 == 0 else -10, 15, 0))
    pose(rig, f1 - 1, head=(28, 0, 0), torso=(4, 0, 0))


def point_laugh(rig, f0, f1, fps):
    look = _glance(rig)
    for i, f in _loop(f0, f1, 4):
        back = 12 if i % 2 else 3
        pose(rig, f, torso=(back, 0, 0), head=(back, 0, look * 0.6), arm_r=(-90, 0, 0),
             arm_l=(-50, -10, 30), offset=(0, 0, 0.12 if i % 2 else 0))
    pose(rig, f1 - 1, torso=(6, 0, 0), arm_r=(-90, 0, 0), arm_l=(-50, -10, 30))


def whisper(rig, f0, f1, fps):
    """Leans toward the speaker focus with a hand by the mouth."""
    look = _glance(rig)
    side = 1 if look >= 0 else -1
    w = dict(arm_r=(-150, -10, 0) if side < 0 else (-20, 10, 0), arm_l=(-150, 10, 0) if side > 0 else (-20, -10, 0))
    pose(rig, f0)
    for i, f in _loop(f0 + 5, f1, 8):
        pose(rig, f, tilt=(0, -8 * side), head=(-4, 0, look + (6 if i % 2 else 0)), **w)
    pose(rig, f1 - 1, tilt=(0, -8 * side), head=(-4, 0, look), **w)


def sad_look_down(rig, f0, f1, fps):
    body = dict(torso=(-10, 0, 0), arm_l=(6, -2, 0), arm_r=(6, 2, 0))
    pose(rig, f0)
    pose(rig, min(f0 + 8, f1 - 1), head=(-25, 0, 0), **body)
    for i, f in _loop(f0 + 14, f1, 14):
        pose(rig, f, offset=(0, 0, -0.04 * (i % 2)), head=(-25, 0, 6 if i % 2 else -6), **body)
    pose(rig, f1 - 1, head=(-25, 0, 0), **body)


def rip_tag(rig, f0, f1, fps):
    """Reaches above the head, yanks something down, crumples it and drops it."""
    pose(rig, f0)
    pose(rig, min(f0 + 8, f1 - 1), arm_r=(0, 165, 0), head=(25, 0, 0), offset=(0, 0, 0.3))
    pose(rig, min(f0 + 14, f1 - 1), arm_r=(-60, 20, 0), head=(-10, 0, 0))
    for i, f in _loop(f0 + 18, min(f1, f0 + 34), 4):
        pose(rig, f, arm_r=(-70, -10 if i % 2 else 10, 0), arm_l=(-70, 10 if i % 2 else -10, 0), head=(-15, 0, 0))
    pose(rig, min(f0 + 40, f1 - 1), arm_r=(10, 20, 0), arm_l=(0, -5, 0), head=(-12, 0, 0))
    pose(rig, f1 - 1, head=(-8, 0, 0))


def celebrate(rig, f0, f1, fps):
    for i, f in _loop(f0, f1, 7):
        s = 1 if i % 2 else -1
        pose(rig, f, offset=(0, 0, 0.6 if i % 2 else 0), arm_l=(0, -160 if s > 0 else -120, 0),
             arm_r=(0, 120 if s > 0 else 160, 0), head=(10, 0, 8 * s), leg_l=(-15 * (i % 2), 0, 0))
    pose(rig, f1 - 1)


def stumble(rig, f0, f1, fps):
    """Gets bumped aside: staggers to his right (screen left) and nearly falls."""
    pose(rig, f0)
    pose(rig, min(f0 + 5, f1 - 1), offset=(-1.2, 0, 0.2), tilt=(0, -25), arm_l=(0, -110, 0), arm_r=(0, 130, 0))
    pose(rig, min(f0 + 11, f1 - 1), offset=(-2.4, 0, 0), tilt=(0, 12), arm_l=(0, -70, 0), arm_r=(0, 60, 0))
    pose(rig, min(f0 + 17, f1 - 1), offset=(-2.6, 0, 0), arm_l=(0, -10, 0), arm_r=(0, 10, 0), head=(-15, 0, 0))
    pose(rig, f1 - 1, offset=(-2.6, 0, 0), head=(-20, 0, 0), torso=(-6, 0, 0))


def step_away_right(rig, f0, f1, fps):
    """Side-steps away from someone (to the right) and keeps a wary look back."""
    for i, f in _loop(f0, min(f1, f0 + 18), 6):
        t = (f - f0) / 18
        s = 1 if i % 2 else -1
        pose(rig, f, offset=(2.5 * t, 0.6 * t, 0.1 * (i % 2)), yaw=-25,
             leg_l=(25 * s, 0, 0), leg_r=(-25 * s, 0, 0), arm_l=(-20 * s, 0, 0), arm_r=(20 * s, 0, 0))
    pose(rig, min(f0 + 20, f1 - 1), offset=(2.5, 0.6, 0), head=(0, 0, -30), arm_l=(-30, -10, 0))
    pose(rig, f1 - 1, offset=(2.5, 0.6, 0), head=(0, 0, -30), arm_l=(-30, -10, 0))


def cut_line(rig, f0, f1, fps):
    """Strolls in front of everyone, 6 studs to the left, chin up, then poses."""
    end = min(f1 - 1, f0 + 36)
    n = max(1, end - f0)
    for i, f in _loop(f0, end, 6):
        t = (f - f0) / n
        s = 1 if i % 2 else -1
        pose(rig, f, offset=(-6 * t, -1.6 * math.sin(math.pi * t), 0.06 * (i % 2)), yaw=80,
             head=(12, 0, -40), leg_l=(28 * s, 0, 0), leg_r=(-28 * s, 0, 0), arm_l=(-20 * s, 0, 0),
             arm_r=(20 * s, 0, 0))
    hips = dict(arm_l=(0, -35, -60), arm_r=(0, 35, 60), head=(12, 0, 0), torso=(6, 0, 0))
    pose(rig, min(f0 + 40, f1 - 1), offset=(-6, 0, 0), **hips)
    pose(rig, f1 - 1, offset=(-6, 0, 0), **hips)


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


def step_right(rig, f0, f1, fps):
    """Walks 3.5 studs to the right (toward a friend) and stays there."""
    _walk(rig, f0, min(f1, f0 + 24), fps, (0, 0, 0), (3.5, 0, 0))
    pose(rig, min(f0 + 26, f1 - 1), offset=(3.5, 0, 0.1), head=(5, 0, 15), arm_l=(0, -8, 0), arm_r=(0, 8, 0))
    pose(rig, f1 - 1, offset=(3.5, 0, 0), head=(0, 0, 15), arm_l=(0, -5, 0), arm_r=(0, 5, 0))


def run_out_left(rig, f0, f1, fps):
    _walk(rig, f0, f1, fps, (0, 0, 0), (-22, 0, 0), speed_frames=4, run=True)


def run_out_right(rig, f0, f1, fps):
    _walk(rig, f0, f1, fps, (0, 0, 0), (22, 0, 0), speed_frames=4, run=True)


def frozen(rig, f0, f1, fps):
    """Stuck mid-run like a statue (Freeze Tag)."""
    ice = dict(leg_l=(35, 0, 0), leg_r=(-35, 0, 0), arm_l=(-60, -10, 0), arm_r=(50, 10, 0),
               torso=(-8, 0, 0), head=(5, 0, 8))
    pose(rig, f0, **ice)
    pose(rig, f1 - 1, **ice)


def unfreeze(rig, f0, f1, fps):
    """Breaks out of the frozen pose with a little shake, then relaxes."""
    ice = dict(leg_l=(35, 0, 0), leg_r=(-35, 0, 0), arm_l=(-60, -10, 0), arm_r=(50, 10, 0), torso=(-8, 0, 0))
    pose(rig, f0, **ice)
    for i, f in _loop(f0 + 3, min(f1, f0 + 15), 3):
        pose(rig, f, offset=(0.08 if i % 2 else -0.08, 0, 0), **ice)
    pose(rig, min(f0 + 18, f1 - 1), arm_l=(0, -150, 0), arm_r=(0, 150, 0), offset=(0, 0, 0.6))
    pose(rig, f1 - 1)


def hidden(rig, f0, f1, fps):
    """Character is off-stage for this shot."""
    pose(rig, f0, offset=(0, 0, -500))
    pose(rig, f1 - 1, offset=(0, 0, -500))


def turn_around(rig, f0, f1, fps):
    """Slowly turns to show their back to the camera (e.g. to reveal a patch), glances over the shoulder."""
    yaw0 = -rig.base_yaw
    pose(rig, f0)
    end = min(f1 - 1, f0 + 14)
    for i, f in _loop(f0 + 2, end, 3):
        t = (f - f0) / max(1, end - f0)
        pose(rig, f, yaw=yaw0 + 180 * t, arm_l=(0, -5, 0), arm_r=(0, 5, 0), offset=(0, 0, 0.04 * (i % 2)))
    pose(rig, end, yaw=yaw0 + 180, head=(0, 0, 25), arm_l=(0, -5, 0), arm_r=(0, 5, 0))
    pose(rig, f1 - 1, yaw=yaw0 + 180, head=(0, 0, 35), arm_l=(0, -5, 0), arm_r=(0, 5, 0))


def sit_talk(rig, f0, f1, fps):
    """Seated and talking (dinner table / classroom)."""
    s = dict(offset=(0, 0.4, -0.95), leg_l=(-90, 0, 0), leg_r=(-90, 0, 0))
    for i, f in _loop(f0, f1, max(6, fps // 4)):
        g = ((-40, 10, 20), (-60, 5, 30), (-25, 15, 10))[i % 3]
        pose(rig, f, head=(5 if i % 2 else -3, 0, 6 * math.sin(i)), arm_r=g, arm_l=(-45, -5, 0), **s)
    pose(rig, f1 - 1, arm_l=(-40, 0, 0), arm_r=(-40, 0, 0), **s)


def sit_shocked(rig, f0, f1, fps):
    s = dict(offset=(0, 0.4, -0.95), leg_l=(-90, 0, 0), leg_r=(-90, 0, 0))
    pose(rig, f0, arm_l=(-40, 0, 0), arm_r=(-40, 0, 0), **s)
    for i, f in _loop(f0 + 3, f1, 4):
        pose(rig, f, torso=(-8, 0, 0), head=(10, 3 if i % 2 else -3, 0), arm_l=(-150, -20, 0), arm_r=(-150, 20, 0), **s)
    pose(rig, f1 - 1, torso=(-8, 0, 0), head=(10, 0, 0), arm_l=(-150, -20, 0), arm_r=(-150, 20, 0), **s)


def sit_fall(rig, f0, f1, fps):
    """Sitting, then topples sideways off the chair onto the floor."""
    s = dict(leg_l=(-90, 0, 0), leg_r=(-90, 0, 0))
    pose(rig, f0, offset=(0, 0.4, -0.95), **s)
    pose(rig, min(f0 + 4, f1 - 1), offset=(0.3, 0.4, -0.85), tilt=(0, 30), arm_l=(0, -120, 0), arm_r=(0, 120, 0), **s)
    pose(rig, min(f0 + 10, f1 - 1), offset=(1.6, 0.4, -1.4), tilt=(0, 88), arm_l=(0, -90, 0), arm_r=(0, 90, 0),
         leg_l=(-60, 0, 0), leg_r=(-30, 0, 0))
    pose(rig, f1 - 1, offset=(1.8, 0.4, -1.45), tilt=(0, 90), arm_l=(0, -80, 0), arm_r=(0, 70, 0),
         leg_l=(-60, 0, 0), leg_r=(-30, 0, 0))


def sit_point(rig, f0, f1, fps):
    s = dict(offset=(0, 0.4, -0.95), leg_l=(-90, 0, 0), leg_r=(-90, 0, 0))
    look = _glance(rig)
    for i, f in _loop(f0, f1, 5):
        pose(rig, f, head=(4, 0, look), arm_r=(-90, 0, 0), arm_l=(-40, 0, 0), torso=(0, 0, 0),
             **dict(s, offset=(0, 0.4, -0.95 + 0.04 * (i % 2))))
    pose(rig, f1 - 1, head=(4, 0, look), arm_r=(-90, 0, 0), arm_l=(-40, 0, 0), **s)


def slide_object(rig, f0, f1, fps):
    """Leans forward and pushes something across a table with one hand (seated or standing)."""
    pose(rig, f0)
    pose(rig, min(f0 + 6, f1 - 1), torso=(-15, 0, 0), arm_r=(-80, 0, 0), head=(-5, 0, 0))
    pose(rig, min(f0 + 16, f1 - 1), torso=(-20, 0, 10), arm_r=(-95, 0, 25), head=(-8, 0, 0))
    pose(rig, f1 - 1, torso=(-5, 0, 0), arm_r=(0, 5, 0), arm_l=(0, -35, -60), head=(8, 0, 0))


def film_selfie(rig, f0, f1, fps):
    """Holds a phone out at arm's length, posing and dancing for a video."""
    for i, f in _loop(f0, f1, 6):
        s = 1 if i % 2 else -1
        pose(rig, f, offset=(0.15 * s, 0, 0.08 * (i % 2)), yaw=10 * s, arm_r=(-120, 0, 0),
             arm_l=(0, -40 if s > 0 else -15, 30), head=(5, 6 * s, 8 * s), torso=(3, 4 * s, 0))
    pose(rig, f1 - 1, arm_r=(-120, 0, 0))


def back_up_bump(rig, f0, f1, fps):
    """Steps backwards while filming and bumps into something behind her, then freezes."""
    for i, f in _loop(f0, min(f1, f0 + 12), 4):
        t = (f - f0) / 12
        s = 1 if i % 2 else -1
        pose(rig, f, offset=(-1.0 * t, 0.6 * t, 0.05 * (i % 2)), arm_r=(-120, 0, 0), leg_l=(-20 * s, 0, 0),
             leg_r=(20 * s, 0, 0))
    pose(rig, min(f0 + 14, f1 - 1), offset=(-1.1, 0.65, 0.15), arm_r=(-120, 0, 0), arm_l=(0, -60, 0), head=(10, 0, 30))
    pose(rig, f1 - 1, offset=(-1.1, 0.65, 0), arm_r=(-60, 0, 0), arm_l=(-30, -30, 0), head=(-15, 0, 40))


def sit_faceplant(rig, f0, f1, fps):
    """Seated, then slams face-down onto the desk and stays there."""
    s = dict(offset=(0, 0.4, -0.95), leg_l=(-90, 0, 0), leg_r=(-90, 0, 0))
    pose(rig, f0, arm_l=(-40, 0, 0), arm_r=(-40, 0, 0), **s)
    pose(rig, min(f0 + 5, f1 - 1), torso=(8, 0, 0), head=(10, 0, 0), arm_l=(-60, 0, 0), arm_r=(-60, 0, 0), **s)
    pose(rig, min(f0 + 9, f1 - 1), torso=(-55, 0, 0), head=(-20, 0, 0), arm_l=(-120, -20, 0), arm_r=(-120, 20, 0), **s)
    for i, f in _loop(f0 + 14, f1, 10):
        pose(rig, f, torso=(-55, 0, 0), head=(-20, 0, 4 if i % 2 else -4), arm_l=(-120, -20, 0), arm_r=(-120, 20, 0), **s)
    pose(rig, f1 - 1, torso=(-55, 0, 0), head=(-20, 0, 0), arm_l=(-120, -20, 0), arm_r=(-120, 20, 0), **s)


def flatten(rig, f0, f1, fps):
    """Presses flat against the wall behind them, arms spread, terrified."""
    pose(rig, f0)
    pose(rig, min(f0 + 5, f1 - 1), offset=(0, 0.7, 0.1), torso=(8, 0, 0), head=(12, 0, 0),
         arm_l=(0, -80, 0), arm_r=(0, 80, 0))
    for i, f in _loop(f0 + 8, f1, 4):
        pose(rig, f, offset=(0.03 * (1 if i % 2 else -1), 0.7, 0.1), torso=(8, 0, 0), head=(12, 0, 6 if i % 2 else -6),
             arm_l=(0, -80, 0), arm_r=(0, 80, 0))
    pose(rig, f1 - 1, offset=(0, 0.7, 0.1), torso=(8, 0, 0), head=(12, 0, 0), arm_l=(0, -80, 0), arm_r=(0, 80, 0))


def sit_slide_down(rig, f0, f1, fps):
    """Embarrassed: slowly slides down in the chair until only the head shows."""
    pose(rig, f0, offset=(0, 0.4, -0.95), leg_l=(-90, 0, 0), leg_r=(-90, 0, 0), arm_l=(-40, 0, 0), arm_r=(-40, 0, 0))
    pose(rig, f1 - 1, offset=(0, -0.3, -1.6), tilt=(-25, 0), leg_l=(-70, 0, 0), leg_r=(-70, 0, 0), head=(20, 0, 0),
         arm_l=(-20, -10, 0), arm_r=(-20, 10, 0))


def sweat(rig, f0, f1, fps):
    """Nervous: tugs collar, shifts weight, glances around."""
    for i, f in _loop(f0, f1, 5):
        s = 1 if i % 2 else -1
        pose(rig, f, offset=(0.05 * s, 0, 0), head=(-5, 0, 20 * s), arm_r=(-150, 30, 0), arm_l=(0, -8, 0), torso=(-3, 0, 0))
    pose(rig, f1 - 1, arm_r=(-150, 30, 0))


def hug(rig, f0, f1, fps):
    """Side hug: arm over the shoulder of the person beside them, leaning in, swaying happily.
    The partner is on whichever side the character is turned toward."""
    right = rig.base_yaw >= 0
    over = (0, -72, 0) if right else (0, 72, 0)
    across = (-70, 0, 40) if right else (-70, 0, -40)
    for i, f in _loop(f0, f1, 8):
        s = 1 if i % 2 else -1
        kw = {"arm_l": over, "arm_r": across} if right else {"arm_r": over, "arm_l": across}
        pose(rig, f, offset=((0.12 if right else -0.12) + 0.04 * s, 0, 0), tilt=(0, 4 if right else -4),
             head=(4, 10 if right else -10, 6 * s), **kw)
    kw = {"arm_l": over, "arm_r": across} if right else {"arm_r": over, "arm_l": across}
    pose(rig, f1 - 1, offset=(0.12 if right else -0.12, 0, 0), tilt=(0, 4 if right else -4),
         head=(4, 10 if right else -10, 0), **kw)


def yell_back(rig, f0, f1, fps):
    """Spins round to face the window/door behind them and points, yelling."""
    back = 180 - rig.base_yaw
    pose(rig, f0)
    pose(rig, min(f0 + 5, f1 - 1), yaw=back, arm_r=(-90, 0, 0), head=(8, 0, 0), torso=(6, 0, 0))
    for i, f in _loop(f0 + 8, f1, 5):
        pose(rig, f, yaw=back, offset=(0, 0, 0.04 * (i % 2)), arm_r=(-95 if i % 2 else -85, 0, 0),
             head=(10 if i % 2 else 4, 0, 0), torso=(6, 0, 0))
    pose(rig, f1 - 1, yaw=back, arm_r=(-90, 0, 0), head=(8, 0, 0), torso=(6, 0, 0))


def bang_window(rig, f0, f1, fps):
    """Pounds on glass in front of them with both fists, desperate."""
    for i, f in _loop(f0, f1, 4):
        a = i % 2
        pose(rig, f, offset=(0, -0.08 * a, 0.03 * a), head=(6, 0, 5 if a else -5), torso=(5 if a else 0, 0, 0),
             arm_l=(-150 if a else -110, -15, 0), arm_r=(-110 if a else -150, 15, 0))
    pose(rig, f1 - 1, arm_l=(-130, -15, 0), arm_r=(-130, 15, 0))


def play_game(rig, f0, f1, fps):
    """Holds a game controller in both hands, thumbs mashing, leaning into it."""
    for i, f in _loop(f0, f1, 4):
        a = i % 2
        pose(rig, f, offset=(0, 0, 0.02 * a), head=(-12, 0, 4 if a else -4), torso=(8, 3 if a else -3, 0),
             arm_l=(-60 - 6 * a, -18, -25), arm_r=(-66 + 6 * a, 18, 25))
    pose(rig, f1 - 1, head=(-12, 0, 0), torso=(8, 0, 0), arm_l=(-60, -18, -25), arm_r=(-60, 18, 25))


def touch_cheek(rig, f0, f1, fps):
    """Slowly raises a hand to touch their cheek, frozen in realisation."""
    tc = dict(arm_r=(-145, -30, 0), head=(-6, 8, -10))
    pose(rig, f0)
    pose(rig, min(f0 + 12, f1 - 1), **tc)
    for i, f in _loop(f0 + 16, f1, 9):
        pose(rig, f, arm_r=(-145, -30, 0), head=(-6, 8, -10 + (2 if i % 2 else -2)))
    pose(rig, f1 - 1, **tc)


def hold_photo(rig, f0, f1, fps):
    """Holds something up in both hands for the other person to see."""
    hp = dict(arm_l=(-95, -5, -20), arm_r=(-95, 5, 20), head=(-4, 0, 0))
    pose(rig, f0)
    pose(rig, min(f0 + 6, f1 - 1), **hp)
    pose(rig, f1 - 1, **hp)


def lean_whisper(rig, f0, f1, fps):
    """Leans in slowly toward the other person, hand cupped by the mouth (face stays to camera)."""
    d = 1 if rig.base_yaw >= 0 else -1
    pose(rig, f0)
    pose(rig, f1 - 1, offset=(0.15 * d, 0, -0.05), tilt=(0, 4 * d), torso=(8, 0, 0), head=(4, 4 * d, 0),
         arm_r=(-140, -30, 0) if d > 0 else (0, 5, 0), arm_l=(0, -5, 0) if d > 0 else (-140, 30, 0))

SEAT = dict(offset=(0, 0.4, -0.95), leg_l=(-90, 0, 0), leg_r=(-90, 0, 0))


def _sneeze(rig, f0, f1, seat):
    """Ah... ah... CHOO: head and body wind back, then snap forward, then a little recoil."""
    base = SEAT if seat else {}
    ox, oy, oz = base.get("offset", (0, 0, 0))
    legs = {k: v for k, v in base.items() if k != "offset"}
    n = f1 - f0
    wind = f0 + int(n * 0.35)
    snap = min(wind + 3, f1 - 2)
    pose(rig, f0, offset=(ox, oy, oz), **legs)
    pose(rig, wind, offset=(ox, oy + 0.15, oz + 0.05), head=(28, 0, 0), torso=(-14, 0, 0),
         arm_l=(-20, -30, 0), arm_r=(-20, 30, 0), **legs)
    pose(rig, snap, offset=(ox, oy - 0.35, oz - 0.05), head=(-35, 0, 0), torso=(26, 0, 0),
         arm_l=(-60, -10, 0), arm_r=(-60, 10, 0), **legs)
    pose(rig, min(snap + 5, f1 - 1), offset=(ox, oy - 0.1, oz), head=(-8, 0, 6), torso=(8, 0, 0), **legs)
    pose(rig, f1 - 1, offset=(ox, oy, oz), head=(0, 0, 0), **legs)


def sneeze(rig, f0, f1, fps):
    _sneeze(rig, f0, f1, False)


def sit_sneeze(rig, f0, f1, fps):
    _sneeze(rig, f0, f1, True)


def sneeze_build(rig, f0, f1, fps):
    """The 'ah... ah...' before a sneeze: nose twitches, head tilts further and further back, eyes squeeze.
    Ends at the peak of the wind-up (the next shot is the sneeze)."""
    for i, f in _loop(f0, f1, 3):
        t = (f - f0) / max(1, f1 - f0)
        tw = 2 if i % 2 else -2
        pose(rig, f, offset=(0, 0.2 * t, 0.05 * t), head=(32 * t + tw, 0, tw), torso=(-15 * t, 0, 0),
             arm_l=(-30 * t, -30 * t, 0), arm_r=(-30 * t, 30 * t, 0))
    pose(rig, f1 - 1, offset=(0, 0.2, 0.05), head=(34, 0, 0), torso=(-16, 0, 0), arm_l=(-30, -30, 0), arm_r=(-30, 30, 0))


def sit_write(rig, f0, f1, fps):
    """Seated, scribbling answers at lightning speed."""
    for i, f in _loop(f0, f1, 2):
        a = i % 2
        pose(rig, f, head=(-20, 0, 4 if a else -4), torso=(10, 0, 0), arm_r=(-55 - 10 * a, 10 * a, 0),
             arm_l=(-40, -10, 0), **SEAT)
    pose(rig, f1 - 1, head=(-20, 0, 0), torso=(10, 0, 0), arm_r=(-55, 0, 0), arm_l=(-40, -10, 0), **SEAT)


def sit_up_scream(rig, f0, f1, fps):
    """Bolts upright in bed, arms flung out, screaming."""
    pose(rig, f0, tilt=(-40, 0), **SEAT)
    pose(rig, min(f0 + 4, f1 - 1), arm_l=(0, -110, 0), arm_r=(0, 110, 0), head=(12, 0, 0), **SEAT)
    for i, f in _loop(f0 + 6, f1, 3):
        s = 1 if i % 2 else -1
        pose(rig, f, arm_l=(0, -110 - 8 * s, 0), arm_r=(0, 110 + 8 * s, 0), head=(12, 0, 5 * s), **SEAT)
    pose(rig, f1 - 1, arm_l=(0, -110, 0), arm_r=(0, 110, 0), head=(12, 0, 0), **SEAT)


def hold_feather(rig, f0, f1, fps):
    """Holds something up beside their face with one hand, grinning (the feather)."""
    pose(rig, f0, arm_r=(-150, 20, 0))
    for i, f in _loop(f0, f1, 7):
        pose(rig, f, arm_r=(-150, 20 + (4 if i % 2 else -4), 0), head=(4, 0, 6 if i % 2 else -6))
    pose(rig, f1 - 1, arm_r=(-150, 20, 0))

def still(rig, f0, f1, fps):
    """Stands completely still (used before a delayed move)."""
    pose(rig, f0)
    pose(rig, f1 - 1)


HAND_START = (0, 40, 0)  # where a loop-ending hand raise stops, and the opening raise starts from


def raise_hand(rig, f0, f1, fps):
    """Right hand shoots straight up from the low 'starting' position and stays up."""
    pose(rig, f0, arm_r=HAND_START)
    pose(rig, min(f0 + 4, f1 - 1), arm_r=(0, 140, 0), head=(6, 0, 0))
    for i, f in _loop(f0 + 7, f1, 8):
        pose(rig, f, arm_r=(0, 140, 0), head=(6, 0, 3 if i % 2 else -3))
    pose(rig, f1 - 1, arm_r=(0, 140, 0))


def raise_hand_start(rig, f0, f1, fps):
    """Begins lifting the right hand slowly; the shot (and video) ends mid-lift."""
    pose(rig, f0)
    pose(rig, f1 - 1, arm_r=HAND_START)


def spin(rig, f0, f1, fps):
    n = max(8, min(f1 - f0 - 1, 16))
    for k in range(0, n + 1, 2):
        pose(rig, f0 + k, yaw=360 * k / n, offset=(0, 0, 0.3 * math.sin(math.pi * k / n)), arm_l=(0, -70, 0), arm_r=(0, 70, 0))
    pose(rig, f1 - 1)


def chicken_dance(rig, f0, f1, fps):
    """Elbows flapping like wings, head pecking, knees bobbing."""
    for i, f in _loop(f0, f1, 4):
        a = i % 2
        pose(rig, f, offset=(0, 0, 0.12 * a), head=(18 if a else -6, 0, 0), torso=(6 * a, 0, 0),
             arm_l=(-20, -60 if a else -15, 40), arm_r=(-20, 60 if a else 15, -40),
             leg_l=(-12 * a, 0, 0), leg_r=(-12 * (1 - a), 0, 0))
    pose(rig, f1 - 1)


def sit_eat(rig, f0, f1, fps):
    """Seated, shovels food into mouth happily."""
    seat = dict(offset=(0, 0.4, -0.95), leg_l=(-90, 0, 0), leg_r=(-90, 0, 0))
    for i, f in _loop(f0, f1, 5):
        a = i % 2
        pose(rig, f, arm_r=(-150 if a else -60, -25 if a else 0, 0), head=(-6 if a else 2, 0, 0), **seat)
    pose(rig, f1 - 1, arm_r=(-60, 0, 0), **seat)


def sit_reach_freeze(rig, f0, f1, fps):
    """Seated, slowly reaches toward the plate... and freezes mid-air."""
    seat = dict(offset=(0, 0.4, -0.95), leg_l=(-90, 0, 0), leg_r=(-90, 0, 0))
    pose(rig, f0, **seat)
    mid = min(f0 + int((f1 - f0) * 0.4), f1 - 2)
    pose(rig, mid, arm_r=(-75, 0, 0), torso=(8, 0, 0), **seat)
    pose(rig, f1 - 1, arm_r=(-75, 0, 0), torso=(8, 0, 0), head=(4, 0, 18), **seat)


def sit_thumbs_up(rig, f0, f1, fps):
    seat = dict(offset=(0, 0.4, -0.95), leg_l=(-90, 0, 0), leg_r=(-90, 0, 0))
    pose(rig, f0, **seat)
    pose(rig, min(f0 + 4, f1 - 1), arm_r=(-100, -20, 0), head=(4, 6, 0), **seat)
    pose(rig, f1 - 1, arm_r=(-100, -20, 0), head=(4, 6, 0), **seat)


def tilt_glass(rig, f0, f1, fps):
    """Holds a glass out at chest height and slowly, dramatically tips it."""
    pose(rig, f0, arm_r=(-80, 0, 0))
    pose(rig, f1 - 1, arm_r=(-85, 0, -35), head=(-10, 0, 8), torso=(4, 0, 0))


def resist_raise(rig, f0, f1, fps):
    """The right arm rises on its own while the left hand grabs it and pulls down."""
    n = f1 - f0
    for i, f in _loop(f0, f1, 3):
        t = (f - f0) / max(1, n)
        up = 40 + 100 * min(1.0, t * 1.3)
        sh = 6 if i % 2 else -6
        pose(rig, f, offset=(0.05 * (1 if i % 2 else -1), 0, 0), arm_r=(0, up + sh, 0),
             arm_l=(-90 - up * 0.3, 0, -40), torso=(-6, 0, 0), head=(14, 0, 8 * (1 if i % 2 else -1)))
    pose(rig, f1 - 1, arm_r=(0, 140, 0), arm_l=(-140, 0, -40), head=(14, 0, 0))


def arms_up(rig, f0, f1, fps):
    """Both arms shoot straight up and stay there."""
    pose(rig, f0)
    pose(rig, min(f0 + 3, f1 - 1), arm_l=(0, -140, 0), arm_r=(0, 140, 0), offset=(0, 0, 0.15))
    for i, f in _loop(f0 + 6, f1, 6):
        pose(rig, f, arm_l=(0, -140, 0), arm_r=(0, 140, 0), head=(0, 0, 4 if i % 2 else -4))
    pose(rig, f1 - 1, arm_l=(0, -140, 0), arm_r=(0, 140, 0))


def raise_hand_l(rig, f0, f1, fps):
    """Same as raise_hand but with the left hand (the side away from someone standing on their right)."""
    L = (0, -HAND_START[1], 0)
    pose(rig, f0, arm_l=L)
    pose(rig, min(f0 + 4, f1 - 1), arm_l=(0, -140, 0), head=(6, 0, 0))
    for i, f in _loop(f0 + 7, f1, 8):
        pose(rig, f, arm_l=(0, -140, 0), head=(6, 0, 3 if i % 2 else -3))
    pose(rig, f1 - 1, arm_l=(0, -140, 0))


def raise_hand_start_l(rig, f0, f1, fps):
    pose(rig, f0)
    pose(rig, f1 - 1, arm_l=(0, -HAND_START[1], 0))



REACH = dict(arm_r=(-70, 0, 0), torso=(10, 0, 0), head=(-6, 0, 0))  # sneaky reach toward something in front


def reach_to(rig, f0, f1, fps):
    """Grins and slowly reaches forward; the shot (video) ends with the hand almost there."""
    pose(rig, f0, head=(-4, 0, 0))
    pose(rig, f1 - 1, **REACH)


def reach_caught(rig, f0, f1, fps):
    """Starts mid-reach (where reach_to ends), freezes, then snaps the hand back guiltily."""
    pose(rig, f0, **REACH)
    pose(rig, min(f0 + 10, f1 - 1), **REACH)
    pose(rig, min(f0 + 14, f1 - 1), arm_r=(-20, 0, 0), torso=(-4, 0, 0), head=(8, 0, 0))
    pose(rig, f1 - 1, arm_r=(-10, 0, 0), head=(6, 0, 0))


def sit_eat_chips(rig, f0, f1, fps):
    """Lounging on the couch munching snacks."""
    seat = dict(offset=(0, 0.4, -0.95), leg_l=(-90, 0, 0), leg_r=(-90, 0, 0))
    for i, f in _loop(f0, f1, 6):
        a = i % 2
        pose(rig, f, arm_r=(-140 if a else -70, -20 if a else 0, 0), arm_l=(-50, 0, 0), head=(4 if a else 0, 0, 0), **seat)
    pose(rig, f1 - 1, arm_l=(-50, 0, 0), **seat)


def eyes_closed_smile(rig, f0, f1, fps):
    """Concentrating hard on a sneaky thought: hands steepled, little sway."""
    for i, f in _loop(f0, f1, 8):
        s = 1 if i % 2 else -1
        pose(rig, f, arm_l=(-80, 0, 30), arm_r=(-80, 0, -30), head=(8, 0, 4 * s), torso=(3, 0, 0))
    pose(rig, f1 - 1, arm_l=(-80, 0, 30), arm_r=(-80, 0, -30), head=(8, 0, 0))



PENCIL_UP = dict(arm_r=(-125, 0, 0), head=(4, 0, 0), torso=(-2, 0, 0))  # holds the pencil up to the camera


def pencil_up(rig, f0, f1, fps):
    """Seated; grins and lifts the pencil up toward the camera. The video ends in this pose."""
    pose(rig, f0, arm_r=(-55, 0, 0), **SEAT)
    pose(rig, f1 - 1, **PENCIL_UP, **SEAT)


def pencil_down(rig, f0, f1, fps):
    """Seated; starts with the pencil held up, brings it down to the notebook and starts sketching."""
    pose(rig, f0, **PENCIL_UP, **SEAT)
    d = min(f0 + 10, f1 - 2)
    pose(rig, d, arm_r=(-55, 0, 0), head=(-18, 0, 0), torso=(8, 0, 0), **SEAT)
    for i, f in _loop(d + 2, f1, 3):
        a = i % 2
        pose(rig, f, arm_r=(-55 - 8 * a, 6 * a, 0), head=(-18, 0, 3 if a else -3), torso=(8, 0, 0), **SEAT)
    pose(rig, f1 - 1, arm_r=(-55, 0, 0), head=(-18, 0, 0), torso=(8, 0, 0), **SEAT)


def backflip(rig, f0, f1, fps):
    """Jumps and does a full backflip, lands, then arms up like a gymnast. Repeats if there's time."""
    f = f0
    while f + 16 < f1:
        pose(rig, f, offset=(0, 0, 0), leg_l=(-20, 0, 0), leg_r=(-20, 0, 0), arm_l=(0, -20, 0), arm_r=(0, 20, 0))
        for k in range(1, 9):
            t = k / 8
            pose(rig, f + 2 * k, offset=(0, 0, 3.2 * math.sin(math.pi * t)), tilt=(-360 * t, 0),
                 arm_l=(-170, 0, 0), arm_r=(-170, 0, 0), leg_l=(-60, 0, 0), leg_r=(-60, 0, 0))
        pose(rig, f + 18, arm_l=(0, -150, 0), arm_r=(0, 150, 0), head=(8, 0, 0))
        f += 26
    pose(rig, f1 - 1, arm_l=(0, -150, 0), arm_r=(0, 150, 0))

ANIMS = {f.__name__: f for f in [
    idle, talk, shocked, scared, angry, laugh, sad, cry, wave, point, facepalm, think, dance, jump,
    fall, lie, sit, run_in_place, walk_in_left, walk_in_right, walk_out_left, walk_out_right,
    run_out_left, run_out_right, frozen, unfreeze, hidden, nod, shrug, brag, cross_arms, look_up,
    point_laugh, whisper, sad_look_down, rip_tag, celebrate, stumble, step_away_right, cut_line, step_right,
    turn_around, sit_talk, sit_shocked, sit_fall, sit_point, slide_object, film_selfie, back_up_bump,
    sit_faceplant, flatten, sit_slide_down, sweat, hug, bang_window, play_game, touch_cheek, hold_photo,
    lean_whisper, yell_back, sneeze, sit_sneeze, sneeze_build, sit_write, sit_up_scream, hold_feather,
    still, raise_hand, raise_hand_start, spin, chicken_dance, sit_eat, sit_reach_freeze, sit_thumbs_up, tilt_glass,
    resist_raise, arms_up, raise_hand_l, raise_hand_start_l, reach_to, reach_caught, sit_eat_chips,
    eyes_closed_smile, pencil_up, pencil_down, backflip]}


def walk_to(rig, f0, start, end, fps, speed=6.5, run=False, max_frames=None):
    """Walk the character in world space from `start` (x, y) to `end` (x, y), starting at f0.
    Turns to face the direction of travel, swings arms and legs, bobs, then turns back.
    Returns the frame the character arrives on. The caller then sets rig.base = end."""
    dx, dy = end[0] - start[0], end[1] - start[1]
    dist = math.hypot(dx, dy)
    if dist < 0.05:
        return f0
    n = max(10, round(dist / speed * fps))
    if max_frames:
        n = max(6, min(n, max_frames - 4))  # walk faster rather than spill into the next shot
    face = math.degrees(math.atan2(dx, -dy)) - rig.base_yaw  # yaw that faces the travel direction
    face = (face + 180) % 360 - 180
    amp, step = (50, 4) if run else (34, 5)
    keep = rig.base
    rig.base = (start[0], start[1], keep[2])
    for i, f in _loop(f0, f0 + n + 1, step):
        t = (f - f0) / n
        turn = min(1.0, (f - f0) / 5.0)
        s = 1 if i % 2 else -1
        pose(rig, f, offset=(dx * t, dy * t, (0.14 if run else 0.07) * (i % 2)), yaw=face * turn,
             leg_l=(amp * s, 0, 0), leg_r=(-amp * s, 0, 0), arm_l=(-amp * s, 0, 0), arm_r=(amp * s, 0, 0),
             torso=(-8 if run else -2, 0, 0), head=(0, 0, 0))
    pose(rig, f0 + n, offset=(dx, dy, 0), yaw=face * 0.5, arm_l=(0, -5, 0), arm_r=(0, 5, 0))
    rig.base = keep
    return f0 + n + 3
