from blessed import Terminal

term = Terminal()


class Card:
    """A standard playing card.

    Attributes:
        rank_value: A number representing the card's rank
            (e.g. 5 for 5, or 12 for Queen)
        suit_value: A letter representing the card's suit
            (e.g. H for Hearts)
        rank_symbol: A print symbol representing the card's rank
            (e.g. 5 for 5, or Q for Queen)
        suit_symbol: A print symbol representing the card's suit
            (e.g. ♥ for Hearts)
    """
    RANK_LOWEST = 2
    RANK_HIGHEST = 14

    rank_symbol = {
        2: '2',
        3: '3',
        4: '4',
        5: '5',
        6: '6',
        7: '7',
        8: '8',
        9: '9',
        10: '10',
        11: 'J',
        12: 'Q',
        13: 'K',
        14: 'A'
    }
    suit_symbol = {
        'C': term.green('♣'),
        'D': term.cyan('♦'),
        'H': term.red('♥'),
        'S': term.yellow('♠')
    }

    def __init__(self, rank: int, suit: str) -> None:
        self.rank_value = rank
        self.suit_value = suit
        self.rank_symbol = self.rank_symbol[rank]
        self.suit_symbol = self.suit_symbol[suit]

    def __str__(self) -> str:
        """Returns a readable string representation of a Card.

        Example:
            [A  ♦]
            [10 ♥]
        """
        return f'[{self.rank_symbol:<2}{self.suit_symbol}]'
