from collections import Counter

from src.poker.card import Card
from src.poker.deck import Deck
from src.tests.test_utils.test_utils import PokerTestCase


class TestDeck(PokerTestCase):

    def test_init(self):
        deck = Deck()
        self.assertEqual(52, len(deck.cards))

    def test_refill(self):
        deck = Deck()
        deck.cards = []

        deck.refill()

        suit_counts = Counter([card.suit_value for card in deck.cards])
        rank_counts = Counter([card.rank_value for card in deck.cards])
        for count in suit_counts.values():
            self.assertEqual(13, count)
        for count in rank_counts.values():
            self.assertEqual(4, count)
        self.assertEqual(52, len(deck.cards))
        self.assertEqual(52, len(set(deck.cards)))

    def test_shuffle(self):
        deck = Deck()
        cards_before = deck.cards.copy()

        deck.shuffle()
        cards_after = deck.cards.copy()

        differences = 0
        for c_before, c_after in zip(cards_before, cards_after):
            if c_before != c_after:
                differences += 1
        self.assertGreater(differences, 0)

    def test_burn(self):
        deck = Deck()

        deck.burn()

        self.assertEqual(51, len(deck.cards))

    def test_str(self):
        deck = Deck()
        deck.cards = [Card(5, 'H'), Card(13, 'D'), Card(8, 'S')]

        self.assertEqualStripColor('[5 ♥] [K ♦] [8 ♠]', str(deck))
