import json

def load_fnf_chart(path):
    """Loads an FNF-style JSON and returns:
       - song_bpm (float)
       - player_notes (list of dict)
       - opponent_notes (list of dict)
       - song_metadata (dict, optional)
    """
    with open(path, 'r') as f:
        raw = json.load(f)
    song = raw['song']
    bpm = song.get('bpm', 120)
    speed = song.get('speed', song.get('songSpeed', 1.0))  # Default to 1.0 if missing

    sections = song['notes']
    player_notes, opponent_notes = split_fnf_sections(sections)
    return bpm, speed, player_notes, opponent_notes, song

def split_fnf_sections(sections):
    """Splits by both mustHitSection AND lane numbers for max compatibility."""
    player_notes = []
    opponent_notes = []
    direction_map = {
        0: "left", 1: "down", 2: "up", 3: "right",
        4: "left", 5: "down", 6: "up", 7: "right"
    }

    for section in sections:
        must_hit = section.get("mustHitSection", False)
        for note in section.get("sectionNotes", []):
            time, lane, sustain = note
            note_obj = {
                "direction": direction_map.get(lane, str(lane)),
                "time": int(time),
                "sustain": sustain
            }
            # True FNF-style ownership:
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

# If you add more formats:
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
