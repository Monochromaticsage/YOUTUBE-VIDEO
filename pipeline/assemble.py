"""Step 3: frames + voices + sound effects + music + captions -> final MP4.

Sound effects: put files in assets/sfx/ (e.g. vine_boom.mp3) and use
"sfx": "vine_boom" on a shot (plays at the start of the shot), or
"sfx": [{"name": "bruh", "at": 0.8}] to offset it.
Music: "music": "chill_loop" on the episode -> assets/music/chill_loop.mp3 (looped, quiet).
"""
import array
import glob
import os
import re
import subprocess
import wave

from voice import SAMPLE_RATE

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))


# ffmpeg colour grades: warm highlights / teal shadows like cinematic animation
GRADES = {
    "none": "",
    "cinematic": "eq=contrast=1.12:saturation=1.12:gamma=0.96,"
                 "colorbalance=rs=-0.10:gs=0.03:bs=0.13:rm=0.0:bm=0.0:rh=0.05:gh=0.02:bh=-0.05",
    "warm": "eq=contrast=1.08:saturation=1.2,colorbalance=rs=0.02:bs=0.04:rm=0.05:bm=-0.04:rh=0.1:bh=-0.08",
    "cool": "eq=contrast=1.1:saturation=1.05,colorbalance=rs=-0.08:bs=0.12:rh=0.02:bh=0.04",
    "night": "eq=contrast=1.15:saturation=0.9:brightness=-0.03,colorbalance=rs=-0.1:bs=0.15:rh=-0.02:bh=0.08",
}


def find_asset(folder, name):
    for ext in ("wav", "mp3", "ogg", "m4a", "flac"):
        p = os.path.join(ROOT, "assets", folder, f"{name}.{ext}")
        if os.path.exists(p):
            return p
    return None


def dialogue_track(timing, out_wav):
    out = array.array("h")
    for s in timing["shots"]:
        n = int(round(s["duration"] * SAMPLE_RATE))
        seg = array.array("h", b"\x00\x00" * n)
        if s.get("audio"):
            with wave.open(s["audio"], "rb") as w:
                data = array.array("h", w.readframes(w.getnframes()))
            seg[:min(n, len(data))] = data[:n]
        out.extend(seg)
    with wave.open(out_wav, "wb") as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(SAMPLE_RATE)
        w.writeframes(out.tobytes())


def ass_time(t):
    h, rem = divmod(t, 3600)
    m, s = divmod(rem, 60)
    return f"{int(h)}:{int(m):02d}:{s:05.2f}"


def captions(ep, timing, cast, out_ass):
    """Shorts-style captions: 2-4 words at a time, big and bold, speaker colour."""
    short = ep.get("format", "short") == "short"
    W, H = (1080, 1920) if short else (1920, 1080)
    size = 96 if short else 64
    margin_v = 560 if short else 90
    lines = ["[Script Info]", "ScriptType: v4.00+", f"PlayResX: {W}", f"PlayResY: {H}", "",
             "[V4+ Styles]",
             "Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, "
             "Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, "
             "Shadow, Alignment, MarginL, MarginR, MarginV, Encoding",
             f"Style: Cap,{ep.get('caption_font', 'Arial Black')},{size},&H00FFFFFF,&H00FFFFFF,&H00000000,"
             f"&H80000000,1,0,0,0,100,100,0,0,1,{8 if short else 5},3,2,60,60,{margin_v},1",
             "", "[Events]", "Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text"]
    t = 0.0
    i = 0
    for sc in ep["scenes"]:
        for shot in sc["shots"]:
            dur = timing["shots"][i]["duration"]
            text = shot.get("caption", shot.get("line", "")).strip()
            if text and ep.get("captions", True):
                spk = shot.get("speaker")
                color = (cast.get(spk, {}).get("caption_color") or "#FFFFFF").lstrip("#")
                bgr = color[4:6] + color[2:4] + color[0:2]
                words = text.split()
                per = 3 if short else 7
                chunks = [" ".join(words[k:k + per]) for k in range(0, len(words), per)]
                speak = max(0.4, dur - 0.25)
                total_chars = sum(len(c) for c in chunks)
                ct = t
                for c in chunks:
                    d = speak * len(c) / max(1, total_chars)
                    pop = r"{\fscx80\fscy80\t(0,80,\fscx100\fscy100)}" if short else ""
                    c_esc = re.sub(r"[{}]", "", c)
                    if short:
                        c_esc = c_esc.upper()
                    lines.append(f"Dialogue: 0,{ass_time(ct)},{ass_time(ct + d)},Cap,,0,0,0,,"
                                 f"{pop}{{\\c&H{bgr}&}}{c_esc}")
                    ct += d
            t += dur
            i += 1
    with open(out_ass, "w", encoding="utf-8") as f:
        f.write("\n".join(lines) + "\n")


