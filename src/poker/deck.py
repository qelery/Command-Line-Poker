import random

from src.poker.card import Card


class Deck:
    """A standard deck of 52 playing cards.

    Attributes:
        cards: A list of playing cards remaining in the deck
    """

    def __init__(self) -> None:
        self.cards = []
        self.refill()

    def refill(self) -> None:
        """Refills deck with 52 standard playing cards."""
        suits = ['C', 'D', 'H', 'S']
        self.cards = [Card(rank, suit) for suit in suits for rank in
                      range(Card.RANK_LOWEST, Card.RANK_HIGHEST + 1)]

    def shuffle(self) -> None:
        """Shuffles the deck."""
        random.shuffle(self.cards)

    def deal(self, n: int) -> list[Card]:
        """Deals the specified number of cards from the deck.

        Args:
            n: The number of cards to return
        """
        return [self.cards.pop() for _ in range(n)]

    def burn(self) -> None:
        """Discards one card from the deck.

        A card is typically burned before dealing the flop, turn, and river.
        """
        self.cards.pop()

    def __str__(self) -> str:
        """Returns a readable string representation of a Deck.

        Example:
            [2 ♣] [3 ♣] [4 ♣] [5 ♣] [6 ♣]
        """
        return ' '.join(str(card) for card in self.cards)
