"""Thumbnail for S11 draw-real: Sage with the golden pencil, sketches popping off the page.
usage: python tools/make_thumb_s11.py <dir with full-res frame_0002.png>"""
import os
import sys

from PIL import Image

sys.path.insert(0, os.path.dirname(__file__))
from make_thumbs_batch01 import W, H, base, line, save, sticker  # noqa: E402

T = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "assets", "textures", "s11")


def card(im, name, size, cx, cy, rot):
    c = Image.open(os.path.join(T, name)).convert("RGBA")
    c.thumbnail((size, size))
    c = c.rotate(rot, resample=Image.BICUBIC, expand=True)
    im.alpha_composite(c, (int(cx - c.width / 2), int(cy - c.height / 2)))


def main(src):
    im = base(os.path.join(src, "frame_0002.png"))
    line(im, "WHATEVER I DRAW", 190, 104)
    line(im, "BECOMES REAL!", 320, 128, hl={"REAL!": (255, 210, 63)})
    card(im, "draw_car.png", 360, 230, 1500, -10)
    card(im, "draw_pizza.png", 300, 860, 1560, 9)
    sticker(im, {"e": "✏️", "size": 170}, 900, 700)
    sticker(im, {"e": "💨", "size": 200, "burst": "#ffffff"}, 560, 1640)
    save(im, "s11_draw_real")


if __name__ == "__main__":
    main(sys.argv[1])
