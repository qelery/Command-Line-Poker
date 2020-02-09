"""
#####################################################################################
RULES OF TEXAS HOLD 'EM POKER

Source: Wikipedia - "Texas Hold em"
#####################################################################################


#####################################################################################
Future project ideas:
# Implement more sophisticated computer players
# Create gui for this game in Tkinter or Pygame
#####################################################################################
"""

import random
import display
import handranker


class Card:
    """Class representing a standard playing card"""
    def __init__(self, rank, suit):
        self.rank_value = rank
        self.suit_value = suit
        self.rank_symbol_dict = {
            2 :  '2',
            3 :  '3',
            4 :  '4',
            5 :  '5',
            6 :  '6',
            7 :  '7',
            8 :  '8',
            9 :  '9',
            10 : '10',
            11 : 'J',
            12 : 'Q',
            13 : 'K',
            14 : 'A'
        }
        self.suit_symbol_dict = {
            'C': '♣',
            'D': '♦',
            'H': '♥',
            'S': '♠'
        }
        self.rank_symbol = self.rank_symbol_dict[self.rank_value]
        self.suit_symbol = self.suit_symbol_dict[self.suit_value]

    def __str__(self):
        """Print card

        Example:
            [A  ♦]
            [10 ♥]
        """
        return f'[{self.rank_symbol:<2}{self.suit_symbol}]'



class Deck:
    """Class representing a standard deck of 52 playing cards"""
    def __init__(self):
        self.cards = []
        self.reset()

    def reset(self):
        """Refill deck with all cards in order"""
        suits = ['C', 'D', 'H', 'S']
        self.cards = [Card(rank_value, suit_value) for suit_value in suits for rank_value in range(2, 15)]

    def shuffle(self):
        """"Shuffle deck"""
        random.shuffle(self.cards)

    def deal(self, location, num_cards):
        """Append n number of card objects from deck to location (table's community or player's hand)

        Args:
            location (list): object to receive the card
            num_cards (int): number of cards to deal
        """
        for i in range(num_cards):
            self.cards.pop(0) # Burn a card like done in real poker
            location.append(self.cards.pop(0))

    def __str__(self):
        """Print deck

        Example:
            [2 ♣] [3 ♣] [4 ♣] [5 ♣] [6 ♣]
        """
        return ' '.join(str(card) for card in self.cards)



class Player:
    """Class representing a player.

    Args:
        name (str): player's name
        playing_style (function) = determines how the player will decide what move to execute
        table: a Table object
    """
    def __init__(self, name, playing_style, table, isHuman=False):
        self.name = name
        self.playing_style = playing_style
        self.table = table
        self.isHuman = isHuman
        self.chips = 0
        self.bet = 0
        self.hand = []
        self.isDealer = False
        self.isFolded = False
        self.isFirstAct = False
        self.isLocked = False
        self.isAllIn = False
        self.isInGame = True
        self.best_hand_cards = None
        self.best_hand_score = 0
        self.best_hand_rank = ''
        self.rank_subtype = ''
        self.kicker_card = None

    def make_move(self):
        """Allow player to choose either to call, check, fold, etc. with specific playing style."""
        return self.playing_style(self)

