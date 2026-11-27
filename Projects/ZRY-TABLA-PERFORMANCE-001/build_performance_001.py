import os, math, json
import numpy as np
import soundfile as sf

SR=44100
BPM=98
BEAT=60.0/BPM
S16=BEAT/4.0

OLD=r"%ZIRYAB_STUDIO%\Samples\CC0_Egyptian_Perc"
NEW=r"%ZIRYAB_SAMPLES%\New folder"
OUT=r"%ZIRYAB_STUDIO%\Projects\ZRY-TABLA-PERFORMANCE-001"
LISTEN=r"%ZIRYAB_SAMPLES%"
os.makedirs(LISTEN,exist_ok=True)

def load(path):
    x,sr=sf.read(path,dtype="float32",always_2d=False)
    if x.ndim>1:x=x.mean(axis=1)
    x=x.astype(np.float64)
    if sr!=SR:
        old=np.arange(len(x))/sr
        new=np.arange(int(round(len(x)*SR/sr)))/SR
        x=np.interp(new,old,x)
    return x

def trim(x,secs,fade=.05):
    y=x[:min(len(x),int(secs*SR))].copy()
    f=min(len(y),int(fade*SR))
    if f>1:y[-f:]*=np.linspace(1,0,f)
    return y

D   = trim(load(os.path.join(NEW,"Darbuka_68_76_SP.wav")),.58)
KA  = trim(load(os.path.join(NEW,"413798__pjcohen__doumbek_ka2.wav")),.30)
MUT = trim(load(os.path.join(NEW,"413782__pjcohen__doumbek_mute2.wav")),.20)
SLP = trim(load(os.path.join(NEW,"413781__pjcohen__doumbek_slap1.wav")),.18)
T1  = trim(load(os.path.join(OLD,"tak_02_03.flac")),.18)
T2  = trim(load(os.path.join(OLD,"tak_02_07.flac")),.18)

# All patterns are 16 slots in 4/4.
# No quantization humanization yet. Character comes from articulation + dynamics + phrase design.
BASE = {
 "MAQSUM": ["D","-","T","-","-","-","T","-","D","-","T","-","-","-","T","-"],
 "BALADI": ["D","-","D","-","-","-","T","-","D","-","T","-","-","-","T","-"],
 "SAIDI":  ["D","-","T","-","-","-","D","-","D","-","T","-","-","-","T","-"],
}

# Two restrained movements plus one turnaround per rhythm.
MOVES = {
 "MAQSUM":[
   ["D","-","T","K","-","-","T","-","D","-","T","-","K","-","T","-"],
   ["D","-","T","-","M","-","T","-","D","-","T","K","-","-","T","-"],
   ["D","-","T","K","T","-","M","-","D","-","T","-","S","K","T","-"],
 ],
 "BALADI":[
   ["D","D","-","-","M","-","T","-","D","-","T","-","K","-","T","-"],
   ["D","D","-","T","-","M","T","-","D","-","T","K","-","-","T","-"],
   ["D","D","M","-","T","K","-","-","D","-","T","-","S","K","T","-"],
 ],
 "SAIDI":[
   ["D","-","T","-","K","-","D","-","D","-","T","-","K","-","T","-"],
   ["D","-","T","K","-","-","D","-","D","M","T","-","K","-","T","-"],
   ["D","-","T","K","T","-","D","-","D","M","T","-","S","K","T","-"],
 ]
}

structure=[
 ("BASE",2),
 ("MOVE1",2),
 ("MOVE2",2),
 ("TURN",1),
 ("BASE_RETURN",1),
]

section_gap=BEAT*1.5
lead=.5
bar_dur=16*S16
total=lead + 3*(sum(n for _,n in structure)*bar_dur + section_gap) + .5
N=int(total*SR)
L=np.zeros(N); R=np.zeros(N)

def add(sample,t,g,pan=0.0):
    i=int(round(t*SR)); m=min(len(sample),N-i)
    if m<=0:return
    y=sample[:m]*g
    lg=math.sqrt((1-pan)*.5); rg=math.sqrt((1+pan)*.5)
    L[i:i+m]+=y*lg; R[i:i+m]+=y*rg

def stroke(rhythm,sym,t,slot,bar_no):
    if sym=="D":
        g={"MAQSUM":.72,"BALADI":.82,"SAIDI":.78}[rhythm]
        if slot in (0,8): g*=1.04
        add(D,t,g,-.02)
    elif sym=="T":
        g={"MAQSUM":.47,"BALADI":.44,"SAIDI":.51}[rhythm]
        add(T1 if (bar_no+slot)%2==0 else T2,t,g,.03)
    elif sym=="K":
        add(KA,t,.34,-.035)
    elif sym=="M":
        add(MUT,t,.28,0.0)
    elif sym=="S":
        add(SLP,t,.26,.01)

cursor=lead
timeline=[]
for rhythm in ["MAQSUM","BALADI","SAIDI"]:
    rstart=cursor
    bar_no=0
    for tag,reps in structure:
        if tag=="BASE" or tag=="BASE_RETURN":
            pat=BASE[rhythm]
        elif tag=="MOVE1":
            pat=MOVES[rhythm][0]
        elif tag=="MOVE2":
            pat=MOVES[rhythm][1]
        else:
            pat=MOVES[rhythm][2]
        seg_start=cursor
        for _ in range(reps):
            for s,sym in enumerate(pat):
                if sym!="-": stroke(rhythm,sym,cursor+s*S16,s,bar_no)
            cursor+=bar_dur
            bar_no+=1
        timeline.append({
          "rhythm":rhythm,"part":tag,
          "start":round(seg_start,3),"end":round(cursor,3),
          "bars":reps,"pattern":" ".join(pat)
        })
    cursor+=section_gap
    timeline.append({"rhythm":rhythm,"section_start":round(rstart,3),"section_end":round(cursor-section_gap,3)})

mix=np.stack([L,R],axis=1)
pk=float(np.max(np.abs(mix))) or 1.0
mix*=10**(-8/20)/pk

name="ZIRYAB-PERFORMANCE-001-THREE-RHYTHMS-LIGHT-COLOR.wav"
wav=os.path.join(OUT,name)
listen=os.path.join(LISTEN,name)
sf.write(wav,mix,SR,subtype="PCM_24")
sf.write(listen,mix,SR,subtype="PCM_24")

report={
 "bpm":BPM,
 "structure":"base 2 bars -> move1 2 -> move2 2 -> turnaround 1 -> base return 1",
 "articulations":{
   "D":"Darbuka_68_76_SP.wav (DUM-like resonant candidate)",
   "T":["tak_02_03.flac","tak_02_07.flac"],
   "K":"413798__pjcohen__doumbek_ka2.wav (verified KA category; hand not assumed)",
   "M":"413782__pjcohen__doumbek_mute2.wav (verified MUTE category)",
   "S":"413781__pjcohen__doumbek_slap1.wav (verified SLAP category)"
 },
 "claims":["KA is not relabeled KAH_LEFT","MUTE is not relabeled DUM_CLOSED","SLAP is not relabeled SAK"],
 "humanization_ms":0,
 "rolls":0,
 "timeline":timeline
}
with open(os.path.join(OUT,"PERFORMANCE-001.json"),"w",encoding="utf-8") as f:
    json.dump(report,f,ensure_ascii=False,indent=2)

print(listen)
