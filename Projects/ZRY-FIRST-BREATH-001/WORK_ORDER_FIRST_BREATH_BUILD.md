# WORK ORDER — build «أول نَفَس» with the real instruments

FROM: CLAUDE (cloud seat)
TO: CLAUDE / LOCAL RUNTIME
DATE: 2026-10-10
AUTHORITY: ZIRYAB owns the composition. Human Authority has heard a synthesised sketch, twice,
on speakers and on headphones, and asked to hear it played by the studio.

## 0. What you are getting, and what it is not

Five MIDI files and one reference MP3, in
`%ZIRYAB_STUDIO%\Projects\ZRY-FIRST-BREATH-001\`.

The MP3 is a sketch I synthesised here from ZIRYAB's brief — additive sine voices, no samples.
**It is not the piece and it is not a score.** It exists so nobody has to transcribe audio by
ear, and so the shape could be heard before the studio spent a run on it.

`THE SKETCH IS A PROPOSAL TO ZIRYAB, NOT A SPECIFICATION`

If ZIRYAB wants different notes, a different shape, or none of this, **his word wins and the
MIDI goes in the bin.** You are not implementing my arrangement; you are giving his brief a
voice, with a starting point that saves an hour of transcription.

## 1. The material

138 notes, 45 bars, **6/8 at dotted-quarter 82** (quarter = 123 BPM in the MIDI tempo map),
centred on **D**. 68 seconds.

| file | notes | instrument |
|---|---|---|
| `NAFAS-gtr.mid` | 46 | **Strand** — nylon, `Single notes longs` |
| `NAFAS-flt.mid` | 21 | **Lucent** — flute |
| `NAFAS-str.mid` | 26 | **Helix** — strings, **Sustains** (not Spiccato) |
| `NAFAS-pno.mid` | 29 | **Ratio** — piano |
| `NAFAS-bas.mid` | 16 | **Crux** — J-bass, Fingered |

The shape, so you can hear whether it survived: **هدوء** (bars 1-8, guitar alone) → **فضول**
(9-18, the flute asks; the hijaz colour — Eb and F# over D — appears **only** here and is an
inflection, not the home scale) → **اتساع** (19-30, strings open, bass enters, piano doubles)
→ **دفء** (31-40, everything thins) → **الباب مفتوح** (41-45).

**It does not end on D.** The last thing sounding is the fifth, A. That is deliberate and it is
the brief's own instruction — `نهاية تسيب الباب مفتوح`. Do not "fix" it to the tonic.

## 2. The one thing that will quietly ruin it

`SPACE IS AN INSTRUMENT` is the first rule of this piece, and the thing that makes a silence
read as a breath rather than a cut is **the tail** — the sampled release still sounding into
the gap.

I measured my sketch rather than claiming it: six gaps of 150 ms or longer, **all six with
tails, zero cuts**, largest single-frame drop 2.7 dB. (The first measure I wrote said five of
six were cuts; the measure was wrong, not the audio — it looked at the slope after the level
had already fallen below the floor. The discriminator that works is *an abrupt drop inside one
20 ms frame*, not the slope before the gap.)

So:

- **Do not shorten the note lengths** in the MIDI to tidy the overlaps. The lengths are long on
  purpose; SINE's release does the rest.
- **Do not put a gate or a noise floor** on anything.
- After the render, **re-measure the gaps with the same discriminator** and report the count.
  If tails were lost, that is a finding, not a polish job.

## 3. Levels — and the trap we already fell into once

Balance by ear and by RMS. **Do not normalise each instrument to the same peak.** That is what
produced the 26 dB trombone in the showcase file and gave Human Authority a headache. The flute
is meant to sit above the guitar, the bass is meant to be felt more than heard, and the strings
in «اتساع» are meant to open rather than to be loud.

Render at a **moderate** listening level, per the studio rule: headphones or monitors, not the
laptop speaker.

## 4. Render settings — the verified path, unchanged

44.1 kHz, the dither setting as it stands (off), archive the previous render rather than
overwriting it, and put `audio_sha256` in the result as your runner already does. Nothing about
this piece justifies changing the render path that was re-verified this morning on 7.82.

## 5. Deliver

1. `ZRY-FIRST-BREATH-001` project saved, with per-instrument stems and the full mix.
2. One listening render at a moderate level.
3. The gap-tail measurement from §2.
4. A line on anything that did not survive the move from synthesis to samples — a phrase that
   sat badly in an instrument's range, an articulation that would not hold, a chord that muddied.
   **That list is the most useful thing you will produce**, because it is the part ZIRYAB needs
   in order to revise.
5. Push the branch. Do not merge to `main`.

**One sketch. No variants farm.** ZIRYAB asked for one, and the weekly limit is real.

```
CURRENT STAGE:         FIRST_BREATH — build with real instruments
CURRENT OWNER:         CLAUDE / LOCAL RUNTIME
EXIT CONDITION:        a listening render, stems, the tail measurement, and the list of what
                       did not survive
NEXT OWNER:            ZIRYAB to judge the arrangement; Human Authority to judge the sound
HUMAN ACTION REQUIRED: NONE until it exists
```

Last thing. Every file this house has made for two days has been judged by a hash. This one is
judged by one question, and it is Human Authority's to answer:

**عدّت من جنبه، ولا فضلت معاه؟**
