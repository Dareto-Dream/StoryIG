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

# === Customizable Text Box Layout ===
TEXTBOX_X, TEXTBOX_Y, TEXTBOX_WIDTH, TEXTBOX_HEIGHT = 10, 390, 780, 150
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
typing = True
typed_text = ""
text_start_time = 0
user_text_speed = 40  # ms per character (default speed if page doesn't override)
current_background = None
previous_background = None
bg_transition_alpha = 0
bg_transition_speed = 10  # alpha step per frame (adjust for faster/slower fade)

# === Load story from JSON file ===
def load_story(json_file):
    with open(json_file, "r", encoding="utf-8") as f:
        return json.load(f)

# === Draw text on screen ===
def draw_text(screen, text, position, color=(0, 0, 0), font_size=24):
    font = pygame.font.Font("assets/fonts/VarelaRound-Regular.ttf", font_size)
    text_surface = font.render(text, True, color)  # Anti-aliasing enabled
    screen.blit(text_surface, position)

def draw_typing_text(screen, full_text, position, font_size=24, color=(0, 0, 0), max_width=760, chars_to_show=None):
    font = pygame.font.Font("assets/fonts/VarelaRound-Regular.ttf", font_size)
    words = full_text.split(' ')
    lines = []
    current_line = ""
    total_chars = 0

    for word in words:
        test_line = current_line + word + " "
        word_len = len(word) + 1  # +1 for space
        if font.size(test_line)[0] <= max_width:
            if chars_to_show is not None and total_chars + word_len > chars_to_show:
                # Partial word rendering
                remaining = chars_to_show - total_chars
                partial_word = word[:max(0, remaining)]
                current_line += partial_word
                break
            current_line = test_line
            total_chars += word_len
        else:
            lines.append(current_line.strip())
            current_line = ""
            if chars_to_show is not None and total_chars >= chars_to_show:
                break
    lines.append(current_line.strip())

    # Draw all wrapped lines
    x, y = position
    drawn_chars = 0
    for line in lines:
        if chars_to_show is not None and drawn_chars + len(line) > chars_to_show:
            line = line[:chars_to_show - drawn_chars]
        rendered = font.render(line, True, color)
        screen.blit(rendered, (x, y))
        y += font.get_linesize()
        drawn_chars += len(line)

