"""Generates the channel's sound effects and music loops from pure maths.

Everything is synthesised here, so there are no samples, no licences and no copyright claims.
  python pipeline/make_sounds.py              -> assets/sfx/*.wav and assets/music/*.wav
  python pipeline/make_sounds.py --list

Needs only numpy (pip install numpy).
"""
import argparse
import os
import wave

import numpy as np

SR = 44100
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
rng = np.random.default_rng(7)


# ------------------------------------------------------------------ helpers
def t_(dur):
    return np.arange(int(dur * SR)) / SR


def env_exp(dur, tau, attack=0.003):
    t = t_(dur)
    e = np.exp(-t / tau)
    a = int(attack * SR)
    if a:
        e[:a] *= np.linspace(0, 1, a)
    return e


def sweep(f0, f1, dur, curve="exp"):
    t = t_(dur)
    if curve == "exp":
        f = f0 * (f1 / f0) ** (t / dur)
    else:
        f = f0 + (f1 - f0) * t / dur
    return np.sin(2 * np.pi * np.cumsum(f) / SR)


def saw(freq, dur, vib=0.0, vib_rate=5.0):
    t = t_(dur)
    f = freq * (1 + vib * np.sin(2 * np.pi * vib_rate * t))
    ph = np.cumsum(f) / SR
    return 2 * (ph % 1.0) - 1


def noise(dur):
    return rng.uniform(-1, 1, int(dur * SR))


def lowpass(x, cutoff):
    """One-pole lowpass; cutoff may be a number or an array (sweeping filter)."""
    c = np.broadcast_to(np.asarray(cutoff, float), x.shape)
    a = np.exp(-2 * np.pi * c / SR)
    y = np.empty_like(x)
    acc = 0.0
    for i in range(len(x)):  # small sounds only - fine in pure python
        acc = (1 - a[i]) * x[i] + a[i] * acc
        y[i] = acc
    return y


def lp_fast(x, cutoff):
    """Fixed-cutoff lowpass via FFT (for long music buffers)."""
    X = np.fft.rfft(x)
    f = np.fft.rfftfreq(len(x), 1 / SR)
    X *= 1 / np.sqrt(1 + (f / cutoff) ** 4)
    return np.fft.irfft(X, len(x))


def hp_fast(x, cutoff):
    X = np.fft.rfft(x)
    f = np.fft.rfftfreq(len(x), 1 / SR)
    X *= 1 - 1 / np.sqrt(1 + (f / cutoff) ** 4)
    return np.fft.irfft(X, len(x))


def reverb(x, decay=1.2, mix=0.25):
    n = int(decay * SR)
    ir = rng.uniform(-1, 1, n) * np.exp(-np.arange(n) / SR / (decay / 5))
    ir = lp_fast(ir, 6000)
    ir /= np.sqrt(np.sum(ir ** 2)) + 1e-9
    L = len(x) + n
    wet = np.fft.irfft(np.fft.rfft(x, L) * np.fft.rfft(ir, L), L)
    dry = np.concatenate([x, np.zeros(n)])
    return (1 - mix) * dry + mix * wet


def pad(x, dur):
    n = int(dur * SR)
    return np.concatenate([x, np.zeros(max(0, n - len(x)))])[:n] if n else x


def mix_at(buf, x, at):
    i = int(at * SR)
    end = min(len(buf), i + len(x))
    buf[i:end] += x[:end - i]
    return buf


def norm(x, peak=0.89):
    m = np.max(np.abs(x)) + 1e-9
    return x / m * peak


def fade(x, fin=0.005, fout=0.05):
    a, b = int(fin * SR), int(fout * SR)
    x = x.copy()
    if a:
        x[:a] *= np.linspace(0, 1, a)
    if b:
        x[-b:] *= np.linspace(1, 0, b)
    return x


def save(path, x, trim=True):
    x = np.clip(x, -1, 1)
    if trim:  # drop the silent end of reverb tails
        loud = np.nonzero(np.abs(x) > 0.003)[0]
        if len(loud):
            end = min(len(x), loud[-1] + int(0.05 * SR))
            x = x[:end]
            k = min(len(x), int(0.05 * SR))
            x[-k:] *= np.linspace(1, 0, k)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with wave.open(path, "wb") as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(SR)
        w.writeframes((x * 32767).astype("<i2").tobytes())


