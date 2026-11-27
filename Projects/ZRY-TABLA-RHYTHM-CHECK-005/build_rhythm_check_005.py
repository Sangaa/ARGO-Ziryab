import os, math, json
import numpy as np
import soundfile as sf

SR=44100
BPM=96
BEAT=60.0/BPM
EIGHTH=BEAT/2.0

OLD=r"%ZIRYAB_STUDIO%\Samples\CC0_Egyptian_Perc"
NEW=r"%ZIRYAB_SAMPLES%\New folder"
OUT=r"%ZIRYAB_STUDIO%\Projects\ZRY-TABLA-RHYTHM-CHECK-005"
LISTEN=r"%ZIRYAB_SAMPLES%"
os.makedirs(LISTEN,exist_ok=True)

def load(path):
    x,sr=sf.read(path,dtype="float32",always_2d=False)
    if x.ndim>1:x=x.mean(axis=1)
    x=x.astype(np.float64)
    if sr!=SR:
        old=np.arange(len(x))/sr
        new=np.arange(int(round(len(x)*SR/sr)))/SR
        x=np.interp(new,old,x)
    return x

def trim(x,secs):
    y=x[:min(len(x),int(secs*SR))].copy()
    f=min(len(y),int(.05*SR))
    if f>1:y[-f:]*=np.linspace(1,0,f)
    return y

D=trim(load(os.path.join(NEW,"Darbuka_68_76_SP.wav")),.58)
T1=trim(load(os.path.join(OLD,"tak_02_03.flac")),.18)
T2=trim(load(os.path.join(OLD,"tak_02_07.flac")),.18)

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
    if sym=="D":
        if rhythm=="MAQSUM":
            g=.72 if slot==0 else .66
        elif rhythm=="BALADI":
            g=.82 if slot in (0,1) else .74
        else:
            g=.79 if slot in (3,4) else .72
        add(D,t,g,-.02)
    elif sym=="T":
        if rhythm=="MAQSUM": g=.48
        elif rhythm=="BALADI": g=.44
        else: g=.52
        s=T1 if (bar+slot)%2==0 else T2
        add(s,t,g,.03)

cursor=lead
timeline=[]
for rhythm,pat in patterns:
    st=cursor
    for b in range(bars):
        for s,sym in enumerate(pat):
            if sym!="-": hit(rhythm,sym,cursor+s*EIGHTH,s,b)
        cursor+=8*EIGHTH
    timeline.append({"rhythm":rhythm,"start":round(st,3),"end":round(cursor,3),"pattern":" ".join(pat)})
    cursor+=gap

mix=np.stack([L,R],1)
pk=float(np.max(np.abs(mix))) or 1.0
mix*=10**(-8/20)/pk

name="ZIRYAB-RHYTHM-CHECK-005-NEW-DUM-THREE-RHYTHMS.wav"
wav=os.path.join(OUT,name)
listen=os.path.join(LISTEN,name)
sf.write(wav,mix,SR,subtype="PCM_24")
sf.write(listen,mix,SR,subtype="PCM_24")

with open(os.path.join(OUT,"RHYTHM-CHECK-005.json"),"w",encoding="utf-8") as f:
    json.dump({
      "bpm":BPM,
      "dum_source":"Darbuka_68_76_SP.wav",
      "tak_sources":["tak_02_03.flac","tak_02_07.flac"],
      "patterns":timeline,
      "kah":0,"ghosts":0,"rolls":0,"humanization_ms":0
    },f,ensure_ascii=False,indent=2)

print(listen)
