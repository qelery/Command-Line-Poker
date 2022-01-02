from time import sleep

from src.poker.enums.phase import Phase
from src.poker.prompts import big_text
from src.poker.utils.io_utils import clear_screen


def prompt_for_name() -> str:
    """Prompts user for their name."""
    clear_screen()
    print(big_text.welcome)
    print('\n' * 4)
    name = ''
    while not name.strip():
        name = input('What is your name?    ')
    return name


def prompt_for_number_computer_players() -> int:
    clear_screen()
    print(big_text.settings)
    print('\n' * 4)
    error_message = '\nMust choose between 1 to 5 computer players.'
    num_computer_players = 0
    while num_computer_players < 1 or num_computer_players > 5:
        try:
            num_computer_players = int(input('How many computer players? (up to 5)    '))
            if num_computer_players < 1 or num_computer_players > 5:
                print(error_message)
        except ValueError:
            print(error_message)
    return num_computer_players


def prompt_for_starting_chips() -> int:
    clear_screen()
    print(big_text.settings)
    print('\n' * 4)
    error_message = '\nMust choose between 100 and 999,999 chips.'
    starting_chips = 0
    while starting_chips < 100 or starting_chips > 999999:
        try:
            chips = input('How many chips to start with? (between 100 and 999,999)    ')
            starting_chips = int(chips.replace(',', ''))
            if starting_chips < 100 or starting_chips > 999999:
                print(error_message)
        except ValueError:
            print(error_message)
    return starting_chips


def prompt_for_big_blind(min_blind: int, max_blind: int) -> int:
    clear_screen()
    print(big_text.settings)
    print('\n' * 3)
    print('Last question!')
    error_message = f'\nBig Blind amount must be between {min_blind:,} - {max_blind:,}, ' \
                    f'or game will be too long or too short. '
    big_blind = 0
    while big_blind < min_blind or big_blind > max_blind:
        try:
            blind = input(f'How much should the Big Blind amount be? (between {min_blind:,} and {max_blind:,})    ')
            big_blind = int(blind.replace(',', ''))
            if big_blind < min_blind or big_blind > max_blind:
                print(error_message)
        except ValueError:
            print(error_message)
    return big_blind


def show_player_stats(initial_players, isShowDown=False):
    """Format each player's stats as a single line.

    A helper function for show_table().
    If the game is in the Show Down phase, line displays a little differently.

    Args:
        initial_players (list): all players who began the game
        isShowDown (bool): if True reveal computer player's cards and best hand rank
    """
    # Sort players such that those who are out of game display last
    players = sorted(initial_players, key=lambda player: player.is_in_game, reverse=True)
    # Display each player's stat line
    for i in range(len(players)):
        this_player = players[i]
        if this_player.is_in_game:
            hand_str = []
            if this_player.is_folded or this_player.hand == []:
                for j in range(2):
                    hand_str.append('     ')
            elif this_player.is_human:
                for card in this_player.hand:
                    hand_str.append(str(card))
            elif not this_player.is_human and isShowDown:
                for card in this_player.hand:
                    hand_str.append(str(card))
            elif not this_player.is_human and not isShowDown:
                for j in range(len(this_player.hand)):
                    hand_str.append('[###]')
            hand_str = '  '.join(hand_str)
            if isShowDown:
                chips = f'             Chips:{this_player.chips:>6}'
                print_msg = f"{this_player.name:>11}'s hand:    {hand_str}{chips}"
                if this_player.best_hand_rank:
                    print_msg += f'        <{this_player.best_hand_rank}>'
            else:
                bet = f'        Bet:{this_player.bet:>6}'
                if this_player.is_all_in:
                    chips = '                   all-in'
                    if this_player.bet == 0:
                        bet = '         '
                else:
                    chips = f'             Chips:{this_player.chips:>6}'
                print_msg = f"{this_player.name:>11}'s hand:    {hand_str}{chips}{bet}"
                if this_player.is_dealer:
                    print_msg += f'       <Dealer>'
                if this_player.is_SB:
                    print_msg += f'       <SB>'
                if this_player.is_BB:
                    print_msg += f'       <BB>'
        else:
            print_msg = f"{this_player.name:>18}:    [OUT OF CHIPS, OUT OF GAME]"
        print(print_msg)


