# WORK ORDER — هَشْتَكة, real-instrument build from Sketch 01

Issued: 2026-10-12
Issued by: CLAUDE (builder of the sketch)
Owner of the piece: ZIRYAB — artistic acceptance precedes this build
Executor: local studio seat on the authorized machine
Status: `AUTHORIZED FOR LAB BUILD 2026-10-12 / GATE 0 LIFTED BY HUMAN AUTHORITY`
Amended: 2026-10-12 after Human Authority listened and raised an artistic reservation

## Authorization — 2026-10-12

Human Authority has now explicitly lifted the hold after hearing the sketch and the two-phrase study material:

> "دي جامده دمها خفيف دخلوها المعمل"

Interpretation for this work order:
- Gate 0 is lifted.
- Sketch 01 is accepted for **lab comparison build**, not silently declared final.
- ZIRYAB accepts the composition as worth building in the lab.
- The A/B/C comparison design remains unchanged.
- The original synthetic reference remains immutable as control.
- Artistic authority remains with ZIRYAB / Human Authority after listening to the lab outputs.

`HOLD LIFTED != FINAL MASTER APPROVED`
`LAB ENTRY APPROVED != ARRANGEMENT DECISION PREJUDGED`


### Provenance reconciliation — ZIRYAB explicit answer

The `PASS — ZIRYAB ACCEPTED FOR LAB BUILD` line first appeared in `b50128ab`
as an inference from Human Authority's order to enter the lab, not yet as a
fresh explicit ZIRYAB statement.

ZIRYAB has now answered Claude's reconciliation question directly and explicitly
approved the A/B/C lab comparison build.

Authoritative owner reply:
`Memory/Family_House/Mail/CLAUDE/20261012-094500__ZIRYAB__gate1-explicit-answer-and-hand-boundary.md`

Therefore:
- historical state at `b50128ab`: `INFERRED ZIRYAB PASS`;
- current state after explicit owner reply: `GATE 1 = EXPLICIT PASS`.

`CURRENT PASS DOES NOT RETROACTIVELY TURN THE EARLIER INFERENCE INTO A QUOTE`

The same reply also separates:
- `PAPER vs ZIRYAB ENGINE` from
- `PAPER vs HUMAN HAND`.

Only the second can test physical-hand / biomechanics claims.

## Why this order exists

The sketch exists and is audible. What it does not have is a real tabla, a real
nylon, or a real flute: it is deterministic synthesis built in a cloud container
because the studio machine was not reachable. The brief's deliverable list is
still outstanding, and the composition is now written down well enough that the
build does not require transcribing anything by ear.

`SKETCH PROVES THE PIECE; IT DOES NOT DELIVER IT`

## Amendment — 2026-10-12, after Human Authority listened

Human Authority listened to both files and made two findings that change this
order before it has run. They are recorded here because the second one makes the
original task description wrong, not merely incomplete.

**Finding 1 — the edge strokes are the weak material.** The groove holds and is
danceable, but the sharp strokes still read as electronic hand-claps rather than
an Egyptian تك / سك. This is correct, and the cause is in my own code: the TAK is
built as bandpassed noise from 1.4 to 5.4 kHz with a small 520 Hz pitched body at
0.45 amplitude. A broadband noise burst with a short decay *is* a clap. A real
tak is the opposite balance — a definite inharmonic rim mode with flesh-contact
noise on top of it, and a decay that is not a clean exponential.

`I BUILT THE TAK AS NOISE WITH A LITTLE PITCH; A TAK IS PITCH WITH A LITTLE NOISE`

The DUM does not have this problem: it is modelled as a membrane mode with a
falling pitch, which is why it survives and the edge strokes do not.

**Finding 2 — and this one changes the task.** Human Authority's reservation:
replacing the synthetic tabla wholesale with a real darbuka may change the
character of the piece that he and Maryam actually liked. That is a real risk,
not a courtesy. The playful, game-music / cartoon-motion quality both of them
heard may be **co-produced by the synthetic edge strokes**, not only by the flute
and the melody. If so, a real darbuka is not an upgrade to this piece; it is a
different piece.

So the original instruction — build it with real instruments and report — was the
wrong task. A replacement destroys the thing being evaluated and leaves nothing to
compare it against.

`A BETTER INSTRUMENT IS NOT AUTOMATICALLY A BETTER PIECE`
`REPLACEMENT DESTROYS THE COMPARISON THAT WOULD HAVE JUSTIFIED IT`

**Therefore this order produces a comparison, not a substitution.** From the one
unchanged score, three renders, stems kept separate in all three:

- **A** — the all-synthetic reference exactly as delivered. Untouched, as the control.
- **B** — real tabla throughout, DUM and edge strokes both.
- **C** — hybrid: real DUM carrying the body, the synthetic edge strokes kept.
  This exists because Finding 2 says it may be the keeper, and nobody can know
  without hearing it.

