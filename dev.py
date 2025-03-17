from packages.poker.cards import Deck, Hand, Table
from packages.poker.game import deal_hands, deal_table
from packages.poker.eval import best_hand
import packages.poker.consts as consts


class Player:
    def __init__(self, name):
        self.name = name
        self.hand = Hand()
        self.bet = 0

    def place_bet(self, amount):
        self.bet += amount
    
    def fold(self):
        self.hand = Hand()
    
    def raise_bet(self, amount):
        self.bet += amount
        

class Bet:
    def __init__(self, amount, player, round):
        self.amount = amount
        self.player = player
        self.round = round


def deal_hands(deck: Deck, players: list[Hand]):
    for _ in range(2):
        for player in players:
            player.add_card(deck.deal())


def betting_round(round_number, players):
    print(f"Betting round {round_number + 1} (Pre-flop, Flop, Turn, River)")
    for player in players:
        action = input(f"{player.name}, what would you like to do? (1) Check, (2) Bet, (3) Fold, (4) Raise : ")
        if action == "1":  # Check
            print(f"{player.name} checks.")
        elif action == "2":  # Bet
            bet_amount = int(input(f"{player.name}, how much would you like to bet? "))
            player.place_bet(bet_amount)
            print(f"{player.name} bets {bet_amount}.")
        elif action == "3":  # Fold
            player.fold()
            print(f"{player.name} folds.")
        elif action == "4":  # Raise
            raise_amount = int(input(f"{player.name}, how much would you like to raise? "))
            player.raise_bet(raise_amount)
            print(f"{player.name} raises by {raise_amount}.")


def play_table(deck: Deck, table: Table, players: list[Player]):
    betting_rounds = 4
    for i in range(betting_rounds):
        if i == 0:
            deck.deal() # burn card
            deal_hands(deck, [player.hand for player in players])
        elif i == 1:
            deck.deal() # burn card
            table.deal_flop(deck)
        elif i == 2:
            deck.deal() # burn card
            table.deal_turn(deck)
        elif i == 3:
            deck.deal() # burn card
            table.deal_river(deck)

        betting_round(i, players)


if __name__ == "__main__":
    deck = Deck()
    deck.shuffle()

    # player_hand = Hand()
    # bot_hand = Hand()
    player = Player("Player")
    bot = Player("Bot")

    table = Table()

    # deal_hands(deck, [player_hand, bot_hand])
    # deal_hands(deck, [player.hand, bot.hand])
    play_table(deck, table, [player, bot])

    print("Player hand:")
    player.hand.display()
    print("Bot hand:")
    bot.hand.display()
    print("Table:")
    table.display()

    player_best = best_hand(player.hand, table)
    bot_best = best_hand(bot.hand, table)

    # print("Player best hand:", consts.HAND_RANKINGS[player_best['hand_rank']])
    # player_best['combination'].display()

    # print("Bot best hand:", consts.HAND_RANKINGS[bot_best['hand_rank']])
    # bot_best['combination'].display()

    if player_best['hand_rank'] > bot_best['hand_rank']:
        print("Player wins!")
        player_best['combination'].display()
    elif player_best['hand_rank'] < bot_best['hand_rank']:
        print("Bot wins!")
        bot_best['combination'].display()
    else:
        print("Tie!")
