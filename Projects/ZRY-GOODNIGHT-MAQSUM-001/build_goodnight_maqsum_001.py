import os, math, json, random
import numpy as np
import soundfile as sf

SR=44100
BPM=102
BEAT=60/BPM
S16=BEAT/4
OLD=r"%ZIRYAB_STUDIO%\Samples\CC0_Egyptian_Perc"
NEW=r"%ZIRYAB_SAMPLES%\New folder"
OUT=r"%ZIRYAB_STUDIO%\Projects\ZRY-GOODNIGHT-MAQSUM-001"
LISTEN=r"%ZIRYAB_SAMPLES%"
os.makedirs(LISTEN,exist_ok=True)

def load(path):
    x,sr=sf.read(path,dtype="float32",always_2d=False)
    if x.ndim>1: x=x.mean(axis=1)
    x=x.astype(np.float64)
    if sr!=SR:
        old=np.arange(len(x))/sr
        new=np.arange(int(round(len(x)*SR/sr)))/SR
        x=np.interp(new,old,x)
    return x

def trim(x,secs,fade=.05):
    y=x[:min(len(x),int(secs*SR))].copy()
    f=min(len(y),int(fade*SR))
    if f>1: y[-f:]*=np.linspace(1,0,f)
    return y

D=trim(load(os.path.join(NEW,"Darbuka_68_76_SP.wav")),.62)
KA=trim(load(os.path.join(NEW,"413798__pjcohen__doumbek_ka2.wav")),.26)
MUT=trim(load(os.path.join(NEW,"413782__pjcohen__doumbek_mute2.wav")),.20)
SLP=trim(load(os.path.join(NEW,"413781__pjcohen__doumbek_slap1.wav")),.18)
T1=trim(load(os.path.join(OLD,"tak_02_03.flac")),.18)
T2=trim(load(os.path.join(OLD,"tak_02_07.flac")),.18)

# Learned/source-derived vocabulary:
BASIC=["D","-","T","-","-","-","T","-","D","-","T","-","-","-","T","-"]
LIGHT=["D","-","T","-","t","k","T","-","D","-","t","k","T","-","t","k"]
# restrained color derived from learned slap/mute vocabulary, not a claimed canonical source pattern
BREAK1=["D","-","-","-","M","-","T","-","D","-","K","-","S","-","T","-"]
ANSWER=["D","-","T","K","-","-","T","-","D","-","T","-","K","-","T","-"]
FINAL=["D","-","T","-","-","-","T","-","D","-","T","-","-","-","-","-"]

structure=[
 ("BASIC",BASIC,2),
 ("LIGHT",LIGHT,2),
 ("BASIC_RETURN",BASIC,1),
 ("BREAK",BREAK1,1),
 ("ANSWER",ANSWER,2),
 ("LIGHT_RETURN",LIGHT,2),
 ("FINAL",FINAL,1)
]
bars_total=sum(n for _,_,n in structure)
lead=.35
bar_dur=16*S16
tail=1.5
N=int((lead+bars_total*bar_dur+tail)*SR)
L=np.zeros(N);R=np.zeros(N)

def add(s,t,g,pan=0):
    i=int(round(t*SR)); m=min(len(s),N-i)
    if m<=0:return
    y=s[:m]*g
    lg=math.sqrt((1-pan)*.5); rg=math.sqrt((1+pan)*.5)
    L[i:i+m]+=y*lg; R[i:i+m]+=y*rg

random.seed(7)
def play(sym,t,slot,bar_idx,tag):
    # subtle controlled dynamics and tiny timing variation only
    jitter=(random.uniform(-0.006,0.006) if sym in ("t","k","T","K") else random.uniform(-0.003,0.003))
    tt=max(0,t+jitter)
    if sym=="D":
        g=.72*(1.05 if slot in (0,8) else 1.0)
        if tag=="FINAL" and slot==0:g=.80
        add(D,tt,g,-.02)
    elif sym=="T":
        add(T1 if (bar_idx+slot)%2==0 else T2,tt,.46,.03)
    elif sym=="t":
        add(T1 if (bar_idx+slot)%2==0 else T2,tt,.25,.03)
    elif sym=="k":
        add(KA,tt,.22,-.03)
    elif sym=="K":
        add(KA,tt,.30,-.03)
    elif sym=="M":
        add(MUT,tt,.23,0)
    elif sym=="S":
        add(SLP,tt,.20,.01)

cursor=lead
timeline=[]
bar_idx=0
for tag,pat,reps in structure:
    st=cursor
    for _ in range(reps):
        for s,sym in enumerate(pat):
            if sym!="-": play(sym,cursor+s*S16,s,bar_idx,tag)
        cursor+=bar_dur
        bar_idx+=1
    timeline.append({"part":tag,"bars":reps,"start":round(st,3),"end":round(cursor,3)})

# open final DUM ring as a coda
add(D,cursor+.06,.68,-.02)

mix=np.stack([L,R],1)
pk=float(np.max(np.abs(mix))) or 1
mix*=10**(-7/20)/pk

name="ZIRYAB-GOODNIGHT-MAQSUM-001.wav"
listen=os.path.join(LISTEN,name)
project=os.path.join(OUT,name)
sf.write(listen,mix,SR,subtype="PCM_24")
sf.write(project,mix,SR,subtype="PCM_24")

with open(os.path.join(OUT,"GOODNIGHT-MAQSUM-001.json"),"w",encoding="utf-8") as f:
    json.dump({
      "bpm":BPM,
      "duration_sec":round(len(mix)/SR,2),
      "structure":timeline,
      "source_basis":"Maqsum basic/light vocabulary learned from Khafif; break/answer are restrained Ziryab practice composition",
      "timing_jitter_ms":"DUM ±3; rim strokes ±6",
      "rolls":0
    },f,ensure_ascii=False,indent=2)

print(listen)
print(round(len(mix)/SR,2))
