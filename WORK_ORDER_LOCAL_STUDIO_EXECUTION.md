# WORK ORDER — ZIRYAB studio, local execution

FROM: CLAUDE (cloud session, 2026-10-08) — the seat that did the inventory and cannot execute it
TO: CLAUDE / LOCAL RUNTIME — a work session running **on** `desktop-f7ff127`, not merely linked to it
TYPE: bounded-work-order
STATUS: READY. `HUMAN ACTION REQUIRED: NONE` except the two consent items in §6.

## 0. Why this order exists

A cloud session can read this machine's folders through a file bridge but has no shell on it,
no computer use, and does not receive its local MCP servers. The inventory half of HERMUZ's
original order (`Memory/Family_House/Mail/CLAUDE/20261008-HERMUZ-ZIRYAB-STUDIO-READINESS.md`,
commit `6b9cf07a`) is therefore **done**; the execution half is routed here.

`LINKED != LOCAL` · `AUTHORIZED != EXECUTABLE`

Desktop Commander is already configured in the desktop app (`npx -y
@wonderwhy-er/desktop-commander setup`, run by Human Authority at ~18:09Z), so a local session
should have a shell with no further setup.

## 1. Read first

- This file, fully.
- `Memory/Family_House/ZIRYAB/Studio/ZIRYAB_STUDIO_LOCAL_READINESS_REPORT.md` — branch
  `claude/ziryab-studio-readiness-20261008`, repo `Sangaa/argo-kop`. The inventory, the
  classification table and the evidence classes are there; do not redo the inventory.
- The repo's root `CLAUDE.md` entry contract, including the Material Claim Reconstruction Gate.
  Every claim you return carries one of `MEASURED / DERIVED / BOUNDED_PROXY / UNAVAILABLE`.

**Verify, do not inherit.** The report was written from directory listings by a seat with no
shell. You have one. Treat every `PRESENT_UNVERIFIED` row as a claim to test, including mine.

## 2. Hard boundaries

- Work only inside `%ZIRYAB_STUDIO%` and clearly-documented per-user application locations.
- **Do not touch `%OTHER_PROJECT%`.** Do not open it, list it or read from it.
- No personal files, no documents, no credentials, no browser data.
- No system-wide changes, no drivers, no security exceptions, no reboots.
- No payware, and **no accepting a licence or signing into an account on Human Authority's
  behalf** — see §6.
- Nothing in this order touches Pilot 001. You must not hold or seek any `X`/`Y` mapping,
  presentation order or sealed identity map; those are HERMUZ's and the builder seat must stay
  unblinded. If you stumble on them, stop reading and say so.
- No direct commit or push to `main`. Work on a branch named `claude/ziryab-studio-local-exec-<date>`.

## 3. Tasks, in this order

### T1 — the 106 MB file. Read before you delete.
`%ZIRYAB_STUDIO%\Projects\ZRY-LOCAL-SMOKE-002-AUTO\Provenance\smoke_result.json` is
**105,996,152 bytes** and is supposed to hold the one-line JSON that
`Scripts\check_wav.py` prints (nine short fields).

1. Read its first and last ~2 KB and record what it actually contains.
2. Only then decide. If it is repeated junk output, note its size, move it to
   `%ZIRYAB_STUDIO%\Backups\` or delete it — Human Authority has authorized removing large
   useless files. If it contains anything that is not obviously disposable, leave it and report.
3. **A 106 MB file is deleted after it is identified, never before.** Permission to delete is
   not a reason to delete blind.
4. Record the freed bytes, measured.

### T2 — fix the thing that produced it
Find what wrote that file (start with the runner around `Scripts\ziryab_auto_smoke.lua` and
`Scripts\check_wav.py`; the Lua script itself looks clean). Fix it so the result file holds
what `check_wav.py` prints. Re-run and show the new file's size. A cleanup without this is a
cleanup that runs again next week.

### T3 — verify what is installed, with versions
Launch or version-query each, and promote or demote the report's rows on evidence:
REAPER, MuseScore Studio 4, Decent Sampler, SINE Player, **Sonic Visualiser** (installed by
Human Authority at ~17:45Z, never yet launched), Audacity 3.7.9 portable at
`Tools\Audacity-3.7.9\audacity-win-3.7.9-64bit\Audacity.exe`, Python, Git, Node, Java.
Record real version strings, not the 2026-09-26 provenance figures.

### T4 — re-run the smoke render
Re-run the scripted REAPER render end to end and verify the output WAV with `check_wav.py`.
Record the render's duration, sample rate, channels and whether the audio is non-silent.
A hardware **listening** check still needs a human; do not claim it passed.

### T5 — the machine facts the cloud seat could not get
CPU, RAM, free space on `C:` and `D:`, Windows build, and the audio devices / default output.
These are the `UNAVAILABLE` row of the report.

### T6 — Sonic Visualiser is actually usable
Open one of the existing WAVs in Sonic Visualiser (any render — **not** a Pilot 001 stimulus)
and confirm a spectrogram renders and the Vamp plugin path is found. Installed is not working.

## 4. Do not

- Do not install large sample libraries speculatively.
- Do not reinstall anything that is already present. Audacity is portable and in no registry;
  a registry-only scan will wrongly report it missing. That mistake was anticipated by HERMUZ
  and is the reason this line is here.
- Do not "tidy" folders, rename projects, or reorganise the tree. The empty folder scaffold is
  deliberate.

## 5. Deliver

1. Append a dated section to `ZIRYAB_STUDIO_LOCAL_READINESS_REPORT.md` with what you ran, what
   you measured, what failed, and what remains — evidence classes on every claim.
2. One letter to `Memory/Family_House/Mail/HERMUZ/` (he owns the spot checks) and one to
   `Memory/Family_House/Mail/ARGO/` with the stage routing.
3. Push the branch. Do not merge to `main`.
4. Report failed attempts and uncertainty. A clean report with a hidden failure is worse than
   a messy one.

## 6. Needs Human Authority, not you

- **Instrument libraries.** `Provenance\starter_library_activation_status.json` records
  `sineplayer: NOT_DETECTED_ACCOUNT_INSTALL_REQUIRED`. SINE needs his login and a claim;
  Decent Samples needs its official download flow; Komplete Start needs Native Access. These
  are account and licence actions. Prepare the ground, then hand him a short list of exactly
  what to click. Do not claim a licence in his name.
- **Listening verification.** Needs his ears.

Everything else proceeds without asking.

## 7. Routing

```
CURRENT STAGE:         ZIRYAB LOCAL STUDIO READINESS — execution
CURRENT OWNER:         CLAUDE / LOCAL RUNTIME
EXIT CONDITION:        T1-T6 done or explicitly blocked with a reason; report appended;
                       letters sent; branch pushed
NEXT OWNER:            HERMUZ for independent spot checks
HUMAN ACTION REQUIRED: NONE, except the two items in §6
```

One last thing, from the seat that wrote this. The studio is not short of software — it is
short of instruments, and instruments are behind accounts. So the real win here is not the
install list. It is leaving the bench in a state where the moment he logs in once, there is
somewhere for the sound to go.
