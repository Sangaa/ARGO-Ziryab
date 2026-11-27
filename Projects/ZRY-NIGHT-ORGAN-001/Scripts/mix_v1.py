import math,json
from pathlib import Path
import numpy as np
import soundfile as sf

SR=44100
srcs={
 "organ":Path(r"%ZIRYAB_STUDIO%\Projects\ZRY-NIGHT-ORGAN-001\Renders\ORGAN_STEM.wav"),
 "trumpet":Path(r"%ZIRYAB_STUDIO%\Projects\ZRY-NIGHT-ORGAN-001\Renders\MUTED_TRUMPET_STEM.wav"),
 "bass":Path(r"%ZIRYAB_STUDIO%\Projects\ZRY-NIGHT-ORGAN-001\Renders\JAZZ_BASS_STEM.wav"),
 "tabla":Path(r"%ZIRYAB_STUDIO%\Projects\ZRY-NIGHT-ORGAN-001\Renders\TABLA_LIGHT_STEM.wav"),
}
targets={"organ":-20.5,"trumpet":-19.5,"bass":-23.5,"tabla":-24.0}

def active_rms(x):
    m=x.mean(axis=1)
    vals=[]; frame=2048
    for i in range(0,len(m)-frame+1,frame):
        r=float(np.sqrt(np.mean(m[i:i+frame]**2)))
        if r>1e-7: vals.append(r)
    if not vals:return 1e-12
    a=np.array(vals)
    cut=np.percentile(a,35)
    a=a[a>=cut]
    return float(np.sqrt(np.mean(a*a))) if len(a) else 1e-12

tracks={};N=0;rep={}
for name,p in srcs.items():
    x,sr=sf.read(p,dtype="float64",always_2d=True)
    if sr!=SR:raise RuntimeError((name,sr))
    if x.shape[1]==1:x=np.repeat(x,2,axis=1)
    tracks[name]=x[:,:2];N=max(N,len(x))
for name,x in list(tracks.items()):
    if len(x)<N:x=np.pad(x,((0,N-len(x)),(0,0)))
    ar=active_rms(x); tgt=10**(targets[name]/20); g=tgt/(ar+1e-30)
    tracks[name]=x*g
    rep[name]={"active_in_db":20*math.log10(ar+1e-30),"target_db":targets[name],"gain_db":20*math.log10(g+1e-30)}

# staging: organ slightly left, trumpet slightly right, bass/tabla center
tracks["organ"][:,0]*=1.02;tracks["organ"][:,1]*=0.92
tracks["trumpet"][:,0]*=0.91;tracks["trumpet"][:,1]*=1.03

mix=tracks["organ"]+tracks["trumpet"]+tracks["bass"]+tracks["tabla"]
fade=int(0.6*SR)
mix[-fade:]*=np.linspace(1,0,fade)[:,None]
pk=float(np.max(np.abs(mix))+1e-30)
g=(10**(-1.2/20))/pk
mix*=g
mono=mix.mean(axis=1)
out=Path(r"%ZIRYAB_SAMPLES%\ZIRYAB-NIGHT-ORGAN-001.wav")
sf.write(out,mix,SR,subtype="PCM_24")
rep["master"]={
 "gain_db":20*math.log10(g),
 "peak_dbfs":20*math.log10(float(np.max(np.abs(mix)))+1e-30),
 "rms_dbfs":20*math.log10(float(np.sqrt(np.mean(mono**2)))+1e-30),
 "duration_sec":len(mix)/SR,
 "output":str(out)
}
Path(r"%ZIRYAB_STUDIO%\Projects\ZRY-NIGHT-ORGAN-001\Provenance\mix_report.json").write_text(json.dumps(rep,ensure_ascii=False,indent=2),encoding="utf-8")
print(json.dumps(rep,ensure_ascii=False,indent=2))
