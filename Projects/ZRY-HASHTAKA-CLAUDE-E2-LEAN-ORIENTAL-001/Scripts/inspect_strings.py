import re, pathlib, statistics
t=pathlib.Path(r"%ZIRYAB_STUDIO%\\Projects\\ZRY-HASHTAKA-CLAUDE-D-REAL-BAND-001\\Scripts\\score_events.lua").read_text(encoding="utf-8")
m=re.search(r'\["Helix_Strings"\]\s*=\s*\{(.*?)\n\s*\},',t,re.S)
print("matched",bool(m))
ev=[(float(a),float(b),int(n),int(v)) for a,b,n,v in re.findall(r'\{([0-9.]+),([0-9.]+),(\d+),(\d+)\}',m.group(1))]
print("count",len(ev),"min",min(x[2] for x in ev),"max",max(x[2] for x in ev))
print("dur_med",statistics.median(x[1]-x[0] for x in ev),"dur_max",max(x[1]-x[0] for x in ev))
print("notes",sorted(set(x[2] for x in ev)))
