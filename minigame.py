import pygame
import json

pygame.init()
WIDTH, HEIGHT = 1920, 1080
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.toggle_fullscreen()
pygame.display.set_caption("Mini FNF Clone")

clock = pygame.time.Clock()

# === Load arrow sprites ===
arrow_sheet = pygame.image.load("assets/minigame/arrows/arrows.png").convert_alpha()
arrow_size = 128
sprite_map = {
    'left': arrow_sheet.subsurface(pygame.Rect(0, 128, arrow_size, arrow_size)),
    'down': arrow_sheet.subsurface(pygame.Rect(128, 128, arrow_size, arrow_size)),
    'up': arrow_sheet.subsurface(pygame.Rect(256, 128, arrow_size, arrow_size)),
    'right': arrow_sheet.subsurface(pygame.Rect(384, 128, arrow_size, arrow_size)),
    'left_op': arrow_sheet.subsurface(pygame.Rect(0, 0, arrow_size, arrow_size)),
    'down_op': arrow_sheet.subsurface(pygame.Rect(128, 0, arrow_size, arrow_size)),
    'up_op': arrow_sheet.subsurface(pygame.Rect(256, 0, arrow_size, arrow_size)),
    'right_op': arrow_sheet.subsurface(pygame.Rect(384, 0, arrow_size, arrow_size)),
}

# === Lane + Target Positions ===
opponent_x = {'left': 100, 'down': 200, 'up': 300, 'right': 400}
player_x = {'left': 600, 'down': 700, 'up': 800, 'right': 900}
opponent_target_y = 50
player_target_y = 50
arrow_speed = 10

spawn_offset_px = 1000
spawn_delay_ms = spawn_offset_px / arrow_speed * 1000

directions = ['left', 'down', 'up', 'right']
keys = {
    'left': pygame.K_LEFT,
    'down': pygame.K_DOWN,
    'up': pygame.K_UP,
    'right': pygame.K_RIGHT
}

# === Load JSON Chart ===
with open("assets/minigame/songs/song1.json", "r") as f:
    chart = json.load(f)
chart_index = 0

player_arrows = []
opponent_arrows = []

def draw_targets():
    for dir in directions:
        screen.blit(sprite_map[dir + '_op'], (opponent_x[dir], opponent_target_y))
        screen.blit(sprite_map[dir], (player_x[dir], player_target_y))

# === Load and play music ===
pygame.mixer.init()
pygame.mixer.music.load("assets/minigame/songs/song1.mp3")
pygame.mixer.music.play()
start_time = pygame.time.get_ticks()

# === Game Loop ===
running = True
while running:
    screen.fill((0, 0, 0))
    draw_targets()

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    current_time = pygame.time.get_ticks() - start_time

    # Spawn chart arrows
    while chart_index < len(chart) and current_time >= chart[chart_index]["time"] - spawn_delay_ms:
        dir = chart[chart_index]["dir"]
        player_arrows.append({'dir': dir, 'y': HEIGHT})
        opponent_arrows.append({'dir': dir, 'y': HEIGHT})
        chart_index += 1

    # Move + draw opponent arrows
    for arrow in opponent_arrows:
        arrow['y'] -= arrow_speed
        screen.blit(sprite_map[arrow['dir']], (opponent_x[arrow['dir']], arrow['y']))

    # Move + draw player arrows
    for arrow in player_arrows:
        arrow['y'] -= arrow_speed
        screen.blit(sprite_map[arrow['dir']], (player_x[arrow['dir']], arrow['y']))

    # Player hit detection
    keys_pressed = pygame.key.get_pressed()
    for arrow in player_arrows[:]:
        if player_target_y < arrow['y'] < player_target_y + 30:
            if keys_pressed[keys[arrow['dir']]]:
                player_arrows.remove(arrow)

    pygame.display.flip()
    clock.tick(60)

pygame.quit()
