import json
CW="at:0,-10.5,7.8,0,2.2,2.6,30"   # classroom two-shot: Sage (left) + Noob (right)
TICK=[{"name":"tick_tock","at":0.0,"volume":0.55}]
def later(): return [{"text":"10 SECONDS LATER...","color":"#ffffff","size":96,"at":0.0,"x":0.5,"y":0.5,"dur":0.9},{"e":"⏳","at":0.0,"x":0.5,"y":0.36,"size":150,"dur":0.9}]
def pizza(i,x,y): return {"id":f"pz{i}","type":"flat_pizza","at":[x,y,13],"rot":i*40,"scale":0.9,"hidden":True}
cls_cast={"sage":[-3,1.6,0,0],"noob":[3,1.6,0,0],"goldie":[8,1.6,0,0],"ms_brick":[1.8,9.3,0,0]}
def cls_props(floor_pizza=True):
    P=[pizza(1,-3,0.4),pizza(2,3,0.4),pizza(3,0,2.5),pizza(4,-1.5,-0.5)]
    if floor_pizza: P.append({"id":"clue_pizza","type":"flat_pizza","at":[0.2,-0.6,0.05],"rot":20,"scale":0.8})
    return P
    P+=[{"id":f"ban{i}","type":"banana","at":[1.8+dx,8.3,z],"rot":r,"scale":0.9,"hidden":True} for i,(dx,z,r) in enumerate([(-1.6,5.0,20),(1.6,5.4,-30),(0,6.4,90),(-2.2,3.6,-60),(2.3,3.4,45)])]
    return P
def A(**k):
    d={"sage":"sit","noob":"sit","goldie":"sit","ms_brick":"idle"}; d.update(k); return d
