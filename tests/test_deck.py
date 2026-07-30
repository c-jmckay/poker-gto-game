import pytest

from backend.app.poker.deck import Deck

def test_card_count():
    deck = Deck()

    assert len(deck) == 52

def test_cards_unique():
    deck = Deck()

    assert len(set(deck.cards)) == 52

def test_draw():
    deck = Deck()
    card = deck.draw()

    assert len(deck) == 51
    assert card is not None


