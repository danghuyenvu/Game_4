class Player:
    def __init__(self):
        self.temp = {
            "white": 0,
            "green": 0,
            "Gold": 0,
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

    def get_gems(self, name = None):
        if name is None:
            return self.gems
        else:
            return self.gems[name]
        
    def purchase(self, gems : dict, card):
        for keys, item in gems.items():
            cur = self.gems[keys]
            if item > cur:
                return False
            self.gems[keys] =  cur - item
        self.cards.append(card)
        return True
    
    def get_cards():
        pass

        
