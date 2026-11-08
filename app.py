
import streamlit as st
import random
import time
import math
import wave
import struct
import io

st.set_page_config(
    page_title="Jackpot Guessing Game",
    page_icon="🎯",
    layout="centered"
)

LEVELS = {
    "Easy": {"maximum": 50, "time": 60, "attempts": 10},
    "Medium": {"maximum": 100, "time": 45, "attempts": 8},
    "Hard": {"maximum": 200, "time": 30, "attempts": 7}
}

defaults = {
    "difficulty": "Easy",
    "jackpot": random.randint(1, 50),
    "attempts": 0,
    "started_at": None,
    "game_over": False,
    "won": False,
    "message": "Choose your level and start guessing!",
    "best_score": 0,
    "score": 0,
    "last_sound": None,
    "guess_input": 1
}

for key, value in defaults.items():
    if key not in st.session_state:
        st.session_state[key] = value


def new_game(level):
    config = LEVELS[level]
    st.session_state.difficulty = level
    st.session_state.jackpot = random.randint(1, config["maximum"])
    st.session_state.attempts = 0
    st.session_state.started_at = None
    st.session_state.game_over = False
    st.session_state.won = False
    st.session_state.message = "New game started!"
    st.session_state.score = 0
    st.session_state.last_sound = None
    st.session_state.guess_input = 1


def make_sound(notes):
    rate = 22050
    buffer = io.BytesIO()

    with wave.open(buffer, "wb") as wav:
        wav.setnchannels(1)
        wav.setsampwidth(2)
        wav.setframerate(rate)

        for frequency, duration in notes:
            for i in range(int(rate * duration)):
                fade = min(1, i / 300, (rate * duration - i) / 300)
                sample = int(
                    10000 * fade *
                    math.sin(2 * math.pi * frequency * i / rate)
                )
                wav.writeframesraw(struct.pack("<h", sample))

    return buffer.getvalue()


def play_sound(name):
    sounds = {
        "win": [(523, 0.15), (659, 0.15), (784, 0.3)],
        "wrong": [(220, 0.18)],
        "timeout": [(330, 0.2), (220, 0.3)]
    }
    st.audio(make_sound(sounds[name]), format="audio/wav", autoplay=True)


st.markdown("""
<style>
.stApp {
    background: linear-gradient(135deg, #101426, #17112e, #101426);
    color: white;
}
.block-container {
    max-width: 850px;
    padding-top: 2rem;
}
.hero {
    text-align: center;
    padding: 20px 5px;
}
.hero h1 {
    font-size: clamp(28px, 6vw, 48px);
    background: linear-gradient(90deg, #9c8cff, #46d9ff);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
}
.hero p {color: #b9b9d5;}
.game-card {
    background: linear-gradient(135deg, #242345, #191a35);
    border: 1px solid #454475;
    border-radius: 18px;
    padding: 15px 5px;
    text-align: center;
    margin-bottom: 12px;
}
div.stButton > button, div.stFormSubmitButton > button {
    width: 100%;
    min-height: 48px;
    border-radius: 12px;
    background: linear-gradient(90deg, #6554e8, #3679e8);
    color: white;
    font-weight: bold;
}
@media(max-width: 600px) {
    .block-container {padding: 1rem 0.8rem;}
}
</style>
""", unsafe_allow_html=True)


st.markdown("""
<div class="hero">
<h1>🎯 JACKPOT GUESSING GAME</h1>
<p>Think smart. Guess right. Win the Jackpot!</p>
</div>
""", unsafe_allow_html=True)


level = st.selectbox(
    "🎮 Choose Difficulty",
    ["Easy", "Medium", "Hard"],
    index=["Easy", "Medium", "Hard"].index(st.session_state.difficulty),
    key="level_select"
)

if level != st.session_state.difficulty:
    new_game(level)
    st.rerun()

settings = LEVELS[st.session_state.difficulty]

c1, c2, c3 = st.columns(3)

with c1:
    st.markdown(
        f"""<div class="game-card">
        <h3>🎯 Range</h3><h2>1-{settings['maximum']}</h2>
        </div>""",
        unsafe_allow_html=True
    )

