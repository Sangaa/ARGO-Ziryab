# I2 diagnostic results — 2026-11-16

This is an execution record, not an artistic pass. No one in this session auditioned these files.

## Sequence

| Take | Setup | Observed result | Interpretation |
|---|---|---|---|
| 01 | Initial RPP extraction retained an extra template track. | 529,890-byte WAV, sample peak 0. | Failed; extra-track defect preserved. |
| 02 | One-track Strand_Nylon project, CLI render. | 529,890-byte WAV, sample peak 0. | Failed; source of silence unresolved. |
| 03 | ReaScript passed a full filename to REAPER `RENDER_FILE`. | One-byte WAV. Saved RPP target joined `TAKE-03.wav\TAKE-02.wav`. | Failed; API misuse identified. REAPER defines `RENDER_FILE` as directory and `RENDER_PATTERN` as file name. |
| 04 | Corrected directory and pattern, original sixteenth MIDI. | 860,640-byte, 3.25s, stereo, 44.1kHz, 24-bit WAV; REAPER peak -11.024303 dBFS. | Valid nonzero partial output. Per-slot peaks: 2,142,465; 1,768,920; 2,357,625; 468,640; 11,561; 0. |
| 05 | 80%-gate script before MIDI sort. | REAPER read B4 start=1200/end=0. Script would have moved its end incorrectly; render prompt canceled. | Invalid MIDI pairing detected, no TAKE-05 WAV. |
| 06 | Called `MIDI_Sort`, verified six valid note pairs, 80%-gate variant. | 860,640-byte WAV; REAPER peak -11.287980 dBFS; 67,404 nonzero channel samples. Per-slot peaks: 2,287,130; 1,872,090; 1,220,414; 208,619; 0; 0. | MIDI sort corrected the end-pair readback; later two output slots remained zero. |
| 07 | Six pitches separated by 2.5s; item extended but source not. | 18.25s WAV; first two 0.5s windows nonzero; remaining four zero. | Confounded; embedded MIDI source was too short. Preserved, not evidence about SINE pitch support. |
| 08 | Duplicate project with source `HASDATA=16000 QN), item 18s, note positions spaced to 14,400 PPQ. | 18.25s WAV; sample scan found nonzero samples only in first 0.5s window. A fresh REAPER readback confirms all six notes and raw event positions/ends are present. | MIDI events are present, but later audio is absent. Cause unresolved. |

## Current SINE state observation
On TAKE-08 Strand_Nylon and local known-good project Strand_Nylon, REAPER reports the SINE Player instrument enabled and online; both show 32 output pins. TAKE-08 track is unmuted. This excludes simple track mute/offline flags but does not prove the patch loaded the intended samples or explain the render.

## Evidence boundary and next
- No audition or listening comparison occurred.
- No imitation pass or musical-quality score exists.
- TAKE-01 through TAKE-08 files/logs and malformed/canceled project copies remain in the lab project.
- Preserve source and failures. Next useful step requires inspecting the SINE patch/content state through its UI or an available audio-output path, then human auditory review. Do not claim an instrument defect from the current sample scans.
- No paid GitHub Actions were run.

Official REAPER API: https://www.reaper.fm/sdk/reascript/reascripthelp (documents `RENDER_FILE` as render directory and `RENDER_PATTERN` as file name).
