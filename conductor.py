import os
import pygame

from discord import presence
from tools.character_animations import CharacterAnimator
from tools.event_handler import EventHandler
from tools.judgement_splash import JudgementSplash
from tools.lane_manager import LaneManager
from tools import judgement
from tools.utils import VideoPlayer
from tools.xml_sprite_loader import load_sprites_from_xml, load_character_frames, load_character_sprites_from_xml
from tools.loader import load_fnf_chart, load_chart


class Conductor:
    def __init__(self, song_name, frames, screen, side_configs):
        self.song_name = song_name
        self.frames = frames
        self.screen = screen
        self.lanes = []
        self.start_time = None

        # --- Use legacy_loader for all chart parsing and BPM/song_speed extraction ---
        chart_path = f"assets/minigame/songs/{song_name}/{song_name}.json"
        bpm, song_speed, player_notes, opponent_notes, song_meta, section_list, events = load_chart(chart_path, "fnf")

        # --- Event support ---
        self.event_handler = EventHandler(events, conductor=self)
        self.video_player = None
        self.video_active = False

        # --- Load in judgement_splash for splash text ---
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

    def play_video(self, path):
        self.video_player = VideoPlayer(path, self.screen.get_size())
        self.video_active = True

    def set_scroll_speed(self, speed, lane=None):
        # If lane is specified, update only that lane; else update all
        if lane is not None and 0 <= lane < len(self.lanes):
            self.lanes[lane].scroll_speed = speed
        else:
            for lane_obj in self.lanes:
                lane_obj.scroll_speed = speed
        print(f"Set scroll speed: {speed} (lane {lane})")
    def get_song_time(self):
        return pygame.time.get_ticks() - self.start_time

    def update(self, dt):
        song_time = self.get_song_time()
        self.event_handler.update(song_time)
        if self.video_active:
            frame = self.video_player.update(dt)
            if frame is None:
                self.video_active = False
                self.video_player.release()
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
        # Overlay video if active (draws ON TOP)
        if self.video_active and self.video_player and self.video_player.frame:
            self.video_player.draw(self.screen)

# ------------------- MAIN GAME LOOP DEMO ------------------------

if __name__ == "__main__":
    import sys

    pygame.init()
    screen = pygame.display.set_mode((1280, 720))
    pygame.display.set_caption("Conductor (Character) Test")
    clock = pygame.time.Clock()

    frames = load_sprites_from_xml(
        "assets/minigame/notes/NOTE_assets.png",
        "assets/minigame/notes/NOTE_assets.xml",
        scale=0.7 # arrow scale
    )

    # For a mod character:
    dustman_raw = load_character_sprites_from_xml("assets/minigame/characters/dearest_fnfbaby.png", "assets/minigame/characters/dearest_fnfbaby.xml", scale=0.3)
    dustman_frames = load_character_frames("unused", dustman_raw)
    megaman_raw = load_character_sprites_from_xml("assets/minigame/characters/nmi_real.png", "assets/minigame/characters/nmi_real.xml", scale=0.2)
    tiffany_frames = load_character_frames("tiffany", megaman_raw)

    # player_animator = CharacterAnimator(dustman_frames, position=(950, 620))
    # tiffany_animator = CharacterAnimator(tiffany_frames, position=(330, 620))

    player_animator = CharacterAnimator(dustman_frames, position=(1000, 575))
    tiffany_animator = CharacterAnimator(tiffany_frames, position=(550, 400))
    three_animator = CharacterAnimator(tiffany_frames, position=(550, 400))

    background_img = pygame.image.load("assets/minigame/backgrounds/skynsuch.png").convert()
    background_img = pygame.transform.smoothscale(background_img, (1280, 720))
    midground_img = pygame.image.load("assets/minigame/backgrounds/letrees.png").convert_alpha()
    midground_img = pygame.transform.smoothscale(midground_img, (1280, 720))
    foreground_img = pygame.image.load("assets/minigame/backgrounds/agua.png").convert_alpha()
    foreground_img = pygame.transform.smoothscale(foreground_img, (1280, 720))
    highground_img = pygame.image.load("assets/minigame/backgrounds/lefrontree.png").convert_alpha() # ITS OVER LUKE I HAVE THE HIGHGROUND
    highground_img = pygame.transform.smoothscale(highground_img, (1280, 720))

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
        },
        {
            'name': "three",
            'animator': three_animator,
            'arrow_x': 550,
        }
    ]

    conductor = Conductor("fakebaby", frames, screen, side_configs)
    presence.set_presence(state="Playing Alpha", large_image="fakebaby", details="No More Innocence Fakebaby", small_image="vn",
                          small_text="Im dead")

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
        screen.blit(background_img, (0, 0))
        screen.blit(midground_img, (0, 0))
        screen.blit(foreground_img, (0, 0))
        conductor.draw()
        if hasattr(conductor, "judgement_splash"):
            conductor.judgement_splash.draw(screen)
        screen.blit(highground_img, (0, 0))
        pygame.display.flip()

    pygame.quit()
    sys.exit()
