import pygame
import xml.etree.ElementTree as ET

BASE_WIDTH = 1280
BASE_HEIGHT = 720


def load_sprites_from_xml(image_path, xml_path):
    image = pygame.image.load(image_path).convert_alpha()
    tree = ET.parse(xml_path)
    root = tree.getroot()

    frames = {}
    for sub in root.findall('SubTexture'):
        name = sub.attrib['name']
        x = int(sub.attrib['x'])
        y = int(sub.attrib['y'])
        w = int(sub.attrib['width'])
        h = int(sub.attrib['height'])
        frames[name] = image.subsurface(pygame.Rect(x, y, w, h)).copy()

    return frames


class Arrow:
    def __init__(self, idle, hold, flash, base_pos):
        self.base_idle = idle
        self.base_hold = hold
        self.base_flash = flash
        self.base_pos = base_pos

        self.scaled_idle = idle
        self.scaled_hold = hold
        self.scaled_flash = flash
        self.scaled_pos = base_pos

        self.state = "idle"
        self.anim_timer = 0
        self.note_active = False
        self.held = False

    def press(self, with_note=False):
        self.note_active = with_note
        self.held = True
        self.state = "flash"
        self.anim_timer = 100

    def release(self):
        self.held = False
        self.note_active = False
        self.state = "idle"

    def update(self, dt):
        if self.state == "flash":
            self.anim_timer -= dt
            if self.anim_timer <= 0:
                if self.held:
                    self.state = "hold"
                else:
                    self.state = "idle"

    def rescale(self, scale):
        def scale_image(img):
            w = int(img.get_width() * scale)
            h = int(img.get_height() * scale)
            return pygame.transform.smoothscale(img, (w, h))

        self.scaled_idle = scale_image(self.base_idle)
        self.scaled_hold = scale_image(self.base_hold)
        self.scaled_flash = scale_image(self.base_flash)

        self.scaled_pos = (int(self.base_pos[0] * scale), int(self.base_pos[1] * scale))

    def draw(self, screen):
        if self.state == "flash":

            frame = self.scaled_flash
        elif self.state == "hold":
            frame = self.scaled_flash if self.note_active else self.scaled_hold
        else:
            frame = self.scaled_idle

        rect = frame.get_rect(center=self.scaled_pos)
        screen.blit(frame, rect.topleft)


def run_minigame(screen):
    clock = pygame.time.Clock()
    running = True
    start_time = pygame.time.get_ticks()

    frames = load_sprites_from_xml(
        "assets/minigame/notes/NOTE_assets.png",
        "assets/minigame/notes/NOTE_assets.xml"
    )

    def compute_base_positions():
        spacing = BASE_WIDTH // 8
        center_x = BASE_WIDTH // 2
        return [
            center_x - spacing * 1.5,
            center_x - spacing * 0.5,
            center_x + spacing * 0.5,
            center_x + spacing * 1.5
        ]

    base_y = 100
    positions = compute_base_positions()

    arrow_map = {
        'left': Arrow(
            idle=frames["arrow static instance 10000"],
            flash=frames["purple instance 10000"],
            hold=frames["left press instance 10000"],
            base_pos=(positions[0], base_y)
        ),
        'down': Arrow(
            idle=frames["arrow static instance 20000"],
            flash=frames["blue instance 10000"],
            hold=frames["down press instance 10000"],
            base_pos=(positions[1], base_y)
        ),
        'right': Arrow(
            idle=frames["arrow static instance 30000"],
            flash=frames["red instance 10000"],
            hold=frames["right press instance 10000"],
            base_pos=(positions[3], base_y)
        ),
        'up': Arrow(
            idle=frames["arrow static instance 40000"],
            flash=frames["green instance 10000"],
            hold=frames["up press instance 10000"],
            base_pos=(positions[2], base_y)
        ),
    }

    def rescale_all_arrows(screen_size):
        scale_x = screen_size[0] / BASE_WIDTH
        scale_y = screen_size[1] / BASE_HEIGHT
        scale = min(scale_x, scale_y)
        for arrow in arrow_map.values():
            arrow.rescale(scale)

    rescale_all_arrows(screen.get_size())

    key_to_dir = {
        pygame.K_a: 'left',
        pygame.K_s: 'down',
        pygame.K_d: 'right',
        pygame.K_w: 'up',
    }

    held_keys = set()

    while running:
        dt = clock.tick(60)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
                elif event.key in key_to_dir:
                    direction = key_to_dir[event.key]
                    arrow_map[direction].press(with_note=False)
                    held_keys.add(direction)

            elif event.type == pygame.KEYUP:
                if event.key in key_to_dir:
                    direction = key_to_dir[event.key]
                    arrow_map[direction].release()
                    held_keys.discard(direction)

            elif event.type == pygame.VIDEORESIZE:
                screen = pygame.display.set_mode((event.w, event.h), pygame.RESIZABLE)
                rescale_all_arrows((event.w, event.h))

        for arrow in arrow_map.values():
            arrow.update(dt)

        screen.fill((0, 0, 0))
        for arrow in arrow_map.values():
            arrow.draw(screen)
        pygame.display.flip()

        if pygame.time.get_ticks() - start_time > 15000:
            running = False


if __name__ == "__main__":
    pygame.init()
    screen = pygame.display.set_mode((BASE_WIDTH, BASE_HEIGHT), pygame.RESIZABLE)
    pygame.display.set_caption("Minigame Test")
    run_minigame(screen)
    pygame.quit()