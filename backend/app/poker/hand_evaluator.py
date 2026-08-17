from .hand_rank import HandRank
from .hand import Hand
from .card import Card
from .deck import Deck
from itertools import combinations
#from collections import Counter

class HandEvaluator:
    @staticmethod
    def evaluate(hand: Hand):
        hand_rank = (HandRank.HIGH_CARD,)
        rank_counts = HandEvaluator.rank_counter(hand)
        suit_counts = HandEvaluator.suit_counter(hand)
        rank_counts_sorted = sorted(rank_counts, reverse=True)
        #print(rank_counts)
        #print(rank_counts)
        #check for pair
        if 2 in rank_counts:
            hand_rank = (HandRank.PAIR,)
        #check for two pair
        if 2 in rank_counts_sorted[1:]:
            hand_rank = (HandRank.TWO_PAIR,)
        #trips
        if 3 in rank_counts:
            hand_rank = (HandRank.THREE_OF_A_KIND,)
        #straight
        if HandEvaluator.is_straight(rank_counts):
            hand_rank = (HandRank.STRAIGHT,)
        #flush
        if 5 in suit_counts:
            hand_rank = (HandRank.FLUSH,)
        #full house
        if 3 in rank_counts and 2 in rank_counts:
            hand_rank = (HandRank.FULL_HOUSE,)
        #quads
        if 4 in rank_counts:
            hand_rank = (HandRank.FOUR_OF_A_KIND,)
        #straight flush
        if 5 in suit_counts and HandEvaluator.is_straight(rank_counts):
            hand_rank = (HandRank.STRAIGHT_FLUSH,)
        #print(hand_rank)

        #high card hands
        if hand_rank == (1,):
            #vals = HandEvaluator.unsuited_values_sorted(hand)
            #for val in vals:
            #    hand_rank+=(val,)
            for i in range(13):
                if rank_counts[12-i]==1:
                    hand_rank+=(13-i,)
        #pair hands
        elif hand_rank == (2,):
            pair_value = rank_counts.index(2)+1
            hand_rank += (pair_value,)
            for i in range(13):
                if rank_counts[12-i]==1:
                    hand_rank+=(13-i,)
        #two-pair hands
        elif hand_rank == (3,):
            pair_value2 = rank_counts.index(2)+1
            pair_value1 = rank_counts.index(2, pair_value2)+1
            hand_rank += (pair_value1, pair_value2, rank_counts.index(1)+1)
        #trips hands
        elif hand_rank == (4,):
            trip_value = rank_counts.index(3)+1
            hand_rank += (trip_value,)
            for i in range(13):
                if rank_counts[12-i]==1:
                    hand_rank+=(13-i,)
        #straight hands
        elif hand_rank == (5,):
            if (rank_counts[3]==1 and rank_counts[12]==1):
                hand_rank+=(4,)
            else:
                for i in range (13):
                    if rank_counts[12-i]==1:
                        hand_rank+=(13-i,)
                        break
        #flush hands
        elif hand_rank == (6,):
            for i in range(13):
                if rank_counts[12-i]==1:
                    hand_rank+=(13-i,)
        #boat hands
        elif hand_rank == (7,):
            hand_rank += (rank_counts.index(3)+1, rank_counts.index(2)+1,)
        #quad hands
        elif hand_rank == (8,):
            hand_rank += (rank_counts.index(4)+1, rank_counts.index(1)+1,)
        #straight flush hands
        else:
            if (rank_counts[3]==1 and rank_counts[12]==1):
                hand_rank+=(4,)
            else:
                for i in range (13):
                    if rank_counts[12-i]==1:
                        hand_rank+=(13-i,)
                        break
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
        i = -1
        while i < 9:
            if (rank_counts[i%13] == 1 and rank_counts[i+1]== 1 and rank_counts[i+2]==1 and rank_counts[i+3]==1 and rank_counts[i+4]==1):
                return True
            i+=1
        return False
            
    @staticmethod
    def evaluate_perms(hand: Hand):
        cur = (0,)
        for combo in combinations(hand,5):
            if HandEvaluator.evaluate(combo) > cur:
                cur = HandEvaluator.evaluate(combo)
                #print(cur)
                #five = Hand()
                #for card in combo:
                #    five.add_card(card)
                #print(five)
        return cur
    
#if __name__ == "__main__":
#    hand = Hand()
#    hand.add_card(Card("K", "Diamonds"))
#    hand.add_card(Card("3", "Clubs"))
#    print(HandEvaluator.evaluate(hand))
    #hand.add_card(Card("3", "Diamonds"))
    #tup1 = (HandRank.STRAIGHT, 11, 8, 6, 5, 1)
    #tup2 = (HandRank.FLUSH, 11, 8, 6, 5, 1)
    #print(f"{tup1}\n{tup2}")
    #print(tup1<tup2)
    #hand = Hand()
    #hand.add_card(Card("K", "Diamonds"))
    #hand.add_card(Card("3", "Clubs"))
    #hand.add_card(Card("3", "Diamonds"))
    #hand.add_card(Card("3", "Hearts"))
    #hand.add_card(Card("Q", "Spades"))
    #print(HandEvaluator.unsuited_values_sorted(hand))
    #hand.add_card(Card("J", "Diamonds"))
    #hand.add_card(Card("J", "Clubs"))
    #HandEvaluator.evaluate_perms(hand)
    #print(HandEvaluator.evaluate(hand))
    #print(-1%13)
    #print(0%13)

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

    #j=0
    #best_hand = Hand()
    #deck = Deck()
    #deck.shuffle()
    #for i in range(7):
    #    best_hand.add_card(deck.draw())
    #best_hand_rank = HandEvaluator.evaluate_perms(best_hand)
    #print(f"{best_hand} ---> {best_hand_rank}")
#
    #while (j<1000):
    #    deck.reset()
    #    new_hand = Hand()
    #    for i in range(7):
    #        new_hand.add_card(deck.draw())
    #    new_hand_rank = HandEvaluator.evaluate_perms(new_hand)
    #    if new_hand_rank > best_hand_rank:
    #        best_hand = new_hand
    #        best_hand_rank = new_hand_rank
    #        print(f"{j}th iteration: {best_hand} ---> {best_hand_rank}")
    #    j+=1

##how many iterations does it take to hit a royal flush
#    j=0
#    deck = Deck()
#    while (True):
#        deck.reset()
#        new_hand = Hand()
#        for i in range(7):
#            new_hand.add_card(deck.draw())
#        new_hand_rank = HandEvaluator.evaluate_perms(new_hand)
#        if new_hand_rank == (HandRank.STRAIGHT_FLUSH, 13):
#            print(f"{j}th iteration: {new_hand} ---> {new_hand_rank}")
#            break
#        j+=1