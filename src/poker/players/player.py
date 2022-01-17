from __future__ import annotations

from abc import ABC, abstractmethod

from src.poker.card import Card
from src.poker.enums.betting_move import BettingMove


class Player(ABC):
    """Abstract class representing a poker player.

    Args:
        name: The name of the player
    """

    def __init__(self, name: str):
        self.name = name
        self.chips = 0
        self.bet = 0
        self.hand: list[Card] = []
        self.is_dealer = False
        self.is_BB = False
        self.is_SB = False
        self.is_folded = False
        self.is_locked = False
        self.is_all_in = False
        self.is_in_game = True
        self.best_hand_cards: list[Card] = []
        self.best_hand_score = 0
        self.best_hand_rank = ''
        self.rank_subtype = ''
        self.kicker_card: Card | None = None

    def reset(self):
        """Reset player's state in between hands."""
        self.bet = 0
        self.hand = []
        self.is_dealer = False
        self.is_BB = False
        self.is_SB = False
        self.is_folded = False
        self.is_all_in = False
        self.is_locked = False
        self.best_hand_cards = []
        self.best_hand_score = 0
        self.best_hand_rank = ''
        self.rank_subtype = ''
        self.kicker_card = None

    def match_bet(self, amount: int) -> int:
        if amount < self.bet:
            raise ValueError(f'Player {self.name} made an illegal bet. '
                             f'Cannot match lesser bet of {amount} '
                             f'since player has already bet {self.bet}.')
        n = abs(self.bet - amount)
        self.chips -= n
        self.bet += n
        if self.chips < 0:
            raise ValueError(f'Player {self.name} made an illegal bet. '
                             f'Player left with {self.chips} chips.')
        return self.bet

    def go_all_in(self) -> None:
        self.bet += self.chips
        self.chips = 0
        self.is_all_in = True

    def fold(self) -> None:
        self.is_folded = True

    @abstractmethod
    def choose_next_move(self, table_raise_amount, num_times_table_raised, table_last_bet) -> BettingMove:
        pass
