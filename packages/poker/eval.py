from collections import Counter
from itertools import combinations

from packages.poker import cards


def rank_values(ranks):
    """Convert card ranks to numerical values for evaluation."""
    rank_mapping = {
        "2": 2,
        "3": 3,
        "4": 4,
        "5": 5,
        "6": 6,
        "7": 7,
        "8": 8,
        "9": 9,
        "10": 10,
        "J": 11,
        "Q": 12,
        "K": 13,
        "A": 14,
        "1": 10,
        "0": 10,
    }
    return [rank_mapping[rank] for rank in ranks]


def is_flush(suits):
    """Check if all the suits are the same (Flush) for a 5 card set."""
    return len(set(suits)) == 1


def is_straight(ranks):
    """Check if the ranks form a sequence (Straight) for a 5 card set."""
    ranks = rank_values(ranks)
    return sorted(ranks) == list(range(min(ranks), max(ranks) + 1))


def evaluate_hand(hand_cards):
    """
    Evaluate the best poker hand from a list of 5 cards.
    :param hand_cards: List of Card objects (5 cards).
    :return: The hand rank and the highest ranking card's rank.
    """
    ranks = [card.rank for card in hand_cards]
    suits = [card.suit for card in hand_cards]

    # Count occurrences of each rank (for pairs, three-of-a-kinds, etc.)
    rank_counts = Counter(ranks)
    most_common = rank_counts.most_common()

    match (
        is_flush(suits),
        is_straight(ranks),
        most_common[0][1],
        most_common[1][1] if len(most_common) > 1 else 0,
    ):
        case (True, True, _, _):
            # Royal Flush or Straight Flush
            sorted_cards = sorted(
                hand_cards, key=lambda x: rank_values([x.rank])[0], reverse=True
            )
            if "A" in ranks and "K" in ranks:
                return 10, sorted_cards  # Royal Flush (Ace-high)
            return 9, sorted  # Straight Flush
        case (_, _, 4, _):
            quads = [card for card in hand_cards if card.rank == most_common[0][0]]
            kickers = [card for card in hand_cards if card.rank != most_common[0][0]]
            return 8, (quads + kickers)  # Four of a Kind
        case (_, _, 3, 2):
            trips = [card for card in hand_cards if card.rank == most_common[0][0]]
            pair = [card for card in hand_cards if card.rank == most_common[1][0]]
            return 7, (trips + pair)  # Full House
        case (True, _, _, _):
            sorted_cards = sorted(
                hand_cards, key=lambda x: rank_values([x.rank])[0], reverse=True
            )
            return 6, sorted_cards  # Flush
        case (_, True, _, _):
            sorted_cards = sorted(
                hand_cards, key=lambda x: rank_values([x.rank])[0], reverse=True
            )
            return 5, sorted_cards  # Straight
        case (_, _, 3, _):
            trips = [card for card in hand_cards if card.rank == most_common[0][0]]
            kickers = [card for card in hand_cards if card.rank != most_common[0][0]]
            return 4, (trips + kickers)  # Three of a Kind
        case (_, _, 2, 2):
            pair1 = [card for card in hand_cards if card.rank == most_common[0][0]]
            pair2 = [card for card in hand_cards if card.rank == most_common[1][0]]
            if rank_values([pair1[0].rank])[0] > rank_values([pair2[0].rank])[0]:
                pairs = pair1 + pair2  # pair1 first
            else:
                pairs = pair2 + pair1
            kickers = [
                card
                for card in hand_cards
                if card.rank != most_common[0][0] and card.rank != most_common[1][0]
            ]
            return 3, (pairs + kickers)  # Two Pair
        case (_, _, 2, _):
            pair = [card for card in hand_cards if card.rank == most_common[0][0]]
            kickers = [card for card in hand_cards if card.rank != most_common[0][0]]
            return 2, (pair + kickers)  # One Pair
        case _:
            sorted_cards = sorted(
                hand_cards, key=lambda x: rank_values([x.rank])[0], reverse=True
            )
            return 1, sorted_cards  # High Card


def best_hand(hand, table):
    """
    Determine the best hand possible with the player's hole cards and the community cards.
    :param hand: Hand object containing the player's two hole cards.
    :param table: Table object containing the community cards (flop, turn, river).
    :return: A tuple containing the best hand rank and the best hand combination.
    """
    # Combine hand cards (player's two hole cards) with the community cards (flop, turn, river)
    all_cards = hand.cards + table.flop + table.turn + table.river

    # Generate all possible 5-card combinations from the 7 available cards
    possible_hands = combinations(all_cards, 5)

    # store all evaluated hands with their scores
    evaluated_hands = []

    for hand_combination in possible_hands:
        hand_rank, sorted_hand = evaluate_hand(hand_combination)
        evaluated_hands.append((hand_rank, sorted_hand))

    evaluated_hands.sort(key=lambda x: x[0], reverse=True)

    highest_hand_rank = evaluated_hands[0][0]

    highest_hand_combinations = [
        hand[1] for hand in evaluated_hands if hand[0] == highest_hand_rank
    ]

    if len(highest_hand_combinations) == 1:
        best_hand_combination = highest_hand_combinations[0]
    else:
        best_hand_combination = max(
            highest_hand_combinations,
            key=lambda hand: [
                rank_values([card.rank])[0]
                for card in sorted(
                    hand, key=lambda x: rank_values([x.rank])[0], reverse=True
                )
            ],
        )

    best_hand_obj = cards.Hand()
    # for card in best_hand_combination:
    for i in range(5):
        best_hand_obj.add_card(best_hand_combination[i])

    return {"hand_rank": highest_hand_rank, "combination": best_hand_obj}
