"""High-detail drawn face for a main character (used when cast.json has
"face_style": {"detailed": {...}}). Draws soft anti-aliased features at 512 px:
almond eyes with iris + catchlight, eyeshadow, winged lashes, tapered brows,
nose, blush and glossy lips, for all 12 expressions with closed / open mouth.

Colours can be overridden in cast.json -> face_style.detailed:
  iris, lashes, brows, eyeshadow, lips, blush, teeth, mouth
"""
import math

import numpy as np

N = 512
ZOOM = 1.35  # features are designed on a 512 canvas, then enlarged to fill the head
_YY, _XX = np.mgrid[0:N, 0:N].astype(np.float32)
_XX = (_XX - N / 2) / ZOOM + N / 2
_YY = (_YY - N / 2) / ZOOM + N / 2 + 10


def hex3(h):
    h = h.lstrip("#")
    c = [int(h[i:i + 2], 16) / 255.0 for i in (0, 2, 4)]
    return np.array([x / 12.92 if x <= 0.04045 else ((x + 0.055) / 1.055) ** 2.4 for x in c], np.float32)


# ---------------------------------------------------------------- soft masks
def _aa(d, w=1.4):
    return np.clip(0.5 - d / w, 0.0, 1.0)


def ellipse(cx, cy, rx, ry, soft=1.4):
    d = (np.sqrt(((_XX - cx) / rx) ** 2 + ((_YY - cy) / ry) ** 2) - 1.0) * min(rx, ry)
    return _aa(d, soft)


def ring(cx, cy, rx, ry, w):
    d = np.abs(np.sqrt(((_XX - cx) / rx) ** 2 + ((_YY - cy) / ry) ** 2) - 1.0) * min(rx, ry) - w / 2
    return _aa(d)


def capsule(x0, y0, x1, y1, w0, w1=None):
    w1 = w0 if w1 is None else w1
    dx, dy = x1 - x0, y1 - y0
    t = np.clip(((_XX - x0) * dx + (_YY - y0) * dy) / (dx * dx + dy * dy + 1e-6), 0, 1)
    d = np.sqrt((_XX - (x0 + t * dx)) ** 2 + (_YY - (y0 + t * dy)) ** 2) - (w0 + (w1 - w0) * t) / 2
    return _aa(d)


def polyline(pts, w0, w1):
    m = np.zeros((N, N), np.float32)
    n = len(pts) - 1
    for i in range(n):
        a = w0 + (w1 - w0) * i / n
        b = w0 + (w1 - w0) * (i + 1) / n
        m = np.maximum(m, capsule(*pts[i], *pts[i + 1], a, b))
    return m


def bezier(p0, p1, p2, steps=14):
    return [((1 - t) ** 2 * p0[0] + 2 * (1 - t) * t * p1[0] + t * t * p2[0],
             (1 - t) ** 2 * p0[1] + 2 * (1 - t) * t * p1[1] + t * t * p2[1]) for t in np.linspace(0, 1, steps)]


def heart(cx, cy, s):
    x = (_XX - cx) / s
    y = -(_YY - cy) / s + 0.25
    v = (x * x + y * y - 1) ** 3 - x * x * y ** 3
    return np.clip(-v * 6 + 0.5, 0, 1)


class Canvas:
    def __init__(self, skin):
        self.px = np.empty((N, N, 3), np.float32)
        self.px[:] = skin

    def paint(self, mask, color, alpha=1.0):
        a = (mask * alpha)[..., None]
        self.px = self.px * (1 - a) + np.asarray(color, np.float32) * a


# --------------------------------------------------------------- expression
#            eye_open brow_tilt brow_raise pupil  look_y  eye_mode   mouth
EXPR = {
    "neutral": (1.00, 0, 0, 1.00, 0, "normal", "soft"),
    "happy":   (0.80, -4, 6, 1.00, 0, "smile", "teeth"),
    "smug":    (0.55, 6, 0, 1.00, 2, "normal", "smirk"),
    "angry":   (0.72, 22, -6, 0.90, 0, "normal", "frown"),
    "sad":     (0.80, -20, 4, 1.00, 6, "normal", "frown"),
    "shocked": (1.35, -4, 24, 0.62, 0, "normal", "o"),
    "scared":  (1.25, -18, 16, 0.62, 2, "normal", "wobble"),
    "sus":     (0.38, 10, -4, 1.00, 0, "normal", "flat"),
    "cry":     (1.00, -22, 6, 1.00, 0, "closed", "frown"),
    "dead":    (1.00, 0, 0, 1.00, 0, "x", "flat"),
    "evil":    (0.62, 26, -4, 0.85, 0, "evil", "grin"),
    "love":    (1.05, -6, 12, 1.00, 0, "heart", "teeth"),
}

