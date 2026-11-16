"""Describe the evaluator's showdown tuples, where 1 is a two and 13 an ace."""

from .hand_rank import HandRank


PLURALS = ("twos", "threes", "fours", "fives", "sixes", "sevens", "eights",
           "nines", "tens", "jacks", "queens", "kings", "aces")
CARD_NAMES = ("2", "3", "4", "5", "6", "7", "8", "9", "10",
              "jack", "queen", "king", "ace")


def describe_hand(rank, opponents=()):
    """Describe a hand and the first deciding card against each comparable hand."""
    category = HandRank(rank[0])
    high = CARD_NAMES[rank[1] - 1]
    group = PLURALS[rank[1] - 1]
    base_length = 2
    if category == HandRank.PAIR:
        description = f"pair of {group}"
    elif category == HandRank.TWO_PAIR:
        description = f"two pair, {group} and {PLURALS[rank[2] - 1]}"
        base_length = 3
    elif category == HandRank.THREE_OF_A_KIND:
        description = f"three {group}"
    elif category == HandRank.FOUR_OF_A_KIND:
        description = f"four {group}"
    elif category == HandRank.FULL_HOUSE:
        return f"{group} full of {PLURALS[rank[2] - 1]}"
    elif category == HandRank.STRAIGHT:
        return f"{high}-high straight"
    elif category == HandRank.STRAIGHT_FLUSH:
        return f"{high}-high straight flush"
    elif category == HandRank.FLUSH:
        description = f"{high}-high flush"
    else:
        description = f"{high} high"

    deciding_indices = set()
    for other in opponents:
        if other[:base_length] != rank[:base_length]:
            continue
        for index in range(base_length, len(rank)):
            if rank[index] != other[index]:
                deciding_indices.add(index)
                break

    for index in sorted(deciding_indices):
        card = CARD_NAMES[rank[index] - 1]
        if category == HandRank.FLUSH:
            description += f" · {card} plays"
        else:
            description += f" · {card} kicker"
    return description
