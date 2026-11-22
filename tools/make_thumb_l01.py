"""16:9 thumbnail for long-form L01 (compilation of 5 stories), built from the Short thumbnails."""
import os
from PIL import Image, ImageDraw, ImageFont, ImageEnhance

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
B = os.path.join(ROOT, "branding")
F = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "assets", "fonts", "InterDisplay-Black.otf")
W, H = 1280, 720
im = Image.new("RGB", (W, H), (20, 16, 40))
crops = [("s03_taste_lies", 250), ("s05_noob_genius", 160), ("s04_substitute_mom", 220)]
sw = W // 3
for i, (ep, cx_off) in enumerate(crops):
    t = Image.open(os.path.join(B, f"{ep}_thumbnail.png")).convert("RGB")
    cx = t.width // 2 + (cx_off - 220)
    box = (cx - 330, 425, cx + 330, 425 + int(660 * H / sw))
    p = ImageEnhance.Color(t.crop(box)).enhance(1.15).resize((sw + 2, H), Image.LANCZOS)
    im.paste(p, (i * sw, 0))
d = ImageDraw.Draw(im)
for x in (sw, 2 * sw):
    d.line([(x, 0), (x, H)], fill=(255, 210, 63), width=10)
# top band
grad = Image.new("L", (W, H), 0)
g = ImageDraw.Draw(grad)
for y in range(H):
    g.line([(0, y), (W, y)], fill=int(min(250, min(1, max(0, (215 - y) / 70)) * 250 + min(1, max(0, (y - 560) / 70)) * 240)))
im = Image.composite(Image.new("RGB", (W, H), (12, 10, 28)), im, grad)
d = ImageDraw.Draw(im)
def t(xy, s, size, fill):
    f = ImageFont.truetype(F, size)
    d.text((xy[0] + 5, xy[1] + 7), s, font=f, fill=(0, 0, 0), anchor="mm", stroke_width=12, stroke_fill=(0, 0, 0))
    d.text(xy, s, font=f, fill=fill, anchor="mm", stroke_width=10, stroke_fill=(10, 12, 25))
t((W / 2, 95), "5 CRAZIEST FAMILY STORIES", 84, (255, 255, 255))
t((W / 2, 640), "WAIT FOR #3...", 92, (255, 210, 63))
out = os.path.join(B, "l01_compilation_5_stories_thumbnail")
im.save(out + ".png"); im.save(out + ".jpg", quality=92); print("wrote", out)
