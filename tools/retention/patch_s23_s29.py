"""Retention pass on S23-S29 (before rendering): curiosity promise at 0:00,
explanation VO rewritten to hide the twist, mid-video re-hook stickers, curiosity titles.
Text stickers never contain emoji (they render as boxes) - emoji go in their own sticker."""
import json
def T(text, at, dur, color="#ffd23f", em=None):
    size = min(92, int(1700 / len(text)))
    out = [{"text": text, "color": color, "size": size, "at": at, "x": 0.5, "y": 0.72, "dur": dur, "anim": "pop"}]
    if em: out.append({"e": em, "at": at + 0.15, "x": 0.5, "y": 0.63, "size": 150, "dur": dur - 0.15, "anim": "pop"})
    return out
P = {
 "s23_cool_dad": dict(title="My Dad Tried to Be COOL at My School... Wait for Lunch 😳",
   lines={1: "This is my dad. He came to school to be COOL. It did NOT go how I expected."},
   fx={0: T("Wait till lunch...", 0.0, 1.8, em="😳"), 7: T("wait for it...", 0.4, 1.8, "#ffffff", "👀")}),
 "s24_santa_mixup": dict(title="Someone Mixed Up EVERYONE'S Christmas Presents... 🎁👀",
   lines={2: "This Christmas... everyone got the WRONG present. And I was gonna find out WHY."},
   fx={0: T("Wait till you see WHO did it...", 0.0, 1.8, em="🎅"), 7: T("but WHO mixed them up?", 0.4, 1.8, "#ffffff", "🤔")}),
 "s25_elf_spy": dict(title="Our Elf on the Shelf Is a SNITCH... Wait for the LAST Report 😳",
   lines={2: "Our elf on the shelf reports EVERYTHING to Mom. Everything... about EVERYONE."},
   fx={0: T("Wait for the LAST breaking news...", 0.0, 1.9, em="📺"), 9: T("but the elf isn't done...", 0.6, 1.8, "#ffffff", "👀")}),
 "s26_body_swap": dict(title="I Swapped Bodies With My Sister... But We Weren't the Only Ones 😱",
   lines={2: "My little sister and I bumped heads and SWAPPED bodies. But we weren't the only ones..."},
   fx={0: T("We're NOT the only ones who swapped...", 0.0, 1.9, em="👀"), 9: T("listen to Mom's voice...", 0.5, 1.8, "#ffffff", "👂")}),
 "s27_grandpa_babysit": dict(title="Grandpa Fell Asleep Babysitting Us... Or DID He? 👀",
   lines={3: "Grandpa babysat us for ONE day. He lasted two seconds... or did he?"},
   fx={0: T("Watch Grandpa's EYES...", 0.0, 1.9, em="👀"), 8: T("keep watching Grandpa...", 0.2, 1.6, "#ffffff", "👀")}),
 "s28_goldie_broke": dict(title="The Richest Kid Lost ALL His Money... Then Moved Into OUR House 😳",
   lines={2: "Goldie. The richest kid in school. Lost ALL his money... or so he THOUGHT."},
   fx={0: T("Wait till the END...", 0.0, 1.9, em="💰"), 10: T("but where DID the money go?", 0.4, 1.8, "#ffffff", "🤔")}),
 "s29_teacher_kid": dict(title="Our Teacher Turned Into a KID... Wait Till It Wears Off 😱",
   lines={3: "Our teacher drank Noob's mystery juice... and turned into a KID. For ONE hour."},
   fx={0: T("Wait till it WEARS OFF...", 0.0, 1.9, em="⏰"), 9: T("the hour is almost up...", 0.4, 1.8, "#ffffff", "⏰")}),
}
for i, p in P.items():
    path = f"episodes/shorts/{i}.json"; ep = json.load(open(path))
    shots = [s for sc in ep["scenes"] for s in sc["shots"]]
    if ep.get("_retention"): print("already patched", i); continue
    ep["title"] = p["title"]; ep["_retention"] = True
    for k, line in p["lines"].items():
        assert shots[k].get("vo"), (i, k); shots[k]["line"] = line
    for k, fx in p["fx"].items():
        shots[k].setdefault("fx", []).extend(fx)
    json.dump(ep, open(path, "w"), indent=1, ensure_ascii=False)
    print("patched", i)
