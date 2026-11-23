"""Images for S14 'My little sister can UNDO anything': phone screens, wall scribble, tally sheets, rewind overlay."""
import math
import os
import random

from PIL import Image, ImageDraw, ImageFont

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
OUT = os.path.join(ROOT, "assets", "textures", "s14")
BLACK = os.path.join(ROOT, "assets", "fonts", "InterDisplay-Black.otf")
BOLD = os.path.join(ROOT, "assets", "fonts", "InterDisplay-Bold.otf")
os.makedirs(OUT, exist_ok=True)

# phone screens (portrait)
for cracked in (False, True):
    im = Image.new("RGB", (300, 560), (40, 90, 200))
    d = ImageDraw.Draw(im)
    for y in range(560):
        d.line([(0, y), (300, y)], fill=(60 + y // 8, 90 + y // 10, 210))
    d.text((150, 120), "9:41", font=ImageFont.truetype(BOLD, 70), fill=(255, 255, 255), anchor="mm")
    for i in range(8):
        x, y = 50 + (i % 4) * 66, 260 + (i // 4) * 80
        d.rounded_rectangle([x - 22, y - 22, x + 22, y + 22], 10, fill=[(255, 200, 60), (90, 220, 120), (255, 120, 150), (120, 200, 255)][i % 4])
    if cracked:
        rnd = random.Random(4)
        cx, cy = 190, 330
        for k in range(14):
            a = rnd.uniform(0, 2 * math.pi)
            pts = [(cx, cy)]
            r = 0
            for s in range(5):
                r += rnd.uniform(40, 90)
                a += rnd.uniform(-0.4, 0.4)
                pts.append((cx + r * math.cos(a), cy + r * math.sin(a)))
            d.line(pts, fill=(245, 245, 255), width=4)
        d.ellipse([cx - 20, cy - 20, cx + 20, cy + 20], fill=(230, 230, 240))
    im.save(os.path.join(OUT, "phone_cracked.png" if cracked else "phone_ok.png"))

# crayon scribble on the wall
im = Image.new("RGBA", (900, 600), (0, 0, 0, 0))
d = ImageDraw.Draw(im)
rnd = random.Random(7)
for col in [(230, 40, 60), (40, 120, 230), (40, 180, 80), (250, 170, 30)]:
    pts = [(rnd.randint(60, 840), rnd.randint(60, 540)) for _ in range(9)]
    d.line(pts, fill=col, width=18, joint="curve")
d.text((450, 300), "PIP WAS HERE", font=ImageFont.truetype(BLACK, 90), fill=(160, 40, 200), anchor="mm")
im.save(os.path.join(OUT, "scribble.png"))


def tally(n, name, W=900, H=640):
    im = Image.new("RGB", (W, H), (255, 252, 240))
    d = ImageDraw.Draw(im)
    rnd = random.Random(n)
    x, y = 50, 60
    for g in range(n // 5 + (1 if n % 5 else 0)):
        k = min(5, n - g * 5)
        for i in range(min(k, 4)):
            d.line([(x + i * 22, y + rnd.randint(-3, 3)), (x + i * 22 + rnd.randint(-4, 4), y + 90)], fill=(40, 40, 60), width=8)
        if k == 5:
            d.line([(x - 10, y + 80), (x + 80, y + 10)], fill=(200, 40, 50), width=8)
        x += 130
        if x > W - 120:
            x, y = 50, y + 140
    d.text((W - 40, H - 40), f"DAY {n}", font=ImageFont.truetype(BLACK, 70), fill=(200, 40, 50), anchor="rs")
    im.save(os.path.join(OUT, name))


tally(47, "tally_47.png")
tally(48, "tally_48.png")
tally(47, "note_47.png", 420, 420)

# VHS rewind overlay
W, H = 1080, 1920
im = Image.new("RGBA", (W, H), (0, 0, 0, 0))
d = ImageDraw.Draw(im)
for y in range(0, H, 10):
    d.line([(0, y), (W, y)], fill=(255, 255, 255, 26), width=2)
rnd = random.Random(3)
for _ in range(12):
    y = rnd.randint(0, H)
    d.rectangle([0, y, W, y + rnd.randint(6, 22)], fill=(255, 255, 255, 70))
d.text((W / 2, H * 0.42), "◀◀  UNDO", font=ImageFont.truetype(BLACK, 130), fill=(255, 255, 255, 235), anchor="mm",
       stroke_width=10, stroke_fill=(30, 30, 60, 235))
im.save(os.path.join(OUT, "rewind.png"))
print("ok")