def human_play(self):
    """Allow human player to choose either to call, raise, fold, etc

    Returns:
        player's choice as string
    """
    choice = ''
    # If player doesn't have enough chips to raise or if player has just enough chips to raise
    if self.chips <= abs(self.bet - self.table.raise_amount):
        valid_moves = ['f', '(f)', 'fold', 'folded', 'a', '(a)', 'all', 'all in', 'all-in']
        # If not enough chips to call
        if self.chips <= abs(self.bet - self.table.last_bet):
            prompt = f" >>> Input (a) to go all-in or (f) to fold.   "
        else:
            valid_moves.extend(['c', '(c)', 'call', 'called'])
            prompt = f" >>> Input (c) to call {self.table.last_bet}, (a) to go all-in, or (f) to fold.   "
    elif self.table.num_times_raised < 4:
        valid_moves = ['c', '(c)', 'f', '(f)', 'fold', 'folded']
        if self.bet == self.table.last_bet:
            valid_moves.extend(['b', '(b)', 'bet', 'check', 'checked'])
            prompt = f" >>> Input (c) to check, (b) to bet {self.table.raise_amount} chips, or (f) to fold.   "
        else:
            valid_moves.extend(['r', '(r)', 'raise', 'raised', 'call', 'called'])
            prompt = f" >>> Input (c) to call {self.table.last_bet} chips, (r) to raise to {self.table.raise_amount} chips, or (f) to fold.   "
    # If there have been 4 bets/raises in current round
    else:
        valid_moves = ['c', '(c)', 'call', 'called', 'f', '(f)', 'fold', 'folded']
        prompt = f" >>> Input (c) to call {self.table.last_bet} chips or (f) to fold.   "
    while choice.lower() not in valid_moves:
            choice = input(prompt)
    # Return player's choice'
    choice = choice.lower()
    if 'b' in choice:
        return 'bet'
    if 'r' in choice:
        return 'raised'
    elif 'f' in choice:
        return 'folded'
    elif 'a' in choice:
        return 'all-in'
    elif self.bet == self.table.last_bet:
        return 'checked'
    else:
        return 'called'

def risky_play(self):
    """Computer player choice to check, call, raise, bet, fold, or go all-in. Player more likely to bet and raise."""
    x = random.random()
    # If player doesn't have enough chips to raise or just enough chips to raise
    if self.chips <= abs(self.bet - self.table.raise_amount):
        # If not enough chips to call
        if self.chips <= abs(self.bet - self.table.last_bet):
            if x <= .90:
                return 'all-in'
            else:
                return 'folded'
        else:
            if x <= .40:
                if self.bet == self.table.last_bet:
                    return 'checked'
                else:
                    return 'called'
            elif x <= .90:
                return 'all-in'
            else:
                return 'folded'
    elif self.table.num_times_raised < 4:
        if self.bet == self.table.last_bet:
            if x <= .40:
                return 'checked'
            elif x <= .90:
                return 'bet'
            else:
                return 'folded'
        else:
            if x <= .40:
                return 'called'
            elif x <= .90:
                return 'raised'
            else:
                return 'folded'
    # If there have been 4 bets/raises in current round
    else:
        if x <= .90:
            return 'called'
        else:
            return 'folded'

def safe_play(self):
    """Computer player choice to check, call, raise, bet, fold, or go all-in. Player less likely to bet and raise."""
    x = random.random()
    # If player doesn't have enough chips to raise or just enough chips to raise
    if self.chips <= abs(self.bet - self.table.raise_amount):
        # If not enough chips to call
        if self.chips <= abs(self.bet - self.table.last_bet):
            if x <= .60:
                return 'all-in'
            else:
                return 'folded'
        else:
            if x <= .60:
                if self.bet == self.table.last_bet:
                    return 'checked'
                else:
                    return 'called'
            elif x <= .80:
                return 'all-in'
            else:
                return 'folded'
    elif self.table.num_times_raised < 4:
        if self.bet == self.table.last_bet:
            if x <= .70:
                return 'checked'
            elif x <= .90:
                return 'bet'
            else:
                return 'folded'
        else:
            if x <= .70:
                return 'called'
            elif x <= .90:
                return 'raised'
            else:
                return 'folded'
    # If there have been 4 bets/raises in current round
    else:
        if x <= .90:
            return 'called'
        else:
            return 'folded'

