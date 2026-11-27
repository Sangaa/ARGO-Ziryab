import os, json, math
from pathlib import Path
import numpy as np
import soundfile as sf

SR=44100
BPM=100.0
BEAT=60/BPM
S8=BEAT/2
BAR=4*BEAT

D_PATH=r"%ZIRYAB_SAMPLES%\New folder\Darbuka_68_76_SP.wav"
T_PATHS=[
 r"%ZIRYAB_STUDIO%\Samples\CC0_Egyptian_Perc\tak_02_03.flac",
 r"%ZIRYAB_STUDIO%\Samples\CC0_Egyptian_Perc\tak_02_07.flac",
]
OUT=Path(r"%ZIRYAB_STUDIO%\Projects\ZRY-TABLA-SCHOOL-BALADI-IDENTITY-002\Renders\ZIRYAB-BALADI-IDENTITY-002-100BPM.wav")
DESK=Path(r"%ZIRYAB_SAMPLES%\ZIRYAB-BALADI-IDENTITY-002-100BPM.wav")
PROV=Path(r"%ZIRYAB_STUDIO%\Projects\ZRY-TABLA-SCHOOL-BALADI-IDENTITY-002\Provenance\lesson.json")

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

BAL=["D","D","-","T","D","-","T","-"]
bars=6
TOTAL=bars*BAR+0.45
N=int(TOTAL*SR)
L=np.zeros(N);R=np.zeros(N);events=[];ti=0

def add(sig,t,g,pan=0):
    i=int(round(t*SR))
    if i<0 or i>=N:return
    m=min(len(sig),N-i)
    if m<=0:return
    y=sig[:m]*g
    L[i:i+m]+=y*math.sqrt((1-pan)*.5)
    R[i:i+m]+=y*math.sqrt((1+pan)*.5)

for bi in range(1,bars+1):
    for slot,s in enumerate(BAL):
        if s=="-":continue
        t=(bi-1)*BAR+slot*S8
        if s=="D":
            g=0.50 if slot==1 else 0.58
            add(D,t,g,-.01)
        else:
            add(T[ti%2],t,.42,.04);ti+=1
        events.append({"bar":bi,"slot_1based":slot+1,"stroke":s,"time_sec":round(t,6)})

st=np.stack([L,R],1)
fade=int(.3*SR);st[-fade:]*=np.linspace(1,0,fade)[:,None]
st*=10**(-1.5/20)/(np.max(np.abs(st))+1e-12)
sf.write(OUT,st,SR,subtype="PCM_24")
sf.write(DESK,st,SR,subtype="PCM_24")
PROV.write_text(json.dumps({
 "lesson":"BALADI IDENTITY / TEMPO TRANSFER 002",
 "bpm":BPM,
 "pattern":"D D - T | D - T -",
 "bars":bars,
 "variation":"OFF",
 "humanization":"OFF",
 "goal":"preserve the simplified Baladi identity at higher tempo before reintroducing detail",
 "events":events
},ensure_ascii=False,indent=2),encoding="utf-8")
print(OUT)
