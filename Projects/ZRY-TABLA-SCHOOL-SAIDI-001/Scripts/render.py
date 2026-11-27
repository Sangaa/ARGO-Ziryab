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

OUT=Path(r"%ZIRYAB_STUDIO%\Projects\ZRY-TABLA-SCHOOL-SAIDI-001\Renders\ZIRYAB-TABLA-SCHOOL-SAIDI-001-82BPM.wav")
DESK=Path(r"%ZIRYAB_SAMPLES%\ZIRYAB-TABLA-SCHOOL-SAIDI-001-82BPM.wav")
PROV=Path(r"%ZIRYAB_STUDIO%\Projects\ZRY-TABLA-SCHOOL-SAIDI-001\Provenance\lesson.json")

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

# Saidi training skeleton supplied in the learning notes:
# D - T - | K - D - | D - T - | K - T K
BASE=["D","-","T","-","K","-","D","-","D","-","T","-","K","-","T","K"]

bars=6
N=int((bars*BAR+0.5)*SR)
L=np.zeros(N);R=np.zeros(N);events=[];ti=0

def add(sig,t,g,pan=0):
    i=int(round(t*SR))
    if i<0 or i>=N:return
    m=min(len(sig),N-i)
    if m<=0:return
    y=sig[:m]*g
    L[i:i+m]+=y*math.sqrt((1-pan)*0.5)
    R[i:i+m]+=y*math.sqrt((1+pan)*0.5)

for bi in range(1,bars+1):
    for slot,s in enumerate(BASE):
        if s=="-":continue
        t=(bi-1)*BAR+slot*S16
        if s=="D":
            # balanced DUM, same family as passed Maqsum/Baladi
            add(D,t,0.58,-0.01)
        elif s=="T":
            add(T[ti%2],t,0.42,0.04);ti+=1
        elif s=="K":
            add(K,t,0.30,-0.04)
        events.append({"bar":bi,"slot_1based":slot+1,"stroke":s,"time_sec":round(t,6)})

st=np.stack([L,R],1)
fade=int(.3*SR); st[-fade:]*=np.linspace(1,0,fade)[:,None]
st*=10**(-1.5/20)/(np.max(np.abs(st))+1e-12)

sf.write(OUT,st,SR,subtype="PCM_24")
sf.write(DESK,st,SR,subtype="PCM_24")

meta={
 "lesson":"TABLA FOUNDATION / SAIDI 001",
 "bpm":BPM,
 "meter":"4/4",
 "grid":"1/16",
 "bars":bars,
 "base_pattern":"D - T - | K - D - | D - T - | K - T K",
 "variation":"OFF",
 "humanization":"OFF",
 "microtiming":"NONE",
 "goal":"make Saidi identity audible before any variation",
 "articulation_boundary":"K = real Ka-category sample; NOT asserted KAH_LEFT",
 "events":events
}
PROV.write_text(json.dumps(meta,ensure_ascii=False,indent=2),encoding="utf-8")
print(json.dumps({k:meta[k] for k in ("lesson","bpm","bars","base_pattern","goal")},ensure_ascii=False,indent=2))
