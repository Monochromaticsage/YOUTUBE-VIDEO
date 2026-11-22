import os
import sys
from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageEnhance, ImageOps
S = sys.argv[1]; OUT = sys.argv[2]
W, H = 1080, 1920
F = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "assets", "fonts", "InterDisplay-Black.otf")
EMO = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "assets", "fonts", "NotoColorEmoji.ttf")

bg = Image.open(f"{S}/hi_985/frame_0985.png").convert("RGB").resize((W, H), Image.LANCZOS)
shift = 170
canvas = Image.new("RGB", (W, H))
top = bg.crop((0, 0, W, 60)).resize((W, shift + 60)).filter(ImageFilter.GaussianBlur(12))
canvas.paste(top, (0, 0)); canvas.paste(bg, (0, shift))
canvas = ImageEnhance.Contrast(canvas).enhance(1.12)
canvas = ImageEnhance.Color(canvas).enhance(1.15)
# dark gradient behind the text + subtle bottom vignette
grad = Image.new("L", (W, H), 0); g = ImageDraw.Draw(grad)
for y in range(H):
    a = max(0, 1 - y / 760) * 185 + max(0, (y - 1450) / 470) * 120
    g.line([(0, y), (W, y)], fill=int(min(255, a)))
canvas = Image.composite(Image.new("RGB", (W, H), (8, 14, 30)), canvas, grad)

# frozen Noob inset: icy tint, frost frame, tilted
noob = Image.open(f"{S}/hi_90/frame_0090.png").convert("RGB")
nw, nh = noob.size
noob = noob.crop((int(nw*0.06), int(nh*0.22), int(nw*0.94), int(nh*0.22) + int(nw*0.88)))
noob = noob.resize((470, 470), Image.LANCZOS)
gray = ImageOps.grayscale(noob)
icy = ImageOps.colorize(gray, black=(10, 40, 90), white=(225, 250, 255))
noob = Image.blend(noob, icy, 0.62)
ImageDraw.Draw(noob).rectangle([0, 0, 469, 469], outline=(190, 240, 255), width=14)
card = Image.new("RGBA", (470 + 40, 470 + 110), (0, 0, 0, 0))
card.paste(noob, (20, 20))
d = ImageDraw.Draw(card)
lf = ImageFont.truetype(F, 62)
d.text((255, 535), "FROZEN", font=lf, anchor="mm", fill=(170, 235, 255),
       stroke_width=8, stroke_fill=(5, 20, 50))
card = card.rotate(-7, resample=Image.BICUBIC, expand=True)
glow = card.split()[3].filter(ImageFilter.GaussianBlur(22))
glowc = Image.new("RGBA", card.size, (120, 220, 255, 0)); glowc.putalpha(glow.point(lambda v: int(v*0.8)))
cx, cy = 40, 1150
canvas.paste(glowc, (cx, cy), glowc); canvas.paste(card, (cx, cy), card)

# headline
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
line("WHAT SECRET", 70, 128, (255, 255, 255))
line("WOULD YOU TELL", 215, 118, (255, 255, 255), {"YOU": (255, 214, 40)})
line("TO UNFREEZE?", 355, 132, (130, 225, 255))

# emoji 👇❄️ (Noto Color Emoji only renders at size 109)
ef = ImageFont.truetype(EMO, 109)
for i, ch in enumerate(["\U0001F447", "❄️"]):
    e = Image.new("RGBA", (160, 160), (0, 0, 0, 0))
    ImageDraw.Draw(e).text((10, 10), ch, font=ef, embedded_color=True)
    e = e.resize((190, 190), Image.LANCZOS)
    canvas.paste(e, (W - 360 + i * 165, 1180 + i * 40), e)
canvas.save(OUT, quality=95)
canvas.convert("RGB").save(OUT.replace(".png", ".jpg"), quality=92)