def midi(n):
    return 440.0 * 2 ** ((n - 69) / 12)


# ------------------------------------------------------------- sound effects
def vine_boom():
    """Deep dramatic 'BOOM' for reveals."""
    body = sweep(110, 38, 1.6) * env_exp(1.6, 0.45)
    sub = sweep(60, 30, 1.6) * env_exp(1.6, 0.6)
    click = lowpass(noise(0.03), 2500) * env_exp(0.03, 0.008)
    x = np.tanh(2.5 * (body + 0.7 * sub)) + pad(click, 1.6) * 2
    return fade(norm(reverb(x, 1.8, 0.3)), 0.001, 0.3)


def sting():
    """Dramatic shock chord (the 'gasp' moment)."""
    d = 2.2
    x = np.zeros(int(d * SR))
    for n in (45, 46, 52, 58, 63):  # dissonant cluster
        x += saw(midi(n), d, 0.004, 6) * env_exp(d, 0.7)
    x = lp_fast(x, 2200) * 0.4 + 0.8 * pad(vine_boom(), d)
    return fade(norm(reverb(x, 2.0, 0.35)), 0.001, 0.4)


def sad_trombone():
    """'Wah wah wah waaah' for fails."""
    notes = [(62, 0.42), (61, 0.42), (60, 0.42), (59, 1.3)]
    out = []
    for i, (n, d) in enumerate(notes):
        vib = 0.018 if i == 3 else 0.006
        s = saw(midi(n - 12), d, vib, 6.5)
        e = np.minimum(1, t_(d) / 0.05) * np.minimum(1, (d - t_(d)) / 0.08)
        out.append(lowpass(s * e, 1300))
    return fade(norm(reverb(np.concatenate(out), 0.8, 0.15)))


def record_scratch():
    d = 0.7
    t = t_(d)
    f = 300 + 900 * np.abs(np.sin(2 * np.pi * 3.2 * t)) * np.exp(-t * 1.5)
    s = np.sin(2 * np.pi * np.cumsum(f) / SR) * 0.5 + lowpass(noise(d), f * 2) * 0.9
    e = np.minimum(1, t / 0.01) * np.exp(-t * 2.5)
    return fade(norm(s * e))


def airhorn():
    """Party horn blasts: baa - baa - baaaaa."""
    def blast(d):
        x = sum(saw(f, d, 0.003, 9) for f in (466, 470, 233, 699))
        e = np.minimum(1, t_(d) / 0.02) * np.minimum(1, (d - t_(d)) / 0.04)
        return np.tanh(1.8 * lowpass(x, 3500) * e)
    buf = np.zeros(int(1.9 * SR))
    for at, d in ((0, 0.18), (0.25, 0.18), (0.5, 1.2)):
        mix_at(buf, blast(d), at)
    return fade(norm(reverb(buf, 0.6, 0.12)))


def thud(freq=120, d=0.5):
    body = sweep(freq, freq * 0.4, d) * env_exp(d, 0.09)
    hit = lowpass(noise(d), 900) * env_exp(d, 0.03)
    return norm(np.tanh(2 * (body + 0.6 * hit)))


def oof_thud():
    return fade(norm(reverb(thud(140, 0.6), 0.5, 0.15)))


def door_knock():
    buf = np.zeros(int(1.2 * SR))
    for at in (0.0, 0.22, 0.44):
        mix_at(buf, thud(210, 0.18) * 0.9, at)
    return fade(norm(reverb(buf, 0.5, 0.2)))


def door_slam():
    x = pad(thud(80, 0.9), 1.4) + pad(lowpass(noise(0.15), 3000) * env_exp(0.15, 0.04), 1.4) * 0.6
    return fade(norm(reverb(x, 1.2, 0.3)))


def whoosh():
    d = 0.8
    t = t_(d)
    bell = np.sin(np.pi * t / d) ** 2
    cut = 300 + 3500 * bell
    return fade(norm(lowpass(noise(d), cut) * bell))


def pop():
    d = 0.12
    return fade(norm(sweep(500, 1400, d) * env_exp(d, 0.03)), 0.001, 0.02)


