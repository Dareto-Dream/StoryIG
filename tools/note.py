import pygame

class Note:
    def __init__(self, direction, time_ms):
        self.direction = direction
        self.time_ms = time_ms
        self.hit = False
        self.missed = False
        self.judgement = None

    def get_screen_y(self, song_time, scroll_speed, hit_y):
        distance = self.time_ms - song_time
        return hit_y + distance * scroll_speed

    def is_visible(self, song_time, scroll_speed, hit_y, screen_height):
        y = self.get_screen_y(song_time, scroll_speed, hit_y)
        return -100 <= y <= screen_height + 100

    def draw(self, screen, song_time, scroll_speed, hit_y, sprite, center_x):
        if self.hit or self.missed:
            return
        y = self.get_screen_y(song_time, scroll_speed, hit_y)
        rect = sprite.get_rect(center=(center_x, int(y)))
        screen.blit(sprite, rect.topleft)
