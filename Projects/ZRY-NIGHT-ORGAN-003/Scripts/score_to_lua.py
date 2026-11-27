import json
from pathlib import Path
s=json.loads(Path(r"%ZIRYAB_STUDIO%\Projects\ZRY-NIGHT-ORGAN-003\Provenance\score_v3.json").read_text(encoding="utf-8"))
out=["return {"]
for key in ("organ",):
    out.append(f'  ["{key}"]={{')
    for a,b,n,v in s[key]:
        out.append(f"    {{{a:.9f},{b:.9f},{n},{v}}},")
    out.append("  },")
out.append("}")
Path(r"%ZIRYAB_STUDIO%\Projects\ZRY-NIGHT-ORGAN-003\Scripts\score_events.lua").write_text("\n".join(out),encoding="utf-8")
print("organ",len(s["organ"]))
