"""Thumbnails for batch 01 (S03 Taste Lies, S04 Substitute Mom, S05 Noob Genius).
usage: python tools/make_thumbs_batch01.py <dir with <episode>/frame_XXXX.png full-res stills>
Headlines sit below the top ~10% so the channel grid's crop doesn't cut them off.
"""
import glob
import os
import sys

from PIL import Image, ImageDraw, ImageEnhance, ImageFilter, ImageFont

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.join(ROOT, "pipeline"))
import fx  # noqa: E402

W, H = 1080, 1920
F = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "assets", "fonts", "InterDisplay-Black.otf")


def base(path):
    im = Image.open(path).convert("RGB").resize((W, H), Image.LANCZOS)
    im = ImageEnhance.Contrast(im).enhance(1.08)
    im = ImageEnhance.Color(im).enhance(1.2)
    grad = Image.new("L", (W, H), 0)
    g = ImageDraw.Draw(grad)
    for y in range(H):
        a = max(0, 1 - y / 820) * 175 + max(0, (y - 1540) / 380) * 120
        g.line([(0, y), (W, y)], fill=int(min(255, a)))
    return Image.composite(Image.new("RGB", (W, H), (12, 10, 28)), im, grad).convert("RGBA")


def line(img, txt, y, size, fill=(255, 255, 255), hl=None):
    d = ImageDraw.Draw(img)
    f = ImageFont.truetype(F, size)
    parts = txt.split(" ")
    widths = [d.textlength(p + " ", font=f) for p in parts]
    total = sum(widths) - d.textlength(" ", font=f)
    x = (W - total) / 2
    for p, w in zip(parts, widths):
        col = (hl or {}).get(p, fill)
        d.text((x + 6, y + 9), p, font=f, fill=(0, 0, 0), stroke_width=16, stroke_fill=(0, 0, 0))
        d.text((x, y), p, font=f, fill=col, stroke_width=14, stroke_fill=(10, 12, 25))
        x += w


def sticker(img, spec, cx, cy):
    tmp = os.path.join(ROOT, "build", "_thumb_fx")
    fx.render_sticker(dict(spec, dur=1.0), tmp, W, H)
    st = Image.open(sorted(glob.glob(os.path.join(tmp, "f_*.png")))[12])
    img.alpha_composite(st, (int(cx - st.width / 2), int(cy - st.height / 2)))


def card(img, path, size, cx, cy, rot, label, color):
    ph = Image.open(path).convert("RGB")
    ph.thumbnail((size, size))
    c = Image.new("RGBA", (ph.width + 40, ph.height + 110), (0, 0, 0, 0))
    c.paste(ph, (20, 20))
    d = ImageDraw.Draw(c)
    d.rectangle([20, 20, 20 + ph.width - 1, 20 + ph.height - 1], outline=color, width=12)
    d.text((c.width / 2, ph.height + 70), label, font=ImageFont.truetype(F, 54), anchor="mm", fill=color,
           stroke_width=8, stroke_fill=(20, 10, 20))
    c = c.rotate(rot, resample=Image.BICUBIC, expand=True)
    img.alpha_composite(c, (int(cx - c.width / 2), int(cy - c.height / 2)))


def save(img, name):
    out = os.path.join(ROOT, "branding", f"{name}_thumbnail")
    img.convert("RGB").save(out + ".png")
    img.convert("RGB").save(out + ".jpg", quality=92)
    print("wrote", out + ".jpg")


def main(src):
    # S03: Pip's furious lemon face
    im = base(glob.glob(os.path.join(src, "s03_taste_lies", "frame_*.png"))[0])
    line(im, "MY SISTER CAN", 200, 118)
    line(im, "TASTE LIES!", 340, 150, hl={"LIES!": (255, 224, 58)})
    sticker(im, {"e": "🍋", "size": 330, "burst": True}, 820, 1380)
    sticker(im, {"text": "LEMON!", "color": "#ffe03a", "size": 120}, 330, 1560)
    save(im, "s03_taste_lies")

    # S04: Mom's scary smile + the baby photo
    im = base(glob.glob(os.path.join(src, "s04_substitute_mom", "frame_*.png"))[0])
    line(im, "MY MOM BECAME", 200, 112)
    line(im, "MY TEACHER!", 335, 150, hl={"TEACHER!": (255, 127, 110)})
    card(im, os.path.join(ROOT, "assets", "textures", "baby_sage.png"), 470, 790, 1370, 8, "MY BABY PHOTO", "#ff8fb1")
    sticker(im, {"e": "😳", "size": 200}, 230, 1560)
    save(im, "s04_substitute_mom")

    # S05: Noob in Grandpa's glasses
    im = base(glob.glob(os.path.join(src, "s05_noob_genius", "frame_*.png"))[0])
    line(im, "2 + 2 =", 190, 140)
    line(im, "FISH?!", 340, 190, fill=(124, 212, 255))
    line(im, "...AND THEY THINK HE'S A GENIUS", 1600, 54, fill=(255, 210, 63))
    sticker(im, {"e": "🐟", "size": 260, "burst": "#7cd4ff"}, 820, 1330)
    sticker(im, {"e": "🤓", "size": 190}, 230, 1380)
    save(im, "s05_noob_genius")


if __name__ == "__main__":
    main(sys.argv[1])