def random_play(self):
    """Computer player choice to check, call, raise, bet, fold, or go all-in at random."""
    x = random.random()
    # If player doesn't have enough chips to raise or just enough chips to raise
    if self.chips <= abs(self.bet - self.table.raise_amount):
        # If not enough chips to call
        if self.chips <= abs(self.bet - self.table.last_bet):
            if x <= .50:
                return 'all-in'
            else:
                return 'folded'
        else:
            if x <= .30:
                if self.bet == self.table.last_bet:
                    return 'checked'
                else:
                    return 'called'
            elif x <= .66:
                return 'all-in'
            else:
                return 'folded'
    elif self.table.num_times_raised < 4:
        if self.bet == self.table.last_bet:
            if x <= .33:
                return 'checked'
            elif x <= .66:
                return 'bet'
            else:
                return 'folded'
        else:
            if x <= .33:
                return 'called'
            elif x <= .66:
                return 'raised'
            else:
                return 'folded'
    # If there have been 4 bets/raises in current round
    else:
        if x <= .66:
            return 'called'
        else:
            return 'folded'



class Table:
    """Class representing the poker table"""
    def __init__(self):
        self.community = []
        self.pots = []
        self.pot_transfers = []
        self.last_bet = 0
        self.big_blind = 0
        self.hands_played = 0
        self.phase = None
        self.raise_amount = 0
        self.num_times_raised = 0

    def update_raise_amount (self):
        """Updates the bet/raise amount.

        Fixed-limit Hold'em -- so in the preflop and flop the bet/raise increment is equal to the big blind,
        and in the turn and river the bet/raise increment is equal to double the big blind.
        """
        if self.phase in ['preflop', 'flop']:
            self.raise_amount = self.last_bet + self.big_blind
        elif self.phase in ['turn', 'river']:
            self.raise_amount = self.last_bet + (self.big_blind * 2)



