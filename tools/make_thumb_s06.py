"""Thumbnail for S06 My Clone Replaced Me: real Sage (scared, at the window) over the clone (evil grin).
usage: python tools/make_thumb_s06.py <dir with full-res frame_0040.png and frame_0850.png>"""
import os
import sys

from PIL import Image, ImageDraw, ImageEnhance

sys.path.insert(0, os.path.dirname(__file__))
from make_thumbs_batch01 import W, H, line, save, sticker  # noqa: E402


def panel(path, box, h):
    im = Image.open(path).convert("RGB").crop(box).resize((W, h), Image.LANCZOS)
    im = ImageEnhance.Color(ImageEnhance.Contrast(im).enhance(1.08)).enhance(1.2)
    return im


def main(src):
    img = Image.new("RGBA", (W, H), (14, 10, 30, 255))
    a = panel(os.path.join(src, "frame_0040.png"), (0, 440, 1080, 1240), 720)
    b = panel(os.path.join(src, "frame_0850.png"), (0, 480, 1080, 1280), 720)
    img.paste(a, (0, 480))
    img.paste(b, (0, 1200))
    d = ImageDraw.Draw(img)
    d.rectangle([0, 1192, W, 1208], fill=(255, 210, 63))
    line(img, "MY CLONE", 170, 150)
    line(img, "REPLACED ME!", 320, 128, hl={"REPLACED": (255, 90, 90)})
    line(img, "REAL?", 1080, 100, fill=(124, 212, 255))
    line(img, "FAKE?", 1760, 100, fill=(255, 90, 90))
    sticker(img, {"e": "😱", "size": 170}, 900, 640)
    save(img, "s06_clone")


if __name__ == "__main__":
    main(sys.argv[1])
