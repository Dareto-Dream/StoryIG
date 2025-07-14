import pygame
from tools.chart_handler import ChartHandler
from tools.note_handler import NoteHandler, render_notes
from tools.arrow_handler import ArrowHandler
from tools.character_animations import CharacterAnimator
from tools.judgement import JUDGEMENT_WINDOWS

class LaneManager:
    def __init__(
        self,
        name,
        chart,
        frames,
        animator,
        screen,
        judgement,
        arrow_x,
        hit_y=100,
        is_player=False,
        bpm=120,
        song_speed=1.0,
        section_list=None,
        key_map=None,
        lane_positions=None,
        scroll_speed=0.3
    ):
        self.name = name
        self.is_player = is_player
        self.screen = screen

        self.base_pixels_per_beat = 250
        self.bpm = bpm
        self.song_speed = song_speed

        self.section_list = section_list or []

        self.chart_handler = ChartHandler(chart)
        self.arrow_handler = ArrowHandler(
            arrow_frames=frames,
            position=(arrow_x, hit_y)
        )
        self.note_handler = NoteHandler(
            judgement, self.arrow_handler, animator
        )
        self.animator = animator

        self.hit_y = hit_y
        self.scroll_speed = scroll_speed
        self.key_map = key_map or {}
        self.lane_positions = lane_positions or self.default_lane_positions(arrow_x)
        self.frames = frames

    def default_lane_positions(self, arrow_x):
        spacing = 150
        return {
            'left': arrow_x - spacing * 1.5,
            'down': arrow_x - spacing * 0.5,
            'up':   arrow_x + spacing * 0.5,
            'right':arrow_x + spacing * 1.5
        }

    def update(self, song_time, dt):
        self.chart_handler.update(song_time, self.note_handler, prebuffer=2500)
        self.note_handler.update(song_time)
        self.arrow_handler.update(dt)
        self.animator.update(dt)
        if not self.is_player:
            self.simple_opponent_ai(song_time)

    def draw(self, song_time):
        render_notes(
            self.screen,
            self.note_handler,
            song_time=song_time,
            hit_y=self.hit_y,
            arrow_frames=self.frames,
            lane_positions=self.lane_positions,
            section_list=self.section_list  # <--- NEW
        )
        self.arrow_handler.draw(self.screen)
        self.animator.draw(self.screen)

    def handle_input(self, event, song_time):
        if not self.is_player:
            return  # Only player responds to input
        if event.type == pygame.KEYDOWN and event.key in self.key_map:
            direction = self.key_map[event.key]
            hit = self.note_handler.handle_key_press(direction, song_time)
            if not hit:
                self.arrow_handler.press(direction)
                self.animator.play(direction)
        elif event.type == pygame.KEYUP and event.key in self.key_map:
            direction = self.key_map[event.key]
            self.note_handler.handle_key_release(direction)

    def simple_opponent_ai(self, song_time):
        # "Bot" logic: hit notes perfectly in the 'sick' window
        for direction, notes in self.note_handler.notes_by_lane.items():
            for note in notes:
                if note.hit or note.missed:
                    continue
                diff = abs(song_time - note.time_ms)
                if diff <= JUDGEMENT_WINDOWS['sick']:
                    note.hit = True
                    note.judgement = 'sick'
                    self.arrow_handler.press(direction, with_note=True, judgement='sick')
                    self.animator.play(direction)
                    break  # One note per lane per frame

    def get_song_time(self):
        # Optionally override this to sync with global song time
        # If not overridden, conductor should pass song_time to draw()
        return pygame.time.get_ticks()  # Fallback, for testing