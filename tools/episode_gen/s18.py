import json
W="at:0.3,-8.8,6.4,0.3,3.8,3.7,34"
SIT={"grandpa":"sit","sage":"sit","pip":"sit","mom":"idle"}
def A(**k):
    d=dict(SIT); d.update(k); return d
def poof(x=0.5,y=0.55):
    return [{"e":"💨","at":0.0,"x":x,"y":y,"size":220,"dur":0.7,"anim":"pop"},{"flash":"#ffffff","at":0.0,"dur":0.12,"x":0.5,"y":0.5}]
POOF_SFX=[{"name":"pop","at":0.0,"volume":0.8},{"name":"whoosh","at":0.05,"volume":0.5}]
cast1={"grandpa":[-2.7,3.9,0,0],"sage":[0.2,3.9,0,0],"pip":[3.1,3.9,0,0],"mom":[1.65,6.5,0,0]}
def props(hide=()):
    P=[{"id":"turkey","type":"turkey","at":[1.65,1.8,2.16],"scale":0.7},
       {"id":"phone","type":"phone","at":[0.2,1.3,2.17],"rot":15,"scale":1.0,"image":"assets/textures/s14/phone_ok.png"},
       {"id":"homework","type":"paper_stack","at":[3.6,1.0,2.16],"rot":-10,"scale":0.14}]
    for p in P:
        if p["id"] in hide: p["hidden"]=True
    return P
