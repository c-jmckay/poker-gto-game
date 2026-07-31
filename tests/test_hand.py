from backend.app.poker.card import Card
from backend.app.poker.hand import Hand


def test_new_hand_is_empty() -> None:
    hand = Hand()

    assert len(hand) == 0


def test_add_card() -> None:
    hand = Hand()
    card = Card("A", "Spades")
    hand.add_card(card)
    print(card)
    print(hand)

    assert len(hand) == 1
    assert card in hand


def test_add_multiple_cards() -> None:
    hand = Hand()
    ace = Card("A", "Spades")
    king = Card("K", "Hearts")

    hand.add_card(ace)
    hand.add_card(king)

    assert len(hand) == 2
    assert ace in hand
    assert king in hand


def test_remove_card() -> None:
    hand = Hand()
    card = Card("A", "Spades")
    hand.add_card(card)

    hand.remove_card(card)

    assert len(hand) == 0
    assert card not in hand


def test_clear_hand() -> None:
    hand = Hand()
    hand.add_card(Card("A", "Spades"))
    hand.add_card(Card("K", "Hearts"))

    hand.clear()

    assert len(hand) == 0


def test_hand_is_iterable() -> None:
    hand = Hand()
    cards = [
        Card("A", "Spades"),
        Card("K", "Hearts"),
    ]

    for card in cards:
        hand.add_card(card)

    assert list(hand) == cards


def test_hand_supports_indexing() -> None:
    hand = Hand()
    ace = Card("A", "Spades")
    king = Card("K", "Hearts")

    hand.add_card(ace)
    hand.add_card(king)

    assert hand[0] == ace
    assert hand[1] == king