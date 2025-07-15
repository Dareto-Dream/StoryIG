from tools.note import get_screen_y_fnf

class NoteHandler:
    def __init__(self, judgement, arrow_handler, player_animator):
        self.judgement = judgement
        self.arrow_handler = arrow_handler
        self.player_animator = player_animator

        self.notes_by_lane = {
            'left': [],
            'down': [],
            'up': [],
            'right': []
        }

    def add_note(self, note):
        """Add a new note to the correct lane"""
        # print(f"Spawning {note.direction} at {note.time_ms}")
        self.notes_by_lane[note.direction].append(note)

    def update(self, current_time):
        """Clean up old notes, sort lanes"""
        for lane in self.notes_by_lane:
            self.notes_by_lane[lane] = [
                n for n in self.notes_by_lane[lane]
                if not n.hit and not n.missed
            ]
            self.notes_by_lane[lane].sort(key=lambda n: n.time_ms)

    def handle_key_press(self, direction, press_time):
        """Handle a key press and return True if a note was hit."""
        lane = self.notes_by_lane.get(direction, [])
        if not lane:
            return False

        for note in lane:
            if note.hit or note.missed:
                continue

            result = self.judgement.evaluate(note, press_time)
            print("You've Been Judged:", result)

            if result != "miss":
                note.hit = True
                note.judgement = result

                self.arrow_handler.press(direction, with_note=True, judgement=result)
                self.player_animator.play(direction)

                return True
            else:
                # Too late? mark as missed
                if press_time > note.time_ms + self.judgement.window("miss"):
                    note.missed = True
                break

        return False

    def handle_key_release(self, direction):
        self.arrow_handler.release(direction)
        self.player_animator.release()

def render_notes(screen, note_handler, song_time, hit_y, arrow_frames, lane_positions, section_list, base_pixels_per_beat):
    NOTE_SPAWN_TIME = 2500  # ms

    for direction, notes in note_handler.notes_by_lane.items():
        x = lane_positions[direction]
        sprite = arrow_frames[direction]['flash']

        for note in notes:
            time_until_hit = note.time_ms - song_time
            if time_until_hit > NOTE_SPAWN_TIME:
                continue # Too early to show this note
            if note.time_ms < song_time:
                continue  # Note already passed (missed or hit)

            y = get_screen_y_fnf(note.time_ms, song_time, hit_y, section_list)
            if y < 0 or y > screen.get_height() + 100:
                continue

            note.draw(screen, song_time, hit_y, sprite, x, base_pixels_per_beat)