from packages.poker.cards import Deck, Hand, Table
from packages.poker.gameplay import deal_hands, deal_table
from packages.poker.eval import best_hand
import packages.poker.consts as consts


class Player:
    def __init__(self, name):
        self.name = name
        self.hand = Hand()
        self.bet = 0
        self.marked = False

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
    max_bet = 0
    marked_player = None
    last_raiser = None
    last_raiser_index = None
    players_active = [player for player in players if player.hand]  # Active players are those who have not folded

    # Ensure that we mark the first player to start the round (if no one is marked)
    for player in players:
        if player.marked:
            marked_player = player
            break
    if not marked_player:  # If no player is marked, mark the first player
        marked_player = players[0]
        marked_player.marked = True

    current_player_index = players.index(marked_player)
    last_raiser_index = current_player_index

    while True:
        current_player = players[current_player_index]

        # Skip players who folded
        if not current_player.hand:
            current_player_index = (current_player_index + 1) % len(players)
            if current_player_index == last_raiser_index:
                break
            continue
        
        action = input(f"{current_player.name}, what would you like to do? (1) Check, (2) Call, (3) Fold, (4) Raise : ")

        if action == "1":  # Check
            if current_player.bet < max_bet:
                print("You cannot check. You must call or raise.")
                continue
            print(f"{current_player.name} checks.")
        
        elif action == "2":  # Call
            if current_player.bet < max_bet:
                call_amount = max_bet - current_player.bet
                current_player.place_bet(call_amount)
                print(f"{current_player.name} calls {call_amount}.")
            else:
                print("You have already matched the maximum bet. You can check or raise.")
                continue
        
        elif action == "3":  # Fold
            if current_player.bet < max_bet:
                print(f"{current_player.name} folds.")
                current_player.fold()
            else:
                print("You cannot fold. You must call or raise.")
                continue
        
        elif action == "4":  # Raise
            if max_bet == 0:  # First player to bet in the round
                raise_amount = int(input(f"{current_player.name}, how much would you like to raise? "))
                current_player.raise_bet(raise_amount)
                max_bet = current_player.bet
                last_raiser = current_player
                last_raiser_index = current_player_index
                print(f"{current_player.name} raises by {raise_amount}.")
            elif current_player.bet < max_bet:
                raise_amount = int(input(f"{current_player.name}, how much would you like to raise? "))
                if current_player.bet + raise_amount <= max_bet:
                    print(f"Your raise must increae the current bet of {max_bet}.")
                    continue
                current_player.raise_bet(raise_amount)
                max_bet = current_player.bet
                last_raiser = current_player
                last_raiser_index = current_player_index
                print(f"{current_player.name} raises by {raise_amount}.")
            else:
                print("You cannot raise. You must check or call.")
                continue

        # Move to the next player
        current_player_index = (current_player_index + 1) % len(players)
        
        # Break the loop if we've returned to the last raiser or all players are inactive
        if current_player_index == last_raiser_index:
            break

    # Mark the player who started the betting round
    for player in players:
        if player == last_raiser:
            player.marked = True
            break


def play_table(deck: Deck, table: Table, players: list[Player]): #! need to select 1 player as the marked player and play out from there to reset between rounds
    betting_rounds = 4
    for i in range(betting_rounds):
        match i:
            case 0:
                deck.deal() # burn card
                deal_hands(deck, [player.hand for player in players])
            case 1:
                deck.deal() # burn card
                table.deal_flop(deck)
            case 2:
                deck.deal() # burn card
                table.deal_turn(deck)
            case 3:
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
