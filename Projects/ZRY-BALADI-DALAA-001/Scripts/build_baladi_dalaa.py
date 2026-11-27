import os, math, random
import numpy as np
import soundfile as sf

ROOT=r"%ZIRYAB_STUDIO%\Projects\ZRY-BALADI-DALAA-001"
SAMPLES=r"%ZIRYAB_STUDIO%\Samples\CC0_Egyptian_Perc"
REND=os.path.join(ROOT,"Renders")
PROV=os.path.join(ROOT,"Provenance")
os.makedirs(REND,exist_ok=True); os.makedirs(PROV,exist_ok=True)

SR=48000
BPM=112
BEAT=60/BPM
DUR=43.0
N=int(DUR*SR)
rng=random.Random(369)
np.random.seed(369)

def load_mono(path):
    x,sr=sf.read(path,dtype="float32",always_2d=False)
    if x.ndim>1: x=x.mean(axis=1)
    if sr!=SR:
        # linear resample, enough for one-shots
        old=np.arange(len(x))/sr
        new=np.arange(int(len(x)*SR/sr))/SR
        x=np.interp(new,old,x).astype(np.float32)
    return x

doom=[load_mono(os.path.join(SAMPLES,f)) for f in ["doom_01_01.flac","doom_01_04.flac","doom_01_07.flac","doom_01_10.flac"]]
tak =[load_mono(os.path.join(SAMPLES,f)) for f in ["tak_02_01.flac","tak_02_03.flac","tak_02_05.flac","tak_02_07.flac"]]
pa  =[load_mono(os.path.join(SAMPLES,f)) for f in ["pa_03_01.flac","pa_03_03.flac","pa_03_05.flac"]]

# Find several transient slices from the real finger-cymbal recording.
cy=load_mono(os.path.join(SAMPLES,"finger_cymbals_2274.mp3"))
absx=np.abs(cy)
peaks=[]
guard=int(.35*SR)
for i in np.argsort(absx)[::-1]:
    if all(abs(i-p)>guard for p in peaks):
        peaks.append(int(i))
        if len(peaks)>=5: break
peaks=sorted(peaks)
zills=[]
for p in peaks:
    a=max(0,p-int(.012*SR)); b=min(len(cy),p+int(.42*SR))
    zz=cy[a:b].copy()
    if len(zz):
        fade=min(len(zz),int(.09*SR))
        zz[-fade:]*=np.linspace(1,0,fade)
        zills.append(zz)

L=np.zeros(N,dtype=np.float64); R=np.zeros(N,dtype=np.float64)

def add(sample,t,gain=1.0,pan=0.0):
    i=int(t*SR)
    if i<0 or i>=N: return
    m=min(len(sample),N-i)
    if m<=0:return
    s=sample[:m]*gain
    lg=math.sqrt((1-pan)*.5); rg=math.sqrt((1+pan)*.5)
    L[i:i+m]+=s*lg; R[i:i+m]+=s*rg

def hit(pool,t,gain=1.0,pan=0.0):
    s=pool[rng.randrange(len(pool))]
    # tiny natural level drift; never pitch-shift the real drum
    add(s,t,gain*(.94+rng.random()*.12),pan)

# rhythmic vocabulary: body first, ornament second
def groove_bar(b,variant=0,fill=False,air=False):
    t=b*4*BEAT
    if air:
        # conductor raises hand: only anchor + late pickup
        hit(doom,t,1.00,-.03)
        hit(tak,t+1.0*BEAT,.74,.08)
        hit(pa,t+3.25*BEAT,.46,.12)
        hit(tak,t+3.55*BEAT,.88,.10)
        return
    # Egyptian-flavored core based on user's spoken cue:
    # DUM ... TAK | DU-DUM ... TAK | DUM ... TRAK
    hit(doom,t+0.00*BEAT,1.00,-.04)
    hit(tak ,t+0.95*BEAT,.82,.10)
    if variant%2==0:
        hit(doom,t+1.80*BEAT,.68,-.06)
        hit(doom,t+2.12*BEAT,.92,-.03)
    else:
        hit(pa  ,t+1.72*BEAT,.38,.08)
        hit(doom,t+2.02*BEAT,.90,-.03)
    hit(tak ,t+2.92*BEAT,.86,.11)
    hit(pa  ,t+3.38*BEAT,.34,.12)
    if fill:
        hit(tak,t+3.48*BEAT,.62,.12)
        hit(pa ,t+3.66*BEAT,.50,.13)
        hit(tak,t+3.82*BEAT,.90,.10)

# Real zills converse with tabla rather than carpet it.
def zill_bar(b,mode=0):
    if not zills:return
    t=b*4*BEAT
    if mode==0:
        offs=[1.48,3.48]
    elif mode==1:
        offs=[.48,1.48,2.48,3.48]
    else:
        offs=[.48,1.48,2.22,2.48,3.22,3.48]
    for j,o in enumerate(offs):
        add(zills[(b+j)%len(zills)],t+o*BEAT,.20 if mode<2 else .17,.42)

bars=int(DUR/(4*BEAT))
for b in range(bars):
    # changes every 4 bars; rests preserve dancing via anticipation
    air=b in (6,13)
    fill=(b%4==3) or b in (5,12,17)
    groove_bar(b,b%3,fill,air)
    if b>=2 and b not in (6,13):
        zill_bar(b, 0 if b<6 else (1 if b<13 else 2))

