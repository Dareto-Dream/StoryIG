import pygame
import json

pygame.init()
WIDTH, HEIGHT = 1920, 1080
screen = pygame.display.set_mode((WIDTH, HEIGHT))
# pygame.display.toggle_fullscreen()
pygame.display.set_caption("Mini FNF Clone")

clock = pygame.time.Clock()

# === Load Assets ===
monika_img = pygame.image.load("assets/minigame/death/monika.png").convert()
monika_img = pygame.transform.scale(monika_img, (WIDTH, HEIGHT))

char_opponent = pygame.image.load("assets/minigame/chars/opponent.png").convert_alpha()
char_player = pygame.image.load("assets/minigame/chars/player.png").convert_alpha()

# Arrow direction to sprite map
arrow_sheet = pygame.image.load("assets/minigame/arrows/arrows.png").convert_alpha()
arrow_w, arrow_h = 134, 139

sprite_map = {
    # Target (gray) arrows – row 0
    'left_target': arrow_sheet.subsurface(pygame.Rect(0 * arrow_w, 0 * arrow_h, arrow_w, arrow_h)),
    'down_target': arrow_sheet.subsurface(pygame.Rect(1 * arrow_w, 0 * arrow_h, arrow_w, arrow_h)),
    'up_target': arrow_sheet.subsurface(pygame.Rect(2 * arrow_w, 0 * arrow_h, arrow_w, arrow_h)),
    'right_target': arrow_sheet.subsurface(pygame.Rect(3 * arrow_w, 0 * arrow_h, arrow_w, arrow_h)),

    # Colored arrows – row 1
    'left': arrow_sheet.subsurface(pygame.Rect(0 * arrow_w, 1 * arrow_h, arrow_w, arrow_h)),
    'down': arrow_sheet.subsurface(pygame.Rect(1 * arrow_w, 1 * arrow_h, arrow_w, arrow_h)),
    'up': arrow_sheet.subsurface(pygame.Rect(2 * arrow_w, 1 * arrow_h, arrow_w, arrow_h)),
    'right': arrow_sheet.subsurface(pygame.Rect(3 * arrow_w, 1 * arrow_h, arrow_w, arrow_h)),

    # Optional: Outline FX – row 2
    'left_outline': arrow_sheet.subsurface(pygame.Rect(0 * arrow_w, 2 * arrow_h, arrow_w, arrow_h)),
    'down_outline': arrow_sheet.subsurface(pygame.Rect(1 * arrow_w, 2 * arrow_h, arrow_w, arrow_h)),
    'up_outline': arrow_sheet.subsurface(pygame.Rect(2 * arrow_w, 2 * arrow_h, arrow_w, arrow_h)),
    'right_outline': arrow_sheet.subsurface(pygame.Rect(3 * arrow_w, 2 * arrow_h, arrow_w, arrow_h)),
}

# === Config ===
opponent_x = {'left': 100, 'down': 200, 'up': 300, 'right': 400}
player_x = {'left': 1350, 'down': 1500, 'up': 1650, 'right': 1800}
target_y = 100
arrow_speed = 10
spawn_offset_px = 1000
spawn_delay_ms = spawn_offset_px / arrow_speed * 1000

keys = {
    'left': pygame.K_LEFT,
    'down': pygame.K_DOWN,
    'up': pygame.K_UP,
    'right': pygame.K_RIGHT
}

# === Load Chart ===
with open("assets/minigame/songs/song2.json", "r") as f:
    chart = json.load(f)
chart_index = 0

# === Game State ===
player_arrows = []
opponent_arrows = []
judgments = []
love = 1.0  # 0.0 = death, 1.0 = full love
dead = False

# === Audio ===
pygame.mixer.init()
pygame.mixer.music.load("assets/minigame/songs/song2.mp3")
pygame.mixer.music.play()
start_time = pygame.time.get_ticks()

# === Fonts ===
# REPLACE_FONT - replace with DDLC-style font
font = pygame.font.Font(None, 64)
# END_REPLACE_FONT

# === Functions ===
def draw_targets():
    keys_down = pygame.key.get_pressed()
    for dir in ['left', 'down', 'up', 'right']:
        x = player_x[dir]
        y = target_y
        base = sprite_map[dir + '_target'].copy()
        screen.blit(base, (x, y))

        if keys_down[keys[dir]]:
            ghost = sprite_map[dir].copy()
            ghost.set_alpha(128)  # semi-transparent overlay
            screen.blit(ghost, (x, y))

def draw_love_meter():
    bar_height = 400
    filled = int(love * bar_height)
    pygame.draw.rect(screen, (255, 0, 100), pygame.Rect(50, 200 + (bar_height - filled), 30, filled))
    pygame.draw.rect(screen, (255, 255, 255), pygame.Rect(50, 200, 30, bar_height), 2)
    label = font.render("Love", True, (255, 255, 255))
    screen.blit(label, (40, 160))

