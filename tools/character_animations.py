import pygame

BASE_WIDTH = 1280
BASE_HEIGHT = 720
DEFAULT_FPS = 24  # frame rate per animation

class CharacterAnimator:
    def __init__(self, sprite_map: dict, position: tuple):
        """
        sprite_map: dict of state name → list[Surface]
            Required: 'idle', 'singLEFT', 'singDOWN', 'singUP', 'singRIGHT'
        position: (x, y) on screen at 1280x720 base
        """
        self.sprite_map = sprite_map
        self.base_pos = position
        self.scaled_pos = position
        self.scale = 1.0

        self.current_state = "idle"
        self.held = False
        self.anim_time = 1000 // DEFAULT_FPS  # time per frame (ms)

        self.frame_index = 0
        self.frame_timer = self.anim_time

        self.scaled_frames = {
            state: frames[:] for state, frames in sprite_map.items()
        }
        self._rescale_all_frames()

    def play(self, direction: str):
        """Start playing a directional animation"""
        key = {
            "left": "singLEFT",
            "down": "singDOWN",
            "up": "singUP",
            "right": "singRIGHT"
        }.get(direction.lower())
        if key in self.sprite_map:
            self.current_state = key
            self.frame_index = 0
            self.frame_timer = self.anim_time
            self.held = True

    def release(self):
        """Release input and return to idle after anim finishes"""
        self.held = False

    def update(self, dt):
        frames = self.scaled_frames.get(self.current_state)
        if not frames:
            return

        self.frame_timer -= dt
        if self.frame_timer <= 0:
            self.frame_index += 1
            if self.frame_index >= len(frames):
                if self.held:
                    self.frame_index = 0  # loop animation
                else:
                    self.current_state = "idle"
                    self.frame_index = 0
            self.frame_timer = self.anim_time

    def draw(self, screen):
        frames = self.scaled_frames.get(self.current_state)
        if frames:
            frame = frames[self.frame_index % len(frames)]
            rect = frame.get_rect(midbottom=self.scaled_pos)
            screen.blit(frame, rect.topleft)

    def rescale(self, screen_size):
        scale_x = screen_size[0] / BASE_WIDTH
        scale_y = screen_size[1] / BASE_HEIGHT
        self.scale = min(scale_x, scale_y)
        self.scaled_pos = (int(self.base_pos[0] * self.scale), int(self.base_pos[1] * self.scale))
        self._rescale_all_frames()

    def _rescale_all_frames(self):
        self.scaled_frames = {}
        for state, frames in self.sprite_map.items():
            self.scaled_frames[state] = [
                pygame.transform.smoothscale(frame, (
                    int(frame.get_width() * self.scale),
                    int(frame.get_height() * self.scale)
                )) for frame in frames
            ]
