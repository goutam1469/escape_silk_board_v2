from pydantic import BaseModel

class GameState(BaseModel):
    money: int
    battery: int
    distance_to_airport: float
    time_remaining: int
    inventory: list[str]
    location: str
    game_over: bool = False
    outcome: str | None = None          # "won" or "lost"
    started: bool = False               # loadout chosen?
    item_nodes: dict[str, str] = {}     # item -> short note
    item_burden: dict[str, int] = {}    # item -> 0..3