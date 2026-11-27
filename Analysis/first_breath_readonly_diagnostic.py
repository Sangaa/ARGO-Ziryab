import os,wave,glob,struct,numpy as np
root=r'%ZIRYAB_STUDIO%\Projects\ZRY-FIRST-BREATH-001'
def vlq(b,i):
 v=0
 while True:
  x=b[i];i+=1;v=(v<<7)|(x&127)
  if x<128:return v,i
def midi(path):
 b=open(path,'rb').read();i=14;events=[];division=int.from_bytes(b[12:14],'big')
 while i<len(b):
  if b[i:i+4]!=b'MTrk':break
  sz=int.from_bytes(b[i+4:i+8],'big');end=i+8+sz;i+=8;tick=0;running=0
  while i<end:
   delta,i=vlq(b,i);tick+=delta;status=b[i]
   if status&128:i+=1;running=status
   else:status=running
   if status==255:
    typ=b[i];i+=1;size,i=vlq(b,i);i+=size;continue
   if status in (240,247):
    size,i=vlq(b,i);i+=size;continue
   size=1 if status&240 in (192,208) else 2
   data=b[i:i+size];i+=size
   if status&240==144 and len(data)==2 and data[1]:events.append((round(tick/division*60/123,3),data[0],data[1]))
  i=end
 return division,events
for f in sorted(glob.glob(root+r'\MIDI\*.mid')):
 div,ev=midi(f);print('MIDI',os.path.basename(f),'division',div,'notes',len(ev),'first',ev[:6],'last',ev[-3:])
for f in sorted(glob.glob(root+r'\Renders\*.wav')):
 with wave.open(f,'rb') as w:
  raw=w.readframes(w.getnframes());a=np.frombuffer(raw,dtype=np.uint8).reshape(-1,3).astype(np.int32);val=a[:,0]|(a[:,1]<<8)|(a[:,2]<<16);val=np.where(val>=8388608,val-16777216,val)/8388608.;sr=w.getframerate(); sec=val.reshape(-1,2)
  rms=np.sqrt(np.mean(sec**2));peak=np.max(np.abs(sec))
  rmssec=[round(20*np.log10(max(1e-9,np.sqrt(np.mean(sec[t*sr:(t+1)*sr]**2)))),1) for t in range(0,66,5)]
  print('AUDIO',os.path.basename(f),'rmsdb',round(20*np.log10(max(rms,1e-9)),1),'peakdb',round(20*np.log10(max(peak,1e-9)),1),'rms at 0,5,...65s',rmssec)
