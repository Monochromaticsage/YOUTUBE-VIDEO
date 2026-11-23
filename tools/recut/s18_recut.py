import json, os, shutil, sys
sys.path.insert(0, 'pipeline')
import voice, assemble
R = os.getcwd(); FPS = 30
OLD = f'{R}/build/s18_thankful'; NEW = f'{R}/build/s18_recut'
ep = json.load(open('episodes/shorts/s18_thankful.json'))
cast = json.load(open('episodes/cast.json'))
old_t = json.load(open(f'{OLD}/timing.json'))
shots = [s for sc in ep['scenes'] for s in sc['shots']]

# 1) Hide the rule, plant a promise: "especially Mom"
shots[2]['line'] = "Be VERY careful what you say this Thanksgiving... especially Mom."
# 2) Curiosity stickers
shots[0].setdefault('fx', []).append({"text": "WAIT for Mom's turn...", "color": "#ffd23f", "size": 92, "at": 0.0, "x": 0.5, "y": 0.70, "dur": 2.3, "anim": "pop"})
shots[8].setdefault('fx', []).append({"text": "it gets WORSE...", "color": "#ffffff", "size": 96, "at": 1.0, "x": 0.5, "y": 0.72, "dur": 2.0, "anim": "pop"})
shots[14].setdefault('fx', []).append({"text": "Mom's turn is coming...", "color": "#ffd23f", "size": 88, "at": 1.2, "x": 0.5, "y": 0.74, "dur": 2.0, "anim": "pop"})
shots[18].setdefault('fx', []).append({"e": "😳", "at": 0.3, "x": 0.8, "y": 0.62, "size": 200, "dur": 1.6, "anim": "pop"})

# new build dir: reuse every cached voice line except shot 2
os.makedirs(f'{NEW}/audio', exist_ok=True)
for f in os.listdir(f'{OLD}/audio'):
    if not f.startswith('shot_002'):
        shutil.copy(f'{OLD}/audio/{f}', f'{NEW}/audio/{f}')
for f in os.listdir(f'{NEW}/audio'):
    if f.startswith('shot_002'): os.remove(f'{NEW}/audio/{f}')
t = voice.build(ep, cast, NEW)

# frame mapping (old frames, re-timed)
def counts(tim): return [max(2, round(s['duration'] * FPS)) for s in tim['shots']]
oc, nc = counts(old_t), counts(t)
fr = f'{NEW}/frames'; shutil.rmtree(fr, ignore_errors=True); os.makedirs(fr)
o0, n = 1, 1
for k in range(len(oc)):
    for j in range(nc[k]):
        src = o0 + min(int(j * oc[k] / nc[k]), oc[k] - 1)
        os.symlink(f'{OLD}/frames/frame_{src:04d}.png', f'{fr}/frame_{n:04d}.png'); n += 1
    o0 += oc[k]
for k, s in enumerate(t['shots']): s['duration'] = nc[k] / FPS
t['total'] = sum(s['duration'] for s in t['shots'])
json.dump(t, open(f'{NEW}/timing.json', 'w'), indent=1)
print('shot2 old/new frames', oc[2], nc[2], 'total', n - 1, t['total'])
ep['_chars'] = {}
assemble.assemble(ep, t, cast, NEW, f'{R}/output/s18_thankful_recut.mp4')
json.dump(ep, open(f'{S}/s18_recut_ep.json', 'w'), indent=1, ensure_ascii=False) if (S := os.environ.get('S')) else None
