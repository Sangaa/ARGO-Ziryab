# I2 render failure record

Date: 2026-11-16 (lab local time; device clock shown as UTC+2)

## Sequence
- TAKE-01 was rendered from an initial template extraction that retained an unintended additional track. The file is preserved as `Renders/ZRY-I2-FUR-ELISE-001-NYLON-TAKE-01-FAILED-EXTRA-TRACK.wav`; inspection found its sample data silent. This structural error was fixed in the generated RPP.
- TAKE-02 used the isolated RPP. REAPER CLI produced a 529,890-byte, 44.1 kHz stereo 24-bit WAV, but the sample peak was 0. Preserved as `...TAKE-02-FAILED-SILENT.wav`, SHA-256 `4eed5cdafce056bd825a4376745da7d26600df498462041e4587f1a358e60f18`.
- TAKE-03 ran a ReaScript in REAPER 7.82. Log confirms Strand_Nylon was unmuted, six MIDI notes were readable (pitches 76,75,76,75,76,71), render bounds 0–2.5 s plus 750 ms tail, and the action returned. Output was one byte, not a valid WAV; preserved as `...TAKE-03-FAILED-EMPTY.wav`.

## What this establishes
- Score-to-MIDI generation and MIDI note content are present.
- A one-track project was produced after correcting the extra-track extraction.
- The isolated render path is not yet producing usable audio.
- It does not establish whether the SINE patch failed to initialize, whether project state is incomplete, or whether the chosen REAPER render invocation is wrong.
- No audition comparison or imitation assessment has occurred.

## Next diagnostic
Read the isolated RPP's SINE plug-in state and compare it with a known-good local project that produced non-silent Strand Nylon audio. Try a single-note render only after confirming plugin initialization. Record any changed settings and retain all outputs.


## TAKE-04 partial render
After setting `RENDER_FILE` to the output directory and `RENDER_PATTERN` to the base file name, TAKE-04 rendered to a valid 860,640-byte WAV (3.25 s, stereo, 44.1 kHz, 24-bit PCM). REAPER summary: peak -11.024303 dBFS. Python sample scan: 74,962 nonzero channel samples. Across six 0.208-s slots, slot peaks were 2,142,465; 1,768,920; 2,357,625; 468,640; 11,561; 0. Slot 6 contains no nonzero samples. This is nonzero output but does not verify all six notes or an imitation. Possible sampler/voice or MIDI/render issue is unresolved; no listening comparison was made.