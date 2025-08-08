import numpy as np

class PokerMCTS:
	def __init__(self):
		num_ranks = 13
		num_suits = 4
		all_cards = [(i, j) for i, j in np.ndindex((num_ranks, num_suits))]
		# get all UNIQUE player holes
		#    2 holes are the same if they vary only in card order,
		#    card order is removed as a differentiating property via card sorting
		#    cards are sorted by rank, then suit
		possible_player_holes = {
			sorted(c)
			for c in zip(all_cards, all_cards)
			if c[0] != c[1]
		}
		win_rates = {
			hole: 0.0
			for hole in possible_player_holes
		}