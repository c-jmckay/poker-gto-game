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
            ", ".join(action.value for action in legal_actions),
        )

        choice = input("Choose an action: ").strip().lower()

        try:
            action_type = ActionType(choice)
        except ValueError:
            print("That is not a valid action.")
            continue

        if action_type not in legal_actions:
            print("Illegal action.")
            continue

        if action_type in (ActionType.BET, ActionType.RAISE):
            try:
                amount = int(input("Enter the total bet amount: "))
            except ValueError:
                print("Please enter a whole number.")
                continue
            print()    
            return PlayerAction(action_type, amount)
        print()
        return PlayerAction(action_type)


