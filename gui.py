# === Imports ===
import pygame
import json
import sys
import subprocess
import os
from pygame.locals import *
from time import sleep

# === Configuration ===
SCREEN_WIDTH, SCREEN_HEIGHT = 1000, 563
TEXTBOX_RECT = pygame.Rect(10, 390, 780, 200)

# === Global State Variables ===
variables = {}
input_texts = []
current_page = 0
current_background = None
selected_input = 0
in_start_screen = True
start_options = ["Start Game", "Load (Disabled)", "Exit"]
selected_option = 0

# === Load story from JSON file ===
def load_story(json_file):
    with open(json_file, 'r') as f:
        return json.load(f)

# === Draw text on screen ===
def draw_text(screen, text, position, color=(0, 0, 0), font_size=24):
    font = pygame.font.Font(None, font_size)
    text_surface = font.render(text, True, color)
    screen.blit(text_surface, position)

def load_song(song_name="song"):
    pygame.mixer.init()
    pygame.mixer.music.load(f"assets/minigame/songs/{song_name}.mp3")
    pygame.mixer.music.play()

# === Draw textbox background ===
def draw_textbox(screen):
    sprite = pygame.image.load("assets/icons/text_box.png").convert_alpha()
    sprite = pygame.transform.smoothscale(sprite, (780, 150))
    screen.blit(sprite, (10, 400))

# === Draw character sprite (single image) ===
def draw_character(screen, image_path, position, size=None):
    try:
        sprite = pygame.image.load(image_path).convert_alpha()
        if size:
            sprite = pygame.transform.smoothscale(sprite, tuple(size))
        screen.blit(sprite, position)
    except Exception as e:
        print(f"Error loading character image '{image_path}': {e}")

# === Draw combined pose+face sprite ===
def get_combined_character_image(character, pose, face):
    base_path = f"assets/characters/{character}/"
    try:
        pose_img = pygame.image.load(os.path.join(base_path, f"{pose}.png")).convert_alpha()
        face_img = pygame.image.load(os.path.join(base_path, f"{face}.png")).convert_alpha()
        combined = pygame.Surface(pose_img.get_size(), pygame.SRCALPHA)
        combined.blit(pose_img, (0, 0))
        combined.blit(face_img, (0, 0))
        return combined
    except Exception as e:
        print(f"Error loading layered character ({character}, {pose}, {face}): {e}")
        return None

# === Display speaker + dialogue ===
def draw_dialogue(screen, speaker, text):
    draw_text(screen, f"{speaker}:", (30, 420), font_size=28)
    draw_text(screen, text, (30, 460), font_size=24)

# === Draw input field ===
def draw_input_box(screen, position, width, height, text='', selected=False):
    border_color = (255, 0, 0) if selected else (0, 0, 0)
    pygame.draw.rect(screen, border_color, (position[0], position[1], width, height), 3)
    draw_text(screen, text, (position[0] + 5, position[1] + 5))

# === Replace [var] in dialogue ===
def substitute_text(text):
    for var, val in variables.items():
        text = text.replace(f"[{var}]", val)
    return text

# === Input handler ===
def handle_input_event(event, selected_input):
    global input_texts
    if event.key == K_RETURN:
        return True
    elif event.key == K_BACKSPACE:
        input_texts[selected_input] = input_texts[selected_input][:-1]
    else:
        input_texts[selected_input] += event.unicode
    return False

# === Load background ===
def draw_background(screen, image_path):
    try:
        bg = pygame.image.load(image_path).convert()
        bg = pygame.transform.scale(bg, (SCREEN_WIDTH, SCREEN_HEIGHT))
        return bg
    except Exception as e:
        print(f"Error loading background '{image_path}': {e}")
        return None

