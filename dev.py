from packages.poker.cards import Deck, Hand, Table
from packages.poker.game import deal_hands, deal_table
from packages.poker.eval import best_hand
import packages.poker.consts as consts


if __name__ == "__main__":
    hand = Hand()
    deck = Deck()
    deck.shuffle()
    table = Table()

    deal_hands(deck, [hand])
    deal_table(deck, table)

    hand.display()
    table.display()

    best = best_hand(hand, table)

    print(consts.HAND_RANKINGS[best['hand_rank']])
    best['combination'].display()
