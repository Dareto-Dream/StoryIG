import json

def load_fnf_chart(path):
    """Loads an FNF-style JSON and returns bpm, song_speed, player_notes, opponent_notes, song_meta, section_list"""
    with open(path, 'r') as f:
        raw = json.load(f)
    song = raw.get("song", {})
    global_bpm = song.get("bpm", 120)
    global_speed = song.get("speed", song.get("songSpeed", 1.0))
    sections = song["notes"]
    player_notes, opponent_notes = split_fnf_chart_sections_with_bpm_speed(
        sections, global_bpm, global_speed
    )
    section_list = build_section_table(sections, global_bpm, global_speed)
    return global_bpm, global_speed, player_notes, opponent_notes, song, section_list

def split_fnf_chart_sections_with_bpm_speed(sections, global_bpm, global_speed):
    player_notes = []
    opponent_notes = []
    direction_map = {
        0: "left", 1: "down", 2: "up", 3: "right",
        4: "left", 5: "down", 6: "up", 7: "right"
    }

    current_bpm = global_bpm
    current_speed = global_speed

    for section in sections:
        # Per-section BPM/scroll speed logic
        if section.get("changeBPM"):
            current_bpm = section.get("bpm", current_bpm)
        if "scrollSpeed" in section:
            current_speed = section["scrollSpeed"]

        must_hit = section.get("mustHitSection", False)
        for note in section.get("sectionNotes", []):
            time, lane, sustain = note
            note_obj = {
                "direction": direction_map[lane],
                "time": int(time),
                "sustain": sustain,
                "bpm": current_bpm,
                "song_speed": current_speed,
            }
            if must_hit:
                if lane in (0, 1, 2, 3):
                    player_notes.append(note_obj)
                elif lane in (4, 5, 6, 7):
                    opponent_notes.append(note_obj)
            else:
                if lane in (0, 1, 2, 3):
                    opponent_notes.append(note_obj)
                elif lane in (4, 5, 6, 7):
                    player_notes.append(note_obj)
    return player_notes, opponent_notes

def build_section_table(sections, global_bpm, global_speed):
    section_list = []
    current_time = 0
    for section in sections:
        bpm = section.get("bpm", global_bpm)
        scroll_speed = section.get("scrollSpeed", global_speed)
        length_steps = section.get("lengthInSteps", 16)
        # In FNF: 4 steps = 1 beat, so 16 steps = 4 beats
        beats = length_steps / 4
        beat_time = 60000 / bpm
        section_length_ms = beats * beat_time
        section_dict = {
            "start_time": int(current_time),
            "end_time": int(current_time + section_length_ms),
            "bpm": bpm,
            "scroll_speed": scroll_speed
        }
        section_list.append(section_dict)
        current_time += section_length_ms

    for i, sec in enumerate(section_list):
        print(
            f"Section {i}: start={sec['start_time']}ms, end={sec['end_time']}ms, bpm={sec['bpm']}, speed={sec['scroll_speed']}")

    return section_list

# If I add more formats:
def load_stepmania_chart(path):
    """Placeholder for StepMania .sm parser."""
    pass

def load_osu_chart(path):
    """Placeholder for Osu!mania .osu parser."""
    pass

# --- Main entrypoint for loading any chart ---
def load_chart(path, fmt="fnf"):
    if fmt == "fnf":
        return load_fnf_chart(path)
    elif fmt == "stepmania":
        return load_stepmania_chart(path)
    elif fmt == "osu":
        return load_osu_chart(path)
    else:
        raise ValueError(f"Unsupported chart format: {fmt}")
