import math,json
from pathlib import Path
import numpy as np
import soundfile as sf

root=Path(r"%ZIRYAB_STUDIO%\Projects\ZRY-HASHTAKA-CLAUDE-E-ORIENTAL-BAND-001\Auditions")
files=[
 ("OUD",root/"01_OUD_TURKISH_HASHTAKA_PHRASE.wav"),
 ("ACCORDION",root/"02_ACCORDION_HOHNER_HASHTAKA_PHRASE.wav"),
 ("VIOLIN",root/"03_VIOLIN_SIMPLY_HASHTAKA_PHRASE.wav"),
 ("NEY_AUDITION",root/"04_NEY_CC0_DERIVED_HASHTAKA_PHRASE.wav"),
]
parts=[]
rep={}
sr0=None
for label,p in files:
    x,sr=sf.read(p,dtype="float64",always_2d=True)
    if x.shape[1]==1:
        x=np.repeat(x,2,axis=1)
    if sr0 is None:
        sr0=sr
    mono=x.mean(axis=1)
    rms=float(np.sqrt(np.mean(mono*mono))+1e-12)
    pk=float(np.max(np.abs(x))+1e-12)
    gain=min((10**(-20/20))/rms,(10**(-2/20))/pk)
    y=x*gain
    yrms=float(np.sqrt(np.mean((y.mean(axis=1))**2))+1e-12)
    ypk=float(np.max(np.abs(y))+1e-12)
    rep[label]={
        "rms_db":20*math.log10(yrms),
        "peak_db":20*math.log10(ypk)
    }
    parts.append(y)
    parts.append(np.zeros((int(1.0*sr0),2),dtype=np.float64))

out=np.concatenate(parts[:-1],axis=0)
dest=Path(r"%ZIRYAB_SAMPLES%\HASHTAKA_ABC_LAB\HASHTAKA-E-ORIENTAL-AUDITION_OUD-ACC-VIOLIN-NEY.wav")
sf.write(dest,out,sr0,subtype="PCM_24")
(root/"ORIENTAL_AUDITION_LEVELS.json").write_text(json.dumps(rep,indent=2),encoding="utf-8")
print(dest)
print(json.dumps(rep,indent=2))
