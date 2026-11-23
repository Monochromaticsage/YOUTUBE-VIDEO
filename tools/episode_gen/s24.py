import json
OW="at:0,-7.8,4.3,0,2.0,3.0,30"
TREE={"id":"tree","type":"xmas_tree","at":[-4.6,4.6,0],"scale":0.85}
def gifts(): return [TREE,{"id":"g1","type":"present","at":[-3.0,3.2,0],"color":"#1e88e5","ribbon":"#ffffff","size":1.0},
                     {"id":"g2","type":"present","at":[-5.6,2.6,0],"color":"#43a047","ribbon":"#e53935","size":0.8},
                     {"id":"g3","type":"present","at":[3.4,3.6,0],"color":"#e53935","ribbon":"#ffd54f","size":0.9}]
kids={"sage":[-1.4,1.0,0,15],"pip":[1.6,1.6,0,-15]}
crayon={"id":"crayon","type":"pencil","attach":"pip:arm_l","local":[0.5,-0.45,-1.55],"local_rot":[90,0,0]}
def em(e,x=0.7,y=0.5,at=0.3,dur=1.4,size=170): return {"e":e,"at":at,"x":x,"y":y,"size":size,"dur":dur,"anim":"pop"}
UNWRAP=[{"name":"whoosh","at":0.0,"volume":0.4},{"name":"pop","at":0.25,"volume":0.6}]
ep={"id":"s24_santa_mixup","title":"Santa Mixed Up EVERYONE'S Presents! 🎁","format":"short","mood":"bright","grade":"bright",
 "fog":False,"dof":False,"handheld":0.35,"caption_style":"word","caption_pos":"top","cut_every":1.25,"sting":False,"cta":{"at":16},
 "music":"happy_loop","music_volume":0.13,"loop":True,
 "_loop":"Pip: 'Here. Open yours.' -> same shot -> Sage: 'A... UNICORN dress?'",
 "_secret":"Pip is already holding a crayon in the first second (she wrote Santa's list)",
 "_pinned_comment":"What's the WORST present you ever got? 🎁👇",
 "scenes":[
  {"set":"living_room_clear","cast":kids,"props":gifts()+[crayon],"shots":[
   {"_beat":"HOOK (loop point)","speaker":"sage","line":"A... UNICORN dress?","camera":OW,"no_cuts":True,"move":"none","anims":{"sage":"shocked","pip":"idle"},"face":"shocked","faces":{"pip":"smug"},
    "sfx":UNWRAP,"fx":[em("🦄",0.3,0.42),em("👗",0.42,0.55,0.45)]},
   {"speaker":"pip","line":"And I got a... VIDEO GAME?","camera":"at:2.7,-3.0,3.7,1.6,1.6,3.3,34","no_cuts":True,"anims":{"pip":"shrug","sage":"shocked"},"face":"smug","fx":[em("🎮",0.72,0.45)],"sfx":UNWRAP},
   {"speaker":"sage","vo":True,"line":"This Christmas... Santa mixed up EVERYONE'S presents.","camera":"at:-1.8,-8.5,5.0,-1.8,3.0,3.4,30","no_cuts":True,"move":"push","anims":{"sage":"facepalm","pip":"idle"},"faces":{"sage":"sad"}}]},
  {"set":"living_room_clear","cast":{"grandpa":[-1.6,1.0,0,20],"mom":[1.6,1.2,0,-20]},"props":gifts(),"shots":[
   {"speaker":"grandpa","line":"A baby bottle?","camera":"medium:grandpa","no_cuts":True,"anims":{"grandpa":"sus" if False else "think","mom":"idle"},"face":"sus","fx":[em("🍼",0.7,0.5)],"sfx":UNWRAP},
   {"speaker":"grandpa","line":"...Actually. I'll keep it.","camera":"closeup:grandpa","no_cuts":True,"move":"push","anims":{"grandpa":"nod","mom":"idle"},"face":"happy"},
   {"speaker":"mom","line":"Gold sneakers? These are GOLDIE'S.","camera":"medium:mom","no_cuts":True,"anims":{"mom":"shrug","grandpa":"idle"},"face":"sus","fx":[em("👟",0.3,0.5)],"sfx":UNWRAP}]},
  {"set":"hallway","cast":{"goldie":[0.6,1,0,0]},"shots":[
   {"speaker":"goldie","line":"A BANANA? I asked for a YACHT!","camera":"medium:goldie","no_cuts":True,"move":"shake","anims":{"goldie":"angry"},"face":"angry","fx":[em("🍌",0.72,0.5)],"sfx":UNWRAP}]},
  {"set":"living_room_window","cast":{"noob":[0,1,0,0]},"shots":[
   {"speaker":"noob","line":"A YACHT?! ...But I asked for a banana.","camera":"medium:noob","no_cuts":True,"anims":{"noob":"sad"},"face":"sad","fx":[em("🛥️",0.7,0.42)],"sfx":UNWRAP+[{"name":"sad_trombone","at":1.6,"volume":0.4}]}]},
  {"set":"classroom_bright","cast":{"ms_brick":[1.8,9.3,0,0]},"shots":[
   {"speaker":"ms_brick","line":"'How to Be FUN.' ...By Noob?","camera":"medium:ms_brick","no_cuts":True,"anims":{"ms_brick":"think"},"face":"sus",
    "fx":[{"text":"HOW TO BE FUN","color":"#ffd23f","size":100,"at":0.2,"x":0.5,"y":0.7,"dur":1.6}],"sfx":UNWRAP}]},
  {"set":"living_room_clear","cast":kids,"props":gifts()+[crayon],"shots":[
   {"speaker":"sage","vo":True,"line":"Then I found Santa's list. Written in... CRAYON.","camera":"closeup:sage","no_cuts":True,"move":"push","anims":{"sage":"hold_photo","pip":"idle"},"faces":{"sage":"sus"},
    "fx":[{"text":"SANTA'S LIST","color":"#e53935","size":110,"at":0.6,"x":0.5,"y":0.68,"dur":1.8,"anim":"shake"}]},
   {"speaker":"sage","line":"Pip?! This is YOUR handwriting!","camera":"medium:sage","no_cuts":True,"move":"punch","anims":{"sage":"point","pip":"idle"},"face":"angry","sfx":[{"name":"record_scratch","at":0.0,"volume":0.5}]},
   {"speaker":"pip","line":"Santa looked tired. I helped.","camera":"at:2.7,-3.0,3.7,1.6,1.6,3.3,34","no_cuts":True,"anims":{"pip":"brag","sage":"point"},"face":"smug"},
   {"speaker":"pip","line":"...You're welcome.","camera":"at:2.7,-3.0,3.7,1.6,1.6,3.3,34","no_cuts":True,"move":"push","anims":{"pip":"nod","sage":"facepalm"},"face":"evil","sfx":[{"name":"sting","at":0.2,"volume":0.5}]}]},
  {"set":"living_room_clear","cast":kids,"props":gifts()+[crayon],"_beat":"LOOP: identical to scene 1","shots":[
   {"_beat":"LOOP","speaker":"pip","line":"Here. Open yours.","camera":OW,"no_cuts":True,"move":"none","pad":0.0,"anims":{"pip":"reach_to","sage":"idle"},"faces":{"pip":"smug","sage":"neutral"}}]}
 ]}
json.dump(ep,open("/home/user/YOUTUBE-VIDEO/episodes/shorts/s24_santa_mixup.json","w"),indent=1,ensure_ascii=False)
print("ok")
