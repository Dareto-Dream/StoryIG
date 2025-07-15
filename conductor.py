import os
import pygame
from tools.character_animations import CharacterAnimator
from tools.judgement_splash import JudgementSplash
from tools.lane_manager import LaneManager
from tools import judgement
from tools.xml_sprite_loader import load_sprites_from_xml, load_character_frames
from tools.legacy_loader import load_fnf_chart

class Conductor:
    def __init__(self, song_name, frames, screen, side_configs):
        self.song_name = song_name
        self.frames = frames
        self.screen = screen
        self.lanes = []
        self.start_time = None

        # --- Use legacy_loader for all chart parsing and BPM/song_speed extraction ---
        chart_path = f"assets/minigame/songs/{song_name}/{song_name}.json"
        bpm, song_speed, player_notes, opponent_notes, song_meta, section_list = load_fnf_chart(chart_path)

        # --- Load in judgement_splash for splash text
        self.judgement_splash = JudgementSplash(center=(screen.get_width() // 2, 180))

        # --- Assign correct chart to each LaneManager ---
        charts = []
        for side_cfg in side_configs:
            if side_cfg['name'] == "player":
                charts.append(player_notes)
            else:
                charts.append(opponent_notes)

        # --- Initialize LaneManagers with bpm and song_speed ---
        for i, side_cfg in enumerate(side_configs):
            lane = LaneManager(
                name=side_cfg['name'],
                chart=charts[i],
                frames=frames,
                animator=side_cfg['animator'],
                screen=screen,
                judgement=judgement,
                arrow_x=side_cfg['arrow_x'],
                hit_y=side_cfg.get('hit_y', 100),
                is_player=side_cfg.get('is_player', False),
                bpm=bpm,
                song_speed=song_speed,
                key_map=side_cfg.get('key_map'),
                lane_positions=side_cfg.get('lane_positions'),
                section_list=section_list,
                judgement_splash=self.judgement_splash if side_cfg['name'] == "player" else None  # THIS LINE ADDED
            )
            self.lanes.append(lane)

        self.load_and_play_music(song_name)

    def load_and_play_music(self, song_name):
        inst_path = f"assets/minigame/songs/{song_name}/Inst.ogg"
        voices_path = f"assets/minigame/songs/{song_name}/Voices.ogg"
        fallback_mp3 = f"assets/minigame/songs/{song_name}/{song_name}.mp3"

        if os.path.exists(inst_path) and os.path.exists(voices_path):
            inst_sound = pygame.mixer.Sound(inst_path)
            voices_sound = pygame.mixer.Sound(voices_path)

            self.inst_channel = pygame.mixer.Channel(0)
            self.voices_channel = pygame.mixer.Channel(1)

            self.inst_channel.play(inst_sound)
            self.voices_channel.play(voices_sound)
            self.start_time = pygame.time.get_ticks()  # <-- Move here!
        elif os.path.exists(fallback_mp3):
            pygame.mixer.music.load(fallback_mp3)
            pygame.mixer.music.play()
            self.start_time = pygame.time.get_ticks()  # <-- Move here!

    def get_song_time(self):
        return pygame.time.get_ticks() - self.start_time

    def update(self, dt):
        song_time = self.get_song_time()
        for lane in self.lanes:
            lane.update(song_time, dt)

    def handle_input(self, event):
        song_time = self.get_song_time()
        for lane in self.lanes:
            lane.handle_input(event, song_time)

    def draw(self):
        song_time = self.get_song_time()
        for lane in self.lanes:
            lane.draw(song_time)

# ------------------- MAIN GAME LOOP DEMO ------------------------

if __name__ == "__main__":
    import sys

    pygame.init()
    screen = pygame.display.set_mode((1280, 720))
    pygame.display.set_caption("Conductor (LaneManager) Test")
    clock = pygame.time.Clock()

    frames = load_sprites_from_xml(
        "assets/minigame/notes/NOTE_assets.png",
        "assets/minigame/notes/NOTE_assets.xml",
        scale=0.7 # arrow scale
    )

    player_frames = load_character_frames("player", frames)
    tiffany_frames = load_character_frames("tiffany", frames)

    player_animator = CharacterAnimator(player_frames, position=(950, 620))
    tiffany_animator = CharacterAnimator(tiffany_frames, position=(330, 620))

    player_key_map = {
        pygame.K_a: 'left',
        pygame.K_s: 'down',
        pygame.K_w: 'up',
        pygame.K_d: 'right',
        # Arrow key controls
        pygame.K_LEFT: 'left',
        pygame.K_DOWN: 'down',
        pygame.K_UP: 'up',
        pygame.K_RIGHT: 'right'
    }

    side_configs = [
        {
            'name': "player",
            'animator': player_animator,
            'arrow_x': 900,
            'is_player': True,
            'key_map': player_key_map,
        },
        {
            'name': "tiffany",
            'animator': tiffany_animator,
            'arrow_x': 350,
        }
    ]

    conductor = Conductor("tutorial", frames, screen, side_configs)

    running = True
    while running:
        dt = clock.tick(60)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            conductor.handle_input(event)
        conductor.update(dt)
        if hasattr(conductor, "judgement_splash"):
            conductor.judgement_splash.update(dt)
        screen.fill((0, 0, 0))
        conductor.draw()
        if hasattr(conductor, "judgement_splash"):
            conductor.judgement_splash.draw(screen)
        pygame.display.flip()

    pygame.quit()
    sys.exit()