EYE_L, EYE_R, EYE_Y = 176, 336, 226


def draw_eye(cv, c, cx, side, open_, pupil, look_y, mode, skin):
    cy = EYE_Y
    rx, ry = 46, 25 * open_
    # rose eyeshadow, soft
    cv.paint(ellipse(cx + side * 6, cy - 16, 62, 26 + 14 * open_, soft=26), c["eyeshadow"], 0.55)
    if mode == "x":
        for s in (-1, 1):
            cv.paint(capsule(cx - 26, cy - 26 * s, cx + 26, cy + 26 * s, 12), c["lashes"])
        return
    if mode == "closed":  # crying: closed lids curving down, lashes, tears
        pts = bezier((cx - 44, cy + 4), (cx, cy - 22), (cx + 44, cy + 4))
        cv.paint(polyline(pts, 9, 9), c["lashes"])
        for k in (0.2, 0.5, 0.8):
            px_, py_ = pts[int(k * (len(pts) - 1))]
            cv.paint(capsule(px_, py_, px_ + side * 8, py_ - 12, 4, 2), c["lashes"])
        tx = cx + side * 6
        cv.paint(capsule(tx, cy + 6, tx + side * 4, 420, 18, 26), (0.35, 0.65, 1.0), 0.85)
        return
    white = ellipse(cx, cy, rx, ry)
    cv.paint(white, (0.97, 0.96, 0.95))
    # iris clipped to the eye white
    ic = (cx, cy + look_y)
    iris_col = c["iris"] if mode != "evil" else hex3("#c4102c")
    if mode == "heart":
        cv.paint(heart(ic[0], ic[1] - 2, 20) * white, hex3("#ff3d6e"))
    else:
        r = 21 * pupil
        cv.paint(ellipse(ic[0], ic[1], r, r) * white, iris_col)
        cv.paint(ring(ic[0], ic[1], r, r, 3) * white, iris_col * 0.45)
        cv.paint(ellipse(ic[0], ic[1], r * 0.45, r * 0.45) * white, (0.02, 0.01, 0.01))
        cv.paint(ellipse(ic[0] + 6, ic[1] - 7, 5.5, 5.5) * white, (1, 1, 1))
        cv.paint(ellipse(ic[0] - 6, ic[1] + 7, 2.5, 2.5) * white, (1, 1, 1), 0.8)
    if mode == "smile":  # cheeks push the lower lid up
        cv.paint(ellipse(cx, cy + ry + 12, 56, 18, soft=3), skin)
    # upper lid line + wing
    top = bezier((cx - rx, cy + 2), (cx, cy - ry * 2.0), (cx + rx, cy + 2))
    if side < 0:
        top = top[::-1]
    cv.paint(polyline(top, 4, 9), c["lashes"])  # thick toward the outer corner
    ox, oy = cx + side * rx, cy + 2
    cv.paint(capsule(ox, oy, ox + side * 18, oy - 14, 8, 2), c["lashes"])
    # lashes fanning from the outer half of the lid
    for k, ln in ((0.55, 12), (0.7, 15), (0.85, 17)):
        px_, py_ = top[int(k * (len(top) - 1))]
        cv.paint(capsule(px_, py_, px_ + side * ln * 0.7, py_ - ln, 4, 1.5), c["lashes"])
    # soft lower lid
    low = bezier((cx - rx * 0.8, cy + ry * 0.6), (cx, cy + ry * 1.25), (cx + rx * 0.9, cy + ry * 0.55))
    cv.paint(polyline(low, 2, 2), c["lashes"], 0.35)


def draw_brow(cv, c, cx, side, tilt, raise_):
    by = EYE_Y - 62 - raise_
    inner = (cx - side * 40, by + 6 + tilt * 0.8)
    peak = (cx + side * 12, by - 12 + tilt * 0.1)
    outer = (cx + side * 56, by + 8 - tilt * 0.3)
    pts = bezier(inner, peak, outer, 16)
    cv.paint(polyline(pts, 19, 7), c["brows"])


def draw_nose(cv, skin):
    shade = skin * 0.8
    cv.paint(ellipse(256, 304, 30, 18, soft=14), shade, 0.6)
    for x in (240, 272):
        cv.paint(ellipse(x, 310, 8, 4.5, soft=3), skin * 0.55, 0.9)
    cv.paint(ellipse(256, 282, 6, 12, soft=8), (1, 1, 1), 0.25)


