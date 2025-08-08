from typing import List, Tuple, Any, Dict
import random

class GameState:
	def __init__(
			self,
			all_cards: List[Tuple[int, int]],
			player_hole: List[Tuple[int, int]]
		):
		# store the deck and holes as lists of tuples
		self.deck = [c for c in all_cards if c not in player_hole]
		self.player = player_hole
		self.opponent = set()
		self.community = list()
    
	def get_card_from_deck(self):
	    return self.deck.pop(random.randint(len(self.deck)))
    
	def set_opponent_hole(self):
        self.opponent.append(self.get_card_from_deck())
        self.opponent.append(self.get_card_from_deck())
	def set_flop(self):
        self.community.append(self.get_card_from_deck())
        self.community.append(self.get_card_from_deck())
        self.community.append(self.get_card_from_deck())
	def set_river(self):
	    self.community.append(self.get_card_from_deck())
	def set_river(self):
	    self.community.append(self.get_card_from_deck())
	
	def get_kicker(self):
        # sort cards by rank, then suit
        player_hole_sorted = sorted(
            self.player,
            reverse=True
        )
        opponent_hole_sorted = sorted(
            self.opponent,
            reverse=True
        )
        # loop through all cards in player, opponent hands
        for i in range(len(player_hole_sorted)):
            high_card_diff = player_hole_sorted[i] - opponent_hole_sorted[i]
            if high_card_diff != 0:
                return high_card_diff > 0
        # if it's somehow a perfect tie, return a win
        return True

    def is_winner(self):
        player_score = self.score(self.player)
        opponent_score = self.score(self.opponent)
        match player_score - opponent_score:
            case > 0:
                return True
            case == 0:
                return self.get_kicker()
            case < 0:
                return False