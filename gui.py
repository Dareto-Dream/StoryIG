# === Imports ===
import pygame
import json
import sys
import subprocess
import os
from pygame.locals import *
from time import sleep

from character_renderer import render_character
from conductor import Conductor
from discord import presence
from rendering.background import BackgroundManager
from rendering.text import TextManager
from tools.xml_sprite_loader import load_sprites_from_xml, load_character_frames, load_character_sprites_from_xml
from tools.character_animations import CharacterAnimator

# === Configuration ===
SCREEN_WIDTH, SCREEN_HEIGHT = 1280, 720

# === Customizable Text Box Layout ===
TEXTBOX_X, TEXTBOX_Y, TEXTBOX_WIDTH, TEXTBOX_HEIGHT = 30, 400, 1200, 200
TEXTBOX_RECT = pygame.Rect(TEXTBOX_X, TEXTBOX_Y, TEXTBOX_WIDTH, TEXTBOX_HEIGHT)
TEXT_MARGIN = 20  # Padding inside the text box

# === Global State Variables ===
variables = {}
input_texts = []
current_page = 0
selected_input = 0
in_start_screen = True
start_options = ["Start Game", "Load (Disabled)", "Exit"]
selected_option = 0
last_page = -1
user_text_speed = 40  # ms per character (default speed if page doesn't override)

def load_story(json_file):
    with open(json_file, "r", encoding="utf-8") as f:
        return json.load(f)

def draw_text(screen, text, position, color=(0, 0, 0), font_size=24):
    font = pygame.font.Font("assets/fonts/VarelaRound-Regular.ttf", font_size)
    text_surface = font.render(text, True, color)
    screen.blit(text_surface, position)

def run_rhythm_minigame(screen, song_name="tutorial"):
    frames = load_sprites_from_xml(
        "assets/minigame/notes/NOTE_assets.png",
        "assets/minigame/notes/NOTE_assets.xml",
        scale=0.7
    )
    dustman_raw = load_character_sprites_from_xml("assets/minigame/characters/dustmanltbl.png", "assets/minigame/characters/dustmanltbl.xml", scale=0.6)
    dustman_frames = load_character_frames("unused", dustman_raw)
    megaman_raw = load_character_sprites_from_xml("assets/minigame/characters/megamanltbl1.png", "assets/minigame/characters/megamanltbl1.xml", scale=0.6)
    tiffany_frames = load_character_frames("tiffany", megaman_raw)
    player_animator = CharacterAnimator(dustman_frames, position=(950, 620))
    tiffany_animator = CharacterAnimator(tiffany_frames, position=(330, 620))
    player_key_map = {
        pygame.K_a: 'left',
        pygame.K_s: 'down',
        pygame.K_w: 'up',
        pygame.K_d: 'right',
        pygame.K_LEFT: 'left',
        pygame.K_DOWN: 'down',
        pygame.K_UP: 'up',
        pygame.K_RIGHT: 'right'
    }
    side_configs = [
        {'name': "tiffany", 'animator': player_animator, 'arrow_x': 900},
        {'name': "player", 'animator': tiffany_animator, 'arrow_x': 350, 'is_player': True, 'key_map': player_key_map}
    ]
    conductor = Conductor(song_name, frames, screen, side_configs)
    clock = pygame.time.Clock()
    background_img = pygame.image.load("assets/minigame/backgrounds/lettherebebg.png").convert()
    background_img = pygame.transform.smoothscale(background_img, (1280, 720))
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
        conductor.draw()
        if hasattr(conductor, "judgement_splash"):
            conductor.judgement_splash.draw(screen)
        pygame.display.flip()

def load_song(song_name="song", song_type="mp3", loops=0):
    pygame.mixer.init()
    pygame.mixer.music.load(f"assets/songs/{song_name}.{song_type}")
    pygame.mixer.music.play(loops)

def draw_textbox(screen):
    sprite = pygame.image.load("assets/icons/text_box.png").convert_alpha()
    sprite = pygame.transform.smoothscale(sprite, (TEXTBOX_WIDTH, TEXTBOX_HEIGHT))
    screen.blit(sprite, (TEXTBOX_X, TEXTBOX_Y))

