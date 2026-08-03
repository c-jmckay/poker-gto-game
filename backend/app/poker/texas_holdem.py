from .deck import Deck
from .card import Card
from .hand import Hand
from .hand_evaluator import HandEvaluator
from .player import Player

class TexasHoldem:
    def __init__(self, players: list[Player]):
        self.players = players

        #cards
        self.deck = Deck()
        self.deck.shuffle()
        self.community_cards = Hand()

        #betting
        self.pot = 0
        self.small_blind = 10
        self.big_blind = 20
        self.current_bet = 0

        #order of play
        self.dealer_index = 2
        self.num_players = len(players)
        self.hands_played = 0
        self.max_hands_played = 3
        

    def start_game(self):
        while (self.hands_played < self.max_hands_played):
            self.start_hand()
            self.finish_hand()
        return
    
    def start_hand(self):
        self.enter_blinds()
        self.deal_hole_cards()
        self.first_round()
        self.deal_flop()
        self.second_round()
        self.deal_turn()
        self.third_round()
        self.deal_river()
        self.final_round()
        self.showdown()
        return
    
    def enter_blinds(self):
        self.player_bet(self.players[(self.dealer_index+1)%self.num_players], self.small_blind)
        print(f"{self.players[(self.dealer_index+1)%self.num_players].name} enters small blind")
        self.player_bet(self.players[(self.dealer_index+2)%self.num_players], self.big_blind)
        print(f"{self.players[(self.dealer_index+2)%self.num_players].name} enters big blind")

    def first_round(self):
        i = 0
        while (i < self.num_players):
            p = (self.dealer_index+3+i)%self.num_players
            bet = self.current_bet-self.players[p].current_bet
            if (bet>0):
                print(f"{self.players[p].name} calls {self.current_bet}")
                self.player_bet(self.players[p], bet)
            else:
                print(f"{self.players[p].name} checks")
            i+=1
        self.current_bet = 0

    def second_round(self):
        i = 0
        while (i < self.num_players):
            p = (self.dealer_index+3+i)%self.num_players
            print(f"{self.players[p].name} checks")
            i+=1
        self.current_bet = 0
    
    def third_round(self):
        i = 0
        while (i < self.num_players):
            p = (self.dealer_index+3+i)%self.num_players
            print(f"{self.players[p].name} checks")
            i+=1
        self.current_bet = 0
    
    def final_round(self):
        i = 0
        while (i < self.num_players):
            p = (self.dealer_index+3+i)%self.num_players
            print(f"{self.players[p].name} checks")
            i+=1
        self.current_bet = 0
    
    def player_bet(self, player: Player, size: int):
        player.bet(size)
        self.pot+=size
        self.current_bet = max(self.current_bet, player.current_bet)

    def deal_hole_cards(self):
        i = 0
        while (i<self.num_players*2):
            p = (self.dealer_index+1+i)%(self.num_players)
            self.players[p].draw_card(self.deck.draw())
            i+=1
        return
    
    def deal_flop(self):
        #burn card
        self.deck.draw()
        self.community_cards.add_card(self.deck.draw())
        self.community_cards.add_card(self.deck.draw())
        self.community_cards.add_card(self.deck.draw())
        print(f"Flop: {self.community_cards}")
        return
    
    def deal_turn(self):
        self.deck.draw()
        self.community_cards.add_card(self.deck.draw())
        print(f"Turn: {self.community_cards}")
        return

    def deal_river(self):
        self.deck.draw()
        self.community_cards.add_card(self.deck.draw())
        print(f"River: {self.community_cards}")
        return
    
    def showdown(self):
        best_hand_rank = (0,)
        winner_index = (self.dealer_index+3)%self.num_players
        i = 0
        while (i < self.num_players):
            p = (self.dealer_index+3+i)%self.num_players
            if (self.players[p].folded == False):
                full_hand = Hand()
                for card in self.community_cards:
                    full_hand.add_card(card)
                for card in self.players[p].hand:
                    full_hand.add_card(card)
                hand_rank = HandEvaluator.evaluate_seven(full_hand)
                print(f"{self.players[p].name} reveals {self.players[p].hand} giving {hand_rank}")
                if (hand_rank>best_hand_rank):
                    best_hand_rank = hand_rank
                    winner_index = p
            i+=1
        self.player_wins(winner_index)
        print(f"{self.players[winner_index].name} wins the hand with {best_hand_rank}.")

    def player_wins(self, player_index: int):
        self.players[player_index].receive_winnings(self.pot)

    def finish_hand(self):
        for player in self.players:
            player.reset_hand()
        self.dealer_index = (self.dealer_index+1)%self.num_players
        self.current_bet = 0
        self.pot = 0
        self.deck.reset()
        self.community_cards.clear()
        self.hands_played+=1
        self.show_player_stacks()
    
    def show_hole_cards(self):
        for player in self.players:
            player.show_hole_cards()

    def show_player_stacks(self):
        for player in self.players:
            player.show_stack()


if __name__ == "__main__":
    players = [Player("Colin", 2000), Player("Brooke", 2000), Player("Ella", 2000), Player("Ray", 2000), Player("Ty", 2000)]
    game = TexasHoldem(players)
    game.start_game()
