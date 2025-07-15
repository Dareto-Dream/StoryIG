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

    def _note_is_active(self, n, current_time):
        # Remove tap notes if hit or missed
        if not n.is_hold():
            return not n.hit and not n.missed
        # For hold notes, keep until tail time passes + a small fudge (for scroll-off), or missed and tail is gone
        tail_gone = current_time > n.get_tail_time() + 200
        return (not n.missed and not tail_gone) or (n.missed and not tail_gone)

    def add_note(self, note):
        """Add a new note to the correct lane"""
        # print(f"Spawning {note.direction} at {note.time_ms}")
        self.notes_by_lane[note.direction].append(note)

    def update(self, current_time):
        """Clean up old notes, sort lanes, and handle hold-miss logic."""
        for lane in self.notes_by_lane:
            self.notes_by_lane[lane] = [
                n for n in self.notes_by_lane[lane]
                if self._note_is_active(n, current_time)
            ]
            self.notes_by_lane[lane].sort(key=lambda n: n.time_ms)
            for note in self.notes_by_lane[lane]:
                # FNF hold logic: If this is a hold note, was hit, but not being held, and it's not finished yet
                if note.is_hold() and note.hit and not note.held and not note.missed:
                    if current_time < note.get_tail_time():
                        note.missed = True
                        note.hold_judgement = 'miss'
                        print(f"Hold note missed early on {lane} at {current_time}")

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

                # FNF hold note logic: Only start "held" if we hit the head!
                if note.is_hold():
                    note.held = True

                return True
            else:
                # Too late? mark as missed
                if press_time - 20 > note.time_ms + self.judgement.window("miss"):
                    note.missed = True
                break

        return False

    def handle_key_release(self, direction):
        self.arrow_handler.release(direction)
        self.player_animator.release()

def render_notes(
    screen,
    note_handler,
    song_time,
    hit_y,
    arrow_frames,
    lane_positions,
    section_list,
    base_pixels_per_beat
):
    NOTE_SPAWN_TIME = 2500  # ms

    for direction, notes in note_handler.notes_by_lane.items():
        x = lane_positions[direction]
        frameset = arrow_frames[direction]

        for note in notes:
            time_until_hit = note.time_ms - song_time
            if time_until_hit > NOTE_SPAWN_TIME:
                continue # Too early to show this note
            if note.time_ms + 75 < song_time and (not note.is_hold() or song_time > note.get_tail_time()):
                continue  # Tap note already passed, or hold note completely finished

            # HEAD Y position (where you hit the note)
            y_head = note.get_screen_y(song_time, hit_y, base_pixels_per_beat)
            # For hold notes, TAIL Y (where you finish holding)
            y_tail = note.get_tail_screen_y(song_time, hit_y, base_pixels_per_beat) if note.is_hold() else y_head

            # Only render visible range
            if y_head > screen.get_height() + 100 or y_tail < -100:
                continue

            # RENDER HOLD BAR (between head and tail, below head and above tail)
            if note.is_hold():
                hold_piece = frameset.get("hold_piece")
                hold_end = frameset.get("hold_end")
                if hold_piece is not None and hold_end is not None:
                    piece_height = hold_piece.get_height()

                    head_y = note.get_screen_y(song_time, hit_y, base_pixels_per_beat)
                    tail_y = note.get_tail_screen_y(song_time, hit_y, base_pixels_per_beat)

                    if note.hit and note.held and not note.missed:
                        # Being held: bar starts at receptor (hit_y), not at head_y
                        y_top = hit_y
                    else:
                        # Not held (yet), or missed: bar starts at head_y
                        y_top = head_y

                    y_bot = tail_y

                    # Ensure correct direction
                    if y_top > y_bot:
                        y_top, y_bot = y_bot, y_top

                    if y_bot - y_top > 0:
                        y_pos = y_top
                        while y_pos < y_bot - piece_height:
                            rect = hold_piece.get_rect(center=(x, int(y_pos + piece_height / 2)))
                            screen.blit(hold_piece, rect.topleft)
                            y_pos += piece_height
                        # Draw end cap/tail at y_bot
                        rect_end = hold_end.get_rect(center=(x, int(y_bot)))
                        screen.blit(hold_end, rect_end.topleft)

            # RENDER HEAD (flash sprite for now, can switch to state-based)
            sprite = frameset['flash']
            note.draw(screen, song_time, hit_y, sprite, x, base_pixels_per_beat)