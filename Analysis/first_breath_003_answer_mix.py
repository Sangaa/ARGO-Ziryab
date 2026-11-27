import wave,os,math,numpy as np
root=r'%ZIRYAB_STUDIO%\Projects\ZRY-FIRST-BREATH-003-FLUTE-ANSWER'
folder=os.path.join(root,'Renders')
names=['Strand_Nylon','Lucent_Flute','Helix_Strings','Ratio_Piano','Crux_JBass']
gains={'Strand_Nylon':-10,'Lucent_Flute':11,'Helix_Strings':3,'Ratio_Piano':0,'Crux_JBass':2}
def load(name):
 p=os.path.join(folder,'ZRY-FIRST-BREATH-003-FLUTE-ANSWER-stem-'+name+'.wav')
 with wave.open(p,'rb') as w:
  assert w.getnchannels()==2 and w.getsampwidth()==3 and w.getframerate()==44100
  frames=w.getnframes()
  b=np.frombuffer(w.readframes(frames),dtype=np.uint8).reshape(-1,3).astype(np.int32)
  u=b[:,0]|(b[:,1]<<8)|(b[:,2]<<16)
  a=np.where(u>=8388608,u-16777216,u).astype(np.float32)/8388608.
 return a,frames
audio={};length=None
for name in names:
 audio[name],n=load(name)
 if length is None:length=n*2
 assert n*2==length
sr=44100; fl=audio['Lucent_Flute'].reshape(-1,2)
# Determine time-varying flute activity in 50ms bins, and softly duck the competing guitar.
win=2205;num=(length//2//win)
levels=np.sqrt(np.mean(fl[:num*win].reshape(num,win,2)**2,axis=(1,2)))
active=np.clip((20*np.log10(np.maximum(levels,1e-10))+68)/16,0,1)
smooth=np.convolve(np.pad(active,(15,15),mode='edge'),np.ones(31,dtype=np.float32)/31,mode='valid')
duck=np.interp(np.arange(length//2)/sr,np.arange(num)*win/sr,smooth,left=0,right=0)
duck_lin=10**((-3.5*duck)/20)
mix=np.zeros(length,dtype=np.float64)
for name in names:
 a=audio[name].astype(np.float64)
 volume=10**(gains[name]/20)
 if name=='Strand_Nylon':a=a.reshape(-1,2)*duck_lin[:,None];a=a.reshape(-1)
 mix+=a*volume
peak=float(np.max(abs(mix)));master=min(1.,10**(-6/20)/peak);mix*=master
dest=os.path.join(folder,'ZRY-FIRST-BREATH-003-FLUTE-ANSWER-LISTENING-DRAFT.wav')
v=np.clip(np.rint(mix*8388607),-8388608,8388607).astype(np.int32)&0xffffff
b=np.empty((len(v),3),dtype=np.uint8);b[:,0]=v&255;b[:,1]=(v>>8)&255;b[:,2]=(v>>16)&255
with wave.open(dest,'wb') as w:w.setparams((2,3,sr,length//2,'NONE','not compressed'));w.writeframes(b.tobytes())
# note activity into last measure
for name in ['Lucent_Flute','Strand_Nylon']:
 a=audio[name].reshape(-1,2).astype(np.float64)
 for t in [54,55,56,62,64,66,67]:
  seg=a[int(t*sr):int((t+1)*sr)]
  rms=np.sqrt(np.mean(seg**2)) if len(seg) else 0
  print('STEM',name,'sec',t,'dBFS',round(20*math.log10(max(rms,1e-10)),1))
print('DRAFT',dest,'duration',length/(2*sr),'peak',round(20*math.log10(np.max(np.abs(mix))),2),'master_gain',round(20*math.log10(master),2),'duck_peak_db',-3.5,'gains',gains)
