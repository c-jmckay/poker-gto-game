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

@dataclass(frozen=True)
class LegalActions:
    actions: list[ActionType]
    amount_to_call: int
    min_bet: int | None = None
    min_raise: int | None = None
    max_bet: int | None = None