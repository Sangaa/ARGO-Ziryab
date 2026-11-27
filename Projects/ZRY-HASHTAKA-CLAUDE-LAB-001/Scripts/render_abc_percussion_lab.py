# -*- coding: utf-8 -*-
import os, sys, json, math, hashlib, wave
import numpy as np
import soundfile as sf
from scipy.signal import butter, sosfilt, lfilter, lfilter_zi
from scipy.ndimage import maximum_filter1d

ROOT = r"%ZIRYAB_STUDIO%\Projects\ZRY-HASHTAKA-CLAUDE-LAB-001"
SRC = os.path.join(ROOT, "Source")
OUT = os.path.join(ROOT, "Renders")
PROV = os.path.join(ROOT, "Provenance")
LISTEN = r"%ZIRYAB_SAMPLES%\HASHTAKA_ABC_LAB"
os.makedirs(OUT, exist_ok=True)
os.makedirs(PROV, exist_ok=True)
os.makedirs(LISTEN, exist_ok=True)

os.chdir(SRC)
sys.path.insert(0, SRC)
import build_hashtaka as H
import tabla as TB

SR = H.SR
N = H.N
END = H.end

OLD = r"%ZIRYAB_STUDIO%\Samples\CC0_Egyptian_Perc"
NEW = r"%ZIRYAB_SAMPLES%\New folder"

def load_mono(path):
    x, sr = sf.read(path, dtype="float64", always_2d=False)
    if x.ndim > 1:
        x = x.mean(axis=1)
    if sr != SR:
        old = np.arange(len(x), dtype=np.float64) / float(sr)
        new = np.arange(int(round(len(x) * SR / float(sr))), dtype=np.float64) / float(SR)
        x = np.interp(new, old, x)
    p = float(np.max(np.abs(x))) if len(x) else 0.0
    if p > 0:
        x = x / p
    return x

samples = {
    "D": [load_mono(os.path.join(NEW, "Darbuka_68_76_SP.wav"))],
    "T": [
        load_mono(os.path.join(OLD, "tak_02_03.flac")),
        load_mono(os.path.join(OLD, "tak_02_07.flac")),
    ],
    "K": [load_mono(os.path.join(NEW, "413798__pjcohen__doumbek_ka2.wav"))],
    "S": [load_mono(os.path.join(NEW, "413781__pjcohen__doumbek_slap1.wav"))],
}

def add(arr, start, sig):
    i = int(round(start * SR))
    if i < 0:
        sig = sig[-i:]
        i = 0
    j = min(len(arr), i + len(sig))
    if j > i:
        arr[i:j] += sig[:j-i]

def timing(bar, slot, stroke):
    jit, vm = H.feel(bar, slot)
    if stroke in ("T", "K"):
        jit -= 0.0032
    return H.t_of(bar, slot) + jit, vm

def real_voice(stroke, bar, slot):
    vv = samples[stroke]
    idx = (int(bar) + int(round(slot * 2))) % len(vv)
    return vv[idx]

def synth_voice(stroke, bar, slot):
    vv = TB.VOICES[stroke]
    idx = (int(bar) + int(round(slot * 2))) % len(vv)
    return vv[idx]

# B: all available real recorded articulation categories.
real_raw = np.zeros(N, dtype=np.float64)
# C: real DUM, original synthetic edge-family strokes.
hybrid_raw = np.zeros(N, dtype=np.float64)

for bar, slot, stroke, vel in H.STROKE_LOG:
    start, vm = timing(bar, slot, stroke)
    gain = H.LVL[stroke] * vel * vm

    rs = real_voice(stroke, bar, slot)
    add(real_raw, start, rs * gain)

    if stroke == "D":
        cs = real_voice("D", bar, slot)
    else:
        cs = synth_voice(stroke, bar, slot)
    add(hybrid_raw, start, cs * gain)

# Same tabla-bus saturation as the control.
B_TAB = np.tanh(real_raw * 1.9) / 1.9
C_TAB = np.tanh(hybrid_raw * 1.9) / 1.9
A_TAB = H.buf["tab"].copy()  # already saturated by the control build

GAIN = H.GAIN
PAN = H.PAN
TARGET_RMS_DB = H.TARGET_RMS_DB
CEIL = H.CEIL

def limit_lr(L, R, pre_db, look=0.0015, rel=0.055):
    g0 = 10 ** (pre_db / 20)
    L2, R2 = L * g0, R * g0
    pk = maximum_filter1d(np.maximum(np.abs(L2), np.abs(R2)), size=int(look * SR) * 2 + 1)
    g = np.minimum(1.0, CEIL / (pk + 1e-9))
    a = np.exp(-1.0 / (rel * SR))
    b, aa = [1-a], [1.0, -a]
    gs, _ = lfilter(b, aa, g, zi=lfilter_zi(b, aa) * g[0])
    g = np.minimum(g, gs)
    return L2*g, R2*g, float(20*np.log10(np.min(g)+1e-9))