ep={"id":"s20_comes_true","title":"Whatever You Say Comes TRUE... 10 Seconds Later ⏳","format":"short","mood":"bright","grade":"bright",
 "fog":False,"dof":False,"handheld":0.35,"caption_style":"word","caption_pos":"top","cut_every":1.25,"sting":False,"cta":{"at":16},
 "music":"quirky_loop","music_volume":0.13,"loop":True,
 "_loop":"Sage: 'I wish this day would START OVER.' 3-2-1 -> the day starts over: Noob: 'I wish it would rain PIZZA!'",
 "_secret":"A pizza slice is ALREADY lying on the classroom floor in the first second (from the last time the day started over)",
 "_pinned_comment":"You have 10 seconds. What do you say? ⏳👇",
 "scenes":[
  {"set":"classroom_bright","cast":cls_cast,"props":cls_props(),"shots":[
   {"_beat":"HOOK (loop point)","speaker":"noob","line":"I wish it would rain PIZZA!","camera":CW,"no_cuts":True,"move":"none","anims":A(noob="sit_talk"),"face":"happy","faces":{"sage":"neutral"}},
   {"speaker":"sage","vo":True,"line":"In this world... whatever you say comes true. Ten seconds later.","camera":"closeup:sage","no_cuts":True,"move":"push","anims":A(sage="sit_shocked"),"faces":{"sage":"scared"},
    "fx":[{"text":"10","color":"#ffd23f","size":200,"at":0.2,"x":0.5,"y":0.7,"dur":0.6,"anim":"pop"}],"sfx":TICK},
   {"_beat":"10 SECONDS LATER","duration":0.9,"camera":CW,"no_cuts":True,"move":"none","anims":A(),"fx":later(),"sfx":TICK},
   {"_beat":"PIZZA RAIN","speaker":"noob","line":"YESSS!","camera":CW,"no_cuts":True,"move":"shake","show":["pz1","pz2","pz3","pz4"],
    "prop_moves":{"pz1":{"to":[0,0,-11.0],"at":0.0,"dur":0.45},"pz2":{"to":[0,0,-11.0],"at":0.15,"dur":0.45},"pz3":{"to":[0,0,-12.9],"at":0.3,"dur":0.5},"pz4":{"to":[0,0,-12.9],"at":0.4,"dur":0.5}},
    "anims":A(noob="celebrate",sage="sit_shocked"),"face":"happy","faces":{"sage":"shocked"},"sfx":[{"name":"oof_thud","at":0.45},{"name":"oof_thud","at":0.6},{"name":"airhorn","at":0.7,"volume":0.4}]},
   {"speaker":"goldie","line":"Pfft. I'm so rich... I could SWIM in money.","camera":"medium:goldie","no_cuts":True,"anims":A(goldie="brag"),"face":"smug"},
   {"_beat":"money rain","duration":1.3,"camera":"medium:goldie","no_cuts":True,"move":"shake","anims":A(goldie="celebrate"),"faces":{"goldie":"happy"},
    "sfx":[{"name":"cash","at":0.1},{"name":"cash","at":0.5}],
    "fx":later()[:1]+[{"img":"assets/textures/s11/dollar.png","at":0.4+0.15*i,"x":0.2+0.15*i,"y":0.35+0.08*(i%3),"size":260,"dur":0.9,"tilt":(-15 if i%2 else 12)} for i in range(5)]},
   {"speaker":"ms_brick","line":"Settle DOWN! You kids are driving me... BANANAS!","camera":"medium:ms_brick","no_cuts":True,"anims":A(ms_brick="angry"),"face":"angry"},
   {"_beat":"BANANAS","duration":1.1,"camera":"medium:ms_brick","no_cuts":True,"move":"punch","fx":[{"e":"🍌","at":0.08*i,"x":x,"y":y,"size":150,"dur":1.0-0.08*i,"anim":"pop"} for i,(x,y) in enumerate([(0.25,0.35),(0.75,0.3),(0.5,0.18),(0.18,0.6),(0.82,0.58)])],"anims":A(ms_brick="shocked"),"faces":{"ms_brick":"shocked"},
    "sfx":[{"name":"pop","at":0.08*i,"volume":0.6} for i in range(5)]},
   {"speaker":"sage","vo":True,"line":"So everyone got VERY careful with their words.","camera":CW,"no_cuts":True,"anims":A(sage="sit",noob="sit_eat"),"faces":{"sage":"sus","noob":"happy"}}]},
  {"set":"living_room_clear","cast":{"mom":[1.6,1.2,0,-20],"sage":[-1.6,1.0,0,20]},"shots":[
   {"speaker":"mom","line":"Sage, if you don't clean your room, I'll—","camera":"medium:mom","no_cuts":True,"anims":{"mom":"point","sage":"idle"},"face":"angry"},
   {"_beat":"mom stops herself","duration":1.1,"camera":"closeup:mom","no_cuts":True,"move":"punch","anims":{"mom":"facepalm","sage":"idle"},"faces":{"mom":"scared"},"sfx":[{"name":"record_scratch","at":0.0,"volume":0.6}]},
   {"speaker":"mom","line":"...I'll be VERY proud of you.","camera":"closeup:mom","no_cuts":True,"anims":{"mom":"talk","sage":"idle"},"face":"happy",
    "fx":[{"e":"🫶","at":0.6,"x":0.72,"y":0.5,"size":150,"dur":1.2}]}]},
  {"set":"dining_room","cast":{"grandpa":[-3.4,3.9,0,0],"sage":[0.2,3.9,0,0],"pip":[3.8,3.9,0,0]},"shots":[
   {"speaker":"grandpa","line":"Well... I'm not getting any younger.","camera":"medium:grandpa","no_cuts":True,"anims":{"grandpa":"sit_talk","sage":"sit","pip":"sit"},"face":"neutral"},
   {"_beat":"nothing","duration":0.9,"camera":"closeup:grandpa","no_cuts":True,"anims":{"grandpa":"sit","sage":"sit","pip":"sit"},"faces":{"grandpa":"sus"},"fx":later()[:1],"sfx":TICK},
   {"speaker":"grandpa","line":"...Yep. Still true.","camera":"closeup:grandpa","no_cuts":True,"anims":{"grandpa":"sit_talk","sage":"sit","pip":"sit"},"face":"sad","sfx":[{"name":"sad_trombone","at":0.9,"volume":0.4}]},
   {"speaker":"pip","line":"I wish my brother was a CHICKEN.","camera":"closeup:pip","no_cuts":True,"anims":{"pip":"sit_talk","sage":"sit","grandpa":"sit"},"face":"evil"},
   {"_beat":"countdown","duration":0.9,"camera":"closeup:sage","no_cuts":True,"move":"push","anims":{"sage":"sit_shocked","pip":"sit","grandpa":"sit"},"faces":{"sage":"scared"},"fx":later(),"sfx":TICK}]},
  {"set":"living_room_clear","cast":{"sage":[0,1.0,0,0],"pip":[2.6,1.4,0,-20]},"shots":[
   {"speaker":"sage","line":"Bawk! Bawk-BAWK!","camera":"medium:sage","no_cuts":True,"move":"shake","anims":{"sage":"chicken_dance","pip":"laugh"},"face":"shocked",
    "fx":[{"e":"🐔","at":0.2,"x":0.75,"y":0.42,"size":170,"dur":1.4,"anim":"shake"}],"sfx":[{"name":"boing","at":0.3}]},
   {"speaker":"sage","vo":True,"line":"Okay. ONE wish. Choose... carefully.","camera":"closeup:sage","no_cuts":True,"move":"push","anims":{"sage":"think","pip":"laugh"},"faces":{"sage":"sus"}},
   {"speaker":"sage","line":"I wish... this day would START OVER.","camera":"closeup:sage","no_cuts":True,"move":"punch","anims":{"sage":"point","pip":"shocked"},"face":"smug","faces":{"pip":"shocked"},
    "fx":[{"text":"3","color":"#ffd23f","size":200,"at":1.6,"x":0.5,"y":0.72,"dur":0.3,"anim":"pop"}],"sfx":TICK}]},
  {"set":"classroom_bright","cast":cls_cast,"props":cls_props(),"_beat":"LOOP: identical to scene 1","shots":[
   {"_beat":"LOOP 2-1","duration":0.7,"camera":CW,"no_cuts":True,"move":"none","pad":0.0,"anims":A(),"faces":{"sage":"neutral"},
    "fx":[{"text":"2","color":"#ffd23f","size":200,"at":0.0,"x":0.5,"y":0.72,"dur":0.33,"anim":"pop"},{"text":"1","color":"#ffd23f","size":200,"at":0.35,"x":0.5,"y":0.72,"dur":0.33,"anim":"pop"}],
    "sfx":[{"name":"whoosh","at":0.4,"volume":0.5}]}]}
 ]}
json.dump(ep,open("/home/user/YOUTUBE-VIDEO/episodes/shorts/s20_comes_true.json","w"),indent=1,ensure_ascii=False)
print("ok")
