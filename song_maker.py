import librosa
import json
import random

# === CONFIG ===
input_file = "assets/minigame/songs/song1.mp3"
output_json = "assets/minigame/songs/song1.json"
directions = ['left', 'down', 'up', 'right']
sensitivity = 1.0  # lower = more notes

# === Load audio & detect beats ===
y, sr = librosa.load(input_file, sr=None)
tempo, beat_frames = librosa.beat.beat_track(y=y, sr=sr, trim=False)
beat_times = librosa.frames_to_time(beat_frames, sr=sr)
beat_ms = [int(bt * 1000) for bt in beat_times]

# === Generate chart ===
chart = []
last_time = -9999
for t in beat_ms:
    if t - last_time > sensitivity * 100:  # simple spam limiter
        print("note!")
        chart.append({
            "time": t,
            "dir": random.choice(directions)
        })
        last_time = t

# === Save chart ===
with open(output_json, "w") as f:
    json.dump(chart, f, indent=4)

print(f"Generated {len(chart)} notes from {input_file}")
