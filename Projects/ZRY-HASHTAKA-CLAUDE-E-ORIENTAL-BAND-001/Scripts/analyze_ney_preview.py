import numpy as np, soundfile as sf, math, json
from scipy.signal import correlate
from pathlib import Path

p=Path(r"%ZIRYAB_STUDIO%\Instruments\World\Ney_CC0\Ankara-110-Amin-Ney_CC0_preview.mp3")
x,sr=sf.read(p,dtype="float64",always_2d=True)
x=x.mean(axis=1)
# remove DC
x=x-np.mean(x)
win=4096
hop=1024
minf,maxf=140,1000
minlag=int(sr/maxf)
maxlag=int(sr/minf)
frames=[]
for i in range(0,len(x)-win,hop):
    y=x[i:i+win]
    rms=float(np.sqrt(np.mean(y*y)))
    if rms<0.005:
        frames.append((i/sr,None,rms,0.0)); continue
    y=y*np.hanning(win)
    ac=correlate(y,y,mode="full",method="fft")[win-1:]
    ac0=ac[0]+1e-12
    seg=ac[minlag:maxlag+1]
    k=int(np.argmax(seg))+minlag
    q=float(ac[k]/ac0)
    # parabolic refine
    lag=float(k)
    if 1<=k<len(ac)-1:
        a,b,c=ac[k-1],ac[k],ac[k+1]
        den=(a-2*b+c)
        if abs(den)>1e-12:
            lag=k+0.5*(a-c)/den
    f=sr/lag
    midi=69+12*math.log2(f/440.0)
    frames.append((i/sr,midi,rms,q))

# group stable high-confidence frames close in pitch
segments=[]
cur=[]
for fr in frames:
    t,m,r,q=fr
    good=(m is not None and q>0.35 and 42<m<90)
    if not good:
        if cur: segments.append(cur); cur=[]
        continue
    if cur and abs(m-cur[-1][1])>0.65:
        segments.append(cur); cur=[]
    cur.append(fr)
if cur:segments.append(cur)

summ=[]
for seg in segments:
    if len(seg)<3: continue
    ts=[z[0] for z in seg]; ms=[z[1] for z in seg]; qs=[z[3] for z in seg]
    dur=(len(seg)-1)*hop/sr+win/sr
    med=float(np.median(ms))
    spread=float(np.percentile(ms,90)-np.percentile(ms,10))
    summ.append({
      "start":round(ts[0],3),"end":round(ts[-1]+win/sr,3),"duration":round(dur,3),
      "midi_med":round(med,3),"note_nearest":int(round(med)),
      "spread_semitones":round(spread,3),"quality":round(float(np.mean(qs)),3)
    })
summ=sorted(summ,key=lambda z:(z["duration"],-z["spread_semitones"]),reverse=True)
print(json.dumps(summ[:20],indent=2))
(Path(r"%ZIRYAB_STUDIO%\Projects\ZRY-HASHTAKA-CLAUDE-E-ORIENTAL-BAND-001\Provenance")/"ney_pitch_segments.json").write_text(json.dumps(summ,indent=2),encoding="utf-8")
