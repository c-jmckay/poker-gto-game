from enum import Enum
from dataclasses import dataclass

class ActionType(Enum):
    FOLD = "fold"
    CHECK = "check"
    CALL = "call"
    BET = "bet"
    RAISE = "raise"
    ALL_IN = "all in"

@dataclass(frozen=True)
class PlayerAction:
    action_type: ActionType
    amount: int = 0

    def __str__(self) -> str:
        return f"{self.action_type}, amount={self.amount}"

@dataclass(frozen=True)
class LegalActions:
    actions: list[ActionType]
    amount_to_call: int
    min_bet: int | None = None
    max_bet: int | None = None

    def __str__(self) -> str:
        s = f"legal actions: {self.actions}"
        s += f"\n amount to call: {self.amount_to_call}"
        s += f"\nminimum bet: {self.min_bet}"
        s += f"\nmaximum bet: {self.max_bet}"
        return s
