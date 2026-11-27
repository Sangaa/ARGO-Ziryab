import os, math, random
import numpy as np
import soundfile as sf

SAMPLES=r"%ZIRYAB_STUDIO%\Samples\CC0_Egyptian_Perc"
OUT=r"%ZIRYAB_STUDIO%\Projects\ZRY-TABLA-LESSON-001"
os.makedirs(OUT,exist_ok=True)
SR=48000
BPM=108
B=60.0/BPM
DUR=34.0
N=int(DUR*SR)
rng=random.Random(1010)

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

def add(pool,t,g=.7,pan=0.0,trim=1.0):
    if t<0 or t>=DUR: return
    s=pool[rng.randrange(len(pool))].copy()
    if trim<1:
        m=max(50,int(len(s)*trim)); s=s[:m]
        f=min(len(s),int(.025*SR))
        if f>1:s[-f:]*=np.linspace(1,0,f)
    # human level variation
    g*=rng.uniform(.92,1.08)
    i=int(t*SR); m=min(len(s),N-i); s=s[:m]*g
    lg=math.sqrt((1-pan)*.5); rg=math.sqrt((1+pan)*.5)
    L[i:i+m]+=s*lg; R[i:i+m]+=s*rg

def doom(t,g=.9): add(DOOM,t+ rng.uniform(-.008,.008),g,-.06)
def tak(t,g=.68):  add(TAK ,t+ rng.uniform(-.010,.010),g,.12)
def pa(t,g=.36,short=True): add(PA,t+rng.uniform(-.012,.012),g,.05,.55 if short else 1)

# 0-4s: sound vocabulary, not "rhythm" yet
doom(.35,.88)
tak(1.15,.62); pa(1.55,.28); tak(1.82,.46)
doom(2.55,.75); pa(2.92,.24); pa(3.10,.20); tak(3.32,.68)

# 4-11s: pulse appears, with spaces and finger ghosts
t0=4.15
for bar in range(3):
    t=t0+bar*2*B
    doom(t,.88)
    pa(t+.42*B,.20)
    tak(t+.92*B,.62)
    pa(t+1.23*B,.22)
    if bar!=1:
        doom(t+1.52*B,.58)
    pa(t+1.70*B,.18)
    tak(t+1.88*B,.72)
# pickup
for k,(o,g,typ) in enumerate([(0,.22,'p'),(.13,.28,'p'),(.25,.42,'t'),(.37,.60,'t')]):
    (pa if typ=='p' else tak)(10.0+o,g)

# 11-18s: "doudum" body + edge conversation
t0=11.0
for bar in range(3):
    t=t0+bar*2*B
    doom(t,.82)
    tak(t+.78*B,.58)
    doom(t+1.16*B,.54)
    doom(t+1.43*B,.78)
    pa(t+1.62*B,.20)
    tak(t+1.86*B,.72)
    if bar==1:
        pa(t+1.98*B,.22)

# 18-24s: finger-work / ghuraz, tempo implied not stated
t=18.15
seq=[
('d',0,.86),('p',.31,.18),('p',.48,.24),('t',.65,.55),
('p',.89,.19),('t',1.03,.42),('p',1.15,.20),('t',1.31,.68),
('d',1.72,.72),('p',1.96,.20),('p',2.08,.22),('t',2.22,.47),
('p',2.36,.18),('t',2.50,.56),('p',2.62,.22),('t',2.76,.74)]
for typ,o,g in seq:
    {'d':doom,'t':tak,'p':pa}[typ](t+o*B,g)
# repeat mutated
for typ,o,g in seq:
    if o<1.7:
        {'d':doom,'t':tak,'p':pa}[typ](t+3.25*B+o*B,g*.92)

# 24-29s: conductor moment: big statement, then "hand up" space, then response
t=24.0
doom(t,.96); doom(t+.34*B,.58); tak(t+.86*B,.70)
pa(t+1.14*B,.20); tak(t+1.40*B,.46)
# deliberate air
tak(t+2.28*B,.54); pa(t+2.47*B,.18)
# answer with edge fingers
for o,g,typ in [(2.82,.24,'p'),(2.96,.34,'p'),(3.10,.48,'t'),(3.24,.25,'p'),(3.39,.62,'t')]:
    {'t':tak,'p':pa}[typ](t+o*B,g)

# 29-34s: return and one little flourish, then clean last DUM
t=29.0
doom(t,.92); tak(t+.90*B,.63); pa(t+1.20*B,.21)
doom(t+1.50*B,.60); tak(t+1.88*B,.73)
for o,g,typ in [(2.25,.20,'p'),(2.38,.24,'p'),(2.50,.38,'t'),(2.62,.22,'p'),(2.74,.52,'t'),(2.86,.26,'p'),(3.0,.74,'t')]:
    {'t':tak,'p':pa}[typ](t+o*B,g)
doom(32.55,1.0)
pa(33.00,.18)
tak(33.18,.42)
doom(33.52,.82)

mix=np.stack([L,R],1)
# very short natural room, keep drum dry/close
sh=int(.055*SR)
mix[sh:]+=mix[:-sh]*.035
# no loudness race
pk=np.max(np.abs(mix)) or 1
mix*=10**(-7/20)/pk
wav=os.path.join(OUT,"ZIRYAB-TABLA-LESSON-001.wav")
sf.write(wav,mix,SR,subtype="PCM_24")
desktop=os.path.join(os.path.expanduser("~"),"Desktop","ZIRYAB-TABLA-LESSON-001.wav")
sf.write(desktop,mix,SR,subtype="PCM_24")
print(wav)
print(desktop)