def assemble(ep, timing, cast, build_dir, out_mp4):
    fps = timing["fps"]
    frames = sorted(glob.glob(os.path.join(build_dir, "frames", "frame_*.png")))
    if not frames:
        raise SystemExit("no frames rendered")
    dialogue_track(timing, os.path.join(build_dir, "dialogue.wav"))
    captions(ep, timing, cast, os.path.join(build_dir, "subs.ass"))

    first = int(re.search(r"(\d+)\.png$", frames[0]).group(1))
    inputs = ["-framerate", str(fps), "-start_number", str(first), "-i", "frames/frame_%04d.png",
              "-i", "dialogue.wav"]
    mix = ["[1:a]volume=1.0[a1]"]
    labels = ["[a1]"]
    idx = 2
    # sound effects
    t = 0.0
    k = 0
    for sc in ep["scenes"]:
        for shot in sc["shots"]:
            sfx = shot.get("sfx")
            if isinstance(sfx, str):
                sfx = [{"name": sfx, "at": 0}]
            for fx in sfx or []:
                p = find_asset("sfx", fx["name"])
                if not p:
                    print(f"[assemble] missing sound effect assets/sfx/{fx['name']}.* (skipped)")
                    continue
                ms = int((t + fx.get("at", 0)) * 1000)
                inputs += ["-i", p]
                mix.append(f"[{idx}:a]aformat=channel_layouts=mono,volume={fx.get('volume', 0.8)},"
                           f"adelay={ms}|{ms}[s{idx}]")
                labels.append(f"[s{idx}]")
                idx += 1
            t += timing["shots"][k]["duration"]
            k += 1
    music = ep.get("music")
    if music:
        p = find_asset("music", music)
        if p:
            inputs += ["-stream_loop", "-1", "-i", p]
            mix.append(f"[{idx}:a]aformat=channel_layouts=mono,volume={ep.get('music_volume', 0.12)}[m]")
            labels.append("[m]")
            idx += 1
        else:
            print(f"[assemble] missing music assets/music/{music}.* (skipped)")
    mix.append(f"{''.join(labels)}amix=inputs={len(labels)}:duration=first:normalize=0,"
               f"alimiter=limit=0.95[aout]")
    W, H = (1080, 1920) if ep.get("format", "short") == "short" else (1920, 1080)
    grade = GRADES[ep.get("grade", "none")]
    if grade:
        # colour grade -> soft glow (bloom) -> vignette -> captions
        vf = (f"[0:v]scale={W}:{H}:flags=lanczos,{grade},split[g1][g2];"
              f"[g2]gblur=sigma=22,eq=brightness=-0.06[glow];"
              f"[g1][glow]blend=all_mode=screen:all_opacity=0.28,vignette=angle=PI/4.6,"
              f"subtitles=subs.ass,format=yuv420p[vout]")
    else:
        vf = f"[0:v]scale={W}:{H}:flags=lanczos,subtitles=subs.ass,format=yuv420p[vout]"
    cmd = ["ffmpeg", "-y", "-loglevel", "error", *inputs, "-filter_complex", ";".join(mix + [vf]),
           "-map", "[vout]", "-map", "[aout]", "-c:v", "libx264", "-preset", "medium", "-crf", "18",
           "-c:a", "aac", "-b:a", "192k", "-movflags", "+faststart", "-shortest",
           os.path.relpath(out_mp4, build_dir)]
    subprocess.run(cmd, check=True, cwd=build_dir)
    print(f"[assemble] wrote {out_mp4}")