def show_community(community):
    """Display community cards.

    Args:
        community (list): the 5 cards of the community
    """
    community_str = []
    for card in community:
        community_str.append(str(card))
    community_str = '  '.join(community_str)
    padding = ' '
    print(f'{padding:>9}COMMUNITY:  {community_str}')


def show_blinds(table):
    """ Display small and big blind amounts.

    Args:
        table (__main__.Table): the poker table
    """
    padding = ' '
    print(f'{padding:>7}Small Blind:{int(table.big_blind / 2):>6}')
    print(f'{padding:>9}Big Blind:{table.big_blind:>6}')


def show_pots(pots):
    """Display the amount of each pot.

    Args:
        pot (list): sublists are of len 2——index 0 being amount of pot, index 1 being players eligible for pot
    """
    # Display main pot
    if pots[0][0] == 1:
        chips = 'CHIP'
    else:
        chips = 'CHIPS'
    padding = ' '
    pot_str = f'{padding:>15}POT:{pots[0][0]:>6} {chips}'
    # Display side pots
    for i in range(1, len(pots)):
        if pots[0][0] == 1:
            chips = 'CHIP'
        else:
            chips = 'CHIPS'
        if i % 3 == 0:
            pot_str += f'\n{padding:>7}SIDE POT #{i}:{pots[i][0]:>6} {chips}'
        else:
            pot_str += f'{padding:>12}SIDE POT #{i}:{pots[i][0]:>6}'
    print(pot_str)


def show_pot_winners(hand_winners, showdown_players, pot_num):
    """Display the winners of each pot.

    Args:
        hand_winners (list): players who won the pot
        showdown_players (list): all players who participated in the showdown
        pot_num (int): which pot is currently being displayed
    """
    pot_type = 'the pot'
    if pot_num > 0:
        pot_type = f'SIDE POT #{pot_num}'
        players_str = ''
        for player in showdown_players:
            players_str += f'{player.name}   '
        print(f"           Players eligible for SIDE POT #{pot_num}:      {players_str}")
        print('\n')
    if len(hand_winners) == 1:
        hand_str = [str(c) for c in hand_winners[0].best_hand_cards]
        hand_str = '  '.join(hand_str)
        print(
            f"           {hand_str}      {hand_winners[0].name} won {pot_type} with a {hand_winners[0].best_hand_rank}{hand_winners[0].rank_subtype}!")
        if hand_winners[0].kicker_card:
            kicker_str = f'Kicker card was the {hand_winners[0].kicker_card}'
            print(f"{kicker_str:>75}")
        else:
            print()
    else:
        for i in range(len(hand_winners)):
            hand_str = [str(c) for c in hand_winners[i].best_hand_cards]
            hand_str = '  '.join(hand_str)
            print(f'           {hand_str}      {hand_winners[i].name}')
            if i == len(hand_winners) - 1:
                print(
                    f"\n\n           Split {pot_type} with a {hand_winners[i].best_hand_rank}{hand_winners[i].rank_subtype}!")
                if hand_winners[0].kicker_card:
                    kicker_str = f'Kicker card was the  {hand_winners[0].kicker_card.rank_symbol}'
                    print(f"{kicker_str:>33}")
        print()


def show_table(initial_players, table, time):
    """Update display with player's stats, community, blinds, and pot.

    Parameters:
        initial_players (list): all players who began the game
        table (__main__.Table): the poker table
        time (float): amount of time to pause the game
    """
    clear_screen()
    show_player_stats(initial_players)
    print('\n')
    show_community(table.community)
    print()
    show_blinds(table)
    show_pots(table.pots)
    print('\n\n')
    sleep(time)


