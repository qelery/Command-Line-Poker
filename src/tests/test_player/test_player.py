from src.poker.card import Card
from src.poker.players.player import Player
from src.tests.test_utils.test_utils import PokerTestCase


class MockConcretePlayerClass(Player):
    def __init__(self, name):
        super().__init__(name)

    def choose_next_move(self, table_raise_amount, num_times_table_raised, table_last_bet):
        pass


class TestPlayer(PokerTestCase):
    def test_init(self):
        name = 'John'

        player = MockConcretePlayerClass(name)

        self.assertEqual(name, player.name)

    def test_reset(self):
        card = Card(2, 'H')
        name = 'John'
        chips = 5000

        player = MockConcretePlayerClass(name)
        player.chips = 5000

        player.is_dealer = True
        player.is_BB = True
        player.is_SB = True
        player.is_folded = True
        player.is_all_in = True
        player.is_locked = True
        player.bet = 300
        player.hand = [card]
        player.best_hand_cards = [card]
        player.best_hand_score = 1000
        player.best_hand_rank = 'best hand rank'
        player.rank_subtype = 'rank subtype'
        player.kicker_card = card

        player.reset()

        # These properties should change when a player is reset
        self.assertFalse(player.is_dealer)
        self.assertFalse(player.is_BB)
        self.assertFalse(player.is_SB)
        self.assertFalse(player.is_folded)
        self.assertFalse(player.is_all_in)
        self.assertFalse(player.is_locked)
        self.assertEqual(0, player.bet)
        self.assertListEqual([], player.hand)
        self.assertEqual([], player.best_hand_cards)
        self.assertEqual(0, player.best_hand_score)
        self.assertEqual('', player.best_hand_rank)
        self.assertEqual('', player.rank_subtype)
        self.assertIsNone(player.kicker_card)
        # These properties should not change when a player is reset
        self.assertEqual(name, player.name)
        self.assertEqual(chips, player.chips)

    def test_go_all_in(self):
        player = MockConcretePlayerClass('John')
        player.chips = 30
        player.bet = 250

        player.go_all_in()

        self.assertEqual(0, player.chips)
        self.assertEqual(280, player.bet)
        self.assertTrue(player.is_all_in)

    def test_fold(self):
        player = MockConcretePlayerClass('John')

        player.fold()

        self.assertTrue(player.is_folded)


class TestPlayerMatchBet(PokerTestCase):

    def test_match_bet(self):
        player = MockConcretePlayerClass('John')
        player.chips = 1000
        player.bet = 250

        player.match_bet(300)

        self.assertEqual(300, player.bet)
        self.assertEqual(950, player.chips)

    def test_value_error_when_player_left_with_negative_chips(self):
        player = MockConcretePlayerClass('John')
        player.chips = 5
        player.bet = 90

        with self.assertRaises(ValueError):
            player.match_bet(100)

    def test_value_error_when_amount_to_match_less_than_players_current_bet(self):
        player = MockConcretePlayerClass('John')
        player.chips = 100000
        player.bet = 500

        with self.assertRaises(ValueError):
            player.match_bet(250)
