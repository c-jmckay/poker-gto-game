from .card import Card
from .hand_rank import HandRank

class Hand:
    def __init__(self):
        self.cards = []

    def add_card(self, card: Card):
        self.cards.append(card)

    def remove_card(self, card: Card):
        self.cards.remove(card)

    def clear(self):
        self.cards = []
    
    def __len__(self):
        return len(self.cards)
    
    def __iter__(self):
        for card in self.cards:
            yield card
    
    def __getitem__(self, index):
        return self.cards[index]

    def __repr__(self):
        return f"Hand({self.cards})"

    def __contains__(self, card: Card):
        return card in self.cards
    
    def __str__(self) -> str:
        output = ""
        for i in range (len(self.cards)-1):
            output += f"{self.cards[i]}, "
        output += f"{self.cards[-1]}"
        return output

  
#hand = Hand()
#hand.add_card(Card("A", "Clubs"))
#hand.add_card(Card("K", "Clubs"))
#hand.add_card(Card("Q", "Clubs"))
#print(len(hand))
#print(hand)
#five = Card("5", "Clubs")
#ace = Card("A", "Clubs")
#ace_2 = Card("A", "Diamonds")
#print(five in hand)
#print(ace in hand)
#print(ace_2 in hand)