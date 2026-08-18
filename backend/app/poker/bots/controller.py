from abc import ABC, abstractmethod

from ..action import PlayerAction
from ..player import Player
from ..state import GameState, HeroState, VillainState

class Controller(ABC):

    @abstractmethod
    def choose_action(self, state: GameState) -> PlayerAction:
        pass