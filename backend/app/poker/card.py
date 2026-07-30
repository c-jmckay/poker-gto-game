from dataclasses import dataclass
# constructor is card = Card("A", "Spades")

VALID_RANKS = ("2", "3", "4", "5", "6", "7", "8", "9", "10", "J", "Q", "K", "A")
VALID_SUITS = ("Clubs", "Diamonds", "Hearts", "Spades")

# cannot be changed after creation
@dataclass(frozen=True)
class Card:
    rank: str
    suit: str

    def __post_init__(self) -> None:
        if self.rank not in VALID_RANKS:
            raise ValueError(f"Invalid rank: {self.rank}")
        
        if self.suit not in VALID_SUITS:
            raise ValueError(f"Invalid suit: {self.suit}")
        
    def __str__(self) -> str:
        return f"{self.rank} of {self.suit}"