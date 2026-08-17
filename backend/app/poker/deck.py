from .card import Card, VALID_RANKS, VALID_SUITS
import random

class Deck:

    def __init__(self):
        self.cards = []
        for suit in VALID_SUITS:
            for rank in VALID_RANKS:
                self.cards.append(Card(rank, suit))

    def shuffle(self):
        random.shuffle(self.cards)

    def draw(self):
        dealt_card = self.cards.pop()
        return dealt_card
    
    def reset(self):
        self.cards = []
        for suit in VALID_SUITS:
            for rank in VALID_RANKS:
                self.cards.append(Card(rank, suit))
        self.shuffle()

    def remove(self, card: Card):
        self.cards.remove(card)

    def __len__(self):
        return len(self.cards)
    
    def __iter__(self):
        for card in self.cards:
            yield card

    def __getitem__(self, index):
        return self.cards[index]

    def __repr__(self):
        return f"Deck({len(self)} cards)"

    def __contains__(self, card: Card):
        return card in self.cards
    
    def __str__(self) -> str:
        output = ""
        for card in self.cards:
            output += f"{card}\n"
        return output