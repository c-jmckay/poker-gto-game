from enum import Enum
from dataclasses import dataclass

class ActionType(Enum):
    FOLD = "fold"
    CHECK = "check"
    CALL = "call"
    BET = "bet"
    RAISE = "raise"

@dataclass(frozen=True)
class PlayerAction:
    action_type: ActionType
    amount: int = 0