import os, math, json
import numpy as np
import soundfile as sf

SR=44100
BPM=96
BEAT=60.0/BPM
S16=BEAT/4.0

OLD=r"%ZIRYAB_STUDIO%\Samples\CC0_Egyptian_Perc"
NEW=r"%ZIRYAB_SAMPLES%\New folder"
OUT=r"%ZIRYAB_STUDIO%\Projects\ZRY-TABLA-PERFORMANCE-002"
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

def trim(x,secs,fade=.05):
    y=x[:min(len(x),int(secs*SR))].copy()
    f=min(len(y),int(fade*SR))
    if f>1:y[-f:]*=np.linspace(1,0,f)
    return y

D   = trim(load(os.path.join(NEW,"Darbuka_68_76_SP.wav")),.60)
KA  = trim(load(os.path.join(NEW,"413798__pjcohen__doumbek_ka2.wav")),.30)
MUT = trim(load(os.path.join(NEW,"413782__pjcohen__doumbek_mute2.wav")),.22)
SLP = trim(load(os.path.join(NEW,"413781__pjcohen__doumbek_slap1.wav")),.19)
T1  = trim(load(os.path.join(OLD,"tak_02_03.flac")),.18)
T2  = trim(load(os.path.join(OLD,"tak_02_07.flac")),.18)

# 16 slots = 4/4.
# Clear phrase architecture. Break is two full bars, not a quick fill.
A = ["D","-","T","-","-","-","T","-","D","-","T","-","-","-","T","-"]
B = ["D","-","T","K","-","-","T","-","D","-","T","-","K","-","T","-"]

# Break bar 1: opens space but keeps pulse.
BREAK1 = ["D","-","-","-","M","-","T","-","D","-","-","K","-","-","T","-"]
# Break bar 2: answer + preparation to return, still no roll.
BREAK2 = ["D","-","T","-","K","-","M","-","D","-","T","K","S","-","T","-"]

# Return phrase slightly simplified first, then full A.
RETURN1 = ["D","-","T","-","-","-","T","-","D","-","T","-","-","-","-","-"]
RETURN2 = A

structure=[
 ("A1",A),("A2",A),
 ("B1",B),("B2",B),
 ("BREAK_1",BREAK1),("BREAK_2",BREAK2),
 ("RETURN_1",RETURN1),("RETURN_2",RETURN2),
 ("A_FINAL",A),("A_FINAL_REPEAT",A)
]

bar_dur=16*S16
lead=.5
tail=.8
N=int((lead+len(structure)*bar_dur+tail)*SR)
L=np.zeros(N);R=np.zeros(N)

def add(sample,t,g,pan=0.0):
    i=int(round(t*SR));m=min(len(sample),N-i)
    if m<=0:return
    y=sample[:m]*g
    lg=math.sqrt((1-pan)*.5);rg=math.sqrt((1+pan)*.5)
    L[i:i+m]+=y*lg;R[i:i+m]+=y*rg

def stroke(sym,t,slot,bar_no,tag):
    # restrained dynamic contour, no timing humanization
    if sym=="D":
        g=.72
        if slot in (0,8): g*=1.05
        if "BREAK" in tag: g*=.95
        add(D,t,g,-.02)
    elif sym=="T":
        g=.47
        if "RETURN" in tag: g*=.95
        add(T1 if (bar_no+slot)%2==0 else T2,t,g,.03)
    elif sym=="K":
        add(KA,t,.30,-.03)
    elif sym=="M":
        add(MUT,t,.24,0.0)
    elif sym=="S":
        add(SLP,t,.22,.01)

cursor=lead
timeline=[]
for bar_no,(tag,pat) in enumerate(structure):
    st=cursor
    for s,sym in enumerate(pat):
        if sym!="-":
            stroke(sym,cursor+s*S16,s,bar_no,tag)
    cursor+=bar_dur
    timeline.append({"part":tag,"start":round(st,3),"end":round(cursor,3),"pattern":" ".join(pat)})

mix=np.stack([L,R],1)
pk=float(np.max(np.abs(mix))) or 1.0
mix*=10**(-8/20)/pk

name="ZIRYAB-MAQSUM-PHRASES-BREAK-RETURN-001.wav"
listen=os.path.join(LISTEN,name)
project=os.path.join(OUT,name)
sf.write(listen,mix,SR,subtype="PCM_24")
sf.write(project,mix,SR,subtype="PCM_24")

report={
 "bpm":BPM,
 "rhythm":"Maqsum",
 "architecture":"A x2 -> B x2 -> 2-bar break -> return x2 -> A x2",
 "break_duration_bars":2,
 "humanization_ms":0,
 "rolls":0,
 "timeline":timeline,
 "claims":["KA stays KA","MUTE stays MUTE","SLAP stays SLAP"]
}
with open(os.path.join(OUT,"PERFORMANCE-002.json"),"w",encoding="utf-8") as f:
    json.dump(report,f,ensure_ascii=False,indent=2)

print(listen)
