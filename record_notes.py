import pygame
import json
import os

# === Config ===
SONG_NAME = "song1"
SONG_PATH = f"assets/minigame/songs/{SONG_NAME}.mp3"
OUTPUT_PATH = f"assets/minigame/songs/{SONG_NAME}.json"

pygame.init()
pygame.mixer.init()
screen = pygame.display.set_mode((800, 200))
pygame.display.set_caption("FNF Note Recorder")

# Arrow keys and directions
directions = {
    pygame.K_LEFT: "left",
    pygame.K_DOWN: "down",
    pygame.K_UP: "up",
    pygame.K_RIGHT: "right"
}

# Load and play song
pygame.mixer.music.load(SONG_PATH)
pygame.mixer.music.play()
pygame.time.wait(100)  # Ensure playback has started

# Main loop
chart = []
font = pygame.font.Font(None, 36)
log_text = f"Recording {SONG_NAME}. Press ESC to stop."
running = True

while running:
    screen.fill((0, 0, 0))
    screen.blit(font.render(log_text, True, (255, 255, 255)), (20, 80))
    pygame.display.flip()

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                running = False

            elif event.key in directions:
                current_time = pygame.mixer.music.get_pos()  # Time since song started (ms)
                note = {
                    "time": current_time,
                    "dir": directions[event.key]
                }
                chart.append(note)
                print(f"[{current_time} ms] → {note['dir']}")

pygame.quit()

# Save chart to JSON
with open(OUTPUT_PATH, "w") as f:
    json.dump(chart, f, indent=4)

print(f"\n🎵 Recording complete!")
print(f"📝 Saved {len(chart)} notes to {OUTPUT_PATH}")
