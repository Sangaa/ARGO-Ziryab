import struct,glob,os
root=r'%ZIRYAB_STUDIO%\Projects\ZRY-FIRST-BREATH-001\MIDI'
def vlq(b,i):
 v=0
 while 1:
  z=b[i];i+=1;v=(v<<7)|(z&127)
  if z<128:return v,i
def parse(path):
 b=open(path,'rb').read();div=int.from_bytes(b[12:14],'big');i=14;notes=[];on={};tempo=[]
 while i<len(b):
  if b[i:i+4]!=b'MTrk':break
  length=int.from_bytes(b[i+4:i+8],'big');end=i+8+length;i+=8;t=0;run=0
  while i<end:
   d,i=vlq(b,i);t+=d;status=b[i]
   if status&128:i+=1;run=status
   else: status=run
   if status==255:
    typ=b[i];i+=1;l,i=vlq(b,i);dat=b[i:i+l];i+=l
    if typ==81:tempo.append((t,int.from_bytes(dat,'big')))
    continue
   if status in (240,247):
    l,i=vlq(b,i);i+=l;continue
   n=1 if status&240 in (192,208) else 2
   data=b[i:i+n];i+=n
   if status&240==144 and data[1]:on.setdefault((status&15,data[0]),[]).append((t,data[1]))
   if status&240==128 or (status&240==144 and data[1]==0):
    key=(status&15,data[0])
    if on.get(key):
     t0,v=on[key].pop(0);notes.append((t0/div,t/div,data[0],v))
  i=end
 return div,sorted(notes),tempo
for f in sorted(glob.glob(root+r'\*.mid')):
 div,notes,tempo=parse(f)
 print('\n',os.path.basename(f),'notes',len(notes),'division',div,'tempo',tempo)
 for s,e,n,v in notes:print('%5.1f - %5.1f : %3d vel %d'%(s,e,n,v))
