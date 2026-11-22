"""Thumbnail for S09 teacher-future: Sage shocked + the DETENTION slip + the creepy laptop smile.
usage: python tools/make_thumb_s09.py <dir with full-res frame_0135.png>"""
import os
import sys

from PIL import Image, ImageDraw

sys.path.insert(0, os.path.dirname(__file__))
from make_thumbs_batch01 import W, H, base, line, save, sticker  # noqa: E402

T = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "assets", "textures", "s09")


def main(src):
    im = base(os.path.join(src, "frame_0135.png"))
    slip = Image.open(os.path.join(T, "slip.png")).convert("RGBA")
    slip.thumbnail((560, 560))
    slip = slip.rotate(-8, resample=Image.BICUBIC, expand=True)
    im.alpha_composite(slip, (40, 1330))
    lap = Image.open(os.path.join(T, "lap_smile.png")).convert("RGBA")
    lap.thumbnail((520, 520))
    lap = lap.rotate(6, resample=Image.BICUBIC, expand=True)
    im.alpha_composite(lap, (W - lap.width - 20, 1290))
    line(im, "MY TEACHER PUNISHED ME", 200, 70)
    line(im, "BEFORE", 300, 160, fill=(255, 90, 90))
    line(im, "I DID ANYTHING!", 470, 104)
    sticker(im, {"e": "😳", "size": 170}, 900, 1140)
    save(im, "s09_teacher_future")


if __name__ == "__main__":
    main(sys.argv[1])