def draw_text_wrapped(screen, full_text, position, font_size=24, color=(0, 0, 0), max_width=760):
    draw_typing_text(
        screen,
        full_text,
        position,
        font_size=font_size,
        color=color,
        max_width=max_width,
        chars_to_show=None  # Show full text
    )

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
def draw_dialogue(screen, speaker, text, font_size=24):
    font = pygame.font.Font("assets/fonts/VarelaRound-Regular.ttf", font_size)

    # Speaker name
    speaker_surface = font.render(f"{speaker}:", True, (0, 0, 0))
    screen.blit(speaker_surface, (TEXTBOX_X + TEXT_MARGIN, TEXTBOX_Y + TEXT_MARGIN))

    # Dialogue text (wrapped)
    draw_text_wrapped(
        screen,
        text,
        (TEXTBOX_X + TEXT_MARGIN, TEXTBOX_Y + TEXT_MARGIN + font.get_linesize()),
        font_size=font_size,
        color=(0, 0, 0),
        max_width=TEXTBOX_WIDTH - 2 * TEXT_MARGIN
    )

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
    global current_page, input_texts, variables
    global selected_input, in_start_screen, selected_option
    global typing, typed_text, text_start_time, user_text_speed
    global previous_background, current_background, bg_transition_speed, bg_transition_alpha

    pygame.init()
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption('AdLibs Visual Novel')
    clock = pygame.time.Clock()

    story = load_story('story.json')
    running = True
    # load_song("song1")

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
                    if 'type' in page and page['type'] == 'game':
                        game_number = page.get('game_number', 1)
                        if game_number == 1:
                            from minigame import run_minigame
                            run_minigame(screen)  # Waits for game to complete
                        current_page += 1
                        continue  # Skip normal render/input

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
                        if typing:
                            typing = False  # skip typing animation
                        else:
                            current_page += 1
                            typing = True
                            typed_text = ""
                            text_start_time = pygame.time.get_ticks()

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
                if page['background'] != page.get('last_loaded_bg'):
                    previous_background = current_background
                    current_background = draw_background(screen, page['background'])
                    page['last_loaded_bg'] = page['background']
                    bg_transition_alpha = 255

            if current_background:
                if previous_background and bg_transition_alpha > 0:
                    temp = current_background.copy()
                    temp.set_alpha(255 - bg_transition_alpha)
                    prev = previous_background.copy()
                    prev.set_alpha(bg_transition_alpha)
                    screen.blit(prev, (0, 0))
                    screen.blit(temp, (0, 0))
                    bg_transition_alpha = max(0, bg_transition_alpha - bg_transition_speed)
                else:
                    screen.blit(current_background, (0, 0))
            else:
                screen.fill((255, 255, 255))

            # === Character sprite logic (priority: split > pose > image) ===
            try:
                if all(k in page for k in ["character", "pose_left", "pose_right", "face", "position"]):
                    base_path = f"assets/characters/{page['character']}/"
                    left = pygame.image.load(os.path.join(base_path, f"{page['pose_left']}.png")).convert_alpha()
                    right = pygame.image.load(os.path.join(base_path, f"{page['pose_right']}.png")).convert_alpha()
                    face = pygame.image.load(os.path.join(base_path, f"{page['face']}.png")).convert_alpha()
                    combined = pygame.Surface(left.get_size(), pygame.SRCALPHA)
                    combined.blit(left, (0, 0))
                    combined.blit(right, (0, 0))
                    combined.blit(face, (0, 0))
                    screen.blit(combined, page["position"])
                elif all(k in page for k in ["character", "pose", "face", "position"]):
                    base_path = f"assets/characters/{page['character']}/"
                    pose = pygame.image.load(os.path.join(base_path, f"{page['pose']}.png")).convert_alpha()
                    face = pygame.image.load(os.path.join(base_path, f"{page['face']}.png")).convert_alpha()
                    combined = pygame.Surface(pose.get_size(), pygame.SRCALPHA)
                    combined.blit(pose, (0, 0))
                    combined.blit(face, (0, 0))
                    screen.blit(combined, page["position"])
                elif "image" in page and "position" in page:
                    size = page.get("image_size", None)
                    draw_character(screen, page["image"], page["position"], size)
            except Exception as e:
                print(f"[!] Character render error on page {current_page}: {e}")

            draw_textbox(screen)

            if 'inputs' in page and not page.get('inputs_done', False):
                for i, prompt in enumerate(page['inputs']):
                    draw_text(screen, f"{prompt}:", (50, 100 + i * 60))
                    draw_input_box(screen, (150, 100 + i * 60), 300, 40, text=input_texts[i], selected=(i == selected_input))
            else:
                full_text = substitute_text(page['text'])
                page_speed = page.get("text_speed", user_text_speed)

                if typing:
                    elapsed = pygame.time.get_ticks() - text_start_time
                    chars_to_show = elapsed // page_speed if page_speed > 0 else len(full_text)
                    typed_text = full_text[:chars_to_show]
                    draw_text(screen, f"{page['speaker']}:", (TEXTBOX_X + TEXT_MARGIN, TEXTBOX_Y + TEXT_MARGIN))
                    draw_typing_text(
                        screen,
                        substitute_text(page['text']),
                        (TEXTBOX_X + TEXT_MARGIN, TEXTBOX_Y + TEXT_MARGIN + 30),
                        font_size=24,
                        color=(0, 0, 0),
                        max_width=TEXTBOX_WIDTH - 2 * TEXT_MARGIN,
                        chars_to_show=chars_to_show
                    )
                    if chars_to_show >= len(full_text):
                        typing = False
                else:
                    draw_dialogue(screen, page['speaker'], full_text)
        else:
            draw_text(screen, "THE END", (SCREEN_WIDTH // 2 - 80, SCREEN_HEIGHT // 2), font_size=48)

        pygame.display.flip()
        clock.tick(30)

    pygame.quit()
    sys.exit()

# === Launch ===
if __name__ == "__main__":
    run_gui()
