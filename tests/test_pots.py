from backend.app.poker.player import Player
from backend.app.poker.texas_holdem import TexasHoldem

def print_pots(pots):
    for pot in pots:
        print(pot.amount, pot.eligible_players)

def make_game():
    players = [
        Player("Adam", 1000),
        Player("Beth", 1000),
        Player("Colin", 1000),
    ]
    return TexasHoldem(players)


def test_single_pot():
    game = make_game()

    game.players[0].total_contribution = 100
    game.players[1].total_contribution = 100
    game.players[2].total_contribution = 100

    pots = game.construct_side_pots()

    assert len(pots) == 1
    assert pots[0].amount == 300
    assert pots[0].eligible_players == game.players

def test_one_side_pot():
    game = make_game()

    game.players[0].total_contribution = 200
    game.players[1].total_contribution = 500
    game.players[2].total_contribution = 500

    pots = game.construct_side_pots()

    assert len(pots) == 2

    assert pots[0].amount == 600
    assert pots[1].amount == 600

    assert pots[0].eligible_players == game.players
    assert pots[1].eligible_players == game.players[1:]

def test_folded_player_not_eligible():
    game = make_game()

    adam, beth, colin = game.players

    adam.total_contribution = 200
    beth.total_contribution = 500
    colin.total_contribution = 500

    beth.fold()

    pots = game.construct_side_pots()

    assert len(pots) == 2

    assert pots[0].amount == 600
    assert pots[0].eligible_players == [adam, colin]

    assert pots[1].amount == 600
    assert pots[1].eligible_players == [colin]

def test_zero_contributions():
    game = make_game()

    pots = game.construct_side_pots()

    assert len(pots) == 0


def test_one_short_stack():
    game = make_game()

    adam, beth, colin = game.players

    adam.total_contribution = 50
    beth.total_contribution = 100
    colin.total_contribution = 100

    pots = game.construct_side_pots()

    assert len(pots) == 2

    assert pots[0].amount == 150
    assert pots[0].eligible_players == [adam, beth, colin]

    assert pots[1].amount == 100
    assert pots[1].eligible_players == [beth, colin]


def test_three_different_contribution_levels():
    game = make_game()

    adam, beth, colin = game.players

    adam.total_contribution = 100
    beth.total_contribution = 300
    colin.total_contribution = 600

    pots = game.construct_side_pots()

    assert len(pots) == 3

    assert pots[0].amount == 300
    assert pots[0].eligible_players == [adam, beth, colin]

    assert pots[1].amount == 400
    assert pots[1].eligible_players == [beth, colin]

    assert pots[2].amount == 300
    assert pots[2].eligible_players == [colin]


def test_four_players_multiple_side_pots():
    players = [
        Player("Adam", 1000),
        Player("Beth", 1000),
        Player("Colin", 1000),
        Player("David", 1000),
    ]

    game = TexasHoldem(players)

    adam, beth, colin, david = game.players

    adam.total_contribution = 100
    beth.total_contribution = 300
    colin.total_contribution = 600
    david.total_contribution = 600

    pots = game.construct_side_pots()

    assert len(pots) == 3

    assert pots[0].amount == 400
    assert pots[0].eligible_players == [adam, beth, colin, david]

    assert pots[1].amount == 600
    assert pots[1].eligible_players == [beth, colin, david]

    assert pots[2].amount == 600
    assert pots[2].eligible_players == [colin, david]


def test_player_with_zero_contribution_not_in_pot():
    game = make_game()

    adam, beth, colin = game.players

    adam.total_contribution = 0
    beth.total_contribution = 100
    colin.total_contribution = 100

    pots = game.construct_side_pots()

    assert len(pots) == 1

    assert pots[0].amount == 200
    assert pots[0].eligible_players == [beth, colin]


def test_folded_player_still_adds_chips_to_pot():
    game = make_game()

    adam, beth, colin = game.players

    adam.total_contribution = 100
    beth.total_contribution = 100
    colin.total_contribution = 100

    beth.folded = True

    pots = game.construct_side_pots()

    assert len(pots) == 1
    assert pots[0].amount == 300
    assert pots[0].eligible_players == [adam, colin]


def test_folded_player_with_largest_contribution():
    game = make_game()

    adam, beth, colin = game.players

    adam.total_contribution = 100
    beth.total_contribution = 500
    colin.total_contribution = 300

    beth.folded = True

    pots = game.construct_side_pots()

    assert len(pots) == 3

    assert pots[0].amount == 300
    assert pots[0].eligible_players == [adam, colin]

    assert pots[1].amount == 400
    assert pots[1].eligible_players == [colin]

    assert pots[2].amount == 200
    assert pots[2].eligible_players == []


def test_multiple_folded_players():
    players = [
        Player("Adam", 1000),
        Player("Beth", 1000),
        Player("Colin", 1000),
        Player("David", 1000),
    ]

    game = TexasHoldem(players)

    adam, beth, colin, david = game.players

    adam.total_contribution = 100
    beth.total_contribution = 300
    colin.total_contribution = 300
    david.total_contribution = 300

    beth.folded = True
    colin.folded = True

    pots = game.construct_side_pots()

    assert len(pots) == 2

    assert pots[0].amount == 400
    assert pots[0].eligible_players == [adam, david]

    assert pots[1].amount == 600
    assert pots[1].eligible_players == [david]


def test_identical_middle_contributions():
    players = [
        Player("Adam", 1000),
        Player("Beth", 1000),
        Player("Colin", 1000),
        Player("David", 1000),
    ]

    game = TexasHoldem(players)

    adam, beth, colin, david = game.players

    adam.total_contribution = 100
    beth.total_contribution = 300
    colin.total_contribution = 300
    david.total_contribution = 600

    pots = game.construct_side_pots()

    assert len(pots) == 3

    assert pots[0].amount == 400
    assert pots[0].eligible_players == [adam, beth, colin, david]

    assert pots[1].amount == 600
    assert pots[1].eligible_players == [beth, colin, david]

    assert pots[2].amount == 300
    assert pots[2].eligible_players == [david]


def test_chip_conservation():
    players = [
        Player("Adam", 1000),
        Player("Beth", 1000),
        Player("Colin", 1000),
        Player("David", 1000),
    ]

    game = TexasHoldem(players)

    contributions = [100, 300, 600, 600]

    for player, contribution in zip(game.players, contributions):
        player.total_contribution = contribution

    pots = game.construct_side_pots()

    total_contributed = sum(contributions)
    total_in_pots = sum(pot.amount for pot in pots)

    assert total_in_pots == total_contributed