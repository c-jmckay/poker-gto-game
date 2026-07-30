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
    
    @property
    def value(self):
        return {
            "2": 1,
            "3": 2,
            "4": 3,
            "5": 4,
            "6": 5,
            "7": 6,
            "8": 7,
            "9": 8,
            "10": 9,
            "J": 10,
            "Q": 11,
            "K": 12,
            "A": 13
        }[self.rank]

card = Card("9", "Diamonds")
print(card)
print(card.value)