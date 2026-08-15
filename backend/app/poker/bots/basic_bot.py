from .controller import Controller
import random
from ..action import ActionType, PlayerAction
from ..hand_evaluator import HandEvaluator
from ..hand import Hand

class BasicBot(Controller):
    def choose_action(self, game, player):
        legal_actions = game.get_legal_actions(player)

        hand_strength = 1
        if (len(game.community_cards) == 0):
            if HandEvaluator.evaluate(player.hand) > (2,):
                hand_strength += 2
            for card in player.hand:
                if card.rank == "A":
                    hand_strength += 2
                elif card.rank == "K":
                    hand_strength += 1
        else:
            full_hand = Hand()
            for card in player.hand:
                full_hand.add_card(card)
            for card in game.community_cards:
                full_hand.add_card(card)
            hand_strength = HandEvaluator.evaluate_seven(full_hand)[0]
        
        if(legal_actions.min_bet>player.chips):
            if (ActionType.CALL in legal_actions.actions and legal_actions.amount_to_call <= player.chips):
                return PlayerAction(ActionType.CALL, 0)
            elif (ActionType.CHECK in legal_actions.actions):
                return PlayerAction(ActionType.CHECK, 0)
            else:
                return PlayerAction(ActionType.FOLD, 0)
        #print(f"{player.name}: holding {player.hand}, hand strength of {hand_strength}")
        if (hand_strength == 1):
            if (ActionType.CHECK in legal_actions.actions):
                return PlayerAction(ActionType.CHECK, 0)
            else:
                return PlayerAction(ActionType.FOLD, 0)
        elif (hand_strength <= 3):
            if (ActionType.BET in legal_actions.actions and legal_actions.min_bet <= 3*game.big_blind):
                return PlayerAction(ActionType.BET, legal_actions.min_bet)
            elif (ActionType.RAISE in legal_actions.actions and legal_actions.min_bet <= 10*game.big_blind):
                return PlayerAction(ActionType.RAISE, legal_actions.min_bet)
            if (ActionType.CALL in legal_actions.actions):
                return PlayerAction(ActionType.CALL, 0)
            elif (ActionType.CHECK in legal_actions.actions):
                return PlayerAction(ActionType.CHECK, 0)
            else:
                return PlayerAction(ActionType.FOLD, 0)
        else:
            return PlayerAction(ActionType.ALL_IN, 0)