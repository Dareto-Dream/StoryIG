import librosa
import json
import random

# === CONFIG ===
input_file = "assets/minigame/songs/song2.mp3"
output_json = "assets/minigame/songs/song2.json"
directions = ['left', 'down', 'up', 'right']
singers = ['player', 'opponent']
sensitivity = 0.5  # lower = more notes
hold_chance = 0.2  # 20% of notes are long notes
min_hold = 300     # ms
max_hold = 1000    # ms

# === Load audio & detect beats ===
y, sr = librosa.load(input_file, sr=None)
tempo, beat_frames = librosa.beat.beat_track(y=y, sr=sr, trim=False)
beat_times = librosa.frames_to_time(beat_frames, sr=sr)
beat_ms = [int(bt * 1000) for bt in beat_times]

# === Generate chart ===
chart = []
last_time = -9999
for t in beat_ms:
    if t - last_time > sensitivity * 100:  # basic spam limiter
        note = {
            "time": t,
            "dir": random.choice(directions),
            "singer": random.choice(singers)
        }
        if random.random() < hold_chance:
            note["hold"] = random.randint(min_hold, max_hold)
        chart.append(note)
        last_time = t

# === Save chart ===
with open(output_json, "w") as f:
    json.dump(chart, f, indent=4)

print(f"Generated {len(chart)} notes from {input_file}")
