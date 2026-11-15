from google.genai import types
from backend.llm import client, MODEL


SYSTEM = """You narrate a comedic, sarcastic text game set in Bengaluru traffic.
Write ONE short sarcastic sentence (max 20 words) about what just happened.
Do not mention numbers. If the game is over, say whether the player made the flight or missed it."""

def narrate(action: str, outcome: dict, state) -> str:
    if client is None:
        return outcome["reason"]

    if state.game_over:
        result = "WON: reached the airport in time" if state.distance_to_airport <= 0 and state.time_remaining > 0 else "LOST: ran out of time"
    else:
        result = "game continues"
    prompt = (
        f"Player action: {action!r}\n"
        f"What happened: {outcome['reason']} (plausible={outcome['plausible']})\n"
        f"{state.time_remaining} min left. Status: {result}"
    )
    try:
        resp = client.models.generate_content(
            model=MODEL,
            contents=prompt,
            config=types.GenerateContentConfig(
                system_instruction=SYSTEM,
                temperature=0.9,
                max_output_tokens=2048,
            ),
        )
        return resp.text
    except Exception as e:
        print("Narrator failed:", e)
        return outcome["reason"]