"""Notebook-page sketches and the $1 bill for S11 'Whatever I Draw Becomes REAL'."""
import math
import os
import random

from PIL import Image, ImageDraw, ImageFont

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
OUT = os.path.join(ROOT, "assets", "textures", "s11")
BOLD = os.path.join(ROOT, "assets", "fonts", "InterDisplay-Bold.otf")
BLACK = os.path.join(ROOT, "assets", "fonts", "InterDisplay-Black.otf")
INK = (55, 55, 75)
W, H = 900, 760


def page():
    im = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    d.rounded_rectangle([0, 0, W - 1, H - 1], 24, fill=(253, 252, 246), outline=(70, 70, 80), width=6)
    for y in range(110, H - 30, 56):
        d.line([(30, y), (W - 30, y)], fill=(175, 205, 240), width=3)
    d.line([(110, 10), (110, H - 10)], fill=(240, 150, 150), width=3)
    for y in range(60, H - 40, 90):  # spiral holes
        d.ellipse([22, y, 48, y + 26], fill=(220, 220, 225), outline=(90, 90, 100), width=3)
    return im, d


def wob(d, pts, w=9, closed=False, seed=1):
    """A wobbly hand-drawn pencil line."""
    rnd = random.Random(seed)
    pts = list(pts) + ([pts[0]] if closed else [])
    out = []
    for (x0, y0), (x1, y1) in zip(pts, pts[1:]):
        for k in range(12):
            t = k / 12
            out.append((x0 + (x1 - x0) * t + rnd.uniform(-3, 3), y0 + (y1 - y0) * t + rnd.uniform(-3, 3)))
    out.append(pts[-1])
    d.line(out, fill=INK, width=w, joint="curve")


def circle(d, cx, cy, r, w=8, seed=2):
    pts = [(cx + r * math.cos(a / 20 * 2 * math.pi), cy + r * math.sin(a / 20 * 2 * math.pi)) for a in range(20)]
    wob(d, pts, w, closed=True, seed=seed)


def save(im, name):
    os.makedirs(OUT, exist_ok=True)
    im.save(os.path.join(OUT, name + ".png"))


# blank page for the notebook prop
im, d = page()
save(im, "page_blank")

# pizza: a triangle with dots
im, d = page()
wob(d, [(300, 200), (700, 330), (330, 620)], closed=True, seed=3)
for (x, y) in [(400, 330), (500, 420), (390, 500), (560, 350)]:
    circle(d, x, y, 28, seed=x)
save(im, "draw_pizza")

# car with square wheels
im, d = page()
wob(d, [(200, 470), (200, 360), (330, 360), (390, 260), (560, 260), (620, 360), (740, 360), (740, 470)], closed=True, seed=5)
for x in (250, 600):
    wob(d, [(x, 450), (x + 110, 450), (x + 110, 560), (x, 560)], closed=True, seed=x)
wob(d, [(420, 290), (530, 290), (560, 350), (400, 350)], closed=True, w=6, seed=9)
save(im, "draw_car")

# money: "$1" with the zeros missing
im, d = page()
d.rounded_rectangle([200, 250, 720, 520], 20, outline=INK, width=9)
d.text((460, 385), "$1", font=ImageFont.truetype(BLACK, 190), fill=INK, anchor="mm")
d.text((640, 600), "...", font=ImageFont.truetype(BOLD, 70), fill=(150, 150, 160), anchor="mm")
save(im, "draw_money")

# "puppy": basically a potato with legs
im, d = page()
circle(d, 450, 380, 150, seed=11)
for x in (360, 420, 480, 540):
    wob(d, [(x, 500), (x - 5, 600)], seed=x)
circle(d, 520, 340, 14, seed=12)
circle(d, 570, 340, 14, seed=13)
wob(d, [(300, 360), (240, 320)], seed=14)
d.text((450, 680), "puppy?", font=ImageFont.truetype(BOLD, 52), fill=INK, anchor="mm")
save(im, "draw_puppy")

# pencil
im, d = page()
wob(d, [(250, 520), (620, 270), (680, 330), (310, 580)], closed=True, seed=21)
wob(d, [(250, 520), (200, 620), (310, 580)], seed=22)
for (x, y) in [(700, 220), (740, 300), (650, 190)]:
    wob(d, [(x - 18, y), (x + 18, y)], w=6, seed=x)
    wob(d, [(x, y - 18), (x, y + 18)], w=6, seed=y)
save(im, "draw_pencil")

# $1 bill
b = Image.new("RGBA", (760, 340), (0, 0, 0, 0))
d = ImageDraw.Draw(b)
d.rounded_rectangle([0, 0, 759, 339], 22, fill=(196, 226, 178), outline=(60, 110, 60), width=10)
d.rounded_rectangle([30, 30, 729, 309], 14, outline=(90, 140, 90), width=5)
d.ellipse([290, 80, 470, 260], fill=(170, 210, 150), outline=(60, 110, 60), width=6)
d.text((380, 170), "1", font=ImageFont.truetype(BLACK, 130), fill=(50, 100, 50), anchor="mm")
for x in (90, 670):
    d.text((x, 80), "1", font=ImageFont.truetype(BLACK, 70), fill=(50, 100, 50), anchor="mm")
    d.text((x, 260), "1", font=ImageFont.truetype(BLACK, 70), fill=(50, 100, 50), anchor="mm")
save(b, "dollar")
print("ok")
