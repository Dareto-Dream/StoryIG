import pygame
import json
import os
from pygame.locals import *

# === Config ===
SCREEN_WIDTH, SCREEN_HEIGHT = 1000, 563
STORY_FILE = "story.json"

# === Load story ===
def load_story():
    with open(STORY_FILE, 'r') as f:
        return json.load(f)

def save_story(story):
    with open(STORY_FILE, 'w') as f:
        json.dump(story, f, indent=4)

# === Load and combine character image ===
def get_combined_image(character, pose, face):
    try:
        base = pygame.image.load(f"assets/characters/{character}/{pose}.png").convert_alpha()
        face_img = pygame.image.load(f"assets/characters/{character}/{face}.png").convert_alpha()
        out = pygame.Surface(base.get_size(), pygame.SRCALPHA)
        out.blit(base, (0, 0))
        out.blit(face_img, (0, 0))
        return out
    except Exception as e:
        print(f"[!] Error loading pose/face for {character}: {e}")
        return None

# === Load legacy flat image ===
def get_flat_image(image_path):
    try:
        return pygame.image.load(image_path).convert_alpha()
    except Exception as e:
        print(f"[!] Error loading flat image {image_path}: {e}")
        return None

# === Main GUI ===
def main():
    pygame.init()
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("Position Tool")
    font = pygame.font.Font(None, 28)

    story = load_story()
    current_page = 0
    clock = pygame.time.Clock()

    while True:
        screen.fill((255, 255, 255))
        page = story[current_page]
        text = page.get("text", "")

        # Load character image
        sprite = None
        if all(k in page for k in ["character", "pose", "face"]):
            sprite = get_combined_image(page["character"], page["pose"], page["face"])
        elif "image" in page:
            sprite = get_flat_image(page["image"])

        # Load position or set default
        if "position" not in page:
            page["position"] = [SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2]
        pos = page["position"]

        # Draw character
        if sprite:
            screen.blit(sprite, pos)

        # UI text
        screen.blit(font.render(f"Page {page['page']} | Pos: {pos}", True, (0, 0, 0)), (10, 10))
        screen.blit(font.render(text, True, (0, 0, 0)), (10, 40))
        screen.blit(font.render("Arrow keys = move | Enter = save | PgUp/PgDn = change page | Esc = quit", True, (0, 0, 0)), (10, 500))

        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == QUIT:
                save_story(story)
                pygame.quit()
                return
            elif event.type == KEYDOWN:
                if event.key == K_ESCAPE:
                    save_story(story)
                    pygame.quit()
                    return
                elif event.key == K_LEFT:
                    pos[0] -= 10
                elif event.key == K_RIGHT:
                    pos[0] += 10
                elif event.key == K_UP:
                    pos[1] -= 10
                elif event.key == K_DOWN:
                    pos[1] += 10
                elif event.key == K_RETURN:
                    page["position"] = pos.copy()
                    print(f"[✓] Saved position: {pos} to page {page['page']}")
                elif event.key == K_PAGEUP:
                    current_page = max(0, current_page - 1)
                elif event.key == K_PAGEDOWN:
                    current_page = min(len(story) - 1, current_page + 1)

        clock.tick(30)

if __name__ == "__main__":
    main()
