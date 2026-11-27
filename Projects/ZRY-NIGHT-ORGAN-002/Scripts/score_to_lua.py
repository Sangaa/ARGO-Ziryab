import json
from pathlib import Path
s=json.loads(Path(r"%ZIRYAB_STUDIO%\Projects\ZRY-NIGHT-ORGAN-002\Provenance\score_v2.json").read_text(encoding="utf-8"))
out=["return {"]
for key in ("organ","trumpet","bass"):
    out.append(f'  ["{key}"]={{')
    for a,b,n,v in s[key]:
        out.append(f"    {{{a:.9f},{b:.9f},{n},{v}}},")
    out.append("  },")
out.append("}")
Path(r"%ZIRYAB_STUDIO%\Projects\ZRY-NIGHT-ORGAN-002\Scripts\score_events.lua").write_text("\n".join(out),encoding="utf-8")
print("done")
