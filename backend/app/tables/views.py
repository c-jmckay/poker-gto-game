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
    if request.method == "GET":
        return render(request, "tables/new_table.html")
    
    owner_token = request.session.get("poker_owner_token")
    if owner_token is None:
        owner_token = str(uuid.uuid4())
        request.session["poker_owner_token"] = owner_token

    human = Player("You", 1000)
    bot = Player("Bot", 1000, EquityBot())
    game = TexasHoldem([human, bot])
    game.advance_until_decision()

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

    action_buttons = []
    wager_button = None
    legal = state.legal_actions

    for action in legal.actions:
        label = BUTTON_LABELS[action]

        if action in WAGER_ACTIONS:
            if legal.min_bet <= legal.max_bet:
                wager_button = {"value": action.value, "label": label}
            continue

        if action == ActionType.CALL:
            label = f"Call {legal.amount_to_call} chips"

        action_buttons.append({"value": action.value, "label": label})

    return render(request, "tables/detail.html", {
        "state": state,
        "table_id": table.pk,
        "revision": table.revision,
        "action_buttons": action_buttons,
        "wager_button": wager_button,
        "can_deal_next_hand": can_deal_next_hand(state),
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

        game.advance_until_decision()

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
        game.advance_until_decision()

        table.snapshot = game.to_snapshot()
        table.revision += 1
        table.save(update_fields=["snapshot", "revision", "updated_at"])

    return redirect("tables:detail", table_id=table.pk)