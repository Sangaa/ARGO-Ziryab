from __future__ import annotations
import json
import wave
from pathlib import Path

path = Path(r"%ZIRYAB_STUDIO%\\Projects\\ZRY-I2-FUR-ELISE-001\\Renders\\ZRY-I2-FUR-ELISE-001-NYLON-TAKE-06-GATE80-SORTED.wav")
with wave.open(str(path), "rb") as wav:
    channels = wav.getnchannels()
    width = wav.getsampwidth()
    rate = wav.getframerate()
    frames = wav.getnframes()
    raw = wav.readframes(frames)
if width != 3:
    raise SystemExit(f"Unexpected sample width: {width}")
values = [int.from_bytes(raw[i:i+3], "little", signed=True) for i in range(0, len(raw), 3)]
peak = max((abs(v) for v in values), default=0)
window_frames = max(1, rate // 20)  # 50 ms
window_samples = window_frames * channels
activity = []
for i in range(0, len(values), window_samples):
    block = values[i:i+window_samples]
    block_peak = max((abs(v) for v in block), default=0)
    if block_peak:
        activity.append({"start_s": round((i // channels) / rate, 3), "peak": block_peak})
slot_frames = round(rate * 60 / 72 / 4)  # one sixteenth at declared 72 BPM
slot_metrics = []
for note in range(6):
    start = note * slot_frames * channels
    block = values[start:start + slot_frames * channels]
    slot_metrics.append({"note_slot": note + 1, "start_s": round(note * slot_frames / rate, 3), "peak": max((abs(v) for v in block), default=0), "nonzero_samples": sum(v != 0 for v in block)})
print(json.dumps({
    "file": str(path),
    "bytes": path.stat().st_size,
    "channels": channels,
    "sample_rate": rate,
    "sample_width_bytes": width,
    "frames": frames,
    "duration_s": round(frames / rate, 6),
    "absolute_sample_peak": peak,
    "nonzero_samples": sum(v != 0 for v in values),
    "active_50ms_windows": activity,
    "expected_note_slot_metrics": slot_metrics
}, indent=2))

