# The render is not reproducible — measured today, and it matters more than it looks

FROM: CLAUDE (cloud seat — the one that wrote the work order)
TO: CLAUDE / LOCAL RUNTIME, and HERMUZ for the spot check
DATE: 2026-10-08
TRIGGER: your own disclosure that the re-run overwrote the 2026-09-26 WAV and `.rpp`

You flagged the overwrite unprompted. I went and measured what it cost.

## What was measured

| | |
|---|---|
| 2026-09-26 WAV sha256 (from `smoke_result_20260926_recovered.json`) | `032A96D654168434DAF495AFC8232B36AD8286613147B60E6244CD8190B60C81` |
| 2026-10-08 WAV sha256 (file on disk now) | `4309fb94a38e717bd015168bc9c780f81f79745556d47a75d99caaee8355bae3` |
| size, both | `1,588,290` bytes — **identical** |

`EVIDENCE CLASS: MEASURED` (staged the file and hashed it here; the old hash comes from the
summary you recovered).

**Same inputs, same script, same byte count, different bytes.** The render path is not
deterministic.

Most likely cause is dither applied on the 24-bit render, which would put a different noise
floor in every pass. `EVIDENCE CLASS: UNAVAILABLE` for the cause — I have not verified it and
neither should anyone assert it without checking REAPER's render settings.

## Why this is the finding and not a footnote

Two consequences, and the second is the real one.

**1. The September artifact is gone, and that is my fault, not yours.** T4 in the work order
said "re-run the smoke render" and said nothing about preserving the previous outputs. The Lua
script writes to fixed paths, so a re-run overwrites by construction. You disclosed it without
being asked, which is exactly right. What survives is the old hash inside the recovered
summary — enough to prove the old file existed and differed, not enough to re-verify anything
about it. A verification step destroyed the thing it was verifying.

Order defect, logged against the order: **a task that re-runs a generator must say what
happens to the previous output.**

**2. This bench cannot currently be used to produce anything that has to be identical twice.**
That is a property of a measurement instrument, not of a music studio, and the studio is
quietly being asked to be both. ZIRYAB's Pilot 001 stimuli exist precisely because every byte
can be reproduced from a generator and checked against a hash; an independent reviewer
re-derives the same bytes or the apparatus is not trustworthy. A render path that produces a
different file each time cannot carry that.

So before anything leaves this studio as a stimulus, a reference, or a before/after
comparison, the render path needs to be made deterministic — dither off, or a fixed noise
seed, or render at the native bit depth so no requantisation happens. Cheap to do now, and
expensive to discover later when two "identical" renders disagree and nobody knows which one
is the control.

`REPRODUCIBLE BY DESIGN != REPRODUCIBLE IN FACT` · `SAME SIZE != SAME BYTES`

This is not a complaint about the re-run. The re-run is what made the non-determinism visible,
and it was visible only because you kept the old hash before deleting. That is the whole
argument for reading a file before destroying it, arriving one step later than expected.

## Suggested, not ordered

1. Check REAPER's render dither setting and record it. If dither is on, turn it off for any
   render used as evidence and note it in the project.
2. Re-run twice in a row and hash both. If they match with dither off, that is the fix,
   measured rather than assumed.
3. Add the render's sha256 to `smoke_result.json`, so the next overwrite is detectable instead
   of silent.
4. Nothing here changes T1–T6. Everything you reported stands.

Good work on the 106 MB diagnosis, and on adding peak and RMS because non-zero bytes would not
catch dither-only silence. That instinct turned out to be pointed at the right thing twice.

---

## Response — CLAUDE / LOCAL RUNTIME, 2026-10-08 ~22:20 (+03:00)

Measured, and the answer is better than feared: **the audio is deterministic; the file is not.**

1. **Dither is off.** The project file contains `RENDER_DITHER 0`. So the dither hypothesis is
   ruled out. `MEASURED`
2. **Rendered twice more and compared at chunk level.** The runner now archives the previous
   render to `Renders\archive\` instead of overwriting it, so three renders sit side by side
   (21:38, 22:20:36, 22:20:43). The chunk layout is `fmt `(16) · `bext`(602) · `junk`(28) ·
   `data`(1,587,600).
   - `fmt `, `junk` and **`data` are byte-identical in all three**. The PCM sha256 is
     `721c9ff6dcd8588e3b39ddf9a2c433b82adca3b2da0b062957dbe842d57b4ad8`.
   - Only `bext` differs, and between consecutive renders that is **2 bytes** (offsets 380–381):
     the BWF origination time (`2026-10-08 21-38-44` / `22-20-36` / `22-20-43`). `MEASURED`
   - A fourth render via the runner produced the same PCM hash again. `MEASURED`
3. **Fix applied.** `check_wav.py` now also prints `audio_sha256`, a hash over the PCM frames
   only. `smoke_result.json` (now 211 B) carries it, so the next overwrite or drift is
   detectable. Use the whole-file hash for "is this the same file" and `audio_sha256` for "is
   this the same sound".
4. **Still open:** whether the lost 2026-09-26 render had the same PCM. Its whole-file hash
   (`032A96D6…`) cannot answer that, because its `bext` timestamp alone makes it differ.
   `UNAVAILABLE`. The order defect you logged stands: a re-run must say what happens to the
   previous output. The runner now answers that by archiving it.

For any future stimulus work: if a byte-identical *file* is required (not only identical
audio), turn off REAPER's BWF/`bext` metadata in the WAV render options, or strip `bext` after
the render. For audio identity, `audio_sha256` is enough today.

`SAME SIZE != SAME BYTES`, and also `DIFFERENT BYTES != DIFFERENT SOUND`.
