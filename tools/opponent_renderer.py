import pygame
from character_animations import CharacterAnimator

class OpponentRenderer:
    def __init__(self):
        self.opponents = {}
        self.scale = 1.0

    def add_opponent(self, name, sprite_map, position):
        """
        sprite_map: dict of anim name → list[Surface]
            Required: 'idle', 'singLEFT', 'singDOWN', 'singUP', 'singRIGHT'
        position: (x, y) — base position on 1280x720 grid
        """
        anim = CharacterAnimator(sprite_map, position)
        anim.rescale((1280, 720))  # default until resized
        self.opponents[name] = anim

    def remove_opponent(self, name):
        if name in self.opponents:
            del self.opponents[name]

    def clear_cache(self):
        self.opponents.clear()

    def play(self, name, direction):
        if name in self.opponents:
            self.opponents[name].play(direction)

    def release(self, name):
        if name in self.opponents:
            self.opponents[name].release()

    def update(self, dt):
        for anim in self.opponents.values():
            anim.update(dt)

    def draw(self, screen):
        for anim in self.opponents.values():
            anim.draw(screen)

    def rescale(self, screen_size):
        for anim in self.opponents.values():
            anim.rescale(screen_size)
