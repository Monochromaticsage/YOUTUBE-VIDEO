"""Generic Short thumbnail: one full-res frame + two headline lines + up to two emoji stickers.
usage: python tools/make_thumb_generic.py <frame.png> <episode_id> "LINE ONE" "LINE TWO" [HIGHLIGHT_WORD] [emoji1] [emoji2]"""
import os
import sys

sys.path.insert(0, os.path.dirname(__file__))
from make_thumbs_batch01 import W, base, line, save, sticker  # noqa: E402
from PIL import ImageDraw, ImageFont  # noqa: E402
from make_thumbs_batch01 import F  # noqa: E402


def fit(text, start, maxw=1010):
    d = ImageDraw.Draw(__import__("PIL.Image", fromlist=["Image"]).new("RGB", (1, 1)))
    s = start
    while s > 50 and d.textlength(text, font=ImageFont.truetype(F, s)) > maxw:
        s -= 4
    return s


def main(frame, ep, l1, l2, hl=None, e1=None, e2=None):
    im = base(frame)
    line(im, l1, 190, fit(l1, 110))
    line(im, l2, 330, fit(l2, 140), hl={hl: (255, 210, 63)} if hl else None)
    if e1:
        sticker(im, {"e": e1, "size": 220, "burst": True}, 840, 1560)
    if e2:
        sticker(im, {"e": e2, "size": 170}, 220, 1600)
    save(im, ep)


if __name__ == "__main__":
    a = sys.argv[1:] + [None] * 7
    main(*a[:7])
