from pathlib import Path

src=Path(r"%ZIRYAB_STUDIO%\\Projects\\ZRY-FIRST-BREATH-003-FLUTE-ANSWER\\ZRY-FIRST-BREATH-003-FLUTE-ANSWER.rpp")
dst=Path(r"%ZIRYAB_STUDIO%\\Projects\\ZRY-HASHTAKA-CLAUDE-D-REAL-BAND-001\\ZRY-HASHTAKA-CLAUDE-D-REAL-BAND-001.rpp")

lines=src.read_text(encoding="utf-8-sig",errors="replace").splitlines(True)
out=[]
skip=False
depth=0
removed=0
for line in lines:
    s=line.lstrip()
    if not skip and s.startswith("<ITEM"):
        skip=True
        depth=1
        removed+=1
        continue
    if skip:
        if s.startswith("<"):
            depth+=1
        if s.strip()==">":
            depth-=1
            if depth==0:
                skip=False
        continue
    out.append(line)

dst.write_text("".join(out),encoding="utf-8")
print("removed_items",removed,"lines",len(out))
