"""Battery-% badges for S13 'In this world, everyone's battery shows above their head'."""
import os
import sys

from PIL import Image, ImageDraw, ImageFont

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.join(ROOT, "pipeline"))
import fx  # noqa: E402

OUT = os.path.join(ROOT, "assets", "textures", "s13")
BLACK = os.path.join(ROOT, "assets", "fonts", "InterDisplay-Black.otf")
os.makedirs(OUT, exist_ok=True)


def col(p):
    return (60, 200, 90) if p > 50 else (255, 200, 40) if p > 15 else (235, 50, 50)


def battery(p, name=None, label=None, bolt=False):
    W, H = 460, 170
    im = Image.new("RGBA", (W, H + (60 if label else 0)), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    x0, y0, x1, y1 = 10, 20, 300, 150
    d.rounded_rectangle([x0, y0, x1, y1], 26, fill=(255, 255, 255, 240), outline=(25, 25, 35), width=10)
    d.rounded_rectangle([x1 + 2, 62, x1 + 26, 108], 8, fill=(25, 25, 35))
    fw = max(14, int((x1 - x0 - 28) * p / 100))
    d.rounded_rectangle([x0 + 14, y0 + 14, x0 + 14 + fw, y1 - 14], 14, fill=col(p))
    if bolt:
        e = fx._emoji("⚡", 90)
        im.alpha_composite(e, (int((x0 + x1) / 2 - e.width / 2), int((y0 + y1) / 2 - e.height / 2)))
    d.text((390, 85), f"{p}%", font=ImageFont.truetype(BLACK, 72 if p < 100 else 60), fill=(255, 255, 255), anchor="mm",
           stroke_width=8, stroke_fill=(25, 25, 35))
    if label:
        d.text((W / 2, H + 28), label, font=ImageFont.truetype(BLACK, 50), fill=(235, 50, 50), anchor="mm",
               stroke_width=6, stroke_fill=(255, 255, 255))
    im.save(os.path.join(OUT, (name or f"bat_{p}") + ".png"))


for p in (100, 90, 80, 60, 50, 40, 30, 20, 10, 3, 2, 1):
    battery(p)
battery(1, "bat_low", label="LOW BATTERY")
battery(2, "bat_2_dim")
battery(100, "bat_charge", bolt=True)
battery(40, "bat_charge40", bolt=True)
print("ok")
