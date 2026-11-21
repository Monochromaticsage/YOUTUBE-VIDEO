"""2D pop-up stickers laid over the 3D frames (emoji, words, impact bursts) and the end sting.

A shot can carry:  "fx": [{"e": "🍋", "at": 0.3, "x": 0.72, "y": 0.42, "size": 300, "dur": 1.0}]
or a word:         {"text": "LEMON!", "color": "#ffe03a", "size": 150, "x": 0.5, "y": 0.62, "anim": "shake"}
anims: pop (default: overshoot then gentle bob), shake, rise (floats up), spin.
Each sticker becomes a short PNG sequence that assemble.py overlays at the right moment.
"""
import math
import os

from PIL import Image, ImageDraw, ImageFont

FPS = 30
FONT = "/usr/share/fonts/opentype/inter/InterDisplay-Black.otf"
EMOJI = "/usr/share/fonts/truetype/noto/NotoColorEmoji.ttf"


def _emoji(chars, size):
    """Noto Color Emoji only renders at 109 px; draw there and scale."""
    f = ImageFont.truetype(EMOJI, 109)
    tiles = []
    for ch in _split_emoji(chars):
        im = Image.new("RGBA", (160, 140), (0, 0, 0, 0))
        ImageDraw.Draw(im).text((4, 4), ch, font=f, embedded_color=True)
        bb = im.getbbox()
        if bb:
            tiles.append(im.crop(bb))
    if not tiles:
        return Image.new("RGBA", (size, size), (0, 0, 0, 0))
    h = max(t.height for t in tiles)
    row = Image.new("RGBA", (sum(t.width for t in tiles) + 10 * (len(tiles) - 1), h), (0, 0, 0, 0))
    x = 0
    for t in tiles:
        row.alpha_composite(t, (x, (h - t.height) // 2))
        x += t.width + 10
    return row.resize((max(1, int(row.width * size / h)), size), Image.LANCZOS)


def _split_emoji(s):
    out, cur = [], ""
    for ch in s:
        if cur and ord(ch) not in (0xFE0F, 0x200D) and not (cur.endswith("‍")):
            out.append(cur)
            cur = ""
        cur += ch
    if cur:
        out.append(cur)
    return [c for c in out if c.strip()]


def _word(text, size, color):
    f = ImageFont.truetype(FONT, size)
    d = ImageDraw.Draw(Image.new("RGBA", (1, 1)))
    l, t, r, b = d.textbbox((0, 0), text, font=f, stroke_width=size // 9)
    im = Image.new("RGBA", (r - l + 20, b - t + 24), (0, 0, 0, 0))
    dd = ImageDraw.Draw(im)
    dd.text((10 - l + 5, 12 - t + 7), text, font=f, fill=(0, 0, 0, 160), stroke_width=size // 9, stroke_fill=(0, 0, 0, 160))
    dd.text((10 - l, 12 - t), text, font=f, fill=color, stroke_width=size // 9, stroke_fill=(15, 15, 25))
    return im


def _phone(msg, sender, size):
    """A phone with one chat bubble (e.g. a text from Grandpa). size = phone height in px."""
    import textwrap
    W, H = int(size * 0.52), size
    im = Image.new("RGBA", (W + 20, H + 20), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    d.rounded_rectangle([10, 10, W + 10, H + 10], radius=W // 7, fill=(25, 25, 32), outline=(80, 80, 95), width=6)
    d.rounded_rectangle([24, 24, W - 4, H - 4], radius=W // 9, fill=(240, 244, 250))
    hf = ImageFont.truetype(FONT, max(14, W // 11))
    d.text((W // 2 + 10, 60), sender, font=hf, fill=(30, 30, 40), anchor="mm")
    bf = ImageFont.truetype(FONT, max(12, W // 13))
    lines = textwrap.wrap(msg, width=16)
    lh = int(bf.size * 1.25)
    bh = lh * len(lines) + 30
    top = 110
    d.rounded_rectangle([36, top, W - 20, top + bh], radius=24, fill=(229, 229, 234))
    for k, ln in enumerate(lines):
        d.text((52, top + 15 + k * lh), ln, font=bf, fill=(20, 20, 25))
    return im


def _burst(size, color="#ffffff"):
    """Comic impact star behind a sticker."""
    im = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    c = size / 2
    pts = []
    for i in range(24):
        r = c * (0.98 if i % 2 == 0 else 0.62)
        a = i * math.pi / 12
        pts.append((c + r * math.cos(a), c + r * math.sin(a)))
    d.polygon(pts, fill=color, outline=(20, 20, 20), width=max(3, size // 60))
    return im


def _base(fx):
    size = int(fx.get("size", 260))
    if "img" in fx:  # a picture (e.g. an old photo) from assets/, scaled to `size` px tall, optional tilt
        root = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "assets"))
        img = Image.open(os.path.join(root, fx["img"])).convert("RGBA")
        img = img.resize((max(1, int(img.width * size / img.height)), size), Image.LANCZOS)
        if fx.get("tilt"):
            img = img.rotate(fx["tilt"], resample=Image.BICUBIC, expand=True)
    elif "phone" in fx:
        img = _phone(fx["phone"], fx.get("sender", "Grandpa"), size)
    elif "text" in fx:
        img = _word(fx["text"], size, fx.get("color", "#ffffff"))
    else:
        img = _emoji(fx.get("e", "💥"), size)
    if fx.get("burst"):
        b = _burst(int(max(img.width, img.height) * 1.5), fx["burst"] if isinstance(fx["burst"], str) else "#ffe03a")
        b.alpha_composite(img, ((b.width - img.width) // 2, (b.height - img.height) // 2))
        img = b
    return img


def render_sticker(fx, out_dir, W, H):
    os.makedirs(out_dir, exist_ok=True)
    for p in os.listdir(out_dir):
        os.remove(os.path.join(out_dir, p))
    img = _base(fx)
    dur = float(fx.get("dur", 1.0))
    n = max(2, int(dur * FPS))
    anim = fx.get("anim", "pop")
    pad = 1.35
    cw, ch = int(img.width * pad) + 40, int(img.height * pad) + (200 if anim == "rise" else 40)
    for i in range(n):
        t = i / FPS
        k = min(1.0, t / 0.18)
        scale = (k * 1.25) if k < 0.7 else 1.25 - 0.25 * (k - 0.7) / 0.3
        scale *= 1 + 0.03 * math.sin(t * 9)
        rot, dx, dy = 0.0, 0, 0
        if anim == "shake":
            dx = int(10 * math.sin(t * 55)) if t < 0.5 else 0
            rot = 6 * math.sin(t * 40) if t < 0.5 else 0
        elif anim == "rise":
            dy = -int(140 * t / dur)
        elif anim == "spin":
            rot = -360 * min(1.0, t / 0.3)
        alpha = 1.0 if t < dur - 0.15 else max(0.0, (dur - t) / 0.15)
        frame = Image.new("RGBA", (cw, ch), (0, 0, 0, 0))
        if scale > 0.02:
            s = img.resize((max(1, int(img.width * scale)), max(1, int(img.height * scale))), Image.LANCZOS)
            if rot:
                s = s.rotate(rot, resample=Image.BICUBIC, expand=True)
            if alpha < 1:
                s.putalpha(s.getchannel("A").point(lambda v: int(v * alpha)))
            frame.alpha_composite(s, ((cw - s.width) // 2 + dx, (ch - s.height) // 2 + dy))
        frame.save(os.path.join(out_dir, f"f_{i:03d}.png"))


def render_sting(out_dir, W, H, text="PLUTONEX!"):
    """Our signature end sting: a sunburst with the channel name slamming in."""
    os.makedirs(out_dir, exist_ok=True)
    for p in os.listdir(out_dir):
        os.remove(os.path.join(out_dir, p))
    size = int(W * 0.95)
    word = _word(text, int(W * 0.13), "#ffd23f")
    n = int(1.1 * FPS)
    for i in range(n):
        t = i / FPS
        frame = Image.new("RGBA", (size, size), (0, 0, 0, 0))
        k = min(1.0, t / 0.2)
        rays = Image.new("RGBA", (size, size), (0, 0, 0, 0))
        d = ImageDraw.Draw(rays)
        c = size / 2
        for r in range(16):
            a0 = math.radians(r * 22.5 + t * 90)
            a1 = a0 + math.radians(11)
            rr = c * k
            d.polygon([(c, c), (c + rr * math.cos(a0), c + rr * math.sin(a0)), (c + rr * math.cos(a1), c + rr * math.sin(a1))],
                      fill=(124, 58, 237, 230) if r % 2 else (255, 255, 255, 230))
        frame.alpha_composite(rays)
        sc = (k * 1.3) if k < 0.7 else 1.3 - 0.3 * (k - 0.7) / 0.3
        if sc > 0.02:
            w = word.resize((max(1, int(word.width * sc)), max(1, int(word.height * sc))), Image.LANCZOS)
            w = w.rotate(-6 * (1 - k), resample=Image.BICUBIC, expand=True)
            frame.alpha_composite(w, ((size - w.width) // 2, (size - w.height) // 2))
        frame.save(os.path.join(out_dir, f"f_{i:03d}.png"))
