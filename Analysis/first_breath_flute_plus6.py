import wave,os,numpy as np,math
root=r'%ZIRYAB_STUDIO%\Projects\ZRY-FIRST-BREATH-001\Renders'
preview=os.path.join(root,'Preview')
base=os.path.join(preview,'FIRST_BREATH_BALANCE_DIAGNOSTIC_NOT_MASTER.wav')
flute=os.path.join(root,'ZRY-FIRST-BREATH-001-stem-Lucent_Flute.wav')
def read(p):
 with wave.open(p,'rb') as w:
  prm=w.getparams();raw=w.readframes(w.getnframes())
 a=np.frombuffer(raw,dtype=np.uint8).reshape(-1,3).astype(np.int32)
 u=a[:,0]|(a[:,1]<<8)|(a[:,2]<<16)
 return prm,np.where(u>=8388608,u-16777216,u).astype(np.float64)/8388608.
def pack(a):
 u=np.clip(np.rint(a*8388607),-8388608,8388607).astype(np.int32)&0xffffff
 b=np.empty((u.size,3),dtype=np.uint8);b[:,0]=u&255;b[:,1]=(u>>8)&255;b[:,2]=(u>>16)&255
 return b.tobytes()
p,m=read(base);q,f=read(flute);assert p.nframes==q.nframes and p.nchannels==q.nchannels and p.framerate==q.framerate
old=10**(10/20)*10**(-3.58/20)
# Add +6dB above the prior diagnostic flute contribution, keeping all other stems identical
v=m+f*old*(10**(6/20)-1)
target=10**(-6/20);peak=np.max(abs(v));factor=min(1.,target/max(peak,1e-9));v*=factor
dest=os.path.join(preview,'FIRST_BREATH_FLUTE_PLUS6_DIAGNOSTIC_NOT_MASTER.wav')
with wave.open(dest,'wb') as w:w.setparams(p);w.writeframes(pack(v))
print('CREATED',dest,'PEAK_DBFS',round(20*math.log10(np.max(abs(v))),2),'SAFETY_GAIN_DB',round(20*math.log10(factor),3))
