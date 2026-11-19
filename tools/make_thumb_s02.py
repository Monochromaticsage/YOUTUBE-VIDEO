"""Thumbnail for Short #2 "Price Tags": Sage's $0 close-up with a Goldie $1,000,000 inset.
usage: python tools/make_thumb_s02.py <dir with frame_0150.png + frame_0180.png> branding/s02_price_tags_thumbnail.png
"""
import sys
from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageEnhance
SRC = sys.argv[1]; OUT = sys.argv[2]
W, H = 1080, 1920
F = "/usr/share/fonts/opentype/inter/InterDisplay-Black.otf"
EMO = "/usr/share/fonts/truetype/noto/NotoColorEmoji.ttf"

bg = Image.open(f"{SRC}/frame_0150.png").convert("RGB").resize((W, H), Image.LANCZOS)
# zoom the shot out a little and drop it below the headline; blurred copy fills the edges
canvas = bg.resize((int(W * 1.3), int(H * 1.3))).crop((int(W * .15), 0, int(W * .15) + W, H)).filter(ImageFilter.GaussianBlur(28))
k = 0.84
fg = bg.resize((int(W * k), int(H * k)), Image.LANCZOS)
fx, fy = (W - fg.size[0]) // 2, 400
mask = Image.new("L", fg.size, 0); ImageDraw.Draw(mask).rounded_rectangle([0, 0, fg.size[0]-1, fg.size[1]-1], 40, fill=255)
canvas.paste(fg, (fx, fy), mask.filter(ImageFilter.GaussianBlur(6)))
canvas = ImageEnhance.Contrast(canvas).enhance(1.1)
canvas = ImageEnhance.Color(canvas).enhance(1.15)
grad = Image.new("L", (W, H), 0); g = ImageDraw.Draw(grad)
for y in range(H):
    a = max(0, 1 - y / 640) * 200 + max(0, (y - 1500) / 420) * 110
    g.line([(0, y), (W, y)], fill=int(min(255, a)))
canvas = Image.composite(Image.new("RGB", (W, H), (14, 10, 30)), canvas, grad)

# Goldie inset: gold frame, tilted, with his $1,000,000 tag
gd = Image.open(f"{SRC}/frame_0180.png").convert("RGB")
gw, gh = gd.size
side = int(gw * 0.92)
gd = gd.crop(((gw - side) // 2, int(gh * 0.17), (gw - side) // 2 + side, int(gh * 0.17) + side))
gd = gd.resize((370, 370), Image.LANCZOS)
ImageDraw.Draw(gd).rectangle([0, 0, 369, 369], outline=(255, 200, 40), width=12)
card = Image.new("RGBA", (410, 470), (0, 0, 0, 0))
card.paste(gd, (20, 20))
d = ImageDraw.Draw(card)
d.text((205, 435), "GOLDIE", font=ImageFont.truetype(F, 58), anchor="mm", fill=(255, 210, 50),
       stroke_width=8, stroke_fill=(40, 25, 0))
card = card.rotate(7, resample=Image.BICUBIC, expand=True)
glow = card.split()[3].filter(ImageFilter.GaussianBlur(22))
glowc = Image.new("RGBA", card.size, (255, 190, 40, 0)); glowc.putalpha(glow.point(lambda v: int(v * 0.8)))
cx, cy = W - card.size[0] + 10, 820
canvas.paste(glowc, (cx, cy), glowc); canvas.paste(card, (cx, cy), card)

d = ImageDraw.Draw(canvas)
def line(txt, y, size, fill, hl=None):
    f = ImageFont.truetype(F, size)
    parts = txt.split(" ")
    widths = [d.textlength(p + " ", font=f) for p in parts]
    total = sum(widths) - d.textlength(" ", font=f)
    x = (W - total) / 2
    for p, w in zip(parts, widths):
        col = hl.get(p, fill) if hl else fill
        d.text((x + 6, y + 9), p, font=f, fill=(0, 0, 0), stroke_width=16, stroke_fill=(0, 0, 0))
        d.text((x, y), p, font=f, fill=col, stroke_width=14, stroke_fill=(10, 12, 25))
        x += w
line("EVERYONE GOT", 70, 120, (255, 255, 255))
line("A PRICE TAG...", 205, 120, (255, 255, 255))
line("MINE SAID $0", 345, 136, (255, 255, 255), {"$0": (255, 70, 70)})

ef = ImageFont.truetype(EMO, 109)
for i, ch in enumerate(["\U0001F447", "\U0001F3F7️"]):
    e = Image.new("RGBA", (160, 160), (0, 0, 0, 0))
    ImageDraw.Draw(e).text((10, 10), ch, font=ef, embedded_color=True)
    e = e.resize((180, 180), Image.LANCZOS)
    canvas.paste(e, (30 + i * 150, 930 + i * 40), e)
canvas.save(OUT, quality=95)
canvas.convert("RGB").save(OUT.replace(".png", ".jpg"), quality=92)
