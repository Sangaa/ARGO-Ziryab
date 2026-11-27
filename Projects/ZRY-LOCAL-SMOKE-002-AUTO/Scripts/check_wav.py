import sys, wave, json, hashlib
p=sys.argv[1]
out={"wave_readable":False,"nonzero_audio_bytes":False}
try:
    with wave.open(p,"rb") as w:
        frames=w.readframes(w.getnframes())
        out["wave_readable"]=True
        out["channels"]=w.getnchannels()
        out["sample_rate"]=w.getframerate()
        out["sample_width"]=w.getsampwidth()
        out["frames"]=w.getnframes()
        out["nonzero_audio_bytes"]=any(b != 0 for b in frames)
        # Hash of the PCM frames only: REAPER's bext chunk carries the render time, so the
        # whole-file hash changes on every render even when the audio is identical.
        out["audio_sha256"]=hashlib.sha256(frames).hexdigest()
except Exception as e:
    out["error"]=str(e)
print(json.dumps(out))
