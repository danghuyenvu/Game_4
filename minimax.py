import copy
from itertools import combinations
from Deck import card_cost_to_dict
from player import RandomBot

class MinmaxPlayer(RandomBot):
    def __init__(self, search_depth=5):
        super().__init__()
        self.search_depth = search_depth

    # ===== ENTRY =====
    def get_action(self, cards, bank, players=None, shown_nobles=None):
        if players is None:
            players = []
        if shown_nobles is None:
            shown_nobles = []

        current_idx = next((i for i, p in enumerate(players) if p is self), 0)
        _, action = self.minimax(
            cards,
            bank,
            players,
            depth=self.search_depth,
            alpha=-float("inf"),
            beta=float("inf"),
            maximizing=True,
            current_idx=current_idx,
            bot_idx=current_idx,
            shown_nobles=shown_nobles
        )

        if action:
            if action[0] == "RESERVE" and bank.can_book() and sum(self.temp.values()) + 1 <= 10:
                self.total_temp += 1
            self.apply_action(action)

        return self.current_action

    # ===== APPLY TO REAL GAME =====
    def apply_action(self, action):
        action_type, action_data = action

        if action_type == "BUY":
            self.current_action = "BUY"
            self.choosing_card = action_data

        elif action_type == "RESERVE":
            self.current_action = "RESERVE"
            self.choosing_card = action_data

        elif action_type == "TAKE3":
            self.current_action = "TAKE 3"
            self.selected_gems = action_data
            self.total_temp += len(action_data)

        elif action_type == "TAKE2":
            self.current_action = "TAKE 2"
            self.selected_gem = action_data
            self.total_temp += 2

    # ===== ACTION GENERATION =====
    def get_actions(self, board, bank, player):
        actions = []
        keys = ["black", "blue", "green", "red", "white"]

        visible_cards = board[:]
        all_cards = visible_cards + player.deposit_card

        # ===== BUY =====
        for card in all_cards:
            cost = card_cost_to_dict(card)
            if self.can_purchase_sim(player, cost):
                actions.append(("BUY", card))

        # ===== RESERVE =====
        if len(player.deposit_card) < 3:
            for card in visible_cards:
                actions.append(("RESERVE", card))

        # ===== TAKE 3 =====
        current_gems = sum(player.temp.values())
        available_colors = [i for i in range(5) if bank.gem[i] > 0]

        if current_gems + 3 <= 10:
            for combo in combinations(available_colors, 3):
                if bank.can_take_3(combo):
                    actions.append(("TAKE3", list(combo)))

        # ===== TAKE 2 =====
        if current_gems + 2 <= 10:
            for i in available_colors:
                if bank.can_take_2(i):
                    actions.append(("TAKE2", i))

        return actions

    # ===== MINIMAX + ALPHA-BETA =====
    def minimax(self, board, bank, players, depth, alpha, beta, maximizing, current_idx, bot_idx, shown_nobles=None):
        if shown_nobles is None:
            shown_nobles = []
        if depth == 0:
            return self.evaluate(players, bot_idx), None

        actions = self.get_actions(board, bank, players[current_idx])
        if not actions:
            return self.evaluate(players, bot_idx), None

        if maximizing:
            best_val = -float("inf")
            best_action = None

            for action in actions:
                next_board, next_bank, next_players, next_nobles = self.simulate(
                    action, board, bank, players, current_idx, shown_nobles
                )

                val, _ = self.minimax(
                    next_board,
                    next_bank,
                    next_players,
                    depth - 1,
                    alpha,
                    beta,
                    False,
                    (current_idx + 1) % len(players),
                    bot_idx,
                    shown_nobles=next_nobles
                )

                if val > best_val:
                    best_val = val
                    best_action = action

                alpha = max(alpha, val)
                if beta <= alpha:
                    break

            return best_val, best_action

        best_val = float("inf")

        for action in actions:
            next_board, next_bank, next_players, next_nobles = self.simulate(
                action, board, bank, players, current_idx, shown_nobles
            )

            val, _ = self.minimax(
                next_board,
                next_bank,
                next_players,
                depth - 1,
                alpha,
                beta,
                True,
                (current_idx + 1) % len(players),
                bot_idx,
                shown_nobles=next_nobles
            )

            best_val = min(best_val, val)
            beta = min(beta, val)
            if beta <= alpha:
                break

        return best_val, None

    # ===== EVALUATION =====
    def evaluate(self, players, bot_idx):
        me = players[bot_idx]

        temp_total = sum(me.temp.values())
        perm_total = sum(me.perm.values())

        score = (
            me.point * 3 +
            temp_total +
            perm_total * 2 +
            temp_total
        )

        opp = sum(p.point for i, p in enumerate(players) if i != bot_idx)
        return score - opp * 2

    # ===== SIMULATION =====
    def simulate(self, action, board, bank, players, idx, shown_nobles=None):
        board_copy = board.copy()
        bank_copy = bank.copy() if hasattr(bank, "copy") else copy.deepcopy(bank)
        players_copy = [p.copy() if hasattr(p, "copy") else copy.deepcopy(p) for p in players]
        nobles_copy = shown_nobles.copy() if shown_nobles else []

        player = players_copy[idx]
        keys = ["black", "blue", "green", "red", "white"]
        action_type, action_data = action

        if action_type == "TAKE3":
            if bank_copy.get_3(action_data):
                for i in action_data:
                    player.temp[keys[i]] += 1
                    player.total_temp += 1

        elif action_type == "TAKE2":
            if bank_copy.get_2(action_data):
                player.temp[keys[action_data]] += 2
                player.total_temp += 2

        elif action_type == "BUY":
            cost = card_cost_to_dict(action_data)
            payment = player.purchase(cost, action_data)
            if payment:
                bank_copy.pay(payment)
                player.total_temp = max(player.total_temp - sum(payment), 0)
                self._add_perm_bonus(player, action_data)
                if action_data in board_copy:
                    board_copy.remove(action_data)

        elif action_type == "RESERVE":
            if len(player.deposit_card) < 3:
                player.deposit(action_data)
                if action_data in board_copy:
                    board_copy.remove(action_data)
                if bank_copy.can_book() and player.total_temp + 1 <= 10:
                    bank_copy.gem[5] -= 1
                    player.temp["gold"] += 1
                    player.total_temp += 1

        self._acquire_available_nobles(player, nobles_copy)
        return board_copy, bank_copy, players_copy, nobles_copy

    def _add_perm_bonus(self, player, card):
        color_map = {
            "Black": "black",
            "Blue": "blue",
            "Green": "green",
            "Red": "red",
            "White": "white"
        }
        bonus_color = color_map.get(card.color)
        if bonus_color:
            player.perm[bonus_color] = player.perm.get(bonus_color, 0) + 1

    def _acquire_available_nobles(self, player, shown_nobles):
        perm_gems = [player.perm.get(color, 0) for color in ["black", "blue", "green", "red", "white"]]
        available_nobles = [noble for noble in shown_nobles if noble.can_get(perm_gems)]
        if not available_nobles:
            return

        best_noble = max(available_nobles, key=lambda n: n.points)
        player.add_noble(best_noble)
        shown_nobles.remove(best_noble)

    # ===== PURCHASE CHECK =====
    def can_purchase_sim(self, player, cost):
        gold = player.temp.get("gold", 0)

        for color, amount in cost.items():
            available = player.temp.get(color, 0) + player.perm.get(color, 0)
            if available >= amount:
                continue

            need = amount - available
            if gold >= need:
                gold -= need
            else:
                return False

        return True
