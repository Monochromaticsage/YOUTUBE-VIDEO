"""Laptop-screen images ("tomorrow's" security-cam video) and the detention slip for S09.
Reads the CCTV stills in assets/textures/s09/cam_*.png (rendered from episodes/stills/teacher_screens.json)."""
import os
import sys

from PIL import Image, ImageDraw, ImageEnhance, ImageFont

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.join(ROOT, "pipeline"))
import fx  # noqa: E402

D = os.path.join(ROOT, "assets", "textures", "s09")
BLACK = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "assets", "fonts", "InterDisplay-Black.otf")
BOLD = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "assets", "fonts", "InterDisplay-Bold.otf")
SW, SH = 1280, 800


def cam(name, cy):
    im = Image.open(os.path.join(D, f"cam_{name}.png")).convert("RGB")
    w = im.width
    h = int(w * SH / SW)
    top = max(0, min(im.height - h, int(im.height * cy - h / 2)))
    im = im.crop((0, top, w, top + h)).resize((SW, SH), Image.LANCZOS)
    im = ImageEnhance.Color(im).enhance(0.75)
    return ImageEnhance.Contrast(im).enhance(1.05)


def screen(name, cy, delete=None, label="TOMORROW  9:00 AM"):
    im = cam(name, cy).convert("RGBA")
    d = ImageDraw.Draw(im)
    for y in range(0, SH, 6):  # faint scanlines
        d.line([(0, y), (SW, y)], fill=(0, 0, 0, 22))
    f = ImageFont.truetype(BLACK, 60)
    d.ellipse([40, 40, 80, 80], fill=(235, 30, 40))
    d.text((96, 30), "REC", font=f, fill=(255, 255, 255), stroke_width=4, stroke_fill=(0, 0, 0))
    d.text((SW - 40, 30), label, font=f, fill=(255, 230, 80), anchor="ra", stroke_width=4, stroke_fill=(0, 0, 0))
    if delete:
        bx0, by0 = SW - 360, SH - 150
        d.rounded_rectangle([bx0, by0, SW - 40, SH - 40], 22, fill=(225, 35, 45), outline=(255, 255, 255), width=5)
        d.text(((bx0 + SW - 40) / 2, (by0 + SH - 40) / 2), "DELETE", font=ImageFont.truetype(BLACK, 62),
               fill=(255, 255, 255), anchor="mm")
        cx, cy2 = (SW - 520, SH - 330) if delete == "far" else (SW - 200, SH - 95)
        arrow = [(0, 0), (0, 70), (18, 54), (32, 86), (44, 80), (30, 50), (54, 50)]
        pts = [(cx + x * 1.4, cy2 + y * 1.4) for x, y in arrow]
        d.polygon(pts, fill=(255, 255, 255), outline=(0, 0, 0))
    return im


def laptop(scr):
    """Wrap a screen image in a laptop bezel for full-frame overlays."""
    W, H = SW + 120, SH + 230
    im = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    d.rounded_rectangle([0, 0, W - 1, SH + 110], 40, fill=(40, 44, 52))
    im.paste(scr, (60, 55))
    d.polygon([(-0, SH + 110), (W, SH + 110), (W - 0, H - 1), (0, H - 1)], fill=(70, 75, 85))
    d.rounded_rectangle([W / 2 - 120, SH + 150, W / 2 + 120, SH + 195], 12, fill=(55, 60, 70))
    return im


def slip():
    W, H = 900, 640
    im = Image.new("RGBA", (W, H), (255, 251, 230, 255))
    d = ImageDraw.Draw(im)
    d.rectangle([0, 0, W - 1, 130], fill=(220, 40, 50))
    d.text((W / 2, 66), "DETENTION", font=ImageFont.truetype(BLACK, 96), fill=(255, 255, 255), anchor="mm")
    f = ImageFont.truetype(BOLD, 50)
    d.text((50, 180), "Name:  SAGE", font=f, fill=(40, 40, 60))
    d.text((50, 265), "Reason:", font=f, fill=(40, 40, 60))
    plane = fx._emoji("✈️", 150)
    im.alpha_composite(plane, (290, 240))
    d.text((50, 430), "Date:  TOMORROW", font=f, fill=(40, 40, 60))
    d.text((W - 60, H - 70), "- Ms. Brick", font=ImageFont.truetype(BOLD, 44), fill=(40, 40, 160), anchor="ra")
    d.rectangle([0, 0, W - 1, H - 1], outline=(60, 60, 60), width=6)
    return im


os.makedirs(D, exist_ok=True)
outs = {
    "screen_reach": screen("reach", 0.42),
    "screen_plane": screen("plane", 0.42),
    "screen_far": screen("reach", 0.42, delete="far"),
    "screen_near": screen("reach", 0.42, delete="near"),
    "screen_smile": screen("smile", 0.36, label="TOMORROW  9:03 AM"),
    "screen_slam": screen("slam", 0.42, label="TOMORROW  9:00 AM"),
}
for k, v in outs.items():
    v.convert("RGB").save(os.path.join(D, k + ".png"))
    laptop(v).save(os.path.join(D, "lap_" + k.split("_", 1)[1] + ".png"))
slip().convert("RGB").save(os.path.join(D, "slip.png"))
print("ok", sorted(os.listdir(D)))
