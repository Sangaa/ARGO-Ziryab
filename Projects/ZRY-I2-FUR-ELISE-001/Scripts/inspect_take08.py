from pathlib import Path
import json
import wave

path = Path(r"%ZIRYAB_STUDIO%\\Projects\\ZRY-I2-FUR-ELISE-001\\Renders\\ZRY-I2-FUR-ELISE-001-NYLON-TAKE-08-ISOLATED-PITCHES-EXTENDED.wav")
starts = [0.0, 2.5, 5.0, 7.5, 10.0, 12.5]
with wave.open(str(path), "rb") as wav:
    channels, width, rate, frames = wav.getnchannels(), wav.getsampwidth(), wav.getframerate(), wav.getnframes()
    raw = wav.readframes(frames)
if width != 3:
    raise SystemExit(f"Unexpected sample width: {width}")
samples = [int.from_bytes(raw[i:i+3], "little", signed=True) for i in range(0, len(raw), 3)]
metrics = []
for idx, start in enumerate(starts):
    a = round(start * rate) * channels
    b = round((start + 0.5) * rate) * channels
    block = samples[a:b]
    metrics.append({"note_index": idx+1, "window_start_s": start, "peak": max(map(abs, block), default=0), "nonzero_channel_samples": sum(x != 0 for x in block)})
print(json.dumps({
    "file": str(path), "bytes": path.stat().st_size, "duration_s": round(frames/rate, 6),
    "channels": channels, "sample_rate": rate, "sample_width_bytes": width,
    "overall_peak": max(map(abs, samples), default=0), "nonzero_channel_samples": sum(x != 0 for x in samples),
    "isolated_pitch_windows": metrics
}, indent=2))

