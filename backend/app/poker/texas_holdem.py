from .deck import Deck
from .card import Card
from .hand import Hand
from .hand_evaluator import HandEvaluator
from .player import Player
from .action import ActionType, PlayerAction, LegalActions
from copy import deepcopy
from .prompt_terminal import prompt_for_action
from .pot import Pot
from .bots.user_controller import UserController
from .bots.random_bot import RandomBot
from .bots.basic_bot import BasicBot
from .bots.equity_bot import EquityBot
from .state import GameState, HeroState, VillainState


class TexasHoldem:
    def __init__(self, players: list[Player]):
        self.players = players
        for seat_id, player in enumerate(players):
            player.seat_id = seat_id

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
        self._dealer_index = 0
        self.num_players = len(players)
        self.num_players_remaining = self.num_players
        self.num_players_unfolded = self.num_players
        self.hands_played = 0
        self.max_hands_played = 3
        self._last_to_act_index = self._dealer_index
        self.is_heads_up = (self.num_players == 2)
        
        self.street = "ready"
        self._acting_index = None

    _snapshot_fields = (
        "street", "hands_played",
        "small_blind", "big_blind", "total_pot", "current_bet", "min_raise_incr",
        "num_players_remaining", "num_players_unfolded",
    )
    _player_fields = (
        "folded", "all_in", "current_bet", "total_contribution", "recent_winnings",
    )
    _controllers = {cls.__name__: cls for cls in
                    (UserController, BasicBot, EquityBot, RandomBot)}

    def to_snapshot(self):
        """Private JSON-compatible state, including all hidden cards."""
        def cards(collection):
            return [[card.rank, card.suit] for card in collection]

        players = []
        for player in self.players:
            controller = player.controller
            kind = None if controller is None else type(controller).__name__
            if controller is not None and self._controllers.get(kind) is not type(controller):
                raise ValueError(f"Unsupported controller: {kind}")
            fields = {key: getattr(player, key) for key in self._player_fields}
            players.append(dict(fields, seat_id=player.seat_id, name=player.name, chips=player.chips,
                                controller=kind, hand=cards(player.hand),
                                full_hand_rank=list(player.full_hand_rank)))
        table = {key: getattr(self, key) for key in self._snapshot_fields}
        table.update(acting_index=self._acting_index, dealer_index=self._dealer_index,
                     last_to_act=self._last_to_act_index)
        return {"version": 2, "players": players, "deck": cards(self.deck),
                "board": cards(self.community_cards),
                "table": table}

    @classmethod
    def from_snapshot(cls, snapshot):
        """Restore a trusted server-side snapshot without replaying actions."""
        if snapshot["version"] not in (1, 2):
            raise ValueError("Unknown poker snapshot version")
        players = []
        for data in snapshot["players"]:
            kind = data["controller"]
            controller = cls._controllers[kind]() if kind is not None else None
            player = Player(data["name"], data["chips"], controller)
            player.hand.cards = [Card(*card) for card in data["hand"]]
            player.full_hand_rank = tuple(data["full_hand_rank"])
            for key in cls._player_fields:
                setattr(player, key, data[key])
            players.append(player)
        game = cls(players)
        table = snapshot["table"]
        if snapshot["version"] == 2:
            ids = [data["seat_id"] for data in snapshot["players"]]
            if any(type(i) is not int or i < 0 for i in ids) or len(set(ids)) != len(ids):
                raise ValueError("Invalid seat IDs in snapshot")
            for player, seat_id in zip(players, ids):
                player.seat_id = seat_id
            game._acting_index = table["acting_index"]
        else:
            # Older saves only recorded positions in the surviving roster.
            game._acting_index = table["acting_seat"]
        game._dealer_index = table["dealer_index"]
        game._last_to_act_index = table["last_to_act"]
        game.deck.cards = [Card(*card) for card in snapshot["deck"]]
        game.community_cards.cards = [Card(*card) for card in snapshot["board"]]
        for key in cls._snapshot_fields:
            setattr(game, key, snapshot["table"][key])
        return game

    def start_game(self):
        while self.num_players > 1:
            self.start_hand()
            while (seat := self.advance_until_decision()) is not None:
                action = prompt_for_action(self.view_for(seat))
                self.submit_action(seat, action)
            self.finish_hand()
        self.announce_action(f"{self.players[0]} wins!")

    def start_hand(self):
        """Deal a hand and initialize its first betting decision."""
        if self.street != "ready" or self.num_players < 2:
            raise ValueError("A new hand cannot start now")
        self.street = "preflop"
        self.enter_blinds()
        self.deal_hole_cards()
        self.betting_round(True)

    def enter_blinds(self):
        sb_index = (self._dealer_index+1)%self.num_players
        bb_index = (self._dealer_index + 2) % self.num_players
        if self.is_heads_up:
            sb_index = self._dealer_index
            bb_index = (self._dealer_index + 1) % 2
        sb_amount = min(self.small_blind, self.players[sb_index].chips)
        bb_amount = min(self.big_blind, self.players[bb_index].chips)
        self.player_bet(self.players[sb_index], sb_amount)
        self.announce_action(f"{self.players[sb_index].name} enters small blind of {sb_amount}.")
        self.player_bet(self.players[bb_index], bb_amount)
        self.announce_action(f"{self.players[bb_index].name} enters big blind of {bb_amount}.")
    
    def create_game_state(self, hero: Player):
        hero_state = HeroState(hero.seat_id, hero.name, hero.chips, hero.current_bet, hero.hand, hero.folded, hero.all_in)
        villain_states = []
        for player in self.players:
            if (player != hero):
                villain_state = VillainState(player.seat_id, player.name, player.chips, player.current_bet, player.folded, player.all_in)
                villain_states.append(villain_state)
        return GameState(hero_state, villain_states, self.community_cards, self.total_pot, self.dealer_seat_id, self.small_blind, self.big_blind, self.get_legal_actions(hero)
                         if self.acting_seat_id == hero.seat_id else LegalActions([], 0),
                         self.current_bet, self.street, self.acting_seat_id)

    def betting_round(self, is_preflop: bool):
        """Initialize the round cursor without asking any controller for input."""
        first = self._dealer_index + 1
        if is_preflop:
            first = self._dealer_index if self.is_heads_up else self._dealer_index + 3
        self._last_to_act_index = (first - 1) % self.num_players
        self._select_actor(first % self.num_players)

    def _select_actor(self, seat):
        self._acting_index = None
        while self.num_players_unfolded > 1:
            player = self.players[seat]
            if not player.folded and not player.all_in:
                if self.num_players_remaining > 1 or player.current_bet < self.current_bet:
                    self._acting_index = seat
                    return
            if seat == self._last_to_act_index:
                return
            seat = (seat + 1) % self.num_players

    @property
    def dealer_seat_id(self):
        return self.players[self._dealer_index].seat_id

    @property
    def acting_seat_id(self):
        if self._acting_index is None:
            return None
        return self.players[self._acting_index].seat_id

    def _index_for_seat(self, seat_id):
        if type(seat_id) is int:
            for index, player in enumerate(self.players):
                if player.seat_id == seat_id:
                    return index
        raise ValueError("Unknown seat")

    def view_for(self, seat_id):
        """Return a detached view for an active table seat ID."""
        player = self.players[self._index_for_seat(seat_id)]
        return deepcopy(self.create_game_state(player))

    def submit_action(self, seat_id, action):
        index = self._index_for_seat(seat_id)
        if index != self._acting_index:
            raise ValueError("It is not this seat's turn")
        if action.action_type in (ActionType.BET, ActionType.RAISE) and type(action.amount) is not int:
            raise ValueError("Wagers must be whole chips")
        self.apply_action(self.players[index], action)
        self._acting_index = None
        if index != self._last_to_act_index:
            self._select_actor((index + 1) % self.num_players)

    def advance_until_decision(self):
        """Run automatic transitions. Return a human seat or None at hand end."""
        if self.street == "ready":
            self.start_hand()
        streets = {"preflop": ("flop", self.deal_flop),
                   "flop": ("turn", self.deal_turn),
                   "turn": ("river", self.deal_river)}
        while self.street != "complete":
            seat = self.acting_seat_id
            if seat is not None:
                controller = self.players[self._acting_index].controller
                if controller is None or isinstance(controller, UserController):
                    return seat
                self.submit_action(seat, controller.choose_action(self.view_for(seat)))
                continue
            self.reset_round_bets()
            if self.num_players_unfolded == 1 or self.street == "river":
                if self.num_players_unfolded == 1:
                    self.uncontested_win()
                else:
                    self.showdown()
                self.show_winnings()
                self.street = "complete"
            else:
                self.street, deal = streets[self.street]
                deal()
                self.betting_round(False)
        return None

    def player_bet(self, player: Player, size: int):
        player.bet(size)
        self.total_pot+=size
        if player.current_bet > self.current_bet:
            self._last_to_act_index = (self.players.index(player)-1)%self.num_players
            self.current_bet = player.current_bet
        if (player.chips == 0):
            self.num_players_remaining-=1

    def player_fold(self, player: Player):
        player.fold()
        self.num_players_unfolded-=1
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
            p = (self._dealer_index+1+i)%(self.num_players)
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
            player.full_hand_rank = HandEvaluator.evaluate_perms(full_hand)

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
        if self.street != "complete":
            raise ValueError("The hand is still in progress")
        self.street = "ready"
        for player in self.players:
            player.reset_hand()
        #button moves to next player with chips
        self._dealer_index = (self._dealer_index+1)%self.num_players
        while (self.players[self._dealer_index].chips<=0):
            self._dealer_index = (self._dealer_index+1)%self.num_players
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
        dealer = self.players[self._dealer_index]
        self.players = [player for player in self.players if player.chips > 0]
        self.num_players = len(self.players)
        self.is_heads_up = (self.num_players == 2)
        self._dealer_index = self.players.index(dealer)
    
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
        #print(action)
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
                self.player_bet(player, player.chips)
                self.announce_action(f"{player} goes all in for {player.current_bet} chips.")
            else:
                self.player_bet(player, amount_to_call)
                self.announce_action(f"{player} calls.")
            return

        elif action.action_type == ActionType.BET:
            amount_to_add = action.amount - player.current_bet
            if not 0 < amount_to_add <= player.chips:
                raise ValueError("Bet outside stack limits")
            if action.amount < legal_actions.min_bet and amount_to_add != player.chips:
                raise ValueError("Bet below minimum")
            self.min_raise_incr = max(self.min_raise_incr, action.amount - self.current_bet)
            self.player_bet(player, amount_to_add)
            self.announce_action(f"{player} bets {player.current_bet} chips.")
            return

        elif action.action_type == ActionType.RAISE:
            if action.amount <= self.current_bet:
                raise ValueError(f"Raise {action.amount} must exceed the current bet {self.current_bet}")
            amount_to_add = action.amount - player.current_bet
            if amount_to_add > player.chips:
                raise ValueError(f"Player cannot afford that raise {amount_to_add}")
            if amount_to_add == player.chips:
                self.min_raise_incr = action.amount - self.current_bet
                self.player_bet(player, player.chips)
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
            self.player_bet(player, player.chips)
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
        elif amount_to_call > player.chips:
            return LegalActions([ActionType.FOLD, ActionType.ALL_IN], amount_to_call, min_raise, max_bet)
        #player faces a bet, cannot afford to raise again without going all in
        elif min_raise > max_bet:
            return LegalActions([ActionType.FOLD, ActionType.CALL, ActionType.ALL_IN], amount_to_call, min_raise, max_bet)
        #player faces a bet, can afford to raise
        else:
            return LegalActions([ActionType.FOLD, ActionType.CALL, ActionType.RAISE, ActionType.ALL_IN], 
                                amount_to_call, min_raise, max_bet)

if __name__ == "__main__":
    #players = [Player("Colin", 1000, UserController()), Player("Brooke", 1000, BasicBot()), Player("Ella", 1000, BasicBot()), Player("Ray", 1000, BasicBot()), Player("Ty", 1000, BasicBot())]
    #players = [Player("Colin", 10000, BasicBot()), Player("Pat", 1000, BasicBot()), Player("Mikey", 1000, BasicBot()), Player("Noah", 1000, BasicBot()), Player("Ethan", 1000, BasicBot()), Player("RV", 1000, BasicBot())]
    players = [Player("Rick", 1000, EquityBot()), Player("Morty", 1000, EquityBot()), Player("Jerry", 1000, EquityBot())]
    game = TexasHoldem(players)
    game.start_game()