def boing():
    d = 0.9
    t = t_(d)
    f = 180 * (1 + 0.6 * np.exp(-t * 4) * np.sin(2 * np.pi * 9 * t)) * (1 + t * 0.4)
    s = np.sin(2 * np.pi * np.cumsum(f) / SR)
    return fade(norm(s * env_exp(d, 0.3)))


def bell_tone(freq, d, tau=0.9):
    partials = [(1, 1), (2.0, 0.6), (2.76, 0.4), (5.4, 0.25), (8.9, 0.1)]
    x = sum(a * np.sin(2 * np.pi * freq * r * t_(d)) * env_exp(d, tau / r ** 0.5) for r, a in partials)
    return x


def ding():
    return fade(norm(reverb(bell_tone(1320, 1.6), 1.0, 0.2)))


def school_bell():
    d = 2.4
    t = t_(d)
    x = bell_tone(900, d, 2.0) * (0.6 + 0.4 * np.sign(np.sin(2 * np.pi * 14 * t)))
    return fade(norm(reverb(x, 1.2, 0.25)), 0.002, 0.4)


def sparkle():
    """Magic shimmer."""
    d = 1.8
    buf = np.zeros(int(d * SR))
    scale = [84, 86, 88, 91, 93, 96, 98, 100]
    for i in range(22):
        n = scale[rng.integers(len(scale))]
        tone = np.sin(2 * np.pi * midi(n) * t_(0.5)) * env_exp(0.5, 0.12)
        mix_at(buf, tone * rng.uniform(0.3, 1), i * 0.06 + rng.uniform(0, 0.03))
    return fade(norm(reverb(buf, 1.5, 0.45)))


def freeze():
    """Ice crackle plus a falling chime (for Freeze Tag and other magic rules)."""
    d = 1.6
    buf = np.zeros(int(d * SR))
    for _ in range(60):
        at = rng.uniform(0, 0.9)
        c = lowpass(noise(0.02), 7000) * env_exp(0.02, 0.004)
        mix_at(buf, np.diff(np.concatenate([[0], c])) * 3, at)
    for i, n in enumerate((96, 91, 88, 84)):
        mix_at(buf, bell_tone(midi(n), 0.9, 0.5) * 0.35, 0.15 + i * 0.12)
    return fade(norm(reverb(buf, 1.4, 0.35)))


def glitch():
    d = 0.9
    x = np.zeros(int(d * SR))
    i = 0
    while i < len(x):
        seg = int(rng.uniform(0.02, 0.09) * SR)
        kind = rng.integers(3)
        tt = np.arange(seg) / SR
        if kind == 0:
            s = np.sign(np.sin(2 * np.pi * rng.uniform(80, 900) * tt))
        elif kind == 1:
            s = np.round(rng.uniform(-1, 1, seg) * 3) / 3
        else:
            s = np.zeros(seg)
        x[i:i + seg] = s[:len(x) - i] * 0.7
        i += seg
    return fade(norm(x))


def heartbeat():
    buf = np.zeros(int(2.0 * SR))
    for beat in (0, 1.0):
        mix_at(buf, thud(65, 0.25), beat)
        mix_at(buf, thud(55, 0.25) * 0.7, beat + 0.28)
    return norm(lp_fast(buf, 400))


def tick_tock():
    buf = np.zeros(int(2.0 * SR))
    for i in range(4):
        f = 3200 if i % 2 == 0 else 2500
        click = np.sin(2 * np.pi * f * t_(0.02)) * env_exp(0.02, 0.003)
        mix_at(buf, click, i * 0.5)
    return norm(reverb(buf, 0.3, 0.2))


def riser():
    """Builds tension for 2.5 s, then cuts. Put it right before a reveal."""
    d = 2.5
    t = t_(d)
    amp = (t / d) ** 2
    s = sweep(180, 1400, d) * 0.5 + lowpass(noise(d), 500 + 6000 * t / d) * 0.6
    return norm(s * amp)


def footsteps():
    buf = np.zeros(int(2.0 * SR))
    for i in range(5):
        mix_at(buf, lowpass(noise(0.08), 700) * env_exp(0.08, 0.02), i * 0.38)
    return norm(reverb(buf, 0.4, 0.15))


def notification():
    buf = np.zeros(int(0.7 * SR))
    mix_at(buf, bell_tone(1568, 0.4, 0.2), 0)
    mix_at(buf, bell_tone(2093, 0.4, 0.2), 0.12)
    return fade(norm(buf))


