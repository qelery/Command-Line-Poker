"""
#######################################################################################################################
This implementation of a poker hand ranker assigns each hand a score, as a way to quickly compare between hands of 
different ranks, and different hands of the same rank. The first digit scores the rank (e.g. Full House, Straight, etc) 
of the overall hand score. All successive digit PAIRS in the score represent certain values that may be needed to 
break ties between hands of that particular rank.  

A kicker card (tie breaker card) is evaluated in cases where the rules of poker call for one.
#######################################################################################################################
"""

from itertools import combinations

card_int_str_dict = {
    2: 'Two',
    3: 'Three',
    4: 'Four',
    5: 'Five',
    6: 'Six',
    7: 'Seven',
    8: 'Eight',
    9: 'Nine',
    10: 'Ten',
    11: 'Jack',
    12: 'Queen',
    13: 'King',
    14: 'Ace',
}

handrank_int_str_dict = {
    10 : 'Royal Flush',
    9  : 'Straight Flush',
    8  : 'Four of a Kind',
    7  : 'Full House',
    6  : 'Flush',
    5  : 'Straight',
    4  : 'Three of a Kind',
    3  : 'Two Pair',
    2  : 'One Pair',
    1  : 'High Card',
}


def determine_showdown_winner(showdown_players, community):
    """Determines which player(s) wins the showdown.

    Args:
        showdown_players (list): players competing for a particular pot
        community (list): the 5 cards of the community

    Returns:
        winners (list): players who won a particular pot
    """
    # Create a list of the winners with the best scoring hand
    winners = []
    for player in showdown_players:
        combos = combinations(player.hand + community, 5)
        for combo in combos:
            raw_score = score_hand(combo)
            if raw_score > player.best_hand_score:
                player.best_hand_score = raw_score
                combo = sorted(combo, key=lambda x: x.rank_value, reverse=True)
                player.best_hand_cards = combo
        #  Assign the string version of the player's best hand
        player.best_hand_rank = handrank_int_str_dict[int(player.best_hand_score / 10000000000)]
        if winners == []:
            winners = [player]
        elif player.best_hand_score > winners[0].best_hand_score:
            winners = [player]
        elif player.best_hand_score == winners[0].best_hand_score:
            winners.append(player)
    assign_handrank_subtypes(showdown_players)
    assign_kicker_card(winners, showdown_players)
    return winners


def score_hand(hand):
    """Scores a particular hand combination that a player could possibly make.

    Args:
        hand (list): a 5 card combination

    Returns:
        score (int): score of the hand
    """
    hand = list(hand)
    hand.sort(key=lambda card: card.rank_value, reverse=True)
    score_functions = [score_royal_flush, score_straight_flush, score_num_of_kind, score_full_house, score_flush,
                       score_straight, score_num_of_kind,score_two_pair, score_num_of_kind, score_high_card]
    params = [[hand], [hand], [hand, 4], [hand], [hand], [hand], [hand, 3], [hand], [hand, 2], [hand]]
    for func, param in zip(score_functions, params):
        score = func(*param)
        if score:
            return score


def assign_handrank_subtypes(showdown_players):
    """Further categorizes the rank of a player's best hand, by giving it a subtype.

    Example:
        [ A A A K K ] is a hand rank string of "Full House", and the subtype string is "Aces over Kings"

    Args:
        showdown_players (list): players competing for a particular pot
    """
    for player in showdown_players:
        score = player.best_hand_score
        hand_rank = player.best_hand_rank
        if hand_rank == 'Straight Flush' or hand_rank == 'Straight':
            high_card = card_int_str_dict[int(str(score)[1:3])]
            player.rank_subtype = f': {high_card} high'
        elif hand_rank == 'Full House':
            pair_card = card_int_str_dict[int(str(score)[1:3])]
            triple_card = card_int_str_dict[int(str(score)[3:5])]
            if pair_card == 'Six': pair_card = 'Sixe'
            if triple_card == 'Six': triple_card = 'Sixe'
            player.rank_subtype = f': {pair_card}s over {triple_card}s'
        elif hand_rank == 'Two Pair':
            higher_pair = card_int_str_dict[int(str(score)[1:3])]
            lower_pair = card_int_str_dict[int(str(score)[3:5])]
            if higher_pair == 'Six': higher_pair = 'Sixe'
            if lower_pair == 'Six': lower_pair = 'Sixe'
            player.rank_subtype = f': {higher_pair}s and {lower_pair}s'
        elif hand_rank == 'One Pair':
            pair_card = card_int_str_dict[int(str(score)[1:3])]
            if pair_card == 'Six': pair_card = 'Sixe'
            player.rank_subtype = f': {pair_card}s'
        elif hand_rank in ['Four of a Kind', 'Three of a Kind', 'two of a kind']:
            tuple_card = card_int_str_dict[int(str(score)[1:3])]
            if tuple_card == 'Six': tuple_card = 'Sixe'
            player.rank_subtype = f': {tuple_card}s'
        elif hand_rank == 'High Card':
            high_card = card_int_str_dict[int(str(score)[1:3])]
            player.rank_subtype = f': {high_card}'


