import pygame
from concurrent.futures import ThreadPoolExecutor

from pygame.locals import *
from settings import * 

class Game():
    def __init__(self, workers=4):
        # pygame stuff
        pygame.init()
        self.screen = pygame.display.set_mode(WINDOW_RESOLUTION)
        pygame.display.set_caption(GAME_NAME)
        self.clock = pygame.time.Clock()

        self.running = True
        self.executor = ThreadPoolExecutor(max_workers=workers)
        # game stuffs here
        self.cards = None
        self.nobles = None
        self.shown_nobles = []
        self.players = []
        self.bank = None

    # Setting up game (can be used to restart new game)
    def init_game(self):
        # load sprites
        list(self.executor.map(x.load()) for x in self.cards)
        list(self.executor.map(x.load()) for x in self.nobles)

    def play(self):
        while self.running:
            self.handle_input()
            self.draw()
            self.update()
            self.clock.tick(FPS)
        
        pygame.quit()

    def draw(self):
        # Clear screen
        self.screen.fill((30, 30, 30))

        main_width = int(WINDOW_RESOLUTION[0] * 0.75)
        main_rect = pygame.Rect(0, 0, main_width, WINDOW_RESOLUTION[1])
        pygame.draw.rect(self.screen, (0, 200, 200), main_rect)

        side_width = WINDOW_RESOLUTION[0] - main_width
        side_height = WINDOW_RESOLUTION[1] // 3

        # other player's resource zone
        for i in range(3):
            rect = pygame.Rect(main_width, i * side_height, side_width, side_height)
            pygame.draw.rect(self.screen, (150, 150, 150), rect)
            pygame.draw.rect(self.screen, (0, 0, 0), rect, 2)  

        pygame.display.flip()

    def update(self):
        # refill cards and nobles
        pass

    def handle_input(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False