import numpy as np, soundfile as sf, json, os
raw=r"%ZIRYAB_STUDIO%\Projects\ZRY-HASHTAKA-CLAUDE-D-REAL-BAND-001\Renders\HASHTAKA-D_REAL_BAND_RAW-v2.wav"
tab=r"%ZIRYAB_STUDIO%\Projects\ZRY-HASHTAKA-CLAUDE-LAB-001\Renders\HASHTAKA-B_REAL_SAMPLES-TABLA-STEM.wav"
out=r"%ZIRYAB_SAMPLES%\HASHTAKA_ABC_LAB\HASHTAKA-D_REAL_BAND-SAME_MELODY-v2.wav"
x,sr=sf.read(raw,dtype="float64",always_2d=True)
t,srt=sf.read(tab,dtype="float64",always_2d=True)
n=min(len(x),len(t))
xm=x[:n].mean(axis=1); tm=t[:n].mean(axis=1)
a=float(np.dot(xm,tm)/(np.dot(tm,tm)+1e-30))
res=xm-a*tm
xr=float(np.sqrt(np.mean(xm*xm))); rr=float(np.sqrt(np.mean(res*res)))
pk=float(np.max(np.abs(x)))
gain=(10**(-1/20))/(pk+1e-30)
y=x*gain
sf.write(out,y,sr,subtype="PCM_24")
rep={
 "raw_peak_db":float(20*np.log10(pk+1e-30)),
 "raw_rms_db":float(20*np.log10(xr+1e-30)),
 "normalize_gain_db":float(20*np.log10(gain)),
 "final_peak_db":float(20*np.log10(np.max(np.abs(y))+1e-30)),
 "final_rms_db":float(20*np.log10(np.sqrt(np.mean((y.mean(axis=1))**2))+1e-30)),
 "best_fit_tabla_scalar":a,
 "non_tabla_residual_ratio":rr/(xr+1e-30),
 "non_tabla_residual_db_relative_mix":float(20*np.log10(rr/(xr+1e-30)+1e-30)),
 "output":out
}
print(json.dumps(rep,indent=2))
