import json
KW="at:-6.0,-2.6,5.4,-6.4,8.4,3.6,30"
EC="at:-8.2,4.6,4.6,-8.2,8.7,4.1,40"   # elf close-up on the counter
kit={"sage":[-5.2,6.4,0,170],"elf":[-8.2,8.7,3.3,0],"mom":[2.2,4.0,0,-35]}
def kprops(): return [{"id":"jar","type":"cookie_jar","at":[-5.2,8.6,3.3],"scale":0.8}]
def news(t="BREAKING NEWS"): return [{"text":t,"color":"#ff3b30","size":110,"at":0.0,"x":0.5,"y":0.7,"dur":1.2,"anim":"shake"}]
DING=[{"name":"ding","at":0.0,"volume":0.6}]
def A(**k):
    d={"sage":"reach_to","elf":"idle","mom":"hidden"}; d.update(k); return d
ep={"id":"s25_elf_spy","title":"Our Elf on the Shelf Is SPYING for Mom! 🎄","format":"short","mood":"bright","grade":"bright",
 "fog":False,"dof":False,"handheld":0.35,"caption_style":"word","caption_pos":"top","cut_every":1.25,"sting":False,"cta":{"at":16},
 "music":"quirky_loop","music_volume":0.13,"loop":True,
 "_loop":"Elf: 'Stay tuned... for MORE breaking news.' -> same kitchen shot -> Sage reaches for the cookie jar, Elf: 'BREAKING NEWS...'",
 "_secret":"The elf is staring straight at YOU (the camera) in the first second",
 "_pinned_comment":"Does YOUR elf snitch too? 🎄👇",
 "scenes":[
  {"set":"dining_room","cast":kit,"props":kprops(),"shots":[
   {"_beat":"HOOK (loop point)","speaker":"elf","line":"BREAKING NEWS. Sage is stealing a cookie.","camera":KW,"no_cuts":True,"move":"none","anims":A(elf="talk"),"face":"smug","sfx":DING,"fx":news()},
   {"speaker":"mom","line":"SAGE!","camera":"medium:mom","no_cuts":True,"move":"punch","anims":A(mom="point",sage="reach_caught"),"face":"angry","sfx":[{"name":"vine_boom","at":0.0}]},
   {"speaker":"sage","vo":True,"line":"Our elf on the shelf... reports EVERYTHING to Mom. LIVE.","camera":EC,"no_cuts":True,"move":"push","anims":A(elf="brag",sage="still"),"faces":{"elf":"smug"}}]},
  {"set":"dining_room","cast":{"grandpa":[-3.4,3.9,0,0],"pip":[3.8,3.9,0,0],"elf":[-8.2,8.7,3.3,15]},
   "props":[{"id":"gphone","type":"phone","at":[-3.0,1.4,2.17],"scale":1.0,"image":"textures/s14/phone_ok.png"}],"shots":[
   {"speaker":"elf","line":"Update: Grandpa is watching cat videos. Again.","camera":EC,"no_cuts":True,"anims":{"elf":"talk","grandpa":"sit","pip":"sit"},"face":"smug","sfx":DING,"fx":news("UPDATE")},
   {"speaker":"grandpa","line":"...Snitch.","camera":"closeup:grandpa","no_cuts":True,"move":"push","anims":{"grandpa":"sit","elf":"idle","pip":"sit"},"face":"angry","sfx":[{"name":"vine_boom","at":0.5,"volume":0.6}]},
   {"speaker":"elf","line":"Also... Pip drew on the wall.","camera":EC,"no_cuts":True,"anims":{"elf":"point","grandpa":"sit","pip":"sit"},"face":"smug","sfx":DING},
   {"speaker":"pip","line":"It's called ART.","camera":"closeup:pip","no_cuts":True,"anims":{"pip":"sit_talk","grandpa":"sit","elf":"idle"},"face":"smug",
    "fx":[{"e":"🖍️","at":0.3,"x":0.72,"y":0.48,"size":140,"dur":1.2}]}]},
  {"set":"dining_room","cast":dict(kit,sage=[-5.6,6.4,0,-30]),"props":kprops(),"shots":[
   {"speaker":"sage","line":"Hey, elf. I'll give you a cookie... to stay quiet.","camera":"at:-6.8,0.4,4.8,-6.9,7.5,3.8,30","no_cuts":True,"anims":A(sage="talk",elf="idle"),"faces":{"sage":"smug"}},
   {"speaker":"elf","line":"Bribery attempt. REPORTING.","camera":EC,"no_cuts":True,"move":"punch","anims":A(elf="cross_arms",sage="still"),"face":"angry","sfx":DING+[{"name":"siren","at":0.3,"volume":0.35}],"fx":news("BRIBERY!")}]},
  {"set":"living_room_clear","cast":{"mom":[1.4,1.2,0,-15],"sage":[-1.8,1.0,0,20]},"shots":[
   {"speaker":"sage","vo":True,"line":"So I locked him in a drawer. Problem solved.","camera":"medium:sage","no_cuts":True,"anims":{"sage":"brag","mom":"idle"},"faces":{"sage":"smug"}},
   {"_beat":"text from elf","duration":1.8,"camera":"medium:mom","no_cuts":True,"anims":{"mom":"idle","sage":"brag"},"faces":{"mom":"sus"},"sfx":[{"name":"notification","at":0.1}],
    "fx":[{"phone":"Sage put me in a drawer.","sender":"Elf","at":0.1,"x":0.5,"y":0.58,"size":640,"dur":1.6}]},
   {"speaker":"mom","line":"Sage. Let him OUT.","camera":"closeup:mom","no_cuts":True,"move":"push","anims":{"mom":"cross_arms","sage":"shocked"},"face":"angry"}]},
  {"set":"dining_room","cast":{"mom":[1.0,4.6,0,0],"elf":[-8.2,8.7,3.3,25]},"props":[{"id":"plate","type":"plate","at":[1.0,2.2,2.16],"scale":0.8}],"shots":[
   {"speaker":"elf","line":"BREAKING NEWS... Mom ate Santa's cookies.","camera":EC,"no_cuts":True,"anims":{"elf":"talk","mom":"sit_eat"},"face":"evil","sfx":DING,"fx":news()},
   {"_beat":"mom caught","duration":1.0,"camera":"closeup:mom","no_cuts":True,"move":"punch","anims":{"mom":"sit_reach_freeze","elf":"idle"},"faces":{"mom":"shocked"},
    "fx":[{"e":"🍪","at":0.0,"x":0.66,"y":0.6,"size":140,"dur":0.9}],"sfx":[{"name":"record_scratch","at":0.0,"volume":0.6}]},
   {"speaker":"mom","line":"...Who wants PRESENTS?!","camera":"closeup:mom","no_cuts":True,"anims":{"mom":"sit_thumbs_up","elf":"idle"},"face":"happy"}]},
  {"set":"dining_room","cast":kit,"props":kprops(),"_beat":"LOOP: identical to scene 1","shots":[
   {"_beat":"LOOP","speaker":"elf","line":"Stay tuned... for MORE breaking news.","camera":KW,"no_cuts":True,"move":"none","pad":0.0,"anims":A(elf="talk"),"faces":{"elf":"smug"}}]}
 ]}
json.dump(ep,open("/home/user/YOUTUBE-VIDEO/episodes/shorts/s25_elf_spy.json","w"),indent=1,ensure_ascii=False)
print("ok")
