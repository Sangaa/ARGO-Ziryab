import os, numpy as np, soundfile as sf
ROOT=r"%ZIRYAB_STUDIO%\Projects\ZRY-HASHTAKA-CLAUDE-LAB-001"
LISTEN=r"%ZIRYAB_SAMPLES%\HASHTAKA_ABC_LAB"
files=[
 ("A",os.path.join(ROOT,"Renders","HASHTAKA-A_CONTROL.wav")),
 ("B",os.path.join(ROOT,"Renders","HASHTAKA-B_REAL_SAMPLES.wav")),
 ("C",os.path.join(ROOT,"Renders","HASHTAKA-C_REAL_DUM_SYNTH_EDGES.wav")),
]
BPM=112.0
BAR=4*60/BPM
PRE=3*(BAR/16)
start=PRE+(22-1)*BAR
dur=8*BAR
gap=1.25
parts=[]
sr0=None
for label,p in files:
    x,sr=sf.read(p,dtype="float32",always_2d=True)
    if sr0 is None: sr0=sr
    i0=int(round(start*sr)); i1=min(len(x),int(round((start+dur)*sr)))
    parts.append(x[i0:i1])
    parts.append(np.zeros((int(gap*sr),2),dtype=np.float32))
out=np.concatenate(parts[:-1],axis=0)
dest=os.path.join(LISTEN,"HASHTAKA-ABC-GROOVE-COMPARE_A-then-B-then-C.wav")
sf.write(dest,out,sr0,subtype="PCM_16")
print(dest)
print("segment_seconds",dur,"total",len(out)/sr0)
