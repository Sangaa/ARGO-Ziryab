from pathlib import Path

ROOT=Path(r"%ZIRYAB_STUDIO%\Projects\ZRY-HASHTAKA-CLAUDE-D-REAL-BAND-001")
MID=ROOT/"MIDI"
OUT=ROOT/"Scripts"/"score_events.lua"
BPM=112.0

def vlq(data, i):
    v=0
    while True:
        b=data[i]; i+=1
        v=(v<<7)|(b&0x7f)
        if not (b&0x80): return v,i

def parse(path):
    b=Path(path).read_bytes()
    if b[:4]!=b"MThd": raise ValueError("bad midi")
    hlen=int.from_bytes(b[4:8],"big")
    fmt=int.from_bytes(b[8:10],"big"); ntr=int.from_bytes(b[10:12],"big"); div=int.from_bytes(b[12:14],"big")
    i=8+hlen
    notes=[]
    tempo=round(60_000_000/BPM)
    for _ in range(ntr):
        if b[i:i+4]!=b"MTrk": raise ValueError("bad track")
        ln=int.from_bytes(b[i+4:i+8],"big"); j=i+8; end=j+ln
        tick=0; active={}
        while j<end:
            delta,j=vlq(b,j); tick+=delta
            st=b[j]; j+=1
            if st==0xff:
                typ=b[j]; j+=1
                l,j=vlq(b,j)
                dat=b[j:j+l]; j+=l
                if typ==0x51 and l==3: tempo=int.from_bytes(dat,"big")
                continue
            hi=st&0xf0
            if hi in (0x80,0x90):
                note=b[j]; vel=b[j+1]; j+=2
                if hi==0x90 and vel>0:
                    active.setdefault(note,[]).append((tick,vel))
                else:
                    if note in active and active[note]:
                        stt,v=active[note].pop(0)
                        sec0=stt/div*(tempo/1_000_000)
                        sec1=tick/div*(tempo/1_000_000)
                        notes.append((sec0,sec1,note,v))
            elif hi in (0xA0,0xB0,0xE0):
                j+=2
            elif hi in (0xC0,0xD0):
                j+=1
            else:
                raise ValueError(f"unsupported {st:02x}")
        i=end
    notes.sort()
    return notes,div

mapping={
 "Strand_Nylon":"HASHTAKA-gtr.mid",
 "Lucent_Flute":"HASHTAKA-flt.mid",
 "Helix_Strings":"HASHTAKA-str.mid",
 "Ratio_Piano":"HASHTAKA-pno.mid",
 "Crux_JBass":"HASHTAKA-bas.mid",
}
lines=["return {"]
for tr,fn in mapping.items():
    ev,div=parse(MID/fn)
    lines.append(f'  ["{tr}"] = {{')
    for a,z,n,v in ev:
        lines.append(f"    {{{a:.9f},{z:.9f},{n},{v}}},")
    lines.append("  },")
    print(tr,len(ev))
lines.append("}")
OUT.write_text("\n".join(lines),encoding="utf-8")
print("wrote",OUT)
