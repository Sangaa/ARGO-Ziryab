import os,shutil,importlib.util
from pathlib import Path
base=Path(r'%ZIRYAB_STUDIO%\Projects\ZRY-FIRST-BREATH-002-PHRASE4')
dest=Path(r'%ZIRYAB_STUDIO%\Projects\ZRY-FIRST-BREATH-003-FLUTE-ANSWER')
first=Path(r'%ZIRYAB_STUDIO%\Projects\ZRY-FIRST-BREATH-001')
if dest.exists():raise SystemExit('Destination already exists')
for directory in ['MIDI','Scripts','Renders','Provenance']:
 (dest/directory).mkdir(parents=True)
for f in (base/'MIDI').glob('*.mid'):shutil.copy2(f,dest/'MIDI'/f.name)
# Rebuild flute from the ORIGINAL MIDI and exactly repeat its first three note events.
spec=importlib.util.spec_from_file_location('builder',r'%ZIRYAB_STUDIO%\Analysis\build_first_breath_002.py')
# Avoid importing since it executes the original build.
code=Path(r'%ZIRYAB_STUDIO%\Analysis\build_first_breath_002.py').read_text()
start=code.index('def vq(n):')
end=code.index("path=dst/'MIDI'/'NAFAS-flt.mid'")
ns={};exec(code[start:end],ns)
vq,parse=ns['vq'],ns['parse']
header,tracks=parse((first/'MIDI'/'NAFAS-flt.mid').read_bytes())
# First flute phrase: D5 Eb5 D5; QN 25,26,27. Replay exactly with same velocities and durations.
firstnotes=[(25,26.4,74,96),(26,27.1,75,96),(27,28.8,74,96)]
shift=86.5
tail=[(129.1,130.9,74,72),(132,134,72,66),(135,138.5,69,62)]
for t0,t1,p,v in [(a+shift,b+shift,p,v) for a,b,p,v in firstnotes]+tail:
 tracks[-1].append((round(t0*480),bytes([0x90,p,v])))
 tracks[-1].append((round(t1*480),bytes([0x80,p,0])))
data=header
for track in tracks:
 track.sort(key=lambda x:(x[0],0 if x[1][0]&240==128 else 1))
 last=0;blob=b''
 for t,e in track:blob+=vq(t-last)+e;last=t
 blob+=b'\x00\xff\x2f\x00'
 data+=b'MTrk'+len(blob).to_bytes(4,'big')+blob
(dest/'MIDI'/'NAFAS-flt.mid').write_bytes(data)
rpp=(base/'ZRY-FIRST-BREATH-002-PHRASE4.rpp').read_text(encoding='utf8')
rpp=rpp.replace('ZRY-FIRST-BREATH-002-PHRASE4','ZRY-FIRST-BREATH-003-FLUTE-ANSWER')
(dest/'ZRY-FIRST-BREATH-003-FLUTE-ANSWER.rpp').write_text(rpp,encoding='utf8')
lua=(base/'Scripts'/'render_first_breath_v2.lua').read_text(encoding='utf8')
lua=lua.replace('ZRY-FIRST-BREATH-002-PHRASE4','ZRY-FIRST-BREATH-003-FLUTE-ANSWER')
(dest/'Scripts'/'render_first_breath_v3.lua').write_text(lua,encoding='utf8')
(dest/'Provenance'/'CHANGE.txt').write_text('First flute phrase (QN 25,26,27, pitches 74,75,74) repeated exactly at QN 111.5,112.5,113.5 to answer its earlier call. Replaces v2 transformed callback; v2 ending notes retained. All first-breath 001 and 002 files untouched.\n',encoding='utf8')
print('CREATED',dest)
