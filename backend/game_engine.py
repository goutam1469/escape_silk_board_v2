from backend.state import GameState
from backend.judge import judge_action
from backend.narrator import narrate
from backend.loadout import evaluate_loadout

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
        # Can't afford it: the action fails instead of giving a free ride
        spent = 0
        o.update(km_covered=0, minutes_spent=2, items_gained=[], items_lost=[],
                 reason="The player couldn't afford that and got nowhere.")
    state.money -= spent

    km = max(0, min(o["km_covered"], 8))
    minutes = max(1, min(o["minutes_spent"], 30))
    if km > 0:
        minutes += total_burden(state)   # heavy items slow every move that covers distance

    state.distance_to_airport = max(0, state.distance_to_airport - km)
    state.time_remaining -= minutes
    state.battery = max(0, min(4, state.battery - max(0, o["battery_used"])))

    for item in o["items_lost"]:
        item = item.lower()
        if item in state.inventory:
            state.inventory.remove(item)
    for item in o["items_gained"]:
        item = item.lower()
        if item not in state.inventory:
            state.inventory.append(item)

def total_burden(s: GameState) -> int:
    return min(4, sum(b for n,b in s.item_burden.items() if n in s.inventory))

def stats_line(s: GameState) -> str:
    drag = f" . +{total_burden(s)} min/move" if total_burden(s) else ""
    return (
        f"Remaining Balance : ₹{s.money} . Remaining Battery : {s.battery}/4 ."
        f"Distance to airport : {s.distance_to_airport:.1f} km . Time Left : {max(0,s.time_remaining)} min"
    )

def check_game_over(state: GameState) -> None:
    if state.distance_to_airport <= 0 and state.time_remaining > 0:
        state.game_over, state.outcome = True, "won"
    elif state.time_remaining <= 0:
        state.game_over, state.outcome = True, "lost"

def start_game(state: GameState, text: str) -> str:
    state.started = True
    if text.strip().lower() in {"", "nothing", "none", "no", "skip"}:
        return f"Travelling light. How do you get out of Silk Board?\n\n{stats_line(state)}"

    lines = []
    for it in evaluate_loadout(text):
        name = it["name"].lower()[:30]
        if not it["accepted"]:
            lines.append(f"✖ {name}: you can't carry that")
            continue
        if name in state.inventory:
            continue
        state.inventory.append(name)
        state.item_notes[name] = it["note"]
        state.item_burden[name] = max(0, min(3, it["burden"]))
        icon = "🐌" if state.item_burden[name] else "✔"
        lines.append(f"{icon} {name}: {it['note']}")

    packed = "\n".join(lines) if lines else "You pack nothing useful."
    return f"{packed}\n\nHow do you get out of Silk Board?\n\n{stats_line(state)}"

def play_turn(state: GameState, action: str) -> str:
    if state.game_over:
        return "The game is over. Press **New game** to play again."
    if not state.started:
        return start_game(state, action)
    outcome = judge_action(action, state)
    apply_outcome(state, outcome)
    check_game_over(state)
    return f"{narrate(action, outcome, state)}\n\n{stats_line(state)}"