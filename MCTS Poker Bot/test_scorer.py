import pytest
from collections import Counter
from Scorer import Scorer


class TestScorer:
    """Test suite for the Scorer class."""
    
    def test_init_sorts_cards(self):
        """Test that cards are sorted by rank in descending order."""
        cards = [(5, 0), (12, 1), (3, 2), (10, 3)]  # Mixed order
        scorer = Scorer(cards)
        expected = [(12, 1), (10, 3), (5, 0), (3, 2)]  # Sorted by rank desc
        assert scorer.cards == expected
    
    def test_analyze_hand_basic(self):
        """Test basic hand analysis functionality."""
        # Test with a simple hand
        cards = [(12, 0), (12, 1), (5, 2), (3, 3), (2, 0)]  # Pair of Aces
        scorer = Scorer(cards)
        stats = scorer.analyze_hand()
        
        assert stats['max_same_rank'] == 2
        assert stats['pairs'] == 1
        assert stats['num_suits'] == 4
        assert stats['high_card'] == 12
        assert not stats['straight']
        assert stats['rank_counts'][12] == 2
    
    def test_analyze_hand_straight(self):
        """Test straight detection."""
        # Regular straight: 8-9-10-J-Q
        cards = [(8, 0), (9, 1), (10, 2), (11, 3), (7, 0)]
        scorer = Scorer(cards)
        stats = scorer.analyze_hand()
        assert not stats['straight']  # Only 4 consecutive cards
        
        # Add the missing card for a straight
        cards = [(8, 0), (9, 1), (10, 2), (11, 3), (12, 0)]  # 8-9-10-J-Q
        scorer = Scorer(cards)
        stats = scorer.analyze_hand()
        assert stats['straight']
    
    def test_analyze_hand_wheel_straight(self):
        """Test wheel straight (A-2-3-4-5) detection."""
        cards = [(12, 0), (0, 1), (1, 2), (2, 3), (3, 0)]  # A-2-3-4-5
        scorer = Scorer(cards)
        stats = scorer.analyze_hand()
        assert stats['straight']
    
    def test_get_straight_cards_regular(self):
        """Test getting cards for a regular straight."""
        cards = [(8, 0), (9, 1), (10, 2), (11, 3), (12, 0), (5, 1)]
        scorer = Scorer(cards)
        stats = scorer.analyze_hand()
        straight_cards = scorer._get_straight_cards(stats)
        
        expected_ranks = {8, 9, 10, 11, 12}
        actual_ranks = {card[0] for card in straight_cards}
        assert actual_ranks == expected_ranks
        assert len(straight_cards) == 5
    
    def test_get_straight_cards_wheel(self):
        """Test getting cards for a wheel straight."""
        cards = [(12, 0), (0, 1), (1, 2), (2, 3), (3, 0), (10, 1)]
        scorer = Scorer(cards)
        stats = scorer.analyze_hand()
        straight_cards = scorer._get_straight_cards(stats)
        
        expected_ranks = {12, 0, 1, 2, 3}
        actual_ranks = {card[0] for card in straight_cards}
        assert actual_ranks == expected_ranks
        assert len(straight_cards) == 5
    
    def test_get_flush_cards(self):
        """Test getting cards for a flush."""
        # 5 spades (suit 1)
        cards = [(12, 1), (10, 1), (8, 1), (5, 1), (2, 1), (7, 0)]
        scorer = Scorer(cards)
        stats = scorer.analyze_hand()
        flush_cards = scorer._get_flush_cards(stats)
        
        assert len(flush_cards) == 5
        assert all(card[1] == 1 for card in flush_cards)  # All spades
        # Should be sorted by rank descending
        ranks = [card[0] for card in flush_cards]
        assert ranks == sorted(ranks, reverse=True)
    
    def test_get_best_cards_by_rank_groups(self):
        """Test getting best cards by rank groups."""
        # Full house: three 10s, pair of 5s
        cards = [(10, 0), (10, 1), (10, 2), (5, 3), (5, 0), (2, 1)]
        scorer = Scorer(cards)
        stats = scorer.analyze_hand()
        best_cards = scorer._get_best_cards_by_rank_groups(stats)
        
        assert len(best_cards) == 5
        ranks = [card[0] for card in best_cards]
        # Should prioritize trips then pair
        assert ranks.count(10) == 3
        assert ranks.count(5) == 2

    def test_possible_hands_high_card(self):
        """Test possible hands for high card only."""
        cards = [(12, 0), (10, 1), (8, 2), (5, 3), (2, 0)]
        scorer = Scorer(cards)
        possible = scorer.get_possible_hands()
        
        # Only high card should be possible
        assert possible['high_card'] is not None
        assert possible['pair'] is None
        assert possible['two_pair'] is None
        assert possible['three_of_a_kind'] is None
        assert possible['straight'] is None
        assert possible['flush'] is None
        assert possible['full_house'] is None
        assert possible['four_of_a_kind'] is None
        assert possible['straight_flush'] is None
        assert possible['royal_flush'] is None
    
    def test_possible_hands_pair(self):
        """Test possible hands for a pair."""
        cards = [(12, 0), (12, 1), (8, 2), (5, 3), (2, 0)]
        scorer = Scorer(cards)
        possible = scorer.get_possible_hands()
        
        # Pair and high card should be possible
        assert possible['high_card'] is not None
        assert possible['pair'] is not None
        assert possible['two_pair'] is None
        assert possible['three_of_a_kind'] is None
    
    def test_possible_hands_two_pair(self):
        """Test possible hands for two pair."""
        cards = [(12, 0), (12, 1), (8, 2), (8, 3), (2, 0)]
        scorer = Scorer(cards)
        possible = scorer.get_possible_hands()
        
        # Two pair, pair, and high card should be possible
        assert possible['high_card'] is not None
        assert possible['pair'] is not None
        assert possible['two_pair'] is not None
        assert possible['three_of_a_kind'] is None
    
    def test_possible_hands_three_of_a_kind(self):
        """Test possible hands for three of a kind."""
        cards = [(12, 0), (12, 1), (12, 2), (8, 3), (2, 0)]
        scorer = Scorer(cards)
        possible = scorer.get_possible_hands()
        
        # Three of a kind, pair, and high card should be possible
        assert possible['high_card'] is not None
        assert possible['pair'] is not None
        assert possible['two_pair'] is None  # No second pair
        assert possible['three_of_a_kind'] is not None
        assert possible['full_house'] is None
    
    def test_possible_hands_full_house(self):
        """Test possible hands for full house."""
        cards = [(12, 0), (12, 1), (12, 2), (8, 3), (8, 0)]
        scorer = Scorer(cards)
        possible = scorer.get_possible_hands()
        
        # Full house, three of a kind, two pair, pair, and high card should be possible
        assert possible['high_card'] is not None
        assert possible['pair'] is not None
        assert possible['two_pair'] is not None
        assert possible['three_of_a_kind'] is not None
        assert possible['full_house'] is not None
        assert possible['four_of_a_kind'] is None
    
    def test_possible_hands_four_of_a_kind(self):
        """Test possible hands for four of a kind."""
        cards = [(12, 0), (12, 1), (12, 2), (12, 3), (8, 0)]
        scorer = Scorer(cards)
        possible = scorer.get_possible_hands()
        
        # Four of a kind, three of a kind, pair, and high card should be possible
        assert possible['high_card'] is not None
        assert possible['pair'] is not None
        assert possible['two_pair'] is None  # No second pair
        assert possible['three_of_a_kind'] is not None
        assert possible['full_house'] is None  # No second pair
        assert possible['four_of_a_kind'] is not None
    
    def test_possible_hands_straight(self):
        """Test possible hands for straight."""
        cards = [(8, 0), (9, 1), (10, 2), (11, 3), (12, 0)]
        scorer = Scorer(cards)
        possible = scorer.get_possible_hands()
        
        assert possible['straight'] is not None
        assert possible['flush'] is None
        assert possible['straight_flush'] is None
    
    def test_possible_hands_flush(self):
        """Test possible hands for flush."""
        cards = [(12, 1), (10, 1), (8, 1), (5, 1), (2, 1)]
        scorer = Scorer(cards)
        possible = scorer.get_possible_hands()
        
        assert possible['flush'] is not None
        assert possible['straight'] is None
        assert possible['straight_flush'] is None
    
    def test_possible_hands_straight_flush(self):
        """Test possible hands for straight flush."""
        cards = [(8, 1), (9, 1), (10, 1), (11, 1), (12, 1)]
        scorer = Scorer(cards)
        possible = scorer.get_possible_hands()
        
        assert possible['straight'] is not None
        assert possible['flush'] is not None
        assert possible['straight_flush'] is not None
        assert possible['royal_flush'] is None  # Not 10-J-Q-K-A
    
    def test_possible_hands_royal_flush(self):
        """Test possible hands for royal flush."""
        cards = [(8, 1), (9, 1), (10, 1), (11, 1), (12, 1)]
        scorer = Scorer(cards)
        possible = scorer.get_possible_hands()
        
        assert possible['straight'] is not None
        assert possible['flush'] is not None
        assert possible['straight_flush'] is not None
        assert possible['royal_flush'] is not None
    
    def test_get_best_hand_hierarchy(self):
        """Test that get_best_hand returns the highest ranking hand."""
        # Royal flush
        cards = [(8, 1), (9, 1), (10, 1), (11, 1), (12, 1)]
        scorer = Scorer(cards)
        hand_name, hand_cards = scorer.get_best_hand()
        assert hand_name == 'royal_flush'
        
        # Four of a kind
        cards = [(12, 0), (12, 1), (12, 2), (12, 3), (8, 0)]
        scorer = Scorer(cards)
        hand_name, hand_cards = scorer.get_best_hand()
        assert hand_name == 'four_of_a_kind'
        
        # Pair
        cards = [(12, 0), (12, 1), (8, 2), (5, 3), (2, 0)]
        scorer = Scorer(cards)
        hand_name, hand_cards = scorer.get_best_hand()
        assert hand_name == 'pair'
    
    def test_score_royal_flush(self):
        """Test scoring for royal flush."""
        cards = [(8, 1), (9, 1), (10, 1), (11, 1), (12, 1)]
        scorer = Scorer(cards)
        score = scorer.score()
        assert score == 90000
    
    def test_score_straight_flush(self):
        """Test scoring for straight flush."""
        # Regular straight flush
        cards = [(5, 1), (6, 1), (7, 1), (8, 1), (9, 1)]
        scorer = Scorer(cards)
        score = scorer.score()
        assert score == 80009  # 80000 + 9 (high card)
        
        # Wheel straight flush
        cards = [(12, 1), (0, 1), (1, 1), (2, 1), (3, 1)]
        scorer = Scorer(cards)
        score = scorer.score()
        assert score == 80003  # Special wheel scoring
    
    def test_score_four_of_a_kind(self):
        """Test scoring for four of a kind."""
        cards = [(10, 0), (10, 1), (10, 2), (10, 3), (5, 0)]
        scorer = Scorer(cards)
        score = scorer.score()
        assert score == 70010  # 70000 + 10 (quad rank)
    
    def test_score_full_house(self):
        """Test scoring for full house."""
        cards = [(10, 0), (10, 1), (10, 2), (5, 3), (5, 0)]
        scorer = Scorer(cards)
        score = scorer.score()
        assert score == 61005  # 60000 + (10 * 100) + 5
    
    def test_score_flush(self):
        """Test scoring for flush."""
        cards = [(12, 1), (10, 1), (8, 1), (5, 1), (2, 1)]
        scorer = Scorer(cards)
        score = scorer.score()
        assert score == 50012  # 50000 + 12 (high card)
    
    def test_score_straight(self):
        """Test scoring for straight."""
        # Regular straight
        cards = [(8, 0), (9, 1), (10, 2), (11, 3), (12, 0)]
        scorer = Scorer(cards)
        score = scorer.score()
        assert score == 40012  # 40000 + 12 (high card)
        
        # Wheel straight
        cards = [(12, 0), (0, 1), (1, 2), (2, 3), (3, 0)]
        scorer = Scorer(cards)
        score = scorer.score()
        assert score == 40003  # Special wheel scoring
    
    def test_score_three_of_a_kind(self):
        """Test scoring for three of a kind."""
        cards = [(10, 0), (10, 1), (10, 2), (8, 3), (5, 0)]
        scorer = Scorer(cards)
        score = scorer.score()
        assert score == 30010  # 30000 + 10 (trips rank)
    
    def test_score_two_pair(self):
        """Test scoring for two pair."""
        cards = [(12, 0), (12, 1), (8, 2), (8, 3), (5, 0)]
        scorer = Scorer(cards)
        score = scorer.score()
        assert score == 21208  # 20000 + (12 * 100) + 8
    
    def test_score_pair(self):
        """Test scoring for pair."""
        cards = [(12, 0), (12, 1), (8, 2), (5, 3), (2, 0)]
        scorer = Scorer(cards)
        score = scorer.score()
        assert score == 10012  # 10000 + 12 (pair rank)
    
    def test_score_high_card(self):
        """Test scoring for high card."""
        cards = [(12, 0), (10, 1), (8, 2), (5, 3), (2, 0)]
        scorer = Scorer(cards)
        score = scorer.score()
        assert score == 12  # Just the high card rank
    
    def test_seven_card_hand(self):
        """Test that the scorer works with more than 5 cards (like Texas Hold'em)."""
        # 7 cards with a flush possible
        cards = [(12, 1), (11, 1), (10, 1), (9, 1), (8, 1), (5, 0), (2, 3)]
        scorer = Scorer(cards)
        hand_name, hand_cards = scorer.get_best_hand()
        
        assert hand_name == 'royal_flush'
        assert len(hand_cards) == 5
        # Verify it's the royal flush cards
        ranks = sorted([card[0] for card in hand_cards])
        assert ranks == [8, 9, 10, 11, 12]
    
    def test_edge_case_empty_hand(self):
        """Test edge case with empty hand."""
        scorer = Scorer([])
        stats = scorer.analyze_hand()
        assert stats['max_same_rank'] == 1
        assert stats['high_card'] == 0
    
    def test_edge_case_single_card(self):
        """Test edge case with single card."""
        cards = [(12, 0)]
        scorer = Scorer(cards)
        hand_name, hand_cards = scorer.get_best_hand()
        assert hand_name == 'high_card'
        assert len(hand_cards) == 1
        assert hand_cards[0] == (12, 0)