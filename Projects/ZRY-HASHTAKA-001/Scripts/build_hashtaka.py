import math, os, wave, struct, random
import numpy as np

ROOT = r"%ZIRYAB_STUDIO%\Projects\ZRY-HASHTAKA-001"
MIDIDIR = os.path.join(ROOT, "MIDI")
RENDERDIR = os.path.join(ROOT, "Renders")
PROVDIR = os.path.join(ROOT, "Provenance")
os.makedirs(MIDIDIR, exist_ok=True)
os.makedirs(RENDERDIR, exist_ok=True)
os.makedirs(PROVDIR, exist_ok=True)

BPM = 112
PPQ = 480
SR = 44100
BARS = 36
BEATS = BARS * 4
DUR = BEATS * 60.0 / BPM + 2.5
N = int(DUR * SR)
random.seed(369)
np.random.seed(369)

def hz(midi):
    return 440.0 * (2.0 ** ((midi - 69) / 12.0))

def vlen(n):
    buf = [n & 0x7F]
    n >>= 7
    while n:
        buf.append((n & 0x7F) | 0x80)
        n >>= 7
    return bytes(reversed(buf))

def midi_file(path, events, channel=0, percussion=False):
    # events: (start_beat, dur_beat, note, velocity)
    tempo = int(round(60000000 / BPM))
    raw = bytearray()
    # tempo
    raw += vlen(0) + b"\xff\x51\x03" + tempo.to_bytes(3, "big")
    # 4/4
    raw += vlen(0) + b"\xff\x58\x04\x04\x02\x18\x08"
    evs = []
    ch = 9 if percussion else channel
    for st, dur, note, vel in events:
        on = int(round(st * PPQ))
        off = int(round((st + dur) * PPQ))
        evs.append((on, 1, bytes([0x90 | ch, note, vel])))
        evs.append((off, 0, bytes([0x80 | ch, note, 0])))
    evs.sort(key=lambda x: (x[0], x[1]))
    last = 0
    for tick, _, msg in evs:
        raw += vlen(tick-last) + msg
        last = tick
    raw += vlen(0) + b"\xff\x2f\x00"
    hdr = b"MThd" + (6).to_bytes(4,"big") + (0).to_bytes(2,"big") + (1).to_bytes(2,"big") + PPQ.to_bytes(2,"big")
    trk = b"MTrk" + len(raw).to_bytes(4,"big") + bytes(raw)
    with open(path, "wb") as f:
        f.write(hdr + trk)

tabla=[]; gtr=[]; bass=[]; flute=[]; strings=[]; piano=[]

# --- Tabla: maqsum-inspired, with fills and micro-breaks ---
for bar in range(BARS):
    b = bar*4.0
    # short intro pickup in bar 0
    if bar == 0:
        tabla += [(b+2.75,0.10,50,82),(b+3.25,0.10,50,90),(b+3.75,0.12,36,112)]
        continue
    # micro-breaks before selected returns
    if bar in (15,27):
        tabla += [(b+0.0,0.12,36,112),(b+1.0,0.10,50,88)]
        tabla += [(b+3.50,0.10,50,96),(b+3.75,0.10,50,104)]
        continue
    # base groove
    tabla += [
        (b+0.00,0.12,36,112),
        (b+1.00,0.10,50,90),
        (b+2.00,0.12,36,106),
        (b+2.50,0.10,50,92),
        (b+3.50,0.10,50,98),
    ]
    if bar >= 4:
        tabla += [(b+1.75,0.08,50,48)]
    # fills at section ends
    if bar in (7,11,19,23,31,35):
        tabla += [(b+3.00,0.08,50,78),(b+3.25,0.08,50,86),(b+3.50,0.08,50,96),(b+3.75,0.08,50,112)]

# occasional clap / riq-like accent
for bar in range(4,BARS):
    b=bar*4
    if bar % 2 == 0:
        tabla += [(b+1.0,0.08,38,58),(b+3.0,0.08,38,62)]

# --- Hook material ---
# D Hijaz-ish: D Eb F# G A Bb C
CALL = [(74,0.0,0.50),(77,0.75,0.25),(79,1.0,0.50),(81,1.75,0.25),(79,2.0,0.50),(77,2.75,0.25),(74,3.0,0.75)]
ANSWER=[(81,0.0,0.35),(82,0.50,0.25),(81,0.75,0.25),(79,1.0,0.45),(78,1.75,0.25),(79,2.0,0.35),(75,2.50,0.25),(74,3.0,0.75)]

def add_phrase(dst, start, phrase, transpose=0, vel=88, scale_dur=1.0):
    for n,off,d in phrase:
        dst.append((start+off, d*scale_dur, n+transpose, vel))

# nylon: short rhythmic riff, playful
for bar in range(1,BARS):
    b=bar*4.0
    if bar < 4:
        notes=[62,65,67,69]
        for i,n in enumerate(notes):
            gtr.append((b+i*0.75,0.22,n,62+i*4))
    else:
        patt=[62,65,67,69,67,65]
        offs=[0.0,0.75,1.5,2.0,2.75,3.5]
        for n,o in zip(patt,offs):
            gtr.append((b+o,0.20,n,72 if o in (0.0,2.0) else 60))
        if bar in (8,16,24,32):
            gtr.append((b+3.75,0.12,70,82))

