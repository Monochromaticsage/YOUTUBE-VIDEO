"""Build a 16:9 long-form compilation from finished vertical Shorts.
usage: python tools/make_compilation.py <out_id> "<Title>" <ep_id> [<ep_id> ...]
Each Short sits in the centre over a blurred copy of itself, with a story counter on the
left and a subscribe panel on the right. Ends with a short subscribe outro card.
"""
import os
import subprocess
import sys

from PIL import Image, ImageDraw, ImageFont

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
BUILD = os.path.join(ROOT, "build", "compilation")
W, H = 1920, 1080
BLACK = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "assets", "fonts", "InterDisplay-Black.otf")
BOLD = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "assets", "fonts", "InterDisplay-Bold.otf")
YELLOW, PINK, WHITE = (255, 210, 63), (255, 127, 160), (255, 255, 255)

# Story titles shown in the side panel (short, punchy).
NAMES = {
    "s01_freeze_tag": "FREEZE TAG\nWENT WRONG",
    "s02_price_tags": "I SEE\nPRICE TAGS",
    "s03_taste_lies": "MY SISTER\nTASTES LIES",
    "s04_substitute_mom": "MOM IS OUR\nSUBSTITUTE",
    "s05_noob_genius": "NOOB IS A\nGENIUS?!",
}


def run(cmd):
    subprocess.run(cmd, check=True)


def text(d, xy, s, size, fill, font=BLACK, anchor="mm", stroke=8, spacing=10):
    f = ImageFont.truetype(font, size)
    d.multiline_text(xy, s, font=f, fill=fill, anchor=anchor, align="center",
                     stroke_width=stroke, stroke_fill=(15, 12, 30), spacing=spacing)


def panel(path, n, total, name):
    im = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    lx, rx = 330, W - 330
    # left: story counter + name
    d.rounded_rectangle([lx - 170, 300, lx + 170, 420], 30, fill=(255, 210, 63, 235))
    text(d, (lx, 360), f"STORY {n}/{total}", 54, (20, 16, 40), stroke=0)
    text(d, (lx, 560), name, 74, WHITE, spacing=18)
    # right: subscribe reminder
    d.rounded_rectangle([rx - 190, 330, rx + 190, 450], 60, fill=(229, 45, 39, 240))
    text(d, (rx, 390), "SUBSCRIBE", 58, WHITE, stroke=0)
    text(d, (rx, 540), "new story\nevery day!", 52, YELLOW, font=BOLD, spacing=14)
    text(d, (rx, 700), "comment your\nfavourite story!", 40, WHITE, font=BOLD, spacing=12)
    im.save(path)


def segment(src, png, out):
    fc = ("[0:v]scale=1920:-2,crop=1920:1080,boxblur=30:3,eq=brightness=-0.18:saturation=1.2[bg];"
          "[0:v]scale=-2:1080[fg];[bg][fg]overlay=(W-w)/2:0[v1];[v1][1:v]overlay=0:0,format=yuv420p[v]")
    run(["ffmpeg", "-v", "error", "-y", "-i", src, "-i", png, "-filter_complex", fc,
         "-map", "[v]", "-map", "0:a", "-r", "30", "-c:v", "libx264", "-preset", "medium", "-crf", "19",
         "-c:a", "aac", "-b:a", "192k", "-ar", "44100", "-ac", "2", out])


def outro(out, secs=5):
    png = os.path.join(BUILD, "outro.png")
    im = Image.new("RGB", (W, H), (30, 24, 70))
    d = ImageDraw.Draw(im)
    for y in range(H):
        d.line([(0, y), (W, y)], fill=(30 + y // 30, 24 + y // 60, 70 + y // 20))
    text(d, (W / 2, 330), "WHICH STORY WAS THE BEST?", 92, YELLOW, stroke=10)
    text(d, (W / 2, 470), "Tell me in the comments!", 60, WHITE, font=BOLD)
    d.rounded_rectangle([W / 2 - 330, 600, W / 2 + 330, 760], 80, fill=(229, 45, 39))
    text(d, (W / 2, 680), "SUBSCRIBE", 96, WHITE, stroke=0)
    text(d, (W / 2, 880), "PLUTONEX TALES  •  new story every day", 50, WHITE, font=BOLD)
    im.save(png)
    music = os.path.join(ROOT, "assets", "music", "happy_loop.wav")
    run(["ffmpeg", "-v", "error", "-y", "-loop", "1", "-t", str(secs), "-i", png, "-i", music,
         "-filter_complex", f"[1:a]atrim=0:{secs},volume=0.35,afade=t=out:st={secs - 1.2}:d=1.2[a]",
         "-map", "0:v", "-map", "[a]", "-r", "30", "-c:v", "libx264", "-preset", "medium", "-crf", "19",
         "-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", "192k", "-ar", "44100", "-ac", "2", out])


def main(out_id, title, eps):
    os.makedirs(BUILD, exist_ok=True)
    parts = []
    for i, ep in enumerate(eps, 1):
        png = os.path.join(BUILD, f"panel_{i}.png")
        panel(png, i, len(eps), NAMES.get(ep, ep.upper()))
        seg = os.path.join(BUILD, f"seg_{i}.mp4")
        segment(os.path.join(ROOT, "output", f"{ep}.mp4"), png, seg)
        parts.append(seg)
        print("segment", i, ep)
    parts.append(os.path.join(BUILD, "outro.mp4"))
    outro(parts[-1])
    lst = os.path.join(BUILD, "list.txt")
    with open(lst, "w") as f:
        f.writelines(f"file '{p}'\n" for p in parts)
    out = os.path.join(ROOT, "output", f"{out_id}.mp4")
    run(["ffmpeg", "-v", "error", "-y", "-f", "concat", "-safe", "0", "-i", lst, "-c", "copy",
         "-movflags", "+faststart", out])
    print("wrote", out, "-", title)


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2], sys.argv[3:])
