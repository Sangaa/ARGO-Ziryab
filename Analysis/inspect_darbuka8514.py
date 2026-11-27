import os,glob,soundfile as sf,numpy as np,hashlib,json
from pathlib import Path
root=Path(r'%ZIRYAB_SAMPLES%\Darbuka8514\Darbuka8514')
rows=[]
for p in sorted(root.glob('*.wav')):
 a,sr=sf.read(str(p),always_2d=True)
 m=a.mean(axis=1); n=len(m);peak=float(abs(a).max());rms=float(np.sqrt(np.mean(a*a)))
 # 10ms moving rms, early strike, tail, spectral center
 hop=max(1,int(sr*.01));en=np.array([np.sqrt(np.mean(m[k:k+hop]**2)) for k in range(0,n,hop)])
 threshold=max(.003, float(en.max())*.04)
 inds=np.where(en>threshold)[0];length=round((inds[-1]-inds[0])*0.01,3) if len(inds) else 0
 i=int(np.argmax(en))*hop
 seg=m[i:min(n,i+int(sr*.14))]
 window=np.hanning(len(seg));spec=abs(np.fft.rfft(seg*window));freq=np.fft.rfftfreq(len(seg),1/sr)
 centroid=float(np.sum(freq*spec)/(np.sum(spec)+1e-12))
 lo=float(np.sum(spec[freq<250]**2)/(np.sum(spec**2)+1e-12))
 hi=float(np.sum(spec[freq>2000]**2)/(np.sum(spec**2)+1e-12))
 rows.append(dict(file=p.name,sr=sr,channels=a.shape[1],duration=round(n/sr,2),peak_db=round(20*np.log10(max(peak,1e-10)),1),rms_db=round(20*np.log10(max(rms,1e-10)),1),tail=length,centroid=int(centroid),low_frac=round(lo,3),high_frac=round(hi,3),sha256=hashlib.sha256(p.read_bytes()).hexdigest()))
for x in rows:print(f"{x['file']:22s} {x['duration']:5.2f}s pk{x['peak_db']:5.1f} rms{x['rms_db']:5.1f} tail{x['tail']:4.2f} cent{x['centroid']:5d} bass{x['low_frac']:.2f} hi{x['high_frac']:.2f}")
out=Path(r'%ZIRYAB_STUDIO%\Analysis\Tabla_Articulation_Audit_20261011');out.mkdir(exist_ok=True,parents=True);(out/'Darbuka8514_inventory.json').write_text(json.dumps(rows,indent=2),encoding='utf8')