def draw_mouth(cv, c, kind, open_):
    cx, cy = 256, 372
    lips, dark, teeth = c["lips"], c["mouth"], c["teeth"]
    if kind in ("teeth", "grin"):
        w = 82 if kind == "teeth" else 94
        h = (40 if open_ else 30) + (6 if kind == "grin" else 0)
        top = cy - 8
        inside = ellipse(cx, top, w, h + 6) * (_YY >= top)
        cv.paint(ellipse(cx, top - 2, w + 10, h + 16) * (_YY >= top - 10), lips)     # lower lip
        cv.paint(ellipse(cx, top + 2, w + 8, 12), lips)                               # upper lip
        cv.paint(inside, dark)
        cv.paint(inside * (_YY <= top + h * 0.48), teeth)                              # top teeth
        if kind == "grin" or open_:
            cv.paint(inside * (_YY >= top + h * 0.85), teeth * 0.95)                  # bottom teeth
        cv.paint(ellipse(cx + 18, top + h + 9, 22, 4, soft=4), (1, 1, 1), 0.55)       # gloss
        return
    if kind == "o":
        r = 30 if open_ else 24
        cv.paint(ellipse(cx, cy + 4, r + 10, r + 16), lips)
        cv.paint(ellipse(cx, cy + 4, r, r + 6), dark)
        cv.paint(ellipse(cx + 10, cy + r + 14, 10, 3, soft=3), (1, 1, 1), 0.5)
        return
    if open_:  # generic talking mouth for the other shapes
        cv.paint(ellipse(cx, cy + 2, 46, 30), lips)
        cv.paint(ellipse(cx, cy + 2, 36, 20), dark)
        cv.paint(ellipse(cx, cy - 8, 32, 8) * ellipse(cx, cy + 2, 36, 20), teeth)
        return
    # closed shapes: two full lips with a parting line
    if kind == "soft":
        line = bezier((cx - 50, cy - 4), (cx, cy + 12), (cx + 50, cy - 4))
    elif kind == "frown":
        line = bezier((cx - 44, cy + 10), (cx, cy - 8), (cx + 44, cy + 10))
    elif kind == "smirk":
        line = bezier((cx - 40, cy + 6), (cx + 10, cy + 8), (cx + 50, cy - 12))
    elif kind == "wobble":
        line = [(cx - 48 + i * 12, cy + (6 if i % 2 else -4)) for i in range(9)]
    else:  # flat
        line = [(cx - 38, cy), (cx + 38, cy)]
    lip = np.zeros((N, N), np.float32)
    for (x, y) in line:
        lip = np.maximum(lip, ellipse(x, y, 16, 15))
    cv.paint(lip, lips)
    cv.paint(polyline(line, 5, 5), lips * 0.55)
    mx = line[len(line) // 2][0]
    my = line[len(line) // 2][1]
    cv.paint(ellipse(mx + 14, my + 11, 14, 3, soft=3), (1, 1, 1), 0.5)


def draw_face_detailed(expr, mouth_open, skin_lin, opts):
    c = {k: hex3(v) for k, v in {
        "iris": "#4a2716", "lashes": "#170c0a", "brows": "#4a2a1c", "eyeshadow": "#e0727f",
        "lips": "#e3a1a6", "blush": "#ff8c8c", "teeth": "#fbfaf6", "mouth": "#5b1d22"}.items()}
    c.update({k: hex3(v) for k, v in opts.items() if isinstance(v, str) and v.startswith("#")})
    skin = np.asarray(skin_lin[:3], np.float32)
    open_, tilt, raise_, pupil, look_y, mode, mouth = EXPR[expr]
    cv = Canvas(skin)
    for cx in (EYE_L - 26, EYE_R + 26):  # blush
        cv.paint(ellipse(cx, 304, 50, 24, soft=40), c["blush"], 0.5)
    draw_nose(cv, skin)
    if opts.get("birthmark"):  # small dark mark high on the right cheek (viewer's left)
        cv.paint(ellipse(EYE_L - 30, 318, 15, 13, soft=3), c.get("birthmark", hex3("#4a2414")), 0.95)
    for cx, side in ((EYE_L, -1), (EYE_R, 1)):
        draw_eye(cv, c, cx, side, open_, pupil, look_y, mode, skin)
        if expr == "smug" and side > 0:
            draw_brow(cv, c, cx, side, -6, 14)
        else:
            draw_brow(cv, c, cx, side, tilt, raise_)
    talk = mouth_open or mouth == "o" and expr == "shocked"
    draw_mouth(cv, c, mouth, bool(mouth_open))
    return np.concatenate([cv.px, np.ones((N, N, 1), np.float32)], -1)
