from .hand_rank import HandRank
from .hand import Hand
from .card import Card
from .deck import Deck

class Player:
    def __init__(self, name: str, chips: int):
        self.hand = Hand()
        self.name = name
        self.chips = chips
        self.folded = False
        self.current_bet = 0

    def fold(self):
        self.folded = True
        return
    
    def draw_card(self, card: Card):
        self.hand.add_card(card)

    def reset_hand(self):
        self.folded = False
        self.current_bet = 0
        self.hand.clear()
    
    def show_stack(self):
        print(f"{self.name}: {self.chips} chips")

    def show_hole_cards(self):
        print(f"{self.name}: {self.hand}")

    def bet(self, size: int):
        self.current_bet += size
        self.chips-=size

    def receive_winnings(self, size: int):
        self.chips+=size
    