def cash():
    buf = np.zeros(int(1.0 * SR))
    for i in range(6):
        mix_at(buf, bell_tone(midi(rng.integers(90, 100)), 0.5, 0.15) * 0.6, i * 0.04)
    mix_at(buf, ding() * 0.8, 0.25)
    return fade(norm(buf))


SFX = {
    "vine_boom": vine_boom, "sting": sting, "sad_trombone": sad_trombone, "record_scratch": record_scratch,
    "airhorn": airhorn, "oof_thud": oof_thud, "door_knock": door_knock, "door_slam": door_slam,
    "whoosh": whoosh, "pop": pop, "boing": boing, "ding": ding, "school_bell": school_bell,
    "sparkle": sparkle, "freeze": freeze, "glitch": glitch, "heartbeat": heartbeat, "tick_tock": tick_tock,
    "riser": riser, "footsteps": footsteps, "notification": notification, "cash": cash,
}


# -------------------------------------------------------------------- music
def ep_note(freq, d, bright=1.0):
    """Soft electric-piano-ish note."""
    t = t_(d)
    x = np.sin(2 * np.pi * freq * t) + 0.35 * bright * np.sin(2 * np.pi * 2 * freq * t) * np.exp(-t * 3)
    x += 0.15 * bright * np.sin(2 * np.pi * 3 * freq * t) * np.exp(-t * 6)
    return x * np.exp(-t / (0.9 * d + 0.2)) * np.minimum(1, t / 0.01)


def pluck(freq, d):
    t = t_(d)
    x = saw(freq, d) * np.exp(-t * 7)
    return lp_fast(x, 2500) * 0.8 + np.sin(2 * np.pi * freq * t) * np.exp(-t * 4) * 0.6


def pad_chord(notes, d):
    x = sum(saw(midi(n), d, 0.002, 4.5 + i * 0.3) for i, n in enumerate(notes))
    e = np.minimum(1, t_(d) / 0.6) * np.minimum(1, (d - t_(d)) / 0.6)
    return lp_fast(x * e, 900) * 0.25


def kick():
    return thud(95, 0.35) * 0.9


def snare():
    d = 0.2
    return (lowpass(noise(d), 5000) * env_exp(d, 0.05) + np.sin(2 * np.pi * 190 * t_(d)) * env_exp(d, 0.04) * 0.5)


def hat():
    return hp_fast(noise(0.05), 7000) * env_exp(0.05, 0.012) * 0.6


def drums(buf, bpm, bars, pattern):
    beat = 60 / bpm
    for bar in range(bars):
        for step, kinds in enumerate(pattern):  # 8 steps per bar (eighth notes)
            at = (bar * 8 + step) * beat / 2
            for k in kinds:
                mix_at(buf, {"k": kick, "s": snare, "h": hat}[k]() * {"k": 0.8, "s": 0.45, "h": 0.25}[k], at)


def song(bpm, bars, chords, voice, drum_pattern=None, arp=False, pad=False, melody=None, cutoff=8000, swing=0.0):
    beat = 60 / bpm
    total = bars * 4 * beat
    buf = np.zeros(int((total + 2) * SR))
    for bar in range(bars):
        ch = chords[bar % len(chords)]
        t0 = bar * 4 * beat
        if pad:
            mix_at(buf, pad_chord(ch, 4 * beat), t0)
        if arp:
            for i in range(8):
                n = ch[i % len(ch)] + (12 if i >= 4 else 0)
                at = t0 + i * beat / 2 + (swing * beat / 2 if i % 2 else 0)
                mix_at(buf, voice(midi(n), beat * 0.9) * 0.35, at)
        else:
            for hit in (0, 2.5) if voice is ep_note else (0,):
                for n in ch:
                    mix_at(buf, voice(midi(n), beat * 1.6) * 0.22, t0 + hit * beat)
        mix_at(buf, ep_note(midi(ch[0] - 12), 4 * beat, 0.3) * 0.5, t0)  # bass
    if melody:
        for at_beats, n, dur in melody:
            mix_at(buf, ep_note(midi(n), dur * beat, 1.2) * 0.3, at_beats * beat)
    if drum_pattern:
        drums(buf, bpm, bars, drum_pattern)
    buf = lp_fast(buf, cutoff)
    # make it loop seamlessly: fold the reverb tail back onto the start
    n = int(total * SR)
    tail = buf[n:]
    buf = buf[:n]
    buf[:len(tail)] += tail
    return norm(buf, 0.8)


