import pygame

class JudgementSplash:
    COLORS = {
        "SICK": (110, 255, 120),
        "GOOD": (70, 200, 255),
        "BAD":  (255, 180, 60),
        "MISS": (255, 60, 60),
        "ABYSMAL DOGSHIT": (170, 90, 255)
    }
    def __init__(self, font_size=96, duration=600, center=(640, 200)):
        self.font = pygame.font.Font(None, font_size)
        self.duration = duration
        self.center = center
        self.text = None
        self.color = (255, 255, 255)
        self.timer = 0
        self.alpha = 0

    def show(self, judgement):
        text = judgement.upper()
        self.text = text
        self.color = self.COLORS.get(text, (255, 255, 255))
        self.timer = self.duration
        self.alpha = 255

    def update(self, dt):
        if self.text:
            self.timer -= dt
            if self.timer <= 0:
                self.text = None
            else:
                self.alpha = int(255 * (self.timer / self.duration))

    def draw(self, screen):
        if self.text:
            surf = self.font.render(self.text, True, self.color)
            surf.set_alpha(self.alpha)
            rect = surf.get_rect(center=self.center)
            screen.blit(surf, rect)
