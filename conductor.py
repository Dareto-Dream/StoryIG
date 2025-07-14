import os
import json
import pygame

from tools import judgement
from tools.chart_handler import ChartHandler
from tools.note_handler import NoteHandler, render_notes
from tools.judgement import evaluate, window
from tools.arrow_handler import ArrowHandler, DEFAULT_SPRITE_KEYS
from tools.character_animations import CharacterAnimator
from tools.note import Note

class Conductor:
    def __init__(self, song_name, frames, player_animator, screen):
        self.song_name = song_name
        self.frames = frames
        self.screen = screen
        self.player_animator = player_animator

        self.chart_handler = None
        self.note_handler = None
        self.arrow_handler = None

        self.start_time = None
        self.scroll_speed = 0.3
        self.hit_y = 100

        self.inst_channel = None
        self.voices_channel = None

        self.load_song()
        self.play_music()

    def load_song(self):
        chart_path = f"assets/minigame/songs/{self.song_name}/{self.song_name}.json"
        audio_path = f"assets/minigame/songs/{self.song_name}/{self.song_name}.mp3"

        with open(chart_path, 'r') as f:
            raw = json.load(f)

        # Legacy format support
        if isinstance(raw, dict) and "song" in raw and "notes" in raw["song"]:
            chart_data = self.convert_legacy_chart(raw["song"]["notes"])
        else:
            chart_data = raw

        self.chart_handler = ChartHandler(chart_data)

        self.arrow_handler = ArrowHandler(arrow_frames=self.frames)

        self.note_handler = NoteHandler(
            judgement=judgement,
            arrow_handler=self.arrow_handler,
            player_animator=self.player_animator
        )

        if os.path.exists(audio_path):
            pygame.mixer.music.load(audio_path)

    def play_music(self):
        self.start_time = pygame.time.get_ticks()

        inst_path = f"assets/minigame/songs/{self.song_name}/Inst.ogg"
        voices_path = f"assets/minigame/songs/{self.song_name}/Voices.ogg"
        fallback_mp3 = f"assets/minigame/songs/{self.song_name}/{self.song_name}.mp3"

        if os.path.exists(inst_path) and os.path.exists(voices_path):
            # Use legacy split playback
            inst_sound = pygame.mixer.Sound(inst_path)
            voices_sound = pygame.mixer.Sound(voices_path)

            self.inst_channel = pygame.mixer.Channel(0)
            self.voices_channel = pygame.mixer.Channel(1)

            self.inst_channel.play(inst_sound)
            self.voices_channel.play(voices_sound)
        else:
            # Fallback to single MP3 playback
            pygame.mixer.music.load(fallback_mp3)
            pygame.mixer.music.play()

    def get_song_time(self):
        return pygame.time.get_ticks() - self.start_time

    def update(self, dt=0):
        """Update active game objects.

        Parameters
        ----------
        dt : int
            Time since last update in milliseconds.  Used for animations.
        """
        song_time = self.get_song_time()
        # Spawn notes early enough so they scroll from the bottom
        self.chart_handler.update(song_time, self.note_handler, prebuffer=2500)
        self.note_handler.update(song_time)
        self.arrow_handler.update(dt)
        self.player_animator.update(dt)

    def handle_input(self, event, key_map):
        song_time = self.get_song_time()

        if event.type == pygame.KEYDOWN:
            if event.key in key_map:
                direction = key_map[event.key]
                hit = self.note_handler.handle_key_press(direction, song_time)
                if not hit:
                    # Flash arrows and play animation even without a note
                    self.arrow_handler.press(direction)
                    self.player_animator.play(direction)

        elif event.type == pygame.KEYUP:
            if event.key in key_map:
                direction = key_map[event.key]
                self.note_handler.handle_key_release(direction)

    def draw(self, lane_positions):
        song_time = self.get_song_time()
        render_notes(
            self.screen,
            self.note_handler,
            song_time,
            self.scroll_speed,
            self.hit_y,
            self.frames,
            lane_positions
        )
        self.arrow_handler.draw(self.screen)
        self.player_animator.draw(self.screen)

    def convert_legacy_chart(self, legacy_sections):
        direction_map = {
            0: "left",
            1: "down",
            2: "up",
            3: "right"
        }

        notes = []
        for section in legacy_sections:
            for note in section["sectionNotes"]:
                time, direction_num, _ = note
                direction = direction_map.get(direction_num)
                if direction:
                    notes.append({
                        "direction": direction,
                        "time": int(time)
                    })
        return sorted(notes, key=lambda n: n["time"])


if __name__ == "__main__":
    import pygame
    import sys
    from tools.xml_sprite_loader import load_sprites_from_xml, load_character_frames
    from tools.character_animations import CharacterAnimator

    pygame.init()
    screen = pygame.display.set_mode((1280, 720))
    pygame.display.set_caption("Conductor Test")
    clock = pygame.time.Clock()

    # Load arrow sprites
    frames = load_sprites_from_xml(
        "assets/minigame/notes/NOTE_assets.png",
        "assets/minigame/notes/NOTE_assets.xml"
    )

    # Load player character (must exist in sprite XML)
    char_frames = load_character_frames("player", frames)
    player_animator = CharacterAnimator(char_frames, position=(300, 600))

    # Create conductor with your test song
    conductor = Conductor("tutorial", frames, player_animator, screen)

    key_map = {
        pygame.K_a: 'left',
        pygame.K_s: 'down',
        pygame.K_w: 'up',
        pygame.K_d: 'right'
    }

    # Precompute lane positions
    spacing = 150
    center_x = 640
    lane_positions = {
        'left': center_x - spacing * 1.5,
        'down': center_x - spacing * 0.5,
        'up':   center_x + spacing * 0.5,
        'right':center_x + spacing * 1.5
    }

    running = True
    while running:
        dt = clock.tick(60)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            conductor.handle_input(event, key_map)

        conductor.update(dt)

        screen.fill((0, 0, 0))
        conductor.draw(lane_positions)
        pygame.display.flip()

    pygame.quit()
    sys.exit()