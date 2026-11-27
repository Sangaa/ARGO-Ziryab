import os, json, math
from pathlib import Path
import numpy as np
import soundfile as sf

SR=44100
BPM=82.0
BEAT=60/BPM
S8=BEAT/2
BAR=4*BEAT

D_PATH=r"%ZIRYAB_SAMPLES%\New folder\Darbuka_68_76_SP.wav"
T_PATHS=[
 r"%ZIRYAB_STUDIO%\Samples\CC0_Egyptian_Perc\tak_02_03.flac",
 r"%ZIRYAB_STUDIO%\Samples\CC0_Egyptian_Perc\tak_02_07.flac",
]
OUT=Path(r"%ZIRYAB_STUDIO%\Projects\ZRY-TABLA-SCHOOL-IDENTITY-3WAY-001\Renders\ZIRYAB-MAQSUM-BALADI-SAIDI-IDENTITY-001.wav")
DESK=Path(r"%ZIRYAB_SAMPLES%\ZIRYAB-MAQSUM-BALADI-SAIDI-IDENTITY-001.wav")
PROV=Path(r"%ZIRYAB_STUDIO%\Projects\ZRY-TABLA-SCHOOL-IDENTITY-3WAY-001\Provenance\identity_test.json")

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

PAT={
 "MAQSUM":["D","T","-","T","D","-","T","-"],
 "BALADI":["D","D","-","T","D","-","T","-"],
 "SAIDI":["D","T","-","D","D","-","T","-"],
}
sequence=["MAQSUM","MAQSUM","BALADI","BALADI","SAIDI","SAIDI",
          "MAQSUM","BALADI","SAIDI"]

TOTAL=len(sequence)*BAR+0.5
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

for bi,name in enumerate(sequence,1):
    for slot,s in enumerate(PAT[name]):
        if s=="-":continue
        t=(bi-1)*BAR+slot*S8
        if s=="D":
            # emphasize each rhythm's defining DUM relationship without changing timing
            if name=="BALADI" and slot==1:
                g=.50
            elif name=="SAIDI" and slot in (3,4):
                g=.55 if slot==3 else .58
            else:
                g=.58
            add(D,t,g,-.01)
        else:
            add(T[ti%2],t,.42,.04);ti+=1
        events.append({"bar":bi,"rhythm":name,"slot_1based":slot+1,"stroke":s,"time_sec":round(t,6)})

st=np.stack([L,R],1)
fade=int(.3*SR);st[-fade:]*=np.linspace(1,0,fade)[:,None]
st*=10**(-1.5/20)/(np.max(np.abs(st))+1e-12)
sf.write(OUT,st,SR,subtype="PCM_24")
sf.write(DESK,st,SR,subtype="PCM_24")

meta={
 "lesson":"THREE-WAY RHYTHM IDENTITY CONTRAST 001",
 "bpm":BPM,
 "grid":"1/8 teaching skeleton",
 "patterns":{
  "maqsum":"D T - T | D - T -",
  "baladi":"D D - T | D - T -",
  "saidi":"D T - D | D - T -"
 },
 "sequence":sequence,
 "variation":"OFF",
 "humanization":"OFF",
 "goal":"isolate defining DUM placement before reintroducing ornamentation",
 "events":events
}
PROV.write_text(json.dumps(meta,ensure_ascii=False,indent=2),encoding="utf-8")
print(json.dumps(meta,ensure_ascii=False,indent=2))
