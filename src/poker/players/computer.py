import random

from src.poker.enums.betting_move import BettingMove
from src.poker.enums.computer_playing_style import ComputerPlayingStyle
from src.poker.players.player import Player


class Computer(Player):
    """A computer player.

    Args:
        name: The name of the player
        playing_style: An enum which determines how computer will make its next move
    """

    def __init__(self, name: str, playing_style: ComputerPlayingStyle):
        super().__init__(name)
        self.playing_style = playing_style

    def choose_next_move(self, table_raise_amount: int, times_table_raised: int, last_table_bet: int) -> BettingMove:
        """Allows human player to choose their next move (call, raise, fold, etc.).

        Returns:
            player's choice for their next move
        """
        if self.playing_style is ComputerPlayingStyle.SAFE:
            return self.safe_play(table_raise_amount, times_table_raised, last_table_bet)
        elif self.playing_style is ComputerPlayingStyle.RISKY:
            return self.risky_play(table_raise_amount, times_table_raised, last_table_bet)
        else:
            return self.random_play(table_raise_amount, times_table_raised, last_table_bet)

    def risky_play(self, table_raise_amount: int, num_times_table_raised: int, table_last_bet: int) -> BettingMove:
        """Computer choice to check, call, raise, bet, fold, or go all-in. Player more likely to bet and raise."""
        x = random.random()
        # If player doesn't have enough chips to raise or just enough chips to raise
        if self.chips <= abs(self.bet - table_raise_amount):
            # If not enough chips to call
            if self.chips <= abs(self.bet - table_last_bet):
                if x <= .90:
                    return BettingMove.ALL_IN
                else:
                    return BettingMove.FOLDED
            else:
                if x <= .40:
                    if self.bet == table_last_bet:
                        return BettingMove.CHECKED
                    else:
                        return BettingMove.CALLED
                elif x <= .90:
                    return BettingMove.ALL_IN
                else:
                    return BettingMove.FOLDED
        elif num_times_table_raised < 4:
            if self.bet == table_last_bet:
                if x <= .40:
                    return BettingMove.CHECKED
                elif x <= .90:
                    return BettingMove.BET
                else:
                    return BettingMove.FOLDED
            else:
                if x <= .40:
                    return BettingMove.CALLED
                elif x <= .90:
                    return BettingMove.RAISED
                else:
                    return BettingMove.FOLDED
        # If there have been 4 bets/raises in current round
        else:
            if x <= .90:
                return BettingMove.CALLED
            else:
                return BettingMove.FOLDED

    def safe_play(self, table_raise_amount: int, num_times_table_raised: int, table_last_bet: int) -> BettingMove:
        """Computer choice to check, call, raise, bet, fold, or go all-in. Player less likely to bet and raise."""
        x = random.random()
        # If player doesn't have enough chips to raise or just enough chips to raise
        if self.chips <= abs(self.bet - table_raise_amount):
            # If not enough chips to call
            if self.chips <= abs(self.bet - table_last_bet):
                if x <= .60:
                    return BettingMove.ALL_IN
                else:
                    return BettingMove.FOLDED
            else:
                if x <= .60:
                    if self.bet == table_last_bet:
                        return BettingMove.CHECKED
                    else:
                        return BettingMove.CALLED
                elif x <= .80:
                    return BettingMove.ALL_IN
                else:
                    return BettingMove.FOLDED
        elif num_times_table_raised < 4:
            if self.bet == table_last_bet:
                if x <= .70:
                    return BettingMove.CHECKED
                elif x <= .90:
                    return BettingMove.BET
                else:
                    return BettingMove.FOLDED
            else:
                if x <= .70:
                    return BettingMove.CALLED
                elif x <= .90:
                    return BettingMove.RAISED
                else:
                    return BettingMove.FOLDED
        # If there have been 4 bets/raises in current round
        else:
            if x <= .90:
                return BettingMove.CALLED
            else:
                return BettingMove.FOLDED

    def random_play(self, table_raise_amount: int, num_times_table_raised: int, table_last_bet: int) -> BettingMove:
        """Computer choice to check, call, raise, bet, fold, or go all-in at random."""
        x = random.random()
        # If player doesn't have enough chips to raise or just enough chips to raise
        if self.chips <= abs(self.bet - table_raise_amount):
            # If not enough chips to call
            if self.chips <= abs(self.bet - table_last_bet):
                if x <= .50:
                    return BettingMove.ALL_IN
                else:
                    return BettingMove.FOLDED
            else:
                if x <= .30:
                    if self.bet == table_last_bet:
                        return BettingMove.CHECKED
                    else:
                        return BettingMove.CALLED
                elif x <= .66:
                    return BettingMove.ALL_IN
                else:
                    return BettingMove.FOLDED
        elif num_times_table_raised < 4:
            if self.bet == table_last_bet:
                if x <= .33:
                    return BettingMove.CHECKED
                elif x <= .66:
                    return BettingMove.BET
                else:
                    return BettingMove.FOLDED
            else:
                if x <= .33:
                    return BettingMove.CALLED
                elif x <= .66:
                    return BettingMove.RAISED
                else:
                    return BettingMove.FOLDED
        # If there have been 4 bets/raises in current round
        else:
            if x <= .66:
                return BettingMove.CALLED
            else:
                return BettingMove.FOLDED
