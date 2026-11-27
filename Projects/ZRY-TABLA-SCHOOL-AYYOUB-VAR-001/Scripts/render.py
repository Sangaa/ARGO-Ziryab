import os, json, math
from pathlib import Path
import numpy as np
import soundfile as sf

SR=44100
BPM=100.0
BEAT=60.0/BPM
S16=BEAT/4.0
BAR=2.0*BEAT

D_PATH=r"%ZIRYAB_SAMPLES%\New folder\Darbuka_68_76_SP.wav"
T_PATHS=[
 r"%ZIRYAB_STUDIO%\Samples\CC0_Egyptian_Perc\tak_02_03.flac",
 r"%ZIRYAB_STUDIO%\Samples\CC0_Egyptian_Perc\tak_02_07.flac",
]
K_PATH=r"%ZIRYAB_SAMPLES%\New folder\413798__pjcohen__doumbek_ka2.wav"

OUT=Path(r"%ZIRYAB_STUDIO%\Projects\ZRY-TABLA-SCHOOL-AYYOUB-VAR-001\Renders\ZIRYAB-AYYOUB-VAR-001-100BPM.wav")
DESK=Path(r"%ZIRYAB_SAMPLES%\ZIRYAB-AYYOUB-VAR-001-100BPM.wav")
PROV=Path(r"%ZIRYAB_STUDIO%\Projects\ZRY-TABLA-SCHOOL-AYYOUB-VAR-001\Provenance\lesson.json")

def load(p):
    x,sr=sf.read(p,dtype="float64",always_2d=False)
    if x.ndim>1:x=x.mean(1)
    if sr!=SR:
        old=np.arange(len(x))/sr
        new=np.arange(int(round(len(x)*SR/sr)))/SR
        x=np.interp(new,old,x)
    x=x-np.mean(x)
    return x/(np.max(np.abs(x))+1e-12)

D=load(D_PATH)
T=[load(p) for p in T_PATHS]
K=load(K_PATH)

BASE=["D","-","K","D","-","T","-","K"]

# Two light support strokes only. Core Ayyoub anchors untouched.
VAR =["D","t","K","D","k","T","-","K"]

plan=["BASE","BASE","VAR","VAR","BASE","VAR","BASE","BASE"]
patterns={"BASE":BASE,"VAR":VAR}

N=int((len(plan)*BAR+0.45)*SR)
L=np.zeros(N);R=np.zeros(N);events=[];ti=0

def add(sig,t,g,pan=0):
    i=int(round(t*SR))
    if i<0 or i>=N:return
    m=min(len(sig),N-i)
    if m<=0:return
    y=sig[:m]*g
    L[i:i+m]+=y*math.sqrt((1-pan)*.5)
    R[i:i+m]+=y*math.sqrt((1+pan)*.5)

for bi,name in enumerate(plan,1):
    for slot,s in enumerate(patterns[name]):
        if s=="-": continue
        t=(bi-1)*BAR+slot*S16
        if s=="D":
            g=.58 if slot==0 else .52
            add(D,t,g,-.01)
        elif s=="T":
            add(T[ti%2],t,.42,.04);ti+=1
        elif s=="K":
            add(K,t,.30,-.04)
        elif s=="t":
            add(T[ti%2],t,.17,.04);ti+=1
        elif s=="k":
            add(K,t,.14,-.04)
        events.append({"bar":bi,"pattern":name,"slot_1based":slot+1,"stroke":s,"time_sec":round(t,6)})

st=np.stack([L,R],1)
fade=int(.25*SR);st[-fade:]*=np.linspace(1,0,fade)[:,None]
st*=10**(-1.5/20)/(np.max(np.abs(st))+1e-12)

sf.write(OUT,st,SR,subtype="PCM_24")
sf.write(DESK,st,SR,subtype="PCM_24")

meta={
 "lesson":"AYYOUB CONTROLLED VARIATION 001",
 "bpm":BPM,
 "meter":"2/4",
 "base":"D - K D | - T - K",
 "variation":"D t K D | k T - K",
 "plan":plan,
 "humanization":"OFF",
 "microtiming":"NONE",
 "goal":"add minimal life without losing Ayyoub pull and anchor identity",
 "articulation_boundary":"K = real Ka-category sample; NOT asserted KAH_LEFT",
 "events":events
}
PROV.write_text(json.dumps(meta,ensure_ascii=False,indent=2),encoding="utf-8")
print("rendered",OUT)
