from unittest.mock import Mock

from src.poker.card import Card
from src.poker.table import Table
from src.tests.test_utils.test_utils import PokerTestCase


class TestTableReset(PokerTestCase):

    def test_reset(self):
        active_players = []
        table = Table()
        table.big_blind = 50
        table.community = [Card(3, 'D'), Card(9, 'H')]
        table.pots = [[300, active_players]]
        table.pot_transfers = [300, 400]
        table.last_bet = 100
        table.num_times_raised = 1

        table.reset(active_players)

        self.assertEqual([], table.community)
        self.assertListEqual([[0, active_players]], table.pots)
        self.assertEqual([], table.pot_transfers)
        self.assertEqual(0, table.last_bet)
        self.assertEqual(0, table.num_times_raised)
        self.assertEqual(table.big_blind, table.raise_amount)

    def test_reset_increases_big_blind(self):
        table = Table()
        table.big_blind = 50
        table.check_increase_big_blind = Mock(return_value=True)

        table.reset(active_players=[])

        self.assertEqual(100, table.big_blind)
        self.assertEqual(table.big_blind, table.raise_amount)

    def test_reset_does_not_increase_big_blind(self):
        table = Table()
        table.big_blind = 50
        table.check_increase_big_blind = Mock(return_value=False)

        table.reset(active_players=[])

        self.assertEqual(50, table.big_blind)
        self.assertEqual(table.big_blind, table.raise_amount)


class TestTableCheckIncreaseBigBlind(PokerTestCase):

    def test_check_increase_big_blind_returns_true(self):
        Table.increase_blind_hand_increments = 5
        table = Table()

        table.hands_played = 5
        self.assertTrue(table.check_increase_big_blind())

        table.hands_played = 15
        self.assertTrue(table.check_increase_big_blind())

    def test_check_increase_big_blind_returns_false(self):
        Table.increase_blind_hand_increments = 5
        table = Table()

        table.hands_played = 0
        self.assertFalse(table.check_increase_big_blind())

        table.hands_played = 4
        self.assertFalse(table.check_increase_big_blind())

        table.hands_played = 11
        self.assertFalse(table.check_increase_big_blind())