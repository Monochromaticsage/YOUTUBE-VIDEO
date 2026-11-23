import json
DW="at:0.4,-7.8,4.6,0.4,2.4,3.2,29"
door={"goldie":[1.5,1.2,0,-20],"sage":[-1.6,1.0,0,20]}
def coins(): return [{"id":"coins","type":"coins","at":[3.2,6.2,1.72],"scale":1.0,"count":7}]
ep={"id":"s28_goldie_broke","title":"The Richest Kid in School Lost ALL His Money 😳","format":"short","mood":"bright","grade":"bright",
 "fog":False,"dof":False,"handheld":0.35,"caption_style":"word","caption_pos":"top","cut_every":1.25,"sting":False,"cta":{"at":16},
 "music":"chill_loop","music_volume":0.13,"loop":True,
 "_loop":"Mom: 'Goldie! Your dad's here to pick you up!' -> same shot -> Goldie: 'So... can I live here now?'",
 "_secret":"Gold coins are ALREADY peeking out of our couch in the first second (that's where his money was)",
 "_pinned_comment":"Should Goldie stay? YES or NO 👇",
 "scenes":[
  {"set":"living_room_clear","cast":door,"props":coins(),"shots":[
   {"_beat":"HOOK (loop point)","speaker":"goldie","line":"So... can I live here now?","camera":DW,"no_cuts":True,"move":"none","anims":{"goldie":"sad","sage":"cross_arms"},"face":"sad","faces":{"sage":"sus"}},
   {"speaker":"sage","line":"...WHAT?!","camera":"closeup:sage","no_cuts":True,"move":"punch","anims":{"sage":"shocked","goldie":"sad"},"face":"shocked","sfx":[{"name":"record_scratch","at":0.0,"volume":0.5}]},
   {"speaker":"sage","vo":True,"line":"Goldie. The richest kid in school. Lost ALL his money.","camera":"medium:goldie","no_cuts":True,"move":"push","anims":{"goldie":"sad_look_down","sage":"idle"},"faces":{"goldie":"sad"},
    "fx":[{"text":"$0.00","color":"#ff3b30","size":130,"at":0.6,"x":0.5,"y":0.72,"dur":1.6,"anim":"shake"}],"sfx":[{"name":"sad_trombone","at":0.6,"volume":0.45}]}]},
  {"set":"dining_room","cast":{"goldie":[0.2,3.9,0,0],"pip":[3.8,3.9,0,0]},"props":[{"id":"bowl","type":"plate","at":[0.2,1.6,2.16],"scale":0.7}],"shots":[
   {"speaker":"goldie","line":"Wait... you eat cereal with a SPOON? Every single bite?","camera":"medium:goldie","no_cuts":True,"anims":{"goldie":"sit_eat","pip":"sit"},"face":"shocked",
    "fx":[{"e":"🥣","at":0.3,"x":0.72,"y":0.55,"size":140,"dur":1.6}]},
   {"speaker":"pip","line":"What did you use before?","camera":"closeup:pip","no_cuts":True,"anims":{"pip":"sit_talk","goldie":"sit"},"face":"sus"},
   {"speaker":"goldie","line":"...A butler.","camera":"closeup:goldie","no_cuts":True,"move":"push","anims":{"goldie":"sit","pip":"sit"},"face":"sad","sfx":[{"name":"vine_boom","at":0.4,"volume":0.6}]}]},
  {"set":"living_room_clear","cast":{"mom":[1.6,1.2,0,-20],"goldie":[-1.6,1.0,0,20]},"shots":[
   {"speaker":"mom","line":"Goldie, sweetie. Take out the trash.","camera":"medium:mom","no_cuts":True,"anims":{"mom":"point","goldie":"idle"},"face":"happy"},
   {"speaker":"goldie","line":"I have PEOPLE for that— ...I HAD people for that.","camera":"medium:goldie","no_cuts":True,"anims":{"goldie":"brag","mom":"cross_arms"},"face":"smug",
    "sfx":[{"name":"sad_trombone","at":2.0,"volume":0.4}]}]},
  {"set":"living_room_clear","cast":{"grandpa":[1.6,1.2,0,-20],"goldie":[-1.6,1.0,0,20]},"shots":[
   {"speaker":"grandpa","line":"Here, kiddo. A whole dollar. Don't spend it all at once.","camera":"medium:grandpa","no_cuts":True,"anims":{"grandpa":"reach_to","goldie":"sad"},"face":"happy",
    "fx":[{"img":"assets/textures/s11/dollar.png","at":1.0,"x":0.5,"y":0.66,"size":320,"dur":1.6,"tilt":-6}]},
   {"speaker":"goldie","line":"Thank you... GRANDPA!","camera":"at:0,-6.0,4.2,0,1.1,3.4,32","no_cuts":True,"anims":{"goldie":"hug","grandpa":"hug"},"face":"cry","faces":{"grandpa":"happy"},
    "sfx":[{"name":"sparkle","at":0.5,"volume":0.5}]}]},
  {"set":"living_room_clear","cast":{"pip":[1.4,1.2,0,-20],"goldie":[-1.4,1.0,0,20]},"shots":[
   {"speaker":"pip","line":"I drew you a NEW gold chain.","camera":"at:2.4,-2.8,3.7,1.4,1.2,3.3,34","no_cuts":True,"anims":{"pip":"hold_photo","goldie":"sad"},"face":"happy",
    "fx":[{"text":"crayon chain","color":"#ffd23f","size":80,"at":0.9,"x":0.5,"y":0.78,"dur":1.2}]},
   {"speaker":"goldie","line":"This is the BEST thing I have ever owned.","camera":"closeup:goldie","no_cuts":True,"move":"push","anims":{"goldie":"cry","pip":"hold_photo"},"face":"cry"}]},
  {"set":"living_room_clear","cast":door,"props":coins(),"shots":[
   {"_beat":"text","duration":1.8,"camera":"medium:goldie","no_cuts":True,"anims":{"goldie":"film_selfie","sage":"idle"},"faces":{"goldie":"shocked"},"sfx":[{"name":"notification","at":0.1}],
    "fx":[{"phone":"Found the money! It fell in YOUR friend's couch.","sender":"Dad","at":0.1,"x":0.5,"y":0.58,"size":640,"dur":1.6}]},
   {"speaker":"sage","line":"...OUR couch?","camera":"closeup:sage","no_cuts":True,"move":"punch","anims":{"sage":"shocked","goldie":"film_selfie"},"face":"shocked","sfx":[{"name":"vine_boom","at":0.3}]},
   {"_beat":"coins reveal","duration":1.0,"camera":"at:3.2,1.2,3.6,3.2,6.2,1.9,40","no_cuts":True,"move":"push","anims":{"sage":"shocked","goldie":"shocked"},"sfx":[{"name":"cash","at":0.2},{"name":"sparkle","at":0.3}]},
   {"speaker":"goldie","line":"I'm RICH again! ...But can I still come over? Like... every day?","camera":"medium:goldie","no_cuts":True,"anims":{"goldie":"celebrate","sage":"idle"},"face":"happy"},
   {"speaker":"mom","vo":True,"line":"Goldie! Your dad's here to pick you up!","camera":DW,"no_cuts":True,"anims":{"goldie":"sad","sage":"cross_arms"},"faces":{"goldie":"sad","sage":"sus"},"sfx":[{"name":"door_knock","at":0.0,"volume":0.5}]}]},
  {"set":"living_room_clear","cast":door,"props":coins(),"_beat":"LOOP: identical to scene 1","shots":[
   {"_beat":"LOOP tail","duration":0.4,"camera":DW,"no_cuts":True,"move":"none","pad":0.0,"anims":{"goldie":"sad","sage":"cross_arms"},"faces":{"goldie":"sad","sage":"sus"}}]}
 ]}
json.dump(ep,open("/home/user/YOUTUBE-VIDEO/episodes/shorts/s28_goldie_broke.json","w"),indent=1,ensure_ascii=False)
print("ok")
