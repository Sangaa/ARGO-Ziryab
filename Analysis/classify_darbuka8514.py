import json,os,numpy as np,soundfile as sf
from pathlib import Path
src=Path(r'%ZIRYAB_SAMPLES%\Darbuka8514\Darbuka8514')
dst=Path(r'%ZIRYAB_STUDIO%\Analysis\Tabla_Articulation_Audit_20261011')
rows=json.loads((dst/'Darbuka8514_inventory.json').read_text())
for x in rows:
 if x['low_frac']>=.75 and x['tail']>=.27: k='A_BASS_RESONANT_DUM_CANDIDATE'
 elif x['low_frac']>=.60: k='B_BASS_SHORT_OR_MUTED_CANDIDATE'
 elif x['low_frac']<.30 and x['tail']<=.25: k='C_SHARP_DRY_TAK_SAK_CANDIDATE'
 elif x['low_frac']<.30:k='D_SHARP_RESONANT_TAK_KAH_CANDIDATE'
 else:k='E_MIXED_AMBIGUOUS'
 x['acoustic_bucket']=k
 x['verified_articulation']=None
 x['verified_hand']=None
 x['classification_scope']='spectral and transient candidate only, not performer technique'
buckets={}
for r in rows:buckets.setdefault(r['acoustic_bucket'],[]).append(r)
allparts=[];listing=[];srout=44100;cursor=0
for label,group in sorted(buckets.items()):
 for r in group:
  y,sr=sf.read(str(src/r['file']),always_2d=True);y=y.mean(axis=1)
  if sr!=srout:
   count=int(len(y)*srout/sr);y=np.interp(np.arange(count)/srout,np.arange(len(y))/sr,y)
  # preserve natural dynamics, no normalization; source includes long silence, use first 0.9s only
  seg=y[:int(srout*.95)]
  allparts.extend([seg,np.zeros(int(srout*.35))])
  listing.append(dict(start_sec=round(cursor/srout,2),file=r['file'],group=label))
  cursor+=len(seg)+int(srout*.35)
wav=dst/'Darbuka8514_CLASSIFIED_CANDIDATES_AUDITION.wav'
out=np.concatenate(allparts)
sf.write(str(wav),out,srout,subtype='PCM_24')
(dst/'Darbuka8514_classification.json').write_text(json.dumps({'classification':'PROVISIONAL ACOUSTIC ONLY','source_directory':str(src),'source_files_unmodified':True,'samples':rows,'audition_timeline':listing},indent=2),encoding='utf8')
lines=['Darbuka8514 audition — PROVISIONAL acoustic groupings, NOT authentic technique labels','Source files untouched; no per-hit normalization. WAV is 44.1 kHz, 24-bit mono.','']
for k,g in sorted(buckets.items()):
 lines.append(k+' ('+str(len(g))+')')
 for z in g:lines.append('    '+z['file']+' | bass='+str(z['low_frac'])+' tail='+str(z['tail'])+'s')
lines+=['','Audit: no filename or audio statistics establish left-hand KAH, closed DUM, or muted SAK. These are candidates requiring ears and provenance.']
(dst/'Darbuka8514_README.txt').write_text('\n'.join(lines),encoding='utf8')
print('\n'.join(lines));print('AUDITION',wav,'SEC',round(len(out)/srout,2))
