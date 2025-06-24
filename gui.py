import pygame
import json
import sys
from pygame.locals import *

# === Config ===
SCREEN_WIDTH, SCREEN_HEIGHT = 800, 600
TEXTBOX_RECT = pygame.Rect(0, 400, 800, 200)

# === Globals ===
variables = {}
input_texts = []
current_page = 0
current_background = None
selected_input = 0


def load_story(json_file):
    with open(json_file, 'r') as f:
        return json.load(f)

def draw_text(screen, text, position, color=(0, 0, 0), font_size=24):
    font = pygame.font.Font(None, font_size)
    text_surface = font.render(text, True, color)
    screen.blit(text_surface, position)

def draw_textbox(screen):
    pygame.draw.rect(screen, (200, 200, 200), TEXTBOX_RECT)

def draw_character(screen, image_path, position, size=None):
    try:
        sprite = pygame.image.load(image_path).convert_alpha()
        if size:
            sprite = pygame.transform.smoothscale(sprite, tuple(size))
        screen.blit(sprite, position)
    except Exception as e:
        print(f"Error loading or drawing image '{image_path}': {e}")

def draw_dialogue(screen, speaker, text):
    draw_text(screen, f"{speaker}:", (30, 420), font_size=28)
    draw_text(screen, text, (30, 460), font_size=24)

def draw_input_box(screen, position, width, height, text='', selected=False):
    border_color = (255, 0, 0) if selected else (0, 0, 0)
    pygame.draw.rect(screen, border_color, (position[0], position[1], width, height), 3)
    draw_text(screen, text, (position[0] + 5, position[1] + 5))

def substitute_text(text):
    for var, val in variables.items():
        text = text.replace(f"[{var}]", val)
    return text

def handle_input_event(event, selected_input):
    global input_texts
    if event.key == K_RETURN:
        return True  # submit
    elif event.key == K_BACKSPACE:
        input_texts[selected_input] = input_texts[selected_input][:-1]
    else:
        input_texts[selected_input] += event.unicode
    return False

def draw_background(screen, image_path):
    try:
        bg = pygame.image.load(image_path).convert()
        bg = pygame.transform.scale(bg, (SCREEN_WIDTH, SCREEN_HEIGHT))
        return bg
    except Exception as e:
        print(f"Error loading background '{image_path}': {e}")
        return None


def run_gui():
    global current_page, input_texts, variables, current_background, selected_input

    pygame.init()
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption('AdLibs Visual Novel')
    clock = pygame.time.Clock()

    story = load_story('story.json')
    running = True

    while running and current_page < len(story):
        page = story[current_page]

        # Initialize input_texts early
        if 'inputs' in page and not page.get('inputs_done', False):
            if not input_texts:
                input_texts = ['' for _ in page['inputs']]
                selected_input = 0

        # Update background
        if 'background' in page:
            new_bg = draw_background(screen, page['background'])
            if new_bg:
                current_background = new_bg

        # Draw background
        if current_background:
            screen.blit(current_background, (0, 0))
        else:
            screen.fill((255, 255, 255))

        for event in pygame.event.get():
            if event.type == QUIT:
                running = False

            elif event.type == KEYDOWN:
                # Input box handling
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

        # Draw character
        if 'image' in page and 'position' in page:
            size = page.get('image_size', None)
            draw_character(screen, page['image'], page['position'], size)

        # Draw textbox
        draw_textbox(screen)

        # Input or dialogue
        if 'inputs' in page and not page.get('inputs_done', False):
            for i, prompt in enumerate(page['inputs']):
                draw_text(screen, f"{prompt}:", (50, 100 + i * 60))
                draw_input_box(
                    screen,
                    (150, 100 + i * 60),
                    300, 40,
                    text=input_texts[i],
                    selected=(i == selected_input)
                )
        else:
            substituted_text = substitute_text(page['text'])
            draw_dialogue(screen, page['speaker'], substituted_text)

        pygame.display.flip()
        clock.tick(30)

    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    run_gui()
