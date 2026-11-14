from google.genai import types

try:
    from app.services.llm import client, MODEL
except ModuleNotFoundError:
    from services.llm import client, MODEL

SYSTEM = """You narrate a comedic, slightly sarcastic text game set in Bengaluru traffic.
Write 2-3 vivid sentences describing what just happened. Stay consistent with the facts
given (money, time, distance). Do not invent different numbers. If the game is over,
say whether the player made the flight or missed it. No bullet points."""

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
        f"State after: ₹{state.money}, {state.distance_to_airport:.1f} km left, "
        f"{state.time_remaining} min left. Status: {result}"
    )
    try:
        resp = client.models.generate_content(
            model=MODEL,
            contents=prompt,
            config=types.GenerateContentConfig(
                system_instruction=SYSTEM,
                temperature=0.9,
                max_output_tokens=300,
            ),
        )
        return resp.text
    except Exception as e:
        print("Narrator failed:", e)
        return outcome["reason"]