# bass locks to DUM
for bar in range(4,BARS):
    b=bar*4.0
    bass += [(b+0.0,0.55,38,88),(b+2.0,0.55,38,82)]
    if bar % 4 in (2,3):
        bass += [(b+3.0,0.40,45,72)]
    if bar in (11,19,27,35):
        bass += [(b+3.5,0.22,36,78),(b+3.75,0.22,38,90)]

# flute hook from bar 5 onward, not continuous
for bar in (5,7,9,11):
    add_phrase(flute, bar*4, CALL if bar%4==1 else ANSWER, vel=86)
for bar in (13,15,17,19):
    # flirt section: answer higher / mutated
    phr = ANSWER if bar in (13,17) else CALL
    add_phrase(flute, bar*4, phr, transpose=12 if bar in (15,19) else 0, vel=84 if bar in (13,17) else 78)
for bar in (21,23,25,27):
    add_phrase(flute, bar*4, CALL if bar in (21,25) else ANSWER, transpose=0, vel=92)
# final return / grin
add_phrase(flute, 31*4, CALL, vel=90)
add_phrase(flute, 33*4, ANSWER, vel=88)
flute += [(35*4+2.0,0.30,81,94),(35*4+2.5,0.25,79,92),(35*4+3.0,0.70,74,96)]

# strings accents, never carpet
for bar in range(8,BARS):
    b=bar*4.0
    if bar % 2 == 0:
        strings += [(b+0.0,0.40,62,58),(b+0.0,0.40,69,52),(b+2.0,0.35,67,54),(b+2.0,0.35,70,48)]
    if bar in (20,24,28,32):
        strings += [(b+3.0,0.65,69,62),(b+3.0,0.65,74,56)]

# piano sparkle only in peak
for bar in range(20,32,2):
    b=bar*4.0
    for off,n in [(0.5,74),(1.5,79),(2.5,81),(3.5,79)]:
        piano.append((b+off,0.18,n,52))

tracks=[
    ("tabla",tabla,9,True),
    ("strand_nylon",gtr,0,False),
    ("crux_bass",bass,1,False),
    ("lucent_flute",flute,2,False),
    ("helix_strings",strings,3,False),
    ("ratio_piano",piano,4,False),
]
for name,ev,ch,perc in tracks:
    midi_file(os.path.join(MIDIDIR,f"HASHTAKA-{name}.mid"),ev,ch,perc)

# --- synth reference ---
stems={k:np.zeros((N,2),dtype=np.float64) for k in ["tabla","gtr","bass","flute","strings","piano"]}

def add(buf, start_s, sig, pan=0.0, gain=1.0):
    i=int(start_s*SR)
    if i>=N: return
    m=min(len(sig),N-i)
    l=math.sqrt((1-pan)*0.5)
    r=math.sqrt((1+pan)*0.5)
    buf[i:i+m,0]+=sig[:m]*gain*l
    buf[i:i+m,1]+=sig[:m]*gain*r

def t_of(beats):
    return beats*60.0/BPM

def env_ar(n, attack=0.01, release=0.12):
    e=np.ones(n)
    a=min(n,max(1,int(attack*SR)))
    r=min(n,max(1,int(release*SR)))
    e[:a]=np.linspace(0,1,a,endpoint=False)
    e[-r:]=np.linspace(1,0,r)
    return e

def pluck(freq,dur,vel):
    n=max(1,int(dur*SR)); tt=np.arange(n)/SR
    s=np.zeros(n)
    for h,a in [(1,1.0),(2,0.45),(3,0.24),(4,0.12),(5,0.07)]:
        s += a*np.sin(2*np.pi*freq*h*tt + h*0.17)
    s *= np.exp(-tt*5.2) * env_ar(n,0.003,0.06)
    return s*(vel/127)*0.18

def basssig(freq,dur,vel):
    n=max(1,int(dur*SR)); tt=np.arange(n)/SR
    s=np.sin(2*np.pi*freq*tt)+0.28*np.sin(4*np.pi*freq*tt)
    s*=np.exp(-tt*1.8)*env_ar(n,0.008,0.08)
    return s*(vel/127)*0.24

def flutesig(freq,dur,vel):
    n=max(1,int((dur+0.10)*SR)); tt=np.arange(n)/SR
    vib=0.0035*np.sin(2*np.pi*5.3*tt)
    phase=2*np.pi*freq*np.cumsum(1+vib)/SR
    s=np.sin(phase)+0.18*np.sin(2*phase)+0.06*np.sin(3*phase)
    breath=np.random.randn(n)*0.018
    s=(s+breath)*env_ar(n,0.045,0.10)
    return s*(vel/127)*0.15

