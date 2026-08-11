from backend.app.poker.card import Card
from backend.app.poker.player import Player
from backend.app.poker.texas_holdem import TexasHoldem


def give_cards(player: Player, *cards: tuple[str, str]) -> None:
    for rank, suit in cards:
        player.draw_card(Card(rank, suit))


def set_board(game: TexasHoldem, *cards: tuple[str, str]) -> None:
    for rank, suit in cards:
        game.community_cards.add_card(Card(rank, suit))


def make_three_player_game() -> TexasHoldem:
    players = [
        Player("Adam", 500),
        Player("Beth", 1000),
        Player("Colin", 2000),
    ]
    return TexasHoldem(players)

def test_showdown_single_winner() -> None:
    game = make_three_player_game()
    adam, beth, colin = game.players

    # Each player has already contributed 100.
    adam.chips = 400
    beth.chips = 900
    colin.chips = 1900

    adam.total_contribution = 100
    beth.total_contribution = 100
    colin.total_contribution = 100

    set_board(
        game,
        ("2", "Clubs"),
        ("4", "Diamonds"),
        ("7", "Hearts"),
        ("9", "Spades"),
        ("Q", "Clubs"),
    )

    give_cards(adam, ("A", "Spades"), ("A", "Hearts"))
    give_cards(beth, ("K", "Spades"), ("K", "Hearts"))
    give_cards(colin, ("J", "Spades"), ("10", "Hearts"))

    game.showdown()

    # Adam wins the 300-chip pot.
    assert adam.chips == 700
    assert beth.chips == 900
    assert colin.chips == 1900

def test_three_way_split_pot() -> None:
    game = make_three_player_game()
    adam, beth, colin = game.players

    adam.chips = 400
    beth.chips = 900
    colin.chips = 1900

    for player in game.players:
        player.total_contribution = 100

    set_board(
        game,
        ("10", "Hearts"),
        ("J", "Hearts"),
        ("Q", "Hearts"),
        ("K", "Hearts"),
        ("A", "Hearts"),
    )

    give_cards(adam, ("2", "Clubs"), ("3", "Clubs"))
    give_cards(beth, ("4", "Diamonds"), ("5", "Diamonds"))
    give_cards(colin, ("6", "Spades"), ("7", "Spades"))

    game.showdown()

    # 300 / 3 = 100 each
    assert adam.chips == 500
    assert beth.chips == 1000
    assert colin.chips == 2000

def test_all_in_main_pot_and_side_pot_different_winners() -> None:
    players = [
        Player("Adam", 100),
        Player("Beth", 500),
        Player("Colin", 1000),
    ]
    game = TexasHoldem(players)

    adam, beth, colin = game.players

    # Chips remaining after contributions.
    adam.chips = 0
    beth.chips = 200
    colin.chips = 700

    adam.total_contribution = 100
    beth.total_contribution = 300
    colin.total_contribution = 300

    adam.all_in = True

    set_board(
        game,
        ("2", "Clubs"),
        ("4", "Diamonds"),
        ("7", "Hearts"),
        ("9", "Spades"),
        ("Q", "Clubs"),
    )

    # Adam > Colin > Beth
    give_cards(adam, ("A", "Spades"), ("A", "Hearts"))
    give_cards(beth, ("10", "Spades"), ("10", "Hearts"))
    give_cards(colin, ("K", "Spades"), ("K", "Hearts"))

    game.showdown()

    # Main pot: 100 * 3 = 300 -> Adam
    # Side pot: 200 * 2 = 400 -> Colin
    assert adam.chips == 300
    assert beth.chips == 200
    assert colin.chips == 1100

def test_multiple_all_ins_multiple_side_pots() -> None:
    players = [
        Player("Adam", 100),
        Player("Beth", 300),
        Player("Colin", 600),
        Player("David", 1000),
    ]
    game = TexasHoldem(players)

    adam, beth, colin, david = game.players

    adam.chips = 0
    beth.chips = 0
    colin.chips = 0
    david.chips = 400

    adam.total_contribution = 100
    beth.total_contribution = 300
    colin.total_contribution = 600
    david.total_contribution = 600

    adam.all_in = True
    beth.all_in = True
    colin.all_in = True

    set_board(
        game,
        ("2", "Clubs"),
        ("4", "Diamonds"),
        ("7", "Hearts"),
        ("9", "Spades"),
        ("Q", "Clubs"),
    )

    # Strength order:
    # Adam > Beth > Colin > David
    give_cards(adam, ("A", "Spades"), ("A", "Hearts"))
    give_cards(beth, ("K", "Spades"), ("K", "Hearts"))
    give_cards(colin, ("J", "Spades"), ("J", "Hearts"))
    give_cards(david, ("10", "Spades"), ("10", "Hearts"))

    game.showdown()

    # Main:       4 * 100 = 400 -> Adam
    # Side pot 1: 3 * 200 = 600 -> Beth
    # Side pot 2: 2 * 300 = 600 -> Colin

    assert adam.chips == 400
    assert beth.chips == 600
    assert colin.chips == 600
    assert david.chips == 400

