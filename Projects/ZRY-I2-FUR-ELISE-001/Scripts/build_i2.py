from __future__ import annotations

import hashlib
import json
import re
import struct
from pathlib import Path

ROOT = Path(r"%ZIRYAB_STUDIO%\Projects\ZRY-I2-FUR-ELISE-001")
TEMPLATE = Path(r"%ZIRYAB_STUDIO%\Projects\ZRY-LOCAL-SINE-ENSEMBLE-001\ZRY-LOCAL-SINE-ENSEMBLE-001.rpp")
STUDY = "ZRY-I2-FUR-ELISE-001"
OUT_WAV = ROOT / "Renders" / f"{STUDY}-NYLON-TAKE-04.wav"
RENDER_DIR = ROOT / "Renders"
RENDER_PATTERN = OUT_WAV.stem
RPP_OUT = ROOT / f"{STUDY}.rpp"
MIDI_OUT = ROOT / "MIDI" / f"{STUDY}-OPENING-BAR-REFERENCE.mid"
MANIFEST = ROOT / "Provenance" / "study_manifest.json"

# Beethoven, Für Elise, WoO 59, opening bar as printed in the source score.
# The source marks Poco moto, 3/8, pp. The practice tempo is a declared
# control setting, not a claim about Beethoven's unmarked metronome tempo.
PITCHES = [76, 75, 76, 75, 76, 71]  # E5, D#5, E5, D#5, E5, B4
STUDY_BPM = 72
MIDI_PPQ = 480
REAPER_PPQ = 960
MIDI_SIXTEENTH = MIDI_PPQ // 4
REAPER_SIXTEENTH = REAPER_PPQ // 4
VELOCITY = 48  # one level throughout; dynamics are not varied in this baseline

def vlq(n: int) -> bytes:
    n = max(0, int(n))
    out = [n & 0x7F]
    n >>= 7
    while n:
        out.insert(0, 0x80 | (n & 0x7F))
        n >>= 7
    return bytes(out)

def make_midi() -> bytes:
    events: list[tuple[int, bytes]] = []
    mpqn = round(60_000_000 / STUDY_BPM)
    events += [(0, b"\xff\x51\x03" + mpqn.to_bytes(3, "big"))]
    events += [(0, b"\xff\x58\x04\x03\x03\x18\x08")]  # 3/8
    for i, pitch in enumerate(PITCHES):
        start = i * MIDI_SIXTEENTH
        end = start + MIDI_SIXTEENTH
        events.append((start, bytes([0x90, pitch, VELOCITY])))
        events.append((end, bytes([0x80, pitch, 0])))
    events.sort(key=lambda x: (x[0], 0 if x[1][0] == 0x80 else 1))
    data = bytearray()
    last = 0
    for tick, msg in events:
        data += vlq(tick - last) + msg
        last = tick
    data += vlq(MIDI_SIXTEENTH) + b"\xff\x2f\x00"
    track = b"MTrk" + struct.pack(">I", len(data)) + data
    header = b"MThd" + struct.pack(">IHHH", 6, 0, 1, MIDI_PPQ)
    return header + track

def reaper_events() -> list[str]:
    absolute: list[tuple[int, int, int, int, int]] = []
    for i, pitch in enumerate(PITCHES):
        start = i * REAPER_SIXTEENTH
        end = start + REAPER_SIXTEENTH
        absolute.append((start, 1, 0x90, pitch, VELOCITY))
        absolute.append((end, 0, 0x80, pitch, 0))
    absolute.sort(key=lambda e: (e[0], e[1]))
    lines: list[str] = []
    last = 0
    for tick, _, status, pitch, velocity in absolute:
        lines.append(f"        E {tick-last} {status:02x} {pitch:02x} {velocity:02x}")
        last = tick
    return lines