ep={"id":"s18_thankful","title":"Whatever You're Thankful For... DISAPPEARS! 🦃","format":"short","mood":"bright","grade":"bright",
 "fog":False,"dof":False,"handheld":0.35,"caption_style":"word","caption_pos":"top","cut_every":1.25,"sting":False,"cta":{"at":16},
 "music":"quirky_loop","music_volume":0.13,"loop":True,
 "_loop":"Mom: 'Sage. Your turn.' -> same wide shot -> Sage: 'I'm thankful for my phone.'",
 "_secret":"Pip brought her homework to Thanksgiving dinner (it's on the table in the first second)",
 "_pinned_comment":"What are YOU thankful for? (careful...) 👇",
 "scenes":[
  {"set":"dining_room","cast":cast1,"props":props(),"shots":[
   {"_beat":"HOOK (loop point)","speaker":"sage","line":"I'm thankful for my phone.","camera":W,"no_cuts":True,"move":"none",
    "anims":A(sage="sit_talk"),"face":"happy","faces":{"pip":"smug"}},
   {"_beat":"POOF","duration":0.8,"camera":"closeup:sage","no_cuts":True,"move":"punch","hide":["phone"],"anims":A(sage="sit_shocked"),
    "faces":{"sage":"shocked"},"sfx":POOF_SFX,"fx":poof(0.5,0.7)+[{"text":"POOF!","color":"#ffffff","size":120,"at":0.0,"x":0.5,"y":0.42,"dur":0.7,"anim":"shake"}]},
   {"speaker":"sage","vo":True,"line":"This Thanksgiving... whatever you say you're thankful for... DISAPPEARS.","camera":"closeup:sage","no_cuts":True,"move":"push",
    "anims":A(),"faces":{"sage":"sad"}},
   {"speaker":"grandpa","line":"Pfft. Nonsense. I'm thankful for my TEETH.","camera":"medium:grandpa","no_cuts":True,"anims":A(grandpa="sit_talk"),"face":"smug"},
   {"_beat":"POOF teeth","duration":0.9,"camera":"closeup:grandpa","no_cuts":True,"move":"punch","anims":A(grandpa="sit_shocked"),"faces":{"grandpa":"shocked"},
    "sfx":POOF_SFX,"fx":[{"e":"🦷","at":0.0,"x":0.5,"y":0.62,"size":150,"dur":0.35}]+[dict(f,at=0.3) if "e" in f else f for f in poof(0.5,0.62)]},
   {"speaker":"grandpa","line":"Mmph! Mmph-mmph!","camera":"closeup:grandpa","no_cuts":True,"move":"shake","anims":A(grandpa="sit_shocked"),"face":"angry"},
   {"speaker":"pip","line":"My turn! I'm thankful for... HOMEWORK.","camera":"closeup:pip","no_cuts":True,"anims":A(pip="sit_talk"),"face":"smug"},
   {"_beat":"POOF homework","duration":0.8,"camera":"medium:pip","no_cuts":True,"move":"punch","hide":["homework"],"anims":A(pip="sit_thumbs_up"),
    "faces":{"pip":"happy"},"sfx":POOF_SFX,"fx":poof(0.5,0.72)},
   {"speaker":"sage","vo":True,"line":"And every homework... in the WHOLE world... disappeared.","camera":"medium:pip","no_cuts":True,"move":"push","anims":A(pip="sit_thumbs_up"),"faces":{"pip":"smug"}}]},
  {"set":"classroom_bright","cast":{"ms_brick":[1.8,9.3,0,0]},"props":[{"id":"papers","type":"paper_stack","at":[1.8,7.6,2.3],"scale":0.6}],"shots":[
   {"speaker":"ms_brick","line":"NO! My three hundred papers!","camera":"medium:ms_brick","no_cuts":True,"move":"shake","hide":["papers"],"anims":{"ms_brick":"scared"},
    "face":"scared","sfx":POOF_SFX,"fx":poof(0.5,0.72)}]},
  {"set":"living_room_clear","cast":{"noob":[0,1,0,0]},"shots":[
   {"speaker":"noob","line":"PIP! FOR! PRESIDENT!","camera":"medium:noob","no_cuts":True,"move":"punch","anims":{"noob":"celebrate"},"face":"happy",
    "sfx":[{"name":"airhorn","at":0.1,"volume":0.45}]}]},
  {"set":"hallway","cast":{"goldie":[0.6,1,0,0]},"shots":[
   {"speaker":"goldie","line":"Ha! I'm thankful for my MONEY!","camera":"medium:goldie","no_cuts":True,"anims":{"goldie":"brag"},"face":"smug",
    "fx":[{"img":"assets/textures/s11/dollar.png","at":0.3,"x":0.3,"y":0.62,"size":300,"dur":1.6,"tilt":-12},{"img":"assets/textures/s11/dollar.png","at":0.6,"x":0.72,"y":0.7,"size":300,"dur":1.3,"tilt":10}]},
   {"_beat":"POOF money","duration":1.0,"camera":"closeup:goldie","no_cuts":True,"move":"punch","anims":{"goldie":"shocked"},"faces":{"goldie":"shocked"},
    "sfx":POOF_SFX+[{"name":"sad_trombone","at":0.3,"volume":0.5}],"fx":poof(0.5,0.65)+[{"text":"$0.00","color":"#ff3b30","size":130,"at":0.2,"x":0.5,"y":0.72,"dur":0.8,"anim":"shake"}]},
   {"speaker":"goldie","line":"...Mom? Can I borrow a dollar?","camera":"closeup:goldie","no_cuts":True,"move":"push","anims":{"goldie":"sad"},"face":"sad"}]},
  {"set":"dining_room","cast":cast1,"props":props(hide=("phone","homework")),"shots":[
   {"speaker":"mom","line":"Okay! ENOUGH! Nobody say ANYTHING else!","camera":"medium:mom","no_cuts":True,"anims":A(mom="point"),"face":"angry"},
   {"speaker":"pip","line":"I'm thankful for... Grandpa's cooking.","camera":"closeup:pip","no_cuts":True,"anims":A(pip="sit_talk"),"face":"smug"},
   {"_beat":"POOF turkey","duration":0.8,"camera":W,"no_cuts":True,"move":"none","hide":["turkey"],"anims":A(grandpa="sit_shocked"),"faces":{"grandpa":"shocked"},
    "sfx":POOF_SFX,"fx":poof(0.55,0.6)},
   {"speaker":"sage","vo":True,"line":"Honestly... nobody was sad about that one.","camera":W,"no_cuts":True,"move":"push",
    "anims":A(sage="sit_thumbs_up",pip="sit_thumbs_up",mom="celebrate",grandpa="sit_shocked"),"faces":{"sage":"happy","pip":"happy","mom":"happy","grandpa":"angry"}},
   {"speaker":"mom","line":"Ahem. I'm thankful for... some peace and quiet.","camera":"medium:mom","no_cuts":True,"anims":A(mom="eyes_closed_smile"),"face":"happy"},
   {"_beat":"POOF everyone","duration":1.1,"camera":W,"no_cuts":True,"move":"none","anims":{"grandpa":"hidden","sage":"hidden","pip":"hidden","mom":"shocked"},"faces":{"mom":"shocked"},
    "sfx":[{"name":"pop","at":0.0},{"name":"pop","at":0.15},{"name":"pop","at":0.3}],
    "fx":[{"e":"💨","at":0.0,"x":0.22,"y":0.55,"size":200,"dur":0.7},{"e":"💨","at":0.15,"x":0.45,"y":0.55,"size":200,"dur":0.7},{"e":"💨","at":0.3,"x":0.66,"y":0.55,"size":200,"dur":0.7}]},
   {"speaker":"mom","line":"Ahhh. Finally.","camera":"closeup:mom","no_cuts":True,"anims":{"grandpa":"hidden","sage":"hidden","pip":"hidden","mom":"eyes_closed_smile"},"face":"happy",
    "sfx":[{"name":"tick_tock","at":0.6,"volume":0.4}]},
   {"speaker":"mom","line":"...Okay, that's TOO quiet. I'm thankful for my FAMILY!","camera":"closeup:mom","no_cuts":True,"move":"punch","anims":{"grandpa":"hidden","sage":"hidden","pip":"hidden","mom":"shocked"},"face":"scared"},
   {"_beat":"everyone pops back","duration":0.9,"camera":W,"no_cuts":True,"move":"none","anims":A(mom="celebrate",sage="sit_shocked",pip="sit_shocked",grandpa="sit_shocked"),
    "faces":{"sage":"shocked","pip":"shocked","grandpa":"shocked","mom":"happy"},"sfx":[{"name":"sparkle","at":0.0}],"fx":[{"e":"✨","at":0.0,"x":0.5,"y":0.45,"size":220,"dur":0.8}]}]},
  {"set":"dining_room","cast":cast1,"props":props(),"_beat":"LOOP: identical to scene 1","shots":[
   {"_beat":"LOOP","speaker":"mom","line":"Sage. Your turn.","camera":W,"no_cuts":True,"move":"none","pad":0.0,"anims":A(mom="talk"),"face":"happy","faces":{"pip":"smug"}}]}
 ]}
json.dump(ep,open("/home/user/YOUTUBE-VIDEO/episodes/shorts/s18_thankful.json","w"),indent=1,ensure_ascii=False)
print("ok")
