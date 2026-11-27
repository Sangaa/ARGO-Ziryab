import glob,os,hashlib,json,numpy as np,soundfile as sf
from pathlib import Path
src=Path(r'%ZIRYAB_SAMPLES%\New folder')
rows=[]
for f in sorted(src.glob('*.wav')):
 a,sr=sf.read(str(f),always_2d=True);m=a.mean(axis=1)
 rms=float(np.sqrt(np.mean(a*a)));peak=float(np.max(abs(a)))
 win=max(1,int(sr*.01));energy=np.array([np.sqrt(np.mean(m[i:i+win]**2)) for i in range(0,len(m),win)])
 ix=np.where(energy>max(.003,.04*energy.max()))[0]
 tail=round((ix[-1]-ix[0])*.01,3) if len(ix) else 0
 y=m[int(np.argmax(energy))*win:][:int(.12*sr)];F=abs(np.fft.rfft(y*np.hanning(len(y))))**2;hz=np.fft.rfftfreq(len(y),1/sr)
 lo=float(F[hz<250].sum()/max(F.sum(),1e-20))
 d={'name':f.name,'sr':sr,'channels':a.shape[1],'length_sec':round(len(m)/sr,3),'peak_dbfs':round(20*np.log10(max(peak,1e-10)),2),'rms_dbfs':round(20*np.log10(max(rms,1e-10)),2),'tail_sec':tail,'bass_energy_ratio':round(lo,3),'sha256':hashlib.sha256(f.read_bytes()).hexdigest()}
 rows.append(d);print(d)
dst=Path(r'%ZIRYAB_STUDIO%\Analysis\Tabla_Articulation_Audit_20261011')
(dst/'new_folder_4_candidates.json').write_text(json.dumps(rows,indent=2),encoding='utf8')