def assign_kicker_card(winners, showdown_players):
    """Assign a kicker card, if any, to the showdown winner(s).

    In certain cases of a tie between certain hands of the same rank AND subtype, the rules of poker say that
    a kicker card may be needed to break a tie. Determine the kicker card that was used to break the tie, if any,
    and assign that card to the winner.

    Example -
        Player A -  [ K♠  8♥ ]
        Player B -  [ K♠  6♣ ]
        Community - [ K♥  2♣  10♣  5♠  J♥]
        Player A and B both tie with the same hand rank and subtype, One Pair: Kings. A kicker card is used to
        break the tie. The best One Pair hand Player A can make is K-K-J-10-8. The best Player B can make
        is K-K-J-10-6. Player A wins. However if the community's 2♣ were replaced with a Q♣,
        the best One Pair hand each player can make becomes K-K-Q-J-10. Both players would win.

    Args:
        winners (list): players whose best hand have the same rank and subtype
        showdown_players (list): players competing for a particular pot
    """
    kicker_card_rank = None
    if winners[0].best_hand_rank in ['High Card', 'One Pair', 'Three of a Kind', 'Four of a Kind']:
        tied_players = [player for player in showdown_players if str(player.best_hand_score)[0:3] == str(winners[0].best_hand_score)[0:3]]
        if len(tied_players) == 1:
            return
        for i in range(3, 11, 2):
            card_at_index_list = [int(str(player.best_hand_score)[i:i + 2]) for player in tied_players]
            if card_at_index_list.count(max(card_at_index_list)) != len(tied_players):
                kicker_card_rank = max(card_at_index_list)
                break
    elif winners[0].best_hand_rank == 'Two Pair':
        tied_players = [player for player in showdown_players if str(player.best_hand_score)[0:5] == str(winners[0].best_hand_score)[0:5]]
        if len(tied_players) == 1:
            return
        players_last_card_list = [int(str(player.best_hand_score)[5:7]) for player in tied_players]
        if players_last_card_list.count(max(players_last_card_list)) != len(tied_players):
            kicker_card_rank = max(players_last_card_list)
    elif winners[0].best_hand_rank == 'Flush':
        tied_players = [player for player in showdown_players if str(player.best_hand_score)[0] == str(winners[0].best_hand_score)[0]]
        if len(tied_players) == 1:
            return
        for i in range(1, 11, 2):
            card_at_index_list = [int(str(player.best_hand_score)[i:i + 2]) for player in tied_players]
            if card_at_index_list.count(max(card_at_index_list)) != len(tied_players):
                kicker_card_rank = max(card_at_index_list)
                break
    # Assign kicker card to winners if one was needed to break a tie
    if kicker_card_rank:
        for winner in winners:
            for card in winner.best_hand_cards:
                if card.rank_value == kicker_card_rank:
                    winner.kicker_card = card
                    break


def score_high_card(hand):
    """
    All score for hands ranking High Card start with a 1, the lowest hand rank.
    Each successive digit pair represents the value of each card when reverse sorted.

    Example:
         [ A 9 8 4 2 ] scores 1 14  09  08  04  02
         [ A 9 8 5 2 ] scores 1 14  09  08  05  02      <--Winner (higher numerical score)

    Parameters:
        hand: a list of Card objects
    """
    rank_values = [card.rank_value for card in hand]
    score = '1' + ''.join(f'{x:02d}' for x in rank_values)
    return int(score)

def score_two_pair(hand):
    """
    All score for hands ranking Two pair start with 3. The next two pairs of digit pairs represent the value of the cards
    that formed the pairs in order of largest to smallest. The third pair of digits represent the kicker card.

    Example:
         [ J J 8 8 2 ] scores 3 11 08 02 00 00      <-- Winner (higher numerical score)
         [ J J 5 5 3 ] scores 3 11 05 03 00 00

    Parameters:
        hand: a list of Card objects
    """
    score = 0
    rank_values = [card.rank_value for card in hand]
    if rank_values.count(rank_values[1]) == 2 and rank_values.count(rank_values[3]) == 2:
        paired_values = sorted([rank_values[1], rank_values[3]], reverse=True)
        unpaired_value = [k for k in rank_values if k != rank_values[1] and k != rank_values[3]][0]
        score = '3' + f"{paired_values[0]:02d}{paired_values[1]:02d}{unpaired_value:02d}0000"
        score = int(score)
    return score

