from .controller import Controller
import random
from ..action import ActionType, PlayerAction

class RandomBot(Controller):
    def choose_action(self, game, player):
        legal_actions = game.get_legal_actions(player)
        action_type = random.choice(legal_actions.actions)
        return PlayerAction(action_type, 100)