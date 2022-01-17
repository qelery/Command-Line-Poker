from __future__ import annotations

import random

from src.poker.enums.betting_move import BettingMove
from src.poker.enums.computer_playing_style import ComputerPlayingStyle
from src.poker.enums.phase import Phase
from src.poker.deck import Deck
from src.poker.players.computer import Computer
from src.poker.players.human import Human
from src.poker.players.player import Player
from src.poker.table import Table
from src.poker.prompts import text_prompt
from src.poker.utils import io_utils
from src.poker.utils import hand_ranking_utils



class Game:
    """Control center of the game."""

    def __init__(self):
        self.phase = Phase.PREFLOP
        self.deck = Deck()
        self.players = []
        self.dealer = None
        self.table = Table()
        self.short_pause = 0
        self.pause = 0
        self.long_pause = 0
        # self.short_pause = 0.5
        # self.pause = 1.25
        # self.long_pause = 3.0
        self.setup()

    def play(self) -> None:
        """Runs the main loop of the game."""
        while True:
            self.reset_for_next_round()
            for phase in Phase:
                self.phase = phase
                self.deal_cards()
                self.run_round_of_betting()
                if self.check_hand_over():
                    break
            self.determine_winners()
            self.table.hands_played += 1
            if self.check_game_over():
                break

    def setup(self) -> None:
        """Sets up the game before any rounds are run."""
        player_name = text_prompt.prompt_for_name()
        num_computer_players = text_prompt.prompt_for_number_computer_players()
        starting_chips = text_prompt.prompt_for_starting_chips()
        self.create_players(player_name, num_computer_players, starting_chips)

        max_blind = int(starting_chips / 10)
        min_blind = int(starting_chips / 50)
        self.table.big_blind = text_prompt.prompt_for_big_blind(min_blind, max_blind)

    def create_players(self, player_name, num_computer, starting_chips) -> None:
        # human = Player(player_name, is_human=True)
        human = Human(player_name)
        self.players.append(human)
        names = ['Homer', 'Bart', 'Lisa', 'Marge', 'Milhouse', 'Moe', 'Maggie', 'Nelson', 'Ralph']
        computer_names = [n for n in names if n != human.name]
        random.shuffle(computer_names)
        for _ in range(num_computer):
            playing_style = random.choice(list(ComputerPlayingStyle))
            # computer = ComputerPlayer(computer_names.pop(), is_human=False, playing_style=playing_style)
            computer = Computer(computer_names.pop(), playing_style)
            self.players.append(computer)
        for player in self.players:
            player.chips = starting_chips

    def reset_for_next_round(self) -> None:
        """Gets players, table, and deck ready to play another hand."""
        active_players = self.get_active_players()
        # if any(player.is_human for player in active_players):
        if any(isinstance(player, Human) for player in active_players):
            self.set_game_speed(is_fast=False)
        else:
            self.set_game_speed(is_fast=True)
        self.reset_players()
        self.reset_table()
        self.reset_deck()

    def reset_players(self) -> None:
        for player in self.players:
            player.reset()
        self.assign_positions()

    def reset_table(self) -> None:
        active_players = self.get_active_players()
        self.table.reset(active_players)
        if self.table.check_increase_big_blind():
            text_prompt.clear_screen()
            text_prompt.show_table(self.players, self.table, 0)
            text_prompt.show_blind_increase(self.table.big_blind, self.long_pause)

    def reset_deck(self) -> None:
        self.deck.refill()
        self.deck.shuffle()
        text_prompt.clear_screen()
        text_prompt.show_shuffling(self.pause)

    def set_game_speed(self, is_fast: bool) -> None:
        pass # for now
        # if is_fast:
        #     self.pause = 1.25
        #     self.long_pause = 3.0
        #     self.short_pause = 0.5
        # else:
        #     self.pause = 2.75
        #     self.long_pause = 5.0
        #     self.short_pause = 0.75

    def assign_positions(self) -> None:
        """Assigns the position of the players.

        Definitions:
            first act = the player who bets first
            dealer = the player who will bet last
            small blind = the player to the left of the dealer
            big blind = the player to the left of the small blind
        """
        for player in self.get_active_players():
            player.is_SB = False
            player.is_BB = False
        if self.table.hands_played == 0:
            self.determine_positions_randomly()
        else:
            self.shift_positions_left()

    def determine_positions_randomly(self) -> None:
        active_players = self.get_active_players()
        dealer_index = random.randrange(0, len(active_players))
        active_players[dealer_index].is_dealer = True
        self.dealer = active_players[dealer_index]
        # In 2 player poker, the dealer is SB and acts first pre-flop
        if len(active_players) == 2:
            active_players[dealer_index].is_SB = True
            active_players[(dealer_index + 1) % len(active_players)].is_BB = True
        else:
            active_players[(dealer_index + 2) % len(active_players)].is_BB = True
            active_players[(dealer_index + 1) % len(active_players)].is_SB = True

    def shift_positions_left(self) -> None:
        active_players = self.get_active_players()
        old_dealer_index = [player is self.dealer for player in self.players].index(True)
        while True:
            old_dealer_index += 1
            player_to_left = self.players[old_dealer_index % len(self.players)]
            if player_to_left in active_players:
                self.dealer = player_to_left
                player_to_left.is_dealer = True
                new_dealer_index = next(i for i, player in enumerate(active_players) if player.is_dealer)
                # in 2 player poker, the dealer is SB and acts first pre-flop
                if len(active_players) == 2:
                    active_players[new_dealer_index].is_SB = True
                    active_players[(new_dealer_index + 1) % len(active_players)].is_BB = True
                else:
                    active_players[(new_dealer_index + 2) % len(active_players)].is_BB = True
                    active_players[(new_dealer_index + 1) % len(active_players)].is_SB = True
                break

    def deal_cards(self) -> None:
        """Deals cards to the hold and the community."""
        if self.phase is Phase.PREFLOP:
            text_prompt.show_table(self.players, self.table, 0)  ########################### Why is this pause 0?
            text_prompt.show_phase_change_alert(self.phase, self.dealer.name, self.pause)
            self.deal_hole()
        elif self.phase is Phase.FLOP:
            text_prompt.show_phase_change_alert(self.phase, self.dealer, self.pause)
            self.deal_community(3)
        else:
            text_prompt.show_phase_change_alert(self.phase, self.dealer, self.pause)
            self.deal_community(1)
        text_prompt.show_table(self.players, self.table, 0)

    def deal_hole(self) -> None:
        """Deals two cards to each player.

        In poker, you deal one card to each player at a time.
        """
        text_prompt.show_table(self.players, self.table, self.short_pause)
        text_prompt.show_dealing_hole(self.dealer.name, self.pause)
        for i in range(2):
            for player in self.get_active_players():
                card = self.deck.deal(1)
                player.hand.extend(card)

    def deal_community(self, n: int) -> None:
        """Deals cards to the community.

        In poker, a card is burned before dealing to the community.

        Args:
            n: The number of cards to deal to the community
        """
        self.deck.burn()
        cards = self.deck.deal(n)
        self.table.community.extend(cards)

    def run_round_of_betting(self):
        """Runs a round of betting."""
        self.table.num_times_raised = 0
        active_players = self.get_active_players()
        if self.phase is Phase.PREFLOP:
            self.run_small_blind_bet()
            self.run_big_blind_bet()
        first_act = self.get_index_first_act()
        # End round of betting when all but one player fold or when all unfolded players have locked in their bets
        self.bet_util_all_locked_in(first_act, active_players)
        for player in active_players:
            if not player.is_folded and not player.is_all_in:
                player.is_locked = False
        self.table.calculate_side_pots(active_players)
        text_prompt.show_table(self.players, self.table, 0)

    def run_small_blind_bet(self) -> None:
        player = next(player for player in self.players if player.is_SB)
        text_prompt.show_bet_blind(player.name, 'small', self.pause)
        wentAllIn = self.table.take_small_blind(player)
        if wentAllIn:
            text_prompt.show_player_move(player, 'all-in', self.pause)
        text_prompt.show_table(self.players, self.table, 0)

    def run_big_blind_bet(self) -> None:
        player = next(player for player in self.players if player.is_BB)
        text_prompt.show_bet_blind(player.name, 'big', self.pause)
        wentAllIn = self.table.take_big_blind(player)
        if wentAllIn:
            text_prompt.show_player_move(player, 'all-in', self.pause)
        text_prompt.show_table(self.players, self.table, 0)

    def get_index_first_act(self) -> int:
        """Determines the index of the first act.

        Returns:
            The index of the first act
        """
        active_players = self.get_active_players()
        if len(active_players) == 2:
            if active_players[0].is_dealer:
                return 0
            else:
                return 1
        if self.phase is Phase.PREFLOP:
            BB_index = next(i for i, player in enumerate(active_players) if player.is_BB)
            return (BB_index + 1) % len(active_players)
        else:
            dealer_index = next(i for i, player in enumerate(active_players) if player.is_dealer)
            return (dealer_index + 1) % len(active_players)

    def bet_util_all_locked_in(self, first_act: int, active_players: list[Player]) -> None:
        betting_index = first_act
        while True:
            if all(player.is_locked or player.is_all_in for player in active_players):
                break
            if [player.is_folded for player in active_players].count(False) == 1:
                break
            betting_player = active_players[betting_index % len(active_players)]
            if betting_player.is_folded or betting_player.is_all_in:
                betting_index += 1
                continue
            self.table.update_raise_amount(self.phase)
            # self.player_moves(betting_player)
            move = betting_player.choose_next_move(self.table.raise_amount, self.table.num_times_raised,
                                                   self.table.last_bet)
            self.table.take_bet(betting_player, move)
            if move is BettingMove.RAISED or move is BettingMove.BET:
                for active_player in active_players:
                    if not active_player.is_folded:
                        active_player.is_locked = False
                for person in active_players:
                    if person.is_all_in:
                        person.is_locked = True
            elif move is BettingMove.ALL_IN:
                # if self.table.last_bet < betting_player.bet <= self.table.raise_amount:
                #     for active_player in active_players:
                #         if not active_player.is_folded and not active_player.is_all_in:
                #             active_player.is_locked = False
                pass
            # if move is BettingMove.FOLDED and betting_player.is_human:
            if move is BettingMove.FOLDED and isinstance(betting_player, Human):
                self.set_game_speed(is_fast=True)
            betting_player.is_locked = True
            betting_index += 1
            text_prompt.show_table(self.players, self.table, 0)

    # def make_bet(self, player, bet_amount):
    #     """Player makes a bet.
    #
    #     Args:
    #         player (__main__.Player): player making the bet
    #         bet_amount (int): amount of the bet
    #     """
    #     n = abs(player.bet - bet_amount)
    #     player.chips -= n
    #     player.bet += n
    #     self.table.last_bet = player.bet

    # def player_moves(self, player, move=''):
    #     """Gets player's choice of move (call, raise, fold, etc) and execute it
    #
    #     Args:
    #         player (__main__.Player): player making the move
    #     """
    #     if move == '':
    #         if player.playing_style != human_play:
    #             text_prompt.show_thinking(player.name, self.short_pause)
    #         move = player.make_move()
    #     if move == 'checked' or move == 'called':
    #         self.make_bet(player, self.table.last_bet)
    #         text_prompt.show_player_move(player, move, self.pause, player.bet)
    #     elif move == 'raised' or move == 'bet':
    #         self.table.num_times_raised += 1
    #         self.make_bet(player, self.table.raise_amount)
    #         for active_player in self.active_players:
    #             if not active_player.is_folded:
    #                 active_player.is_locked = False
    #         for person in self.active_players:
    #             if person.is_all_in:
    #                 person.is_locked = True
    #         text_prompt.show_player_move(player, move, self.pause, player.bet)
    #     elif move == 'all-in':
    #         player.bet += player.chips
    #         player.chips = 0
    #         # If the player's bet enough to raise (even if not in the proper increment)
    #         if self.table.last_bet < player.bet <= self.table.raise_amount:
    #             for active_player in self.active_players:
    #                 if not active_player.is_folded and not active_player.is_all_in:
    #                     active_player.is_locked = False
    #         self.table.pot_transfers.append(player.bet)
    #         # Prevent multiple side pots being created if players go all-in at same amount in same phase
    #         self.table.pot_transfers = list(set(self.table.pot_transfers))
    #         if player.bet > self.table.last_bet:
    #             self.table.last_bet = player.bet
    #         player.is_all_in = True
    #         text_prompt.show_player_move(player, move, self.pause)
    #     elif move == 'folded':
    #         player.is_folded = True
    #         text_prompt.show_player_move(player, move, self.pause)
    #         if player.is_human:
    #             # Speed up the hand
    #             self.pause = 1.25
    #             self.long_pause = 3.0
    #             self.short_pause = 0.5

    def check_hand_over(self) -> bool:
        """Checks if the current hand is over.

        Returns:
            True if hand is over, False otherwise.
        """
        players_able_to_bet = 0
        for player in self.get_active_players():
            if not player.is_all_in and not player.is_folded:
                players_able_to_bet += 1
        return players_able_to_bet < 2

    def determine_winners(self):
        """Determine the winners of each pot and award them their chips."""
        if self.table.pots[-1][0] == 0:
            self.table.pots = self.table.pots[:-1]
        unfolded_players = [player for player in self.get_active_players() if not player.is_folded]
        if len(unfolded_players) == 1:
            winnings = 0
            for pot in self.table.pots:
                winnings += pot[0]
            winner = unfolded_players[0]
            winner.chips += winnings
            text_prompt.show_table(self.players, self.table, 0)
            text_prompt.show_default_winner_fold(winner.name)
        else:
            # If only 1 player is eligible for last side pot (i.e. other players folded/all-in), award player that pot
            players_eligible_last_pot = []
            for player in self.table.pots[-1][1]:
                if not player.is_folded:
                    players_eligible_last_pot.append(player)
            if len(players_eligible_last_pot) == 1:
                hand_winner = players_eligible_last_pot[0]
                text_prompt.show_table(self.players, self.table, 0)
                text_prompt.show_default_winner_eligibility(hand_winner.name, len(self.table.pots) - 1)
                hand_winner.chips += self.table.pots[-1][0]
                self.table.pots = self.table.pots[:-1]
            while len(self.table.community) < 5:
                self.table.community.extend(self.deck.deal(1))
            self.showdown()

    def showdown(self):
        """Runs the showdown phase."""
        text_prompt.show_table(self.players, self.table, 0)








        # !!!!!!!!!!!!!!!!!!!!!!!!!!!!!
        # text_prompt.show_phase_change_alert('Showdown', self.dealer, self.pause)





        # Divvy chips to the winner(s) of each pot/side pot
        for i in reversed(range(len(self.table.pots))):
            showdown_players = []
            for player in self.table.pots[i][1]:
                if not player.is_folded:
                    showdown_players.append(player)
            hand_winners = hand_ranking_utils.determine_showdown_winner(showdown_players, self.table.community)
            for winner in hand_winners:
                winner.chips += int(self.table.pots[i][0] / len(hand_winners))
            text_prompt.show_showdown_results(self.players, self.table, hand_winners, showdown_players, pot_num=i)

    def check_game_over(self):
        """Checks if the game is over.

        If the game is not over (i.e. all but one player has no chips), ask the user if they would
        like to continue the game.

        Returns:
            bool: True if the game is over, False otherwise.
        """
        for player in self.get_active_players():
            if player.chips == 0:
                player.is_in_game = False
        active_players = self.get_active_players()
        if len(active_players) == 1:
            text_prompt.show_table(self.players, self.table, 0)
            text_prompt.show_game_winners(self.players, [active_players[0].name])
            return True
        else:
            while True:
                text_prompt.clear_screen()
                user_choice = io_utils.input_no_return(
                    "Continue on to next hand? Press (enter) to continue or (n) to stop.   ")
                if 'n' in user_choice.lower():
                    max_chips = max(self.get_active_players(), key=lambda player: player.chips).chips
                    winners_names = [player.name for player in self.get_active_players() if player.chips == max_chips]
                    text_prompt.show_table(self.players, self.table, 0)
                    text_prompt.show_game_winners(self.players, winners_names)
                    return True
                return False

    def get_active_players(self) -> list[Player]:
        return [player for player in self.players if player.is_in_game]
