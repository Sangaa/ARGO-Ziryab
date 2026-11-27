import json
from pathlib import Path

src=Path(r"%ZIRYAB_STUDIO%\Projects\ZRY-NIGHT-ORGAN-002\Provenance\score_v2.json")
dst=Path(r"%ZIRYAB_STUDIO%\Projects\ZRY-NIGHT-ORGAN-003\Provenance\score_v3.json")
s=json.loads(src.read_text(encoding="utf-8"))

org=sorted(s["organ"], key=lambda e:(e[0],e[2]))

# Group notes by onset. Treat 3-note groups as chord events.
groups={}
ornaments=[]
for e in org:
    groups.setdefault(round(e[0],9),[]).append(e)

starts=sorted(groups)
new_org=[]
for i,st in enumerate(starts):
    grp=groups[st]
    if len(grp)>=3:
        # sustain chord until next chord onset, with a tiny overlap for smooth handoff.
        next_chord=None
        for st2 in starts[i+1:]:
            if len(groups[st2])>=3:
                next_chord=st2
                break
        if next_chord is None:
            new_end=max(e[1] for e in grp)+0.6
        else:
            new_end=next_chord+0.035
        for e in grp:
            ee=list(e)
            ee[1]=new_end
            # soften chord velocity slightly because long sustain accumulates energy
            ee[3]=max(38,int(round(ee[3]*0.82)))
            new_org.append(ee)
    else:
        # tiny melodic organ answers are removed in v3 so organ becomes a bed, not a stab voice.
        ornaments.extend(grp)

new_org.sort(key=lambda e:(e[0],e[2]))

s["title"]="ZRY-NIGHT-ORGAN-003"
s["organ"]=new_org
s["v3_changes"]={
  "organ":"continuous sustained chord bed; no intentional gaps between chord blocks",
  "organ_ornaments":"removed",
  "trumpet":"unchanged from v2",
  "bass":"unchanged from v2",
  "tabla":"unchanged from v2",
  "tempo":"unchanged at 92 BPM",
  "goal":"test whether the perceived 'buffering/stutter' was caused by organ articulation"
}
dst.write_text(json.dumps(s,ensure_ascii=False,indent=2),encoding="utf-8")
print(json.dumps(s["v3_changes"],ensure_ascii=False,indent=2))
print("organ_notes",len(new_org),"removed_ornament_notes",len(ornaments))
