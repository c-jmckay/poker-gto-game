from .action import ActionType, PlayerAction
from .player import Player


def prompt_for_action(game, player: Player) -> PlayerAction:
    while True:
        legal_actions = game.get_legal_actions(player)
        
        print(f"\n{player.name}'s turn")
        print(f"Hand: {player.hand}")
        print(f"Stack: {player.chips}")
        print(f"Current table bet: {game.current_bet}")
        print(f"Your current bet: {player.current_bet}")
        print(
            "Legal actions:",
            ", ".join(action.value for action in legal_actions.actions),
        )
        #print(legal_actions)
        choice = input("Choose an action: ").strip().lower()

        try:
            action_type = ActionType(choice)
        except ValueError:
            print("That is not a valid action.")
            continue

        if action_type not in legal_actions.actions:
            print("Illegal action.")
            continue
        
        if action_type in (ActionType.BET, ActionType.RAISE):
            print(f"Betting range: [{legal_actions.min_bet}, {legal_actions.max_bet}]")
            while (True):
                try:
                    amount = int(input("Enter the total bet amount: "))
                except ValueError:
                    print("Please enter a whole number.")
                    continue
                if (amount >= legal_actions.min_bet and amount <= legal_actions.max_bet or amount == legal_actions.max_bet):
                    print()    
                    return PlayerAction(action_type, amount)
                else:
                    print(f"Please enter a legal bet (Minimum: {legal_actions.min_bet}, Maximum: {legal_actions.max_bet}).")
        print()
        return PlayerAction(action_type)


