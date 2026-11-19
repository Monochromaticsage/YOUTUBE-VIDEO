"""Builds the corner "Subscribe / Like / Comment" reminder overlay as a short PNG sequence.
assemble.py lays it over every new video once, in the top-left corner (see "cta" in the episode).

usage: python tools/make_cta_overlay.py        -> assets/overlays/cta/cta_000.png ...
"""
import math
import os
from PIL import Image, ImageDraw, ImageFont

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
OUT = os.path.join(ROOT, "assets", "overlays", "cta")
F = "/usr/share/fonts/opentype/inter/InterDisplay-Black.otf"
EMO = "/usr/share/fonts/truetype/noto/NotoColorEmoji.ttf"
FPS, SECONDS = 30, 4.0
W, H = 640, 150


def emoji(ch, size):
    e = Image.new("RGBA", (136, 128), (0, 0, 0, 0))
    ImageDraw.Draw(e).text((0, 0), ch, font=ImageFont.truetype(EMO, 109), embedded_color=True)
    e = e.crop(e.getbbox())
    return e.resize((int(e.width * size / e.height), size), Image.LANCZOS)


def pop(t, start, dur=0.25):
    """0 before start, overshoots to ~1.25 then settles to 1."""
    if t < start:
        return 0.0
    x = min(1.0, (t - start) / dur)
    return 1 + 0.25 * math.sin(math.pi * x) if x >= 0.5 else 2 * x * 1.25


def paste_scaled(img, src, cx, cy, s):
    if s <= 0.01:
        return
    w, h = max(1, int(src.width * s)), max(1, int(src.height * s))
    r = src.resize((w, h), Image.LANCZOS)
    img.alpha_composite(r, (int(cx - w / 2), int(cy - h / 2)))


def frame(t, icons):
    img = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    # dark pill
    d.rounded_rectangle([6, 14, W - 6, H - 14], 60, fill=(15, 15, 25, 205), outline=(255, 255, 255, 60), width=3)
    # subscribe button: red -> grey "SUBSCRIBED" after the click at 1.3 s
    clicked = t >= 1.3
    press = 0.92 if 1.25 <= t < 1.4 else 1.0
    btn = Image.new("RGBA", (330, 92), (0, 0, 0, 0))
    bd = ImageDraw.Draw(btn)
    bd.rounded_rectangle([0, 0, 329, 91], 46, fill=(90, 90, 100, 255) if clicked else (230, 33, 23, 255))
    f = ImageFont.truetype(F, 40 if not clicked else 34)
    label = "✓ SUBSCRIBED" if clicked else "SUBSCRIBE"
    bd.text((165 if clicked else 140, 46), label, font=f, anchor="mm", fill=(255, 255, 255))
    if not clicked:
        btn.alpha_composite(icons["bell"], (330 - icons["bell"].width - 22, (92 - icons["bell"].height) // 2))
    paste_scaled(img, btn, 26 + 165, H / 2, press)
    # like + comment pop in after the click
    paste_scaled(img, icons["like"], 430, H / 2, pop(t, 1.7))
    paste_scaled(img, icons["comment"], 545, H / 2, pop(t, 2.1))
    # cursor slides onto the button, clicks, then leaves
    if 0.5 <= t < 2.0:
        k = min(1.0, (t - 0.5) / 0.7)
        k = 1 - (1 - k) ** 3
        cx, cy = 330 + (210 - 330) * k, 150 + (80 - 150) * k
        if t >= 1.6:
            cy += (t - 1.6) * 300
        img.alpha_composite(icons["hand"], (int(cx), int(cy)))
    return img


def main():
    os.makedirs(OUT, exist_ok=True)
    for p in os.listdir(OUT):
        os.remove(os.path.join(OUT, p))
    icons = {"bell": emoji("\U0001F514", 48), "like": emoji("\U0001F44D", 82),
             "comment": emoji("\U0001F4AC", 82), "hand": emoji("\U0001F446", 70)}
    for i in range(int(FPS * SECONDS)):
        frame(i / FPS, icons).save(os.path.join(OUT, f"cta_{i:03d}.png"))
    print("wrote", int(FPS * SECONDS), "frames to", OUT)


if __name__ == "__main__":
    main()
