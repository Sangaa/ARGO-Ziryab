import os, math, json
import numpy as np
import soundfile as sf

SR=44100
OLD=r"%ZIRYAB_STUDIO%\Samples\CC0_Egyptian_Perc"
NEW=r"%ZIRYAB_SAMPLES%\New folder"
LISTEN=r"%ZIRYAB_SAMPLES%"
OUT=r"%ZIRYAB_STUDIO%\Projects\ZRY-TABLA-NEW-SAMPLE-CHECK-001"
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

def peaknorm(x,target_db=-8):
    p=np.max(np.abs(x)) or 1.0
    return x*(10**(target_db/20)/p)

new_files=[
 ("SLAP_REAL", "413781__pjcohen__doumbek_slap1.wav"),
 ("MUTE_REAL", "413782__pjcohen__doumbek_mute2.wav"),
 ("KA_REAL_DOMINANT_HAND", "413798__pjcohen__doumbek_ka2.wav"),
 ("DUM_LIKE_NOIIZ", "Darbuka_68_76_SP.wav"),
]
samples={k:peaknorm(load(os.path.join(NEW,f)),-7) for k,f in new_files}
oldD=peaknorm(load(os.path.join(OLD,"doom_01_04.flac")),-8)
oldT=peaknorm(load(os.path.join(OLD,"tak_02_03.flac")),-10)
newD=samples["DUM_LIKE_NOIIZ"]

def render_events(events,duration):
    y=np.zeros(int(duration*SR))
    for t,s,g in events:
        i=int(t*SR); m=min(len(s),len(y)-i)
        if m>0:y[i:i+m]+=s[:m]*g
    p=np.max(np.abs(y)) or 1.0
    if p>0.92:y*=0.92/p
    return y

# 1) Isolated audition: 3 hits each, 0.75s apart, 1.2s between classes
events=[]; t=.4
timeline=[]
for name,_ in new_files:
    st=t
    s=samples[name]
    for _ in range(3):
        events.append((t,s,1.0)); t+=.75
    timeline.append((name,st,t))
    t+=1.2
aud=render_events(events,t+.5)
aud_path=os.path.join(LISTEN,"ZIRYAB-NEW-4-SAMPLES-ISOLATED.wav")
sf.write(aud_path,aud,SR,subtype="PCM_24")

# 2) Same Maqsum skeleton old DUM vs new DUM, T fixed
BPM=92
eighth=(60/BPM)/2
pat=["D","T","-","T","D","-","T","-"]
events=[]; t=.4
sections=[]
for label,D in [("OLD_DUM",oldD),("NEW_DUM_CANDIDATE",newD)]:
    st=t
    for bar in range(4):
        for i,sym in enumerate(pat):
            tt=t+i*eighth
            if sym=="D":events.append((tt,D,.92))
            elif sym=="T":events.append((tt,oldT,.62))
        t+=8*eighth
    sections.append((label,st,t))
    t+=1.5
ab=render_events(events,t+.4)
ab_path=os.path.join(LISTEN,"ZIRYAB-MAQSUM-OLD-vs-NEW-DUM.wav")
sf.write(ab_path,ab,SR,subtype="PCM_24")

report={
 "isolated_file":aud_path,
 "ab_file":ab_path,
 "isolated_order":[x[0] for x in new_files],
 "ab_order":["OLD_DUM","NEW_DUM_CANDIDATE"],
 "fixed_tak":"doom comparison uses tak_02_03.flac unchanged",
 "note":"KA is not claimed KAH_LEFT; SLAP is not claimed SAK; MUTE is not yet promoted to DUM_CLOSED."
}
with open(os.path.join(OUT,"NEW_SAMPLE_CHECK_001.json"),"w",encoding="utf-8") as f:
    json.dump(report,f,ensure_ascii=False,indent=2)
print(json.dumps(report,ensure_ascii=False,indent=2))
