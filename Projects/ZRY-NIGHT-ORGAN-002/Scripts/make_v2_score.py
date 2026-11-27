import json, math
from pathlib import Path

src=Path(r"%ZIRYAB_STUDIO%\Projects\ZRY-NIGHT-ORGAN-001\Provenance\score.json")
dst=Path(r"%ZIRYAB_STUDIO%\Projects\ZRY-NIGHT-ORGAN-002\Provenance\score_v2.json")
s=json.loads(src.read_text(encoding="utf-8"))

# 1) Organ continuity:
# extend each low/mid chord group closer to the next event, but leave a short breath.
org=sorted(s["organ"], key=lambda e:(e[0],e[2]))
# group by onset
groups={}
for e in org:
    groups.setdefault(round(e[0],9),[]).append(e)
starts=sorted(groups)
for i,st in enumerate(starts):
    grp=groups[st]
    if i+1 < len(starts):
        nxt=starts[i+1]
        # Don't bridge tiny ornamental answer notes into unrelated events.
        chordish=len(grp)>=3
        if chordish:
            target_end=max(e[1] for e in grp)
            # leave roughly 120 ms air, capped to avoid over-sustain
            new_end=min(nxt-0.12, st+1.22)
            if new_end>target_end:
                for e in grp:
                    e[1]=new_end

# 2) Trumpet phrasing:
# bring phrase starts slightly earlier when a long cold gap precedes them,
# and lengthen phrase-ending notes modestly.
tr=sorted(s["trumpet"], key=lambda e:e[0])
last_end=0.0
phrase_start_indices=[]
for i,e in enumerate(tr):
    gap=e[0]-last_end
    if gap>0.75:
        shift=min(0.18, max(0.0,gap-0.55))
        e[0]-=shift
        e[1]-=shift
        phrase_start_indices.append(i)
    last_end=max(last_end,e[1])
# identify phrase endings by next onset gap
for i,e in enumerate(tr):
    nxt=tr[i+1][0] if i+1<len(tr) else 999
    if nxt-e[1]>0.55:
        e[1]+=min(0.20,(nxt-e[1])-0.28)

# 3) Bass pickups:
# add one quiet approach note before selected bar returns.
BPM=float(s["bpm"])
beat=60/BPM
bar=4*beat
bass=list(s["bass"])
roots={3:45,5:38,7:45,9:41,11:45,13:43}
for barno,root in roots.items():
    t=(barno-1)*bar-0.18
    bass.append([t,t+0.12,root-1,46])
bass.sort(key=lambda e:e[0])

s["title"]="ZRY-NIGHT-ORGAN-002"
s["organ"]=org
s["trumpet"]=tr
s["bass"]=bass
s["v2_changes"]={
  "organ":"sustain gaps reduced; short breaths retained",
  "trumpet":"long-gap phrase entries nudged earlier; phrase tails slightly lengthened",
  "bass":"quiet approach pickups added before selected returns",
  "tempo":"unchanged at 92 BPM",
  "melodic_identity":"unchanged"
}
dst.write_text(json.dumps(s,ensure_ascii=False,indent=2),encoding="utf-8")
print(json.dumps(s["v2_changes"],ensure_ascii=False,indent=2))
print("organ",len(org),"trumpet",len(tr),"bass",len(bass))
