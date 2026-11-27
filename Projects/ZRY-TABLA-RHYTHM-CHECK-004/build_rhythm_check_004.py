import os, math, json
import numpy as np
import soundfile as sf

SR=48000
BPM=96
BEAT=60.0/BPM
EIGHTH=BEAT/2.0
SAMPLES=r"%ZIRYAB_STUDIO%\Samples\CC0_Egyptian_Perc"
OUT=r"%ZIRYAB_STUDIO%\Projects\ZRY-TABLA-RHYTHM-CHECK-004"
LISTEN=r"%ZIRYAB_SAMPLES%"
os.makedirs(LISTEN,exist_ok=True)

def load(name):
    x,sr=sf.read(os.path.join(SAMPLES,name),dtype="float32",always_2d=False)
    if x.ndim>1:x=x.mean(axis=1)
    return x.astype(np.float64)

def trim(x,secs):
    y=x[:min(len(x),int(secs*SR))].copy()
    f=min(len(y),int(.045*SR))
    if f>1:y[-f:]*=np.linspace(1,0,f)
    return y

D1=trim(load("doom_01_04.flac"),.42)
D2=trim(load("doom_01_07.flac"),.42)
T1=trim(load("tak_02_03.flac"),.18)
T2=trim(load("tak_02_07.flac"),.18)

patterns=[
 ("MAQSUM", ["D","T","-","T","D","-","T","-"]),
 ("BALADI", ["D","D","-","T","D","-","T","-"]),
 ("SAIDI",  ["D","T","-","D","D","-","T","-"]),
]

bars=6
gap=BEAT*2
lead=.4
dur=lead+sum(bars*8*EIGHTH+gap for _ in patterns)+.8
N=int(dur*SR)
L=np.zeros(N);R=np.zeros(N)

def add(s,t,g,pan):
    i=int(round(t*SR));m=min(len(s),N-i)
    if m<=0:return
    y=s[:m]*g
    lg=math.sqrt((1-pan)*.5);rg=math.sqrt((1+pan)*.5)
    L[i:i+m]+=y*lg;R[i:i+m]+=y*rg

def hit(rhythm,sym,t,slot,bar):
    # Character by dynamics/take only, no extra notes.
    if sym=="D":
        if rhythm=="MAQSUM":
            g=.80 if slot==0 else .74
        elif rhythm=="BALADI":
            g=.92 if slot in (0,1) else .84
        else: # SAIDI
            g=.88 if slot in (3,4) else .82
        s=D1 if (bar+slot)%2==0 else D2
        add(s,t,g,-.025)
    elif sym=="T":
        if rhythm=="MAQSUM":
            g=.48
        elif rhythm=="BALADI":
            g=.44
        else:
            g=.52
        s=T1 if (bar+slot)%2==0 else T2
        add(s,t,g,.03)

cursor=lead
timeline=[]
for rhythm,pat in patterns:
    st=cursor
    for b in range(bars):
        for s,sym in enumerate(pat):
            if sym!="-": hit(rhythm,sym,cursor+s*EIGHTH,s,b)
        cursor += 8*EIGHTH
    timeline.append({"rhythm":rhythm,"start":round(st,3),"end":round(cursor,3),"pattern":" ".join(pat)})
    cursor += gap

mix=np.stack([L,R],1)
pk=float(np.max(np.abs(mix))) or 1.0
mix*=10**(-8/20)/pk

name="ZIRYAB-RHYTHM-CHECK-004-CHARACTER-BY-DYNAMICS.wav"
wav=os.path.join(OUT,name)
listen=os.path.join(LISTEN,name)
sf.write(wav,mix,SR,subtype="PCM_24")
sf.write(listen,mix,SR,subtype="PCM_24")
with open(os.path.join(OUT,"RHYTHM-CHECK-004.json"),"w",encoding="utf-8") as f:
    json.dump({"bpm":BPM,"bars_each":bars,"patterns":timeline,
               "new_hits_added":0,"kah":0,"ghosts":0,"rolls":0,"humanization_ms":0,
               "character_controls":["dynamic accents","alternate real takes"]},f,ensure_ascii=False,indent=2)
print(json.dumps(timeline,ensure_ascii=False,indent=2))
print(listen)
