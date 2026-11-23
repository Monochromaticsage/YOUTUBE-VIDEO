"""Writes docs/upload/<id>.md for S18-S29 from the episode JSON plus the copy below."""
import json, os
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
BASE_TAGS = "plutonex tales, roblox animation, roblox story, funny animation, animated story, roblox shorts, 3d animation, funny shorts, story time animation, comedy animation"
META = {
 "s18_thankful": ("This Thanksgiving, whatever you say you're thankful for... DISAPPEARS 🦃💨\nMy phone. Grandpa's teeth. Every homework in the WORLD. Goldie's money 💀\nThen Mom said she was thankful for peace and quiet... 😳",
                  "thanksgiving, thankful, whatever you say disappears, thanksgiving story, family comedy, grandpa, little sister, homework, plot twist, holiday"),
 "s19_pause_time": ("I can PAUSE time ⏸️ Everyone freezes... except me.\nFree A-plus, a clown nose for Goldie, Mom's secret chocolate 🍫\nBut my little sister never froze. Not even once 👀",
                    "i can pause time, time stop, freeze time, superpower story, little sister, plot twist, school story, clown nose, prank"),
 "s20_comes_true": ("In this world, whatever you say comes TRUE... 10 seconds later ⏳\nNoob wished for raining pizza 🍕 Ms. Brick said we drive her BANANAS 🍌\nThen my sister wished I was a chicken 🐔",
                    "whatever you say comes true, in this world, wish comes true, raining pizza, chicken dance, superpower story, school story, little sister"),
 "s21_invisible": ("I turned INVISIBLE... and nobody noticed 👻\nThe teacher marked me absent. AGAIN. Grandpa ate my dinner. Mom replied 'that's nice, sweetie' 💀\nThen my little sister looked RIGHT at me...",
                   "i turned invisible, invisible, nobody noticed, superpower story, little sister, family comedy, school story, plot twist"),
 "s22_bacon_speaks": ("Bacon has NEVER said a single word. 2,847 days 🤐\nGoldie offered him $100. Noob thought he was a robot.\nThen he finally spoke... 😳🎙️",
                      "quiet kid speaks, the quiet kid, bacon, deep voice, school story, movie trailer voice, plot twist, classroom"),
 "s23_cool_dad": ("My dad came to school to be COOL 😎\nHe dabbed. He called Goldie's chain 'bussin'. He asked the teacher for a bathroom pass 💀\nThen he challenged Noob to a dance battle...",
                  "cool dad, embarrassing dad, dad at school, dab, dance battle, backflip, dad jokes, family comedy, school story"),
 "s24_santa_mixup": ("Santa mixed up EVERYONE'S presents 🎁\nI got a unicorn dress. Grandpa got a baby bottle (he kept it). Goldie got a banana 🍌\nThen I found Santa's list... written in CRAYON 🖍️",
                     "christmas, santa, christmas presents, santa mixed up presents, christmas story, worst present, little sister, holiday, plot twist"),
 "s25_elf_spy": ("Our Elf on the Shelf is SPYING for Mom 🎄🕵️\nCookies, cat videos, drawing on the wall... he reports EVERYTHING. Live.\nUntil he reported on MOM 😳🍪",
                 "elf on the shelf, christmas, elf spy, snitch, christmas story, mom story, family comedy, breaking news, holiday"),
 "s26_body_swap": ("I swapped bodies with my little sister 😱\nShe got my A-plus test. I got NAP TIME. And a 7 o'clock bedtime 💀\nThen Mom started talking like Grandpa...",
                   "body swap, swapped bodies, little sister, freaky friday, family comedy, school story, plot twist, sibling story"),
 "s27_grandpa_babysit": ("Grandpa babysat us for ONE day. He lasted two seconds 💤\nPizza for breakfast. Noob as a butler. My sister faking Grandpa's voice on the phone 😂\nBut Grandpa was hiding something...",
                         "grandpa babysitting, babysitter, worst babysitter, grandpa, little sister, family comedy, pizza for breakfast, plot twist"),
 "s28_goldie_broke": ("Goldie, the richest kid in school, lost ALL his money 😳💸\nNow he lives at my house. He's never used a spoon. Grandpa gave him a whole dollar 🥹\nThen we found out where the money went...",
                      "rich kid loses money, rich kid, goldie, rich vs poor, wholesome, friendship, family comedy, plot twist"),
 "s29_teacher_kid": ("Our teacher drank Noob's mystery juice... and turned into a KID 😱🧃\nShe refused homework. Goldie became the teacher. RECESS FOREVER 🎉\nThen the juice wore off...",
                     "teacher turned into a kid, teacher, mystery juice, school story, classroom, recess, plot twist, noob"),
}
for eid, (desc, tags) in META.items():
    ep = json.load(open(os.path.join(ROOT, "episodes", "shorts", f"{eid}.json"), encoding="utf-8"))
    title = ep["title"]
    pin = ep.get("_pinned_comment", "")
    secret = ep.get("_secret", "")
    loop = ep.get("_loop", "")
    md = f"""# Upload pack: {title}

- **Video:** `media/shorts/{eid}.mp4` (seamless loop: {loop})
- **Thumbnail:** `branding/{eid}_thumbnail.jpg`
- **Settings:** Not made for kids · Film & Animation · Altered content: Yes · Comments on · Related video: My Sister Copied EVERYTHING I Did

**Title**
```
{title}
```

**Description**
```
{desc}

Watch the first second again... 👀

New Plutonex Tales stories every day! Subscribe so you don't miss the next one 🔔

#shorts #animation #roblox #robloxanimation #story #funny #plutonextales
```

**Tags**
```
{BASE_TAGS}, {tags}
```

**Pinned comment**
```
{pin}
```

**Secret for replies:** {secret}. When someone spots it, reply with a 👀 and a question back to keep the thread going.
"""
    open(os.path.join(ROOT, "docs", "upload", f"{eid}.md"), "w", encoding="utf-8").write(md)
print("wrote", len(META))