# === Start screen drawing ===
def draw_start_screen(screen, selected_option, options):
    bg = pygame.image.load("assets/screens/all_dokis.png").convert()
    bg = pygame.transform.scale(bg, (SCREEN_WIDTH, SCREEN_HEIGHT))
    screen.blit(bg, (0, 0))
    for i, option in enumerate(options):
        x = SCREEN_WIDTH // 2 - 150
        y = 250 + i * 70
        draw_option_box(screen, option, x, y, 300, 50, selected_option == i)

# === Glitched horror screen ===
def draw_glitched_menu(screen):
    bg = pygame.image.load("assets/screens/gmenu.png").convert()
    bg = pygame.transform.scale(bg, (SCREEN_WIDTH, SCREEN_HEIGHT))
    screen.blit(bg, (0, 0))
    draw_text(screen, "Monika Club", (SCREEN_WIDTH // 2 - 150, 100), font_size=48, color=(255, 0, 0))
    draw_text(screen, "St_rt", (SCREEN_WIDTH // 2 - 100, 250), font_size=32, color=(200, 0, 0))
    draw_text(screen, "Load.chr [missing]", (SCREEN_WIDTH // 2 - 100, 300), font_size=32, color=(180, 0, 0))
    draw_text(screen, "Exi__", (SCREEN_WIDTH // 2 - 100, 350), font_size=32, color=(255, 255, 255))

# === Draw each menu option ===
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

# === Main VN Engine ===
def run_gui():
    global current_page, input_texts, variables, current_background
    global selected_input, in_start_screen, selected_option

    pygame.init()
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption('AdLibs Visual Novel')
    clock = pygame.time.Clock()

    story = load_story('story.json')
    running = True
    load_song("song1")

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
                    if page.get("type") == "game":
                        game_number = page.get("game_number", 1)
                        try:
                            subprocess.run([sys.executable, "minigame.py"])
                        except Exception as e:
                            print(f"Error launching minigame: {e}")
                        current_page += 1
                        continue

                    # === Input handling ===
                    if 'inputs' in page and not page.get('inputs_done', False):
                        if event.key == K_UP:
                            selected_input = (selected_input - 1) % len(input_texts)
                        elif event.key == K_DOWN:
                            selected_input = (selected_input + 1) % len(input_texts)
                        elif handle_input_event(event, selected_input):
                            for i, key in enumerate(page['inputs']):
                                variables[key] = input_texts[i]
                            input_texts = []
                            page['inputs_done'] = True
                    elif event.key == K_RETURN:
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

            if 'inputs' in page and not page.get('inputs_done', False) and not input_texts:
                input_texts = ['' for _ in page['inputs']]
                selected_input = 0

            if 'background' in page:
                new_bg = draw_background(screen, page['background'])
                if new_bg:
                    current_background = new_bg

            if current_background:
                screen.blit(current_background, (0, 0))
            else:
                screen.fill((255, 255, 255))

            # === Character sprite logic (new format or fallback) ===
            if 'character' in page and 'pose' in page and 'face' in page and 'position' in page:
                combined = get_combined_character_image(page['character'], page['pose'], page['face'])
                if combined:
                    screen.blit(combined, page['position'])
            elif 'image' in page and 'position' in page:
                size = page.get('image_size', None)
                draw_character(screen, page['image'], page['position'], size)

            draw_textbox(screen)

            if 'inputs' in page and not page.get('inputs_done', False):
                for i, prompt in enumerate(page['inputs']):
                    draw_text(screen, f"{prompt}:", (50, 100 + i * 60))
                    draw_input_box(screen, (150, 100 + i * 60), 300, 40, text=input_texts[i], selected=(i == selected_input))
            else:
                substituted_text = substitute_text(page['text'])
                draw_dialogue(screen, page['speaker'], substituted_text)
        else:
            draw_text(screen, "THE END", (SCREEN_WIDTH // 2 - 80, SCREEN_HEIGHT // 2), font_size=48)

        pygame.display.flip()
        clock.tick(30)

    pygame.quit()
    sys.exit()

# === Launch ===
if __name__ == "__main__":
    run_gui()