class Poker:
    """This class is the control center of the game."""
    def __init__(self):
        """
        Construct all class instances
        """
        self.table = Table()
        self.initial_players = []
        self.prompt_for_settings()
        self.active_players = self.initial_players
        self.deck = Deck()

    def play(self):
        """Execute the game."""
        while True:
            self.reset_hand()
            phases = ['preflop', 'flop', 'turn', 'river']
            for phase in phases:
                self.run_phase(phase)
                if self.check_hand_over():
                    break
            self.determine_winners()
            if self.check_game_over():
                break

    def prompt_for_settings(self):
        """Prompt user for game settings."""
        human_name, num_computer_players, starting_chips, big_blind = display.show_setting_options()
        computer_playing_styles = [risky_play, safe_play, random_play]
        computer_names = ['Homer', 'Bart', 'Lisa', 'Marge', 'Milhouse', 'Moe', 'Maggie', 'Nelson', 'Ralph', 'Edna']
        random.shuffle(computer_names)
        self.initial_players.append(Player(human_name, human_play, self.table, isHuman=True))
        for i in range(num_computer_players):
            playing_style = random.choice(computer_playing_styles)
            name = computer_names.pop(0)
            if name == human_name: # Prevent computer player from having same name as human
                name = computer_names.pop(0)
            self.initial_players.append(Player(name, playing_style, self.table))
        for player in self.initial_players:
            player.chips = starting_chips
        self.table.big_blind = big_blind

    def assign_positions(self):
        """Assigns the position of the dealer and first act

        dealer = they are simply the player who bets last
        first act = the player who bets first during a new round of betting
        """
        num_players = len(self.active_players)
        if self.table.hands_played == 1:
            # Dealer will be randomly assigned
            x = random.randrange(0, num_players)
            self.active_players[x].isDealer = True
            self.active_players[(x + 3) % num_players].isFirstAct = True
        else:
            # Dealer position moves to the left
            old_dealer_index = [player.isDealer for player in self.initial_players].index(True)
            self.initial_players[old_dealer_index].isDealer = False
            while True:
                old_dealer_index += 1
                player_to_left = self.initial_players[old_dealer_index % len(self.initial_players)]
                if player_to_left in self.active_players:
                    player_to_left.isDealer = True
                    new_dealer_index = [player.isDealer for player in self.active_players].index(True)
                    self.active_players[(new_dealer_index + 3) % num_players].isFirstAct = True
                    break

    def reset_hand(self):
        """Get deck, table, and players ready to play another hand"""
        if any(player.isHuman for player in self.active_players):
            self.pause = 2.75
            self.long_pause = 5.0
            self.short_pause = 0.75
        else:
            self.pause = 1.25
            self.long_pause = 3.0
            self.short_pause = 0.5
        for player in self.active_players:
            player.bet = 0
            player.hand = []
            player.isFolded = False
            player.isAllIn = False
            player.isFirstAct = False
            player.isLocked = False
            player.best_hand_cards = None
            player.best_hand_score = 0
            player.best_hand_rank = ''
            player.rank_subtype = ''
            player.kicker_card = None
        self.table.community = []
        self.table.pots = [[0, self.active_players]]
        self.table.last_bet = 0
        self.table.phase = None
        self.table.hands_played += 1
        # Double the big blind every 5 hands played to make game go faster
        if self.table.hands_played % 5 == 0:
            self.table.big_blind *= 2
            display.clear_screen()
            display.show_table(self.initial_players, self.table, 0)
            display.show_blind_increase(self.table.big_blind, self.long_pause)
        self.table.raise_amount = self.table.big_blind
        self.table.num_times_raised = 0
        self.assign_positions()
        # Reset deck
        self.deck.reset()
        self.deck.shuffle()
        display.clear_screen()
        display.show_shuffling(self.pause)

    def make_bet(self, player, bet_amount):
        """Player makes a bet.

        Args:
            player (__main__.Player): player making the bet
            bet_amount (int): amount of the bet
        """
        n = abs(player.bet - bet_amount)
        player.chips -= n
        player.bet += n
        self.table.last_bet = player.bet

    def deal_hole(self, dealer_name):
        """Two cards are dealt to each player

        Args:
            dealer_name (str): name of current dealer
        """
        display.show_table(self.initial_players, self.table, self.short_pause)
        display.show_dealing_hole(dealer_name, self.pause)
        # Dealing structure matches real poker
        for i in range(2):
            for player in self.active_players:
                self.deck.deal(player.hand, 1)
        display.show_table(self.initial_players, self.table, self.short_pause)

    def player_moves(self, player, move=''):
        """ Get player's choice of move (call, raise, fold, etc) and execute it

        Args:
            player (__main__.Player): player making the move
        """
        if move == '':
            if player.playing_style != human_play:
                display.show_thinking(player.name, self.short_pause)
            move = player.make_move()
        if move == 'checked' or move == 'called':
            self.make_bet(player, self.table.last_bet)
            display.show_player_move(player, move, player.bet, self.pause)
        elif move == 'raised' or move == 'bet':
            self.table.num_times_raised += 1
            self.make_bet(player, self.table.raise_amount)
            for active_player in self.active_players:
                if not active_player.isFolded:
                    active_player.isLocked = False
            for person in self.active_players:
                if person.isAllIn:
                    person.isLocked = True
            display.show_player_move(player, move, player.bet, self.pause)
        elif move == 'all-in':
            player.bet += player.chips
            player.chips = 0
            # If the player's bet enough to raise (even if not in the proper increment)
            if self.table.last_bet < player.bet <= self.table.raise_amount:
                for active_player in self.active_players:
                    if not active_player.isFolded and not active_player.isAllIn:
                        active_player.isLocked = False
            self.table.pot_transfers.append(player.bet)
            # Prevent multiple side pots being created if players go all-in at same amount in same phase
            self.table.pot_transfers = list(set(self.table.pot_transfers))
            if player.bet > self.table.last_bet:
                self.table.last_bet = player.bet
            player.isAllIn = True
            display.show_player_move(player, move, None, self.pause)
        elif move == 'folded':
            player.isFolded = True
            display.show_player_move(player, move, None, self.pause)
            if player.isHuman:
                # Speed up the hand
                self.pause = 1.25
                self.long_pause = 3.0
                self.short_pause = 0.5

    def round_of_bets(self):
        """Run a round of betting."""
        num_players = len(self.active_players)
        if self.table.phase == 'preflop':
            # Place blind bets
            for i in range(num_players):
                if self.active_players[i].isDealer:
                    # Player to left of dealer makes small blind bet
                    small_blind_player = self.active_players[(i + 1) % num_players]
                    small_blind = int(self.table.big_blind / 2)
                    display.show_bet_blind(small_blind_player.name, 'small', self.pause)
                    if small_blind_player.chips >  small_blind:
                        self.make_bet(small_blind_player,  small_blind)
                    else:
                        self.player_moves(small_blind_player, 'all-in')
                    display.show_table(self.initial_players, self.table, 0)
                    # Player two spaces to the left of dealer makes big blind bet
                    big_blind_player = self.active_players[(i + 2) % num_players]
                    display.show_bet_blind(big_blind_player.name, 'big', self.pause)
                    if big_blind_player.chips > self.table.big_blind:
                        self.make_bet(big_blind_player, self.table.big_blind)
                    else:
                        self.player_moves(big_blind_player, 'all-in')
                    display.show_table(self.initial_players, self.table, 0)
                    break
        if self.table.phase == 'flop':
            '''
            During the preflop round, the "first act" is the player three places to the left of the dealer 
            (as the two players before the "first act" must bet the small blind and the big blind). 
            For all subsequent rounds the "first act" is the player immediately to the left of the dealer.
            '''
            # Assign First Act position (i.e. player left of dealer)
            for player in self.active_players:
                player.isFirstAct = False
            for i in range(num_players):
                if self.active_players[i].isDealer:
                    self.active_players[(i + 1) % num_players].isFirstAct = True
                    break
        x = [player.isFirstAct for player in self.active_players].index(True)
        # End round of betting when all but one player fold or when all unfolded players have locked in
        while True:
            if all(player.isLocked or player.isAllIn for player in self.active_players):
                break
            if [player.isFolded for player in self.active_players].count(False) == 1:
                break
            betting_player = self.active_players[(x) % num_players]
            if betting_player.isFolded or betting_player.isAllIn:
                x += 1
                continue
            self.table.update_raise_amount()
            self.player_moves(betting_player)
            betting_player.isLocked = True
            x += 1
            display.show_table(self.initial_players, self.table, 0)
        for player in self.active_players:
            if not player.isFolded and not player.isAllIn:
                player.isLocked = False
        # Determine amounts of side pots and players eligible for each
        if self.table.pot_transfers:
            self.table.pot_transfers.sort()
            net_transfers = []
            for i in range(len(self.table.pot_transfers) - 1):
                net_transfers.append(self.table.pot_transfers[i + 1] - self.table.pot_transfers[i])
            net_transfers.insert(0, self.table.pot_transfers[0])
            for i in range(len(net_transfers)):
                for player in self.active_players:
                    if player.bet == 0:
                        continue
                    if player.bet < net_transfers[i]:
                        self.table.pots[-1][0] += player.bet
                        player.bet = 0
                    else:
                        player.bet -= net_transfers[i]
                        self.table.pots[-1][0] += net_transfers[i]
                if i == len(net_transfers) - 1:
                    eligible_players = []
                    for player in self.active_players:
                        if not player.isFolded and not player.isAllIn:
                            eligible_players.append(player)
                else:
                    eligible_players = [player for player in self.active_players if player.bet > 0]
                self.table.pots.append([0, eligible_players])
        for player in self.active_players:
            if player.bet:
                self.table.pots[-1][0] += player.bet
                player.bet = 0
        self.table.last_bet = 0
        self.table.pot_transfers = []

    def run_phase(self, phase_name):
        """Run the events of a phase.

        Args:
            phase_name (str): name of the phase
            num_deal (int): number of cards to deal to community
        """
        if phase_name == 'preflop':
            for player in self.active_players:
                if player.isDealer:
                    dealer_name = player.name
            display.show_table(self.initial_players, self.table, 0)
            display.show_phase_change_alert(phase_name, self.pause, dealer_name)
            self.deal_hole(dealer_name)
            num_deal = 0
        elif phase_name == 'flop':
            display.show_phase_change_alert(phase_name, self.pause)
            num_deal = 3
        else:
            display.show_phase_change_alert(phase_name, self.pause)
            num_deal = 1
        self.table.phase = phase_name
        self.table.num_times_raised = 0
        self.deck.deal(self.table.community, num_deal)
        display.show_table(self.initial_players, self.table, 0)
        self.round_of_bets()
        display.show_table(self.initial_players, self.table, 0)

    def check_hand_over(self):
        """Checks if the current hand is over

        Returns:
            bool: True if hand is over, False otherwise.
        """
        players_able_to_bet = 0
        for player in self.active_players:
            if player.isAllIn == False and player.isFolded == False:
                players_able_to_bet += 1
        if players_able_to_bet > 1:
            return False
        else:
            return True

    def determine_winners(self):
        """Determine the winners of each pot and award them their chips."""
        if self.table.pots[-1][0] == 0:
            self.table.pots = self.table.pots[:-1]
        unfolded_players = [player for player in self.active_players if not player.isFolded]
        if len(unfolded_players) == 1:
            winnings = 0
            for pot in self.table.pots:
                winnings += pot[0]
            winner = unfolded_players[0]
            winner.chips += winnings
            display.show_table(self.initial_players, self.table, 0)
            display.show_default_winner_fold(winner.name)
        else:
            # If only 1 player is eligible for last side pot (i.e. other players folded/all-in), award player that pot
            players_eligible_last_pot = []
            for player in self.table.pots[-1][1]:
                if not player.isFolded:
                    players_eligible_last_pot.append(player)
            if len(players_eligible_last_pot) == 1:
                hand_winner = players_eligible_last_pot[0]
                display.show_table(self.initial_players, self.table, 0)
                display.show_default_winner_eligibility(hand_winner.name, len(self.table.pots)-1)
                hand_winner.chips += self.table.pots[-1][0]
                self.table.pots = self.table.pots[:-1]
            while len(self.table.community) < 5:
                self.deck.deal(self.table.community, 1)
            self.showdown()

    def showdown(self):
        """Run the showdown phase."""
        display.show_table(self.initial_players, self.table, 0)
        display.show_phase_change_alert('Showdown', self.pause)
        # Divvy chips to the winner(s) of each pot/side pot
        for i in reversed(range(len(self.table.pots))):
            showdown_players = []
            for player in self.table.pots[i][1]:
                if not player.isFolded:
                    showdown_players.append(player)
            hand_winners = handranker.determine_showdown_winner(showdown_players, self.table.community)
            for winner in hand_winners:
                winner.chips += int(self.table.pots[i][0] / len(hand_winners))
            display.show_showdown_results(self.initial_players, self.table, hand_winners, showdown_players, pot_num=i)

    def check_game_over(self):
        """"Check if the game is over.

        If the game is not over (i.e. all but one player has no chips), ask the user if they would
        like to continue the game.

        Returns:
            bool: True if the game is over, False otherwise.
        """
        for player in self.active_players:
            if player.chips == 0:
                player.isInGame = False
        self.active_players = [player for player in self.active_players if player.isInGame]
        if len(self.active_players) == 1:
            display.show_table(self.initial_players, self.table, 0)
            display.show_game_winners(self.initial_players, [self.active_players[0].name], self.long_pause)
            return True
        else:
            while True:
                display.clear_screen()
                user_choice = input("Continue on to next hand? Yes or No   ")
                if 'y' in user_choice.lower():
                    return False
                elif 'n' in user_choice.lower():
                    max_chips = max(self.active_players, key=lambda player: player.chips).chips
                    winners_names = [player.name for player in self.active_players if player.chips == max_chips]
                    display.show_table(self.initial_players, self.table, 0)
                    display.show_game_winners(self.initial_players, winners_names, self.long_pause)
                    return True


if __name__ == '__main__':
    Poker().play()
