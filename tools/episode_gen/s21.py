import json
LW="at:0.9,-8.4,4.6,0.9,2.5,3.1,28"
lr_cast={"grandpa":[-1.9,1.4,0,20],"mom":[1.6,1.2,0,-20],"pip":[3.9,3.4,0,-20],"sage":[-0.2,0.2,0,0]}
def lr_props(): return [{"id":"choc","type":"chocolate","at":[-0.1,0.3,3.0],"rot":-15,"scale":0.7},{"id":"cake","type":"cake","at":[3.9,1.6,0],"scale":0.5,"hidden":True}]
H={"sage":"hidden"}
def A(**k):
    d={"grandpa":"idle","mom":"idle","pip":"idle","sage":"hidden"}; d.update(k); return d
bob={"choc":{"to":[0,0,0.25],"at":0.2,"dur":0.8}}
ep={"id":"s21_invisible","title":"I Turned INVISIBLE... and Nobody Noticed 👻","format":"short","mood":"bright","grade":"bright",
 "fog":False,"dof":False,"handheld":0.35,"caption_style":"word","caption_pos":"top","cut_every":1.25,"sting":False,"cta":{"at":16},
 "music":"mystery_loop","music_volume":0.12,"loop":True,
 "_loop":"Pip: 'Don't worry. I won't tell Mom.' -> same living-room shot -> Mom: 'Has anyone seen Sage today?'",
 "_secret":"A chocolate bar is FLOATING in mid-air in the first second (invisible Sage is holding it), and Pip is staring right at it",
 "_pinned_comment":"Why is the chocolate FLOATING at 0:01? 👀👇",
 "scenes":[
  {"set":"living_room_clear","cast":lr_cast,"props":lr_props(),"shots":[
   {"_beat":"HOOK (loop point)","speaker":"mom","line":"Has anyone seen Sage today?","camera":LW,"no_cuts":True,"move":"none","prop_moves":bob,"anims":A(mom="talk"),"face":"neutral","faces":{"pip":"smug"}},
   {"speaker":"grandpa","line":"Who?","camera":"closeup:grandpa","no_cuts":True,"move":"punch","anims":A(grandpa="shrug"),"face":"sus","sfx":[{"name":"vine_boom","at":0.4,"volume":0.6}]},
   {"speaker":"sage","vo":True,"line":"I turned invisible this morning. And NOBODY noticed.","camera":LW,"no_cuts":True,"move":"push","anims":A(),"faces":{"pip":"smug"},
    "fx":[{"e":"👻","at":0.3,"x":0.45,"y":0.48,"size":170,"dur":1.6,"anim":"rise"}]}]},
  {"set":"classroom_bright","cast":{"ms_brick":[1.8,9.3,0,0],"noob":[-3,1.6,0,0],"goldie":[3,1.6,0,0],"sage":[0,0,0,0]},
   "props":[{"id":"gchoc","type":"chocolate","at":[3.5,0.4,1.96],"rot":10,"scale":0.7}],"shots":[
   {"speaker":"ms_brick","line":"Sage? ...Sage? Absent. AGAIN.","camera":"medium:ms_brick","no_cuts":True,"anims":{"ms_brick":"talk","noob":"sit","goldie":"sit","sage":"hidden"},"face":"sus"},
   {"speaker":"sage","vo":True,"line":"AGAIN?!","camera":"medium:ms_brick","no_cuts":True,"move":"shake","anims":{"ms_brick":"sit_write" if False else "idle","noob":"sit","goldie":"sit","sage":"hidden"},"sfx":[{"name":"record_scratch","at":0.0,"volume":0.5}]},
   {"speaker":"goldie","line":"Hey! My chocolate's FLYING!","camera":"medium:goldie","no_cuts":True,"move":"shake","prop_moves":{"gchoc":{"to":[-2.6,-1.5,2.8],"rot":[0,0,180],"at":0.1,"dur":1.3}},
    "anims":{"goldie":"sit_shocked","noob":"sit","ms_brick":"idle","sage":"hidden"},"face":"shocked","sfx":[{"name":"whoosh","at":0.2}]},
   {"speaker":"noob","line":"Morning, Sage! Nice shirt today.","camera":"closeup:noob","no_cuts":True,"anims":{"noob":"sit_talk","goldie":"sit","ms_brick":"idle","sage":"hidden"},"face":"happy"},
   {"speaker":"sage","vo":True,"line":"Wait... Noob can SEE me?!","camera":"closeup:noob","no_cuts":True,"move":"push","anims":{"noob":"sit","goldie":"sit","ms_brick":"idle","sage":"hidden"},"faces":{"noob":"happy"}},
   {"speaker":"noob","line":"Nope. I just say that to the air every morning.","camera":"closeup:noob","no_cuts":True,"anims":{"noob":"sit_thumbs_up","goldie":"sit","ms_brick":"idle","sage":"hidden"},"face":"happy",
    "sfx":[{"name":"boing","at":2.0,"volume":0.5}]}]},
  {"set":"dining_room","cast":{"grandpa":[-3.4,3.9,0,0],"sage":[0.2,3.9,0,0],"mom":[3.8,3.9,0,0]},
   "props":[{"id":"plate","type":"plate","at":[0.2,1.6,2.16],"scale":0.8},{"id":"phone","type":"phone","at":[1.6,1.2,2.17],"scale":1.0,"image":"assets/textures/s14/phone_ok.png"}],"shots":[
   {"speaker":"grandpa","line":"Sage isn't here? ...FREE FOOD!","camera":"medium:grandpa","no_cuts":True,"anims":{"grandpa":"sit_eat","mom":"sit","sage":"hidden"},"face":"happy",
    "prop_moves":{"plate":{"to":[-3.0,0,0],"at":0.9,"dur":0.5}}},
   {"speaker":"sage","vo":True,"line":"So I texted Mom.","camera":"medium:mom","no_cuts":True,"prop_moves":{"phone":{"to":[0.8,-0.3,1.6],"rot":[70,0,0],"at":0.1,"dur":0.7}},
    "anims":{"mom":"sit","grandpa":"sit_eat","sage":"hidden"},"faces":{"mom":"neutral"},"fx":[{"phone":"Mom. I'm INVISIBLE.","sender":"Sage","at":0.6,"x":0.5,"y":0.6,"size":620,"dur":1.4}]},
   {"speaker":"mom","line":"That's nice, sweetie.","camera":"closeup:mom","no_cuts":True,"anims":{"mom":"sit_talk","grandpa":"sit_eat","sage":"hidden"},"face":"happy",
    "fx":[{"text":"seen","color":"#9e9e9e","size":70,"at":0.8,"x":0.5,"y":0.78,"dur":1.0}]}]},
  {"set":"living_room_clear","cast":lr_cast,"props":lr_props(),"shots":[
   {"speaker":"sage","vo":True,"line":"Then... my little sister looked RIGHT at me.","camera":"at:5.0,-1.4,3.0,3.9,3.4,2.6,34","no_cuts":True,"move":"push","show":["cake"],"anims":A(pip="still"),"faces":{"pip":"smug"},
    "sfx":[{"name":"vine_boom","at":1.8}]},
   {"speaker":"pip","line":"Hi, Sage. I could see you ALL day.","camera":"at:5.0,-1.4,3.0,3.9,3.4,2.6,34","no_cuts":True,"anims":A(pip="wave"),"face":"smug"},
   {"speaker":"pip","line":"I just wanted your dessert.","camera":"at:5.0,-1.4,3.0,3.9,3.4,2.6,34","no_cuts":True,"move":"punch","anims":A(pip="brag"),"face":"evil",
    "fx":[{"e":"🎂","at":0.3,"x":0.7,"y":0.5,"size":150,"dur":1.3}],"sfx":[{"name":"sting","at":0.2,"volume":0.5}]}]},
  {"set":"living_room_clear","cast":lr_cast,"props":lr_props(),"_beat":"LOOP: identical to scene 1","shots":[
   {"_beat":"LOOP","speaker":"pip","line":"Don't worry. I won't tell Mom.","camera":LW,"no_cuts":True,"move":"none","pad":0.0,"prop_moves":bob,"anims":A(pip="talk"),"faces":{"pip":"smug"}}]}
 ]}
json.dump(ep,open("/home/user/YOUTUBE-VIDEO/episodes/shorts/s21_invisible.json","w"),indent=1,ensure_ascii=False)
print("ok")