def stringsig(freq,dur,vel):
    n=max(1,int((dur+0.18)*SR)); tt=np.arange(n)/SR
    s=np.zeros(n)
    for h in range(1,7):
        s += (1/h)*np.sin(2*np.pi*freq*h*tt + h*0.31)
    s*=env_ar(n,0.08,0.18)
    return s*(vel/127)*0.075

def pianosig(freq,dur,vel):
    n=max(1,int((dur+0.5)*SR)); tt=np.arange(n)/SR
    s=np.sin(2*np.pi*freq*tt)+0.35*np.sin(4*np.pi*freq*tt)+0.12*np.sin(6*np.pi*freq*tt)
    s*=np.exp(-tt*4.0)*env_ar(n,0.003,0.08)
    return s*(vel/127)*0.12

def dumsig(vel):
    dur=.34; n=int(dur*SR); tt=np.arange(n)/SR
    f=105*np.exp(-tt*4.0)+48
    ph=2*np.pi*np.cumsum(f)/SR
    s=np.sin(ph)*np.exp(-tt*10.0)
    click=np.random.randn(n)*np.exp(-tt*55.0)*0.10
    return (s+click)*(vel/127)*0.40

def taksig(vel):
    dur=.12; n=int(dur*SR); tt=np.arange(n)/SR
    noise=np.random.randn(n)
    ring=np.sin(2*np.pi*760*tt)+0.55*np.sin(2*np.pi*1250*tt)
    s=(0.20*noise+0.80*ring)*np.exp(-tt*36.0)
    return s*(vel/127)*0.24

def clapsig(vel):
    dur=.10; n=int(dur*SR); tt=np.arange(n)/SR
    noise=np.random.randn(n)
    env=np.exp(-tt*30.0)*(1+0.35*np.sin(2*np.pi*28*tt))
    return noise*env*(vel/127)*0.055

# percussion synth
for st,dur,note,vel in tabla:
    sec=t_of(st)
    if note==36: sig=dumsig(vel)
    elif note==38: sig=clapsig(vel)
    else: sig=taksig(vel)
    add(stems["tabla"],sec,sig,pan=-0.02,gain=1.0)

for st,dur,note,vel in gtr:
    add(stems["gtr"],t_of(st),pluck(hz(note),t_of(dur),vel),pan=-0.24)
for st,dur,note,vel in bass:
    add(stems["bass"],t_of(st),basssig(hz(note),t_of(dur),vel),pan=0.0)
for st,dur,note,vel in flute:
    add(stems["flute"],t_of(st),flutesig(hz(note),t_of(dur),vel),pan=0.22)
for st,dur,note,vel in strings:
    add(stems["strings"],t_of(st),stringsig(hz(note),t_of(dur),vel),pan=-0.10)
for st,dur,note,vel in piano:
    add(stems["piano"],t_of(st),pianosig(hz(note),t_of(dur),vel),pan=0.18)

# fixed musical balance, not per-track normalization
mix=(stems["tabla"]*1.00 + stems["gtr"]*0.88 + stems["bass"]*0.80 +
     stems["flute"]*0.95 + stems["strings"]*0.72 + stems["piano"]*0.62)

# mild room-ish echoes on flute/guitar only
for key,delay,gain in [("flute",0.18,0.15),("gtr",0.11,0.10)]:
    sh=int(delay*SR)
    src=stems[key]
    mix[sh:]+=src[:-sh]*gain

# gentle soft-limit and moderate peak (-6 dBFS)
mix=np.tanh(mix*1.08)
peak=float(np.max(np.abs(mix))) or 1.0
mix *= (10**(-6/20))/peak

def write_wav(path,arr):
    arr=np.clip(arr,-1,1)
    pcm=(arr*32767).astype("<i2")
    with wave.open(path,"wb") as w:
        w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR)
        w.writeframes(pcm.tobytes())

for k,arr in stems.items():
    write_wav(os.path.join(RENDERDIR,f"HASHTAKA-stem-{k}.wav"),arr)
write_wav(os.path.join(RENDERDIR,"ZIRYAB-HASHTAKA-sketch01-synth.wav"),mix)

rms=20*math.log10(math.sqrt(float(np.mean(mix**2)))+1e-12)
with open(os.path.join(PROVDIR,"sketch01.txt"),"w",encoding="utf-8") as f:
    f.write(f"title=HASHTAKA\nbpm={BPM}\nbars={BARS}\nduration_s={DUR:.3f}\n")
    f.write(f"mix_peak_dbfs=-6.00\nmix_rms_dbfs={rms:.2f}\n")
    f.write("hook=CALL/ANSWER; phrase mutation over repeated returns\n")
    f.write("tabla=structural leader; maqsum-inspired; micro-breaks and fills\n")
    f.write("numeric_seed=not forced into pitch; kept only as deterministic seed/accent concept\n")
    for name,ev,_,_ in tracks:
        f.write(f"{name}_events={len(ev)}\n")

print("HASHTAKA build complete")
print(os.path.join(RENDERDIR,"ZIRYAB-HASHTAKA-sketch01-synth.wav"))
print("duration",DUR,"rms",rms)
