import random

from . import consts, eval


class Card:
    def __init__(self, suit, rank):
        """
        Initialize a Card object with given suit and rank.

        :param suit: The suit of the card. Should be one of SUITS.
        :type suit: str
        :param rank: The rank of the card. Should be one of RANKS.
        :type rank: str
        """
        self.suit = suit
        self.rank = rank

    def __str__(self):
        return f"{self.rank}{consts.SUITS_SYMBOLS[self.suit]}"

    def display(self):
        """
        Display the card as a string in the format "Rank of Suit".
        """
        print(f"{self.rank}{consts.SUITS_SYMBOLS[self.suit]}")

    def __img__(self):
        suit_code = consts.SUITS_CODES[self.suit]
        rank_code = f"{eval.rank_values(self.rank)[0]:02}"
        return f"{suit_code}{rank_code}.png"


class Deck:
    def __init__(self):
        """
        Initialize a Deck object with 52 cards.
        """
        self.cards = [
            Card(suit, rank) for suit in consts.SUITS for rank in consts.RANKS
        ]

    def shuffle(self):
        """
        Shuffle the cards in the deck.
        """
        random.shuffle(self.cards)

    def deal(self):
        """
        Deal a card from the deck.
        """
        return self.cards.pop()

    def size(self):
        """
        Return the number of cards left in the deck.
        """
        return len(self.cards)


class Hand:
    """
    A Hand object represents a set of cards. It is initially empty when created.
    """

    def __init__(self):
        self.cards = []

    def add_card(self, card):
        """
        Add a card to the hand.
        """
        self.cards.append(card)

    def display(self):
        """
        Display the cards in the hand.
        """
        print(" ".join([card.__str__() for card in self.cards]))

    def size(self):
        """
        Return the number of cards in the hand.
        """
        return len(self.cards)


class Table:
    def __init__(self):
        self.flop = []
        self.turn = []
        self.river = []

    def deal_flop(self, deck: Deck):
        self.flop = []
        for _ in range(3):
            self.flop.append(deck.deal())

    def deal_turn(self, deck: Deck):
        self.turn = []
        self.turn = [deck.deal()]

    def deal_river(self, deck: Deck):
        self.river = []
        self.river = [deck.deal()]

    def display(self):
        print(" ".join([card.__str__() for card in self.flop + self.turn + self.river]))


class Player:
    def __init__(self, name):
        self.name = name
        self.hand = Hand()
        self.bet = 0
        self.marked = False
        self.folded = False

    def place_bet(self, amount):
        self.bet += amount

    def fold(self):
        self.folded = True


class Bet:
    def __init__(self, amount, player, round):
        self.amount = amount
        self.player = player
        self.round = round
