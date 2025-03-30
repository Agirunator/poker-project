from packages.poker import cards

deck = cards.Deck()
for card in deck.cards:
    print(card.__str__())