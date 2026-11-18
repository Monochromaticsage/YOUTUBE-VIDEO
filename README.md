# Roblox-style 3D animation factory (Blender + Claude Code)

Write a short as a JSON script, then run one command to get a finished vertical MP4
with 3D blocky characters, sets, camera cuts, expressions, lip-flap, voices,
sound effects and captions.

```
episodes/shorts/short_001.json  ->  python pipeline/make_episode.py ...  ->  output/short_001.mp4
```

## Setup (Windows PC, one time)

1. Install **Blender** (free, blender.org). It is found automatically in `C:\Program Files\Blender Foundation\`,
   or set `BLENDER=C:\path\to\blender.exe`.
2. Install **ffmpeg** (`winget install ffmpeg`) and **Python 3.10+**.
3. Optional: an **ElevenLabs** API key for voices. Without one you get silent placeholder clips, which are fine for previews.
   ```bash
   setx ELEVENLABS_API_KEY "your-key"
   ```
   Then paste a `voice_id` for each character in `episodes/cast.json`.

## Make a video

```bash
python pipeline/make_episode.py episodes/shorts/short_001.json --preview
```

```bash
python pipeline/make_episode.py episodes/shorts/short_001.json
```

```bash
python pipeline/make_episode.py "episodes/shorts/*.json"
```

- `--preview` renders at half resolution, which is quick for checking timing.
- `--save-blend` also saves `build/<id>/scene.blend` so you can open the scene in Blender and tweak it by hand.
- `--engine cycles` gives higher quality but is slower. EEVEE (the default) needs a graphics card.

## Writing an episode

```json
{
  "id": "short_008", "title": "...", "format": "short",
  "music": "chill_loop",
  "scenes": [{
    "set": "classroom",
    "cast": {"noob": "left", "bacon": "right"},
    "shots": [
      {"speaker": "noob", "line": "Hello!", "face": "happy", "camera": "closeup:noob",
       "anims": {"bacon": "wave"}, "faces": {"bacon": "smug"}, "sfx": "vine_boom", "move": "push"},
      {"duration": 1.2, "camera": "extreme:bacon", "move": "shake", "faces": {"bacon": "shocked"}}
    ]
  }]
}
```

| Field | Options |
|---|---|
| `format` | `short` (1080x1920) or `long` (1920x1080). A long video is just more `scenes`. |
| `set` | `classroom` `hallway` `bedroom` `kitchen` `outdoors` `stage`, or your own map at `assets/sets/<name>.fbx` |
| marks (`cast`) | `far_left` `left` `center` `right` `far_right` `back_left` `back` `back_right`, plus `teacher` and `board` in the classroom |
| `face` / `faces` | `neutral` `happy` `smug` `angry` `sad` `shocked` `scared` `sus` `cry` `dead` `evil` `love` |
| `anims` | `idle` `talk` `shocked` `scared` `angry` `laugh` `sad` `cry` `wave` `point` `facepalm` `think` `dance` `jump` `fall` `lie` `sit` `run_in_place` `walk_in_left/right` `walk_out_left/right` `run_out_left/right` `hidden` |
| `camera` | `wide` `medium:X` `closeup:X` `extreme:X` `two:X,Y` `ots:X,Y` `low:X` `high:X` |
| `move` | `push` (default) `pull` `pan` `zoom` `shake` `none` |
| `sfx` | the name of a file in `assets/sfx/` (e.g. `vine_boom.mp3`) |
| `hold` / `duration` | extra seconds after the line, or the length of a shot with no dialogue |
| `audio_file` | use your own recorded line instead of ElevenLabs |

The speaker automatically gets `talk` and lip-flap. Everyone else gets `idle` unless you say otherwise.

## Making it look more like your channel

- **Faces:** drop PNGs (transparent, square) into `assets/faces/` named `happy.png`, `happy_open.png`, and so on to replace the drawn faces.
- **Characters:** colours, hair (`block` `bacon` `long` `cap`), sleeves and glasses are set in `episodes/cast.json`.
- **Maps:** in Roblox Studio, right-click a model and choose *Export Selection*, then save it as `assets/sets/myschool.fbx` and use `"set": "myschool"`.
- **Sounds and music:** put files in `assets/sfx/` and `assets/music/`.

## How it works

| File | Job |
|---|---|
| `pipeline/voice.py` | Generates voice lines, measures their length, and builds the lip-flap track (`build/<id>/timing.json`) |
| `pipeline/blender/render_episode.py` | Builds the scene in Blender, keys the camera, animation and faces, and renders PNG frames |
| `pipeline/blender/rig.py` | Blocky R6 characters and the face atlas |
| `pipeline/blender/anims.py` | The move library. Add new moves here. |
| `pipeline/blender/sets.py` | The set library |
| `pipeline/assemble.py` | Uses ffmpeg to combine frames, dialogue, sound effects, music and captions into an MP4 |
