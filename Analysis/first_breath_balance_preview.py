import wave, os, numpy as np, math
p=r'%ZIRYAB_STUDIO%\Projects\ZRY-FIRST-BREATH-001'
folder=os.path.join(p,'Renders'); out=os.path.join(folder,'Preview')
os.makedirs(out,exist_ok=True)
names=['Strand_Nylon','Lucent_Flute','Helix_Strings','Ratio_Piano','Crux_JBass']
db={'Strand_Nylon':-9,'Lucent_Flute':10,'Helix_Strings':5,'Ratio_Piano':2,'Crux_JBass':4}
files={name:wave.open(os.path.join(folder,'ZRY-FIRST-BREATH-001-stem-'+name+'.wav'),'rb') for name in names}
assert len({(f.getnframes(),f.getframerate(),f.getnchannels(),f.getsampwidth()) for f in files.values()})==1
frames=next(iter(files.values())).getnframes()
def decode(raw):
 a=np.frombuffer(raw,dtype=np.uint8).reshape(-1,3).astype(np.int32)
 v=a[:,0]|(a[:,1]<<8)|(a[:,2]<<16)
 return np.where(v>=8388608,v-16777216,v).astype(np.float64)/8388608
def encode(v):
 v=np.clip(np.rint(v*8388607),-8388608,8388607).astype(np.int32).reshape(-1)
 u=(v&16777215).astype(np.uint32); a=np.empty((len(u),3),dtype=np.uint8)
 a[:,0]=u&255;a[:,1]=(u>>8)&255;a[:,2]=(u>>16)&255
 return a.tobytes()
inputs={name:decode(f.readframes(frames)) for name,f in files.items()}
for f in files.values():f.close()
mix=sum(inputs[name]*10**(db[name]/20) for name in names)
peak=float(np.max(np.abs(mix))); target=10**(-6/20); factor=min(1,target/max(peak,1e-20))
mix*=factor
dest=os.path.join(out,'FIRST_BREATH_BALANCE_DIAGNOSTIC_NOT_MASTER.wav')
with wave.open(dest,'wb') as w:
 w.setparams((2,3,44100,frames,'NONE','not compressed'));w.writeframes(encode(mix))
print('PREVIEW',dest,'seconds',frames/44100,'raw_peak',peak,'global_gain_db',round(20*math.log10(factor),2),'output_peak_db',round(20*math.log10(np.max(np.abs(mix))),2))
print('GAINS_DB',db)
print('Original renders unchanged; this is an experimental balance-only preview, not a final fix.')