LOFI = [("h",), ("h",), ("s", "h"), ("h",), ("k", "h"), ("k", "h"), ("s", "h"), ("h",)]
LOFI[0] = ("k", "h")
BOUNCE = [("k", "h"), ("h",), ("s", "h"), ("h",), ("k", "h"), ("k", "h"), ("s", "h"), ("h", "s")]


def music_chill():
    ch = [[60, 64, 67, 71], [57, 60, 64, 67], [53, 57, 60, 64], [55, 59, 62, 65]]  # Cmaj7 Am7 Fmaj7 G7
    return song(84, 8, ch, ep_note, LOFI, cutoff=5000)


def music_happy():
    ch = [[60, 64, 67], [55, 59, 62], [57, 60, 64], [53, 57, 60]]  # C G Am F
    mel = [(i * 2, n, 1.5) for i, n in enumerate([72, 74, 76, 79, 76, 74, 72, 71, 72, 76, 79, 81, 79, 76, 74, 72])]
    return song(112, 8, ch, pluck, BOUNCE, arp=True, melody=mel, cutoff=9000, swing=0.15)


def music_mystery():
    ch = [[57, 60, 64], [53, 57, 60], [50, 53, 57], [52, 56, 59]]  # Am F Dm E
    return song(72, 8, ch, pluck, [("k",), (), (), ("h",), (), (), ("k",), ("h",)], arp=True, pad=True, cutoff=4000)


def music_sad():
    ch = [[57, 60, 64], [53, 57, 60], [48, 52, 55], [55, 59, 62]]  # Am F C G
    mel = [(0, 76, 3), (4, 72, 3), (8, 72, 2), (10, 74, 2), (12, 71, 4),
           (16, 76, 3), (20, 77, 3), (24, 76, 2), (26, 74, 2), (28, 72, 4)]
    return song(64, 8, ch, ep_note, None, pad=True, melody=mel, cutoff=4500)


def music_tension():
    bpm, bars = 90, 8
    beat = 60 / bpm
    total = bars * 4 * beat
    buf = np.zeros(int(total * SR))
    t = t_(total)
    drone = (saw(midi(33), total, 0.003, 0.2) + saw(midi(40), total, 0.004, 0.3)) * 0.3
    buf += lp_fast(drone, 300)
    for i in range(int(total / beat)):
        mix_at(buf, thud(60, 0.3) * (0.7 if i % 2 == 0 else 0.4), i * beat)
        mix_at(buf, np.sin(2 * np.pi * 2600 * t_(0.02)) * env_exp(0.02, 0.003) * 0.2, i * beat + beat / 2)
    return norm(buf, 0.8)


# ---- "quirky_loop": playful sneaky-comedy track (marimba, pizzicato bass, glockenspiel, light drums)
def marimba(freq, d):
    t = t_(d)
    x = np.sin(2 * np.pi * freq * t) * np.exp(-t * 7) + 0.25 * np.sin(2 * np.pi * 4 * freq * t) * np.exp(-t * 30)
    x += 0.1 * np.sin(2 * np.pi * 10 * freq * t) * np.exp(-t * 60)
    return x * np.minimum(1, t / 0.002)


def glock(freq, d):
    t = t_(d)
    x = np.sin(2 * np.pi * freq * t) * np.exp(-t * 2.5) + 0.35 * np.sin(2 * np.pi * 2.76 * freq * t) * np.exp(-t * 9)
    return x * np.minimum(1, t / 0.001)


def pizz_bass(freq, d):
    t = t_(d)
    body = np.sin(2 * np.pi * freq * t) + 0.3 * np.sin(2 * np.pi * 2 * freq * t)
    return lp_fast(body + 0.2 * saw(freq, d), 1200) * np.exp(-t * 6) * np.minimum(1, t / 0.004)


def clap():
    d = 0.18
    x = np.zeros(int(d * SR))
    for k, off in enumerate((0, 0.011, 0.022)):
        mix_at(x, hp_fast(noise(0.12), 900) * env_exp(0.12, 0.03) * (0.6 if k < 2 else 1.0), off)
    return x


