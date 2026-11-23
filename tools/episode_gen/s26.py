import json
LW="at:0.4,-8.2,4.6,0.4,2.2,3.2,29"
lr={"sage":[-1.3,1.0,0,25],"pip":[1.3,1.0,0,-25],"grandpa":[2.6,5.6,0,-15]}
BONK=[{"name":"boing","at":0.0},{"name":"glitch","at":0.15,"volume":0.6}]
def bonk(): return [{"flash":"#ffffff","at":0.0,"dur":0.2,"x":0.5,"y":0.5},{"text":"BONK!","color":"#ffd23f","size":140,"at":0.0,"x":0.5,"y":0.6,"dur":0.6,"anim":"shake"},
                    {"e":"💫","at":0.1,"x":0.5,"y":0.4,"size":180,"dur":0.6}]
ep={"id":"s26_body_swap","title":"I Swapped Bodies With My Little Sister 😱","format":"short","mood":"bright","grade":"bright",
 "fog":False,"dof":False,"handheld":0.35,"caption_style":"word","caption_pos":"top","cut_every":1.25,"sting":False,"cta":{"at":16},
 "music":"quirky_loop","music_volume":0.13,"loop":True,
 "_loop":"Sage: 'So we bumped heads again to swap back—' BONK -> same shot -> (Pip's body, Sage's voice): 'Wait... why am I so SHORT?'",
 "_secret":"Grandpa in the background is pointing and scolding exactly like Mom in the first second (he already swapped with Mom)",
 "_pinned_comment":"Who would YOU swap bodies with? 👇",
 "scenes":[
  {"set":"living_room_clear","cast":lr,"shots":[
   {"_beat":"HOOK (loop point)","speaker":"pip","voice_as":"sage","line":"Wait... why am I so SHORT?!","camera":LW,"no_cuts":True,"move":"none","anims":{"pip":"shocked","sage":"shocked","grandpa":"point"},"face":"shocked","faces":{"sage":"shocked","grandpa":"angry"}},
   {"speaker":"sage","voice_as":"pip","line":"And why am I so TALL?!","camera":"medium:sage","no_cuts":True,"anims":{"sage":"look_up","pip":"shocked","grandpa":"point"},"face":"shocked"},
   {"speaker":"sage","vo":True,"line":"My little sister and I bumped heads... and SWAPPED bodies.","camera":LW,"no_cuts":True,"move":"push","anims":{"sage":"facepalm","pip":"facepalm","grandpa":"cross_arms"},"faces":{"sage":"sad","pip":"sad","grandpa":"angry"}}]},
  {"set":"classroom_bright","cast":{"pip":[-3,1.6,0,0],"ms_brick":[1.8,5.2,0,0]},"shots":[
   {"speaker":"ms_brick","line":"Pip, sweetie! Nap time!","camera":"medium:ms_brick","no_cuts":True,"anims":{"ms_brick":"talk","pip":"sit"},"face":"happy"},
   {"speaker":"pip","voice_as":"sage","line":"I'm TWELVE.","camera":"closeup:pip","no_cuts":True,"move":"punch","anims":{"pip":"sit_talk","ms_brick":"idle"},"face":"angry"},
   {"speaker":"ms_brick","line":"Of course you are. And I'm the Queen.","camera":"medium:ms_brick","no_cuts":True,"anims":{"ms_brick":"nod","pip":"sit"},"face":"smug",
    "fx":[{"e":"👑","at":1.2,"x":0.5,"y":0.25,"size":150,"dur":1.0}]}]},
  {"set":"hallway","cast":{"sage":[-1.6,1.0,0,20],"goldie":[1.6,1.0,0,-20]},"shots":[
   {"speaker":"goldie","line":"Nice hair, loser.","camera":"medium:goldie","no_cuts":True,"anims":{"goldie":"point_laugh","sage":"cross_arms"},"face":"smug"},
   {"speaker":"sage","voice_as":"pip","line":"Nice shoes. Did your MOMMY pick them?","camera":"medium:sage","no_cuts":True,"anims":{"sage":"brag","goldie":"idle"},"face":"smug"},
   {"_beat":"goldie destroyed","duration":1.3,"camera":"closeup:goldie","no_cuts":True,"move":"push","anims":{"goldie":"cry","sage":"brag"},"faces":{"goldie":"cry"},
    "sfx":[{"name":"vine_boom","at":0.0}],"fx":[{"text":"DESTROYED","color":"#ff3b30","size":110,"at":0.2,"x":0.5,"y":0.72,"dur":1.0,"anim":"shake"}]}]},
  {"set":"classroom_bright","cast":{"sage":[-3,1.6,0,0],"ms_brick":[1.8,9.3,0,0]},"shots":[
   {"speaker":"ms_brick","line":"Sage... an A-PLUS?! Who are you?!","camera":"medium:ms_brick","no_cuts":True,"move":"punch","anims":{"ms_brick":"shocked","sage":"sit_thumbs_up"},"face":"shocked",
    "fx":[{"img":"textures/test_aplus.png","at":0.4,"x":0.5,"y":0.66,"size":340,"dur":1.6,"tilt":-6}],"sfx":[{"name":"sparkle","at":0.4}]}]},
  {"set":"living_room_clear","cast":{"mom":[1.6,1.2,0,-20],"pip":[-1.4,1.0,0,20],"sage":[-3.6,2.8,0,25]},"shots":[
   {"speaker":"mom","voice_as":"grandpa","line":"Pip. Bedtime. Seven o'clock.","camera":"medium:mom","no_cuts":True,"anims":{"mom":"point","pip":"idle","sage":"idle"},"face":"neutral"},
   {"speaker":"pip","voice_as":"sage","line":"SEVEN?! ...Wait. Why does Mom sound like GRANDPA?","camera":"closeup:pip","no_cuts":True,"move":"shake","anims":{"pip":"shocked","mom":"idle","sage":"idle"},"face":"shocked"}]},
  {"set":"living_room_clear","cast":{"grandpa":[0,1.0,0,0]},"shots":[
   {"speaker":"grandpa","voice_as":"mom","line":"Oh, we swapped LAST Tuesday. Now go clean your room!","camera":"medium:grandpa","no_cuts":True,"anims":{"grandpa":"point"},"face":"angry",
    "sfx":[{"name":"record_scratch","at":0.0,"volume":0.5}]}]},
  {"set":"living_room_clear","cast":lr,"shots":[
   {"speaker":"sage","vo":True,"line":"So we bumped heads again... to swap back—","camera":LW,"no_cuts":True,"anims":{"sage":"walk_in_right" if False else "idle","pip":"idle","grandpa":"point"},"faces":{"sage":"sus","pip":"sus","grandpa":"angry"}}]},
  {"set":"living_room_clear","cast":lr,"_beat":"LOOP: identical to scene 1","shots":[
   {"_beat":"LOOP BONK","duration":0.5,"camera":LW,"no_cuts":True,"move":"none","pad":0.0,"anims":{"sage":"shocked","pip":"shocked","grandpa":"point"},"faces":{"sage":"shocked","pip":"shocked","grandpa":"angry"},
    "sfx":BONK,"fx":bonk()}]}
 ]}
json.dump(ep,open("/home/user/YOUTUBE-VIDEO/episodes/shorts/s26_body_swap.json","w"),indent=1,ensure_ascii=False)
print("ok")
