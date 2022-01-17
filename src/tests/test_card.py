from src.poker.card import Card
from src.tests.test_utils.test_utils import PokerTestCase


class TestCard(PokerTestCase):
    def test_init(self):
        card = Card(2, 'C')
        self.assertEqual(2, card.rank_value)
        self.assertEqualStripColor('C', card.suit_value)
        self.assertEqualStripColor('2', card.rank_symbol)
        self.assertEqualStripColor('♣', card.suit_symbol)

        card = Card(11, 'D')
        self.assertEqual(11, card.rank_value)
        self.assertEqualStripColor('D', card.suit_value)
        self.assertEqualStripColor('J', card.rank_symbol)
        self.assertEqualStripColor('♦', card.suit_symbol)

        card = Card(12, 'H')
        self.assertEqual(12, card.rank_value)
        self.assertEqualStripColor('H', card.suit_value)
        self.assertEqualStripColor('Q', card.rank_symbol)
        self.assertEqualStripColor('♥', card.suit_symbol)

        card = Card(14, 'S')
        self.assertEqual(14, card.rank_value)
        self.assertEqualStripColor('S', card.suit_value)
        self.assertEqualStripColor('A', card.rank_symbol)
        self.assertEqualStripColor('♠', card.suit_symbol)

    def test_str(self):
        card = Card(8, 'C')
        self.assertEqualStripColor(f'[8 ♣]', str(card))

        card = Card(10, 'D')
        self.assertEqualStripColor('[10♦]', str(card))

        card = Card(13, 'H')
        self.assertEqualStripColor('[K ♥]', str(card))

        card = Card(14, 'S')
        self.assertEqualStripColor('[A ♠]', str(card))

    def test_eq(self):
        card = Card(5, 'H')
        self.assertEqual(card, card)

        card_a = Card(5, 'H')
        card_b = Card(5, 'H')
        self.assertEqual(card_a, card_b)

        card_a = Card(2, 'H')
        card_b = Card(8, 'H')
        self.assertNotEqual(card_a, card_b)

        card_a = Card(7, 'H')
        card_b = Card(7, 'S')
        self.assertNotEqual(card_a, card_b)

        card_a = Card(2, 'D')
        card_b = Card(9, 'C')
        self.assertNotEqual(card_a, card_b)
