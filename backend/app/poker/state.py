from dataclasses import dataclass
from .hand import Hand
from .action import LegalActions

@dataclass(frozen=True)
class VillainState:
    name: str
    chips: int
    current_bet: int
    folded: bool
    all_in: bool

@dataclass(frozen=True)
class HeroState:
    name: str
    chips: int
    current_bet: int
    hand: Hand
    folded: bool
    all_in: bool

@dataclass(frozen=True)
class GameState:
    hero: HeroState
    opponents: list[VillainState]

    board: Hand
    pot: int

    dealer_index: int
    small_blind: int
    big_blind: int

    legal_actions: LegalActions
    current_bet: int

    def __str__(self) -> str:
        s = f"Hero = {self.hero.name}, {self.hero.chips} chips, {self.hero.current_bet} current bet, holding {self.hero.hand.cards[0]} and {self.hero.hand.cards[1]}"
        s += f"\nVillains = "
        for villain in self.opponents:
            s += f"{villain.name} ({villain.chips} chips), "
        s += f"\nBoard = {self.board}\nPot = {self.pot}"
        return s