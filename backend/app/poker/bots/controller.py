from abc import ABC, abstractmethod

from ..action import PlayerAction
from ..player import Player

class Controller(ABC):

    @abstractmethod
    def choose_action(self, game, player: Player) -> PlayerAction:
        pass