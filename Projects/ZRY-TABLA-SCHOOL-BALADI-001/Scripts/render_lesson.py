import os, json, math
from pathlib import Path
import numpy as np
import soundfile as sf

SR=44100
BPM=82.0
BEAT=60.0/BPM
S16=BEAT/4.0
BAR=4.0*BEAT

D_PATH=r"%ZIRYAB_SAMPLES%\New folder\Darbuka_68_76_SP.wav"
T_PATHS=[
 r"%ZIRYAB_STUDIO%\Samples\CC0_Egyptian_Perc\tak_02_03.flac",
 r"%ZIRYAB_STUDIO%\Samples\CC0_Egyptian_Perc\tak_02_07.flac",
]
K_PATH=r"%ZIRYAB_SAMPLES%\New folder\413798__pjcohen__doumbek_ka2.wav"

OUT=Path(r"%ZIRYAB_STUDIO%\Projects\ZRY-TABLA-SCHOOL-BALADI-001\Renders\ZIRYAB-TABLA-SCHOOL-BALADI-001.wav")
PROV=Path(r"%ZIRYAB_STUDIO%\Projects\ZRY-TABLA-SCHOOL-BALADI-001\Provenance\lesson.json")
DESKTOP=Path(r"%ZIRYAB_SAMPLES%\ZIRYAB-TABLA-SCHOOL-BALADI-001.wav")

def load(path):
    x,sr=sf.read(path,dtype="float64",always_2d=False)
    if x.ndim>1: x=x.mean(axis=1)
    if sr!=SR:
        old=np.arange(len(x))/sr
        new=np.arange(int(round(len(x)*SR/sr)))/SR
        x=np.interp(new,old,x)
    x=x-np.mean(x)
    return x/(np.max(np.abs(x))+1e-12)

D=load(D_PATH)
Ts=[load(p) for p in T_PATHS]
K=load(K_PATH)

# Baladi skeleton from the training sheet:
# D - D - | K - D - | - - T - | K - T K
BASE=["D","-","D","-","K","-","D","-","-","-","T","-","K","-","T","K"]
# preserve the Baladi anchors; add only light support.
VAR=["D","t","D","-","K","-","D","k","t","-","T","-","K","t","T","K"]

plan=["BASE","BASE","BASE","VAR","VAR","BASE","VAR","BASE"]
patterns={"BASE":BASE,"VAR":VAR}

TOTAL=len(plan)*BAR+0.65
N=int(round(TOTAL*SR))
L=np.zeros(N);R=np.zeros(N);events=[];ti=0

def add(sig,t,g,pan=0):
    i=int(round(t*SR))
    if i<0 or i>=N:return
    m=min(len(sig),N-i)
    if m<=0:return
    y=sig[:m]*g
    L[i:i+m]+=y*math.sqrt((1-pan)*0.5)
    R[i:i+m]+=y*math.sqrt((1+pan)*0.5)

for bar_i,name in enumerate(plan,1):
    for slot,s in enumerate(patterns[name]):
        if s=="-": continue
        t=(bar_i-1)*BAR+slot*S16
        if s=="D": add(D,t,0.58,-0.01)
        elif s=="T":
            add(Ts[ti%2],t,0.46,0.04); ti+=1
        elif s=="K": add(K,t,0.34,-0.04)
        elif s=="t":
            add(Ts[ti%2],t,0.20,0.04); ti+=1
        elif s=="k": add(K,t,0.16,-0.04)
        events.append({"bar":bar_i,"slot_1based":slot+1,"stroke":s,"time_sec":round(t,6),"pattern":name})

st=np.stack([L,R],1)
fade=int(0.35*SR); st[-fade:]*=np.linspace(1,0,fade)[:,None]
st*=10**(-1.5/20)/(np.max(np.abs(st))+1e-12)
sf.write(OUT,st,SR,subtype="PCM_24")
sf.write(DESKTOP,st,SR,subtype="PCM_24")

meta={
 "lesson":"TABLA FOUNDATION / BALADI 001",
 "bpm":BPM,"meter":"4/4","grid":"1/16","bars":len(plan),
 "duration_sec":round(len(st)/SR,3),
 "base_pattern":"D - D - | K - D - | - - T - | K - T K",
 "variation_pattern":"D t D - | K - D k | t - T - | K t T K",
 "plan":plan,
 "microtiming":"NONE; grid-exact foundation pass",
 "humanization":"OFF",
 "articulation_boundary":"K = real Ka-category sample; NOT asserted KAH_LEFT",
 "samples":{"D":D_PATH,"T":T_PATHS,"K":K_PATH},
 "event_count":len(events),"events":events,
 "goal":"preserve Baladi identity through a small supporting-stroke variation"
}
PROV.write_text(json.dumps(meta,ensure_ascii=False,indent=2),encoding="utf-8")
print(json.dumps({k:meta[k] for k in ("lesson","bpm","base_pattern","variation_pattern","event_count")},ensure_ascii=False,indent=2))
