"""Test-paper images used as stickers in S07 (sneeze loop): an F paper, an A+ paper and a fanned stack of A+ papers."""
import os
import random

from PIL import Image, ImageDraw, ImageFont

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
OUT = os.path.join(ROOT, "assets", "textures")
BLACK = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "assets", "fonts", "InterDisplay-Black.otf")
BOLD = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "assets", "fonts", "InterDisplay-Bold.otf")


def paper(grade, good, name="SAGE", seed=1):
    rnd = random.Random(seed)
    W, H = 700, 900
    im = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    d.rounded_rectangle([6, 6, W - 6, H - 6], 18, fill=(252, 251, 245), outline=(40, 40, 50), width=6)
    for y in range(170, H - 40, 52):
        d.line([(40, y), (W - 40, y)], fill=(170, 200, 235), width=3)
    d.line([(90, 20), (90, H - 20)], fill=(240, 150, 150), width=3)
    f = ImageFont.truetype(BOLD, 40)
    d.text((110, 50), f"MATH TEST   name: {name}", font=f, fill=(40, 40, 60))
    sf = ImageFont.truetype(BOLD, 34)
    for i, y in enumerate(range(200, H - 120, 104)):
        a, b = rnd.randint(2, 9), rnd.randint(2, 9)
        d.text((110, y), f"{i + 1})  {a} x {b} = {a * b if good else a * b + rnd.choice([-3, 2, 5])}", font=sf,
               fill=(50, 50, 70))
        mx, my = W - 150, y + 18
        if good:
            d.line([(mx, my), (mx + 20, my + 22), (mx + 55, my - 22)], fill=(30, 170, 70), width=10)
        else:
            d.line([(mx, my - 20), (mx + 40, my + 20)], fill=(225, 30, 40), width=10)
            d.line([(mx + 40, my - 20), (mx, my + 20)], fill=(225, 30, 40), width=10)
    gf = ImageFont.truetype(BLACK, 230)
    col = (30, 170, 70) if good else (225, 30, 40)
    d.ellipse([W - 330, H - 340, W - 40, H - 50], outline=col, width=14)
    d.text((W - 185, H - 200), grade, font=gf, fill=col, anchor="mm")
    return im


os.makedirs(OUT, exist_ok=True)
paper("F", False).save(os.path.join(OUT, "test_f.png"))
paper("A+", True).save(os.path.join(OUT, "test_aplus.png"))
stack = Image.new("RGBA", (1300, 1200), (0, 0, 0, 0))
for i, rot in enumerate((14, -10, 4)):
    p = paper("A+", True, "GOLDIE", seed=i + 3).rotate(rot, resample=Image.BICUBIC, expand=True)
    stack.alpha_composite(p, (150 + i * 120 - (p.width - 700) // 2, 80 + i * 30 - (p.height - 900) // 2))
stack.crop(stack.getbbox()).save(os.path.join(OUT, "test_stack.png"))
print("ok")