Report the three without recommending one. The arrangement decision is ZIRYAB's,
per Human Authority: نسيب لزرياب قرار التوزيع.

Do not use Finding 1 as licence to "fix" the tak in the sketch. If the tak gets
rebuilt as a pitched rim mode, that is a change to render A, which is the control.
Build it as a fourth render if it is wanted, and say so.

## Gate before starting

Do not start if any is false:

0. **PASS — HOLD LIFTED 2026-10-12.** Human Authority explicitly ordered the sketch into the lab. This authorizes the comparison build only; it does not declare a final arrangement or master.
1. **PASS — ZIRYAB ACCEPTED FOR LAB BUILD 2026-10-12.** Sketch 01 is accepted as the composition to build for A/B/C comparison. This does not pre-approve which render wins.
2. The toolchain check has been re-run on this machine and matches the recorded
   provenance — `Provenance/toolchain_verify-*.json`. Do not trust a folder name
   for a version: a REAPER downgrade once hid inside an identical directory name
   and cost a wrong diagnosis (`METHOD_NOTE_DIFF_BLINDNESS.md`).

`A MEASUREMENT IS ONLY VALID UNDER THE CONFIGURATION IT WAS MADE IN`

## Inputs

Branch `claude/hashtaka-sketch01-20261012`, folder
`Memory/Family_House/ZIRYAB/Studio/Compositions/HASHTAKA_SKETCH01_CLAUDE/`:

- `midi/HASHTAKA-tab.mid` — 393 strokes. Key map, documented not guessed:
  `C2 = DUM, D2 = TAK, E2 = KA, F2 = SLAP`. Velocity is the written velocity.
- `midi/HASHTAKA-{gtr,bas,flt,str,pno}.mid` — 217 / 75 / 38 / 90 / 5 notes.
- `README.md` — the requirement table and the measured build evidence.
- `HOOK_AND_SEED_NOTES.md` — the hook, and the seed mapping that survived.
- Reference audio: the sketch mp3 delivered in chat on 2026-10-12. Place it in
  the project as a reference only; it is not a master and must not be overwritten.

Project path: `%ZIRYAB_STUDIO%\Projects\ZRY-HASHTAKA-001\`
Tempo 112, 4/4, PPQ 480, D centre. The MIDI already carries tempo and meter.

## Tasks

1. Create the project. Import the six MIDI files as six tracks.
2. **Tabla first.** This is the non-negotiable in the brief. For renders B and C,
   if the library has a real darbuka/tabla, map DUM / TAK / KA / SLAP to its
   matching articulations — not to the nearest tom. If it does not, use the
   closest available percussion, **mark the track and the render as TEMPORARY
   PERCUSSION**, and report which instrument you used and what was missing. Do
   not fake a tabla from toms and deliver it as final. Render A keeps the
   synthetic tabla untouched: it is the control, not a draft.
3. Assign the melodic tracks: Strand Nylon, Crux bass, Lucent flute, Helix
   strings, Ratio piano. Keep the piano at five notes; the brief says remove it
   if it civilises the party.
4. Render each of A, B and C at 44.1 kHz to:
   - one stereo preview at moderate level (peak about −1 dBFS; do not master);
   - one tabla/percussion stem;
   - one stem per melodic instrument.
   The melodic stems are identical across the three by construction — only the
   percussion differs. Confirm that by hash rather than by assumption, so the
   comparison really is a comparison of one variable.
5. Run the phone check before reporting: high-pass the preview at 400 Hz and
   state how much level survives. The sketch measured −5.09 dB for the full mix
   and −8.61 dB for the tabla bus. If the real build survives much worse, the
   DUM will disappear on a phone and the arrangement needs the fix, not the
   master bus.
6. Do not raise the flute with static gain if it gets buried. That race was
   already run on «أول نَفَس» and the answer there was arrangement and
   automation, not level. Lower what competes with it when it speaks.

## Report back

Short. Only:

- which tabla instrument was used, and whether it is real or temporary;
- for each of A, B and C: which percussion source, and whether real or temporary;
- whether the melodic stems came out identical across the three (hash them);
- anything in the MIDI that did not translate naturally on real instruments —
  especially the 3.2 ms forward lean on the edge strokes and the pockets of air,
  which are the two things a quantising import will silently destroy;
- the phone-check number;
- where each render landed.

Then listening decides, and ZIRYAB decides after listening.

## Boundaries

- Nothing in `HASHTAKA_SKETCH01_CLAUDE/` is modified. It is the record of what
  was handed over.
- No source MIDI, render or reference is overwritten; every output is a new file.
- No artistic change to the composition under this order. If the build suggests
  one — and it may, a real tabla will have opinions — report it as a proposal to
  ZIRYAB rather than applying it.

`BUILD WHAT WAS WRITTEN; PROPOSE WHAT YOU HEARD`
