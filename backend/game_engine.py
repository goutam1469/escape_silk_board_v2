from state import GameState
from judge import judge_action
from narrator import narrate

def create_game() -> GameState:
    return GameState(
        money=500,
        battery=4,
        distance_to_airport=30,
        time_remaining=60,
        inventory=["cold samosa"],
        location="Silk Board",
    )

def apply_outcome(state: GameState, o: dict) -> None:
    spent = max(-200, min(o["money_spent"], 600))
    if spent > state.money:
        spent = 0
        o["reason"] += " (They couldn't afford it.)"
    state.money -= spent
    state.distance_to_airport = max(0, state.distance_to_airport - max(0, min(o["km_covered"], 8)))
    state.time_remaining -= max(1, min(o["minutes_spent"], 30))
    state.battery = max(0, min(4, state.battery - max(0, o["battery_used"])))
    for item in o["items_lost"]:
        if item in state.inventory:
            state.inventory.remove(item)
    state.inventory += o["items_gained"]

def stats_line(s: GameState) -> str:
    return (
        f"Remaining Balance : ₹{s.money} . Remaining Battery : {s.battery}/4 ."
        f"Distance to airport : {s.distance_to_airport:.1f} km . Time Left : {max(0,s.time_remaining)} min"
    )

def check_game_over(state: GameState) -> None:
    if state.distance_to_airport <= 0 and state.time_remaining > 0:
        state.game_over, state.outcome = True, "won"
    elif state.time_remaining <= 0:
        state.game_over, state.outcome = True, "lost"

def play_turn(state: GameState, action: str) -> str:
    """Runs one full turn: LLM judge -> engine rules -> LLM narrator."""
    if state.game_over:
        return "The game is over. Press **New game** to play again."
    outcome = judge_action(action, state)
    apply_outcome(state, outcome)
    check_game_over(state)
    return f"{narrate(action, outcome, state)} \n\n {stats_line(state)}"