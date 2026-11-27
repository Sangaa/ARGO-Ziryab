import os, math
import numpy as np
import soundfile as sf

SAMPLES=r"%ZIRYAB_STUDIO%\Samples\CC0_Egyptian_Perc"
OUT=r"%ZIRYAB_STUDIO%\Projects\ZRY-TABLA-LESSON-004"
SR=48000
BPM=96
B=60.0/BPM
START=.45
REPS=10
DUR=START+REPS*4*B+.8
N=int(DUR*SR)

def load(name):
    x,sr=sf.read(os.path.join(SAMPLES,name),dtype="float32",always_2d=False)
    if x.ndim>1:x=x.mean(axis=1)
    if sr!=SR:
        old=np.arange(len(x))/sr
        new=np.arange(int(len(x)*SR/sr))/SR
        x=np.interp(new,old,x).astype(np.float32)
    return x.astype(np.float64)

DUM=load("doom_01_04.flac")
TAK=load("tak_02_03.flac")

# Keep TAK short/light so it behaves like fingers, not a second DUM.
TAK=TAK[:min(len(TAK),int(.18*SR))].copy()
fade=min(len(TAK),int(.05*SR))
TAK[-fade:]*=np.linspace(1,0,fade)

L=np.zeros(N); R=np.zeros(N)

def add(s,t,g,pan):
    i=int(round(t*SR)); m=min(len(s),N-i)
    if m<=0:return
    y=s[:m]*g
    lg=math.sqrt((1-pan)*.5); rg=math.sqrt((1+pan)*.5)
    L[i:i+m]+=y*lg; R[i:i+m]+=y*rg

def D(t,g=.92):add(DUM,t,g,-.035)
def T(t,g=.48):add(TAK,t,g,.07)

# BASE PHRASE: all TAKs are pairs.
# DUM DUM | TAK TAK | DUM | TAK TAK | breath
def base(t):
    D(t+0.0*B,.92)
    D(t+0.5*B,.82)
    T(t+1.0*B,.48)
    T(t+1.5*B,.46)
    D(t+2.0*B,.90)
    T(t+2.5*B,.48)
    T(t+3.0*B,.46)
    # 3.5 beat slot intentionally left empty as breath

# SMALL BREAK: same vocabulary, still only pairs.
# DUM DUM | TAK TAK | breath | DUM DUM | TAK TAK
def broken(t):
    D(t+0.0*B,.92)
    D(t+0.5*B,.82)
    T(t+1.0*B,.48)
    T(t+1.5*B,.46)
    # breath at 2.0
    D(t+2.5*B,.88)
    D(t+3.0*B,.78)
    T(t+3.25*B,.44)
    T(t+3.5*B,.44)

for r in range(REPS):
    t=START+r*4*B
    if r in (6,8):
        broken(t)
    else:
        base(t)

mix=np.stack([L,R],1)
pk=np.max(np.abs(mix)) or 1
mix*=10**(-8/20)/pk

name="ZIRYAB-TABLA-LESSON-004-PAIRS-ONLY.wav"
wav=os.path.join(OUT,name)
desktop=os.path.join(os.path.expanduser("~"),"Desktop",name)
sf.write(wav,mix,SR,subtype="PCM_24")
sf.write(desktop,mix,SR,subtype="PCM_24")
print(wav)
print(desktop)
print("BPM",BPM,"BASE","D D T T D T T + breath","BREAK","pairs only")