def music_quirky():
    bpm, bars = 116, 16
    beat = 60 / bpm
    total = bars * 4 * beat
    buf = np.zeros(int((total + 2) * SR))
    # F  Dm  Bb  C  | F  Dm  G7  C   (A: bars 0-7, B with melody: bars 8-15)
    prog = [(53, [65, 69, 72]), (50, [62, 65, 69]), (46, [62, 65, 70]), (48, [64, 67, 72]),
            (53, [65, 69, 72]), (50, [62, 65, 69]), (43, [62, 65, 71]), (48, [64, 67, 70])]
    walk = [0, 7, 12, 7]  # bass: root, fifth, octave, fifth
    for bar in range(bars):
        root, ch = prog[bar % 8]
        t0 = bar * 4 * beat
        for b in range(4):  # bouncy pizzicato bass on every beat
            n = root + walk[b] - 12
            mix_at(buf, pizz_bass(midi(n), beat * 0.8) * 0.55, t0 + b * beat)
        for b in range(4):  # marimba stabs on the off-beats ("and" of each beat)
            for k, n in enumerate(ch):
                mix_at(buf, marimba(midi(n), beat * 0.5) * 0.16, t0 + b * beat + beat / 2 + k * 0.004)
        if bar % 2 == 1:  # little marimba run up at the end of every other bar
            for k, n in enumerate(ch + [ch[0] + 12]):
                mix_at(buf, marimba(midi(n + 12), 0.25) * 0.12, t0 + 3 * beat + k * beat / 4)
        # drums: soft kick 1 & 3, claps 2 & 4 in B section, shaker 16ths
        for b in range(4):
            if b in (0, 2):
                mix_at(buf, kick() * 0.45, t0 + b * beat)
            if b in (1, 3) and bar >= 8:
                mix_at(buf, clap() * 0.35, t0 + b * beat)
            for q in range(4):
                mix_at(buf, hat() * (0.16 if q % 2 else 0.08), t0 + b * beat + q * beat / 4)
    # glockenspiel melody in the B section (two 4-bar phrases), sneaky and catchy
    phrase = [(0, 77, .5), (.5, 76, .5), (1, 74, .5), (1.5, 72, 1), (3, 69, .5), (3.5, 72, .5),
              (4, 74, .5), (4.5, 74, .5), (5, 77, 1), (6.5, 74, .5), (7, 72, 1),
              (8, 70, .5), (8.5, 72, .5), (9, 74, .5), (9.5, 70, 1), (11, 67, .5), (11.5, 70, .5),
              (12, 72, .5), (12.5, 76, .5), (13, 79, 1.5), (15, 72, .5), (15.5, 76, .5)]
    for rep in (0, 1):
        for at_b, n, dl in phrase:
            when = (8 * 4 + rep * 16 + at_b) * beat
            mix_at(buf, glock(midi(n + 12), dl * beat + 0.6) * 0.2, when)
            if rep == 1:
                mix_at(buf, marimba(midi(n), dl * beat) * 0.1, when)
    buf = reverb(buf, decay=0.6, mix=0.12)
    n = int(total * SR)
    tail = buf[n:]
    buf = buf[:n]
    buf[:len(tail)] += tail
    return norm(buf, 0.8)


MUSIC = {"chill_loop": music_chill, "happy_loop": music_happy, "mystery_loop": music_mystery,
         "sad_loop": music_sad, "tension_loop": music_tension,
         "quirky_loop": music_quirky}


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--list", action="store_true")
    p.add_argument("--only", default="")
    args = p.parse_args()
    if args.list:
        print("SFX:  ", ", ".join(SFX))
        print("MUSIC:", ", ".join(MUSIC))
        return
    only = set(args.only.split(",")) if args.only else None
    for name, fn in SFX.items():
        if only and name not in only:
            continue
        save(os.path.join(ROOT, "assets", "sfx", f"{name}.wav"), fn())
        print("sfx  ", name)
    for name, fn in MUSIC.items():
        if only and name not in only:
            continue
        save(os.path.join(ROOT, "assets", "music", f"{name}.wav"), fn(), trim=False)
        print("music", name)


if __name__ == "__main__":
    main()
