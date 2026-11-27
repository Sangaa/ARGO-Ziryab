import math,json
from pathlib import Path
import numpy as np, soundfile as sf
SR=44100
srcs={
 "organ":Path(r"%ZIRYAB_STUDIO%\Projects\ZRY-NIGHT-ORGAN-002\Renders\ORGAN_STEM.wav"),
 "trumpet":Path(r"%ZIRYAB_STUDIO%\Projects\ZRY-NIGHT-ORGAN-002\Renders\MUTED_TRUMPET_STEM.wav"),
 "bass":Path(r"%ZIRYAB_STUDIO%\Projects\ZRY-NIGHT-ORGAN-002\Renders\JAZZ_BASS_STEM.wav"),
 "tabla":Path(r"%ZIRYAB_STUDIO%\Projects\ZRY-NIGHT-ORGAN-002\Renders\TABLA_LIGHT_STEM.wav"),
}
targets={"organ":-20.2,"trumpet":-19.8,"bass":-23.2,"tabla":-24.5}
def active_rms(x):
    m=x.mean(1); vals=[]; frame=2048
    for i in range(0,len(m)-frame+1,frame):
        r=float(np.sqrt(np.mean(m[i:i+frame]**2)))
        if r>1e-7: vals.append(r)
    if not vals:return 1e-12
    a=np.array(vals); cut=np.percentile(a,35); a=a[a>=cut]
    return float(np.sqrt(np.mean(a*a))) if len(a) else 1e-12
tracks={};N=0;rep={}
for name,p in srcs.items():
    x,sr=sf.read(p,dtype="float64",always_2d=True)
    if x.shape[1]==1:x=np.repeat(x,2,1)
    tracks[name]=x[:,:2]; N=max(N,len(x))
for name,x in list(tracks.items()):
    if len(x)<N:x=np.pad(x,((0,N-len(x)),(0,0)))
    ar=active_rms(x); g=10**(targets[name]/20)/(ar+1e-30)
    tracks[name]=x*g
    rep[name]={"target_db":targets[name],"gain_db":20*math.log10(g+1e-30)}
tracks["organ"][:,0]*=1.02; tracks["organ"][:,1]*=.94
tracks["trumpet"][:,0]*=.92; tracks["trumpet"][:,1]*=1.03
mix=sum(tracks.values())
fade=int(.55*SR); mix[-fade:]*=np.linspace(1,0,fade)[:,None]
pk=float(np.max(np.abs(mix))+1e-30); mg=10**(-1.2/20)/pk; mix*=mg
mono=mix.mean(1)
out=Path(r"%ZIRYAB_SAMPLES%\ZIRYAB-NIGHT-ORGAN-002-v2.wav")
sf.write(out,mix,SR,subtype="PCM_24")
rep["master"]={"peak_dbfs":20*math.log10(np.max(np.abs(mix))+1e-30),"rms_dbfs":20*math.log10(np.sqrt(np.mean(mono*mono))+1e-30),"duration_sec":len(mix)/SR,"output":str(out)}
Path(r"%ZIRYAB_STUDIO%\Projects\ZRY-NIGHT-ORGAN-002\Provenance\mix_report.json").write_text(json.dumps(rep,indent=2),encoding="utf-8")
print(json.dumps(rep,indent=2))