def draw_character(screen, image_path, position, size=None):
    try:
        sprite = pygame.image.load(image_path).convert_alpha()
        if size:
            sprite = pygame.transform.smoothscale(sprite, tuple(size))
        screen.blit(sprite, position)
    except Exception as e:
        print(f"Error loading character image '{image_path}': {e}")

def substitute_text(text):
    for var, val in variables.items():
        text = text.replace(f"[{var}]", val)
    return text

def handle_input_event(event, selected_input):
    global input_texts
    if event.key == K_RETURN:
        return True
    elif event.key == K_BACKSPACE:
        input_texts[selected_input] = input_texts[selected_input][:-1]
    else:
        input_texts[selected_input] += event.unicode
    return False

def draw_start_screen(screen, selected_option, options):
    bg = pygame.image.load("assets/screens/all_singers.png").convert()
    bg = pygame.transform.scale(bg, (SCREEN_WIDTH, SCREEN_HEIGHT))
    screen.blit(bg, (0, 0))
    for i, option in enumerate(options):
        x = SCREEN_WIDTH // 2 - 600
        y = 450 + i * 70
        draw_option_box(screen, option, x, y, 300, 50, selected_option == i)

def draw_glitched_menu(screen):
    bg = pygame.image.load("assets/screens/gmenu.png").convert()
    bg = pygame.transform.scale(bg, (SCREEN_WIDTH, SCREEN_HEIGHT))
    screen.blit(bg, (0, 0))
    draw_text(screen, "Monika Club", (SCREEN_WIDTH // 2 - 150, 100), font_size=48, color=(255, 0, 0))
    draw_text(screen, "St_rt", (SCREEN_WIDTH // 2 - 100, 250), font_size=32, color=(200, 0, 0))
    draw_text(screen, "Load.chr [missing]", (SCREEN_WIDTH // 2 - 100, 300), font_size=32, color=(180, 0, 0))
    draw_text(screen, "Exi__", (SCREEN_WIDTH // 2 - 100, 350), font_size=32, color=(255, 255, 255))

def draw_option_box(screen, text, x, y, width, height, selected):
    box_color = (255, 182, 193)
    border_color = (255, 105, 180) if selected else (200, 100, 120)
    text_color = (0, 0, 0)
    pygame.draw.rect(screen, box_color, (x, y, width, height), border_radius=12)
    pygame.draw.rect(screen, border_color, (x, y, width, height), 3 if selected else 1, border_radius=12)
    font = pygame.font.Font(None, 32)
    text_surface = font.render(text, True, text_color)
    text_rect = text_surface.get_rect(center=(x + width // 2, y + height // 2))
    screen.blit(text_surface, text_rect)

def draw_input_box(screen, position, width, height, text='', selected=False):
    border_color = (255, 0, 0) if selected else (0, 0, 0)
    pygame.draw.rect(screen, border_color, (position[0], position[1], width, height), 3)
    draw_text(screen, text, (position[0] + 5, position[1] + 5))

def run_gui():
    global current_page, input_texts, variables
    global selected_input, in_start_screen, selected_option, last_page, user_text_speed

    pygame.init()
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption('Cadence Collapse')
    icon_surface = pygame.image.load("assets/icons/icon32.png").convert_alpha()
    pygame.display.set_icon(icon_surface)
    clock = pygame.time.Clock()
    presence.set_presence(details="In Main Menu")

    background_manager = BackgroundManager(SCREEN_WIDTH, SCREEN_HEIGHT)
    text_manager = TextManager(
        font_path="assets/fonts/VarelaRound-Regular.ttf",
        font_size=24,
        max_width=TEXTBOX_WIDTH - 2 * TEXT_MARGIN
    )


    story = load_story('story.json')
    running = True
    load_song("my_little_world", "wav", 1)

    while running:
        screen.fill((255, 255, 255))

        for event in pygame.event.get():
            if event.type == QUIT:
                running = False
            elif event.type == KEYDOWN:
                if in_start_screen:
                    if event.key == K_UP:
                        selected_option = (selected_option - 1) % len(start_options)
                    elif event.key == K_DOWN:
                        selected_option = (selected_option + 1) % len(start_options)
                    elif event.key == K_RETURN:
                        if selected_option == 0:
                            presence.set_presence(details="Reading VN", state="Act 1: Beginning", small_image="vn",
                                                  small_text="Story Mode")
                            in_start_screen = False
                        elif selected_option == 1:
                            print("Load option is disabled.")
                            bgtemp = pygame.image.load("assets/screens/gmenu.png").convert()
                            bgtemp = pygame.transform.scale(bgtemp, (SCREEN_WIDTH, SCREEN_HEIGHT))
                            screen.blit(bgtemp, (0, 0))
                            pygame.display.flip()
                            sleep(0.5)
                            draw_start_screen(screen, selected_option, start_options)
                        elif selected_option == 2:
                            running = False
                else:
                    if current_page >= len(story):
                        break
                    page = story[current_page]

                    # === Game page trigger ===
                    if 'type' in page and page['type'] == 'game':
                        song_name = page.get('song', "tutorial")
                        presence.set_presence(details="Playing Rhythm Game", state=f"Track: {song_name}",
                                              small_image="rhythm")
                        run_rhythm_minigame(screen, song_name=song_name)
                        presence.set_presence(details="Reading VN", state=f"Act Unknown", small_image="vn")
                        current_page += 1
                        last_page = current_page
                        continue

                    # === Input handling: ONLY for real input pages ===
                    if 'inputs' in page and page['inputs'] and not page.get('inputs_done', False):
                        if event.key == K_UP:
                            selected_input = (selected_input - 1) % len(input_texts)
                        elif event.key == K_DOWN:
                            selected_input = (selected_input + 1) % len(input_texts)
                        elif handle_input_event(event, selected_input):
                            for i, key in enumerate(page['inputs']):
                                variables[key] = input_texts[i]
                            input_texts = []
                            page['inputs_done'] = True
                            current_page += 1
                            continue  # Skip rest of event logic for this frame

                    elif event.key == K_RETURN:
                        if text_manager.typing:
                            text_manager.skip()
                        else:
                            current_page += 1

        # === Render current screen ===
        if in_start_screen:
            draw_start_screen(screen, selected_option, start_options)
        elif current_page < len(story):
            page = story[current_page]

            if page.get("glitch_menu_flash") and not page.get("flashed"):
                draw_glitched_menu(screen)
                pygame.display.flip()
                pygame.time.delay(500)
                page["flashed"] = True

            # Initialize input text array only on fresh input pages
            if 'inputs' in page and page['inputs'] and not page.get('inputs_done', False) and not input_texts:
                input_texts = ['' for _ in page['inputs']]
                selected_input = 0

            # Background logic
            if 'background' in page:
                fade = True
                if page['background'].lower() == "sudden":
                    fade = False
                background_manager.set_background(name=page['background'], fade=fade)

            background_manager.draw(screen)

            try:
                if "position" in page:
                    sprite = render_character(page)
                    if sprite:
                        screen.blit(sprite, page["position"])
            except Exception as e:
                print(f"[!] Character render error on page {current_page}: {e}")

            draw_textbox(screen)

            # --- TextManager: always only treat non-empty 'inputs' as input pages
            if last_page != current_page:
                if 'inputs' in page and page['inputs'] and not page.get('inputs_done', False):
                    text_manager.start("", user_text_speed)
                else:
                    full_text = substitute_text(page.get('text', ''))
                    page_speed = page.get("text_speed", user_text_speed)
                    text_manager.start(full_text, page_speed)
                last_page = current_page

            if 'inputs' in page and page['inputs'] and not page.get('inputs_done', False):
                for i, prompt in enumerate(page['inputs']):
                    draw_text(screen, f"{prompt}:", (50, 100 + i * 60))
                    draw_input_box(screen, (150, 100 + i * 60), 300, 40, text=input_texts[i], selected=(i == selected_input))
            else:
                draw_text(screen, f"{page['speaker']}:", (TEXTBOX_X + TEXT_MARGIN, TEXTBOX_Y + TEXT_MARGIN))
                text_manager.update()
                text_manager.draw(screen, (TEXTBOX_X + TEXT_MARGIN, TEXTBOX_Y + TEXT_MARGIN + 30))

        else:
            draw_text(screen, "THE END", (SCREEN_WIDTH // 2 - 80, SCREEN_HEIGHT // 2), font_size=48)

        pygame.display.flip()
        clock.tick(30)

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    run_gui()
