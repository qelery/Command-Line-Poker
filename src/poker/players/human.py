from src.poker.enums.betting_move import BettingMove
from src.poker.players.player import Player
from src.poker.utils import io_utils


class Human(Player):
    """A human player.

    Args:
        name: The name of the player
    """

    def __init__(self, name: str):
        super().__init__(name)

    def choose_next_move(self, table_raise_amount: int, times_table_raised: int, last_table_bet: int) -> BettingMove:
        """Allows human player to choose their next move (call, raise, fold, etc.).

        Returns:
            player's choice for their next move
        """
        choice = ''
        # If player doesn't have enough chips to raise or if player has just enough chips to raise
        if self.chips <= abs(self.bet - table_raise_amount):
            valid_moves = ['f', 'a']
            # If not enough chips to call
            if self.chips <= abs(self.bet - last_table_bet):
                prompt = f" >>> Press (a) to go all-in or (f) to fold.   "
            else:
                valid_moves = ['c', 'a', 'f']
                prompt = f" >>> Press (c) to call {last_table_bet}, (a) to go all-in, or (f) to fold.   "
        elif times_table_raised < 4:
            if self.bet == last_table_bet:
                valid_moves = ['c', 'b', 'f']
                prompt = f" >>> Press (c) to check, (b) to bet {table_raise_amount} chips, or (f) to fold.   "
            else:
                valid_moves = ['c', 'r', 'f']
                prompt = f" >>> Press (c) to call {last_table_bet} chips, (r) to raise to {table_raise_amount} chips," \
                         f" or (f) to fold.   "
        # If there have been 4 bets/raises in current round
        else:
            valid_moves = ['c', 'f']
            prompt = f" >>> Press (c) to call {last_table_bet} chips or (f) to fold.   "
        while choice.lower() not in valid_moves:
            choice = io_utils.input_no_return(prompt)
        # Return player's choice
        choice = choice.lower()
        if 'b' == choice:
            return BettingMove.BET
        if 'r' == choice:
            return BettingMove.RAISED
        elif 'f' == choice:
            return BettingMove.FOLDED
        elif 'a' == choice:
            return BettingMove.ALL_IN
        elif self.bet == last_table_bet:
            return BettingMove.CHECKED
        else:
            return BettingMove.CALLED
