import os, math, json
import numpy as np
import soundfile as sf
from pathlib import Path

root=Path(r"%ZIRYAB_STUDIO%\Projects\ZRY-HASHTAKA-CLAUDE-E-ORIENTAL-BAND-001\Auditions")
files=[
 ("OUD",root/"01_OUD_TURKISH_HASHTAKA_PHRASE.wav"),
 ("ACCORDION",root/"02_ACCORDION_HOHNER_HASHTAKA_PHRASE.wav"),
 ("VIOLIN",root/"03_VIOLIN_SIMPLY_HASHTAKA_PHRASE.wav"),
]
sr0=None
parts=[]
report={}
gap_sec=1.0
for label,p in files:
    x,sr=sf.read(p,dtype="float64",always_2d=True)
    if sr0 is None: sr0=sr
    if sr!=sr0: raise RuntimeError("sr mismatch")
    mono=x.mean(axis=1)
    rms=float(np.sqrt(np.mean(mono*mono))+1e-12)
    pk=float(np.max(np.abs(x))+1e-12)
    target_rms=10**(-20/20)
    gain=target_rms/rms
    max_gain=(10**(-2/20))/pk
    gain=min(gain,max_gain)
    y=x*gain
    report[label]={
      "source":str(p),
      "input_rms_db":20*math.log10(rms),
      "input_peak_db":20*math.log10(pk),
      "gain_db":20*math.log10(gain),
      "out_rms_db":20*math.log10(float(np.sqrt(np.mean((y.mean(axis=1))**2))+1e-12)),
      "out_peak_db":20*math.log10(float(np.max(np.abs(y))+1e-12)),
    }
    parts.append(y)
    parts.append(np.zeros((int(gap_sec*sr0),2),dtype=np.float64))
out=np.concatenate(parts[:-1],axis=0)
dest=Path(r"%ZIRYAB_SAMPLES%\HASHTAKA_ABC_LAB\HASHTAKA-E-INSTRUMENT-AUDITION_OUD-ACC-VIOLIN.wav")
sf.write(dest,out,sr0,subtype="PCM_24")
(root/"AUDITION_LEVEL_REPORT.json").write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding="utf-8")
print(dest)
print(json.dumps(report,indent=2))
