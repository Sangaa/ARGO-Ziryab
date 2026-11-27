import math,json
from pathlib import Path
import numpy as np
import soundfile as sf

SR=44100
srcs={
 "guitar":Path(r"%ZIRYAB_STUDIO%\Projects\ZRY-NYLON-TABLA-001\Renders\NYLON_GUITAR_STEM.wav"),
 "tabla":Path(r"%ZIRYAB_STUDIO%\Projects\ZRY-NYLON-TABLA-001\Renders\TABLA_REAL_STEM.wav"),
 "bass":Path(r"%ZIRYAB_STUDIO%\Projects\ZRY-NYLON-TABLA-001\Renders\BASS_STEM.wav"),
}
target_active={"guitar":-18.5,"tabla":-19.0,"bass":-23.5}

def active_rms(x):
    m=x.mean(axis=1)
    frame=2048
    vals=[]
    for i in range(0,len(m)-frame+1,frame):
        r=float(np.sqrt(np.mean(m[i:i+frame]**2)))
        if r>1e-7: vals.append(r)
    if not vals:return 1e-12
    a=np.array(vals)
    q=np.percentile(a,35)
    aa=a[a>=q]
    return float(np.sqrt(np.mean(aa**2))) if len(aa) else float(np.sqrt(np.mean(a**2)))

tracks={}
N=0
rep={}
for name,p in srcs.items():
    x,sr=sf.read(p,dtype="float64",always_2d=True)
    if sr!=SR: raise RuntimeError((name,sr))
    if x.shape[1]==1:x=np.repeat(x,2,axis=1)
    tracks[name]=x[:,:2]
    N=max(N,len(x))
for name,x in list(tracks.items()):
    if len(x)<N:x=np.pad(x,((0,N-len(x)),(0,0)))
    ar=active_rms(x)
    tgt=10**(target_active[name]/20)
    g=tgt/(ar+1e-30)
    tracks[name]=x*g
    rep[name]={"active_in_db":20*math.log10(ar+1e-30),"target_active_db":target_active[name],"gain_db":20*math.log10(g+1e-30)}

# modest placement, keep pulse centered
tracks["guitar"][:,0]*=1.03; tracks["guitar"][:,1]*=0.95
tracks["bass"][:,0]*=0.96; tracks["bass"][:,1]*=0.96

mix=tracks["guitar"]+tracks["tabla"]+tracks["bass"]
# tiny tail fade
fade=int(0.45*SR)
mix[-fade:]*=np.linspace(1,0,fade)[:,None]

pk=float(np.max(np.abs(mix))+1e-30)
mg=(10**(-1.2/20))/pk
mix*=mg
mono=mix.mean(axis=1)
out=Path(r"%ZIRYAB_SAMPLES%\ZIRYAB-NYLON-TABLA-001.wav")
sf.write(out,mix,SR,subtype="PCM_24")
rep["master"]={
 "gain_db":20*math.log10(mg),
 "peak_dbfs":20*math.log10(float(np.max(np.abs(mix)))+1e-30),
 "rms_dbfs":20*math.log10(float(np.sqrt(np.mean(mono**2)))+1e-30),
 "duration_sec":len(mix)/SR,
 "instruments":["Strand Nylon Guitar","Real-sample Tabla","Crux JBass"],
 "output":str(out)
}
Path(r"%ZIRYAB_STUDIO%\Projects\ZRY-NYLON-TABLA-001\Provenance\mix_report.json").write_text(json.dumps(rep,ensure_ascii=False,indent=2),encoding="utf-8")
print(json.dumps(rep,ensure_ascii=False,indent=2))
