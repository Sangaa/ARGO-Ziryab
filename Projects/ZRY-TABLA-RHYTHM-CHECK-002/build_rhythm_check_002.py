import os, math, json
import numpy as np
import soundfile as sf

SR=48000
BPM=92
BEAT=60.0/BPM
EIGHTH=BEAT/2.0
SAMPLES=r"%ZIRYAB_STUDIO%\Samples\CC0_Egyptian_Perc"
OUT=r"%ZIRYAB_STUDIO%\Projects\ZRY-TABLA-RHYTHM-CHECK-002"

def load(name):
    x,sr=sf.read(os.path.join(SAMPLES,name),dtype="float32",always_2d=False)
    if x.ndim>1:x=x.mean(axis=1)
    return x.astype(np.float64)

def trim(x,secs):
    y=x[:min(len(x),int(secs*SR))].copy()
    f=min(len(y),int(.045*SR))
    if f>1:y[-f:]*=np.linspace(1,0,f)
    return y

D=trim(load("doom_01_04.flac"),.42)
T=trim(load("tak_02_03.flac"),.18)

patterns=[
 ("MAQSUM",["D","T","-","T","D","-","T","-"]),
 ("BALADI",["D","D","-","T","D","-","T","-"]),
 ("SAIDI", ["D","T","-","D","D","-","T","-"]),
]

bars_each=4
gap=BEAT*2
lead=.4
dur=lead+sum(bars_each*8*EIGHTH+gap for _ in patterns)+.6
N=int(dur*SR)
L=np.zeros(N);R=np.zeros(N)

def add(s,t,g,pan):
    i=int(round(t*SR));m=min(len(s),N-i)
    if m<=0:return
    y=s[:m]*g
    lg=math.sqrt((1-pan)*.5);rg=math.sqrt((1+pan)*.5)
    L[i:i+m]+=y*lg;R[i:i+m]+=y*rg

def hit(sym,t):
    if sym=="D":add(D,t,.88,-.02)
    elif sym=="T":add(T,t,.50,.03)

cursor=lead
timeline=[]
for name,pat in patterns:
    st=cursor
    for _ in range(bars_each):
        for s,sym in enumerate(pat):
            if sym!="-":hit(sym,cursor+s*EIGHTH)
        cursor+=8*EIGHTH
    timeline.append({"name":name,"start":round(st,3),"end":round(cursor,3),"pattern":" ".join(pat)})
    cursor+=gap

mix=np.stack([L,R],1)
pk=np.max(np.abs(mix)) or 1
mix*=10**(-8/20)/pk

name="ZIRYAB-RHYTHM-CHECK-002-THREE-SKELETONS.wav"
wav=os.path.join(OUT,name)
desk=os.path.join(os.path.expanduser("~"),"Desktop",name)
sf.write(wav,mix,SR,subtype="PCM_24")
sf.write(desk,mix,SR,subtype="PCM_24")
with open(os.path.join(OUT,"RHYTHM-CHECK-002.json"),"w",encoding="utf-8") as f:
    json.dump({"bpm":BPM,"grid":"8 eighth-note slots per 4/4 bar","bars_each":bars_each,"patterns":timeline,
               "ornaments":0,"kah":0,"rolls":0,"ghosts":0,"humanization_ms":0},f,ensure_ascii=False,indent=2)
print(json.dumps(timeline,ensure_ascii=False,indent=2))
print(wav)
print(desk)
