import os, math, json
from pathlib import Path
import numpy as np
import soundfile as sf

SR=44100
files={
 "tabla": Path(r"%ZIRYAB_STUDIO%\Projects\ZRY-HASHTAKA-CLAUDE-LAB-001\Renders\HASHTAKA-B_REAL_SAMPLES-TABLA-STEM.wav"),
 "oud": Path(r"%ZIRYAB_STUDIO%\Projects\ZRY-HASHTAKA-CLAUDE-E2-LEAN-ORIENTAL-001\Renders\E2-OUD-FULL.wav"),
 "accordion": Path(r"%ZIRYAB_STUDIO%\Projects\ZRY-HASHTAKA-CLAUDE-E2-LEAN-ORIENTAL-001\Renders\E2-ACCORDION-FULL.wav"),
 "bass": Path(r"%ZIRYAB_STUDIO%\Projects\ZRY-HASHTAKA-CLAUDE-E2-LEAN-ORIENTAL-001\Renders\E2-BASS-FULL.wav"),
}
target_active_db={
 "tabla":-17.5,
 "oud":-20.5,
 "accordion":-24.0,
 "bass":-22.0,
}
tracks={}
report={}

def active_rms(x):
    m=x.mean(axis=1)
    frame=2048
    vals=[]
    for i in range(0,len(m)-frame+1,frame):
        r=float(np.sqrt(np.mean(m[i:i+frame]**2)))
        if r>1e-6: vals.append(r)
    if not vals: return 1e-12
    arr=np.array(vals)
    cut=np.percentile(arr,35)
    active=arr[arr>=cut]
    return float(np.sqrt(np.mean(active**2))) if len(active) else float(np.sqrt(np.mean(arr**2)))

maxN=0
for name,p in files.items():
    x,sr=sf.read(p,dtype="float64",always_2d=True)
    if sr!=SR: raise RuntimeError(f"{name} sr {sr}")
    if x.shape[1]==1:x=np.repeat(x,2,axis=1)
    tracks[name]=x[:,:2]
    maxN=max(maxN,len(x))

for name,x in list(tracks.items()):
    if len(x)<maxN:
        x=np.pad(x,((0,maxN-len(x)),(0,0)))
        tracks[name]=x
    ar=active_rms(x)
    target=10**(target_active_db[name]/20)
    g=target/(ar+1e-30)
    tracks[name]=x*g
    report[name]={
      "source":str(files[name]),
      "active_rms_in_db":20*math.log10(ar+1e-30),
      "target_active_db":target_active_db[name],
      "gain_db":20*math.log10(g+1e-30),
    }

# Tiny stereo positioning. Keep bass + tabla centered.
tracks["oud"][:,0]*=1.04
tracks["oud"][:,1]*=0.92
tracks["accordion"][:,0]*=0.90
tracks["accordion"][:,1]*=1.04

mix=tracks["tabla"]+tracks["oud"]+tracks["accordion"]+tracks["bass"]

# very gentle fade out only, no compression/limiting
fade=int(0.55*SR)
if fade<len(mix):
    mix[-fade:]*=np.linspace(1,0,fade)[:,None]

pk=float(np.max(np.abs(mix))+1e-30)
master_target=10**(-1.2/20)
mg=master_target/pk
mix*=mg
mono=mix.mean(axis=1)
out=Path(r"%ZIRYAB_SAMPLES%\HASHTAKA_ABC_LAB\HASHTAKA-E2-LEAN-ORIENTAL_OUD-ACC-TABLA-BASS-v1.wav")
sf.write(out,mix,SR,subtype="PCM_24")
report["master"]={
 "gain_db":20*math.log10(mg),
 "peak_dbfs":20*math.log10(float(np.max(np.abs(mix)))+1e-30),
 "rms_dbfs":20*math.log10(float(np.sqrt(np.mean(mono**2)))+1e-30),
 "instruments":["Tabla B","Turkish Oud","Hohner Accordion","Crux JBass"],
 "muted":["Flute","Violin/Strings","Piano"],
 "score_boundary":"No melody pitch/onset changes on oud or bass. Accordion uses original Helix_Strings harmony with original onset/pitch/duration. Known tabla duplicate-hit defect remains preserved.",
 "output":str(out)
}
Path(r"%ZIRYAB_STUDIO%\Projects\ZRY-HASHTAKA-CLAUDE-E2-LEAN-ORIENTAL-001\Provenance\E2_MIX_REPORT.json").write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding="utf-8")
print(json.dumps(report,ensure_ascii=False,indent=2))
