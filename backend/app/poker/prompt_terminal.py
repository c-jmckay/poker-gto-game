from .action import ActionType, PlayerAction
from .player import Player
from .state import GameState, HeroState, VillainState


def prompt_for_action(state: GameState) -> PlayerAction:
    while True:
        print(f"\n{state.hero.name}'s turn")
        print(f"Hand: {state.hero.hand}")
        print(f"Stack: {state.hero.chips}")
        print(f"Current table bet: {state.current_bet}")
        print(f"Your current bet: {state.hero.current_bet}")
        print(
            "Legal actions:",
            ", ".join(action.value for action in state.legal_actions.actions),
        )
        #print(state.legal_actions)
        choice = input("Choose an action: ").strip().lower()

        try:
            action_type = ActionType(choice)
        except ValueError:
            print("That is not a valid action.")
            continue

        if action_type not in state.legal_actions.actions:
            print("Illegal action.")
            continue
        
        if action_type in (ActionType.BET, ActionType.RAISE):
            print(f"Betting range: [{state.legal_actions.min_bet}, {state.legal_actions.max_bet}]")
            while (True):
                try:
                    amount = int(input("Enter the total bet amount: "))
                except ValueError:
                    print("Please enter a whole number.")
                    continue
                if (amount >= state.legal_actions.min_bet and amount <= state.legal_actions.max_bet or amount == state.legal_actions.max_bet):
                    print()    
                    return PlayerAction(action_type, amount)
                else:
                    print(f"Please enter a legal bet (Minimum: {state.legal_actions.min_bet}, Maximum: {state.legal_actions.max_bet}).")
        print()
        return PlayerAction(action_type)