# ---------- tonal layer: placeholder timbres, but phrasing is intentionally Egyptian ----------
def hz(n): return 440*2**((n-69)/12)
def ar(n,a=.01,r=.1):
    e=np.ones(n)
    aa=max(1,min(n,int(a*SR))); rr=max(1,min(n,int(r*SR)))
    e[:aa]=np.linspace(0,1,aa,endpoint=False); e[-rr:]=np.linspace(1,0,rr)
    return e

def oud(note,dur=.26):
    n=int(dur*SR); tt=np.arange(n)/SR; f=hz(note)
    s=sum(a*np.sin(2*np.pi*f*h*tt+.16*h) for h,a in [(1,1),(2,.48),(3,.27),(4,.14),(5,.08)])
    return s*np.exp(-tt*5.5)*ar(n,.003,.05)*.115

def ney(note,dur=.5):
    n=int((dur+.12)*SR); tt=np.arange(n)/SR; f=hz(note)
    vib=.004*np.sin(2*np.pi*5.4*tt)
    ph=2*np.pi*f*np.cumsum(1+vib)/SR
    s=np.sin(ph)+.17*np.sin(2*ph)+.05*np.sin(3*ph)
    s+=np.random.normal(0,.014,n)
    return s*ar(n,.055,.12)*.105

def violin(note,dur=.55):
    n=int((dur+.1)*SR); tt=np.arange(n)/SR; f=hz(note)
    # tiny upward scoop at entry
    ratio=2**((-35*np.exp(-tt/.055))/1200)
    ph=2*np.pi*f*np.cumsum(ratio)/SR
    s=sum((1/h)*np.sin(h*ph+.12*h) for h in range(1,7))
    return s*ar(n,.05,.12)*.040

def bass(note,dur=.45):
    n=int(dur*SR); tt=np.arange(n)/SR; f=hz(note)
    s=np.sin(2*np.pi*f*tt)+.24*np.sin(4*np.pi*f*tt)
    return s*np.exp(-tt*2)*ar(n,.008,.08)*.145

# D Hijaz neighborhood: D Eb F# G A Bb C
D4,Eb4,Fs4,G4,A4,Bb4,C5,D5,Eb5,Fs5,G5,A5=62,63,66,67,69,70,72,74,75,78,79,81

# Repeating hook with mutation, because this is dance music
CALL=[(D4,0,.26),(Eb4,.42,.18),(Fs4,.68,.32),(G4,1.18,.22),(A4,1.48,.44),(G4,2.12,.24),(Fs4,2.46,.22),(D4,3.05,.52)]
ANS =[(A4,0,.28),(Bb4,.42,.18),(A4,.70,.22),(G4,1.02,.35),(Fs4,1.62,.22),(Eb4,1.96,.20),(D4,2.42,.32),(Fs4,3.05,.42)]

def phrase(inst,bar,seq,pan,g=.9,oct=0):
    base=bar*4*BEAT
    for note,o,d in seq:
        add(inst(note+oct,d*BEAT),base+o*BEAT,g,pan)

# Oud establishes hook
for b in (1,3,5):
    phrase(oud,b,CALL if b!=3 else ANS,-.27,.95)
# Ney gets space after conductor break
phrase(ney,7,ANS,.24,.93)
phrase(ney,9,CALL,.24,.90)
# Violin answers, then dialogue
phrase(violin,10,CALL,-.12,.92,12)
phrase(ney,11,ANS,.22,.90)
# Peak: shorter alternating fragments
for b in (14,15,16,17):
    phrase(oud,b,CALL if b%2==0 else ANS,-.27,.82)
    if b in (15,17):
        # only half-phrase ney response so tabla still rules
        base=b*4*BEAT+2.05*BEAT
        for note,o,d in ANS[:4]:
            add(ney(note,d*.78*BEAT),base+(o*.42)*BEAT,.72,.24)

# Bass is tied to DUM, not continuous Western bassline
for b in range(3,bars):
    base=b*4*BEAT
    add(bass(38,.54),base,.95,0)
    if b not in (6,13):
        add(bass(38,.42),base+2.04*BEAT,.76,0)
    if b%4==3:
        add(bass(45,.30),base+3.03*BEAT,.57,0)

mix=np.stack([L,R],axis=1)
# small room, percussion stays forward
for delay,g in [(.085,.045),(.155,.025)]:
    sh=int(delay*SR)
    mix[sh:]+=mix[:-sh]*g

mix=np.tanh(mix*1.05)
peak=float(np.max(np.abs(mix))) or 1
mix*=10**(-5/20)/peak

wav=os.path.join(REND,"ZIRYAB-BALADI-DALAA-sketch01-real-percussion.wav")
sf.write(wav,mix,SR,subtype="PCM_24")

with open(os.path.join(PROV,"README.txt"),"w",encoding="utf-8") as f:
    f.write("ZIRYAB BALADI DALAA sketch01\n")
    f.write("Real darbuka one-shots: FreePats World Percussion, CC0 1.0, recorded from real instruments.\n")
    f.write("Finger cymbal recording: BigSoundBank #2274, Joseph SARDIN, CC0.\n")
    f.write("Melodic timbres are temporary synthesis placeholders; rhythm/percussion is the point of this sketch.\n")
    f.write(f"BPM={BPM}; duration={DUR}s; peak=-5 dBFS target.\n")
    f.write("No overwrite of HASHTAKA-001.\n")

print(wav)
print("zill_peaks",peaks)
print("bars",bars)
