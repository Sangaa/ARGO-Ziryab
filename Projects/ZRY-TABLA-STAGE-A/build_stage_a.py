import os, math, json
import numpy as np
import soundfile as sf

SR=48000
BPM=60
SLOT=60.0/BPM/4.0       # 1/16 = 250 ms
DURATION=300.0          # 5 minutes
SAMPLES=r"%ZIRYAB_STUDIO%\Samples\CC0_Egyptian_Perc"
OUT=r"%ZIRYAB_STUDIO%\Projects\ZRY-TABLA-STAGE-A"

def load(name):
    x,sr=sf.read(os.path.join(SAMPLES,name),dtype="float32",always_2d=False)
    if x.ndim>1:
        x=x.mean(axis=1)
    if sr!=SR:
        old=np.arange(len(x),dtype=np.float64)/sr
        new=np.arange(int(round(len(x)*SR/sr)),dtype=np.float64)/SR
        x=np.interp(new,old,x).astype(np.float32)
    return x.astype(np.float64)

def trim(x,secs=.18):
    y=x[:min(len(x),int(secs*SR))].copy()
    f=min(len(y),int(.045*SR))
    if f>1:
        y[-f:]*=np.linspace(1,0,f)
    return y

# Available library has DUM / TAK / PA only.
# For Stage A, use two different TAK takes as right/left EDGE-STROKE PROXIES.
# This is a timing/control diagnostic, NOT a claim that the second take is an authentic KAH sample.
T=trim(load("tak_02_03.flac"))
K=trim(load("tak_02_05.flac"))

def rms(x):
    return float(np.sqrt(np.mean(np.square(x))+1e-15))
def db(x):
    return 20.0*math.log10(max(x,1e-15))

T_rms=rms(T); K_rms=rms(K)
raw_diff_db=db(K_rms/T_rms)

# Same input gain on both sides: Stage A diagnoses natural source imbalance.
GAIN=.46
N=int((DURATION+1.0)*SR)
L=np.zeros(N,dtype=np.float64)
R=np.zeros(N,dtype=np.float64)

def add(sample,t,g,pan):
    i=int(round(t*SR))
    m=min(len(sample),N-i)
    if m<=0: return
    y=sample[:m]*g
    lg=math.sqrt((1.0-pan)*0.5)
    rg=math.sqrt((1.0+pan)*0.5)
    L[i:i+m]+=y*lg
    R[i:i+m]+=y*rg

# Very quiet metronome cue on quarter notes (slots 1,5,9,13).
# Synthetic short click, deliberately low so it guides without masking T/K.
click_len=int(.025*SR)
t=np.arange(click_len)/SR
click=np.sin(2*np.pi*1900*t)*np.exp(-t*120)
click*=0.10

hits=int(DURATION/SLOT)  # 1200 alternating strokes
for n in range(hits):
    ts=n*SLOT
    if n%2==0:
        add(T,ts,GAIN,+0.035)  # T right proxy
    else:
        add(K,ts,GAIN,-0.035)  # K left proxy
    if n%4==0:
        add(click,ts,1.0,0.0)

mix=np.stack([L,R],axis=1)
peak=float(np.max(np.abs(mix))) or 1.0
target=10**(-8/20)
mix*=target/peak

name="ZIRYAB-STAGE-A-TK-5MIN-60BPM.wav"
wav=os.path.join(OUT,name)
desk=os.path.join(os.path.expanduser("~"),"Desktop",name)
sf.write(wav,mix,SR,subtype="PCM_24")
sf.write(desk,mix,SR,subtype="PCM_24")

report={
    "stage":"A - Rim Balance",
    "bpm":BPM,
    "grid":"1/16",
    "slot_ms":SLOT*1000,
    "duration_seconds":DURATION,
    "strokes":hits,
    "pattern":"T K T K continuous",
    "metronome":"quarter-note click on slots 1,5,9,13",
    "input_gain_T":GAIN,
    "input_gain_K":GAIN,
    "T_source":"tak_02_03.flac",
    "K_source":"tak_02_05.flac (KAH proxy only; authentic KAH sample not present)",
    "T_sample_rms":T_rms,
    "K_sample_rms":K_rms,
    "K_minus_T_raw_rms_db":raw_diff_db,
    "timing_humanization_ms":0,
    "ornaments":0,
    "dum":0,
    "ghosts":0,
    "rolls":0
}
with open(os.path.join(OUT,"STAGE-A-DIAGNOSTIC.json"),"w",encoding="utf-8") as f:
    json.dump(report,f,ensure_ascii=False,indent=2)

print(json.dumps(report,ensure_ascii=False,indent=2))
print("WAV",wav)
print("DESKTOP",desk)