def make_rpp() -> str:
    if not TEMPLATE.is_file():
        raise FileNotFoundError(TEMPLATE)
    text = TEMPLATE.read_text(encoding="utf-8", errors="replace")
    parts = re.split(r"(?m)(?=^  <TRACK \{)", text)
    track_parts = [p for p in parts if re.match(r"(?m)^  <TRACK \{", p)]
    if not track_parts:
        raise RuntimeError("No root-level REAPER tracks found in template")
    nylon = [p for p in track_parts if re.search(r"(?m)^    NAME Strand_Nylon\s*$", p)]
    if len(nylon) != 1:
        raise RuntimeError(f"Expected one Strand_Nylon track, found {len(nylon)}")
    track = nylon[0]
    source_match = re.search(r"(?ms)^      <SOURCE MIDI\n(.*?)^      >", track)
    if not source_match:
        raise RuntimeError("No embedded MIDI source found on Strand_Nylon")
    source = source_match.group(1)
    source = re.sub(r"(?m)^        HASDATA .*?$", "        HASDATA 1 1680 QN", source)
    source = re.sub(r"(?m)^        E .*?$", "", source)
    insert_at = source.find("\n")
    source = source[:insert_at+1] + "\n".join(reaper_events()) + "\n" + source[insert_at+1:]
    track = track[:source_match.start(1)] + source + track[source_match.end(1):]
    track = re.sub(r"(?m)^      LENGTH .*?$", "      LENGTH 2.500000000000000", track, count=1)
    track = re.sub(r"(?m)^      LOOP 1\s*$", "      LOOP 0", track, count=1)

    starts = [m.start() for m in re.finditer(r"(?m)^  <TRACK \{", text)]
    if not starts:
        raise RuntimeError("No root-level track blocks found")
    last_end = None
    depth = 0
    pos = starts[-1]
    for line in text[pos:].splitlines(keepends=True):
        stripped = line.strip()
        if stripped.startswith("<"):
            depth += 1
        elif stripped == ">":
            depth -= 1
        pos += len(line)
        if depth == 0:
            last_end = pos
            break
    if last_end is None:
        raise RuntimeError("Could not find end of final root-level track")
    prefix = text[:starts[0]]
    suffix = text[last_end:]
    text = prefix + track + suffix
    if len(re.findall(r"(?m)^  <TRACK \{", text)) != 1:
        raise RuntimeError("Isolation failed: RPP must contain one root-level track")
    text = re.sub(r'(?m)^  RENDER_FILE ".*?"$', f'  RENDER_FILE "{RENDER_DIR.as_posix()}"', text, count=1)
    if re.search(r'(?m)^  RENDER_PATTERN ".*?"$', text):
        text = re.sub(r'(?m)^  RENDER_PATTERN ".*?"$', f'  RENDER_PATTERN "{RENDER_PATTERN}"', text, count=1)
    else:
        text = re.sub(r'(?m)^  RENDER_FILE ".*?"$', f'  RENDER_FILE "{RENDER_DIR.as_posix()}"\n  RENDER_PATTERN "{RENDER_PATTERN}"', text, count=1)
    text = re.sub(r"(?m)^  RENDER_RANGE .*?$", "  RENDER_RANGE 0 0 2 0 1000", text, count=1)
    text = re.sub(r"(?m)^  TEMPO .*?$", f"  TEMPO {STUDY_BPM} 3 8 0", text, count=1)
    return text

def main() -> None:
    (ROOT / "MIDI").mkdir(parents=True, exist_ok=True)
    (ROOT / "Renders").mkdir(parents=True, exist_ok=True)
    (ROOT / "Provenance").mkdir(parents=True, exist_ok=True)
    midi = make_midi()
    MIDI_OUT.write_bytes(midi)
    rpp = make_rpp()
    RPP_OUT.write_text(rpp, encoding="utf-8", newline="\r\n")
    (ROOT / "Scripts" / "build_i2.py").write_text(Path(__file__).read_text(encoding="utf-8"), encoding="utf-8")
    manifest = {
        "study_id": STUDY,
        "lane": "I2 NYLON GUITAR FOUNDATION + KNOWN-PIECE IMITATION",
        "status": "REFERENCE_SCORE_AND_MIDI_CREATED; RENDER_NOT_YET_VERIFIED",
        "source": {
            "composer": "Ludwig van Beethoven",
            "work": "Für Elise, WoO 59",
            "excerpt": "opening bar, E5-D#5-E5-D#5-E5-B4",
            "score_url": "https://commons.wikimedia.org/wiki/File:IMSLP103834-PMLP14377-F%C3%BCr_Elise,_Beethoven-WoO.059,_1867.pdf",
            "source_edition": "1867 scan; score marks Poco moto, 3/8, opening dynamic pp",
            "composition_status": "public domain per source page; no modern edition or recording copied",
        },
        "study_controls": {
            "tempo_bpm_quarter_note": STUDY_BPM,
            "meter": "3/8",
            "grid": "six consecutive sixteenth notes",
            "velocity": VELOCITY,
            "instrument": "Strand Nylon SINE Player patch from existing local REAPER template",
            "articulation": "uniform note gate; no ornament, chord, accompaniment, or variation",
            "purpose": "pitch and temporal foundation baseline, not a competence claim",
        },
        "evidence_boundary": {
            "verified": ["score pitch order from the linked score's opening line", "MIDI bytes generated by this script"],
            "not_yet_verified": ["REAPER render", "SINE patch loading in this isolated project", "listening comparison", "imitation pass"],
            "prior_artifact_warning": "Existing nylon/table compositions are arrangement evidence, not known-piece imitation evidence.",
        },
        "artifacts": {
            "midi": str(MIDI_OUT),
            "reaper_project": str(RPP_OUT),
            "planned_render": str(OUT_WAV),
            "midi_sha256": hashlib.sha256(midi).hexdigest(),
        },
    }
    MANIFEST.write_text(json.dumps(manifest, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(json.dumps({
        "midi": str(MIDI_OUT),
        "midi_bytes": len(midi),
        "midi_sha256": hashlib.sha256(midi).hexdigest(),
        "reaper_project": str(RPP_OUT),
        "reaper_project_bytes": RPP_OUT.stat().st_size,
        "render_target": str(OUT_WAV),
        "status": manifest["status"],
    }, indent=2))

if __name__ == "__main__":
    main()
