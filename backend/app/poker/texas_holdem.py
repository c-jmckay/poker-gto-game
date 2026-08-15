from .deck import Deck
from .card import Card
from .hand import Hand
from .hand_evaluator import HandEvaluator
from .player import Player
from .action import ActionType, PlayerAction, LegalActions
from collections.abc import Callable
from .prompt_terminal import prompt_for_action
from .pot import Pot
from .bots.user_controller import UserController
from .bots.random_bot import RandomBot
from .bots.basic_bot import BasicBot


class TexasHoldem:
    def __init__(self, players: list[Player]):
        self.players = players

        #cards
        self.deck = Deck()
        self.deck.shuffle()
        self.community_cards = Hand()

        #betting
        self.total_pot = 0
        self.small_blind = 10
        self.big_blind = 20
        self.current_bet = 0
        self.min_raise_incr = self.big_blind

        #order of play
        self.dealer_index = 0
        self.num_players = len(players)
        self.num_players_remaining = self.num_players
        self.num_players_unfolded = self.num_players
        self.hands_played = 0
        self.max_hands_played = 3
        self.last_to_act = self.dealer_index
        
    def start_game(self):
        while (self.num_players>1):
            self.start_hand()
            self.finish_hand()
        self.announce_action(f"{players[0]} wins!")
        self.announce_action(f"{self.hands_played} hands played.")
        return
    
    def start_hand(self):
        self.enter_blinds()
        self.deal_hole_cards()
        self.betting_round(True)
        if (self.num_players_unfolded>1):
            self.deal_flop()
            if (self.num_players_remaining>1):
                self.betting_round(False)
        if (self.num_players_unfolded>1):
            self.deal_turn()
            if (self.num_players_remaining>1):
                self.betting_round(False)
        if (self.num_players_unfolded>1):
            self.deal_river()
            if (self.num_players_remaining>1):
                self.betting_round(False)
        
        if (self.num_players_unfolded==1):
            self.uncontested_win()
        else:
            self.showdown()
        self.show_winnings()
        return
    
    def enter_blinds(self):
        self.player_bet(self.players[(self.dealer_index+1)%self.num_players], self.small_blind)
        self.announce_action(f"{self.players[(self.dealer_index+1)%self.num_players].name} enters small blind of {self.small_blind}.")
        self.player_bet(self.players[(self.dealer_index+2)%self.num_players], self.big_blind)
        self.announce_action(f"{self.players[(self.dealer_index+2)%self.num_players].name} enters big blind of {self.big_blind}.")
    
    def betting_round(self, is_preflop: bool):
        first_position = (self.dealer_index+1)%self.num_players
        self.last_to_act = self.dealer_index
        if is_preflop == True:
            first_position = (self.dealer_index+3)%self.num_players
            self.last_to_act = (self.dealer_index+2)%self.num_players

        p = first_position
        while (True):
            if players[p].folded == False and players[p].all_in == False:
                action = players[p].controller.choose_action(self, players[p])
                self.apply_action(players[p], action)

            if p == self.last_to_act or self.num_players_unfolded == 1:
                self.reset_round_bets()
                self.show_pot()
                return
            p = (p+1)%self.num_players
    
    def player_bet(self, player: Player, size: int):
        player.bet(size)
        self.total_pot+=size
        if player.current_bet > self.current_bet:
            self.last_to_act = (self.players.index(player)-1)%self.num_players
            self.current_bet = player.current_bet

    def player_fold(self, player: Player):
        player.fold()
        self.num_players_unfolded-=1
        self.num_players_remaining-=1
        return
    
    def player_all_in(self, player: Player):
        self.player_bet(player, player.chips)
        self.num_players_remaining-=1
        return

    def reset_round_bets(self):
        self.current_bet = 0
        self.min_raise_incr = self.big_blind
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
        return
    
    def deal_turn(self):
        self.deck.draw()
        self.community_cards.add_card(self.deck.draw())
        print(f"\nTurn: {self.community_cards}")
        return

    def deal_river(self):
        self.deck.draw()
        self.community_cards.add_card(self.deck.draw())
        print(f"\nRiver: {self.community_cards}")
        return

    def showdown(self):
        print("\nShowdown:")
        self.evaluate_player_hands()
        for player in self.players:
            if player.folded == False:
                print(f"{player.name} reveals {player.hand}, making {player.full_hand_rank}")
        print()
        pots: list[Pot] = self.construct_side_pots()
        for pot in pots:
            self.award_pot(pot)

    def evaluate_player_hands(self):
        for player in self.players:
            full_hand = Hand() 
            for card in self.community_cards:
                full_hand.add_card(card)
            for card in player.hand:
                full_hand.add_card(card)
            player.full_hand_rank = HandEvaluator.evaluate_seven(full_hand)

    def award_pot(self, pot: Pot):
        best_hand_rank = (0,)
        winners = []
        for player in pot.eligible_players:
            if player.full_hand_rank > best_hand_rank:
                best_hand_rank = player.full_hand_rank
                winners = [player]
            elif player.full_hand_rank == best_hand_rank:
                winners.append(player)
        if len(winners) == 1:
            winners[0].receive_winnings(pot.amount)
            #print(f"\n{winners[0].name} wins {pot.amount} with {best_hand_rank}.")
        else:
            #names = ""
            for player in winners:
                player.receive_winnings(pot.amount//len(winners))
                #names+=f"{player.name}, "
            #print(f"{names} win {pot.amount//len(winners)} each with {best_hand_rank}.")

    def construct_side_pots(self):
        levels = sorted(set(player.total_contribution for player in self.players))
        pots: list[Pot] = []
        i = 0
        last_level = 0
        while (i < len(levels)):
            if (levels[i]>0):
                new_pot_size = 0
                eligibles: list[Player] = []
                for player in self.players:
                    if player.total_contribution >= levels[i]:
                        if player.folded == False:
                            eligibles.append(player)
                        #levels[i]-last_level is the level width
                        new_pot_size += levels[i]-last_level
                pots.append(Pot(new_pot_size, eligibles))
                last_level = levels[i]
            i+=1
        #print(levels)
        #print(pots)
        return pots
        
    def uncontested_win(self):
        for i in range(self.num_players):
            if self.players[i].folded == False:
                self.players[i].receive_winnings(self.total_pot)
                print(f"\n{self.players[i].name} wins the hand before showdown.")

    def finish_hand(self):
        for player in self.players:
            player.reset_hand()
        #button moves to next player with chips
        self.dealer_index = (self.dealer_index+1)%self.num_players
        while (players[self.dealer_index].chips<=0):
            self.dealer_index = (self.dealer_index+1)%self.num_players
        self.remove_losers()
        self.current_bet = 0
        self.total_pot = 0
        self.num_players_remaining = self.num_players
        self.num_players_unfolded = self.num_players
        self.deck.reset()
        self.community_cards.clear()
        self.hands_played+=1
        self.show_player_stacks()
        print("\n")

    def remove_losers(self):
        for player in self.players:
            if player.chips <= 0:
                self.announce_action(f"{player} leaves the table.")
                players.remove(player)
                self.num_players -=1
                self.remove_losers()
    
    def show_winnings(self):
        for player in self.players:
            if player.recent_winnings > 0:
                print(f"{player.name} wins {player.recent_winnings}.")
        
    def show_hole_cards(self):
        for player in self.players:
            player.show_hole_cards()

    def show_player_stacks(self):
        print()
        for player in self.players:
            player.show_stack()
    
    def show_pot(self):
        self.announce_action(f"\nThe pot contains {self.total_pot} chips.")

    def announce_action(self, message: str):
        print(message)
        
    def apply_action(self, player: Player, action: PlayerAction):
        legal_actions = self.get_legal_actions(player)

        if action.action_type not in legal_actions.actions:
            raise ValueError("Illegal action")
            
        if action.action_type == ActionType.FOLD:
            self.player_fold(player)
            self.announce_action(f"{player} folds.")
            return

        elif action.action_type == ActionType.CHECK:
            self.announce_action(f"{player} checks.")
            return

        elif action.action_type == ActionType.CALL:
            amount_to_call = self.current_bet - player.current_bet
            if amount_to_call >= player.chips:
                self.player_all_in(player)
                self.announce_action(f"{player} goes all in for {player.current_bet} chips.")
            else:
                self.player_bet(player, amount_to_call)
                self.announce_action(f"{player} calls.")
            return

        elif action.action_type == ActionType.BET:
            if action.amount <= 0:
                raise ValueError(f"Bet {action.amount} must be positive")
            if action.amount > player.chips:
                raise ValueError(f"Player cannot afford that bet {action.amount}")
            
            if action.amount == player.chips:
                self.player_all_in(player)
                self.announce_action(f"{player} goes all in for {player.current_bet} chips.")
                return
            if action.amount >= legal_actions.min_bet:
                self.min_raise_incr = action.amount - self.current_bet
                self.player_bet(player, action.amount)
                self.announce_action(f"{player} bets {player.current_bet} chips.")
            else: 
                raise ValueError(f"Bet {action.amount} does not exceed minimum raise {legal_actions.min_bet}")
            return

        elif action.action_type == ActionType.RAISE:
            if action.amount <= self.current_bet:
                raise ValueError(f"Raise {amount_to_add} must exceed the current bet {self.current_bet}")
            amount_to_add = action.amount - player.current_bet
            if amount_to_add > player.chips:
                raise ValueError(f"Player cannot afford that raise {amount_to_add}")
            if amount_to_add == player.chips:
                self.min_raise_incr = action.amount - self.current_bet
                self.player_all_in(player)
                self.announce_action(f"{player} goes all in for {player.current_bet} chips.")
                return
            if action.amount >= legal_actions.min_bet:
                self.min_raise_incr = action.amount - self.current_bet
                self.player_bet(player, amount_to_add)
                self.announce_action(f"{player} raises to {player.current_bet} chips.")
            else:
                raise ValueError(f"Bet {action.amount} does not exceed minimum raise {legal_actions.min_bet}")
            return

        elif action.action_type == ActionType.ALL_IN:
            self.min_raise_incr = max(player.chips - self.current_bet, self.min_raise_incr)
            self.player_all_in(player)
            self.announce_action(f"{player} goes all in for {player.current_bet} chips.")
    
    def get_legal_actions(self, player: Player) -> LegalActions:
        amount_to_call = self.current_bet - player.current_bet
        min_bet = self.min_raise_incr + player.current_bet
        min_raise = self.min_raise_incr + self.current_bet
        max_bet = player.chips + player.current_bet

        #either last position on blind or no one has bet yet
        if amount_to_call == 0:
            return LegalActions([ActionType.CHECK, ActionType.BET, ActionType.ALL_IN], 
                                0, min_bet, max_bet)
        #player faces a bet, cannot afford calling price
        elif amount_to_call >= player.chips:
            return LegalActions([ActionType.FOLD, ActionType.ALL_IN], amount_to_call, min_raise, max_bet)
        #player faces a bet, cannot afford to raise again without going all in
        #say in h2h you have 250, raise to 100, v raises to 200, then max_bet is 250 and min_raise is 300
        elif min_raise > max_bet:
            return LegalActions([ActionType.FOLD, ActionType.CALL, ActionType.ALL_IN], amount_to_call, min_raise, max_bet)
        #player faces a bet, can afford to raise
        else:
            return LegalActions([ActionType.FOLD, ActionType.CALL, ActionType.RAISE, ActionType.ALL_IN], 
                                amount_to_call, min_raise, max_bet)

if __name__ == "__main__":
    #players = [Player("Colin", 500, BasicBot()), 
    #           Player("Brooke", 5000, UserController()), 
    #           Player("Ella", 3000, BasicBot()), 
    #           Player("Ray", 2000, BasicBot()), 
    #           Player("Ty", 1000, BasicBot())]
    players = [Player("Colin", 1000, BasicBot()), Player("Pat", 1000, BasicBot()), Player("Mikey", 1000, BasicBot()), Player("Noah", 1000, BasicBot())]
    #players = [Player("Rick", 1000, UserController()), Player("Morty", 1000, RandomBot())]
    game = TexasHoldem(players)
    game.start_game()
