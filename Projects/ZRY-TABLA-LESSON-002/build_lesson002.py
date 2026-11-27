import os, math, random
import numpy as np
import soundfile as sf

SAMPLES=r"%ZIRYAB_STUDIO%\Samples\CC0_Egyptian_Perc"
OUT=r"%ZIRYAB_STUDIO%\Projects\ZRY-TABLA-LESSON-002"
os.makedirs(OUT,exist_ok=True)

SR=48000
BPM=104
B=60.0/BPM
DUR=31.0
N=int(DUR*SR)
rng=random.Random(20261010)

def load(name):
    x,sr=sf.read(os.path.join(SAMPLES,name),dtype="float32",always_2d=False)
    if x.ndim>1: x=x.mean(axis=1)
    if sr!=SR:
        old=np.arange(len(x))/sr
        new=np.arange(int(len(x)*SR/sr))/SR
        x=np.interp(new,old,x).astype(np.float32)
    return x.astype(np.float64)

DOOM=[load(x) for x in ["doom_01_01.flac","doom_01_04.flac","doom_01_07.flac","doom_01_10.flac"]]
TAK =[load(x) for x in ["tak_02_01.flac","tak_02_03.flac","tak_02_05.flac","tak_02_07.flac"]]
PA  =[load(x) for x in ["pa_03_01.flac","pa_03_03.flac","pa_03_05.flac"]]

L=np.zeros(N); R=np.zeros(N)

def add(pool,t,g=1.0,pan=0.0,idx=None):
    if t<0 or t>=DUR: return
    if idx is None: s=pool[rng.randrange(len(pool))]
    else: s=pool[idx % len(pool)]
    i=int(t*SR); m=min(len(s),N-i); s=s[:m]*g
    lg=math.sqrt((1-pan)*.5); rg=math.sqrt((1+pan)*.5)
    L[i:i+m]+=s*lg; R[i:i+m]+=s*rg

def D(t,g=.9,idx=None): add(DOOM,t,g,-.05,idx)
def T(t,g=.7,idx=None): add(TAK,t,g,.10,idx)
def P(t,g=.3,idx=None): add(PA,t,g,.04,idx)

# Pattern in 2 beats: DUM TAK TAK
def basic_bar(t, layer=1, fill=False, idxshift=0):
    if layer==1:
        D(t,.86,0+idxshift); T(t+.95*B,.62,0+idxshift); T(t+1.55*B,.58,1+idxshift)
    elif layer==2:
        D(t,.90,2+idxshift); T(t+.95*B,.68,2+idxshift); T(t+1.55*B,.52,3+idxshift)
    else:
        D(t,.94,3+idxshift); T(t+.95*B,.56,1+idxshift); T(t+1.55*B,.70,0+idxshift)
    if fill:
        # one simple ghurza: two quiet finger notes before final tak, then back home
        P(t+1.28*B,.20,0)
        P(t+1.40*B,.24,1)

# 0-10s: very plain, same layer
t=.45
for k in range(8):
    basic_bar(t+k*2*B,layer=1,fill=False)

# 10-20s: same rhythm, different layers/colors, timing unchanged
t=10.1
layers=[1,2,3,1,2,3,2,1]
for k,layer in enumerate(layers):
    basic_bar(t+k*2*B,layer=layer,fill=False,idxshift=k)

# 20-30s: same rhythm, only occasional simple ghurza
t=20.0
fills={2,5}
for k in range(8):
    basic_bar(t+k*2*B,layer=2 if k%2 else 1,fill=(k in fills),idxshift=k)

# final clean statement
D(29.55,.98,1); T(30.10,.68,2); T(30.45,.62,3)

mix=np.stack([L,R],1)
# tiny room only
sh=int(.045*SR)
mix[sh:]+=mix[:-sh]*.025
pk=np.max(np.abs(mix)) or 1
mix*=10**(-8/20)/pk

wav=os.path.join(OUT,"ZIRYAB-TABLA-LESSON-002-BASIC-LAYERS-GHURZA.wav")
desktop=os.path.join(os.path.expanduser("~"),"Desktop","ZIRYAB-TABLA-LESSON-002-BASIC-LAYERS-GHURZA.wav")
sf.write(wav,mix,SR,subtype="PCM_24")
sf.write(desktop,mix,SR,subtype="PCM_24")
print(wav)
print(desktop)
