import os,math,random,json
from pathlib import Path
import numpy as np
import soundfile as sf
SR=44100; BPM=92.0; BEAT=60/BPM; S16=BEAT/4; BAR=4*BEAT; TOTAL=38.0; N=int(TOTAL*SR)
OLD=r"%ZIRYAB_STUDIO%\Samples\CC0_Egyptian_Perc"
NEW=r"%ZIRYAB_SAMPLES%\New folder"
def load(p):
    x,sr=sf.read(p,dtype="float64",always_2d=False)
    if x.ndim>1:x=x.mean(1)
    if sr!=SR:
        old=np.arange(len(x))/sr; new=np.arange(int(round(len(x)*SR/sr)))/SR
        x=np.interp(new,old,x)
    x=x-np.mean(x); return x/(np.max(np.abs(x))+1e-12)
D=load(os.path.join(NEW,"Darbuka_68_76_SP.wav"))
T=[load(os.path.join(OLD,"tak_02_03.flac")),load(os.path.join(OLD,"tak_02_07.flac"))]
K=load(os.path.join(NEW,"413798__pjcohen__doumbek_ka2.wav"))
M=load(os.path.join(NEW,"413782__pjcohen__doumbek_mute2.wav"))
patterns={
"ghost":["D","-","-","-","t","-","-","-","-","-","T","-","k","-","-","k"],
"light":["D","-","T","-","-","k","-","-","D","-","t","-","-","-","T","k"],
"turn":["D","-","-","-","t","k","T","-","-","k","t","-","M","-","T","k"],
"open":["D","-","-","-","-","-","T","-","-","-","-","-","t","-","-","k"],
}
plan={1:None,2:"open",3:"ghost",4:"light",5:"ghost",6:"light",7:"turn",8:"ghost",9:"light",10:"ghost",11:"turn",12:"open",13:"ghost",14:"turn"}
L=np.zeros(N);R=np.zeros(N);ev=[];random.seed(31)
def add(sig,t,g,pan=0):
    i=int(round(t*SR)); m=min(len(sig),N-i)
    if i<0 or m<=0:return
    y=sig[:m]*g
    L[i:i+m]+=y*math.sqrt((1-pan)*.5); R[i:i+m]+=y*math.sqrt((1+pan)*.5)
for bar in range(1,15):
    name=plan[bar]
    if not name:continue
    for slot,s in enumerate(patterns[name]):
        if s=="-":continue
        t=(bar-1)*BAR+slot*S16
        t+=random.uniform(-0.0035,0.0015) if s in ("T","t","k") else random.uniform(-0.001,0.001)
        if s=="D":add(D,t,.50,-.02)
        elif s=="T":add(T[(bar+slot)%2],t,.31,.04)
        elif s=="t":add(T[(bar+slot)%2],t,.16,.04)
        elif s=="k":add(K,t,.12,-.04)
        elif s=="M":add(M,t,.11,0)
        ev.append([bar,slot,s,round(t,6),name])
st=np.stack([L,R],1); st*=10**(-3.5/20)/(np.max(np.abs(st))+1e-12)
out=Path(r"%ZIRYAB_STUDIO%\Projects\ZRY-NIGHT-ORGAN-002\Renders\TABLA_LIGHT_STEM.wav")
sf.write(out,st,SR,subtype="PCM_24")
Path(r"%ZIRYAB_STUDIO%\Projects\ZRY-NIGHT-ORGAN-002\Provenance\tabla_v2.json").write_text(json.dumps({"events":ev,"plan":plan,"note":"soft end-of-bar ghost pickups added to preserve thread"},ensure_ascii=False,indent=2),encoding="utf-8")
print("events",len(ev))