def show_showdown_results(initial_players, table, hand_winners, showdown_players, pot_num):
    """Update display and show the winner of the a particular pot in the showdown.

    Parameters:
        initial_players (list): all players who began the game
        table (__main__.Table): the poker table
        hand_winners (list): players who won the pot
        showdown_players (list): all players who participated in the showdown
        pot_num (int): which pot is currently being displayed
    """
    clear_screen()
    show_player_stats(initial_players, isShowDown=True)
    print('\n')
    show_community(table.community)
    show_pots(table.pots)
    print('\n\n\n')
    show_pot_winners(hand_winners, showdown_players, pot_num)
    print()
    input("Press any key to continue....")


def show_game_winners(initial_players, winners_names):
    """Display winner(s) of the game and ending chips of each player.

    Args:
        initial_players (list): all players who began the game
        winners_names (list): name of poker winner(s)
    """
    # Sort player by chips remaining
    players = sorted(initial_players, key=lambda player: player.chips, reverse=True)
    clear_screen()
    for i in range(len(players)):
        player_name = f'{players[i].name:<12}'
        chips = f'Chips:{players[i].chips:>6}'
        print(f"{player_name:>44}{chips:>18}")
    print('\n' * 5)
    if len(winners_names) == 1:
        winners_str = winners_names[0]
    elif len(winners_names) == 2:
        winners_str = f'{winners_names[0]} and {winners_names[1]}'
    else:
        winners_str = ''
        for i in range(len(winners_names)):
            if i == len(winners_names) - 1:
                winners_str += f'and {winners_names[i]}'
            else:
                winners_str += f'{winners_names[i]}, '
    print(f'    >>> {winners_str} won the game!')
    print(big_text.game_over)
    print('\n')


# Various functions for displaying short messages on screen
def show_shuffling(time):
    print(f' >>> Deck is being shuffled...')
    sleep(time)


def show_dealing_hole(dealer_name, time):
    print(f' >>> {dealer_name} is dealing cards to players...')
    sleep(time)


def show_blind_increase(blind_amount, time):
    print(f' >>> The big blind has increased to {blind_amount}!')
    sleep(time)


def show_thinking(player_name, time):
    print(f' >>> {player_name} is thinking...')
    sleep(time)


def show_player_move(player, move, pause: float, bet=None):
    """Show player's move choice.

    Args:
        player (__main__.Player): player making the move
        move (str): move player chose
        bet (int): amount of bet
        pause (float): amount of time to pause the game
    """
    chips = 'chip' if bet == 1 else 'chips'
    if move == 'folded':
        print(f' >>> {player.name} folded! ×')
    elif move == 'checked':
        print(f' >>> {player.name} checked. √')
    elif move == 'all-in':
        print(f' >>> {player.name} went all-in!')
    elif move == 'called':
        print(f' >>> {player.name} called {player.bet} {chips}. ←→')
    elif move == 'bet':
        print(f' >>> {player.name} bet {player.bet} {chips}. ↑')
    else:
        print(f' >>> {player.name} raised to {player.bet} {chips}. ↑')
    sleep(pause)


def show_bet_blind(player_name, blind_size, time):
    """Show that player bet a blind

    Args:
        player_name (str): name of player
        blind_size (str): either 'small' or 'big'
        time (float): amount of time to pause the game
    """
    print(f' >>> {player_name} bet the {blind_size} blind')
    sleep(time)


def show_all_in(player_name, time):
    print(f' >>> {player_name} went all in!')
    sleep(time)


def show_default_winner_fold(player_name):
    print(' >>> All other players folded...')
    print(f' >>> {player_name} won the pot!')
    input("\n\nPress any key to continue....")


def show_default_winner_eligibility(player_name, side_pot_num):
    print(f'\n\n >>> {player_name} is the only player eligible for SIDE POT #{side_pot_num}. ')
    print(f' >>> Gave those chips to {player_name}.')
    input("\n\nPress any key to continue....")


def show_phase_change_alert(phase: Phase, dealer: str, pause_time: float):
    if phase is Phase.PREFLOP:
        print(f" >>> {phase.name.capitalize()} Round: {dealer} is the dealer!")
    else:
        print(f' >>> Round Change: the {phase.name.capitalize()}!')
    sleep(pause_time)
