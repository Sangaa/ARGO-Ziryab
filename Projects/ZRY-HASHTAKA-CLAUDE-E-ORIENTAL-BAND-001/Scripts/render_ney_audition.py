import os,re,math,json
from pathlib import Path
import numpy as np
import soundfile as sf

SR=44100
startT=7.55
endT=15.45
score_path=Path(r"%ZIRYAB_STUDIO%\Projects\ZRY-HASHTAKA-CLAUDE-D-REAL-BAND-001\Scripts\score_events.lua")
src_path=Path(r"%ZIRYAB_STUDIO%\Instruments\World\Ney_CC0\Ankara-110-Amin-Ney_CC0_preview.mp3")
out=Path(r"%ZIRYAB_STUDIO%\Projects\ZRY-HASHTAKA-CLAUDE-E-ORIENTAL-BAND-001\Auditions\04_NEY_CC0_DERIVED_HASHTAKA_PHRASE.wav")

txt=score_path.read_text(encoding="utf-8")
m=re.search(r'\["Strand_Nylon"\]\s*=\s*\{(.*?)\n\s*\},',txt,re.S)
events=[]
for a,b,n,v in re.findall(r'\{([0-9.]+),([0-9.]+),(\d+),(\d+)\}',m.group(1)):
    a=float(a); b=float(b); n=int(n); v=int(v)
    if startT<=a<endT: events.append((a,b,n,v))

x,sr=sf.read(src_path,dtype="float64",always_2d=True)
x=x.mean(axis=1)
if sr!=SR:
    old=np.arange(len(x))/sr
    new=np.arange(int(round(len(x)*SR/sr)))/SR
    x=np.interp(new,old,x)

# Stable note regions detected from the real CC0 ney preview.
# midi_ref is the measured median, not a guessed equal-tempered label.
sources=[
    {"start":12.562,"end":13.746,"midi_ref":70.716},
    {"start":9.056,"end":9.613,"midi_ref":71.912},
    {"start":3.855,"end":4.876,"midi_ref":75.775},
]
for s in sources:
    y=x[int(s["start"]*SR):int(s["end"]*SR)].copy()
    y-=np.mean(y)
    # remove noisy edges
    edge=min(int(0.025*SR),len(y)//10)
    if edge>1:
        y[:edge]*=np.linspace(0,1,edge)
        y[-edge:]*=np.linspace(1,0,edge)
    p=np.max(np.abs(y))+1e-12
    s["audio"]=y/p

dur=(endT-startT)+1.0
mix=np.zeros(int(dur*SR),dtype=np.float64)

def shift_audio(src, semis):
    ratio=2**(semis/12.0)
    idx=np.arange(0,len(src),ratio)
    idx=idx[idx<len(src)-1]
    return np.interp(idx,np.arange(len(src)),src)

for a,b,n,v in events:
    s=min(sources,key=lambda z:abs(n-z["midi_ref"]))
    semis=n-s["midi_ref"]
    y=shift_audio(s["audio"],semis)
    note_dur=max(0.08,b-a)
    need=int((note_dur+0.11)*SR)
    if len(y)<need:
        # loop a stable center slice rather than pad with a constant
        mid0=int(len(y)*0.35); mid1=int(len(y)*0.72)
        chunk=y[mid0:mid1] if mid1>mid0+20 else y
        buf=[y]
        total=len(y)
        while total<need:
            buf.append(chunk)
            total+=len(chunk)
        y=np.concatenate(buf)
    y=y[:need].copy()
    atk=min(int(0.018*SR),len(y)//5)
    rel=min(int(0.075*SR),len(y)//3)
    if atk>1: y[:atk]*=np.linspace(0,1,atk)
    if rel>1: y[-rel:]*=np.linspace(1,0,rel)
    gain=(v/127.0)**0.8*0.55
    st=int(((a-startT)+0.25)*SR)
    en=min(len(mix),st+len(y))
    if en>st: mix[st:en]+=y[:en-st]*gain

# gentle HPF by first-order difference blend is avoided; preserve timbre.
pk=np.max(np.abs(mix))+1e-12
mix*=10**(-2/20)/pk
# slight stereo air without fake chorus: 7 ms delayed copy at low level
delay=int(0.007*SR)
L=mix.copy()
R=mix.copy()
if delay>0:
    R[delay:]=0.88*mix[delay:]+0.12*mix[:-delay]
stereo=np.stack([L,R],axis=1)
sf.write(out,stereo,SR,subtype="PCM_24")
meta={
 "instrument":"Ney audition derived from real CC0 Ney recording",
 "source_page":"Freesound 580759 Ankara-110-Amin - Ney.wav by aliaref",
 "license":"CC0",
 "source_material":"HQ preview MP3 only; not production master",
 "notes":len(events),
 "phrase_source":"same HASHTAKA Strand_Nylon phrase as oud/accordion/violin auditions",
 "audition_only":True,
 "source_regions":[{k:v for k,v in s.items() if k!="audio"} for s in sources],
 "output":str(out)
}
Path(str(out).replace(".wav",".json")).write_text(json.dumps(meta,ensure_ascii=False,indent=2),encoding="utf-8")
print(json.dumps(meta,ensure_ascii=False,indent=2))
