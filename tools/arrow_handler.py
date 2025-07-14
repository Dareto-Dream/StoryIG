import pygame

DEFAULT_SPRITE_KEYS = {
    'left': {
        'idle':  "arrow static instance 10000",
        'flash': "purple instance 10000",
        'hold':  "left press instance 10000"
    },
    'down': {
        'idle':  "arrow static instance 20000",
        'flash': "blue instance 10000",
        'hold':  "down press instance 10000"
    },
    'up': {
        'idle':  "arrow static instance 40000",
        'flash': "green instance 10000",
        'hold':  "up press instance 10000"
    },
    'right': {
        'idle':  "arrow static instance 30000",
        'flash': "red instance 10000",
        'hold':  "right press instance 10000"
    },
}

class Arrow:
    def __init__(self, idle, hold, flash, position):
        self.idle = idle
        self.hold = hold
        self.flash = flash
        self.base_position = position
        self.position = position

        self.splash = Splash(position)

        self.state = "idle"
        self.anim_timer = 0
        self.note_active = False
        self.held = False

    def press(self, with_note=False, judgement=None):
        self.note_active = with_note
        self.held = True
        self.state = "flash"
        self.anim_timer = 100
        if with_note and judgement == "sick":
            self.splash.start()

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
        # Update splash effect regardless of arrow state
        self.splash.update(dt)

    def draw(self, screen):
        if self.state == "flash":
            frame = self.flash
        elif self.state == "hold":
            frame = self.flash if self.note_active else self.hold
        else:
            frame = self.idle

        rect = frame.get_rect(center=self.position)
        screen.blit(frame, rect.topleft)
        # Draw splash on top of arrow
        self.splash.draw(screen)

    def set_position(self, pos):
        self.base_position = pos
        self.position = pos

class ArrowHandler:
    def __init__(self, arrow_frames=None, position=(640, 100), spacing=150,
                 directions=("left", "down", "up", "right"), frames=None):
        """Create and manage a set of static arrows for input feedback.

        Parameters
        ----------
        arrow_frames : dict[str, dict[str, Surface]] or None
            Mapping of direction to the three frames (``idle``, ``hold`` and
            ``flash``). If ``None`` a mapping will be built using ``frames`` and
            :data:`DEFAULT_SPRITE_KEYS`.
        position : tuple[int, int]
            Center position of the arrow lane group.
        spacing : int
            Horizontal spacing between each lane.
        directions : iterable[str]
            Directions that should be displayed.
        frames : dict[str, Surface] or None
            Raw frame lookup used when ``arrow_frames`` is ``None``.
        """

        self.arrows = {}
        self.directions = directions
        self.base_position = position
        self.spacing = spacing

        dir_order = ["left", "down", "up", "right"]
        visible_dirs = [d for d in dir_order if d in directions]

        # Build arrow frame mapping if only raw frames were supplied.
        if arrow_frames is None:
            if frames is None:
                raise ValueError("frames is required when arrow_frames is None")
            arrow_frames = {
                d: {
                    "idle": frames[DEFAULT_SPRITE_KEYS[d]["idle"]],
                    "flash": frames[DEFAULT_SPRITE_KEYS[d]["flash"]],
                    "hold": frames[DEFAULT_SPRITE_KEYS[d]["hold"]],
                }
                for d in visible_dirs
            }

        center_x = position[0]
        base_y = position[1]
        total_width = self.spacing * (len(visible_dirs) - 1)
        start_x = center_x - total_width // 2

        # Instantiate Arrow objects for each visible lane
        for i, d in enumerate(visible_dirs):
            frameset = arrow_frames[d]
            self.arrows[d] = Arrow(
                idle=frameset["idle"],
                hold=frameset["hold"],
                flash=frameset["flash"],
                position=(start_x + i * self.spacing, base_y),
            )

    def press(self, direction, with_note=False, judgement=None):
        if direction in self.arrows:
            self.arrows[direction].press(with_note, judgement=judgement)

    def release(self, direction):
        if direction in self.arrows:
            self.arrows[direction].release()

    def update(self, dt):
        for arrow in self.arrows.values():
            arrow.update(dt)

    def draw(self, screen):
        for arrow in self.arrows.values():
            arrow.draw(screen)

    def set_spacing(self, spacing):
        self.spacing = spacing
        self._reposition()

    def set_position(self, position):
        self.base_position = position
        self._reposition()

    def _reposition(self):
        center_x = self.base_position[0]
        base_y = self.base_position[1]
        total_width = self.spacing * (len(self.arrows) - 1)
        start_x = center_x - total_width // 2
        for i, dir in enumerate(self.arrows):
            self.arrows[dir].set_position((start_x + i * self.spacing, base_y))

class Splash:
    def __init__(self, position, radius=50, duration=200):
        self.position = position
        self.radius = radius
        self.duration = duration
        self.timer = 0
        self.active = False
        self.surface = self._generate_surface()

    def _generate_surface(self):
        surf = pygame.Surface((self.radius * 2, self.radius * 2), pygame.SRCALPHA)
        pygame.draw.circle(surf, (255, 255, 255, 180), (self.radius, self.radius), self.radius)
        return surf

    def start(self):
        self.timer = self.duration
        self.active = True

    def update(self, dt):
        if self.active:
            self.timer -= dt
            if self.timer <= 0:
                self.active = False

    def draw(self, screen):
        if not self.active:
            return
        alpha = int(255 * (self.timer / self.duration))
        faded = self.surface.copy()
        faded.fill((255, 255, 255, alpha), special_flags=pygame.BLEND_RGBA_MULT)
        rect = faded.get_rect(center=self.position)
        screen.blit(faded, rect.topleft)
