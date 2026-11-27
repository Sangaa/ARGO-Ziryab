import os, math
import numpy as np
import soundfile as sf

SAMPLES=r"%ZIRYAB_STUDIO%\Samples\CC0_Egyptian_Perc"
OUT=r"%ZIRYAB_STUDIO%\Projects\ZRY-TABLA-LESSON-005"
SR=48000
BPM=100
B=60.0/BPM
START=.35
BARS=16
DUR=START+BARS*4*B+.8
N=int(DUR*SR)

def load(name):
    x,sr=sf.read(os.path.join(SAMPLES,name),dtype="float32",always_2d=False)
    if x.ndim>1:x=x.mean(axis=1)
    if sr!=SR:
        old=np.arange(len(x))/sr
        new=np.arange(int(len(x)*SR/sr))/SR
        x=np.interp(new,old,x).astype(np.float32)
    return x.astype(np.float64)

DUMS=[load(x) for x in ["doom_01_01.flac","doom_01_04.flac","doom_01_07.flac"]]
TAKS=[load(x) for x in ["tak_02_01.flac","tak_02_03.flac","tak_02_05.flac"]]
PAS =[load(x) for x in ["pa_03_01.flac","pa_03_03.flac","pa_03_05.flac"]]

# Shorter finger strokes. DUM keeps body/resonance.
def shorten(x,secs):
    y=x[:min(len(x),int(secs*SR))].copy()
    f=min(len(y),int(.045*SR))
    if f>1:y[-f:]*=np.linspace(1,0,f)
    return y
TAKS=[shorten(x,.18) for x in TAKS]
PAS =[shorten(x,.13) for x in PAS]

L=np.zeros(N);R=np.zeros(N)

def add(sample,t,g,pan=0):
    i=int(round(t*SR));m=min(len(sample),N-i)
    if m<=0:return
    y=sample[:m]*g
    lg=math.sqrt((1-pan)*.5);rg=math.sqrt((1+pan)*.5)
    L[i:i+m]+=y*lg;R[i:i+m]+=y*rg

def D(t,g=.9,i=1):add(DUMS[i%len(DUMS)],t,g,-.035)
def T(t,g=.46,i=1):add(TAKS[i%len(TAKS)],t,g,.07)
def P(t,g=.16,i=1):add(PAS[i%len(PAS)],t,g,.03)

# Every half-beat has some living contact. No dead cut.
# A: D D | T T | D | T T | ghost bridge
def A(t,shade=0):
    D(t+0.0*B,.92,shade)
    D(t+0.5*B,.80,shade+1)
    T(t+1.0*B,.47,shade)
    T(t+1.5*B,.44,shade+1)
    D(t+2.0*B,.88,shade+1)
    T(t+2.5*B,.48,shade+2)
    T(t+3.0*B,.45,shade)
    P(t+3.5*B,.13,shade)   # not silence: hand still alive

# B: related sentence, still pairs. Body moves to second half.
# D | T T | D D | T T | ghost bridge
def Bphrase(t,shade=0):
    D(t+0.0*B,.90,shade+1)
    T(t+0.5*B,.45,shade)
    T(t+1.0*B,.43,shade+1)
    D(t+1.5*B,.78,shade)
    D(t+2.0*B,.92,shade+2)
    T(t+2.5*B,.48,shade+1)
    T(t+3.0*B,.45,shade)
    P(t+3.5*B,.14,shade+1)

# Transition is a "crossfade": old frame still present while new one appears.
# No full silence and no three TAKs.
def X(t,shade=0):
    D(t+0.0*B,.92,shade)
    D(t+0.5*B,.76,shade+1)
    T(t+1.0*B,.45,shade)
    T(t+1.5*B,.42,shade+1)
    # old A anchor at beat 2
    D(t+2.0*B,.72,shade+1)
    # new phrase starts bleeding in underneath with fingers
    P(t+2.25*B,.14,shade)
    P(t+2.5*B,.17,shade+1)
    D(t+2.75*B,.72,shade+2)
    T(t+3.25*B,.44,shade)
    T(t+3.5*B,.46,shade+1)

# Bars: A settles, X announces, B arrives, X returns, A home.
for b in range(BARS):
    t=START+b*4*B
    if b in (5,11):
        X(t,b)
    elif 6 <= b <= 10:
        Bphrase(t,b)
    else:
        A(t,b)

# final landing keeps hand alive to the end, no chopped cutoff
t=START+BARS*4*B
D(t,.96,1)

mix=np.stack([L,R],1)
# tiny room only
sh=int(.04*SR)
mix[sh:]+=mix[:-sh]*.02
pk=np.max(np.abs(mix)) or 1
mix*=10**(-8/20)/pk

name="ZIRYAB-TABLA-LESSON-005-CONTINUOUS-TRANSITION.wav"
wav=os.path.join(OUT,name)
desk=os.path.join(os.path.expanduser("~"),"Desktop",name)
sf.write(wav,mix,SR,subtype="PCM_24")
sf.write(desk,mix,SR,subtype="PCM_24")
print(wav)
print(desk)
print("BPM",BPM,"FORM","A x5 -> X -> B x5 -> X -> A x4","NO FULL SILENCE")
