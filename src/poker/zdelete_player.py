import time

from src.poker.card import Card

import random

from src.poker.enums.betting_move import BettingMove
from src.poker.enums.computer_playing_style import ComputerPlayingStyle
from src.poker.prompts import text_prompt
from src.poker.utils import io_utils


class Player:
    """Class representing a player.

    Args:
        name (str): player's name
        playing_style (function) = determines how the player will decide what move to execute
        table: a Table object
    """

    def __init__(self, name, is_human: bool, playing_style: ComputerPlayingStyle = None):
        self.name = name
        self.is_human = is_human
        self.playing_style = playing_style
        self.chips = 0
        self.bet = 0
        self.hand: list[Card] = []
        self.is_dealer = False
        self.is_BB = False
        self.is_SB = False
        self.is_folded = False
        self.is_first_act = False
        self.is_locked = False
        self.is_all_in = False
        self.is_in_game = True
        self.best_hand_cards = None
        self.best_hand_score = 0
        self.best_hand_rank = ''
        self.rank_subtype = ''
        self.kicker_card = None

    def reset(self):
        """Reset player's state in between hands."""
        self.bet = 0
        self.hand = []
        self.is_folded = False
        self.is_all_in = False
        self.is_first_act = False
        self.is_locked = False
        self.best_hand_cards = None
        self.best_hand_score = 0
        self.best_hand_rank = ''
        self.rank_subtype = ''
        self.kicker_card = None

    def match_bet(self, amount: int) -> int:
        n = abs(self.bet - amount)
        self.chips -= n
        self.bet += n
        return self.bet

    def go_all_in(self) -> None:
        self.bet += self.chips
        self.chips = 0
        self.is_all_in = True

    def fold(self) -> None:
        self.is_folded = True

    def make_move(self, table_raise_amount, num_times_table_raised, table_last_bet) -> BettingMove:
        """Allow player to choose either to call, check, fold, etc. with specific playing style."""
        if self.is_human:
            return self.get_next_move(table_raise_amount, num_times_table_raised, table_last_bet)
        else:
            if self.playing_style is ComputerPlayingStyle.SAFE:
                move = self.safe_play(table_raise_amount, num_times_table_raised, table_last_bet)
                print("COMPUTER SAFE")
                print(move)
                time.sleep(2)
                return move
            elif self.playing_style is ComputerPlayingStyle.RISKY:
                move = self.risky_play(table_raise_amount, num_times_table_raised, table_last_bet)
                print("COMPUTER RISKY")
                print(move)
                time.sleep(2)
                return move
            else:
                move = self.random_play(table_raise_amount, num_times_table_raised, table_last_bet)
                print("COMPUTER RANDOM")
                print(move)
                time.sleep(2)
                return move
    def player_moves(self, player, move=''):
        """Gets player's choice of move (call, raise, fold, etc) and execute it

        Args:
            player (__main__.Player): player making the move
        """
        if move == '':
            if player.playing_style != human_play:
                text_prompt.show_thinking(player.name, self.short_pause)
            move = player.choose_next_move()
        if move == 'checked' or move == 'called':
            self.make_bet(player, self.table.last_bet)
            text_prompt.show_player_move(player, move, self.pause, player.bet)
        elif move == 'raised' or move == 'bet':
            self.table.num_times_raised += 1
            self.make_bet(player, self.table.raise_amount)
            for active_player in self.active_players:
                if not active_player.is_folded:
                    active_player.is_locked = False
            for person in self.active_players:
                if person.is_all_in:
                    person.is_locked = True
            text_prompt.show_player_move(player, move, self.pause, player.bet)
        elif move == 'all-in':
            player.bet += player.chips
            player.chips = 0
            # If the player's bet enough to raise (even if not in the proper increment)
            if self.table.last_bet < player.bet <= self.table.raise_amount:
                for active_player in self.active_players:
                    if not active_player.is_folded and not active_player.is_all_in:
                        active_player.is_locked = False
            self.table.pot_transfers.append(player.bet)
            # Prevent multiple side pots being created if players go all-in at same amount in same phase
            self.table.pot_transfers = list(set(self.table.pot_transfers))
            if player.bet > self.table.last_bet:
                self.table.last_bet = player.bet
            player.is_all_in = True
            text_prompt.show_player_move(player, move, self.pause)
        elif move == 'folded':
            player.is_folded = True
            text_prompt.show_player_move(player, move, self.pause)
            if player.is_human:
                # Speed up the hand
                self.pause = 1.25
                self.long_pause = 3.0
                self.short_pause = 0.5

    def get_next_move(self, table_raise_amount: int, num_times_table_raised: int, table_last_bet: int) -> BettingMove:
        """Allows human player to choose their next move (call, raise, fold, etc.).

        Returns:
            player's choice as string
        """
        choice = ''
        # If player doesn't have enough chips to raise or if player has just enough chips to raise
        if self.chips <= abs(self.bet - table_raise_amount):
            valid_moves = ['f',  'a']
            # If not enough chips to call
            if self.chips <= abs(self.bet - table_last_bet):
                prompt = f" >>> Press (a) to go all-in or (f) to fold.   "
            else:
                valid_moves = ['c', 'a', 'f']
                prompt = f" >>> Press (c) to call {table_last_bet}, (a) to go all-in, or (f) to fold.   "
        elif num_times_table_raised < 4:
            if self.bet == table_last_bet:
                valid_moves = ['c', 'b', 'f']
                prompt = f" >>> Press (c) to check, (b) to bet {table_raise_amount} chips, or (f) to fold.   "
            else:
                valid_moves = ['c', 'r', 'f']
                prompt = f" >>> Press (c) to call {table_last_bet} chips, (r) to raise to {table_raise_amount} chips, or (f) to fold.   "
        # If there have been 4 bets/raises in current round
        else:
            valid_moves = ['c', 'f']
            prompt = f" >>> Press (c) to call {table_last_bet} chips or (f) to fold.   "
        while choice.lower() not in valid_moves:
            choice = io_utils.input_no_return(prompt)
        # Return player's choice'
        choice = choice.lower()
        if 'b' == choice:
            return BettingMove.BET
        if 'r' == choice:
            return BettingMove.RAISED
        elif 'f' == choice:
            return BettingMove.FOLDED
        elif 'a' == choice:
            return BettingMove.ALL_IN
        elif self.bet == table_last_bet:
            return BettingMove.CHECKED
        else:
            return BettingMove.CALLED

    def human_play(self, table_raise_amount: int, num_times_table_raised: int, table_last_bet: int) -> BettingMove:
        """Allow human player to choose either to call, raise, fold, etc.

        Returns:
            player's choice as string
        """
        choice = ''
        # If player doesn't have enough chips to raise or if player has just enough chips to raise
        if self.chips <= abs(self.bet - table_raise_amount):
            valid_moves = ['f', '(f)', 'fold', 'folded', 'a', '(a)', 'all', 'all in', 'all-in']
            # If not enough chips to call
            if self.chips <= abs(self.bet - table_last_bet):
                prompt = f" >>> Press (a) to go all-in or (f) to fold.   "
            else:
                valid_moves.extend(['c', '(c)', 'call', 'called'])
                prompt = f" >>> Press (c) to call {table_last_bet}, (a) to go all-in, or (f) to fold.   "
        elif num_times_table_raised < 4:
            valid_moves = ['c', '(c)', 'f', '(f)', 'fold', 'folded']
            if self.bet == table_last_bet:
                valid_moves.extend(['b', '(b)', 'bet', 'check', 'checked'])
                prompt = f" >>> Press (c) to check, (b) to bet {table_raise_amount} chips, or (f) to fold.   "
            else:
                valid_moves.extend(['r', '(r)', 'raise', 'raised', 'call', 'called'])
                prompt = f" >>> Press (c) to call {table_last_bet} chips, (r) to raise to {table_raise_amount} chips, or (f) to fold.   "
        # If there have been 4 bets/raises in current round
        else:
            valid_moves = ['c', '(c)', 'call', 'called', 'f', '(f)', 'fold', 'folded']
            prompt = f" >>> Press (c) to call {table_last_bet} chips or (f) to fold.   "
        while choice.lower() not in valid_moves:
            choice = io_utils.input_no_return(prompt)
        # Return player's choice'
        choice = choice.lower()
        if 'b' in choice:
            return BettingMove.BET
        if 'r' in choice:
            return BettingMove.RAISED
        elif 'f' in choice:
            return BettingMove.FOLDED
        elif 'a' in choice:
            return BettingMove.ALL_IN
        elif self.bet == table_last_bet:
            return BettingMove.CHECKED
        else:
            return BettingMove.CALLED

    def risky_play(self, table_raise_amount: int, num_times_table_raised: int, table_last_bet: int) -> BettingMove:
        """Computer player choice to check, call, raise, bet, fold, or go all-in. Player more likely to bet and raise."""
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
        """Computer player choice to check, call, raise, bet, fold, or go all-in. Player less likely to bet and raise."""
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
        """Computer player choice to check, call, raise, bet, fold, or go all-in at random."""
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
