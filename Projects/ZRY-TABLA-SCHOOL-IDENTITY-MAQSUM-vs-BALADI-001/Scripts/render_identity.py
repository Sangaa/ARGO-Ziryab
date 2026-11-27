import os, json, math
from pathlib import Path
import numpy as np
import soundfile as sf

SR=44100
BPM=82.0
BEAT=60.0/BPM
S8=BEAT/2.0
BAR=4*BEAT

D_PATH=r"%ZIRYAB_SAMPLES%\New folder\Darbuka_68_76_SP.wav"
T_PATHS=[
 r"%ZIRYAB_STUDIO%\Samples\CC0_Egyptian_Perc\tak_02_03.flac",
 r"%ZIRYAB_STUDIO%\Samples\CC0_Egyptian_Perc\tak_02_07.flac",
]
OUT=Path(r"%ZIRYAB_STUDIO%\Projects\ZRY-TABLA-SCHOOL-IDENTITY-MAQSUM-vs-BALADI-001\Renders\ZIRYAB-MAQSUM-vs-BALADI-IDENTITY-001.wav")
DESK=Path(r"%ZIRYAB_SAMPLES%\ZIRYAB-MAQSUM-vs-BALADI-IDENTITY-001.wav")
PROV=Path(r"%ZIRYAB_STUDIO%\Projects\ZRY-TABLA-SCHOOL-IDENTITY-MAQSUM-vs-BALADI-001\Provenance\identity_test.json")

def load(p):
    x,sr=sf.read(p,dtype="float64",always_2d=False)
    if x.ndim>1: x=x.mean(1)
    if sr!=SR:
        old=np.arange(len(x))/sr
        new=np.arange(int(round(len(x)*SR/sr)))/SR
        x=np.interp(new,old,x)
    x=x-np.mean(x)
    return x/(np.max(np.abs(x))+1e-12)

D=load(D_PATH)
T=[load(p) for p in T_PATHS]

# 8th-note teaching skeletons, deliberately stripped down for identity contrast.
MAQ=["D","T","-","T","D","-","T","-"]
BAL=["D","D","-","T","D","-","T","-"]

sequence=[("MAQSUM",MAQ),("MAQSUM",MAQ),("BALADI",BAL),("BALADI",BAL),
          ("MAQSUM",MAQ),("BALADI",BAL)]

TOTAL=len(sequence)*BAR+0.5
N=int(TOTAL*SR)
L=np.zeros(N);R=np.zeros(N);events=[];ti=0

def add(sig,t,g,pan):
    i=int(round(t*SR))
    if i<0 or i>=N:return
    m=min(len(sig),N-i)
    if m<=0:return
    y=sig[:m]*g
    L[i:i+m]+=y*math.sqrt((1-pan)*0.5)
    R[i:i+m]+=y*math.sqrt((1+pan)*0.5)

for bi,(name,pat) in enumerate(sequence,1):
    for slot,s in enumerate(pat):
        if s=="-":continue
        t=(bi-1)*BAR+slot*S8
        if s=="D":
            # Baladi opening DUM pair intentionally weighted: first anchor, second supporting-heavy.
            if name=="BALADI" and slot==1:
                g=0.52
            else:
                g=0.58
            add(D,t,g,-0.01)
        elif s=="T":
            add(T[ti%2],t,0.42,0.04);ti+=1
        events.append({"bar":bi,"rhythm":name,"slot_1based":slot+1,"stroke":s,"time_sec":round(t,6)})

st=np.stack([L,R],1)
fade=int(.3*SR); st[-fade:]*=np.linspace(1,0,fade)[:,None]
st*=10**(-1.5/20)/(np.max(np.abs(st))+1e-12)
sf.write(OUT,st,SR,subtype="PCM_24")
sf.write(DESK,st,SR,subtype="PCM_24")

meta={
 "lesson":"RHYTHM IDENTITY CONTRAST 001",
 "bpm":BPM,
 "grid":"1/8 teaching skeleton",
 "maqsum":"D T - T | D - T -",
 "baladi":"D D - T | D - T -",
 "sequence":[x[0] for x in sequence],
 "variation":"OFF",
 "humanization":"OFF",
 "goal":"make opening-weight identity audible before reintroducing denser 16th-grid detail",
 "events":events
}
PROV.write_text(json.dumps(meta,ensure_ascii=False,indent=2),encoding="utf-8")
print(json.dumps(meta,ensure_ascii=False,indent=2))