def display_judgments():
    for j in judgments[:]:
        j['time'] += 1
        if j['time'] > 60:
            judgments.remove(j)
        else:
            txt = font.render(j['text'], True, j['color'])
            screen.blit(txt, j['pos'])

def show_death():
    screen.blit(monika_img, (0, 0))
    pygame.display.flip()
    pygame.time.delay(4000)

def add_judgment(result, pos):
    color = {"Perfect": (255, 255, 255), "Good": (200, 150, 255), "Miss": (255, 50, 50)}[result]
    judgments.append({'text': result, 'time': 0, 'color': color, 'pos': pos})

def handle_long_note_hit(arrow, time_held):
    expected = arrow.get('hold', 0)
    if expected > 0 and time_held >= expected - 50:
        return "Perfect"
    elif expected > 0 and time_held >= expected * 0.7:
        return "Good"
    else:
        return "Miss"

# === Game Loop ===
running = True
while running:
    screen.fill((0, 0, 0))

    if dead:
        show_death()
        running = False
        continue

    draw_targets()
    draw_love_meter()

    screen.blit(char_opponent, (300, 600))
    screen.blit(char_player, (1300, 600))
    display_judgments()

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    current_time = pygame.time.get_ticks() - start_time

    # Spawn arrows
    while chart_index < len(chart) and current_time >= chart[chart_index]["time"] - spawn_delay_ms:
        note = chart[chart_index]
        arrow = {
            'dir': note['dir'],
            'y': HEIGHT,
            'time': note['time'],
            'singer': note.get('singer', 'player'),
            'hold': note.get('hold', 0),
            'held': False,
            'start_hold': None
        }
        if arrow['singer'] == 'player':
            player_arrows.append(arrow)
        else:
            opponent_arrows.append(arrow)
        chart_index += 1

    # Update + draw arrows
    for arrow in opponent_arrows:
        arrow['y'] -= arrow_speed
        screen.blit(sprite_map[arrow['dir']], (opponent_x[arrow['dir']], arrow['y']))

    for arrow in player_arrows:
        arrow['y'] -= arrow_speed
        head_pos = (player_x[arrow['dir']], arrow['y'])

        # Draw tail for long notes
        if arrow.get('hold', 0) > 0:
            tail_height = arrow['hold'] / 1000 * arrow_speed * 60
            pygame.draw.rect(screen, (200, 0, 200), pygame.Rect(head_pos[0] + 48, arrow['y'], 32, tail_height))
        screen.blit(sprite_map[arrow['dir']], head_pos)

    # Hit detection
    keys_down = pygame.key.get_pressed()
    handled_dirs = set()  # Prevent double-processing same key

    for arrow in player_arrows[:]:
        arrow_top = arrow['y']
        window_start = target_y
        window_end = target_y + 50
        key = keys[arrow['dir']]

        if window_start < arrow_top < window_end and keys_down[key] and arrow['dir'] not in handled_dirs:
            handled_dirs.add(arrow['dir'])

            now = pygame.time.get_ticks()
            if arrow['hold']:
                if not arrow['held']:
                    arrow['start_hold'] = now
                    arrow['held'] = True
            else:
                diff = abs(arrow['y'] - target_y)
                if diff <= 50:
                    add_judgment("Perfect", (player_x[arrow['dir']], target_y - 50))
                    love = min(1.0, love + 0.05)
                elif diff <= 100:
                    add_judgment("Good", (player_x[arrow['dir']], target_y - 50))
                    love = min(1.0, love + 0.02)
                else:
                    add_judgment("Miss", (player_x[arrow['dir']], target_y - 50))
                    love = max(0.0, love - 0.1)
                player_arrows.remove(arrow)


        # Check hold end
        elif arrow['held'] and arrow_top + arrow['hold'] / 1000 * arrow_speed * 60 < target_y:
            duration = now - arrow['start_hold']
            result = handle_long_note_hit(arrow, duration)
            add_judgment(result, (player_x[arrow['dir']], target_y - 50))
            if result == "Miss":
                love = max(0.0, love - 0.1)
            elif result == "Good":
                love = min(1.0, love + 0.02)
            else:
                love = min(1.0, love + 0.05)
            player_arrows.remove(arrow)

        # Missed
        elif arrow_top < 0:
            add_judgment("Miss", (player_x[arrow['dir']], target_y - 50))
            love = max(0.0, love - 0.1)
            player_arrows.remove(arrow)

    # if love <= 0.0:
    #     dead = True

    pygame.display.flip()
    clock.tick(60)

pygame.quit()
