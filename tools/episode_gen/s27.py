import json
LW="at:0.0,-9.4,4.8,0.0,2.0,3.2,27"
lr={"mom":[-4.2,1.8,0,25],"grandpa":[0.6,2.8,0,0],"sage":[-2.0,0.6,0,20],"pip":[2.9,1.0,0,-20]}
def props(): return [{"id":"pz","type":"flat_pizza","at":[2.8,3.4,2.0],"rot":30,"scale":0.7}]
ZZZ=lambda at=0.3: {"e":"💤","at":at,"x":0.6,"y":0.3,"size":150,"dur":1.6,"anim":"rise"}
def A(**k):
    d={"mom":"hidden","grandpa":"eyes_closed_smile","sage":"idle","pip":"idle"}; d.update(k); return d
ep={"id":"s27_grandpa_babysit","title":"Grandpa Babysat Us for ONE Day 😂","format":"short","mood":"bright","grade":"bright",
 "fog":False,"dof":False,"handheld":0.35,"caption_style":"word","caption_pos":"top","cut_every":1.25,"sting":False,"cta":{"at":16},
 "music":"quirky_loop","music_volume":0.13,"loop":True,
 "_loop":"Mom: '...Okay. I'm leaving again.' -> same shot -> Mom: 'Grandpa's in charge. Be GOOD.'",
 "_secret":"There's already a pizza slice on the shelf behind Grandpa in the first second (the pizza was HIS idea)",
 "_pinned_comment":"Who's the WORST babysitter in your family? 😂👇",
 "scenes":[
  {"set":"living_room_clear","cast":lr,"props":props(),"shots":[
   {"_beat":"HOOK (loop point)","speaker":"mom","line":"Grandpa's in charge. Be GOOD.","camera":LW,"no_cuts":True,"move":"none","anims":A(mom="point",grandpa="nod"),"face":"angry","faces":{"grandpa":"happy"}},
   {"speaker":"grandpa","line":"Don't worry, dear. I've got this—","camera":"at:0.6,-3.2,4.8,0.6,2.8,4.1,34","no_cuts":True,"anims":A(mom="walk_out_left",grandpa="brag"),"face":"smug","sfx":[{"name":"door_slam","at":1.6,"volume":0.6}]},
   {"_beat":"instantly asleep","duration":1.3,"camera":"at:2.0,-1.6,4.9,0.6,2.8,4.3,40","no_cuts":True,"move":"push","anims":A(),"faces":{"grandpa":"happy"},"fx":[ZZZ(0.1)],"sfx":[{"name":"boing","at":0.1,"volume":0.4}]},
   {"speaker":"sage","vo":True,"line":"Grandpa babysat us for ONE day. He lasted two seconds.","camera":LW,"no_cuts":True,"anims":A(),"faces":{"sage":"sus","pip":"evil"},"fx":[ZZZ(0.5)]},
   {"speaker":"pip","line":"New rules. Pizza for breakfast. Bedtime... NEVER.","camera":"at:3.9,-2.4,3.8,2.9,1.0,3.3,34","no_cuts":True,"move":"punch","anims":A(pip="brag"),"face":"evil",
    "fx":[{"e":"🍕","at":0.6,"x":0.25,"y":0.5,"size":150,"dur":1.0},{"e":"🌙","at":1.9,"x":0.75,"y":0.45,"size":150,"dur":1.0}]},
   {"speaker":"sage","line":"Pip! We're gonna get in SO much trouble!","camera":"medium:sage","no_cuts":True,"anims":A(sage="talk"),"face":"scared"}]},
  {"set":"living_room_clear","cast":{"noob":[1.6,1.0,0,-20],"pip":[-1.4,1.0,0,20]},"props":[{"id":"juice","type":"juice","at":[1.0,-0.1,0],"scale":0.6}],"shots":[
   {"speaker":"noob","line":"Your juice, Miss Pip.","camera":"medium:noob","no_cuts":True,"anims":{"noob":"nod","pip":"cross_arms"},"face":"happy"},
   {"speaker":"sage","vo":True,"line":"She hired Noob as a BUTLER. She pays him in stickers.","camera":"at:-1.4,-3.6,3.5,-1.4,1.0,3.2,34","no_cuts":True,"move":"push","anims":{"pip":"brag","noob":"nod"},"faces":{"pip":"smug"},
    "fx":[{"e":"⭐","at":1.6,"x":0.7,"y":0.45,"size":140,"dur":1.2}]}]},
  {"set":"living_room_clear","cast":{"pip":[-1.4,1.0,0,20],"sage":[1.6,1.0,0,-20]},"shots":[
   {"_beat":"phone rings","duration":1.0,"camera":"at:-1.4,-3.6,3.5,-1.4,1.0,3.2,34","no_cuts":True,"anims":{"pip":"film_selfie","sage":"scared"},"faces":{"pip":"neutral"},
    "sfx":[{"name":"notification","at":0.0},{"name":"notification","at":0.5}],"fx":[{"text":"MOM CALLING...","color":"#4caf50","size":90,"at":0.0,"x":0.5,"y":0.72,"dur":1.0,"anim":"shake"}]},
   {"speaker":"pip","voice_as":"grandpa","line":"Everything is FINE, dear. The kids are asleep.","camera":"at:-1.4,-3.6,3.5,-1.4,1.0,3.2,34","no_cuts":True,"anims":{"pip":"film_selfie","sage":"shocked"},"face":"smug"},
   {"speaker":"sage","line":"...Since WHEN can you do Grandpa's voice?!","camera":"medium:sage","no_cuts":True,"move":"shake","anims":{"sage":"shocked","pip":"brag"},"face":"shocked"}]},
  {"set":"living_room_clear","cast":lr,"props":props(),"shots":[
   {"_beat":"grandpa opens one eye","duration":1.0,"camera":"at:2.0,-1.6,4.9,0.6,2.8,4.3,40","no_cuts":True,"move":"punch","anims":A(grandpa="idle"),"faces":{"grandpa":"sus"},"sfx":[{"name":"vine_boom","at":0.0}]},
   {"speaker":"grandpa","line":"Nice try, kiddo. I was awake the WHOLE time.","camera":"at:2.0,-1.6,4.9,0.6,2.8,4.3,40","no_cuts":True,"anims":A(grandpa="cross_arms"),"face":"smug"},
   {"speaker":"grandpa","line":"...The pizza was MY idea.","camera":"at:1.6,-3.4,4.6,0.6,2.8,3.6,32","no_cuts":True,"anims":A(grandpa="celebrate",pip="celebrate",sage="shocked"),"face":"happy","faces":{"pip":"happy","sage":"shocked"},
    "sfx":[{"name":"airhorn","at":1.1,"volume":0.35}]},
   {"_beat":"door opens","duration":0.8,"camera":LW,"no_cuts":True,"anims":A(mom="walk_in_left",grandpa="eyes_closed_smile",pip="still",sage="scared"),"faces":{"mom":"sus","sage":"scared"},
    "sfx":[{"name":"door_knock","at":0.0,"volume":0.5}],"fx":[ZZZ(0.3)]},
   {"speaker":"mom","line":"...Is he ASLEEP?","camera":"at:-3.6,-3.4,4.6,-4.2,1.8,4.0,34","no_cuts":True,"anims":A(mom="cross_arms",grandpa="eyes_closed_smile"),"face":"angry","fx":[ZZZ(0.2)]}]},
  {"set":"living_room_clear","cast":lr,"props":props(),"_beat":"LOOP: identical to scene 1","shots":[
   {"_beat":"LOOP","speaker":"mom","line":"...Okay. I'm leaving again.","camera":LW,"no_cuts":True,"move":"none","pad":0.0,"anims":A(mom="point",grandpa="nod"),"faces":{"mom":"angry","grandpa":"happy"}}]}
 ]}
json.dump(ep,open("/home/user/YOUTUBE-VIDEO/episodes/shorts/s27_grandpa_babysit.json","w"),indent=1,ensure_ascii=False)
print("ok")