def score_num_of_kind(hand, n):
    """
    All score for hands ranking Four of a Kind start with 8.
    All score for hands ranking Three of a Kind start with 4.
    All score for hands ranking Two Pair start with 2.

    After the first digit in the score, the next digit pair represents the value of the tuple card,
    and each remaining digit pair represent the value of the kicker cards, the cards did not contribute to the tuple.

    Example:
         [ 2 2 2 J 6 ] scores 4 02 11 06 00 00
         [ 9 9 Q 7 5 ] scores 2 09 12 07 05 00
         [ 2 2 2 J 7 ] scores 4 02 11 07 00 00      <-- Winner (higher numerical score)

    Parameter:
        n: the number of same ranking cards to look for
    """
    rank_values = [card.rank_value for card in hand]
    score = 0
    for value in rank_values:
        if rank_values.count(value) == n:
            tuple_value = value
            if n == 4:
                nontuple_value = [x for x in rank_values if x != tuple_value]
                score = '8' + f"{tuple_value:02d}{nontuple_value[0]:02d}000000"
                return int(score)
            if n == 3:
                nontuple_values = sorted([x for x in rank_values if x != tuple_value], reverse=True)
                score = '4' + f"{tuple_value:02d}{nontuple_values[0]:02d}{nontuple_values[1]:02d}0000"
                return int(score)
            if n == 2:
                nontuple_values = sorted([x for x in rank_values if x != tuple_value], reverse=True)
                score = '2' + f"{tuple_value:02d}{nontuple_values[0]:02d}{nontuple_values[1]:02d}{nontuple_values[2]:02d}00"
                return int(score)
    return score

def score_full_house(hand):
    """
    All score for hands ranking Full House start with 7.

    After the first digit in the score, the next digit pair represents the value of the triple card,
    and the digit pair after that represents the value of the pair card.

    Example:
         [ 5 5 5 J J ] scores 7 05 11 00 00 00
         [ 5 5 5 Q Q ] scores 7 05 11 00 00 00      <-- Winner (higher numerical score)
    """
    score = 0
    rank_values = [card.rank_value for card in hand]
    if tuple(rank_values.count(card) for card in set(rank_values)) in [(3, 2), (2,3)]:
        if rank_values.count(rank_values[0]) == 3:
            triplet_value = rank_values[0]
            pair_value = rank_values[-1]
        else:
            pair_value = rank_values[0]
            triplet_value = rank_values[-1]
        score = '7' + f"{triplet_value:02d}{pair_value:02d}000000"
        score = int(score)
    return score

def score_straight(hand):
    """
    All score for hands ranking Straight start with 5.

    After the first digit in the score, the next digit pair represents the value of the high card in the straight.

    Example:
         [ 9 8 7 6 5 ] scores 5 09 00 00 00 00          <-- Winner (higher numerical score)
         [ 6 5 4 3 2 ] scores 5 06 00 00 00 00
    """
    score = 0
    rank_values = [card.rank_value for card in hand]
    if (max(rank_values) - min(rank_values) == 4) and len(set(rank_values)) == 5:
        high_card = max(rank_values)
        score = '5' + f'{high_card:02d}00000000'
        score = int(score)
    return score

def score_flush(hand):
    """
    All score for hands ranking Flush start with 6.

    After the first digit in the score, each successive digit pair represents the value of
    each card when reverse sorted.


    Example:
         [ J♣  10♣  5♣  4♣  3♣ ] scores 6 11 10 05 04 03
         [ J♥  10♥  6♥  5♥  3♥ ] scores 6 11 10 06 05 03        <-- Winner (higher numerical score)
    """
    score = 0
    suit_values = [card.suit_value for card in hand]
    if len(set(suit_values)) == 1:
        rank_values = [card.rank_value for card in hand]
        score = '6' + ''.join(f'{x:02d}' for x in rank_values)
        score = int(score)
    return score

def score_straight_flush(hand):
    """
    All score for hands ranking Straight Flush start with 9.

    After the first digit in the score, each successive digit pair represents the value of
    each card when reverse sorted.t

    Example:
         [ J♣  10♣  9♣  8♣  7♣ ] scores 9 11 10 09 08 07        <-- Winner (higher numerical score)
         [ 7♥   6♥  5♥  4♥  3♥ ] scores 9 07 06 05 04 03
    """
    score = 0
    if score_flush(hand) and score_straight(hand):
        score += 90000000000
        score += score_straight(hand) - 50000000000
    return score

def score_royal_flush(hand):
    """
    A score for hands ranking Royal Flush start with 10.
    This is the highest score possible and can only be scored by one player.

    Example:
         [ A♦  K♦  Q♦  J♦  10♦ ] scores 10 00 00 00 00 00
    """
    score = 0
    if score_straight_flush(hand):
        rank_values = [card.rank_value for card in hand]
        if rank_values == [14, 13, 12, 11, 10]:
            score = 100000000000
    return score














