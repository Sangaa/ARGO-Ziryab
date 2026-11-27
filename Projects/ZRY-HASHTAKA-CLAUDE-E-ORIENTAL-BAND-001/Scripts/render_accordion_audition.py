import os,re,math,json
from pathlib import Path
import numpy as np
import soundfile as sf

SR=44100
startT=7.55
endT=15.45
score_path=Path(r"%ZIRYAB_STUDIO%\Projects\ZRY-HASHTAKA-CLAUDE-D-REAL-BAND-001\Scripts\score_events.lua")
sfz_path=Path(r"%ZIRYAB_STUDIO%\Instruments\World\FreePats_ButtonAccordionHN\Button Accordion HN SFZ+FLAC-20240329\PRESET Button Accordion HN tuned.sfz")
out=Path(r"%ZIRYAB_STUDIO%\Projects\ZRY-HASHTAKA-CLAUDE-E-ORIENTAL-BAND-001\Auditions\02_ACCORDION_HOHNER_HASHTAKA_PHRASE.wav")

txt=score_path.read_text(encoding="utf-8")
m=re.search(r'\["Strand_Nylon"\]\s*=\s*\{(.*?)\n\s*\},',txt,re.S)
events=[]
for a,b,n,v in re.findall(r'\{([0-9.]+),([0-9.]+),(\d+),(\d+)\}',m.group(1)):
    a=float(a); b=float(b); n=int(n); v=int(v)
    if startT<=a<endT: events.append((a,b,n,v))

sfztxt=sfz_path.read_text(encoding="utf-8",errors="replace")
# first group only, before release group
main=sfztxt.split("<group>",2)[1]
regions=[]
for line in main.splitlines():
    if line.strip().startswith("<region>"):
        sm=re.search(r'sample=(.*?)\s+pitch_keycenter=(\d+)\s+lokey=(\d+)\s+hikey=(\d+)\s+tune=([-\d]+)',line)
        if sm:
            regions.append({
                "sample":sm.group(1).strip(),
                "center":int(sm.group(2)),
                "lo":int(sm.group(3)),
                "hi":int(sm.group(4)),
                "tune":int(sm.group(5))
            })
base=sfz_path.parent

def load_region(reg):
    x,sr=sf.read(base/reg["sample"],dtype="float64",always_2d=False)
    if x.ndim>1: x=x.mean(axis=1)
    if sr!=SR:
        old=np.arange(len(x))/sr
        new=np.arange(int(round(len(x)*SR/sr)))/SR
        x=np.interp(new,old,x)
    p=np.max(np.abs(x)) if len(x) else 1
    return x/(p+1e-12)

cache={}
dur=(endT-startT)+1.0
mix=np.zeros(int(dur*SR),dtype=np.float64)

for a,b,n,v in events:
    reg=next((r for r in regions if r["lo"]<=n<=r["hi"]),None)
    if reg is None: continue
    key=(reg["sample"],n)
    if reg["sample"] not in cache: cache[reg["sample"]]=load_region(reg)
    src=cache[reg["sample"]]
    # source's tuning offset is cents relative to nominal keycenter; compensate in playback ratio
    semis=(n-reg["center"]) - reg["tune"]/100.0
    ratio=2**(semis/12.0)
    # pitch shift by resampling playback speed
    idx=np.arange(0,len(src),ratio)
    idx=idx[idx<len(src)-1]
    y=np.interp(idx,np.arange(len(src)),src)
    note_dur=max(0.07,b-a)
    need=int((note_dur+0.12)*SR)
    if len(y)<need:
        # repeat a stable middle chunk very gently if needed; usually samples are long enough
        y=np.pad(y,(0,need-len(y)),mode="edge")
    y=y[:need].copy()
    # short natural envelope
    attack=min(int(0.012*SR),len(y)//4)
    release=min(int(0.09*SR),len(y)//3)
    if attack>1: y[:attack]*=np.linspace(0,1,attack)
    if release>1: y[-release:]*=np.linspace(1,0,release)
    gain=(v/127.0)**0.75*0.72
    st=int(((a-startT)+0.25)*SR)
    en=min(len(mix),st+len(y))
    if en>st: mix[st:en]+=y[:en-st]*gain

pk=np.max(np.abs(mix)) if len(mix) else 1
mix*=10**(-1.5/20)/(pk+1e-12)
stereo=np.stack([mix,mix],axis=1)
sf.write(out,stereo,SR,subtype="PCM_24")
meta={
 "instrument":"FreePats Button Accordion HN",
 "source":"real Hohner accordion recordings",
 "notes":len(events),
 "phrase_source":"same HASHTAKA Strand_Nylon phrase as oud audition",
 "start_source_sec":startT,
 "end_source_sec":endT,
 "output":str(out)
}
Path(str(out).replace(".wav",".json")).write_text(json.dumps(meta,ensure_ascii=False,indent=2),encoding="utf-8")
print(json.dumps(meta,ensure_ascii=False,indent=2))
