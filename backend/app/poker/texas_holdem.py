from .deck import Deck
from .card import Card
from .hand import Hand
from .hand_evaluator import HandEvaluator
from .player import Player
from .action import ActionType, PlayerAction
from collections.abc import Callable
from .prompt_terminal import prompt_for_action


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
        self.dealer_index = 0
        self.num_players = len(players)
        self.num_players_remaining = self.num_players
        self.hands_played = 0
        self.max_hands_played = 3
        self.last_to_act = self.dealer_index
        
    def start_game(self):
        while (self.hands_played < self.max_hands_played):
            self.start_hand()
            self.finish_hand()
        return
    
    def start_hand(self):
        self.enter_blinds()
        self.deal_hole_cards()
        self.betting_round(True)
        if (self.num_players_remaining>1):
            self.deal_flop()
            self.betting_round(False)
        if (self.num_players_remaining>1):
            self.deal_turn()
            self.betting_round(False)
        if (self.num_players_remaining>1):
            self.deal_river()
            self.betting_round(False)
        
        if (self.num_players_remaining<=1):
            self.uncontested_win()
        else:
            self.showdown()
        return
    
    def enter_blinds(self):
        self.player_bet(self.players[(self.dealer_index+1)%self.num_players], self.small_blind)
        print(f"{self.players[(self.dealer_index+1)%self.num_players].name} enters small blind")
        self.player_bet(self.players[(self.dealer_index+2)%self.num_players], self.big_blind)
        print(f"{self.players[(self.dealer_index+2)%self.num_players].name} enters big blind")
    
    def betting_round(self, is_preflop: bool):
        first_position = (self.dealer_index+1)%self.num_players
        self.last_to_act = self.dealer_index
        if is_preflop == True:
            first_position = (self.dealer_index+3)%self.num_players
            self.last_to_act = (self.dealer_index+2)%self.num_players

        p = first_position
        while (True):
            if players[p].folded == False:
                self.apply_action(players[p], prompt_for_action(self, players[p]))
            if p == self.last_to_act:
                self.reset_round_bets()
                return
            p = (p+1)%self.num_players
        return
    
    def player_bet(self, player: Player, size: int):
        player.bet(size)
        self.pot+=size
        if player.current_bet > self.current_bet:
            self.last_to_act = (self.players.index(player)-1)%self.num_players
            self.current_bet = player.current_bet

    def reset_round_bets(self):
        self.current_bet = 0
        for player in self.players:
            player.current_bet=0

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
        print(f"\nFlop: {self.community_cards}")
        print(f"The pot contains {self.pot} chips")
        return
    
    def deal_turn(self):
        self.deck.draw()
        self.community_cards.add_card(self.deck.draw())
        print(f"\nTurn: {self.community_cards}")
        print(f"The pot contains {self.pot} chips")
        return

    def deal_river(self):
        self.deck.draw()
        self.community_cards.add_card(self.deck.draw())
        print(f"\nRiver: {self.community_cards}")
        print(f"The pot contains {self.pot} chips")
        return
    
    def showdown(self):
        best_hand_rank = (0,)
        #winner_index = (self.dealer_index+3)%self.num_players
        winners = []
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
                self.players[p].full_hand_rank = hand_rank
                print(f"\n{self.players[p].name} reveals {self.players[p].hand} giving {hand_rank}")
                if (hand_rank>best_hand_rank):
                    best_hand_rank = hand_rank
                    #winner_index = p
                    winners = [self.players[p]]
                elif (hand_rank == best_hand_rank):
                    winners.append(self.players[p])
            i+=1
        #checking for chop pot
        if (len(winners)==1):
            self.player_wins(winners[0], self.pot)
            print(f"\n{winners[0].name} wins the hand with {best_hand_rank}.")
        else:
            names = ""
            for player in winners:
                self.player_wins(player, self.pot/len(winners))
                names+=f"{player.name}, "
            print(f"{names} chop the pot for {self.pot/len(winners)} each")

    def uncontested_win(self):
        for i in range(self.num_players):
            if self.players[i].folded == False:
                self.player_wins(self.players[i])
                print(f"\n{self.players[i].name} wins the hand before showdown.")
        
    def player_wins(self, player: Player, amount: int):
        player.receive_winnings(amount)

    def finish_hand(self):
        for player in self.players:
            player.reset_hand()
        self.dealer_index = (self.dealer_index+1)%self.num_players
        self.current_bet = 0
        self.pot = 0
        self.num_players_remaining = self.num_players
        self.deck.reset()
        self.community_cards.clear()
        self.hands_played+=1
        self.show_player_stacks()
        print("\n")
    
    def show_hole_cards(self):
        for player in self.players:
            player.show_hole_cards()

    def show_player_stacks(self):
        print()
        for player in self.players:
            player.show_stack()

    def apply_action(self, player: Player, action: PlayerAction):
        legal_actions = self.get_legal_actions(player)

        if action.action_type not in legal_actions:
            raise ValueError("Illegal action")
            
        if action.action_type == ActionType.FOLD:
            player.fold()
            self.num_players_remaining-=1
            return

        elif action.action_type == ActionType.CHECK:
            return

        elif action.action_type == ActionType.CALL:
            amount_to_call = self.current_bet - player.current_bet
            if amount_to_call > player.chips:
                raise ValueError("Player cannot afford to call")
            self.player_bet(player, amount_to_call)
            return

        elif action.action_type == ActionType.BET:
            if action.amount <= 0:
                raise ValueError("Bet must be positive")

            if action.amount > player.chips:
                raise ValueError("Player cannot afford that bet")
            self.player_bet(player, action.amount)
            return

        elif action.action_type == ActionType.RAISE:
            if action.amount <= self.current_bet:
                raise ValueError("Raise must exceed the current bet")

            amount_to_add = action.amount - player.current_bet

            if amount_to_add > player.chips:
                raise ValueError("Player cannot afford that raise")
            
            self.player_bet(player, amount_to_add)
            return
    
    def get_legal_actions(self, player: Player) -> list[ActionType]:
        amount_to_call = self.current_bet - player.current_bet

        if amount_to_call == 0:
            return [ActionType.CHECK, ActionType.BET,]

        return [ActionType.FOLD, ActionType.CALL, ActionType.RAISE,]


if __name__ == "__main__":
    players = [Player("Colin", 2000), Player("Brooke", 2000), Player("Ella", 2000), Player("Ray", 2000), Player("Ty", 2000)]
    game = TexasHoldem(players)
    game.start_game()
