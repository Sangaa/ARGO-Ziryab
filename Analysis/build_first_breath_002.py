import os,shutil,struct
from pathlib import Path
src=Path(r'%ZIRYAB_STUDIO%\Projects\ZRY-FIRST-BREATH-001')
dst=Path(r'%ZIRYAB_STUDIO%\Projects\ZRY-FIRST-BREATH-002-PHRASE4')
if dst.exists():
 print('ABORT: destination exists');raise SystemExit(2)
for sub in ['MIDI','Renders','Provenance','Scripts','References']:
 (dst/sub).mkdir(parents=True)
for f in (src/'MIDI').glob('*.mid'): shutil.copy2(f,dst/'MIDI'/f.name)
original=(src/'ZRY-FIRST-BREATH-001.rpp').read_text(encoding='utf-8')
new=original.replace('%ZIRYAB_STUDIO%/Projects/ZRY-FIRST-BREATH-001', '%ZIRYAB_STUDIO%/Projects/ZRY-FIRST-BREATH-002-PHRASE4').replace('ZRY-FIRST-BREATH-001-mix.wav','ZRY-FIRST-BREATH-002-PHRASE4-mix.wav').replace('ZRY-FIRST-BREATH-001','ZRY-FIRST-BREATH-002-PHRASE4')
new=new.replace('RENDER_ENDPOS 70','RENDER_ENDPOS 74')
(dst/'ZRY-FIRST-BREATH-002-PHRASE4.rpp').write_text(new,encoding='utf-8')
def vq(n):
 a=[n&127];n>>=7
 while n:a.insert(0,(n&127)|128);n>>=7
 return bytes(a)
def parse(b):
 header=b[:14]; pos=14;data=[]
 while pos<len(b):
  assert b[pos:pos+4]==b'MTrk'
  ln=int.from_bytes(b[pos+4:pos+8],'big');p=pos+8;end=p+ln;tick=0;running=0;ev=[]
  while p<end:
   n=0
   while 1:
    y=b[p];p+=1;n=(n<<7)|(y&127)
    if y<128:break
   tick+=n;status=b[p]
   if status>=128:p+=1;running=status
   else:status=running
   if status==255:
    typ=b[p];p+=1;k=0
    while 1:
     y=b[p];p+=1;k=(k<<7)|(y&127)
     if y<128:break
    payload=bytes([255,typ])+vq(k)+b[p:p+k];p+=k
   elif status in (240,247):
    k=0
    while 1:
     y=b[p];p+=1;k=(k<<7)|(y&127)
     if y<128:break
    payload=bytes([status])+vq(k)+b[p:p+k];p+=k
   else:
    nbytes=1 if status&240 in (192,208) else 2
    payload=bytes([status])+b[p:p+nbytes];p+=nbytes
   if payload[:2]!=bytes([255,47]):ev.append((tick,payload))
  data.append(ev);pos=end
 return header,data
path=dst/'MIDI'/'NAFAS-flt.mid'
h,tracks=parse(path.read_bytes())
# Phrase 4 transformed callback: ascending fifth+fourth contour from guitar, redistributed to upper flute,
# deliberately lengthened rhythmic intervals; last musical sentence falls to open A rather than tonic D.
notes=[(111.5,112.6,69,73),(113.4,114.4,76,78),(115.3,118.1,81,72),
       (129.1,130.9,74,72),(132.0,134.0,72,66),(135.0,138.5,69,62)]
for start,end,pitch,vel in notes:
 tracks[-1].append((round(start*480),bytes([0x90,pitch,vel])))
 tracks[-1].append((round(end*480),bytes([0x80,pitch,0])))
out=h
for track in tracks:
 track.sort(key=lambda x:(x[0],0 if x[1][0]&0xf0==0x80 else 1))
 last=0;blob=b''
 for tick,event in track:
  blob+=vq(tick-last)+event;last=tick
 blob+=b'\x00\xff\x2f\x00'
 out+=b'MTrk'+len(blob).to_bytes(4,'big')+blob
path.write_bytes(out)
(dst/'Provenance'/'PHRASE4_ARTISTIC_CHANGELOG.txt').write_text('Source ZRY-FIRST-BREATH-001 untouched. New flute additions: transformed phrase 4 (QN 111.5,113.4,115.3); authored ending (QN 129.1,132,135); final A rather than D. Original instruments and source MIDIs otherwise copied unchanged. Awaiting technical render and artistic listening.\n')
print('CREATED',dst,'SIZE RPP',len(new),'FLUTE EXTRA NOTE EVENTS',len(notes))
