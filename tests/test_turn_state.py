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
    assert restored.acting_seat == 1


def test_restored_bot_acts_until_result_or_human():
    game = TexasHoldem([Player("Bot", 100, BasicBot()), Player("Human", 100)])
    game.start_hand()
    restored = TexasHoldem.from_snapshot(game.to_snapshot())
    assert restored.advance_until_decision() in (1, None)
    assert restored.street == "complete" or restored.acting_seat == 1
