import os, math, json, random
from pathlib import Path
import numpy as np
import soundfile as sf

SR=44100
BPM=92.0
BEAT=60/BPM
S16=BEAT/4
BAR=4*BEAT
TOTAL=38.0
N=int(TOTAL*SR)

OLD=r"%ZIRYAB_STUDIO%\Samples\CC0_Egyptian_Perc"
NEW=r"%ZIRYAB_SAMPLES%\New folder"
OUT=Path(r"%ZIRYAB_STUDIO%\Projects\ZRY-NIGHT-ORGAN-001\Renders\TABLA_LIGHT_STEM.wav")
PROV=Path(r"%ZIRYAB_STUDIO%\Projects\ZRY-NIGHT-ORGAN-001\Provenance\tabla_light.json")

def load(path):
    x,sr=sf.read(path,dtype="float64",always_2d=False)
    if x.ndim>1:x=x.mean(axis=1)
    if sr!=SR:
        old=np.arange(len(x))/sr
        new=np.arange(int(round(len(x)*SR/sr)))/SR
        x=np.interp(new,old,x)
    x=x-np.mean(x)
    p=np.max(np.abs(x)) or 1.0
    return x/p

D=load(os.path.join(NEW,"Darbuka_68_76_SP.wav"))
T=[load(os.path.join(OLD,"tak_02_03.flac")),load(os.path.join(OLD,"tak_02_07.flac"))]
K=load(os.path.join(NEW,"413798__pjcohen__doumbek_ka2.wav"))
M=load(os.path.join(NEW,"413782__pjcohen__doumbek_mute2.wav"))

patterns={
"ghost":["D","-","-","-","t","-","-","-","-","-","T","-","k","-","-","-"],
"light":["D","-","T","-","-","k","-","-","D","-","t","-","-","-","T","-"],
"turn":["D","-","-","-","t","k","T","-","-","k","t","-","M","-","T","-"],
"open":["D","-","-","-","-","-","T","-","-","-","-","-","t","-","-","-"],
}
plan={1:None,2:"open",3:"ghost",4:"light",5:"ghost",6:"light",7:"turn",8:"ghost",9:"light",10:"ghost",11:"turn",12:"open",13:"ghost",14:"turn"}

L=np.zeros(N);R=np.zeros(N); events=[]
random.seed(27)

def add(sig,t,g,pan=0):
    i=int(round(t*SR))
    if i<0:return
    m=min(len(sig),N-i)
    if m<=0:return
    y=sig[:m]*g
    L[i:i+m]+=y*math.sqrt((1-pan)*0.5)
    R[i:i+m]+=y*math.sqrt((1+pan)*0.5)

for bar in range(1,15):
    name=plan[bar]
    if not name:continue
    pat=patterns[name]
    for slot,s in enumerate(pat):
        if s=="-":continue
        t=(bar-1)*BAR+slot*S16
        if s in ("T","t","k"): t += random.uniform(-0.004,0.002)
        else:t += random.uniform(-0.0015,0.0015)
        if s=="D":add(D,t,0.54,-0.02)
        elif s=="T":add(T[(bar+slot)%2],t,0.34,0.04)
        elif s=="t":add(T[(bar+slot)%2],t,0.18,0.04)
        elif s=="k":add(K,t,0.15,-0.05)
        elif s=="M":add(M,t,0.13,0.0)
        events.append({"bar":bar,"slot":slot,"stroke":s,"pattern":name,"time":round(t,6)})

st=np.stack([L,R],1)
pk=np.max(np.abs(st)) or 1
st*=10**(-3/20)/pk
sf.write(OUT,st,SR,subtype="PCM_24")
PROV.write_text(json.dumps({"bpm":BPM,"events":events,"patterns":patterns,"plan":plan},ensure_ascii=False,indent=2),encoding="utf-8")
print("events",len(events),"out",OUT)
