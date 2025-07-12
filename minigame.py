import pygame
import xml.etree.ElementTree as ET


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
        frames[name] = image.subsurface(pygame.Rect(x, y, w, h))

    return frames


class Arrow:
    def __init__(self, idle, hold, flash, position):
        self.idle = idle
        self.hold = hold
        self.flash = flash
        self.position = position
        self.state = "idle"
        self.anim_timer = 0
        self.note_active = False
        self.held = False  # <-- NEW: track actual key state

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

    def draw(self, screen):
        if self.state == "flash":
            frame = self.flash  # BRIGHT
        elif self.state == "hold":
            frame = self.flash if self.note_active else self.hold  # BRIGHT if note, else COLORED GRAY
        else:
            frame = self.idle  # GRAY
        rect = frame.get_rect(center=self.position)
        screen.blit(frame, rect.topleft)

def run_minigame(screen):
    clock = pygame.time.Clock()
    running = True
    start_time = pygame.time.get_ticks()

    frames = load_sprites_from_xml(
        "assets/minigame/notes/NOTE_assets.png",
        "assets/minigame/notes/NOTE_assets.xml"
    )

    screen_width, screen_height = screen.get_size()
    arrow_spacing = 120
    base_y = 450
    center_x = screen_width // 2
    positions = [
        center_x - arrow_spacing * 1.5,
        center_x - arrow_spacing * 0.5,
        center_x + arrow_spacing * 0.5,
        center_x + arrow_spacing * 1.5
    ]

    arrow_map = {
        'left': Arrow(
            idle=frames["arrow static instance 10000"],
            flash=frames["purple instance 10000"],
            hold=frames["left press instance 10000"],
            position=(positions[0], base_y)
        ),
        'down': Arrow(
            idle=frames["arrow static instance 20000"],
            flash=frames["blue instance 10000"],
            hold=frames["down press instance 10000"],
            position=(positions[1], base_y)
        ),
        'right': Arrow(
            idle=frames["arrow static instance 30000"],
            flash=frames["red instance 10000"],
            hold=frames["right press instance 10000"],
            position=(positions[2], base_y)
        ),
        'up': Arrow(
            idle=frames["arrow static instance 40000"],
            flash=frames["green instance 10000"],
            hold=frames["up press instance 10000"],
            position=(positions[3], base_y)
        ),
    }

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
                    arrow = arrow_map[direction]
                    arrow.press(with_note=False)  # no note logic yet
                    held_keys.add(direction)

            elif event.type == pygame.KEYUP:
                if event.key in key_to_dir:
                    direction = key_to_dir[event.key]
                    arrow_map[direction].release()
                    held_keys.discard(direction)

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
    screen = pygame.display.set_mode((800, 600))
    pygame.display.set_caption("Minigame Test")
    run_minigame(screen)
    pygame.quit()
