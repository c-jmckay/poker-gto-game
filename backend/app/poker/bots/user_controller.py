from .controller import Controller
from ..prompt_terminal import prompt_for_action

class UserController(Controller):
    def choose_action(self, state):
        return prompt_for_action(state)
