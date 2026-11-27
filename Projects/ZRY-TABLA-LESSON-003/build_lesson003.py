import os, math
import numpy as np
import soundfile as sf

SAMPLES=r"%ZIRYAB_STUDIO%\Samples\CC0_Egyptian_Perc"
OUT=r"%ZIRYAB_STUDIO%\Projects\ZRY-TABLA-LESSON-003"
SR=48000
BPM=96
B=60.0/BPM
REPS=10
START=.45
DUR=START + REPS*4*B + .8
N=int(DUR*SR)

def load(name):
    x,sr=sf.read(os.path.join(SAMPLES,name),dtype="float32",always_2d=False)
    if x.ndim>1: x=x.mean(axis=1)
    if sr!=SR:
        old=np.arange(len(x))/sr
        new=np.arange(int(len(x)*SR/sr))/SR
        x=np.interp(new,old,x).astype(np.float32)
    return x.astype(np.float64)

# One fixed center hit + one fixed light edge hit:
# no ornaments, no sample roulette, no timing humanization.
DUM=load("doom_01_04.flac")
TAK=load("tak_02_03.flac")

# Make TAK a short finger statement, not another "event" the size of DUM.
tak_len=min(len(TAK), int(.19*SR))
TAK=TAK[:tak_len].copy()
fade=min(len(TAK),int(.055*SR))
TAK[-fade:]*=np.linspace(1,0,fade)

L=np.zeros(N); R=np.zeros(N)

def add(s,t,g,pan):
    i=int(round(t*SR)); m=min(len(s),N-i)
    if m<=0:return
    y=s[:m]*g
    lg=math.sqrt((1-pan)*.5); rg=math.sqrt((1+pan)*.5)
    L[i:i+m]+=y*lg; R[i:i+m]+=y*rg

def D(t,g=1.0): add(DUM,t,g,-.035)
def T(t,g=.50): add(TAK,t,g,.07)

# EXACT lesson phrase, 8 equal eighth-note positions over 4 beats:
# DUM DUM | TAK TAK TAK | DUM | TAK TAK
for r in range(REPS):
    t=START+r*4*B
    D(t+0.0*B,.92)
    D(t+0.5*B,.82)
    T(t+1.0*B,.48)
    T(t+1.5*B,.46)
    T(t+2.0*B,.50)
    D(t+2.5*B,.90)
    T(t+3.0*B,.48)
    T(t+3.5*B,.46)

mix=np.stack([L,R],1)
pk=np.max(np.abs(mix)) or 1
mix*=10**(-8/20)/pk

name="ZIRYAB-TABLA-LESSON-003-FIX-THE-PULSE.wav"
wav=os.path.join(OUT,name)
desktop=os.path.join(os.path.expanduser("~"),"Desktop",name)
sf.write(wav,mix,SR,subtype="PCM_24")
sf.write(desktop,mix,SR,subtype="PCM_24")
print(wav)
print(desktop)
print("BPM",BPM,"REPS",REPS,"PATTERN","D D T T T D T T")
