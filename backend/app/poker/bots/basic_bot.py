from .controller import Controller
import random
from ..action import ActionType, PlayerAction
from ..hand_evaluator import HandEvaluator
from ..hand import Hand

class BasicBot(Controller):
    def choose_action(self, state):

        hand_strength = 1
        if (len(state.board) == 0):
            if HandEvaluator.evaluate(state.hero.hand) > (2,):
                hand_strength += 2
            for card in state.hero.hand:
                if card.rank == "A":
                    hand_strength += 2
                elif card.rank == "K":
                    hand_strength += 1
        else:
            full_hand = Hand()
            for card in state.hero.hand:
                full_hand.add_card(card)
            for card in state.board:
                full_hand.add_card(card)
            hand_strength = HandEvaluator.evaluate_perms(full_hand)[0]
        
        if(state.legal_actions.min_bet>state.hero.chips):
            if (ActionType.CALL in state.legal_actions.actions and state.legal_actions.amount_to_call <= state.hero.chips):
                return PlayerAction(ActionType.CALL, 0)
            elif (ActionType.CHECK in state.legal_actions.actions):
                return PlayerAction(ActionType.CHECK, 0)
            else:
                return PlayerAction(ActionType.FOLD, 0)
        #print(f"{state.hero.name}: holding {state.hero.hand}, hand strength of {hand_strength}")
        if (hand_strength == 1):
            if (ActionType.CHECK in state.legal_actions.actions):
                return PlayerAction(ActionType.CHECK, 0)
            else:
                return PlayerAction(ActionType.FOLD, 0)
        elif (hand_strength <= 3):
            if (ActionType.BET in state.legal_actions.actions and state.legal_actions.min_bet <= 3*state.big_blind):
                return PlayerAction(ActionType.BET, state.legal_actions.min_bet)
            elif (ActionType.RAISE in state.legal_actions.actions and state.legal_actions.min_bet <= 10*state.big_blind):
                return PlayerAction(ActionType.RAISE, state.legal_actions.min_bet)
            if (ActionType.CALL in state.legal_actions.actions):
                return PlayerAction(ActionType.CALL, 0)
            elif (ActionType.CHECK in state.legal_actions.actions):
                return PlayerAction(ActionType.CHECK, 0)
            else:
                return PlayerAction(ActionType.FOLD, 0)
        else:
            return PlayerAction(ActionType.ALL_IN, 0)