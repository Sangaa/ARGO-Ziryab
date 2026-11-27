import json
from pathlib import Path
score=json.loads(Path(r"%ZIRYAB_STUDIO%\Projects\ZRY-NYLON-TABLA-001\Provenance\score.json").read_text(encoding="utf-8"))
out=["return {"]
for key in ("guitar","bass"):
    out.append(f'  ["{key}"]={{')
    for a,b,n,v in score[key]:
        out.append(f"    {{{a:.9f},{b:.9f},{n},{v}}},")
    out.append("  },")
out.append("}")
Path(r"%ZIRYAB_STUDIO%\Projects\ZRY-NYLON-TABLA-001\Scripts\score_events.lua").write_text("\n".join(out),encoding="utf-8")
print("wrote",len(score["guitar"]),len(score["bass"]))
