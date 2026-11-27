import os,glob,json,hashlib,numpy as np,soundfile as sf
from pathlib import Path
root=Path(r'%ZIRYAB_STUDIO%\Samples\CC0_Egyptian_Perc')
out=Path(r'%ZIRYAB_STUDIO%\Analysis\Tabla_Articulation_Audit_20261011')
out.mkdir(parents=True,exist_ok=True)
data=[];pieces=[];sr_out=44100
for label,pattern in [('DUM_OPEN','doom_*.flac'),('TAK_RIGHT','tak_*.flac'),('PA_UNCLASSIFIED','pa_*.flac')]:
 files=sorted(root.glob(pattern))
 for f in files:
  a,sr=sf.read(str(f),dtype='float64',always_2d=True)
  mono=np.mean(a,axis=1);peak=float(np.max(np.abs(a)));rms=float(np.sqrt(np.mean(a*a)))
  # last position above -50 dBFS as coarse tail estimate
  above=np.where(abs(mono)>0.0031623)[0]
  tail=(float(above[-1]/sr) if above.size else 0.0)
  data.append(dict(candidate_label=label,filename=f.name,source_path=str(f),sha256=hashlib.sha256(f.read_bytes()).hexdigest(),sample_rate=sr,channels=a.shape[1],duration_sec=round(len(a)/sr,4),peak=round(peak,7),rms=round(rms,7),tail_above_minus50_db_sec=round(tail,4),clipped_samples=int(np.count_nonzero(abs(a)>=.9999)),normalization_applied=False,authenticity_note='Source articulation label only; hand and precise style not acoustically verified'))
 # Audition 3 available per class; no proxies for missing labels
 for f in files[:3]:
  a,sr=sf.read(str(f),dtype='float64',always_2d=True)
  if sr!=sr_out:
   a=np.column_stack([np.interp(np.arange(int(len(a)*sr_out/sr))/sr_out,np.arange(len(a))/sr,a[:,j]) for j in range(a.shape[1])])
  mono=np.mean(a,axis=1)
  pieces.extend([mono,np.zeros(int(.60*sr_out))])
audio=np.concatenate(pieces) if pieces else np.zeros(1)
peak=float(np.max(abs(audio)))
if peak>0.97: audio*=.97/peak
aud=out/'EXISTING_DUM_TAK_PA_AUDITION_NOT_KAH_SAK.wav'
sf.write(str(aud),audio,sr_out,subtype='PCM_24')
mapping={'status':'GAP_CONFIRMED_LOCAL_AUDIT','note':'Filename labels not equivalent to independent acoustic authenticity or verified left/right hand. PA is NOT SAK. TAK is NOT KAH.', 'available_candidates':{'DUM_OPEN':[x['source_path'] for x in data if x['candidate_label']=='DUM_OPEN'],'TAK_RIGHT':[x['source_path'] for x in data if x['candidate_label']=='TAK_RIGHT'],'PA_UNCLASSIFIED':[x['source_path'] for x in data if x['candidate_label']=='PA_UNCLASSIFIED']},'missing_verified': ['KAH_LEFT','DUM_CLOSED','SAK_MUTED_SLAP'],'engine':{'DUM_OPEN':{'hand':'unspecified','velocity':'separate','default_gain_db_range':[-3,0],'tail':'natural'},'TAK_RIGHT':{'hand':'unverified_right','velocity':'separate','default_gain_db_range':[-3,0],'tail':'natural'},'KAH_LEFT':None,'DUM_CLOSED':None,'SAK_MUTED_SLAP':None},'audit_file':'tabla_candidates.json','audition_file':str(aud),'audition_sequence':'3 DUM, 3 TAK, 3 PA; each hit isolated; PA explicitly unclassified'}
(out/'tabla_candidates.json').write_text(json.dumps(data,indent=2),encoding='utf-8')
(out/'engine_mapping.json').write_text(json.dumps(mapping,indent=2),encoding='utf-8')
print('AUDIT',len(data),'AUDITION',aud,'secs',round(len(audio)/sr_out,2),'peak',round(float(np.max(abs(audio))),5),'sample_rates',sorted(set(x['sample_rate'] for x in data)))
