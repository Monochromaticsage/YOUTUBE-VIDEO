"""Notebook-page crayon sketches and a realistic-looking $1 bill for S11 'Whatever I Draw Becomes REAL'."""
import math
import os
import random

from PIL import Image, ImageDraw, ImageFilter, ImageFont

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
OUT = os.path.join(ROOT, "assets", "textures", "s11")
BOLD = os.path.join(ROOT, "assets", "fonts", "InterDisplay-Bold.otf")
BLACK = os.path.join(ROOT, "assets", "fonts", "InterDisplay-Black.otf")
INK = (45, 45, 60)
W, H = 900, 760
SS = 2  # supersample for smooth lines


def page():
    im = Image.new("RGBA", (W * SS, H * SS), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    d.rounded_rectangle([0, 0, W * SS - 1, H * SS - 1], 24 * SS, fill=(253, 252, 246), outline=(70, 70, 80), width=6 * SS)
    for y in range(110, H - 30, 56):
        d.line([(30 * SS, y * SS), ((W - 30) * SS, y * SS)], fill=(185, 210, 240), width=3 * SS)
    d.line([(110 * SS, 10 * SS), (110 * SS, (H - 10) * SS)], fill=(240, 160, 160), width=3 * SS)
    for y in range(60, H - 40, 90):
        d.ellipse([22 * SS, y * SS, 48 * SS, (y + 26) * SS], fill=(225, 225, 230), outline=(90, 90, 100), width=3 * SS)
    return im, d


def P(pts):
    return [(x * SS, y * SS) for x, y in pts]


def crayon_fill(im, pts, color, seed=1):
    """Kid-style crayon colouring: a soft fill plus diagonal strokes."""
    mask = Image.new("L", im.size, 0)
    ImageDraw.Draw(mask).polygon(P(pts), fill=255)
    layer = Image.new("RGBA", im.size, color + (150,))
    strokes = Image.new("L", im.size, 0)
    sd = ImageDraw.Draw(strokes)
    rnd = random.Random(seed)
    for k in range(-H, W, 9):
        sd.line([(k * SS, 0), ((k + H) * SS, H * SS)], fill=rnd.randint(60, 140), width=4 * SS)
    a = Image.composite(strokes, Image.new("L", im.size, 0), mask)
    layer.putalpha(Image.eval(Image.merge("L", [a]), lambda v: min(255, v + 90)).point(lambda v: v if v > 90 else 0))
    im.alpha_composite(layer)


def outline(d, pts, closed=True, w=8, seed=1):
    rnd = random.Random(seed)
    pts = list(pts) + ([pts[0]] if closed else [])
    out = []
    for (x0, y0), (x1, y1) in zip(pts, pts[1:]):
        for k in range(8):
            t = k / 8
            out.append((x0 + (x1 - x0) * t + rnd.uniform(-1.2, 1.2), y0 + (y1 - y0) * t + rnd.uniform(-1.2, 1.2)))
    out.append(pts[-1])
    d.line(P(out), fill=INK, width=w * SS, joint="curve")


def circ(cx, cy, r, n=28):
    return [(cx + r * math.cos(2 * math.pi * k / n), cy + r * math.sin(2 * math.pi * k / n)) for k in range(n)]


def save(im, name):
    os.makedirs(OUT, exist_ok=True)
    im = im.resize((im.width // SS, im.height // SS), Image.LANCZOS)
    im.save(os.path.join(OUT, name + ".png"))


im, d = page()
save(im, "page_blank")

# pizza slice
im, d = page()
tri = [(300, 200), (700, 360), (320, 620)]
crayon_fill(im, tri, (255, 200, 60), 3)
crust = [(290, 190), (330, 205), (345, 630), (305, 640)]
crayon_fill(im, crust, (205, 140, 70), 4)
d = ImageDraw.Draw(im)
outline(d, tri, seed=3)
for (x, y) in [(400, 330), (500, 420), (400, 510), (560, 370)]:
    crayon_fill(im, circ(x, y, 32), (200, 40, 40), x)
    d = ImageDraw.Draw(im)
    outline(d, circ(x, y, 32), w=6, seed=x)
save(im, "draw_pizza")

# car (with square wheels)
im, d = page()
body = [(190, 470), (190, 380), (320, 370), (390, 270), (570, 270), (630, 370), (750, 385), (750, 470)]
crayon_fill(im, body, (230, 50, 50), 5)
win = [(410, 300), (550, 300), (590, 365), (370, 365)]
crayon_fill(im, win, (130, 190, 240), 6)
d = ImageDraw.Draw(im)
outline(d, body, seed=5)
outline(d, win, w=6, seed=6)
for x in (240, 590):
    sq = [(x, 440), (x + 110, 440), (x + 110, 550), (x, 550)]
    crayon_fill(im, sq, (50, 50, 60), x)
    d = ImageDraw.Draw(im)
    outline(d, sq, seed=x)
crayon_fill(im, circ(735, 415, 16), (255, 230, 90), 7)
save(im, "draw_car")

# money: a bill with "$1" (the zeros forgotten)
im, d = page()
bill = [(180, 250), (730, 250), (730, 520), (180, 520)]
crayon_fill(im, bill, (120, 190, 110), 8)
d = ImageDraw.Draw(im)
outline(d, bill, seed=8)
outline(d, circ(455, 385, 80), w=6, seed=9)
d.text((455 * SS, 388 * SS), "$1", font=ImageFont.truetype(BLACK, 110 * SS), fill=INK, anchor="mm")
save(im, "draw_money")

# "puppy" (it's a potato with legs)
im, d = page()
blob = circ(450, 380, 150)
crayon_fill(im, blob, (200, 160, 100), 11)
d = ImageDraw.Draw(im)
outline(d, blob, seed=11)
for x in (360, 420, 480, 540):
    outline(d, [(x, 505), (x - 4, 600)], closed=False, seed=x)
for x in (515, 570):
    crayon_fill(im, circ(x, 340, 16), (255, 255, 255), x)
    d = ImageDraw.Draw(im)
    outline(d, circ(x, 340, 16), w=5, seed=x)
    d.ellipse(P([(x - 6, 334), (x + 6, 346)]), fill=INK)
outline(d, [(300, 360), (240, 320)], closed=False, seed=14)
d.text((450 * SS, 680 * SS), "puppy?", font=ImageFont.truetype(BOLD, 52 * SS), fill=INK, anchor="mm")
save(im, "draw_puppy")

# golden pencil
im, d = page()
body = [(250, 520), (620, 270), (680, 330), (310, 580)]
crayon_fill(im, body, (255, 205, 40), 21)
tip = [(250, 520), (200, 620), (310, 580)]
crayon_fill(im, tip, (240, 200, 160), 22)
d = ImageDraw.Draw(im)
outline(d, body, seed=21)
outline(d, tip, seed=22)
for (x, y) in [(700, 220), (745, 300), (650, 185)]:
    outline(d, [(x - 20, y), (x + 20, y)], closed=False, w=6, seed=x)
    outline(d, [(x, y - 20), (x, y + 20)], closed=False, w=6, seed=y)
save(im, "draw_pencil")

# realistic-looking (stylized) one-dollar bill
BW, BH = 1200, 510
b = Image.new("RGBA", (BW, BH), (0, 0, 0, 0))
d = ImageDraw.Draw(b)
paper, ink, light = (214, 222, 200), (34, 84, 52), (188, 204, 176)
d.rounded_rectangle([0, 0, BW - 1, BH - 1], 18, fill=paper)
for x in range(0, BW, 6):  # fine guilloche-ish lines
    d.line([(x, 0), (x + 40, BH)], fill=(206, 216, 192), width=1)
d.rounded_rectangle([14, 14, BW - 15, BH - 15], 12, outline=ink, width=10)
d.rounded_rectangle([34, 34, BW - 35, BH - 35], 10, outline=ink, width=3)
fT = ImageFont.truetype(BOLD, 40)
d.text((BW / 2, 74), "THE UNITED STATES OF AMERICA", font=fT, fill=ink, anchor="mm")
d.text((BW / 2, BH - 74), "ONE  DOLLAR", font=ImageFont.truetype(BLACK, 52), fill=ink, anchor="mm")
# portrait oval with a generic bust
d.ellipse([BW / 2 - 130, 120, BW / 2 + 130, 400], fill=light, outline=ink, width=6)
d.ellipse([BW / 2 - 52, 170, BW / 2 + 52, 290], fill=(120, 150, 120))
d.chord([BW / 2 - 110, 270, BW / 2 + 110, 470], 180, 360, fill=(120, 150, 120))
# seals and corner numbers
d.ellipse([170, 170, 330, 330], outline=ink, width=6)
d.text((250, 250), "1", font=ImageFont.truetype(BLACK, 90), fill=ink, anchor="mm")
d.ellipse([BW - 330, 180, BW - 190, 320], fill=(60, 120, 80), outline=ink, width=4)
d.text((BW - 260, 250), "$", font=ImageFont.truetype(BLACK, 80), fill=paper, anchor="mm")
for (x, y) in [(90, 100), (BW - 90, 100), (90, BH - 100), (BW - 90, BH - 100)]:
    d.text((x, y), "1", font=ImageFont.truetype(BLACK, 80), fill=ink, anchor="mm")
d.text((300, 400), "A 01234567 B", font=ImageFont.truetype(BOLD, 30), fill=(40, 110, 70), anchor="mm")
b = b.filter(ImageFilter.SMOOTH)
b.save(os.path.join(OUT, "dollar.png"))
print("ok")
