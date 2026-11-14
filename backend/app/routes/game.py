from fastapi import APIRouter

try:
    from app.models.requests import MoveRequest
    from app.services.game_engine import create_game, get_game
    from app.services.judge import judge_action
    from app.services.narrator import narrate
except ModuleNotFoundError:
    from models.requests import MoveRequest
    from services.game_engine import create_game, get_game
    from services.judge import judge_action
    from services.narrator import narrate

router = APIRouter()

#Start Game Endpoint
@router.post("/start")
def start_game():

    state = create_game()

    return {
        "session_id": state.session_id,
        "intro":
            "You are standing at Silk Board."
            "Your flight leaves in 60 minutes.",
        "state": state
    }

#Move Endpoint
@router.post("/move")
def make_move(request: MoveRequest):
    state = get_game(request.session_id)
    if not state:
        return {
            "error": "Invalid session"
        }

    result = judge_action(request.action, state)

    state.money -= result["money_spent"]
    state.distance_to_airport = max(0.0, state.distance_to_airport - result["km_covered"])
    state.time_remaining -= result["minutes_spent"]
    state.battery = max(0, state.battery - result["battery_used"])

    for item in result["items_gained"]:
        if item not in state.inventory:
            state.inventory.append(item)

    for item in result["items_lost"]:
        if item in state.inventory:
            state.inventory.remove(item)

    narration = narrate(request.action, result, state)
    print("Narration: ", narration)

    if (
        state.distance_to_airport <= 0
        and state.time_remaining > 0
    ):
        state.game_over = True

    if state.time_remaining <= 0:
        state.game_over = True

    return {
        "narration": narration,
        "state": state
    }