# ARGO — Ziryab

Egyptian rhythm and ensemble work, built programmatically: scores, generators, and the
records of what each attempt actually produced.

Named for Ziryab, the 9th-century oud player and composer of Córdoba.

---

## ده إيه (بالعربي)

شغل زرياب: إيقاع مصري وتأليف للآلات، **مبني بالكود** — نوتات، ومولّدات، وسجل بيقول كل
محاولة طلّعت إيه فعلًا.

53 مشروع، أغلبهم **مدرسة الطبلة**: مقسوم، بلدي، صعيدي، ملفوف، أيوب — كل إيقاع بدرسه
وتنويعاته واختبارات هويته (هل البلدي والمقسوم يتفرقوا بالسمع ولا لأ). وفيهم مشاريع
تأليف: «أول نَفَس» بتلات مراحل، و«هشتكة» بتشكيلات مختلفة، و«أورغن الليل» بتلات نسخ.

**والحاجة الوحيدة اللي مش هنا هي الصوت نفسه** — وده **قرار لسه ماتاخدش**، مش سياسة.
مين يحدد أي رندر يستاهل ينشر؟ **زرياب**، الكرسي اللي عمله. مش أنا ومش حد تاني.

---

## What is NOT here, said first

**There is not one audio file in this repository.** No `.wav`, no `.mp3`, no `.flac`.

The renders live on the studio machine and are deliberately untracked — they are large, and
several depend on licensed sample libraries that cannot be redistributed. So what you have
here is **the scores and the machines that make them**, not the music.

That is worth stating plainly rather than letting a visitor discover it: a repository of
rhythm pedagogy with no sound in it is a surprising thing, and the surprise is the point of
this paragraph.

**And the absence is an open decision, not a policy.** Which renders are worth publishing is
ZIRYAB's call — the seat that made them — and it has not been made yet. Nothing here should
be read as a judgement that the work is not ready; it is a judgement that the judgement
belongs to someone else. When audio arrives, it arrives because Ziryab chose it.

Also not here, because it belongs to one machine rather than to the work: the local binary
manifest, sample-library activation state, REAPER `.rpp` session files, install logs, and
the bookmark list of where free instrument libraries are downloaded from.

## What IS here

| | |
| --- | --- |
| 53 projects under `Projects/` | each with its generator, its score data and its provenance record |
| 88 Python + 45 Lua scripts | the generators and the REAPER automation that renders them |
| 36 MIDI files, 2 MusicXML | the scores themselves |
| `Analysis/` | a darbuka sample articulation audit — classifying 8514 hits into dum / tak / pa |
| `RENDER_DETERMINISM_FINDING.md` | the one result in here that is a finding rather than a piece |

### The rhythm school

Most of the 53 projects are `ZRY-TABLA-SCHOOL-*`: one per Egyptian rhythm, with lessons,
variations, and **identity tests** — asking whether two rhythms are actually distinguishable
by ear rather than only on paper. `IDENTITY-MAQSUM-vs-BALADI`, `IDENTITY-3WAY`,
`BALADI-IDENTITY`, `SAIDI-IDENTITY`. The question each one asks is a real question.

### The composition line

`ZRY-FIRST-BREATH-001/002/003` is one piece in three stages, each stage its own project so
the earlier version is never overwritten. `ZRY-HASHTAKA-*` is the same idea across
ensembles: a real band, an oriental band, a lean oriental band, a percussion lab.
`ZRY-NIGHT-ORGAN-001/002/003` and `ZRY-NYLON-TABLA-001` are smaller pieces.

`ZRY-I2-FUR-ELISE-001` is a study, not a piece: the opening bar of a public-domain
composition used as a fixed reference for testing the render path. Its eight takes are
preserved, including the failures — `Provenance/RENDER_FAILURES.md` is the useful file.

## The one finding

[`RENDER_DETERMINISM_FINDING.md`](RENDER_DETERMINISM_FINDING.md)

Two renders of the same project, same script, same inputs, gave an **identical byte count of
1,588,290 and different bytes**. The render path is not deterministic. Dither on the 24-bit
render is the likely cause and is recorded as `EVIDENCE CLASS: UNAVAILABLE` — unverified, and
nobody should assert it without checking.

The second half of that record is the part worth reading: the re-run that produced the
measurement had already **overwritten the artifact it was comparing against**, because the
work order said to re-run the generator and said nothing about preserving the previous
output. The old file survives only as a hash inside a recovered summary. It is logged as a
defect in the instruction, not in the hand that followed it.

[`RENDER_DETERMINISM_PROTOCOL.md`](RENDER_DETERMINISM_PROTOCOL.md) is what came out of it.

## Running any of this

The scripts were written against one machine and have been made portable. Two paths that
used to be hard-coded are now environment variables:

```sh
ZIRYAB_STUDIO=/path/to/studio-root      # where Projects/ and Renders/ live
ZIRYAB_SAMPLES=/path/to/raw-samples     # the unprocessed percussion samples
```

477 occurrences across 160 files were rewritten to `%ZIRYAB_STUDIO%` / `%ZIRYAB_SAMPLES%`.
Paths under `C:\Program Files\` were left alone: REAPER, Audacity, MuseScore and FL Studio
sit in the same place on every Windows machine, and knowing which tool a script drives is
documentation rather than a detail about one computer.

A separate repair: 17 files carried a UTF-8 BOM from PowerShell, and **8 of them did not
parse at all** — 7 Python scripts and 1 JSON file, broken before this publication and broken
in the private repository they came from. The BOM is stripped here, so 88/88 Python files and
57/57 JSON files now parse. The private originals are unchanged and still carry the defect.

The sample libraries several projects reference are licensed and are not distributed with
this repository. Those projects will not render without them.

## Provenance

Published from the private studio repository `ziryab_studio` with **no history** — one
initial commit — so nothing beyond what is listed here can be recovered from it. The studio
itself stays private: it is a workbench, and a workbench describes one machine.

Part of the ARGO house, alongside
[ARGO-Research](https://github.com/Sangaa/ARGO-Research) (scientific records) and
[ARGO-Library](https://github.com/Sangaa/ARGO-Library) (transferable experience).
