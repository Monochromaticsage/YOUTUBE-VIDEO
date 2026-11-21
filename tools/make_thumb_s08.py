"""Thumbnail for S08 copy-sister loop: both hands up (Pip first), plus Pip's evil grin inset.
usage: python tools/make_thumb_s08.py <dir with full-res frame_0024.png and frame_1020.png>"""
import os
import sys

from PIL import Image, ImageDraw, ImageEnhance

sys.path.insert(0, os.path.dirname(__file__))
from make_thumbs_batch01 import W, H, line, save, sticker  # noqa: E402


def main(src):
    img = Image.new("RGBA", (W, H), (14, 10, 30, 255))
    a = Image.open(os.path.join(src, "frame_0024.png")).convert("RGB").crop((90, 760, 1010, 1660))
    a = ImageEnhance.Color(a).enhance(1.2).resize((W, 1056), Image.LANCZOS)
    img.paste(a, (0, 600))
    ev = Image.open(os.path.join(src, "frame_1020.png")).convert("RGB").crop((300, 380, 1020, 1100)).resize((440, 440))
    mask = Image.new("L", ev.size, 0)
    ImageDraw.Draw(mask).ellipse([0, 0, 439, 439], fill=255)
    ring = Image.new("RGBA", (480, 480), (0, 0, 0, 0))
    ImageDraw.Draw(ring).ellipse([0, 0, 479, 479], fill=(255, 90, 90, 255))
    ring.paste(ev, (20, 20), mask)
    img.alpha_composite(ring, (W - 510, 1300))
    line(img, "MY SISTER COPIED", 190, 104)
    line(img, "EVERYTHING", 320, 150, fill=(255, 210, 63))
    line(img, "I DID!", 470, 120)
    sticker(img, {"e": "😳", "size": 180}, 160, 1760)
    save(img, "s08_copy_sister")


if __name__ == "__main__":
    main(sys.argv[1])
