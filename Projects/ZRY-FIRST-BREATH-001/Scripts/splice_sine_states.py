"""Splice saved SINE Player states into ZRY-FIRST-BREATH-001.rpp.

SINE has no API; the five instruments were loaded by hand once, in
ZRY-LOCAL-SINE-ENSEMBLE-001 (Strand nylon, Lucent, Helix with Sustains active, Crux J-bass)
and ZRY-LOCAL-SINE-RATIO-001 (Ratio piano). Their <VST ...> state blocks are copied here,
track by track. Also sets each MIDI item LENGTH (the setup script got 0 from
GetMediaSourceLength for file-referenced MIDI). Backs up the project first.
"""
import re, sys, shutil, base64, json, datetime, pathlib

proj = pathlib.Path(r"%ZIRYAB_STUDIO%\Projects\ZRY-FIRST-BREATH-001")
rpp = proj / "ZRY-FIRST-BREATH-001.rpp"
ens = pathlib.Path(r"%ZIRYAB_STUDIO%\Projects\ZRY-LOCAL-SINE-ENSEMBLE-001\ZRY-LOCAL-SINE-ENSEMBLE-001.rpp")
rat = pathlib.Path(r"%ZIRYAB_STUDIO%\Projects\ZRY-LOCAL-SINE-RATIO-001\ZRY-LOCAL-SINE-RATIO-001.rpp")
ITEM_LEN = "66.0"   # last note (guitar) ends 65.69 s; LOOP 0 so nothing repeats

sources = {  # target track -> (project, source track)
    "Strand_Nylon":  (ens, "Strand_Nylon"),
    "Lucent_Flute":  (ens, "Lucent_Flute"),
    "Helix_Strings": (ens, "Helix_Strings"),
    "Ratio_Piano":   (rat, "SINE_RATIO_PIANO"),
    "Crux_JBass":    (ens, "Crux_JBass"),
}

def tracks(lines):
    """yield (name, start, end) line index ranges of each <TRACK block (end = index of its closing >)."""
    i = 0
    while i < len(lines):
        if lines[i].startswith("  <TRACK"):
            j = i + 1
            while not lines[j].strip().startswith("NAME "): j += 1
            name = lines[j].strip()[5:].strip('"')
            depth = 1; k = i + 1
            while depth:
                s = lines[k].strip()
                if s.startswith("<"): depth += 1
                elif s == ">": depth -= 1
                k += 1
            yield name, i, k - 1
            i = k
        else:
            i += 1

def vst_block(lines, a, b):
    """(start, end) of the first <VST block inside lines[a:b]; end = closing > line index."""
    for i in range(a, b):
        if lines[i].strip().startswith("<VST "):
            depth = 1; k = i + 1
            while depth:
                s = lines[k].strip()
                if s.startswith("<"): depth += 1
                elif s == ">": depth -= 1
                k += 1
            return i, k - 1
    raise RuntimeError("no VST block")

def state_json(block):
    b64 = [l.strip() for l in block[1:-1] if re.fullmatch(r"[A-Za-z0-9+/=]+", l.strip())]
    raw = b"".join(base64.b64decode(s + "=" * (-len(s) % 4)) for s in b64)
    a = raw.find(b"{"); b = raw.rfind(b"}") + 1
    return json.loads(raw[a:b].decode("utf-8"))

stamp = datetime.datetime.now().strftime("%Y%m%d-%H%M%S")
bak = proj / "Backups" / f"ZRY-FIRST-BREATH-001.pre-splice-{stamp}.rpp"
shutil.copy2(rpp, bak)

cache = {}
def src_lines(p):
    if p not in cache: cache[p] = p.read_text(encoding="utf-8").splitlines()
    return cache[p]

lines = rpp.read_text(encoding="utf-8").splitlines()
report = []
# process tracks from the bottom so earlier indices stay valid
for name, a, b in reversed(list(tracks(lines))):
    sp, sname = sources[name]
    sl = src_lines(sp)
    sa, sb = next((x, y) for n, x, y in tracks(sl) if n == sname)
    va, vb = vst_block(sl, sa, sb)
    new_block = sl[va:vb + 1]
    ta, tb = vst_block(lines, a, b)
    # item length
    for i in range(a, b):
        if lines[i].strip().startswith("LENGTH "):
            lines[i] = re.sub(r"LENGTH .*", "LENGTH " + ITEM_LEN, lines[i])
    lines[ta:tb + 1] = new_block
    j = state_json(new_block)
    ins = j["instruments"][0]
    sel = j["selectedEntry"]
    arts = [(x["title"], x.get("active")) for x in ins["articulations"]]
    report.append(f"{name:14s} <- {sp.stem}/{sname}: instrument={ins['title']!r} selected_art={ins['articulations'][int(sel['articulationIndex'])]['title']!r} active={[t for t,a in arts if a=='true']} keyrange={ins.get('keyRangeLow')}-{ins.get('keyRangeHigh')}")

rpp.write_text("\n".join(lines) + "\n", encoding="utf-8")
out = "\n".join(reversed(report))
print(out)
(proj / "Provenance" / "splice_done.txt").write_text(f"backup={bak.name}\nitem_length={ITEM_LEN}\n{out}\n", encoding="utf-8")
