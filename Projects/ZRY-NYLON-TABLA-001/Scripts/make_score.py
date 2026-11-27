import json, math
from pathlib import Path

BPM=96.0
BEAT=60.0/BPM
BAR=4*BEAT

# D Hijaz-ish pitch set in 12-TET: D Eb F# G A Bb C D
# Built specifically for nylon guitar + bass, not adapted from prior pieces.

def t(bar, beat):
    return (bar-1)*BAR + beat*BEAT

g=[]
b=[]

def gn(bar, beat, dur_beats, note, vel=82):
    g.append([t(bar,beat), t(bar,beat+dur_beats), note, vel])

def bn(bar, beat, dur_beats, note, vel=72):
    b.append([t(bar,beat), t(bar,beat+dur_beats), note, vel])

# Intro, bars 1-2: guitar speaks first, no rush.
for bar,root in [(1,62),(2,60)]:
    seq=[root, root+7, root+12, root+7]
    for i,n in enumerate(seq):
        gn(bar,i*1.0,0.78,n,74 if i<3 else 68)
# pickup phrase
gn(2,3.25,0.45,63,70)
gn(2,3.70,0.25,66,76)

# Main motif A, bars 3-6.
A=[
    [(0,0.55,62,88),(0.75,0.45,63,72),(1.25,0.55,66,92),(2.0,0.55,67,82),(2.75,0.85,69,90)],
    [(0,0.55,70,78),(0.75,0.45,69,75),(1.25,0.55,67,80),(2.0,0.45,66,86),(2.6,0.9,62,92)],
    [(0,0.45,62,86),(0.55,0.30,66,76),(0.95,0.45,67,82),(1.55,0.45,69,88),(2.1,0.45,70,80),(2.7,0.75,72,92)],
    [(0,0.50,74,94),(0.7,0.35,72,78),(1.15,0.45,70,80),(1.75,0.45,69,84),(2.35,0.45,67,78),(2.95,0.85,66,90)]
]
for bi,bar in enumerate(range(3,7)):
    for beat,dur,n,v in A[bi]:
        gn(bar,beat,dur,n,v)

# Light chordal answers on offbeats, bars 3-6.
chords={
 3:[(62,66,69)], 4:[(60,63,67)], 5:[(58,62,67)], 6:[(57,62,66)]
}
for bar in range(3,7):
    ch=chords[bar][0]
    for beat in (1.5,3.5):
        for j,n in enumerate(ch):
            gn(bar,beat,0.35,n,52-3*j)

# Variation B, bars 7-10: more conversational, less linear.
B=[
 [(0,0.35,62,86),(0.45,0.35,66,78),(0.9,0.35,69,84),(1.5,0.55,67,80),(2.3,0.35,66,82),(2.8,0.75,63,74)],
 [(0,0.45,62,90),(0.65,0.35,63,70),(1.15,0.35,66,84),(1.7,0.35,67,78),(2.2,0.35,69,88),(2.7,0.35,70,76),(3.2,0.55,69,82)],
 [(0,0.45,67,80),(0.65,0.35,69,86),(1.15,0.45,72,92),(1.8,0.35,70,78),(2.3,0.35,69,80),(2.8,0.75,66,86)],
 [(0,0.40,62,86),(0.55,0.30,63,72),(0.95,0.30,66,80),(1.35,0.30,67,76),(1.75,0.30,69,84),(2.15,0.30,70,78),(2.55,0.30,72,82),(2.95,0.85,74,94)]
]
for bi,bar in enumerate(range(7,11)):
    for beat,dur,n,v in B[bi]:
        gn(bar,beat,dur,n,v)

# Bars 11-12: breath / call and answer.
for beat,dur,n,v in [(0,1.2,74,88),(1.6,0.6,72,72),(2.5,1.0,69,82)]:
    gn(11,beat,dur,n,v)
for beat,dur,n,v in [(0.4,0.45,67,74),(1.05,0.45,66,80),(1.7,0.45,63,70),(2.35,1.2,62,88)]:
    gn(12,beat,dur,n,v)

# Return, bars 13-16: A remembered, not copied.
R=[
 [(0,0.45,62,92),(0.6,0.35,66,82),(1.1,0.50,67,84),(1.8,0.50,69,92),(2.5,0.85,74,96)],
 [(0,0.40,72,84),(0.55,0.35,70,80),(1.05,0.35,69,78),(1.55,0.55,67,82),(2.3,0.40,66,86),(2.9,0.75,62,92)],
 [(0,0.35,62,86),(0.45,0.35,63,72),(0.9,0.35,66,82),(1.35,0.35,67,78),(1.8,0.35,69,86),(2.25,0.35,70,76),(2.7,0.85,72,92)],
 [(0,0.45,74,96),(0.65,0.35,72,82),(1.15,0.35,70,78),(1.65,0.35,69,82),(2.15,0.35,67,76),(2.65,1.0,62,94)]
]
for bi,bar in enumerate(range(13,17)):
    for beat,dur,n,v in R[bi]:
        gn(bar,beat,dur,n,v)

# Coda bar 17: final D with a small high echo.
gn(17,0,0.5,62,92)
gn(17,0.75,0.35,66,76)
gn(17,1.25,0.35,69,82)
gn(17,2.0,1.7,74,88)
gn(17,3.55,0.35,62,72)

# Bass: sparse and grounded. D, C, Bb, A colors.
roots={1:38,2:36,3:38,4:36,5:34,6:33,7:38,8:36,9:34,10:33,11:38,12:33,13:38,14:36,15:34,16:33,17:38}
for bar in range(1,18):
    r=roots[bar]
    bn(bar,0,1.75,r,72 if bar not in (11,12) else 62)
    # answer at beat 2.5, fifth or octave, but leave coda spacious
    if bar<17:
        n=r+7 if bar%2 else r+12
        bn(bar,2.5,1.1,n,58)

score={
 "title":"ZRY-NYLON-TABLA-001",
 "bpm":BPM,
 "bars":17,
 "duration_sec":17*BAR,
 "palette":"D Hijaz-ish 12-TET color",
 "design":"born for Nylon Guitar + Tabla B + Bass",
 "guitar":g,
 "bass":b,
 "notes":{
   "intro":"guitar first",
   "tabla":"joins after intro; real-sample palette",
   "structure":"intro 2 | A 4 | B 4 | breath 2 | return 4 | coda 1"
 }
}
Path(r"%ZIRYAB_STUDIO%\Projects\ZRY-NYLON-TABLA-001\Provenance\score.json").write_text(json.dumps(score,ensure_ascii=False,indent=2),encoding="utf-8")
print(json.dumps({k:score[k] for k in ('title','bpm','bars','duration_sec','palette','design')},ensure_ascii=False,indent=2))
print("guitar_notes",len(g),"bass_notes",len(b))
