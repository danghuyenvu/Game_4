import pygame
from concurrent.futures import ThreadPoolExecutor

from pygame.locals import *
from settings import * 
from Deck import *
from bank import *
import time

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

        self.level1 = None
        self.level2 = None
        self.level3 = None

        self.board = {}

        self.gems = []
        # Sửa dòng này trong __init__
        for gem_name in GEMS_INDEX:
            img = pygame.image.load(f"asset/{gem_name}.png").convert_alpha()
            self.gems.append(img)

        self.current_player = 0
        self.num_player = 2

    # Setting up game (can be used to restart new game)
    def init_game(self, num_player = 2):
        if not hasattr(self, 'font'):
            self.font = pygame.font.SysFont("Arial", 16, bold=True)
        cards_by_level, self.cards, self.nobles = process_card_data()
        self.level1 = CardDeck(cards_by_level[1], 1)
        self.level2 = CardDeck(cards_by_level[2], 2)
        self.level3 = CardDeck(cards_by_level[3], 3)
        self.board = {
            1: [self.level1.draw() for _ in range(4)],
            2: [self.level2.draw() for _ in range(4)],
            3: [self.level3.draw() for _ in range(4)]
        }
        self.num_player = num_player
        
        self.bank = Bank(self.gems, None, num_player)
        # load sprites trước khi draw
        for card in self.cards:
            self.executor.submit(card.load)
        for noble in self.nobles.nobles:
            self.executor.submit(noble.load)
        
        # Chờ noble load xong trước khi bắt đầu game
        for noble in self.nobles.nobles:
            while noble.image is None:
                time.sleep(0.01)
        
        self.shown_nobles = [self.nobles.draw() for _ in range(num_player + 1)]

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
        main_height = WINDOW_RESOLUTION[1]

        main_rect = pygame.Rect(0, 0, main_width, WINDOW_RESOLUTION[1])
        pygame.draw.rect(self.screen, (0, 200, 200), main_rect)


        # 2. Draw NOBLE
        noble_rect = pygame.Rect(START_X , 20, CARD_W, CARD_W) 
        pygame.draw.rect(self.screen, (100, 100, 100), noble_rect)
        for i, noble in enumerate(self.shown_nobles):
            noble_rect = pygame.Rect(START_X + (i + 1) * (CARD_W + GAP), 20, CARD_W, CARD_W) # Noble thường hình vuông
            pygame.draw.rect(self.screen, (255, 255, 255), noble_rect, 2)
            noble.draw(self.screen,(START_X + (i + 1) * (CARD_W + GAP), 20))

        # 3. Draw card on BOARD 
        for level in [3, 2, 1]:
            # Tính tọa độ Y dựa trên Level (3 là cao nhất)
            row_y = 150 + (3 - level) * (CARD_H + GAP)
            
            # Vẽ tập bài (Deck) của level đó (đại diện bằng 1 hình chữ nhật)
            deck_rect = pygame.Rect(START_X, row_y, CARD_W, CARD_H)
            pygame.draw.rect(self.screen, (100, 100, 100), deck_rect)
            
            # Vẽ các lá bài đang lật trên bàn
            if level in self.board:
                for i, card in enumerate(self.board[level]):
                    card_x = START_X + (i + 1) * (CARD_W + GAP)
                    card_rect = pygame.Rect(card_x, row_y, CARD_W, CARD_H)
                    
                    # Vẽ khung lá bài
                    color_map = {"Black": (0,0,0), "Blue": (0,0,255), "Red": (255,0,0), "Green": (0,255,0), "White": (255,255,255)}
                    bg_color = color_map.get(card.color, (200, 200, 200))
                    
                    pygame.draw.rect(self.screen, bg_color, card_rect)
                    pygame.draw.rect(self.screen, (255, 255, 255), card_rect, 2)
                    
                    # Nếu card đã load xong image:
                    if card.image:
                        card.draw(self.screen, (card_x, row_y))
        # 4. Draw gem
        gems_start_x = START_X + 5 * (CARD_W + GAP) + 30 
        # Vị trí Y: Bắt đầu ngang với hàng bài Level 3 hoặc Noble
        gems_start_y = 150 
        
        # Khoảng cách dọc giữa các viên đá (có thể tăng lên một chút cho thoáng)
        VERTICAL_GAP = 10

        for i, gem_img in enumerate(self.gems):
            # Chỉ tính toán theo hàng dọc (row), không dùng cột (col)
            gem_x = gems_start_x
            gem_y = gems_start_y + i * (GEM_SIZE + VERTICAL_GAP)
            
            # Vẽ hình ảnh viên đá
            scaled_gem = pygame.transform.smoothscale(gem_img, (GEM_SIZE, GEM_SIZE))
            self.screen.blit(scaled_gem, (gem_x, gem_y))
            
            # Vẽ số lượng đá còn lại trong Bank
            if self.bank:
                # Lấy số lượng dựa trên index từ mảng bank.gem
                count = self.bank.gem[i]
                
                count_txt = self.font.render(str(count), True, (255, 255, 255))
                # Căn giữa số vào viên đá hoặc để ở góc dưới bên phải
                txt_rect = count_txt.get_rect(bottomright=(gem_x + GEM_SIZE - 5, gem_y + GEM_SIZE - 5))
                self.screen.blit(count_txt, txt_rect)

        # 5. Draw action box
        action_zone_h = 150
        action_rect = pygame.Rect(0, main_height - action_zone_h, main_width, action_zone_h)
        pygame.draw.rect(self.screen, (40, 40, 40), action_rect)
        pygame.draw.rect(self.screen, (0, 255, 200), action_rect, 3) # Viền nổi bật cho người chơi hiện tại

        # def action
        actions = [
            "1. TAKE 3 GEMS",
            "2. TAKE 2 GEMS",
            "3. RESERVE CARD",
            "4. BUY CARD"
        ]
        

        # position in map
        start_button_x = main_width - (ACTION_BTN_W + ACTION_GAP) * 2 - ACTION_GAP
        start_button_y = main_height - action_zone_h + ACTION_GAP 

        for i, text in enumerate(actions):
            # Sắp xếp thành lưới 2x2
            col = i % 2
            row = i // 2
            
            bx = start_button_x + col * (ACTION_BTN_W + ACTION_GAP)
            by = start_button_y + row * (60 + ACTION_GAP) # 60 là chiều cao nút rút gọn
            
            btn_rect = pygame.Rect(bx, by, ACTION_BTN_W, 60)
            
            # Vẽ nút
            pygame.draw.rect(self.screen, (60, 60, 60), btn_rect) # Màu nền nút
            pygame.draw.rect(self.screen, (255, 255, 255), btn_rect, 2) # Viền nút
            
            # Vẽ text
            words = text.split(" ")
            # Render text đơn giản (Bạn có thể tối ưu vẽ nhiều dòng nếu text dài)
            txt_surf = self.font.render(text, True, (255, 255, 255))
            txt_rect = txt_surf.get_rect(center=btn_rect.center)
            self.screen.blit(txt_surf, txt_rect)


        side_width = WINDOW_RESOLUTION[0] - main_width
        side_height = WINDOW_RESOLUTION[1] // 3

        # other player's resource zone
        for i in range(3):
            rect = pygame.Rect(main_width, i * side_height, side_width, side_height)
            pygame.draw.rect(self.screen, (150, 150, 150), rect)
            pygame.draw.rect(self.screen, (0, 0, 0), rect, 2)  
        


        
        pygame.display.flip()

    def update(self):
        for level in [1,2,3]:
            while len(self.board[level]) < 4:
                card = getattr(self, f"level{level}").draw()
                if card:
                    self.board[level].append(card)

    def handle_input(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False

    def next_turn(self):
        self.current_player = (self.current_player + 1) % len(self.players)