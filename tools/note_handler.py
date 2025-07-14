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
        lane = self.notes_by_lane.get(direction, [])
        if not lane:
            return

        for note in lane:
            if note.hit or note.missed:
                continue

            result = self.judgement.evaluate(note, press_time)

            if result != "miss":
                note.hit = True
                note.judgement = result

                self.arrow_handler.press(direction, with_note=True, judgement=result)
                self.player_animator.play(direction)

                break
            else:
                # Too late? mark as missed
                if press_time > note.time_ms + self.judgement.window("miss"):
                    note.missed = True
                break

    def handle_key_release(self, direction):
        self.arrow_handler.release(direction)
        self.player_animator.release()

def render_notes(screen, note_handler, song_time, scroll_speed, hit_y, arrow_frames, lane_positions):
    NOTE_SPAWN_TIME = 2500  # in ms; how early notes can appear

    for direction, notes in note_handler.notes_by_lane.items():
        x = lane_positions[direction]
        sprite = arrow_frames[direction]['flash']  # use bright note color

        for note in notes:
            time_until_hit = note.time_ms - song_time
            if time_until_hit > NOTE_SPAWN_TIME:
                continue  # not time to show yet

            y = note.get_screen_y(song_time, scroll_speed, hit_y)
            if y < 0 or y > screen.get_height() + 100:
                continue  # offscreen

            note.draw(screen, song_time, scroll_speed, hit_y, sprite, x)