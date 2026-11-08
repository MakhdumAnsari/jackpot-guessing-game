
import streamlit as st
import random

st.set_page_config(
    page_title="Jackpot Guessing Game",
    page_icon="🎯"
)

if "jackpot" not in st.session_state:
    st.session_state.jackpot = random.randint(1, 100)
    st.session_state.counter = 0
    st.session_state.message = "Guess a number between 1 and 100!"

st.title("🎯 Jackpot Guessing Game")
st.write("Can you guess the secret number?")

guess = st.number_input(
    "Enter your guess:",
    min_value=1,
    max_value=100,
    step=1
)

if st.button("Check Guess"):
    st.session_state.counter += 1

    if guess == st.session_state.jackpot:
        st.session_state.message = "🎉 Congratulations! You won!"
    elif guess < st.session_state.jackpot:
        st.session_state.message = "📈 Guess Higher!"
    else:
        st.session_state.message = "📉 Guess Lower!"

st.info(st.session_state.message)

st.write("Attempts:", st.session_state.counter)

if st.button("🔄 Restart Game"):
    st.session_state.jackpot = random.randint(1, 100)
    st.session_state.counter = 0
    st.session_state.message = "New game started! Guess again!"
    st.rerun()
