from typing import List, Tuple, Dict, Optional
from collections import Counter

class Scorer:
    def __init__(self,
                 cards: List[Tuple[int, int]]):
        self.cards = sorted(
            cards,
            key=lambda x: x[0],
            reverse=True
        )
    
    def analyze_hand(self):
        """
        Analyze a hand of cards and return statistics needed for hand classification.
        
        Args:
            cards: List of tuples (rank, suit) where rank 0-12 (2-A) and suit 0-3
        
        Returns:
            Dictionary with hand statistics
        """
        ranks = [card[0] for card in self.cards]
        suits = [card[1] for card in self.cards]
        
        rank_counts = Counter(ranks)
        suit_counts = Counter(suits)
        
        # Count pairs (groups of 2 or more cards of same rank)
        pairs = sum(1 for count in rank_counts.values() if count >= 2)
        
        # Number of different suits
        num_suits = len(suit_counts)
        
        # Check for straights (including A-2-3-4-5 wheel)
        unique_ranks = sorted(set(ranks))
        longest_straight = 1
        current_straight = 1
        
        # Check normal straights
        for i in range(1, len(unique_ranks)):
            if unique_ranks[i] == unique_ranks[i-1] + 1:
                current_straight += 1
                longest_straight = max(longest_straight, current_straight)
            else:
                current_straight = 1
        
        # Check for normal and wheel straights (A-2-3-4-5)
        has_straight = False
        if longest_straight >= 5\
            or set([12, 0, 1, 2, 3]).issubset(set(ranks)):  # A,2,3,4,5
            has_straight = True
        
        # Max same rank count
        max_same_rank = max(rank_counts.values()) if rank_counts else 1
        
        # High card (highest rank)
        high_card = max(ranks) if ranks else 0
        
        return {
            'pairs': pairs,
            'num_suits': num_suits,
            'straight': has_straight,
            'max_same_rank': max_same_rank,
            'high_card': high_card,
            'ranks': ranks,
            'suits': suits,
            'rank_counts': rank_counts,
            'suit_counts': suit_counts
        }
    
    def _get_straight_cards(self, stats) -> List[Tuple[int, int]]:
        """Get the 5 cards that form the best straight."""
        ranks = stats['ranks']
        
        # Check for wheel straight (A-2-3-4-5) first
        if set([12, 0, 1, 2, 3]).issubset(set(ranks)):
            wheel_ranks = [12, 0, 1, 2, 3]
            straight_cards = []
            for rank in wheel_ranks:
                # Find a card with this rank
                for card in self.cards:
                    if card[0] == rank and card not in straight_cards:
                        straight_cards.append(card)
                        break
            if len(straight_cards) == 5:
                return straight_cards
        
        # Check for regular straights
        unique_ranks = sorted(set(ranks))
        for i in range(len(unique_ranks) - 4):
            consecutive = True
            for j in range(1, 5):
                if unique_ranks[i + j] != unique_ranks[i + j - 1] + 1:
                    consecutive = False
                    break
            
            if consecutive:
                # Found a straight, get the cards
                straight_ranks = unique_ranks[i:i+5]
                straight_cards = []
                for rank in straight_ranks:
                    for card in self.cards:
                        if card[0] == rank and card not in straight_cards:
                            straight_cards.append(card)
                            break
                return straight_cards
        
        return []
    
    def _get_flush_cards(self, stats) -> List[Tuple[int, int]]:
        """Get the 5 highest cards of the flush suit."""
        # Find the suit with 5+ cards
        for suit, count in stats['suit_counts'].items():
            if count >= 5:
                # Get all cards of this suit and sort by rank (highest first)
                flush_cards = [
                    card
                    for card in self.cards
                    if card[1] == suit
                ]
                flush_cards.sort(key=lambda x: x[0], reverse=True)
                return flush_cards[:5]
        return []
    
    def _get_best_cards_by_rank_groups(self, stats) -> List[Tuple[int, int]]:
        """Get the best 5 cards based on rank groups (pairs, trips, quads)."""
        rank_counts = stats['rank_counts']
        cards_by_rank = {}
        
        # Group cards by rank
        for card in self.cards:
            rank = card[0]
            if rank not in cards_by_rank:
                cards_by_rank[rank] = []
            cards_by_rank[rank].append(card)
        
        # Sort ranks by count (descending) then by rank (descending)
        sorted_ranks = sorted(
            rank_counts.keys(), 
            key=lambda x: (rank_counts[x], x), 
            reverse=True
        )
        
        best_cards = []
        for rank in sorted_ranks:
            cards_of_rank = cards_by_rank[rank]
            best_cards += cards_of_rank
            if len(best_cards) >= 5:
                break
        
        return best_cards[:5]
    
    def get_possible_hands(self) -> Dict[str, Optional[List[Tuple[int, int]]]]:
        """
        Get all possible hands that can be made from the cards.
        
        Returns:
            Dictionary with hand names as keys and associated cards as values,
            or None if the hand cannot be made
        """
        stats = self.analyze_hand()
        possible_hands = {}
        
        # Check for flush
        flush_cards = self._get_flush_cards(stats)
        has_flush = len(flush_cards) == 5
        
        if has_flush:
            # Create temporary scorer with flush cards to check for straight flush
            temp_scorer = Scorer(flush_cards)
            flush_stats = temp_scorer.analyze_hand()
            
            if flush_stats['straight']:
                straight_cards = temp_scorer._get_straight_cards(flush_stats)
                # Check for royal flush
                if set([8, 9, 10, 11, 12]).issubset(set([card[0] for card in straight_cards])):
                    possible_hands['royal_flush'] = straight_cards
                    possible_hands['straight_flush'] = straight_cards  # Royal flush is also a straight flush
                else:
                    possible_hands['royal_flush'] = None
                    possible_hands['straight_flush'] = straight_cards
            else:
                possible_hands['royal_flush'] = None
                possible_hands['straight_flush'] = None
            
            possible_hands['flush'] = flush_cards
        else:
            possible_hands['royal_flush'] = None
            possible_hands['straight_flush'] = None
            possible_hands['flush'] = None
        
        # Check for straight (always check, regardless of flush)
        if stats['straight']:
            possible_hands['straight'] = self._get_straight_cards(stats)
        else:
            possible_hands['straight'] = None
        
        # Check for same-rank combinations
        best_cards_by_rank_group = self._get_best_cards_by_rank_groups(stats)
        
        # Four of a kind
        if stats['max_same_rank'] >= 4:
            possible_hands['four_of_a_kind'] = best_cards_by_rank_group
        else:
            possible_hands['four_of_a_kind'] = None
        
        # Full house (needs both 3 of a kind AND a pair)
        if stats['max_same_rank'] >= 3 and 2 in stats['rank_counts'].values():
            possible_hands['full_house'] = best_cards_by_rank_group
        else:
            possible_hands['full_house'] = None
        
        # Three of a kind (any hand with 3+ of same rank)
        if stats['max_same_rank'] >= 3:
            possible_hands['three_of_a_kind'] = best_cards_by_rank_group
        else:
            possible_hands['three_of_a_kind'] = None
        
        # Two pair (exactly 2 pairs, or more pairs/groups that contain 2 pairs)
        pair_ranks = [rank for rank, count in stats['rank_counts'].items() if count >= 2]
        if len(pair_ranks) >= 2:
            possible_hands['two_pair'] = best_cards_by_rank_group
        else:
            possible_hands['two_pair'] = None
        
        # One pair (any hand with at least one pair)
        if stats['max_same_rank'] >= 2:
            possible_hands['pair'] = best_cards_by_rank_group
        else:
            possible_hands['pair'] = None
        
        # High card (always possible)
        possible_hands['high_card'] = self.cards[:5]
        
        return possible_hands
    
    def get_best_hand(self):
        """
        Get the best possible hand from all available hands.
        
        Returns:
            Tuple of (hand_name: str, best_cards: List[Tuple[int, int]])
        """
        possible_hands = self.get_possible_hands()
        
        # Define hand hierarchy (best to worst)
        hand_hierarchy = [
            'royal_flush',
            'straight_flush', 
            'four_of_a_kind',
            'full_house',
            'flush',
            'straight',
            'three_of_a_kind',
            'two_pair',
            'pair',
            'high_card'
        ]
        
        # Find the best available hand
        for hand_name in hand_hierarchy:
            if possible_hands[hand_name] is not None:
                return hand_name, possible_hands[hand_name]
        
        # This should never happen since high_card is always available
        return 'high_card', self.cards[:5]
    

    def score(self) -> int:
        """
        Calculate a numeric score for the hand that allows for proper ranking.
        Higher scores indicate better hands. Assumes kickers are handled separately.
        
        Scoring system:
        - Royal Flush: 90000
        - Straight Flush: 80000 + high_card_rank
        - Four of a Kind: 70000 + quad_rank
        - Full House: 60000 + (trips_rank * 100) + pair_rank
        - Flush: 50000 + high_card_rank
        - Straight: 40000 + high_card_rank (with special handling for wheel)
        - Three of a Kind: 30000 + trips_rank
        - Two Pair: 20000 + (high_pair * 100) + low_pair
        - One Pair: 10000 + pair_rank
        - High Card: high_card_rank
        
        Returns:
            Integer score for the hand
        """
        hand_name, best_cards = self.get_best_hand()
        is_wheel_straight = set([12, 0, 1, 2, 3]).issubset(set([card[0] for card in best_cards]))

        # Sort best cards by rank (highest first)
        sorted_cards = sorted(best_cards, key=lambda x: x[0], reverse=True)
        
        if hand_name == 'royal_flush':
            return 90000
        
        elif hand_name == 'straight_flush':
            # Handle wheel straight flush (A-2-3-4-5) as lowest straight flush
            if is_wheel_straight:
                return 80003
            else:
                return 80000 + sorted_cards[0]
        
        elif hand_name == 'four_of_a_kind':
            # Find the quad rank
            rank_counts = Counter([card[0] for card in best_cards])
            quad_rank = max(rank for rank, count in rank_counts.items() if count == 4)
            return 70000 + quad_rank
        
        elif hand_name == 'full_house':
            # Find triple and pair ranks
            rank_counts = Counter([card[0] for card in best_cards])
            triple_rank = max(rank for rank, count in rank_counts.items() if count == 3)
            pair_rank = max(rank for rank, count in rank_counts.items() if count == 2)
            return 60000 + (trips_rank * 100) + triple_rank
        
        elif hand_name == 'flush':
            # Use highest card for flush ranking
            high_card = max(card[0] for card in best_cards)
            return 50000 + high_card
        
        elif hand_name == 'straight':
            # Handle wheel straight (A-2-3-4-5) as lowest straight
            if is_wheel_straight:
                return 40003
            else:
                high_card = max(card[0] for card in best_cards)
                return 40000 + high_card
        
        elif hand_name == 'three_of_a_kind':
            # Find trips rank
            rank_counts = Counter([card[0] for card in best_cards])
            trips_rank = max(rank for rank, count in rank_counts.items() if count == 3)
            return 30000 + trips_rank
        
        elif hand_name == 'two_pair':
            # Find both pair ranks
            rank_counts = Counter([card[0] for card in best_cards])
            pairs = sorted([rank for rank, count in rank_counts.items() if count == 2], reverse=True)
            high_pair, low_pair = pairs[0], pairs[1]
            return 20000 + (high_pair * 100) + low_pair
        
        elif hand_name == 'pair':
            # Find pair rank
            rank_counts = Counter([card[0] for card in best_cards])
            pair_rank = max(rank for rank, count in rank_counts.items() if count == 2)
            return 10000 + pair_rank
        
        else:
            # Use highest card
            return sorted_cards[0]