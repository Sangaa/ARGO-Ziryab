import os, math, json
import numpy as np
import soundfile as sf

SR=48000
BPM=94
BEAT=60.0/BPM
EIGHTH=BEAT/2.0
SAMPLES=r"%ZIRYAB_STUDIO%\Samples\CC0_Egyptian_Perc"
OUT=r"%ZIRYAB_STUDIO%\Projects\ZRY-TABLA-RHYTHM-CHECK-003"
LISTEN=r"%ZIRYAB_SAMPLES%"
os.makedirs(LISTEN,exist_ok=True)

def load(name):
    x,sr=sf.read(os.path.join(SAMPLES,name),dtype="float32",always_2d=False)
    if x.ndim>1:x=x.mean(axis=1)
    if sr!=SR:
        old=np.arange(len(x),dtype=np.float64)/sr
        new=np.arange(int(round(len(x)*SR/sr)),dtype=np.float64)/SR
        x=np.interp(new,old,x).astype(np.float32)
    return x.astype(np.float64)

def trim(x,secs):
    y=x[:min(len(x),int(secs*SR))].copy()
    f=min(len(y),int(.045*SR))
    if f>1:y[-f:]*=np.linspace(1,0,f)
    return y

D=trim(load("doom_01_04.flac"),.42)
T=trim(load("tak_02_03.flac"),.18)

# 8 eighth-note slots per 4/4 bar.
# Variations are intentionally conservative: preserve each rhythm's defining DUM placement.
sets = [
  ("MAQSUM", [
      ("BASE", ["D","T","-","T","D","-","T","-"]),
      ("VAR_A",["D","T","T","-","D","-","T","-"]),
      ("VAR_B",["D","-","T","T","D","-","T","-"]),
  ]),
  ("BALADI", [
      ("BASE", ["D","D","-","T","D","-","T","-"]),
      ("VAR_A",["D","D","T","-","D","-","T","-"]),
      ("VAR_B",["D","D","-","T","D","T","-","-"]),
  ]),
  ("SAIDI", [
      ("BASE", ["D","T","-","D","D","-","T","-"]),
      ("VAR_A",["D","T","T","D","D","-","T","-"]),
      ("VAR_B",["D","-","T","D","D","T","-","-"]),
  ]),
]

reps_each=2
gap=BEAT*1.5
section_gap=BEAT*2.0
lead=.4

dur=lead
for _,vars_ in sets:
    for _vname,_pat in vars_:
        dur += reps_each*8*EIGHTH + gap
    dur += section_gap
dur += .8

N=int(dur*SR)
L=np.zeros(N);R=np.zeros(N)

def add(s,t,g,pan):
    i=int(round(t*SR));m=min(len(s),N-i)
    if m<=0:return
    y=s[:m]*g
    lg=math.sqrt((1-pan)*.5);rg=math.sqrt((1+pan)*.5)
    L[i:i+m]+=y*lg;R[i:i+m]+=y*rg

def hit(sym,t,accent=1.0):
    if sym=="D":add(D,t,.88*accent,-.02)
    elif sym=="T":add(T,t,.50*accent,.03)

timeline=[]
cursor=lead
for rhythm, vars_ in sets:
    rstart=cursor
    for vname,pat in vars_:
        vstart=cursor
        for _ in range(reps_each):
            for s,sym in enumerate(pat):
                if sym!="-":
                    # only slight beat accents, no humanization.
                    beat_accent=1.04 if s in (0,4) and sym=="D" else 1.0
                    hit(sym,cursor+s*EIGHTH,beat_accent)
            cursor += 8*EIGHTH
        timeline.append({
          "rhythm":rhythm,"variation":vname,
          "start":round(vstart,3),"end":round(cursor,3),
          "pattern":" ".join(pat)
        })
        cursor += gap
    timeline.append({"rhythm":rhythm,"section_end":round(cursor,3)})
    cursor += section_gap

mix=np.stack([L,R],1)
pk=float(np.max(np.abs(mix))) or 1.0
mix*=10**(-8/20)/pk

name="ZIRYAB-RHYTHM-CHECK-003-BASE-PLUS-VARIATIONS.wav"
wav=os.path.join(OUT,name)
listen=os.path.join(LISTEN,name)
sf.write(wav,mix,SR,subtype="PCM_24")
sf.write(listen,mix,SR,subtype="PCM_24")

report={
 "purpose":"Check whether rhythm identity survives two conservative plain variations",
 "bpm":BPM,
 "grid":"8 eighth-note slots per 4/4 bar",
 "repetitions_per_pattern":reps_each,
 "kah":0,"ghosts":0,"rolls":0,"humanization_ms":0,
 "timeline":timeline
}
with open(os.path.join(OUT,"RHYTHM-CHECK-003.json"),"w",encoding="utf-8") as f:
    json.dump(report,f,ensure_ascii=False,indent=2)

print(json.dumps(report,ensure_ascii=False,indent=2))
print("WAV",wav)
print("LISTEN",listen)
