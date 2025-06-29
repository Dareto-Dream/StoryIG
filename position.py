import pygame
import json
import os
from pygame.locals import *

# === Config ===
SCREEN_WIDTH, SCREEN_HEIGHT = 1000, 563
STORY_FILE = "story.json"

def load_story():
    with open(STORY_FILE, 'r') as f:
        return json.load(f)

def save_story(story):
    with open(STORY_FILE, 'w') as f:
        json.dump(story, f, indent=4)

def get_combined_image(page):
    char = page.get("character")
    base = f"assets/characters/{char}/"

    try:
        if "pose_left" in page and "pose_right" in page and "face" in page:
            left = pygame.image.load(base + f"{page['pose_left']}.png").convert_alpha()
            right = pygame.image.load(base + f"{page['pose_right']}.png").convert_alpha()
            face = pygame.image.load(base + f"{page['face']}.png").convert_alpha()
            result = pygame.Surface(left.get_size(), pygame.SRCALPHA)
            result.blit(left, (0, 0))
            result.blit(right, (0, 0))
            result.blit(face, (0, 0))
            return result, "Split Body"
        elif "pose" in page and "face" in page:
            pose = pygame.image.load(base + f"{page['pose']}.png").convert_alpha()
            face = pygame.image.load(base + f"{page['face']}.png").convert_alpha()
            result = pygame.Surface(pose.get_size(), pygame.SRCALPHA)
            result.blit(pose, (0, 0))
            result.blit(face, (0, 0))
            return result, "Full Body"
        elif "image" in page:
            img = pygame.image.load(page["image"]).convert_alpha()
            return img, "Legacy Image"
    except Exception as e:
        print(f"[!] Failed to load image: {e}")
    return None, "Missing"

def main():
    pygame.init()
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("Positioning Tool")
    font = pygame.font.Font(None, 28)

    story = load_story()
    current_page = 0
    clock = pygame.time.Clock()

    while True:
        screen.fill((255, 255, 255))
        page = story[current_page]

        if "position" not in page:
            page["position"] = [SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2]
        pos = page["position"]

        sprite, mode = get_combined_image(page)
        if sprite:
            screen.blit(sprite, pos)

        # UI
        text = page.get("text", "")
        screen.blit(font.render(f"Page {page['page']} | Pos: {pos}", True, (0, 0, 0)), (10, 10))
        screen.blit(font.render(f"Render Mode: {mode}", True, (0, 0, 0)), (10, 40))
        screen.blit(font.render(f"{text}", True, (0, 0, 0)), (10, 70))
        screen.blit(font.render("←↑↓→ = move | Enter = save | PgUp/PgDn = switch page | ESC = quit", True, (100, 0, 0)), (10, 520))

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
                    print(f"[✓] Saved position to page {page['page']}")
                elif event.key == K_PAGEUP:
                    current_page = max(0, current_page - 1)
                elif event.key == K_PAGEDOWN:
                    current_page = min(len(story) - 1, current_page + 1)

        clock.tick(30)

if __name__ == "__main__":
    main()
