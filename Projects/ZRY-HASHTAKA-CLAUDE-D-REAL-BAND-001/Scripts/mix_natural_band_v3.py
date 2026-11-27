import numpy as np, soundfile as sf, os, json, math

mel=r"%ZIRYAB_STUDIO%\Projects\ZRY-HASHTAKA-CLAUDE-D-REAL-BAND-001\Renders\DIAG-MELODY-ONLY.wav"
tab=r"%ZIRYAB_STUDIO%\Projects\ZRY-HASHTAKA-CLAUDE-LAB-001\Renders\HASHTAKA-B_REAL_SAMPLES-TABLA-STEM.wav"
out=r"%ZIRYAB_SAMPLES%\HASHTAKA_ABC_LAB\HASHTAKA-D_REAL_BAND-SAME_SCORE-v3.wav"
prov=r"%ZIRYAB_STUDIO%\Projects\ZRY-HASHTAKA-CLAUDE-D-REAL-BAND-001\Provenance\D_REAL_BAND_v3.json"

m,sr=sf.read(mel,dtype="float64",always_2d=True)
t,srt=sf.read(tab,dtype="float64",always_2d=True)
assert sr==srt
if t.shape[1]==1:
    t=np.repeat(t,2,axis=1)
N=max(len(m),len(t))
mm=np.zeros((N,2)); tt=np.zeros((N,2))
mm[:len(m),:]=m[:,:2]
tt[:len(t),:]=t[:,:2]

# Match Claude's original tabla share of mix energy (37.4%) as a neutral starting balance.
Em=float(np.mean(mm**2))
Et=float(np.mean(tt**2))
share=0.374
scale=math.sqrt((share/(1-share))*Em/(Et+1e-30))
tt2=tt*scale
mix=mm+tt2

pk=float(np.max(np.abs(mix)))
gain=(10**(-1/20))/(pk+1e-30)
y=mix*gain
sf.write(out,y,sr,subtype="PCM_24")

Ems=float(np.mean((mm*gain)**2))
Ets=float(np.mean((tt2*gain)**2))
actual=Ets/(Ems+Ets+1e-30)
mono=y.mean(axis=1)
rep={
 "same_score":True,
 "melody_source":"REAPER/SINE natural instruments: Strand Nylon, Lucent Flute, Helix Strings, Ratio Piano, Crux JBass",
 "tabla_source":"B real-sample tabla stem",
 "target_tabla_energy_share":share,
 "actual_component_energy_share_tabla":actual,
 "tabla_scale_before_master":scale,
 "master_peak_normalize_gain_db":20*math.log10(gain),
 "final_peak_dbfs":20*math.log10(float(np.max(np.abs(y)))+1e-30),
 "final_rms_dbfs":20*math.log10(float(np.sqrt(np.mean(mono**2)))+1e-30),
 "output":out,
 "note":"No melody-note changes. No correction of the known duplicate-hit score defect."
}
os.makedirs(os.path.dirname(prov),exist_ok=True)
with open(prov,"w",encoding="utf-8") as f: json.dump(rep,f,ensure_ascii=False,indent=2)
print(json.dumps(rep,ensure_ascii=False,indent=2))
