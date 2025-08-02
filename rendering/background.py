# === Load background ===
import os

import pygame


class BackgroundManager:
    def __init__(self, width, height):
        self.cache = {}
        self.current = None
        self.previous = None
        self.alpha = 0
        self.fade_speed = 10
        self.SCREEN_WIDTH = width
        self.SCREEN_HEIGHT = height

    def get_bg(self, name):
        if name not in self.cache:
            path = os.path.join("assets/backgrounds", name)
            bg = pygame.image.load(path).convert()
            self.cache[name] = pygame.transform.scale(bg, (self.SCREEN_WIDTH, self.SCREEN_HEIGHT))
        return self.cache[name]

    def set_background(self, name, fade=True):
        # No change -> do nothing
        if name == self.current:
            return

        # Fade only if requested and not 'sudden'
        if fade and name.lower() != "sudden":
            self.previous = self.current
            self.alpha = 255
        else:
            self.previous = None
            self.alpha = 0

        self.current = name

    def draw(self, screen):
        if not self.current:
            screen.fill((255, 255, 255))
            return

        curr_img = self.get_bg(self.current)
        if self.previous and self.alpha > 0:
            prev_img = self.get_bg(self.previous).copy()
            temp = curr_img.copy()
            prev_img.set_alpha(self.alpha)
            temp.set_alpha(255 - self.alpha)
            screen.blit(prev_img, (0, 0))
            screen.blit(temp, (0, 0))
            self.alpha = max(0, self.alpha - self.fade_speed)
        else:
            screen.blit(curr_img, (0, 0))
            self.previous = None