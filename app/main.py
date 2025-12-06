import sys
from pathlib import Path

# Ensure Python can find the 'app' package
ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.append(str(ROOT))

import streamlit as st

from app.services.sentiment import detect_emotion
from app.services.safety import is_distress
from app.services.mood_store import log_mood, load_mood_data
from app.services.chat import generate_ai_reply

# Basic page config
st.set_page_config(
    page_title="MindGaurdAi",
    page_icon="💙",
    layout="wide"
)


def main():
    # -------- SIDEBAR --------
    with st.sidebar:
        st.markdown("## MindGuard AI")
        st.markdown("**Student:** Anvita Shashi (Class IX-B)")
        st.markdown("---")
        st.markdown("### Technologies Used")
        st.markdown(
            "- Python 3.14\n"
            "- Streamlit\n"
            "- TextBlob (Sentiment)\n"
            "- Groq + LLaMA 3 (LLM)\n"
            "- JSON for Mood Logs"
        )
        st.markdown("---")
        st.info(
            "Disclaimer: This tool does not provide medical advice or diagnosis. "
            "For serious concerns, students must talk to a parent, teacher, or counsellor."
        )

    # -------- HEADER --------
    st.markdown(
        """
        <h1 style='text-align: center; color: #4A90E2;'>MindGuard AI</h1>
        <p style='text-align: center; font-size: 18px;'>
            💙 A Safe & Supportive Emotional Wellness Companion for Teenagers
        </p>
        <hr>
        """,
        unsafe_allow_html=True
    )

    # -------- LAYOUT: TWO COLUMNS --------
    col1, col2 = st.columns([2, 1])

    # -------- LEFT COLUMN: CHAT AREA --------
    with col1:
        st.subheader("💬 Chat with MindGuard AI")

        if "history" not in st.session_state:
            st.session_state.history = []  # list of (role, message)

        user_input = st.text_input("How are you feeling today?")

        if st.button("Send") and user_input.strip():
            # 1. Detect emotion
            emotion = detect_emotion(user_input)

            # Map emotion to mood bucket for logging
            if emotion in ("positive", "neutral", "negative"):
                mood_bucket = emotion
            else:  # 'very_negative' also logged as 'negative'
                mood_bucket = "negative"

            log_mood(mood_bucket)

            # 2. Check if this is distress / crisis level
            if is_distress(user_input, emotion):
                ai_reply = (
                    "I am really sorry that you are feeling this much pain. "
                    "Please talk to a parent, teacher, or counsellor right now. "
                    "You do not have to face this alone — someone you trust can "
                    "support you immediately."
                )
            else:
                # 3. Normal case: generate AI reply (Groq + fallback)
                ai_reply = generate_ai_reply(user_input, emotion, st.session_state.history)

            # 4. Store conversation
            st.session_state.history.append(("You", user_input))
            st.session_state.history.append(("MindGuard AI", ai_reply))

        st.markdown("---")

        # Render chat history as chat bubbles
        for role, message in st.session_state.history:
            if role == "You":
                st.markdown(
                    f"""
                    <div style='background-color:#DCF8C6; padding:10px; border-radius:10px; margin-bottom:8px;'>
                        <strong>🧑 You:</strong> {message}
                    </div>
                    """,
                    unsafe_allow_html=True
                )
            else:
                st.markdown(
                    f"""
                    <div style='background-color:#E8F1FF; padding:10px; border-radius:10px; margin-bottom:8px;'>
                        <strong>🤖 MindGuard AI:</strong> {message}
                    </div>
                    """,
                    unsafe_allow_html=True
                )

    # -------- RIGHT COLUMN: MOOD + RESPONSIBLE AI --------
    with col2:
        st.subheader("📊 Mood Summary (Basic View)")

        mood_data = load_mood_data()
        if mood_data:
            st.json(mood_data)
        else:
            st.write("No mood data recorded yet. Start chatting to build your mood history!")

        st.markdown("---")
        st.subheader("🔒 Responsible AI Principles")

        st.markdown(
            """
            <div style='background-color:#FFF7E6; padding:15px; border-radius:10px;'>
            • No medical advice or diagnosis.<br>
            • Age-appropriate, safe and kind language.<br>
            • Encourages students to talk to trusted adults.<br>
            • Detects distress and shows a crisis safety message.<br>
            • Only mood counts are stored, no identity data.<br>
            </div>
            """,
            unsafe_allow_html=True
        )


if __name__ == "__main__":
    main()
    