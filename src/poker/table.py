from __future__ import annotations

from src.poker.enums.betting_move import BettingMove
from src.poker.enums.phase import Phase
from src.poker.players.player import Player


class Table:
    increase_blind_hand_increments = 5

    def __init__(self):
        self.hands_played = 0
        self.community = []
        self.pots = []
        self.pot_transfers: list[int] = []
        self.last_bet = 0
        self.big_blind = 0
        self.raise_amount = 0
        self.num_times_raised = 0

    def reset(self, active_players: list[Player]) -> None:
        """Resets the table for the next hand to be played."""
        self.community = []
        self.pots = [[0, active_players]]
        self.pot_transfers = []
        self.last_bet = 0
        self.num_times_raised = 0
        if self.check_increase_big_blind():
            self.big_blind *= 2
        self.raise_amount = self.big_blind

    def check_increase_big_blind(self) -> bool:
        """Checks if the big blind should be increased.

        Some versions of Texas Hold'Em periodically increase the
        big blind to speed up the game.
        """
        return (self.hands_played > 0 and
                self.hands_played % Table.increase_blind_hand_increments == 0)

    def take_small_blind(self, player: Player) -> bool:
        """Takes the small blind bet from a player.

        Args:
            player: The player to collect the small blind from

        Returns:
            True if player was forced to go all-in, else False
        """
        small_blind = int(self.big_blind / 2)
        if player.chips > small_blind:
            self.last_bet = player.match_bet(small_blind)
            return False
        else:
            player.go_all_in()
            self.pot_transfers.append(player.bet)
            # Prevent multiple side pots being created if players go all-in at same amount in same phase
            self.pot_transfers = list(set(self.pot_transfers))
            if player.bet > self.last_bet:
                self.last_bet = player.bet
            return True

    def take_big_blind(self, player: Player) -> bool:
        """Takes the big blind bet from a player.

        Args:
            player: The player to collect the big blind from

        Returns:
            True if player was forced to go all-in, else False
        """
        if player.chips > self.big_blind:
            self.last_bet = player.match_bet(self.big_blind)
            return False
        else:
            player.go_all_in()
            self.pot_transfers.append(player.bet)
            # Prevent multiple side pots being created if players go all-in at same amount in same phase
            self.pot_transfers = list(set(self.pot_transfers))
            if player.bet > self.last_bet:
                self.last_bet = player.bet
            return True

    def take_bet(self, player: Player, move: BettingMove) -> None:
        if move is BettingMove.CHECKED or move is BettingMove.CALLED:
            self.last_bet = player.match_bet(self.last_bet)
        elif move is BettingMove.RAISED or move is BettingMove.BET:
            self.num_times_raised += 1
            self.last_bet = player.match_bet(self.raise_amount)
        elif move is BettingMove.ALL_IN:
            player.go_all_in()
            self.pot_transfers.append(player.bet)
            # Prevent multiple side pots being created if players go all-in at same amount in same phase
            self.pot_transfers = list(set(self.pot_transfers))
            if player.bet > self.last_bet:
                self.last_bet = player.bet
        else:
            player.fold()

    def update_raise_amount(self, phase: Phase) -> None:
        """Updates the bet/raise amount.

        In fixed-limit Hold'em the bet and raise increments is equal to the big blind
        in the preflop and flop. In the turn and river, the bet and raise increment is
        equal to double the big blind.
        """
        if phase in [Phase.PREFLOP, Phase.FLOP]:
            self.raise_amount = self.last_bet + self.big_blind
        elif phase in [Phase.TURN, Phase.RIVER]:
            self.raise_amount = self.last_bet + (self.big_blind * 2)

    def calculate_side_pots(self, active_players: list[Player]) -> None:
        """Determines amount of each side pot and players eligible for each."""
        if self.pot_transfers:
            self.pot_transfers.sort()
            net_transfers = []
            for i in range(len(self.pot_transfers) - 1):
                net_transfers.append(self.pot_transfers[i + 1] - self.pot_transfers[i])
            net_transfers.insert(0, self.pot_transfers[0])
            for i in range(len(net_transfers)):
                for player in active_players:
                    if player.bet == 0:
                        continue
                    if player.bet < net_transfers[i]:
                        self.pots[-1][0] += player.bet
                        player.bet = 0
                    else:
                        player.bet -= net_transfers[i]
                        self.pots[-1][0] += net_transfers[i]
                if i == len(net_transfers) - 1:
                    eligible_players = []
                    for player in active_players:
                        if not player.is_folded and not player.is_all_in:
                            eligible_players.append(player)
                else:
                    eligible_players = [player for player in active_players if player.bet > 0]
                self.pots.append([0, eligible_players])
        for player in active_players:
            if player.bet:
                self.pots[-1][0] += player.bet
                player.bet = 0
        self.pot_transfers = []
