import os, math, json
import numpy as np
import soundfile as sf

SR=44100
BPM=110
BEAT=60.0/BPM
S16=BEAT/4.0

OLD=r"%ZIRYAB_STUDIO%\Samples\CC0_Egyptian_Perc"
NEW=r"%ZIRYAB_SAMPLES%\New folder"
OUT=r"%ZIRYAB_STUDIO%\Projects\ZRY-TABLA-IMITATION-001"
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

def trim(x,secs,fade=.04):
    y=x[:min(len(x),int(secs*SR))].copy()
    f=min(len(y),int(fade*SR))
    if f>1:y[-f:]*=np.linspace(1,0,f)
    return y

D=trim(load(os.path.join(NEW,"Darbuka_68_76_SP.wav")),.55)
T1=trim(load(os.path.join(OLD,"tak_02_03.flac")),.17)
T2=trim(load(os.path.join(OLD,"tak_02_07.flac")),.17)
K=trim(load(os.path.join(NEW,"413798__pjcohen__doumbek_ka2.wav")),.22)

# PlayDarbuka Maqsum "Classic" lead-darbuka line:
# D · T · t k T · D · t k T · t k
pattern=["D","-","T","-","t","k","T","-","D","-","t","k","T","-","t","k"]

bars=6
lead=.45
tail=.7
bar_dur=16*S16
N=int((lead+bars*bar_dur+tail)*SR)
L=np.zeros(N);R=np.zeros(N)

def add(s,t,g,pan=0):
    i=int(round(t*SR));m=min(len(s),N-i)
    if m<=0:return
    y=s[:m]*g
    lg=math.sqrt((1-pan)*.5);rg=math.sqrt((1+pan)*.5)
    L[i:i+m]+=y*lg;R[i:i+m]+=y*rg

for b in range(bars):
    base=lead+b*bar_dur
    for i,sym in enumerate(pattern):
        t=base+i*S16
        if sym=="D":
            add(D,t,.70,-.02)
        elif sym=="T":
            add(T1 if (b+i)%2==0 else T2,t,.48,.03)
        elif sym=="t":
            add(T1 if (b+i)%2==0 else T2,t,.27,.03)
        elif sym=="k":
            add(K,t,.24,-.03)

mix=np.stack([L,R],1)
pk=float(np.max(np.abs(mix))) or 1
mix*=10**(-8/20)/pk

name="ZIRYAB-IMITATION-001-MAQSUM-CLASSIC.wav"
listen=os.path.join(LISTEN,name)
project=os.path.join(OUT,name)
sf.write(listen,mix,SR,subtype="PCM_24")
sf.write(project,mix,SR,subtype="PCM_24")

report={
 "exercise":"Imitation 001",
 "source_model":"PlayDarbuka Maqsum Classic lead darbuka line",
 "source_pattern":"D - T - t k T - D - t k T - t k",
 "bpm":BPM,
 "bars":bars,
 "grid":"1/16",
 "rule":"copy only; no added notes, rolls, mute, slap, or humanization",
 "articulation_notes":{
   "D":"Darbuka_68_76_SP.wav",
   "T/t":"tak_02_03 + tak_02_07; lowercase = lower velocity only",
   "k":"verified KA-category sample; not relabeled KAH_LEFT"
 }
}
with open(os.path.join(OUT,"IMITATION-001.json"),"w",encoding="utf-8") as f:
    json.dump(report,f,ensure_ascii=False,indent=2)
print(listen)
