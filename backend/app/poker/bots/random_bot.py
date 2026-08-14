from .controller import Controller
import random
from ..action import ActionType, PlayerAction

class RandomBot(Controller):
    def choose_action(self, game, player):
        legal_actions = game.get_legal_actions(player)
        action_type = random.choice(legal_actions.actions)
        if action_type in (ActionType.FOLD, ActionType.ALL_IN, ActionType.CALL, ActionType.CHECK):
            return PlayerAction(action_type, 0)
        amount = random.randrange(legal_actions.min_bet, legal_actions.max_bet, 10)
        return PlayerAction(action_type, amount)