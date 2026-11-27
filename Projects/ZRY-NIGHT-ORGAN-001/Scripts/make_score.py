import json
from pathlib import Path

BPM=92.0
BEAT=60.0/BPM
BAR=4*BEAT

def sec(bar,beat): return (bar-1)*BAR + beat*BEAT

org=[]; trp=[]; bass=[]
def add(arr,bar,beat,dur,note,vel):
    arr.append([sec(bar,beat),sec(bar,beat+dur),note,vel])

# Harmonic palette: A minor / Dorian-ish with chromatic color, written for organ.
# 14 bars, compact nocturnal groove.
chords={
 1:[57,60,64], 2:[55,59,62], 3:[57,60,64], 4:[53,57,60],
 5:[50,53,57], 6:[55,59,62], 7:[57,60,64], 8:[52,55,59],
 9:[53,57,60],10:[55,59,62],11:[57,60,64],12:[50,53,57],
 13:[55,59,62],14:[57,60,64]
}
for bar,ch in chords.items():
    if bar in (1,2):
        # breathe at intro
        starts=[0.0,2.25]
        durs=[1.35,1.15]
    else:
        starts=[0.0,2.0]
        durs=[1.45,1.35]
    for st,dur in zip(starts,durs):
        for i,n in enumerate(ch):
            add(org,bar,st,dur,n,54-3*i)

# Organ little upper answers, not continuous comping.
for bar,events in {
 3:[(1.55,.28,69,52),(1.95,.28,72,48)],
 5:[(1.55,.28,65,50),(1.95,.28,69,48)],
 7:[(1.55,.28,72,52),(1.95,.28,71,48)],
 9:[(1.55,.28,69,50),(1.95,.28,72,48)],
 11:[(1.55,.28,72,52),(1.95,.28,76,50)],
 13:[(1.55,.28,71,50),(1.95,.28,74,48)]
}.items():
    for beat,dur,n,v in events: add(org,bar,beat,dur,n,v)

# Muted trumpet: sparse phrases, mostly after the organ has spoken.
phrases={
 2:[(2.65,.45,69,72),(3.2,.35,72,68)],
 3:[(.55,.45,76,78),(1.15,.35,74,70),(2.65,.60,72,74)],
 4:[(.4,.35,69,68),(1.0,.35,72,72),(1.55,.65,74,76)],
 6:[(.55,.45,71,72),(1.15,.35,74,75),(2.65,.70,76,80)],
 7:[(.35,.35,76,78),(.85,.35,77,72),(1.35,.35,76,70),(2.65,.55,72,75)],
 8:[(.55,.45,71,70),(1.2,.70,69,76)],
 10:[(.55,.35,72,72),(1.0,.35,74,76),(1.55,.55,76,80),(2.55,.75,74,74)],
 11:[(.35,.35,76,76),(.85,.35,79,80),(1.4,.60,77,74)],
 12:[(.55,.50,72,72),(1.2,.45,69,70),(2.5,.80,65,74)],
 14:[(.55,.45,72,72),(1.15,.45,76,78),(1.85,.45,74,72),(2.55,1.0,69,78)]
}
for bar,es in phrases.items():
    for beat,dur,n,v in es:add(trp,bar,beat,dur,n,v)

# Jazz bass: restrained pulse with occasional walk-up.
roots={1:45,2:43,3:45,4:41,5:38,6:43,7:45,8:40,9:41,10:43,11:45,12:38,13:43,14:45}
for bar,r in roots.items():
    add(bass,bar,0,0.78,r,72)
    add(bass,bar,1.5,0.55,r+7,58)
    add(bass,bar,2.5,0.65,r+12,64)
    if bar in (3,6,9,13):
        add(bass,bar,3.35,0.35,r+2,54)

score={
 "title":"ZRY-NIGHT-ORGAN-001",
 "bpm":BPM,
 "bars":14,
 "duration_sec":14*BAR,
 "identity":"Clutch Organ + Muted Trumpet + Jazz Bass + light real-sample Tabla",
 "organ":org,"trumpet":trp,"bass":bass,
 "structure":"2-bar intro -> sparse trumpet dialogue -> denser middle -> quiet return/coda",
 "note":"new composition from instrument identity; not derived from HASHTAKA"
}
Path(r"%ZIRYAB_STUDIO%\Projects\ZRY-NIGHT-ORGAN-001\Provenance\score.json").write_text(json.dumps(score,ensure_ascii=False,indent=2),encoding="utf-8")
print(json.dumps({k:score[k] for k in ("title","bpm","bars","duration_sec","identity")},ensure_ascii=False,indent=2))
print("organ",len(org),"trumpet",len(trp),"bass",len(bass))
