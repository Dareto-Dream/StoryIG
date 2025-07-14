class Note:
    def __init__(self, direction, time_ms, bpm, song_speed):
        self.direction = direction
        self.time_ms = time_ms
        self.hit = False
        self.missed = False
        self.judgement = None
        self.bpm = bpm
        self.song_speed = song_speed

    def get_screen_y(self, song_time, hit_y, base_pixels_per_beat=100):
        beat_time = 60000 / self.bpm
        pixels_per_beat = base_pixels_per_beat * self.song_speed
        pixels_per_ms = pixels_per_beat / beat_time
        distance = self.time_ms - song_time
        return hit_y + distance * pixels_per_ms

    def draw(self, screen, song_time, hit_y, sprite, center_x, base_pixels_per_beat=100):
        if self.hit or self.missed:
            return
        y = self.get_screen_y(song_time, hit_y, base_pixels_per_beat)
        rect = sprite.get_rect(center=(center_x, int(y)))
        screen.blit(sprite, rect.topleft)

def get_screen_y_fnf(note_time, song_time, hit_y, section_list, base_pixels_per_beat=100):
    # Find current and next section
    current_section = None
    next_section = None
    for i, section in enumerate(section_list):
        if section['start_time'] <= song_time < section['end_time']:
            current_section = section
            if i + 1 < len(section_list):
                next_section = section_list[i + 1]
            break
    if not current_section:
        # fallback: use the first section
        current_section = section_list[0]

    section_end = current_section['end_time']

    if note_time <= section_end or not next_section:
        # Note is in current section
        dt = note_time - song_time
        beat_time = 60000 / current_section['bpm']
        pixels_per_beat = base_pixels_per_beat * current_section['scroll_speed']
        pixels_per_ms = pixels_per_beat / beat_time
        return hit_y + dt * pixels_per_ms
    else:
        # Note traverses both sections
        dt0 = section_end - song_time
        dt1 = note_time - section_end
        # Segment 1 (current section)
        beat_time0 = 60000 / current_section['bpm']
        pixels_per_beat0 = base_pixels_per_beat * current_section['scroll_speed']
        pixels_per_ms0 = pixels_per_beat0 / beat_time0
        # Segment 2 (next section)
        beat_time1 = 60000 / next_section['bpm']
        pixels_per_beat1 = base_pixels_per_beat * next_section['scroll_speed']
        pixels_per_ms1 = pixels_per_beat1 / beat_time1
        # Total scroll
        return hit_y + dt0 * pixels_per_ms0 + dt1 * pixels_per_ms1
