import uuid

from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_GET, require_http_methods

from backend.app.poker.bots.basic_bot import BasicBot
from backend.app.poker.bots.random_bot import RandomBot
from backend.app.poker.bots.equity_bot import EquityBot
from backend.app.poker.texas_holdem import TexasHoldem
from backend.app.poker.player import Player

from django.db import transaction
from django.http import HttpResponseBadRequest
from django.views.decorators.http import require_POST

from backend.app.poker.action import ActionType, PlayerAction

from .models import PokerTable

BUTTON_LABELS = {
    ActionType.FOLD: "Fold",
    ActionType.CALL: "Call",
    ActionType.CHECK: "Check",
    ActionType.BET: "Bet",
    ActionType.RAISE: "Raise",
    ActionType.ALL_IN: "All in",
}
WAGER_ACTIONS = {ActionType.BET, ActionType.RAISE}

@require_http_methods(["GET", "POST"])
def new_table(request):
    choices = range(1, 8)
    if request.method == "GET":
        return render(request, "tables/new_table.html", {"choices": choices})
    count = request.POST.get("bot_count", "1")
    if count not in {str(n) for n in choices}:
        return render(request, "tables/new_table.html", {
            "choices": choices, "error": "Choose between 1 and 7 bots.",
        }, status=400)
    count = int(count)
    
    owner_token = request.session.get("poker_owner_token")
    if owner_token is None:
        owner_token = str(uuid.uuid4())
        request.session["poker_owner_token"] = owner_token

    human = Player("You", 1000)
    bots = [Player("Bot" if count == 1 else f"Bot {i + 1}", 1000, EquityBot())
            for i in range(count)]
    game = TexasHoldem([human, *bots])
    game.start_hand()

    table = PokerTable.objects.create(
        owner_token=owner_token,
        human_seat_id=human.seat_id,
        snapshot=game.to_snapshot(),
    )
    return redirect("tables:detail", table_id=table.pk)

def can_deal_next_hand(state):
    return (
        state.street == "complete"
        and state.hero.chips > 0
        and any(opponent.chips > 0 for opponent in state.opponents)
    )

@require_GET
def table_detail(request, table_id):
    table = get_object_or_404(
        PokerTable, 
        pk=table_id, 
        owner_token=request.session.get("poker_owner_token"),
    )
    game = TexasHoldem.from_snapshot(table.snapshot)
    state = game.view_for(table.human_seat_id)

    badges = {
        event.seat_id: "post" if event.kind in {"small_blind", "big_blind"} else event.kind
        for event in state.history
        if event.street == state.street and event.seat_id is not None
        and event.kind != "payout"
    }

    actor = next((seat for seat in (state.hero, *state.opponents)
                  if seat.seat_id == state.acting_seat_id), None)
    waiting = state.street != "complete" and state.acting_seat_id != state.hero.seat_id
    transition = ""
    advance_delay = 0
    if waiting and actor is not None:
        advance_delay = 2200
    elif waiting:
        next_street = {"preflop": "flop", "flop": "turn", "turn": "river"}.get(state.street)
        if next_street and game.num_players_unfolded > 1:
            transition = f"Dealing {next_street}"
            advance_delay = 1000
        else:
            transition = "Settling pot"

    legal = state.legal_actions
    wager_button = None
    call_button = None
    for action in legal.actions:
        if action in WAGER_ACTIONS and legal.min_bet <= legal.max_bet:
            wager_button = {"value": action.value, "label": BUTTON_LABELS[action]}
        elif action in (ActionType.CALL, ActionType.CHECK):
            label = f"Call {legal.amount_to_call} chips" if action == ActionType.CALL else "Check"
            call_button = {"value": action.value, "label": label}

    reveals = game.showdown_hands()
    exposed = {row["seat_id"]: row["hole_cards"] for row in reveals}
    return render(request, "tables/detail.html", {
        "state": state,
        "table_id": table.pk,
        "revision": table.revision,
        "hero_badge": badges.get(state.hero.seat_id),
        "opponent_seats": [(player, badges.get(player.seat_id), exposed.get(player.seat_id))
                           for player in state.opponents],
        "reveals": reveals,
        "display_history": [event for event in reversed(state.history) if event.kind != "board"],
        "can_fold": ActionType.FOLD in legal.actions,
        "can_go_all_in": ActionType.ALL_IN in legal.actions,
        "call_button": call_button,
        "transition": transition,
        "wager_button": wager_button,
        "can_deal_next_hand": can_deal_next_hand(state),
        "waiting_for_step": waiting,
        "actor": actor,
        "actor_to_call": min(actor.chips, max(0, state.current_bet - actor.current_bet)) if actor else 0,
        "advance_delay": advance_delay,
    })

@require_POST
def submit_action(request, table_id):
    try:
        action_type = ActionType(request.POST.get("action"))
    except ValueError:
        return HttpResponseBadRequest("Unknown poker action.")

    try:
        displayed_revision = int(request.POST["revision"])
    except (KeyError, ValueError):
        return HttpResponseBadRequest("Invalid table revision.")

    with transaction.atomic():
        table = get_object_or_404(
            PokerTable.objects.select_for_update(),
            pk=table_id,
            owner_token=request.session.get("poker_owner_token"),
        )

        if displayed_revision != table.revision:
            return redirect("tables:detail", table_id=table.pk)

        amount = 0
        if action_type in WAGER_ACTIONS:
            try:
                amount = int(request.POST["amount"])
            except (KeyError, ValueError):
                return HttpResponseBadRequest("Enter a whole number of chips.")
            
        game = TexasHoldem.from_snapshot(table.snapshot)

        try:
            game.submit_action(
                table.human_seat_id,
                PlayerAction(action_type, amount),
            )
        except ValueError as error:
            return HttpResponseBadRequest(str(error))

        table.snapshot = game.to_snapshot()
        table.revision += 1
        table.save(update_fields=["snapshot", "revision", "updated_at"])

    return redirect("tables:detail", table_id=table.pk)

@require_POST
def next_hand(request, table_id):
    try:
        displayed_revision = int(request.POST["revision"])
    except (KeyError, ValueError):
        return HttpResponseBadRequest("Invalid table revision.")

    with transaction.atomic():
        table = get_object_or_404(
            PokerTable.objects.select_for_update(),
            pk=table_id,
            owner_token=request.session.get("poker_owner_token"),
        )

        if displayed_revision != table.revision:
            return redirect("tables:detail", table_id=table.pk)

        game = TexasHoldem.from_snapshot(table.snapshot)
        state = game.view_for(table.human_seat_id)

        if not can_deal_next_hand(state):
            return HttpResponseBadRequest("This table cannot deal another hand.")

        game.finish_hand()
        game.start_hand()

        table.snapshot = game.to_snapshot()
        table.revision += 1
        table.save(update_fields=["snapshot", "revision", "updated_at"])

    return redirect("tables:detail", table_id=table.pk)

@require_POST
def advance_table(request, table_id):
    try:
        displayed_revision = int(request.POST["revision"])
    except (KeyError, ValueError):
        return HttpResponseBadRequest("Invalid table revision.")

    with transaction.atomic():
        table = get_object_or_404(
            PokerTable.objects.select_for_update(),
            pk=table_id,
            owner_token=request.session.get("poker_owner_token"),
        )

        if displayed_revision == table.revision:
            game = TexasHoldem.from_snapshot(table.snapshot)
            if game.advance_one_step():
                table.snapshot = game.to_snapshot()
                table.revision += 1
                table.save(update_fields=["snapshot", "revision", "updated_at"])

    return redirect("tables:detail", table_id=table.pk)