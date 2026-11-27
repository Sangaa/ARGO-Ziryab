import re, math, json
from pathlib import Path
import numpy as np
import soundfile as sf

SR=44100
score_path=Path(r"%ZIRYAB_STUDIO%\Projects\ZRY-HASHTAKA-CLAUDE-D-REAL-BAND-001\Scripts\score_events.lua")
sfz_path=Path(r"%ZIRYAB_STUDIO%\Instruments\World\FreePats_ButtonAccordionHN\Button Accordion HN SFZ+FLAC-20240329\PRESET Button Accordion HN tuned.sfz")
out=Path(r"%ZIRYAB_STUDIO%\Projects\ZRY-HASHTAKA-CLAUDE-E2-LEAN-ORIENTAL-001\Renders\E2-ACCORDION-FULL.wav")

txt=score_path.read_text(encoding="utf-8")
m=re.search(r'\["Helix_Strings"\]\s*=\s*\{(.*?)\n\s*\},',txt,re.S)
events=[(float(a),float(b),int(n),int(v)) for a,b,n,v in re.findall(r'\{([0-9.]+),([0-9.]+),(\d+),(\d+)\}',m.group(1))]

sfztxt=sfz_path.read_text(encoding="utf-8",errors="replace")
groups=sfztxt.split("<group>")
main=groups[1]
release=groups[2] if len(groups)>2 else ""

def parse_regions(block, release_group=False):
    regs=[]
    for line in block.splitlines():
        if not line.strip().startswith("<region>"): continue
        sm=re.search(r'sample=(.*?)\s+pitch_keycenter=(\d+)\s+lokey=(\d+)\s+hikey=(\d+)\s+tune=([-\d]+)',line)
        if not sm: continue
        reg={
          "sample":sm.group(1).strip(),
          "center":int(sm.group(2)),
          "lo":int(sm.group(3)),
          "hi":int(sm.group(4)),
          "tune":int(sm.group(5)),
        }
        ls=re.search(r'loop_start=(\d+)',line); le=re.search(r'loop_end=(\d+)',line)
        off=re.search(r'offset=(\d+)',line)
        if ls: reg["loop_start"]=int(ls.group(1))
        if le: reg["loop_end"]=int(le.group(1))
        if off: reg["offset"]=int(off.group(1))
        regs.append(reg)
    return regs

main_regs=parse_regions(main)
rel_regs=parse_regions(release,True)
base=sfz_path.parent
cache={}

def load_sample(reg):
    key=reg["sample"]
    if key in cache: return cache[key]
    x,sr=sf.read(base/key,dtype="float64",always_2d=False)
    if x.ndim>1: x=x.mean(axis=1)
    if sr!=SR:
        old=np.arange(len(x))/sr
        new=np.arange(int(round(len(x)*SR/sr)))/SR
        x=np.interp(new,old,x)
    off=reg.get("offset",0)
    if off<len(x): x=x[off:]
    x=x-np.mean(x)
    cache[key]=x
    return x

def pitched(reg,note):
    src=load_sample(reg)
    semis=(note-reg["center"]) - reg["tune"]/100.0
    ratio=2**(semis/12.0)
    idx=np.arange(0,len(src),ratio)
    idx=idx[idx<len(src)-1]
    return np.interp(idx,np.arange(len(src)),src)

N=int(89.0*SR)
mix=np.zeros(N,dtype=np.float64)

for a,b,n,v in events:
    reg=next((r for r in main_regs if r["lo"]<=n<=r["hi"]),None)
    if not reg: continue
    y=pitched(reg,n)
    dur=max(0.06,b-a)
    need=int((dur+0.045)*SR)
    if len(y)<need:
        y=np.pad(y,(0,need-len(y)))
    y=y[:need].copy()
    atk=min(int(0.012*SR),len(y)//5)
    rel=min(int(0.045*SR),len(y)//4)
    if atk>1:y[:atk]*=np.linspace(0,1,atk)
    if rel>1:y[-rel:]*=np.linspace(1,0,rel)
    gain=(v/127.0)**0.72*0.70
    st=int(a*SR)
    en=min(N,st+len(y))
    if en>st: mix[st:en]+=y[:en-st]*gain

    rreg=next((r for r in rel_regs if r["lo"]<=n<=r["hi"]),None)
    if rreg:
        ry=pitched(rreg,n)
        rlen=min(len(ry),int(0.18*SR))
        ry=ry[:rlen].copy()
        if rlen>1: ry*=np.linspace(1,0,rlen)
        rst=int(b*SR)
        ren=min(N,rst+rlen)
        if ren>rst:mix[rst:ren]+=ry[:ren-rst]*gain*0.28

# centered sample, slight right placement in stereo
pk=np.max(np.abs(mix))+1e-12
mix*=10**(-4/20)/pk
L=mix*0.88
R=mix
st=np.stack([L,R],axis=1)
sf.write(out,st,SR,subtype="PCM_24")
meta={
 "source":"FreePats Button Accordion HN SFZ+FLAC",
 "mapping":"original Helix_Strings notes -> accordion, same onset/pitch/duration",
 "notes":len(events),
 "duration_median_sec":float(np.median([b-a for a,b,_,_ in events])),
 "duration_max_sec":float(max(b-a for a,b,_,_ in events)),
 "output":str(out)
}
Path(str(out).replace(".wav",".json")).write_text(json.dumps(meta,ensure_ascii=False,indent=2),encoding="utf-8")
print(json.dumps(meta,ensure_ascii=False,indent=2))