with c2:
    st.markdown(
        f"""<div class="game-card">
        <h3>⏱️ Time</h3><h2>{settings['time']}s</h2>
        </div>""",
        unsafe_allow_html=True
    )

with c3:
    st.markdown(
        f"""<div class="game-card">
        <h3>❤️ Attempts</h3><h2>{settings['attempts']}</h2>
        </div>""",
        unsafe_allow_html=True
    )


@st.fragment(run_every="1s")
def timer():
    if st.session_state.started_at is None:
        remaining = settings["time"]
    else:
        elapsed = int(time.time() - st.session_state.started_at)
        remaining = max(0, settings["time"] - elapsed)

    if (
        remaining == 0
        and st.session_state.started_at is not None
        and not st.session_state.game_over
        and not st.session_state.won
    ):
        st.session_state.game_over = True
        st.session_state.message = "⏰ Time is up!"
        st.session_state.last_sound = "timeout"

    st.markdown("### ⏱️ Countdown Timer")
    st.progress(remaining / settings["time"])
    st.metric("Time Remaining", f"{remaining} seconds")

    if st.session_state.last_sound == "timeout":
        play_sound("timeout")
        st.session_state.last_sound = None

    if st.session_state.game_over and not st.session_state.won:
        st.error(st.session_state.message)


timer()

c1, c2 = st.columns(2)

with c1:
    st.metric("🏆 Your Score", st.session_state.score)

with c2:
    st.metric("🥇 Best Score", st.session_state.best_score)


st.markdown("### 🎲 Make Your Guess")

if st.session_state.game_over or st.session_state.won:
    if st.session_state.won:
        st.success(st.session_state.message)
    else:
        st.error(st.session_state.message)

else:
    with st.form("guess_form", clear_on_submit=False):
        guess = st.number_input(
            f"Enter number (1-{settings['maximum']})",
            min_value=1,
            max_value=settings["maximum"],
            step=1,
            key="guess_input"
        )
        submitted = st.form_submit_button("🚀 CHECK GUESS")

    if submitted:
        if st.session_state.started_at is None:
            st.session_state.started_at = time.time()

        elapsed = int(time.time() - st.session_state.started_at)
        remaining = max(0, settings["time"] - elapsed)

        if remaining == 0:
            st.session_state.game_over = True
            st.session_state.message = "⏰ Time is up!"
            st.session_state.last_sound = "timeout"

        else:
            st.session_state.attempts += 1

            if guess == st.session_state.jackpot:
                st.session_state.won = True
                st.session_state.score = (
                    remaining * 10
                    + (settings["attempts"] - st.session_state.attempts + 1) * 25
                )
                st.session_state.best_score = max(
                    st.session_state.best_score,
                    st.session_state.score
                )
                st.session_state.message = "🎉 JACKPOT! YOU WON!"
                st.session_state.last_sound = "win"

            elif guess < st.session_state.jackpot:
                st.session_state.message = "📈 Guess Higher!"
                st.session_state.last_sound = "wrong"

            else:
                st.session_state.message = "📉 Guess Lower!"
                st.session_state.last_sound = "wrong"

            if (
                not st.session_state.won
                and st.session_state.attempts >= settings["attempts"]
            ):
                st.session_state.game_over = True
                st.session_state.message = (
                    f"❌ Game Over! Number was {st.session_state.jackpot}."
                )

        st.rerun()


if st.session_state.message:
    if st.session_state.won:
        st.success(st.session_state.message)
    elif st.session_state.game_over:
        st.error(st.session_state.message)
    else:
        st.info(st.session_state.message)

st.write(
    f"**Attempts Used:** {st.session_state.attempts} / {settings['attempts']}"
)

if st.session_state.last_sound:
    play_sound(st.session_state.last_sound)
    st.session_state.last_sound = None

st.markdown("---")

if st.button("🔄 START NEW GAME"):
    new_game(st.session_state.difficulty)
    st.rerun()

st.markdown("""
<div style="text-align:center; color:#9999bb; padding:20px;">
🎯 Jackpot Guessing Game 2.1<br>
Made with Python and Streamlit ❤️
</div>
""", unsafe_allow_html=True)
