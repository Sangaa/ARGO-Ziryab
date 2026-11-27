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

OUT=Path(r"%ZIRYAB_STUDIO%\Projects\ZRY-TABLA-SCHOOL-MAQSUM-001\Renders\ZIRYAB-TABLA-SCHOOL-MAQSUM-001.wav")
PROV=Path(r"%ZIRYAB_STUDIO%\Projects\ZRY-TABLA-SCHOOL-MAQSUM-001\Provenance\lesson.json")
DESKTOP=Path(r"%ZIRYAB_SAMPLES%\ZIRYAB-TABLA-SCHOOL-MAQSUM-001.wav")

def load(path):
    x,sr=sf.read(path,dtype="float64",always_2d=False)
    if x.ndim>1:
        x=x.mean(axis=1)
    if sr!=SR:
        old=np.arange(len(x))/sr
        new=np.arange(int(round(len(x)*SR/sr)))/SR
        x=np.interp(new,old,x)
    x=x-np.mean(x)
    pk=np.max(np.abs(x))+1e-12
    return x/pk

D=load(D_PATH)
Ts=[load(p) for p in T_PATHS]
K=load(K_PATH)

# 16th-note grid. User-taught Maqsum skeleton:
# D - T - | K - D - | - - T - | K - T K
BASE=["D","-","T","-","K","-","D","-","-","-","T","-","K","-","T","K"]

# Small controlled variation. All main Maqsum anchors are preserved.
# Lowercase = light supporting stroke, not a new anchor.
VAR=["D","t","T","-","K","-","D","k","t","-","T","-","K","t","T","K"]

plan=["BASE","BASE","BASE","VAR","VAR","BASE","VAR","BASE"]
patterns={"BASE":BASE,"VAR":VAR}

TOTAL=len(plan)*BAR + 0.65
N=int(round(TOTAL*SR))
L=np.zeros(N,dtype=np.float64)
R=np.zeros(N,dtype=np.float64)
events=[]
t_index=0

def add(sig,time,gain,pan=0.0):
    i=int(round(time*SR))
    if i<0 or i>=N:
        return
    m=min(len(sig),N-i)
    if m<=0:
        return
    y=sig[:m]*gain
    lg=math.sqrt((1.0-pan)*0.5)
    rg=math.sqrt((1.0+pan)*0.5)
    L[i:i+m]+=y*lg
    R[i:i+m]+=y*rg

for bar_i,name in enumerate(plan, start=1):
    pat=patterns[name]
    for slot,s in enumerate(pat):
        if s=="-":
            continue
        t=(bar_i-1)*BAR + slot*S16
        if s=="D":
            add(D,t,0.74,-0.01)
            vel=0.74
        elif s=="T":
            sig=Ts[t_index%len(Ts)]; t_index+=1
            add(sig,t,0.46,0.04)
            vel=0.46
        elif s=="K":
            add(K,t,0.34,-0.04)
            vel=0.34
        elif s=="t":
            sig=Ts[t_index%len(Ts)]; t_index+=1
            add(sig,t,0.20,0.04)
            vel=0.20
        elif s=="k":
            add(K,t,0.16,-0.04)
            vel=0.16
        events.append({
            "bar":bar_i,
            "slot_1based":slot+1,
            "stroke":s,
            "time_sec":round(t,6),
            "pattern":name
        })

st=np.stack([L,R],axis=1)
# short natural tail fade
fade=int(0.35*SR)
st[-fade:]*=np.linspace(1,0,fade)[:,None]
pk=np.max(np.abs(st))+1e-12
st*=10**(-1.5/20)/pk

sf.write(OUT,st,SR,subtype="PCM_24")
sf.write(DESKTOP,st,SR,subtype="PCM_24")

meta={
  "lesson":"TABLA FOUNDATION / MAQSUM 001",
  "bpm":BPM,
  "meter":"4/4",
  "grid":"1/16",
  "bars":len(plan),
  "duration_sec":round(len(st)/SR,3),
  "base_pattern":"D - T - | K - D - | - - T - | K - T K",
  "variation_pattern":"D t T - | K - D k | t - T - | K t T K",
  "plan":plan,
  "microtiming":"NONE; grid-exact foundation pass",
  "humanization":"OFF",
  "articulation_boundary":"K = real Ka-category sample; NOT asserted KAH_LEFT",
  "samples":{"D":D_PATH,"T":T_PATHS,"K":K_PATH},
  "event_count":len(events),
  "events":events,
  "goal":"hold Maqsum identity through a small supporting-stroke variation, then return cleanly to base",
  "pass_question":"Does the VAR remain recognizably Maqsum without weakening pulse or anchor identity?"
}
PROV.write_text(json.dumps(meta,ensure_ascii=False,indent=2),encoding="utf-8")
print(json.dumps({k:meta[k] for k in ("lesson","bpm","bars","duration_sec","base_pattern","variation_pattern","plan","event_count")},ensure_ascii=False,indent=2))
print("OUT",OUT)
print("DESKTOP",DESKTOP)
