"""Thumbnail for S10 mom-mind: Sage caught at the cookie jar, Mom behind, plus Mom's thought bubble.
usage: python tools/make_thumb_s10.py <dir with full-res frame_0060.png>"""
import os
import sys

sys.path.insert(0, os.path.dirname(__file__))
from make_thumbs_batch01 import W, H, base, line, save, sticker  # noqa: E402


def main(src):
    im = base(os.path.join(src, "frame_0060.png"))
    line(im, "MY MOM CAN", 190, 120)
    line(im, "READ MY MIND!", 330, 118, hl={"MIND!": (255, 210, 63)})
    sticker(im, {"thought": "DON'T EVEN THINK ABOUT IT!", "size": 360, "tail": "right"}, 200, 680)
    sticker(im, {"e": "🍪", "size": 220, "burst": True}, 820, 1560)
    save(im, "s10_mom_mind")


if __name__ == "__main__":
    main(sys.argv[1])
