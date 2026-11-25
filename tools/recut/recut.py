"""Re-time an already rendered Short with new VO lines / stickers, no re-render.
usage: python tools/recut/recut.py <config.json>
config: {"id": "...", "out": "..._recut", "lines": {"3": "new vo line"}, "fx": {"0": [ {...sticker...} ]}}
Only change lines of VO shots (no lip-sync). Frames of a re-timed shot are stretched/squeezed."""
import json, os, shutil, sys
sys.path.insert(0, 'pipeline')
import voice, assemble
R = os.getcwd(); FPS = 30
cfg = json.load(open(sys.argv[1]))
OLD = f"{R}/build/{cfg['id']}"; NEW = f"{R}/build/{cfg['out']}"
ep = json.load(open(f"episodes/shorts/{cfg['id']}.json"))
cast = json.load(open('episodes/cast.json'))
old_t = json.load(open(f'{OLD}/timing.json'))
shots = [s for sc in ep['scenes'] for s in sc['shots']]
for k, line in cfg.get('lines', {}).items():
    assert shots[int(k)].get('vo') or not shots[int(k)].get('speaker'), f'shot {k} is not VO'
    shots[int(k)]['line'] = line
for k, fx in cfg.get('fx', {}).items():
    shots[int(k)].setdefault('fx', []).extend(fx)
os.makedirs(f'{NEW}/audio', exist_ok=True)
changed = {f'shot_{int(k):03d}' for k in cfg.get('lines', {})}
for f in os.listdir(f'{NEW}/audio'):
    os.remove(f'{NEW}/audio/{f}')
for f in os.listdir(f'{OLD}/audio'):
    if f[:8] not in changed:
        shutil.copy(f'{OLD}/audio/{f}', f'{NEW}/audio/{f}')
t = voice.build(ep, cast, NEW)
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
starts, a = [], 0
for s in t['shots']: starts.append(round(a, 2)); a += s['duration']
print('starts', {k: starts[int(k)] for k in list(cfg.get('lines', {})) + list(cfg.get('fx', {}))}, 'total', round(t['total'], 1))
ep['_chars'] = {}
assemble.assemble(ep, t, cast, NEW, f"{R}/output/{cfg['out']}.mp4")
