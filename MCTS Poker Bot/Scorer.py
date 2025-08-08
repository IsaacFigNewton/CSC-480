from typing import List, Tuple
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
    
    def get_best_hand(self):
        """
        Classify a n-card poker hand using nested if statements based on a 5-card hand criteria hierarchy.
        
        Args:
            cards: List of (rank, suit) tuples
        
        Returns:
            Tuple of (hand_name: str, best_cards: List[Tuple[int, int]])
        """
        stats = self.analyze_hand()
        
        # Start with strictest criteria and broaden
        # Has a flush
        if stats['num_suits'] < len(self.cards) - 4:
            flush_cards = self._get_flush_cards(stats)
            self.cards = flush_cards
            stats = self.analyze_hand()

            # The flush is also a straight
            if stats['straight']:
                straight_cards = self._get_straight_cards(stats)
                # Royal flush: straight flush with A high (10-J-Q-K-A)
                if set([8, 9, 10, 11, 12]).issubset(set(stats['ranks'])):
                    return 'royal_flush', straight_cards
                # Straight flush but not royal
                else:
                    return 'straight_flush', straight_cards
            
            # Flush but not a straight
            else:
                return 'flush', flush_cards

        # Has a straight
        if stats['straight']:
            # Straight but not flush
            return 'straight', self._get_straight_cards(stats)
        
        # Handle same-kind pairs
        best_cards_by_rank_group = self._get_best_cards_by_rank_groups(stats)
        match stats['max_same_rank']:
            # Four of a kind
            case 4:
                return 'four_of_a_kind', best_cards_by_rank_group
        
            # Three of a kind
            case 3:
                # Also has a pair
                if 2 in stats['rank_counts'].values():
                    return 'full_house', best_cards_by_rank_group
                else:
                    return 'three_of_a_kind', best_cards_by_rank_group
        
            # Has pairs
            case 2:
                # Two pairs
                if list(stats['rank_counts'].values()).count(2) == 2:
                    return 'two_pair', best_cards_by_rank_group
                # One pair
                else:
                    return 'pair', best_cards_by_rank_group
        
        # No pairs, no straight, no flush
        # get 5 highest cards
        high_cards = self.cards[:5]
        return 'high_card', high_cards
    

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