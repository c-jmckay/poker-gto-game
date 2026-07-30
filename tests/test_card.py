import pytest

from backend.app.poker.card import Card

def test_create_card():
    card = Card("A", "Spades")

    assert card.rank == "A"
    assert card.suit == "Spades"

def test_card_string():
    card = Card("K", "Hearts")

    assert str(card) == "K of Hearts"

def test_invalid_rank():
    with pytest.raises(ValueError):
        Card("1", "Hearts")

def test_invalid_suit():
    with pytest.raises(ValueError):
        Card("J", "Squares")

def test_card_cannot_change():
    card = Card("A", "Spades")

    with pytest.raises(Exception):
        card.rank = "K"