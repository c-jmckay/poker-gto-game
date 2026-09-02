from .deck import Deck
from .hand import Hand
from .card import Card
from .hand_evaluator import HandEvaluator
from enum import IntEnum

class Sim_Results(IntEnum):
    LOSS = 0
    TIE = 1
    WIN = 2

class EquityCalculator:

    @staticmethod
    def estimate_equity(hero_hand: Hand, board: Hand, num_opponents: int, simulations: int):
        wins = 0
        ties = 0
        for i in range(simulations):
            result = EquityCalculator.simulate_once(hero_hand, board, num_opponents)
            if (result == Sim_Results.WIN):
                wins += 1
            elif (result == Sim_Results.TIE):
                ties += 1
        equity = (wins + ties*.5)/simulations
        return equity
        #print(f"wins: {wins}, ties: {ties}\nequity: {equity}")

    @staticmethod
    def simulate_once(hero_hand: Hand, board: Hand, num_opponents):
        deck = Deck()
        deck.shuffle()
        for card in hero_hand:
            deck.remove(card)
        for card in board:
            deck.remove(card)
        opponent_hands = EquityCalculator.generate_random_opponents(deck, num_opponents)
        board = EquityCalculator.complete_board(deck, board)
        hero_hand_rank = EquityCalculator.get_hand_rank(hero_hand, board)
        opp_hand_ranks = []
        for i in range(num_opponents):
            opp_hand_rank = EquityCalculator.get_hand_rank(opponent_hands[i], board)
            opp_hand_ranks.append(opp_hand_rank)
            #print(f"Villain {i+1}: {opponent_hands[i].cards[0]}, {opponent_hands[i].cards[1]}\n{opp_hand_ranks[i]}")
        #print(f"Hero: {hero_hand.cards[0]}, {hero_hand.cards[1]}\n{hero_hand_rank}")
        #print(board)
        for rank in opp_hand_ranks:
            if (hero_hand_rank < rank):
                return Sim_Results.LOSS
        for rank in opp_hand_ranks:
            if (hero_hand_rank == rank):
                return Sim_Results.TIE
        return Sim_Results.WIN

    @staticmethod
    def get_hand_rank(hand: Hand, board: Hand):
        full_hand = Hand()
        for card in hand:
            full_hand.add_card(card)
        for card in board:
            full_hand.add_card(card)
        return HandEvaluator.evaluate_perms(full_hand)
    
    @staticmethod
    def generate_random_opponents(deck: Deck, num_opponents):
        opp_hands = []
        for i in range(num_opponents):
            opp_hand = Hand()
            opp_hand.add_card(deck.draw())
            opp_hand.add_card(deck.draw())
            opp_hands.append(opp_hand)
        return opp_hands

    @staticmethod
    def complete_board(deck: Deck, board: Hand):
        completed_board = Hand()
        for card in board:
            completed_board.add_card(card)

        for i in range(5-len(completed_board)):
            completed_board.add_card(deck.draw())
        return completed_board

if __name__ == "__main__":
    hand = Hand()
    hand.add_card(Card("A", "Spades"))
    hand.add_card(Card("A", "Clubs"))
    board = Hand()
    #board.add_card(Card("Q", "Spades"))
    #board.add_card(Card("J", "Spades"))
    #board.add_card(Card("10", "Spades"))
    EquityCalculator.estimate_equity(hand, board, 3, 10000)