def test_folded_player_contributes_but_cannot_win() -> None:
    players = [
        Player("Adam", 100),
        Player("Beth", 500),
        Player("Colin", 500),
    ]
    game = TexasHoldem(players)

    adam, beth, colin = game.players

    adam.chips = 0
    beth.chips = 200
    colin.chips = 200

    adam.total_contribution = 100
    beth.total_contribution = 300
    colin.total_contribution = 300

    adam.all_in = True
    beth.folded = True

    set_board(
        game,
        ("2", "Clubs"),
        ("4", "Diamonds"),
        ("7", "Hearts"),
        ("9", "Spades"),
        ("Q", "Clubs"),
    )

    # Adam wins main pot.
    give_cards(adam, ("A", "Spades"), ("A", "Hearts"))

    # Beth actually has the strongest hand, but folded.
    give_cards(beth, ("Q", "Spades"), ("Q", "Hearts"))

    give_cards(colin, ("K", "Spades"), ("K", "Hearts"))

    game.showdown()

    # Main = 300 -> Adam
    # Side = 400 -> Colin automatically, because Beth folded
    assert adam.chips == 300
    assert beth.chips == 200
    assert colin.chips == 600

def test_split_main_pot_with_side_pot() -> None:
    players = [
        Player("Adam", 100),
        Player("Beth", 500),
        Player("Colin", 500),
    ]
    game = TexasHoldem(players)

    adam, beth, colin = game.players

    adam.chips = 0
    beth.chips = 200
    colin.chips = 200

    adam.total_contribution = 100
    beth.total_contribution = 300
    colin.total_contribution = 300

    adam.all_in = True

    set_board(
        game,
        ("2", "Clubs"),
        ("4", "Diamonds"),
        ("7", "Hearts"),
        ("9", "Spades"),
        ("10", "Clubs"),
    )

    # Adam and Beth both have A-K high.
    give_cards(adam, ("A", "Spades"), ("K", "Hearts"))
    give_cards(beth, ("A", "Hearts"), ("K", "Spades"))

    # Colin loses to Beth in the side pot.
    give_cards(colin, ("Q", "Spades"), ("J", "Hearts"))

    game.showdown()

    # Main pot = 300.
    # Adam and Beth split it: 150 each.
    #
    # Side pot = 400.
    # Beth beats Colin and gets all 400.

    assert adam.chips == 150
    assert beth.chips == 750
    assert colin.chips == 200

def test_shortest_stack_can_win_entire_main_pot() -> None:
    players = [
        Player("Adam", 50),
        Player("Beth", 1000),
        Player("Colin", 2000),
    ]
    game = TexasHoldem(players)

    adam, beth, colin = game.players

    adam.chips = 0
    beth.chips = 950
    colin.chips = 1950

    adam.total_contribution = 50
    beth.total_contribution = 50
    colin.total_contribution = 50

    adam.all_in = True

    set_board(
        game,
        ("2", "Clubs"),
        ("4", "Diamonds"),
        ("7", "Hearts"),
        ("9", "Spades"),
        ("Q", "Clubs"),
    )

    give_cards(adam, ("A", "Spades"), ("A", "Hearts"))
    give_cards(beth, ("K", "Spades"), ("K", "Hearts"))
    give_cards(colin, ("J", "Spades"), ("J", "Hearts"))

    game.showdown()

    assert adam.chips == 150
    assert beth.chips == 950
    assert colin.chips == 1950

def test_showdown_conserves_all_chips() -> None:
    players = [
        Player("Adam", 100),
        Player("Beth", 300),
        Player("Colin", 600),
        Player("David", 1000),
    ]
    game = TexasHoldem(players)

    adam, beth, colin, david = game.players

    adam.chips = 0
    beth.chips = 0
    colin.chips = 0
    david.chips = 400

    adam.total_contribution = 100
    beth.total_contribution = 300
    colin.total_contribution = 600
    david.total_contribution = 600

    initial_total = (
        sum(player.chips for player in game.players)
        + sum(player.total_contribution for player in game.players)
    )

    set_board(
        game,
        ("2", "Clubs"),
        ("4", "Diamonds"),
        ("7", "Hearts"),
        ("9", "Spades"),
        ("Q", "Clubs"),
    )

    give_cards(adam, ("A", "Spades"), ("A", "Hearts"))
    give_cards(beth, ("K", "Spades"), ("K", "Hearts"))
    give_cards(colin, ("J", "Spades"), ("J", "Hearts"))
    give_cards(david, ("10", "Spades"), ("10", "Hearts"))

    game.showdown()

    final_total = sum(player.chips for player in game.players)

    assert final_total == initial_total