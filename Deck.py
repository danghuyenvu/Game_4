import pygame
from __future__ import annotations
from pygame.locals import *


class Card:
    def __init__(self, level, resources: list, color=None, points=0, path_dir=None):
        self.level = level
        self.color = color 
        self.resources = resources
        self.points = points
        self.dir = f"asset/level{level}/{path_dir}" if path_dir is not None else None
        self.image = None
        self.is_draw = False

    def load(self):
        if self.image is None:
            self.image = pygame.image.load(self.dir).convert_alpha()

    # draw based on center
    def draw(self, screen, position):
        if self.is_draw:
            screen.blit(self.image)

    def is_same_card(self, card: 'Card'):
        if not card:
            return False
        return self.level == card.level and self.color == card.color and self.points == card.points and len(self.resources) == len(card.resources) and all(self.resources[idx] == card.resources[idx] for idx in range(len(self.resources)))

class Noble(Card):
    def __init__(self, level, color, resources, points=0, path_dir=None):
        super().__init__(level, color, resources, points, None)
        self.dir = path_dir