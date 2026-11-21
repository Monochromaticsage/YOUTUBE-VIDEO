"""Thumbnail for S07 sneeze loop: Sage about to sneeze with the feather, plus the 7:00 clock.
usage: python tools/make_thumb_s07.py <dir with full-res frame_1200.png (Sage) and frame_0075.png (clock)>"""
import os
import sys

from PIL import Image, ImageDraw

sys.path.insert(0, os.path.dirname(__file__))
from make_thumbs_batch01 import W, H, base, line, save, sticker  # noqa: E402


def main(src):
    im = base(os.path.join(src, "frame_1200.png"))
    clock = Image.open(os.path.join(src, "frame_0075.png")).convert("RGB").crop((0, 520, 1080, 1220))
    clock.thumbnail((520, 520))
    c = Image.new("RGBA", (clock.width + 24, clock.height + 24), (255, 255, 255, 255))
    c.paste(clock, (12, 12))
    c = c.rotate(-7, resample=Image.BICUBIC, expand=True)
    im.alpha_composite(c, (W - c.width - 30, 1430))
    line(im, "EVERY TIME I SNEEZE", 200, 92)
    line(im, "MY DAY", 320, 150)
    line(im, "RESTARTS!", 470, 150, fill=(255, 90, 90))
    sticker(im, {"e": "🪶", "size": 330}, 470, 1210)
    sticker(im, {"e": "🤧", "size": 210, "burst": True}, 230, 1560)
    save(im, "s07_sneeze")


if __name__ == "__main__":
    main(sys.argv[1])
