"""Age-counter badges and comment pops for S12 'Every comment makes Grandpa younger'."""
import os
import sys

from PIL import Image, ImageDraw, ImageFont

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.join(ROOT, "pipeline"))
import fx  # noqa: E402

OUT = os.path.join(ROOT, "assets", "textures", "s12")
BLACK = os.path.join(ROOT, "assets", "fonts", "InterDisplay-Black.otf")
os.makedirs(OUT, exist_ok=True)


def badge(age):
    W, H = 520, 190
    im = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    col = (255, 255, 255) if age > 0 else (255, 80, 80)
    d.rounded_rectangle([6, 6, W - 6, H - 6], 60, fill=(25, 22, 40, 235), outline=(255, 210, 63), width=8)
    d.text((140, H / 2), "AGE", font=ImageFont.truetype(BLACK, 56), fill=(255, 210, 63), anchor="mm")
    d.text((350, H / 2 + 4), str(age), font=ImageFont.truetype(BLACK, 120), fill=col, anchor="mm")
    im.save(os.path.join(OUT, f"age_{age}.png"))


for a in [82, 81, 80, 79, 78, 61, 60, 41, 40, 17, 16, 11, 10, 6, 5, 2, 1, 0]:
    badge(a)

pop = Image.new("RGBA", (330, 160), (0, 0, 0, 0))
d = ImageDraw.Draw(pop)
d.rounded_rectangle([4, 4, 326, 156], 50, fill=(255, 255, 255, 245), outline=(30, 30, 40), width=6)
e = fx._emoji("💬", 90)
pop.alpha_composite(e, (30, 35))
d.text((230, 80), "+1", font=ImageFont.truetype(BLACK, 90), fill=(30, 150, 60), anchor="mm")
pop.save(os.path.join(OUT, "comment_pop.png"))
print("ok")
