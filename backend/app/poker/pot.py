from dataclasses import dataclass, field
from .player import Player

@dataclass
class Pot:
    amount: int = 0
    eligible_players: list[Player] = field(default_factory=list)

    def __str__(self) -> str:
        output = f"Pot Size: {self.amount}\nEligible Players: {self.eligible_players}"
        return output