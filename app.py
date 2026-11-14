import os
import gradio as gr

try:
    from backend.app.services.game_engine import create_game, play_turn
except ModuleNotFoundError:
    from app.services.game_engine import create_game, play_turn

try:
    import spaces

    @spaces.GPU
    def _gpu_placeholder():
        # Never called. Only exists so ZeroGPU finds a @spaces.GPU function at startup.
        return None
except ImportError:
    pass  # running locally without the spaces package

INTRO = "You are standing at Silk Board. Your flight leaves in 60 minutes."

def hud(s) -> str:
    banner = ""
    if s.game_over:
        banner = "\n\n### ✈️ You made your flight!" if s.outcome == "won" else "\n\n### ❌ You missed your flight."
    return (
        f"💰 ₹{s.money} &nbsp; 🔋 {s.battery}/4 &nbsp; "
        f"🛣 {s.distance_to_airport:.1f} km &nbsp; ⏰ {s.time_remaining} min"
        f"{banner}"
    )

def new_game():
    s = create_game()
    return s, [{"role": "assistant", "content": INTRO}], hud(s)

def play(action, history, state):
    if not action.strip():
        return "", history, state, hud(state)
    story = play_turn(state, action)
    history = history + [
        {"role": "user", "content": action},
        {"role": "assistant", "content": story},
    ]
    return "", history, state, hud(state)

with gr.Blocks(title="Escape Silk Board") as demo:
    gr.Markdown("# ✈️ Escape Silk Board")
    state = gr.State()
    status = gr.Markdown()
    chat = gr.Chatbot(height=450)
    box = gr.Textbox(placeholder="What do you want to do?", show_label=False)
    restart = gr.Button("New game")

    demo.load(new_game, None, [state, chat, status])
    restart.click(new_game, None, [state, chat, status])
    box.submit(play, [box, chat, state], [box, chat, state, status])

if __name__ == "__main__":
    demo.launch(server_name="0.0.0.0", server_port=int(os.getenv("PORT", 7860)))