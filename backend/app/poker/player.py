from .hand_rank import HandRank
from .hand import Hand
from .card import Card
from .deck import Deck
#from .bots.controller import Controller

class Player:
    def __init__(self, name: str, chips: int, controller):
        self.controller = controller

        self.hand = Hand()
        self.name = name
        self.chips = chips

        self.folded = False
        self.all_in = False

        self.current_bet = 0
        self.total_contribution = 0

        self.full_hand_rank = (0,)
        self.recent_winnings = 0
        

    def fold(self):
        self.folded = True
        return
    
    def draw_card(self, card: Card):
        self.hand.add_card(card)

    def reset_hand(self):
        self.folded = False
        self.all_in = False
        self.current_bet = 0
        self.total_contribution = 0
        self.recent_winnings = 0
        self.hand.clear()
    
    def show_stack(self):
        print(f"{self.name}: {self.chips} chips")

    def show_hole_cards(self):
        print(f"{self.name}: {self.hand}")

    def bet(self, size: int):
        self.current_bet += size
        self.total_contribution += size
        self.chips-=size
        if self.chips <= 0:
            self.all_in = True
    
    def receive_winnings(self, size: int):
        self.chips+=size
        self.recent_winnings+=size

    def __str__(self) -> str:
        return f"{self.name}"
    
    def __repr__(self) -> str:
        return f"{self.name}"
    
