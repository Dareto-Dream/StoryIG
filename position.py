import pygame
import json
import os
from pygame.locals import *
from character_renderer import render_character

# === Config ===
SCREEN_WIDTH, SCREEN_HEIGHT = 1280, 720
STORY_FILE = "story.json"

def load_story():
    with open(STORY_FILE, 'r') as f:
        return json.load(f)

def save_story(story):
    with open(STORY_FILE, 'w') as f:
        json.dump(story, f, indent=4)

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

        sprite = render_character(page)  # << use new renderer
        if sprite:
            screen.blit(sprite, pos)

        # UI
        text = page.get("text", "")
        screen.blit(font.render(
            f"Page {page['page']} | Pos: {pos} | Scale: {page.get('scale', 1.0):.2f}",
            True, (0, 0, 0)
        ), (10, 10))
        # Optionally: render mode info if you want (but you probably don't need it now)
        screen.blit(font.render(f"{text}", True, (0, 0, 0)), (10, 40))
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
                    page["scale"] = page.get("scale", 1.0)  # Save current scale explicitly
                    print(f"[✓] Saved position & scale to page {page['page']} (pos={page['position']}, scale={page['scale']})")
                elif event.key == K_PAGEUP:
                    current_page = max(0, current_page - 1)
                elif event.key == K_PAGEDOWN:
                    current_page = min(len(story) - 1, current_page + 1)
                elif event.key in (K_EQUALS, K_PLUS, K_KP_PLUS):
                    # Increase scale
                    scale = page.get("scale", 1.0)
                    scale = min(2.5, scale + 0.05)  # Cap max scale if you want
                    page["scale"] = round(scale, 3)
                    print(f"[+] Scale increased: {page['scale']}")
                elif event.key in (K_MINUS, K_UNDERSCORE, K_KP_MINUS):
                    # Decrease scale
                    scale = page.get("scale", 1.0)
                    scale = max(0.2, scale - 0.05)  # Cap min scale if you want
                    page["scale"] = round(scale, 3)
                    print(f"[-] Scale decreased: {page['scale']}")

        clock.tick(30)

if __name__ == "__main__":
    main()
