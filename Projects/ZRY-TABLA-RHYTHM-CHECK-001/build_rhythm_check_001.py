import os, math, json
import numpy as np
import soundfile as sf

SR=48000
BPM=90
Q=60.0/BPM
SIXTEENTH=Q/4.0
SAMPLES=r"%ZIRYAB_STUDIO%\Samples\CC0_Egyptian_Perc"
OUT=r"%ZIRYAB_STUDIO%\Projects\ZRY-TABLA-RHYTHM-CHECK-001"

def load(name):
    x,sr=sf.read(os.path.join(SAMPLES,name),dtype="float32",always_2d=False)
    if x.ndim>1: x=x.mean(axis=1)
    if sr!=SR:
        old=np.arange(len(x),dtype=np.float64)/sr
        new=np.arange(int(round(len(x)*SR/sr)),dtype=np.float64)/SR
        x=np.interp(new,old,x).astype(np.float32)
    return x.astype(np.float64)

def trim(x,secs):
    y=x[:min(len(x),int(secs*SR))].copy()
    f=min(len(y),int(.045*SR))
    if f>1: y[-f:]*=np.linspace(1,0,f)
    return y

D=trim(load("doom_01_04.flac"),.42)
T=trim(load("tak_02_03.flac"),.18)
K=trim(load("tak_02_05.flac"),.18)  # KAH proxy: distinct edge-stroke take

# Standardized skeletons supplied in the teaching session.
patterns = [
    ("MALFUF_2_4", 8,  ["D","-","-","T","-","-","T","-"]),
    ("AYOUB_2_4",  8,  ["D","-","K","D","-","T","-","K"]),
    ("MAQSUM_4_4", 16, ["D","-","T","-","K","-","D","-","-","-","T","-","K","-","T","K"]),
    ("BALADI_4_4", 16, ["D","-","D","-","K","-","D","-","-","-","T","-","K","-","T","K"]),
    ("SAIDI_4_4",  16, ["D","-","T","-","K","-","D","-","D","-","T","-","K","-","T","K"]),
]

bars_each=3
gap=Q*2.0  # explicit separation for listening test, not musical transition
lead=0.5

dur=lead
for _,slots,_ in patterns:
    dur += bars_each*slots*SIXTEENTH + gap
dur += .8
N=int(dur*SR)
L=np.zeros(N,dtype=np.float64); R=np.zeros(N,dtype=np.float64)

def add(sample,t,g,pan):
    i=int(round(t*SR)); m=min(len(sample),N-i)
    if m<=0:return
    y=sample[:m]*g
    lg=math.sqrt((1-pan)*.5); rg=math.sqrt((1+pan)*.5)
    L[i:i+m]+=y*lg; R[i:i+m]+=y*rg

def hit(sym,t):
    if sym=="D": add(D,t,.86,-.02)
    elif sym=="T": add(T,t,.48,.035)
    elif sym=="K": add(K,t,.46,-.035)

timeline=[]
cursor=lead
for name,slots,pat in patterns:
    section_start=cursor
    for b in range(bars_each):
        for s,sym in enumerate(pat):
            if sym!="-":
                hit(sym,cursor+s*SIXTEENTH)
        cursor += slots*SIXTEENTH
    section_end=cursor
    timeline.append({
        "name":name,
        "start_sec":round(section_start,3),
        "end_sec":round(section_end,3),
        "bars":bars_each,
        "pattern":" ".join(pat)
    })
    cursor += gap

mix=np.stack([L,R],axis=1)
pk=float(np.max(np.abs(mix))) or 1.0
mix*=10**(-8/20)/pk

name="ZIRYAB-RHYTHM-CHECK-001-PLAIN.wav"
wav=os.path.join(OUT,name)
desk=os.path.join(os.path.expanduser("~"),"Desktop",name)
sf.write(wav,mix,SR,subtype="PCM_24")
sf.write(desk,mix,SR,subtype="PCM_24")

report={
    "purpose":"Plain rhythm skeleton listening check before ornaments",
    "bpm":BPM,
    "grid":"1/16",
    "bars_each":bars_each,
    "gap_between_sections_sec":gap,
    "articulations":{
        "D":"doom_01_04.flac",
        "T":"tak_02_03.flac",
        "K":"tak_02_05.flac (KAH proxy only; no authentic KAH sample in current library)"
    },
    "ornaments":0,
    "rolls":0,
    "ghosts":0,
    "humanization_ms":0,
    "timeline":timeline
}
with open(os.path.join(OUT,"RHYTHM-CHECK-001.json"),"w",encoding="utf-8") as f:
    json.dump(report,f,ensure_ascii=False,indent=2)

print(json.dumps(report,ensure_ascii=False,indent=2))
print("WAV",wav)
print("DESKTOP",desk)
