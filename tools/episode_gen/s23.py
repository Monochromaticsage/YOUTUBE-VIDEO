import json
def sg(who,hidden=False):
    d={"id":f"sg_{who}","type":"sunglasses","attach":f"{who}:head","local":[0,-0.64,0.74],"local_rot":[0,0,0]}
    if hidden: d["hidden"]=True
    return d
HW="at:0.2,-7.6,4.6,0.2,2.0,3.2,30"
hall={"dad":[1.2,1.0,0,-15],"sage":[-2.0,1.2,0,20],"ms_brick":[3.4,6.5,0,-20]}
ep={"id":"s23_cool_dad","title":"My Dad Tried to Be COOL at My School 😎","format":"short","mood":"bright","grade":"bright",
 "fog":False,"dof":False,"handheld":0.35,"caption_style":"word","caption_pos":"top","cut_every":1.25,"sting":False,"cta":{"at":16},
 "music":"happy_loop","music_volume":0.13,"loop":True,
 "_loop":"Sage: 'So if you ever see a guy in sunglasses saying—' -> same hallway shot -> Dad: 'What's up, my dudes?'",
 "_secret":"Ms. Brick is ALREADY wearing sunglasses in the background of the first second",
 "_pinned_comment":"Is YOUR dad like this? 😎👇",
 "scenes":[
  {"set":"hallway","cast":hall,"props":[sg("dad"),sg("ms_brick")],"shots":[
   {"_beat":"HOOK (loop point)","speaker":"dad","line":"What's up, my DUDES?","camera":HW,"no_cuts":True,"move":"none","anims":{"dad":"wave","sage":"facepalm","ms_brick":"cross_arms"},"face":"happy","faces":{"sage":"sad"}},
   {"speaker":"sage","vo":True,"line":"This is my dad. He came to school today... to be COOL.","camera":"medium:dad","no_cuts":True,"anims":{"dad":"dab","sage":"facepalm","ms_brick":"cross_arms"},"faces":{"dad":"happy"},
    "sfx":[{"name":"airhorn","at":0.9,"volume":0.35}]},
   {"speaker":"sage","line":"Dad. Please. Nobody dabs anymore.","camera":"medium:sage","no_cuts":True,"anims":{"sage":"talk","dad":"dab","ms_brick":"cross_arms"},"face":"sad"}]},
  {"set":"hallway","cast":{"dad":[-1.6,1.0,0,20],"goldie":[1.6,1.0,0,-20]},"props":[sg("dad")],"shots":[
   {"speaker":"dad","line":"Nice chain, bro. Is it... BUSSIN'?","camera":"medium:dad","no_cuts":True,"anims":{"dad":"point","goldie":"brag"},"face":"happy"},
   {"speaker":"goldie","line":"...Sir. Please leave.","camera":"closeup:goldie","no_cuts":True,"move":"push","anims":{"goldie":"cross_arms","dad":"point"},"face":"sus","sfx":[{"name":"sad_trombone","at":1.0,"volume":0.4}]}]},
  {"set":"classroom_bright","cast":{"dad":[3,1.6,0,0],"sage":[-3,1.6,0,0],"ms_brick":[1.8,9.3,0,0]},"props":[sg("dad")],"shots":[
   {"speaker":"dad","line":"Ms. Brick! Can I go to the bathroom?","camera":"medium:dad","no_cuts":True,"anims":{"dad":"raise_hand","sage":"sit","ms_brick":"idle"},"face":"happy"},
   {"speaker":"ms_brick","line":"Sir. You are FORTY-TWO.","camera":"medium:ms_brick","no_cuts":True,"move":"punch","anims":{"ms_brick":"point","dad":"sit","sage":"facepalm"},"face":"angry"}]},
  {"set":"playground","cast":{"dad":[-1.8,0,0,20],"noob":[1.8,0,0,-20],"sage":[-4.5,3,0,25]},"props":[sg("dad")],"shots":[
   {"speaker":"noob","line":"Dance battle. You versus me. Right now.","camera":"medium:noob","no_cuts":True,"anims":{"noob":"point","dad":"cross_arms","sage":"idle"},"face":"smug"},
   {"speaker":"noob","line":"Ha! Beat THAT, old man!","camera":"medium:noob","no_cuts":True,"anims":{"noob":"dance","dad":"cross_arms","sage":"idle"},"face":"happy","sfx":[{"name":"record_scratch","at":0.0,"volume":0.4}]},
   {"_beat":"dad backflip","duration":1.6,"camera":"medium:dad","no_cuts":True,"move":"shake","anims":{"dad":"backflip","noob":"shocked","sage":"shocked"},"faces":{"noob":"shocked","sage":"shocked","dad":"happy"},
    "sfx":[{"name":"whoosh","at":0.2},{"name":"vine_boom","at":1.0}],"fx":[{"text":"BACKFLIP?!","color":"#ffd23f","size":130,"at":0.9,"x":0.5,"y":0.72,"dur":0.7,"anim":"shake"}]},
   {"speaker":"noob","line":"...Okay. He's actually GOOD.","camera":"closeup:noob","no_cuts":True,"anims":{"noob":"shocked","dad":"dab","sage":"shocked"},"face":"shocked"}]},
  {"set":"hallway","cast":{"goldie":[-3.2,1.2,0,15],"noob":[0,1.0,0,0],"ms_brick":[3.2,1.2,0,-15],"sage":[0,-1.8,0,180]},
   "props":[sg("goldie",True),sg("noob",True),sg("ms_brick",True)],"shots":[
   {"speaker":"sage","vo":True,"line":"By lunch... EVERYONE wanted to be like my dad.","camera":"at:0,-9.0,4.4,0,1.0,3.3,30","no_cuts":True,"show":["sg_goldie","sg_noob","sg_ms_brick"],
    "anims":{"goldie":"dab","noob":"dab","ms_brick":"dab","sage":"hidden"},"faces":{"goldie":"happy","noob":"happy","ms_brick":"happy"},"sfx":[{"name":"pop","at":0.0},{"name":"pop","at":0.15},{"name":"pop","at":0.3}]},
   {"speaker":"goldie","line":"What's up, my DUDES!","camera":"medium:goldie","no_cuts":True,"anims":{"goldie":"dab","noob":"dab","ms_brick":"dab","sage":"hidden"},"face":"happy"}]},
  {"set":"hallway","cast":{"sage":[0,1.0,0,0]},"shots":[
   {"speaker":"sage","line":"Wait... does that make ME the uncool one now?","camera":"closeup:sage","no_cuts":True,"move":"push","anims":{"sage":"think"},"face":"sad","sfx":[{"name":"sad_trombone","at":2.0,"volume":0.4}]}]},
  {"set":"hallway","cast":hall,"props":[sg("dad"),sg("ms_brick")],"_beat":"LOOP: identical to scene 1","shots":[
   {"_beat":"LOOP","speaker":"sage","vo":True,"line":"So if you ever see a guy in sunglasses saying—","camera":HW,"no_cuts":True,"move":"none","pad":0.0,"anims":{"dad":"still","sage":"facepalm","ms_brick":"cross_arms"},"faces":{"sage":"sad","dad":"happy"}}]}
 ]}
json.dump(ep,open("/home/user/YOUTUBE-VIDEO/episodes/shorts/s23_cool_dad.json","w"),indent=1,ensure_ascii=False)
print("ok")
