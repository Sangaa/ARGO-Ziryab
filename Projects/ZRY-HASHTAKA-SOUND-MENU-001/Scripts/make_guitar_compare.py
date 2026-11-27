import math
from pathlib import Path
import numpy as np
import soundfile as sf

root=Path(r"%ZIRYAB_STUDIO%\Projects\ZRY-HASHTAKA-SOUND-MENU-001\Renders")
files=[("NYLON",root/"Strand_Nylon.wav"),("STEEL",root/"Strand_Steel.wav")]
parts=[]
sr0=None
for label,p in files:
    x,sr=sf.read(p,dtype="float64",always_2d=True)
    if sr0 is None:
        sr0=sr
    mono=x.mean(axis=1)
    rms=float(np.sqrt(np.mean(mono*mono))+1e-12)
    pk=float(np.max(np.abs(x))+1e-12)
    gain=min((10**(-20/20))/rms,(10**(-2/20))/pk)
    y=x*gain
    parts.append(y)
    parts.append(np.zeros((int(1.0*sr0),2),dtype=np.float64))

out=np.concatenate(parts[:-1],axis=0)
dest=Path(r"%ZIRYAB_SAMPLES%\HASHTAKA_ABC_LAB\HASHTAKA-GUITAR-AUDITION_NYLON-then-STEEL.wav")
sf.write(dest,out,sr0,subtype="PCM_24")
print(dest)
