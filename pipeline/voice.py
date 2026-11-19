"""Step 1: make the voice lines and the timing file the animation follows.

For each shot with a line, calls ElevenLabs (if ELEVENLABS_API_KEY is set) using
the speaker's "voice_id" from episodes/cast.json. Without a key it makes silent
placeholder clips sized to the text, so you can still preview the animation.

Writes build/<id>/audio/shot_XXX.wav and build/<id>/timing.json:
  {"fps": 30, "shots": [{"duration": 2.4, "audio": "...wav", "mouth": [0,1,1,0,...]}]}
"mouth" is one 0/1 per video frame, from the loudness of the voice (lip-flap).
"""
import array
import json
import math
import os
import subprocess
import urllib.request
import wave

SAMPLE_RATE = 44100
PAD_AFTER = 0.25  # breathing room after each line (seconds)


def tts_elevenlabs(text, voice_id, out_mp3, settings=None):
    """Generates speech AND per-character timestamps (saved next to the mp3 as .words.json)
    so captions can pop one word at a time exactly when it is spoken."""
    import base64
    key = os.environ["ELEVENLABS_API_KEY"]
    url = (f"https://api.elevenlabs.io/v1/text-to-speech/{voice_id}/with-timestamps"
           f"?output_format=mp3_44100_128")
    body = {"text": text, "model_id": os.environ.get("ELEVENLABS_MODEL", "eleven_multilingual_v2")}
    if settings:
        body["voice_settings"] = settings
    req = urllib.request.Request(url, data=json.dumps(body).encode(), method="POST",
                                 headers={"xi-api-key": key, "Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=120) as r:
        data = json.loads(r.read())
    with open(out_mp3, "wb") as f:
        f.write(base64.b64decode(data["audio_base64"]))
    al = data.get("alignment") or data.get("normalized_alignment")
    words = []
    if al:
        cur, start = "", None
        for ch, a, b in zip(al["characters"], al["character_start_times_seconds"],
                            al["character_end_times_seconds"]):
            if ch.isspace():
                if cur:
                    words.append([cur, start, end])
                cur, start = "", None
                continue
            if start is None:
                start = a
            cur += ch
            end = b
        if cur:
            words.append([cur, start, end])
    with open(out_mp3[:-4] + ".words.json", "w", encoding="utf-8") as f:
        json.dump(words, f)


def to_wav(src, dst, speed=1.0, pitch=1.0):
    """Convert anything ffmpeg reads into 44.1k mono 16-bit wav (optionally faster/higher)."""
    af = []
    if pitch != 1.0:
        af += [f"asetrate={int(SAMPLE_RATE * pitch)}", f"aresample={SAMPLE_RATE}", f"atempo={1 / pitch:.4f}"]
    if speed != 1.0:
        af.append(f"atempo={speed:.4f}")
    cmd = ["ffmpeg", "-y", "-loglevel", "error", "-i", src, "-ac", "1", "-ar", str(SAMPLE_RATE)]
    if af:
        cmd += ["-af", ",".join(af)]
    subprocess.run(cmd + [dst], check=True)


def silent_wav(path, seconds):
    n = int(seconds * SAMPLE_RATE)
    with wave.open(path, "wb") as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(SAMPLE_RATE)
        w.writeframes(b"\x00\x00" * n)


def wav_info(path, fps):
    with wave.open(path, "rb") as w:
        n, sr = w.getnframes(), w.getframerate()
        data = array.array("h", w.readframes(n))
    dur = n / sr
    win = max(1, sr // fps)
    levels = []
    for i in range(0, len(data), win):
        chunk = data[i:i + win]
        levels.append(math.sqrt(sum(s * s for s in chunk) / max(1, len(chunk))))
    peak = max(levels) if levels else 0
    if peak < 50:  # silent clip
        return dur, []
    mouth = [1 if lv > peak * 0.18 else 0 for lv in levels]
    # avoid 1-frame flickers
    for i in range(1, len(mouth) - 1):
        if mouth[i - 1] == mouth[i + 1] != mouth[i]:
            mouth[i] = mouth[i - 1]
    return dur, mouth


def estimate_seconds(text):
    words = len(text.split())
    return max(1.0, words / 2.8 + 0.3)


def build(ep, cast, build_dir, force=False):
    fps = ep.get("fps", 30)
    audio_dir = os.path.join(build_dir, "audio")
    os.makedirs(audio_dir, exist_ok=True)
    have_key = bool(os.environ.get("ELEVENLABS_API_KEY"))
    if not have_key:
        print("[voice] ELEVENLABS_API_KEY not set -> using silent placeholder audio")
    shots = []
    i = 0
    for sc in ep["scenes"]:
        for shot in sc["shots"]:
            line = shot.get("line", "").strip()
            speaker = shot.get("speaker")
            entry = {"audio": None, "mouth": []}
            if line and speaker:
                wav = os.path.join(audio_dir, f"shot_{i:03d}.wav")
                spec = dict(cast.get(speaker, {}))
                spec.update(ep.get("characters", {}).get(speaker, {}))
                custom = shot.get("audio_file")  # your own recorded line
                if custom:
                    to_wav(custom, wav, spec.get("speed", 1.0), spec.get("pitch", 1.0))
                elif not os.path.exists(wav) or force:
                    if have_key and spec.get("voice_id"):
                        mp3 = wav[:-4] + ".mp3"
                        print(f"[voice] {speaker}: {line[:60]}")
                        tts_elevenlabs(line, spec["voice_id"], mp3, spec.get("voice_settings"))
                        to_wav(mp3, wav, spec.get("speed", 1.0), spec.get("pitch", 1.0))
                    else:
                        if have_key:
                            print(f"[voice] no voice_id for '{speaker}' in cast.json -> silent")
                        silent_wav(wav, estimate_seconds(line))
                dur, mouth = wav_info(wav, fps)
                entry.update(audio=wav, mouth=mouth)
                wj = wav[:-4] + ".words.json"
                if os.path.exists(wj):
                    with open(wj, encoding="utf-8") as f:
                        sp = spec.get("speed", 1.0)
                        entry["words"] = [[w, a / sp, b / sp] for w, a, b in json.load(f)]
                duration = dur + PAD_AFTER
            else:
                duration = 0
            duration = max(duration, shot.get("duration", 0)) + shot.get("hold", 0)
            if duration <= 0:
                duration = 1.5
            entry["duration"] = round(duration, 3)
            shots.append(entry)
            i += 1
    timing = {"fps": fps, "shots": shots, "total": round(sum(s["duration"] for s in shots), 3)}
    with open(os.path.join(build_dir, "timing.json"), "w", encoding="utf-8") as f:
        json.dump(timing, f, indent=1)
    print(f"[voice] {len(shots)} shots, {timing['total']:.1f}s total")
    return timing
