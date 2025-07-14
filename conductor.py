import os
import json
import pygame

from tools.character_animations import CharacterAnimator
from tools.lane_manager import LaneManager  # <-- NEW!
from tools import judgement
from tools.xml_sprite_loader import load_sprites_from_xml, load_character_frames

class Conductor:
    def __init__(self, song_name, frames, screen, side_configs):
        self.song_name = song_name
        self.frames = frames
        self.screen = screen
        self.lanes = []  # List of LaneManagers (player + opponents)
        self.start_time = None

        # Load charts once per side (can be same or different for player/opponents)
        charts = self.load_charts(song_name, side_configs)
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
                key_map=side_cfg.get('key_map'),
                lane_positions=side_cfg.get('lane_positions'),
                scroll_speed=side_cfg.get('scroll_speed', 0.3)
            )
            self.lanes.append(lane)

        self.load_and_play_music(song_name)

    def load_charts(self, song_name, side_configs):
        chart_path = f"assets/minigame/songs/{song_name}/{song_name}.json"
        with open(chart_path, 'r') as f:
            raw = json.load(f)
        sections = raw["song"]["notes"]
        player_notes, opponent_notes = self.split_fnf_chart_sections(sections)

        charts = []
        for side_cfg in side_configs:
            if side_cfg['name'] == "player":
                charts.append(player_notes)
            else:
                charts.append(opponent_notes)
        return charts

    def split_fnf_chart_sections(self, sections):
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
                    "direction": direction_map[lane],
                    "time": int(time),
                    "sustain": sustain
                }
                # Main twist: assign per mustHitSection
                if must_hit:
                    # Player is on lanes 0-3, opponent is 4-7
                    if lane in (0, 1, 2, 3):
                        player_notes.append(note_obj)
                    elif lane in (4, 5, 6, 7):
                        opponent_notes.append(note_obj)
                else:
                    # Opponent is on lanes 0-3, player is 4-7
                    if lane in (0, 1, 2, 3):
                        opponent_notes.append(note_obj)
                    elif lane in (4, 5, 6, 7):
                        player_notes.append(note_obj)
        return player_notes, opponent_notes

    def load_and_play_music(self, song_name):
        inst_path = f"assets/minigame/songs/{song_name}/Inst.ogg"
        voices_path = f"assets/minigame/songs/{song_name}/Voices.ogg"
        fallback_mp3 = f"assets/minigame/songs/{song_name}/{song_name}.mp3"
        self.start_time = pygame.time.get_ticks()

        if os.path.exists(inst_path) and os.path.exists(voices_path):
            # Legacy FNF style: play both instrumentals and voices
            inst_sound = pygame.mixer.Sound(inst_path)
            voices_sound = pygame.mixer.Sound(voices_path)

            self.inst_channel = pygame.mixer.Channel(0)
            self.voices_channel = pygame.mixer.Channel(1)

            self.inst_channel.play(inst_sound)
            self.voices_channel.play(voices_sound)
        elif os.path.exists(fallback_mp3):
            # Fallback: single file (usually for custom/modern charts)
            pygame.mixer.music.load(fallback_mp3)
            pygame.mixer.music.play()

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
        for lane in self.lanes:
            lane.draw()

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

# ------------------- MAIN GAME LOOP DEMO ------------------------

if __name__ == "__main__":
    import sys

    pygame.init()
    screen = pygame.display.set_mode((1280, 720))
    pygame.display.set_caption("Conductor (LaneManager) Test")
    clock = pygame.time.Clock()

    # Load arrow sprites
    frames = load_sprites_from_xml(
        "assets/minigame/notes/NOTE_assets.png",
        "assets/minigame/notes/NOTE_assets.xml"
    )

    # Load character frames (you can add more for more opponents)
    player_frames = load_character_frames("player", frames)
    tiffany_frames = load_character_frames("tiffany", frames)  # Example opponent

    player_animator = CharacterAnimator(player_frames, position=(950, 620))
    tiffany_animator = CharacterAnimator(tiffany_frames, position=(330, 620))

    # Player and opponent lane configs
    player_key_map = {
        pygame.K_a: 'left',
        pygame.K_s: 'down',
        pygame.K_w: 'up',
        pygame.K_d: 'right'
    }

    # Define your lane layout
    side_configs = [
        {
            'name': "player",
            'animator': player_animator,
            'arrow_x': 900,
            'is_player': True,
            'key_map': player_key_map,
            # Optionally, lane_positions, hit_y, scroll_speed
        },
        {
            'name': "tiffany",
            'animator': tiffany_animator,
            'arrow_x': 350,
            # Optionally, lane_positions, hit_y, scroll_speed
        }
        # Add more opponents here!
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
        screen.fill((0, 0, 0))
        conductor.draw()
        pygame.display.flip()

    pygame.quit()
    sys.exit()
