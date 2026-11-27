import os, math, json, random
from pathlib import Path
import numpy as np
import soundfile as sf

SR=44100
BPM=96.0
BEAT=60.0/BPM
S16=BEAT/4
BAR=4*BEAT
TOTAL=44.0
N=int(TOTAL*SR)

OLD=r"%ZIRYAB_STUDIO%\Samples\CC0_Egyptian_Perc"
NEW=r"%ZIRYAB_SAMPLES%\New folder"
OUT=Path(r"%ZIRYAB_STUDIO%\Projects\ZRY-NYLON-TABLA-001\Renders\TABLA_REAL_STEM.wav")
PROV=Path(r"%ZIRYAB_STUDIO%\Projects\ZRY-NYLON-TABLA-001\Provenance\tabla_score.json")

def load(path):
    x,sr=sf.read(path,dtype="float64",always_2d=False)
    if x.ndim>1:x=x.mean(axis=1)
    if sr!=SR:
        old=np.arange(len(x))/sr
        new=np.arange(int(round(len(x)*SR/sr)))/SR
        x=np.interp(new,old,x)
    x=x-np.mean(x)
    p=float(np.max(np.abs(x))) or 1
    return x/p

D=load(os.path.join(NEW,"Darbuka_68_76_SP.wav"))
T=[load(os.path.join(OLD,"tak_02_03.flac")),load(os.path.join(OLD,"tak_02_07.flac"))]
K=load(os.path.join(NEW,"413798__pjcohen__doumbek_ka2.wav"))
S=load(os.path.join(NEW,"413781__pjcohen__doumbek_slap1.wav"))
M=load(os.path.join(NEW,"413782__pjcohen__doumbek_mute2.wav"))

# 16-slot patterns. Lowercase = light articulation, '-' = rest.
P={
"basic": ["D","-","T","-","-","-","T","-","D","-","T","-","-","-","T","-"],
"light": ["D","-","T","-","t","k","T","-","D","-","t","k","T","-","t","k"],
"drive": ["D","-","T","k","t","k","T","-","D","k","t","k","T","k","t","k"],
"open":  ["D","-","-","-","T","-","-","-","D","-","-","-","T","-","-","-"],
"break1":["D","-","-","-","-","-","T","-","-","-","K","-","S","-","T","-"],
"turn":  ["-","-","k","k","D","-","t","k","T","t","k","T","k","t","K","-"],
"coda":  ["D","-","-","-","t","k","-","-","-","-","T","-","k","-","-","-"],
}

plan={
 1:None,
 2:"open",
 3:"basic",4:"basic",5:"light",6:"basic",
 7:"light",8:"drive",9:"light",10:"drive",
 11:"open",12:"break1",
 13:"basic",14:"light",15:"drive",16:"turn",
 17:"coda"
}

L=np.zeros(N);R=np.zeros(N)
events=[]
random.seed(19)

def add(sig,t,g,pan=0.0):
    i=int(round(t*SR))
    if i<0:return
    m=min(len(sig),N-i)
    if m<=0:return
    y=sig[:m]*g
    lg=math.sqrt((1-pan)*0.5); rg=math.sqrt((1+pan)*0.5)
    L[i:i+m]+=y*lg
    R[i:i+m]+=y*rg

for bar in range(1,18):
    name=plan[bar]
    if not name: continue
    pat=P[name]
    for slot,sym in enumerate(pat):
        if sym=="-": continue
        base=(bar-1)*BAR+slot*S16
        # conscious push on rim-family, steady DUM anchors.
        if sym in ("T","t","K","k","S"):
            jitter=random.uniform(-0.0045,0.0025)
        else:
            jitter=random.uniform(-0.002,0.002)
        t0=max(0,base+jitter)
        accent=1.0
        if slot in (0,8): accent*=1.05
        if bar in (8,10,15,16): accent*=1.03

        if sym=="D":
            g=0.74*accent
            add(D,t0,g,-0.02)
        elif sym=="T":
            g=0.46*accent
            sig=T[(bar+slot)%len(T)]
            add(sig,t0,g,0.04)
        elif sym=="t":
            g=0.26
            sig=T[(bar+slot)%len(T)]
            add(sig,t0,g,0.04)
        elif sym=="K":
            g=0.34*accent
            add(K,t0,g,-0.05)
        elif sym=="k":
            g=0.22
            add(K,t0,g,-0.05)
        elif sym=="S":
            g=0.23
            add(S,t0,g,0.02)
        events.append({"bar":bar,"slot":slot,"stroke":sym,"time":round(t0,6),"pattern":name})

# One deliberate tiny pickup before bar 13 return.
pickup=(13-1)*BAR-0.19
add(M,pickup,0.18,0)
events.append({"bar":12,"slot":"pickup","stroke":"M","time":round(pickup,6),"pattern":"return_pickup"})

# natural fade only at tail
fade=int(0.35*SR)
if fade<N:
    env=np.ones(N)
    env[-fade:]=np.linspace(1,0,fade)
    L*=env;R*=env

st=np.stack([L,R],1)
pk=float(np.max(np.abs(st))) or 1
st*=10**(-2/20)/pk
sf.write(OUT,st,SR,subtype="PCM_24")
PROV.write_text(json.dumps({
 "bpm":BPM,
 "bars":17,
 "plan":plan,
 "patterns":P,
 "event_count":len(events),
 "events":events,
 "samples":{
  "D":"Darbuka_68_76_SP.wav",
  "T":["tak_02_03.flac","tak_02_07.flac"],
  "K":"413798__pjcohen__doumbek_ka2.wav",
  "S":"413781__pjcohen__doumbek_slap1.wav",
  "M":"413782__pjcohen__doumbek_mute2.wav"
 },
 "note":"built for this composition; no loop copy across full piece"
},ensure_ascii=False,indent=2),encoding="utf-8")
print("events",len(events),"peak_db",-2.0,"out",OUT)
