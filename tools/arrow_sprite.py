import pygame

class ArrowSprite:
    def __init__(self, idle_frame, press_frames, position):
        self.idle = idle_frame
        self.press = press_frames  # list of frames
        self.pos = position
        self.state = 'idle'
        self.frame_index = 0
        self.frame_timer = 0

    def update(self, dt):
        if self.state == 'press':
            self.frame_timer += dt
            if self.frame_timer >= 50:  # ms between frames
                self.frame_timer = 0
                self.frame_index += 1
                if self.frame_index >= len(self.press):
                    self.state = 'idle'
                    self.frame_index = 0

    def draw(self, surface):
        if self.state == 'idle':
            surface.blit(self.idle, self.pos)
        else:
            frame = self.press[self.frame_index]
            surface.blit(frame, self.pos)

    def trigger_press(self):
        self.state = 'press'
        self.frame_index = 0
        self.frame_timer = 0
