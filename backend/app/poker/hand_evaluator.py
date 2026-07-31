from .hand_rank import HandRank
from .hand import Hand
from .card import Card
from .deck import Deck
from itertools import combinations
#from collections import Counter

class HandEvaluator:
    @staticmethod
    def evaluate(hand: Hand):
        hand_rank = HandRank.HIGH_CARD
        rank_counts = HandEvaluator.rank_counter(hand)
        suit_counts = HandEvaluator.suit_counter(hand)
        rank_counts_sorted = sorted(rank_counts, reverse=True)
        #print(rank_counts)
        #check for pair
        if 2 in rank_counts:
            hand_rank = HandRank.PAIR
        #check for two pair
        if 2 in rank_counts_sorted[1:]:
            hand_rank = HandRank.TWO_PAIR
        #trips
        if 3 in rank_counts:
            hand_rank = HandRank.THREE_OF_A_KIND
        #straight
        if HandEvaluator.is_straight(rank_counts):
            hand_rank = HandRank.STRAIGHT
        #flush
        if 5 in suit_counts:
            hand_rank = HandRank.FLUSH
        #full house
        if 3 in rank_counts and 2 in rank_counts:
            hand_rank = HandRank.FULL_HOUSE
        #quads
        if 4 in rank_counts:
            hand_rank = HandRank.FOUR_OF_A_KIND
        #straight flush
        if 5 in suit_counts and HandEvaluator.is_straight(rank_counts):
            hand_rank = HandRank.STRAIGHT_FLUSH
        #print(hand_rank)
        return hand_rank
    
    @staticmethod
    def rank_counter(hand: Hand):
        counts = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
        for card in hand:
            counts[card.value-1]+=1
        #print(counts)
        #print(sorted(counts))
        return counts
    
    @staticmethod
    def suit_counter(hand: Hand):
        counts = [0,0,0,0]
        for card in hand:
            if (card.suit == "Clubs"):
                counts[0]+=1
            elif (card.suit == "Diamonds"):
                counts[1]+=1
            elif (card.suit == "Hearts"):
                counts[2]+=1
            else:
                counts[3]+=1
        #print(counts)
        return counts
    
    @staticmethod
    def is_straight(rank_counts):
        for i in range(9):
            if (rank_counts[i] == 1 and rank_counts[i+1]== 1 and rank_counts[i+2]==1 and rank_counts[i+3]==1 and rank_counts[i+4]==1):
                return True
    
    @staticmethod
    def evaluate_seven(hand: Hand):
        cur = HandRank.HIGH_CARD
        for combo in combinations(hand,5):
            if HandEvaluator.evaluate(combo) > cur:
                cur = HandEvaluator.evaluate(combo)
                print(cur)
                five = Hand()
                for card in combo:
                    five.add_card(card)
                print(five)
        return

if __name__ == "__main__":
    hand = Hand()
    hand.add_card(Card("10", "Diamonds"))
    hand.add_card(Card("A", "Clubs"))
    hand.add_card(Card("Q", "Diamonds"))
    hand.add_card(Card("A", "Diamonds"))
    hand.add_card(Card("A", "Hearts"))
    hand.add_card(Card("J", "Diamonds"))
    hand.add_card(Card("J", "Clubs"))
    HandEvaluator.evaluate_seven(hand)
    #print(HandEvaluator.evaluate(hand))

    #hands = [0,0,0,0,0,0,0,0,0]
    #for i in range(100):
    #    deck = Deck()
    #    deck.shuffle()
    #    hand = Hand()
    #    for i in range(5):
    #        hand.add_card(deck.draw())
    #    hands[HandEvaluator.evaluate(hand)-1]+=1
    #    if (HandEvaluator.evaluate(hand)>4):
    #        print(hand)
    #print(hands)

    #j=1
    #while (True):
    #    deck = Deck()
    #    deck.shuffle()
    #    hand = Hand()
    #    for i in range(5):
    #        hand.add_card(deck.draw())
    #    if (HandEvaluator.evaluate(hand)>6):
    #        print(j)
    #        print(hand)
    #        break
    #    j+=1