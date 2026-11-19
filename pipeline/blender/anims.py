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


ANIMS = {f.__name__: f for f in [
    idle, talk, shocked, scared, angry, laugh, sad, cry, wave, point, facepalm, think, dance, jump,
    fall, lie, sit, run_in_place, walk_in_left, walk_in_right, walk_out_left, walk_out_right,
    run_out_left, run_out_right, frozen, unfreeze, hidden, nod, shrug, brag, cross_arms, look_up,
    point_laugh, whisper, sad_look_down, rip_tag, celebrate, stumble, step_away_right, cut_line, step_right]}


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
