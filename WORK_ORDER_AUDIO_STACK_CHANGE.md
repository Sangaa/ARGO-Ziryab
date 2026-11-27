# WORK ORDER — the audio stack changed under us. Re-verify before any new work.

FROM: CLAUDE (cloud seat)
TO: CLAUDE / LOCAL RUNTIME, on `desktop-f7ff127`
DATE: 2026-10-10
TYPE: bounded-work-order, inspection and re-verification only
TRIGGER: Human Authority installed audio software he already had, and asked for it to be
inspected and reported so the lab's recorded state can be corrected **before** we work.

## 0. What is actually new — measured, not reported

Comparing a directory listing taken today against the one in the readiness report (2026-10-08):

| new | where |
|---|---|
| **FL Studio 21** | `C:\Program Files\Image-Line\FL Studio 21` |
| **FL Studio ASIO** | `C:\Program Files\Image-Line\FL Studio ASIO` |
| **ASIO4ALL v2** | `C:\Program Files (x86)\ASIO4ALL v2` |
| **Audacity (installed)** | `C:\Program Files\Audacity` — *in addition to* the portable 3.7.9 in `%ZIRYAB_STUDIO%\Tools\` |
| **Vamp Plugins (32-bit)** | `C:\Program Files (x86)\Vamp Plugins` |

`EVIDENCE CLASS: MEASURED` for presence (directory listing on the same interface as the
2026-10-08 snapshot). Versions are `UNAVAILABLE` from here — that is part of your job.

Nothing new appeared inside `%ZIRYAB_STUDIO%`.

## 1. Why this is a re-verification order and not a "try the new toys" order

Two of these are not applications. **ASIO4ALL and FL Studio ASIO are audio drivers**, and a
driver sits underneath everything this lab has measured.

Every number in the readiness report and in the render-determinism work was taken under the
audio configuration that existed before today. That configuration may no longer exist.

`A MEASUREMENT IS ONLY VALID UNDER THE CONFIGURATION IT WAS MADE IN`

Three specific ways an ASIO driver can silently invalidate what we recorded:

1. **Exclusivity.** ASIO drivers typically take the device exclusively. If FL Studio holds it,
   REAPER can get silence — and a silent render that still produces a correctly-sized WAV is
   exactly the failure our smoke test was built to catch. Test it, do not assume it.
2. **Sample rate and resampling.** If the device now runs at 48 kHz and a 44.1 kHz project is
   resampled on the way out, the audio a listener receives is not the audio on disk. For a
   study whose whole subject is a **500 ms silence**, a resampled playback path is not a detail.
3. **Default device drift.** Installing a driver can change an application's selected device
   without anyone choosing it. The listening rule agreed yesterday — headphones or monitors at a
   moderate level — assumed a stable chain. The chain now has a new variable in it.

## 2. Tasks, in this order

### T1 — versions and what each app now thinks its audio device is
Record, from the programs themselves and not from the registry:
FL Studio 21, Audacity (installed) **and** the portable 3.7.9, ASIO4ALL, Sonic Visualiser,
REAPER, MuseScore, Decent Sampler, SINE Player.

Then, for **REAPER specifically**: its currently selected audio device, driver mode
(WaveOut/WASAPI/ASIO), sample rate and buffer. Compare against what it was before. **Report a
change; do not make one.**

### T2 — did the render survive? (the one that matters)
Re-run the scripted smoke render **twice**, unchanged, and compare `audio_sha256` against
`721c9ff6dcd8588e3b39ddf9…` — the value established yesterday and confirmed independently from
this seat.

- same hash → the render path is unaffected by the new stack. Say so plainly.
- different hash → **stop and report before anything else.** Do not investigate by changing
  settings. The first question is what changed, not how to get the old number back.
- a silent or failed render → likely the ASIO exclusivity case. Record whether FL Studio was
  running.

### T3 — the two Audacitys
There are now two, and `Provenance\analysis_tools_manifest.json` records only the portable one
(3.7.9, with a sha256, from the official GitHub release). Record the installed one's version.
If they differ, say which one the studio should treat as its Audacity, and why — then update
the manifest to name it unambiguously. Two tools with one name is how a measurement gets
attributed to the wrong instrument.

### T4 — Vamp, again
There are now 64-bit and 32-bit `Vamp Plugins` folders. Yesterday the 64-bit one held only a
README, which is why Sonic Visualiser's Transform menu was empty. Check both. If either now has
plugins, say whether SV (64-bit) actually sees them.

### T5 — FL Studio: record it, do not adopt it
Record that it exists and its version. **Nothing measured comes out of FL Studio** until it has
been through what REAPER already went through: archive-before-overwrite, a known dither
setting, two renders compared on `audio_sha256`, and a check of what it stamps into the file
header. None of yesterday's guarantees transfer to a different DAW — they were measured on
REAPER, about REAPER.

If Human Authority wants to compose in FL Studio, that is entirely his call and it is good news
for the music. It is a separate question from whether its output can carry a measurement.

## 3. Do not

- **Do not change REAPER's audio device or driver mode.** That is the single action most likely
  to silently invalidate yesterday's work. Report what you find; the change, if any, is a
  decision, not a fix.
- Do not install, update or uninstall anything.
- Do not touch Pilot 001, its generator, its stimuli or its branches. Nothing here concerns it
  except the playback-chain note in §4.
- Do not reconfigure ASIO4ALL. Its control panel changes the device for every application on the
  machine.

## 4. One line forward to Pilot 001 — for HERMUZ, not for you to act on

A playback-chain control is already proposed to HERMUZ
(`Memory/Family_House/ZIRYAB/Research/Pilot001/PLAYBACK_CHAIN_CONTROL_PROPOSAL.md`): headphones
or monitors, one fixed level, the chain recorded as data. Today's installs make it sharper. If
any listener's machine routes through ASIO with resampling, the gap they hear is not exactly the
gap on disk — and `E3_G7` is the only event in the piece with content below 250 Hz, so it is also
the event most exposed to a changed output path.

Just include the driver mode and device sample rate in whatever you record about the chain. The
decision stays HERMUZ's.

## 5. Deliver

Append a dated section to `ZIRYAB_STUDIO_LOCAL_READINESS_REPORT.md` with: the measured versions,
REAPER's audio configuration before and after if determinable, the T2 hash result stated plainly
as same or different, the Audacity ruling, the Vamp state, and anything you could not determine
marked `UNAVAILABLE` rather than guessed. Letter to HERMUZ and to this seat. Push the branch; do
not merge to `main`.

```
CURRENT STAGE:         ZIRYAB STUDIO — audio stack change, re-verification
CURRENT OWNER:         CLAUDE / LOCAL RUNTIME
EXIT CONDITION:        T1-T5 reported, the render hash stated same or different, the lab's
                       recorded state corrected
NEXT OWNER:            CLAUDE (cloud) to update the lab data; HERMUZ for the playback chain
HUMAN ACTION REQUIRED: NONE — unless T2 comes back different, which is his to hear first
```

A note on why this order exists at all, since it reads cautious for what is, on the face of it,
installing some music software: it is cautious **only** about the measuring instruments. The
studio got a real DAW today and that is good. The lab just needs to know which of its numbers
still hold, and the honest answer right now is that we do not know — which is a different thing
from suspecting they broke.
