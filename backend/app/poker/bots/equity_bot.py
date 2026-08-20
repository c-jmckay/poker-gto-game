from .controller import Controller
import random
from ..action import ActionType, PlayerAction
from ..hand_evaluator import HandEvaluator
from ..hand import Hand
from ..equity import EquityCalculator
from ..state import GameState, HeroState, VillainState

class EquityBot(Controller):
    RAISE_THRESHOLD = 0.7
    ALL_IN_THRESHOLD = 0.9
    
    def choose_action(self, state):
        num_opps_remaining = 0
        for villain in state.opponents:
            if villain.folded == False:
                num_opps_remaining += 1
        equity = EquityCalculator.estimate_equity(state.hero.hand, state.board, num_opps_remaining)
        self._print_info(state, equity)
        if state.legal_actions.amount_to_call == 0:
            return self._facing_no_bet(state, equity)
        else:
            return self._facing_bet(state, equity)

    def _required_equity(self, state: GameState):
        #pot odds
        return state.legal_actions.amount_to_call / (state.pot + state.legal_actions.amount_to_call)

    def _facing_bet(self, state: GameState, equity: float) -> PlayerAction:
        required_equity = self._required_equity(state)
        if (required_equity > equity):
            return PlayerAction(ActionType.FOLD)
        #player should call, but must go all in to call
        if (state.legal_actions.amount_to_call >= state.legal_actions.max_bet):
            return PlayerAction(ActionType.ALL_IN)
        #player should go all in anyway
        if (equity >= self.ALL_IN_THRESHOLD):
            return PlayerAction(ActionType.ALL_IN)
        #player should raise, but must go all in to do so
        if (ActionType.RAISE not in state.legal_actions.actions and equity >= self.RAISE_THRESHOLD):
            return PlayerAction(ActionType.ALL_IN)
        #player should raise and can do so normally
        if (ActionType.RAISE in state.legal_actions.actions and equity >= self.RAISE_THRESHOLD):
            return PlayerAction(ActionType.RAISE, state.legal_actions.min_bet)
        #player should just call and can
        return PlayerAction(ActionType.CALL)
    
    def _facing_no_bet(self, state: GameState, equity: float) -> PlayerAction:
        if (equity > self.ALL_IN_THRESHOLD):
            return PlayerAction(ActionType.ALL_IN)
        if (equity > self.RAISE_THRESHOLD):
            return PlayerAction(ActionType.BET, self._bet_size(state, equity))
        return PlayerAction(ActionType.CHECK)

    def _bet_size(self, state: GameState, equity: float) -> int:
        target = max(state.legal_actions.min_bet, state.pot//2,)
        return min(state.legal_actions.max_bet, target)
    
    def _print_info(self, state: GameState, equity: float) -> int:
        print(state.legal_actions.actions)
        print(f"Equity: {equity}")
        if (state.legal_actions.amount_to_call > 0):
            print(f"Req. Equity: {self._required_equity(state)}")