import json

import pytest

from backend.app.poker.action import ActionType, PlayerAction
from backend.app.poker.bots.basic_bot import BasicBot
from backend.app.poker.player import Player
from backend.app.poker.texas_holdem import TexasHoldem


def test_resume_flop_and_finish_once():
    game = TexasHoldem([Player("Button", 100), Player("Blind", 100)])
    assert game.advance_until_decision() == 0
    game.submit_action(0, PlayerAction(ActionType.CALL))
    game.submit_action(1, PlayerAction(ActionType.CHECK))
    assert game.advance_until_decision() == 1
    assert game.view_for(1).street == "flop"
    assert not game.view_for(0).legal_actions.actions

    snapshot = json.loads(json.dumps(game.to_snapshot()))
    restored = TexasHoldem.from_snapshot(snapshot)
    assert restored.to_snapshot() == snapshot
    with pytest.raises(ValueError):
        restored.submit_action(0, PlayerAction(ActionType.CHECK))
    for table in (game, restored):
        while (seat := table.advance_until_decision()) is not None:
            table.submit_action(seat, PlayerAction(ActionType.CHECK))
        assert table.advance_until_decision() is None
        assert sum(p.chips for p in table.players) == 200
    assert restored.to_snapshot() == game.to_snapshot()
    restored.finish_hand()
    restored.start_hand()
    assert restored.acting_seat_id == 1


def test_restored_bot_acts_until_result_or_human():
    game = TexasHoldem([Player("Bot", 100, BasicBot()), Player("Human", 100)])
    game.start_hand()
    restored = TexasHoldem.from_snapshot(game.to_snapshot())
    assert restored.advance_until_decision() in (1, None)
    assert restored.street == "complete" or restored.acting_seat_id == 1


def test_middle_seat_busts_and_survivor_keeps_identity():
    from backend.app.poker.card import Card

    game = TexasHoldem([Player("Button", 100), Player("Short", 10), Player("Blind", 100)])
    # Draw order starts at seat 1. Seat 2's aces beat seat 1's high card.
    draws = [Card(rank, suit) for rank, suit in [
        ("2", "Clubs"), ("A", "Clubs"), ("3", "Clubs"),
        ("7", "Diamonds"), ("A", "Diamonds"), ("5", "Hearts"),
        ("6", "Hearts"), ("4", "Diamonds"), ("8", "Clubs"), ("J", "Spades"),
        ("Q", "Diamonds"), ("9", "Hearts"), ("K", "Hearts"), ("K", "Spades"),
    ]]
    game.deck.cards = [c for c in game.deck if c not in draws] + draws[::-1]
    assert game.advance_until_decision() == 0
    game.submit_action(0, PlayerAction(ActionType.FOLD))
    assert game.advance_until_decision() is None
    assert game.players[1].chips == 0
    game.finish_hand()
    assert game.advance_until_decision() == 2

    restored = TexasHoldem.from_snapshot(json.loads(json.dumps(game.to_snapshot())))
    for table in (game, restored):
        assert table.advance_until_decision() == 2
        view = table.view_for(seat_id=2)
        assert view.hero.seat_id == view.dealer_seat_id == view.acting_seat_id == 2
        assert view.hero.name == "Blind"
        assert view.hero.hand.cards == game.view_for(2).hero.hand.cards
        assert [p.seat_id for p in view.opponents] == [0]
        with pytest.raises(ValueError, match="Unknown seat"):
            table.view_for(1)
        with pytest.raises(ValueError, match="Unknown seat"):
            table.submit_action(1, PlayerAction(ActionType.CALL))
        table.submit_action(seat_id=2, action=PlayerAction(ActionType.CALL))
        assert table.advance_until_decision() == 0
