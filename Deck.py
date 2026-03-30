import pygame
import random

class NobleDeck:
    def __init__(self, nobles):
        self.nobles = nobles

    def draw(self, num):
        randomdraw = random.randint(0, len(self.nobles))
        card = self.nobles.pop(randomdraw)
        return card
    
    def can_draw(self):
        if not self.nobles:
            return False
        else:
            return True

class CardDeck:
    def __init__(self, cards, level):
        self.level = level
        self.cards = cards

    def draw(self, level):
        if not self.can_draw():
            return
        randomdraw = random.randint(0, len(self.cards))
        card = self.cards.pop(randomdraw)
        return card
        
    def can_draw(self):
        if not self.cards:
            return False
        else:
            return True