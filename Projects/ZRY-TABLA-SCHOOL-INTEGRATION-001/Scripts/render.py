import os, json, math
from pathlib import Path
import numpy as np
import soundfile as sf

SR=44100
BPM=92.0
BEAT=60.0/BPM
S16=BEAT/4.0

D_PATH=r"%ZIRYAB_SAMPLES%\New folder\Darbuka_68_76_SP.wav"
T_PATHS=[
 r"%ZIRYAB_STUDIO%\Samples\CC0_Egyptian_Perc\tak_02_03.flac",
 r"%ZIRYAB_STUDIO%\Samples\CC0_Egyptian_Perc\tak_02_07.flac",
]
K_PATH=r"%ZIRYAB_SAMPLES%\New folder\413798__pjcohen__doumbek_ka2.wav"
M_PATH=r"%ZIRYAB_SAMPLES%\New folder\413782__pjcohen__doumbek_mute2.wav"

OUT=Path(r"%ZIRYAB_STUDIO%\Projects\ZRY-TABLA-SCHOOL-INTEGRATION-001\Renders\ZIRYAB-TABLA-FOUNDATION-INTEGRATION-001.wav")
DESK=Path(r"%ZIRYAB_SAMPLES%\ZIRYAB-TABLA-FOUNDATION-INTEGRATION-001.wav")
PROV=Path(r"%ZIRYAB_STUDIO%\Projects\ZRY-TABLA-SCHOOL-INTEGRATION-001\Provenance\integration.json")

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
M=load(M_PATH)

# All patterns represented on 1/16 pulse.
PAT={
 "MAQSUM":   (16, ["D","-","T","-","K","-","D","-","-","-","T","-","K","-","T","K"]),
 "BALADI":   (16, ["D","-","D","-","-","-","T","-","D","-","-","-","T","-","-","-"]),
 "SAIDI":    (16, ["D","-","T","-","-","-","D","-","D","-","-","-","T","-","-","-"]),
 "MALFOUF":  (8,  ["D","-","-","T","-","-","T","-"]),
 "AYYOUB":   (8,  ["D","-","K","D","-","T","-","K"]),
}

# Two bars each. Short transition fill replaces only the tail of the last source bar.
sequence=["MAQSUM","BALADI","SAIDI","MALFOUF","AYYOUB"]

events=[]
cursor=0.0
L=np.zeros(int(40*SR))
R=np.zeros_like(L)
ti=0

def add(sig,t,g,pan=0):
    i=int(round(t*SR))
    if i<0 or i>=len(L):return
    m=min(len(sig),len(L)-i)
    if m<=0:return
    y=sig[:m]*g
    L[i:i+m]+=y*math.sqrt((1-pan)*.5)
    R[i:i+m]+=y*math.sqrt((1+pan)*.5)

def play_symbol(sym,t):
    global ti
    if sym=="D": add(D,t,.56,-.01)
    elif sym=="T": add(T[ti%2],t,.42,.04); ti+=1
    elif sym=="K": add(K,t,.30,-.04)
    elif sym=="t": add(T[ti%2],t,.18,.04); ti+=1
    elif sym=="k": add(K,t,.14,-.04)
    elif sym=="M": add(M,t,.12,0)

for idx,name in enumerate(sequence):
    slots,pat=PAT[name]
    bar_dur=slots*S16
    for b in range(2):
        bar_start=cursor+b*bar_dur
        # last source bar before a transition gets a small tail fill
        last_before_transition=(b==1 and idx < len(sequence)-1)
        for slot,sym in enumerate(pat):
            # reserve last 4 slots for transition fill only
            if last_before_transition and slot>=slots-4:
                continue
            if sym=="-": continue
            t=bar_start+slot*S16
            play_symbol(sym,t)
            events.append({"section":name,"bar_in_section":b+1,"kind":"BASE","slot":slot+1,"stroke":sym,"time":round(t,6)})
        if last_before_transition:
            # compact promise: light-light-T-mute; next rhythm answers with its own first D
            fill=["t","k","T","M"]
            for j,sym in enumerate(fill):
                slot=slots-4+j
                t=bar_start+slot*S16
                play_symbol(sym,t)
                events.append({"section":name,"bar_in_section":b+1,"kind":"TRANSITION","slot":slot+1,"stroke":sym,"time":round(t,6),"to":sequence[idx+1]})
    cursor += 2*bar_dur

N=int((cursor+0.45)*SR)
st=np.stack([L[:N],R[:N]],1)
fade=int(.25*SR); st[-fade:]*=np.linspace(1,0,fade)[:,None]
st*=10**(-1.5/20)/(np.max(np.abs(st))+1e-12)

sf.write(OUT,st,SR,subtype="PCM_24")
sf.write(DESK,st,SR,subtype="PCM_24")

meta={
 "lesson":"TABLA FOUNDATION INTEGRATION 001",
 "bpm":BPM,
 "sequence":sequence,
 "bars_per_rhythm":2,
 "humanization":"OFF",
 "microtiming":"NONE",
 "transition_rule":"last 4 x 1/16 slots = t k T M; next rhythm answers immediately on D",
 "goal":"preserve rhythm identity across continuous transitions without dead silence",
 "duration_sec":round(len(st)/SR,3),
 "events":events
}
PROV.write_text(json.dumps(meta,ensure_ascii=False,indent=2),encoding="utf-8")
print(json.dumps({k:meta[k] for k in ("lesson","bpm","sequence","bars_per_rhythm","transition_rule","goal","duration_sec")},ensure_ascii=False,indent=2))
