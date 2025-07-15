from tools.note import Note

class ChartHandler:
    def __init__(self, chart_data):
        """
        chart_data: list of dicts like:
            [{ "direction": "left", "time": 1000, "bpm": 120, "song_speed": 1.0 }, ...]
        """
        self.chart = sorted(chart_data, key=lambda n: n["time"])
        self.index = 0  # current spawn index

    def update(self, song_time, note_handler, prebuffer=1000):
        """
        Spawns notes up to (song_time + prebuffer).
        Passes them to NoteHandler.add_note().
        """
        while self.index < len(self.chart):
            note_info = self.chart[self.index]
            if note_info["time"] <= song_time + prebuffer:
                # Now passes bpm and song_speed per note
                note = Note(
                    direction=note_info["direction"],
                    time_ms=note_info["time"],
                    bpm=note_info["bpm"],
                    song_speed=note_info["song_speed"],
                    sustain_ms=note_info.get("sustain", 0)  # Pass sustain_ms!
                )
                note_handler.add_note(note)
                self.index += 1
            else:
                break
