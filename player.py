from Deck import *
class Player:
    def __init__(self):
        self.temp = {
            "white": 0,
            "green": 0,
            "gold": 0,
            "red": 0,
            "black": 0,
            "blue": 0
        }

        self.cards = []

        self.perm = {
            "white": 0,
            "green": 0,
            "red": 0,
            "black": 0,
            "blue": 0
        }
        self.deposit_card = []

    def get_gems(self, name = None):
        if name is None:
            return self.gems
        else:
            return self.gems[name]
        
    def purchase(self, gems : dict, card: Card):
        for keys, item in gems.items():
            cur = self.gems[keys]
            if item > cur:
                return False
            self.gems[keys] =  cur - item
        self.cards.append(card)
        self.perm[card.color] = self.perm[card.color] + 1
        for idx in range(len(self.deposit_card)):
            if card.is_same_card(self.deposit_card[idx]):
                self.deposit_card.pop(idx)
                break
        return True
    
    def deposit(self, card : Card):
        self.temp["gold"] = self.temp["gold"] + 1
        self.deposit_card.append[card]

    def get_deposit_card(self, num = None):
        if num is not None and num < len(self.deposit_card):
            return self.deposit_card[num]
        else:
            return self.deposit_card
    
