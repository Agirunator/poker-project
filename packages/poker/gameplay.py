from . import cards


def deal_hands(deck: cards.Deck, hands: list[cards.Hand]):
    for _ in range(2):
        for player in hands:
            player.add_card(deck.deal())


def deal_table(deck: cards.Deck, table: cards.Table):
    deck.deal()
    table.deal_flop(deck)
    deck.deal()
    table.deal_turn(deck)
    deck.deal()
    table.deal_river(deck)


# TODO: Add betting between rounds