def render_mix(tab_bus):
    tracks = {k: (tab_bus if k == "tab" else H.buf[k]) for k in H.buf}
    L = np.zeros(N, dtype=np.float64)
    R = np.zeros(N, dtype=np.float64)
    for k, x in tracks.items():
        g, p = GAIN[k], PAN[k]
        L += x*g*np.sqrt((1-p)/2 + 0.5*(1-abs(p)))
        R += x*g*np.sqrt((1+p)/2 + 0.5*(1-abs(p)))
    sos = butter(2, 28/(SR/2), btype="high", output="sos")
    L, R = sosfilt(sos,L), sosfilt(sos,R)
    L, R = L[:END], R[:END]
    f=np.ones(END)
    f[-int(0.45*SR):]=np.linspace(1,0,int(0.45*SR))
    L*=f; R*=f

    pk0=max(np.max(np.abs(L)),np.max(np.abs(R)))
    L,R=L/pk0*0.90,R/pk0*0.90
    best=None
    for pre in np.arange(0.0,16.1,0.5):
        La,Ra,gr=limit_lr(L,R,pre)
        rms=20*np.log10(np.sqrt(np.mean(((La+Ra)/2)**2))+1e-12)
        if best is None or abs(rms-TARGET_RMS_DB)<abs(best[1]-TARGET_RMS_DB):
            best=(float(pre),float(rms),float(gr))
    L,R,gr=limit_lr(L,R,best[0])
    pk=max(np.max(np.abs(L)),np.max(np.abs(R)))
    tgt=10**(-1.0/20)
    L,R=L/pk*tgt,R/pk*tgt
    return L,R,{"pre_gain_db":best[0],"rms_dbfs":float(20*np.log10(np.sqrt(np.mean(((L+R)/2)**2))+1e-12)),"gain_reduction_db":gr}

def write_wav(path,L,R):
    st=np.empty(len(L)*2,dtype=np.int16)
    st[0::2]=np.clip(L,-1,1)*32767
    st[1::2]=np.clip(R,-1,1)*32767
    with wave.open(path,"wb") as w:
        w.setnchannels(2);w.setsampwidth(2);w.setframerate(SR);w.writeframes(st.tobytes())

def sha256(path):
    h=hashlib.sha256()
    with open(path,"rb") as f:
        for chunk in iter(lambda:f.read(1024*1024),b""):
            h.update(chunk)
    return h.hexdigest()

def phone_survival(L,R):
    mono=(L+R)/2
    sos=butter(4,400/(SR/2),btype="high",output="sos")
    hp=sosfilt(sos,mono)
    return float(20*np.log10((np.sqrt(np.mean(hp**2))+1e-12)/(np.sqrt(np.mean(mono**2))+1e-12)))

def write_tab_stem(path,tab):
    x=tab[:END]*GAIN["tab"]
    # source tabla is centered
    p=float(np.max(np.abs(x))) or 1.0
    x=x/p*(10**(-1/20))
    write_wav(path,x,x)

variants={"A_CONTROL":A_TAB,"B_REAL_SAMPLES":B_TAB,"C_REAL_DUM_SYNTH_EDGES":C_TAB}
report={
    "source_control_expected_sha256":"0b1ff4dc02338016b27831eff7d82850f691f24a2a5ab62c19d4a72fa070744e",
    "score_strokes":len(H.STROKE_LOG),
    "double_hits_preserved":True,
    "mapping":{
        "D":"Darbuka_68_76_SP.wav — DUM-like resonant candidate; user-auditioned as more natural",
        "T":"FreePats tak_02_03.flac / tak_02_07.flac — real TAK category",
        "K":"413798__pjcohen__doumbek_ka2.wav — real KA category; hand not claimed left",
        "S":"413781__pjcohen__doumbek_slap1.wav — real SLAP category; not relabeled SAK"
    },
    "boundary":"B is REAL-SAMPLE CANDIDATE, not a final verified left-hand/closed/slap taxonomy. C changes DUM only and preserves original synthetic edge-family sound.",
    "variants":{}
}

for name,tab in variants.items():
    L,R,met=render_mix(tab)
    project_path=os.path.join(OUT,f"HASHTAKA-{name}.wav")
    listen_path=os.path.join(LISTEN,f"HASHTAKA-{name}.wav")
    write_wav(project_path,L,R)
    write_wav(listen_path,L,R)
    tab_path=os.path.join(OUT,f"HASHTAKA-{name}-TABLA-STEM.wav")
    write_tab_stem(tab_path,tab)
    met.update({
        "sha256":sha256(project_path),
        "phone_survival_db":phone_survival(L,R),
        "project_path":project_path,
        "listen_path":listen_path,
        "tabla_stem":tab_path,
    })
    report["variants"][name]=met

# Confirm rebuilt control is identical to the deterministic source render.
source_a=os.path.join(SRC,"HASHTAKA-sketch01.wav")
report["source_control_actual_sha256"]=sha256(source_a)
report["source_control_matches_documented"]=(report["source_control_actual_sha256"]==report["source_control_expected_sha256"])
report["A_rebuild_matches_source_control"]=(report["variants"]["A_CONTROL"]["sha256"]==report["source_control_actual_sha256"])

with open(os.path.join(PROV,"HASHTAKA_ABC_LAB_REPORT.json"),"w",encoding="utf-8") as f:
    json.dump(report,f,ensure_ascii=False,indent=2)

print(json.dumps(report,ensure_ascii=False,indent=2))
