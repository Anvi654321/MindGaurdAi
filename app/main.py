import sys
from pathlib import Path

# Ensure Python can find the 'app' package
ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.append(str(ROOT))

import os
import streamlit as st
import pandas as pd

from app.services.sentiment import detect_emotion
from app.services.safety import is_distress
from app.services.mood_store import log_mood, load_mood_data
from app.services.chat import generate_ai_reply

# ----------------- SCHOOL SETTINGS -----------------
SCHOOL_NAME = "The Newtown School, Kolkata"
LOGO_PATH = "assets/logo.png"   # make sure this exists

# ----------------- PAGE CONFIG -----------------
if os.path.exists(LOGO_PATH):
    st.set_page_config(
        page_title="MindGuard AI",
        page_icon=LOGO_PATH,
        layout="wide"
    )
else:
    st.set_page_config(
        page_title="MindGuard AI",
        page_icon="💙",
        layout="wide"
    )

# ----------------- GLOBAL STYLES (light theme + readable chat) -----------------
st.markdown(
    """
    <style>
    /* Force light background + dark text even if browser is in dark mode */
    html, body, [data-testid="stAppViewContainer"] {
        background-color: #F5F7FB !important;
        color: #000000 !important;
    }

    .block-container {
        padding-top: 2.5rem;   /* Enough so header is never cut */
        padding-bottom: 1rem;
    }

    .chat-bubble-user {
        background-color: #DCF8C6;
        padding: 10px;
        border-radius: 10px;
        margin-bottom: 8px;
        border: 1px solid #C5E1A5;
        color: #000000 !important;
    }
    .chat-bubble-ai {
        background-color: #E8F1FF;
        padding: 10px;
        border-radius: 10px;
        margin-bottom: 8px;
        border: 1px solid #BBDEFB;
        color: #000000 !important;
    }

    /* Make buttons (including Quick feelings) a bit more compact */
    .stButton>button {
        padding: 0.2rem 0.6rem;
        font-size: 0.8rem;
    }

    /* Prevent mobile zoom on input, better typing experience */
    input, textarea {
        font-size: 16px !important;
    }

    /* Hide Streamlit's deploy toolbar */
    div[data-testid="stToolbar"] {
        display: none !important;
    }
    </style>
    """,
    unsafe_allow_html=True
)


# ----------------- HELPERS -----------------
def build_mood_df(mood_data: dict):
    """Convert mood JSON into a DataFrame for charts."""
    if not mood_data:
        return None
    rows = []
    for date_str, counts in mood_data.items():
        rows.append({
            "date": date_str,
            "positive": counts.get("positive", 0),
            "neutral": counts.get("neutral", 0),
            "negative": counts.get("negative", 0),
        })
    if not rows:
        return None
    df = pd.DataFrame(rows)
    df = df.sort_values("date")
    df = df.set_index("date")
    return df


def handle_message(message: str):
    """Process one user message: emotion → safety → reply → history + mood log."""
    emotion = detect_emotion(message)

    # Map emotion to mood bucket for logging
    if emotion in ("positive", "neutral", "negative"):
        mood_bucket = emotion
    else:  # 'very_negative' also logged as 'negative'
        mood_bucket = "negative"

    log_mood(mood_bucket)

    # Distress check (crisis safety)
    if is_distress(message, emotion):
        ai_reply = (
            "I am really sorry that you are feeling this much pain. "
            "Please talk to a parent, teacher, or counsellor right now. "
            "You do not have to face this alone — someone you trust can "
            "support you immediately."
        )
    else:
        ai_reply = generate_ai_reply(message, emotion, st.session_state.history)

    # Store conversation (always: You then AI)
    st.session_state.history.append(("You", message))
    st.session_state.history.append(("MindGuard AI", ai_reply))


# ----------------- MAIN APP -----------------
def main():
    # -------- INITIAL SESSION STATE --------
    if "history" not in st.session_state:
        st.session_state.history = []  # list of (role, message)

    # -------- SIDEBAR --------
    with st.sidebar:
        # Logo at top
        if os.path.exists(LOGO_PATH):
            st.image(LOGO_PATH, width=170)

        st.markdown("## 💙 MindGuard AI")

        # Compact student/school/class block
        st.markdown(
            f"""
            <div style='line-height: 1.2; font-size: 14px; margin-top: 0.2rem;'>
                <b>Student:</b> Anvita Shashi<br>
                <b>School:</b> {SCHOOL_NAME}<br>
                <b>Class:</b> IX (B)
            </div>
            """,
            unsafe_allow_html=True
        )

        st.markdown("---")

        st.markdown("### 🛠️ Technologies Used")
        st.markdown(
            "- Python 3.14\n"
            "- Streamlit\n"
            "- TextBlob (Sentiment)\n"
            "- Groq (LLaMA 3)\n"
            "- JSON Mood Storage"
        )
        st.markdown("---")
        st.info(
            "Disclaimer: This tool does not provide medical advice or diagnosis. "
            "For serious concerns, students must talk to a parent, teacher, or counsellor."
        )
        st.markdown("---")
        st.markdown("### ℹ️ About MindGuard AI")
        st.markdown(
            "MindGuard AI is a school project that uses sentiment analysis and a safe "
            "AI model to support teenagers with their everyday emotions. "
            "It gently encourages students to talk to trusted adults when needed."
        )

    # -------- HEADER --------
    st.markdown(
        """
        <div style='text-align: center; margin-bottom: 0.5rem;'>
            <h2 style='color: #4A90E2; margin-bottom: 0.1rem;'>MindGuard AI</h2>
            <p style='font-size: 15px; margin-top: 0.1rem;'>
                A Safe & Supportive Emotional Wellness Companion for Teenagers 💬
            </p>
        </div>
        """,
        unsafe_allow_html=True
    )

    # -------- LAYOUT: TWO COLUMNS --------
    col1, col2 = st.columns([2, 1])

    # -------- LEFT COLUMN: CHAT AREA --------
    with col1:
        st.subheader("💬 Chat with MindGuard AI")

        # Quick feelings – compact
        st.markdown(
            "<p style='font-weight: 600; margin-bottom: 0.2rem;'>Quick feelings:</p>",
            unsafe_allow_html=True
        )
        bcol1, bcol2, bcol3, bcol4 = st.columns(4)
        quick_msg = None
        if bcol1.button("😊 Happy"):
            quick_msg = "I am feeling happy today."
        if bcol2.button("😔 Sad"):
            quick_msg = "I am feeling sad."
        if bcol3.button("😡 Angry"):
            quick_msg = "I am feeling angry."
        if bcol4.button("😰 Stressed"):
            quick_msg = "I am feeling stressed about my life and studies."

        # Handle quick button message
        if quick_msg:
            handle_message(quick_msg)

        st.markdown("---")

        # Chat form (stable for mobile & desktop)
        with st.form("chat_form", clear_on_submit=True):
            st.markdown(
                "<p style='font-weight: 600; margin-bottom: 0.1rem;'>Type your feelings or thoughts here:</p>",
                unsafe_allow_html=True
            )
            user_input = st.text_input(
                "",
                key="input",
                placeholder="Write how you feel..."
            )

            _, btn_col = st.columns([3, 1])
            send_clicked = btn_col.form_submit_button("Send")

        if send_clicked and user_input.strip():
            handle_message(user_input.strip())

        st.markdown("---")

        # Render chat history as chat bubbles (latest pair first)
        history = st.session_state.history
        n = len(history)

        for i in range(n - 2, -1, -2):
            role_user, msg_user = history[i]
            role_ai, msg_ai = (history[i + 1] if i + 1 < n else (None, None))

            # User bubble
            if role_user == "You":
                st.markdown(
                    f"""
                    <div class="chat-bubble-user">
                        <strong>🧑 You:</strong> {msg_user}
                    </div>
                    """,
                    unsafe_allow_html=True
                )
            elif role_user and msg_user:
                st.markdown(
                    f"""
                    <div class="chat-bubble-user">
                        <strong>{role_user}:</strong> {msg_user}
                    </div>
                    """,
                    unsafe_allow_html=True
                )

            # AI bubble
            if role_ai == "MindGuard AI":
                st.markdown(
                    f"""
                    <div class="chat-bubble-ai">
                        <strong>🤖 MindGuard AI:</strong> {msg_ai}
                    </div>
                    """,
                    unsafe_allow_html=True
                )
            elif role_ai and msg_ai:
                st.markdown(
                    f"""
                    <div class="chat-bubble-ai">
                        <strong>{role_ai}:</strong> {msg_ai}
                    </div>
                    """,
                    unsafe_allow_html=True
                )

    # -------- RIGHT COLUMN: MOOD + RESPONSIBLE AI --------
    with col2:
        st.subheader("📊 Mood Overview")

        mood_data = load_mood_data()
        df = build_mood_df(mood_data) if mood_data else None

        if df is not None and not df.empty:
            latest_date = df.index[-1]
            latest_counts = df.loc[latest_date]

            st.markdown(f"**Latest recorded day:** {latest_date}")
            mcol1, mcol2, mcol3 = st.columns(3)
            mcol1.metric("😊 Positive", int(latest_counts.get("positive", 0)))
            mcol2.metric("😐 Neutral", int(latest_counts.get("neutral", 0)))
            mcol3.metric("☹️ Negative", int(latest_counts.get("negative", 0)))

            st.markdown("#### Mood Trend (by day)")
            st.bar_chart(df[["positive", "neutral", "negative"]])
        else:
            st.write("No mood data recorded yet. Start chatting to build your mood history!")

        st.markdown("---")
        st.subheader("🔒 Responsible AI Principles")

        st.markdown(
            """
            <div style='background-color:#FFF7E6; padding:15px; border-radius:10px;'>
            • No medical advice or diagnosis.<br>
            • Age-appropriate, kind and simple language.<br>
            • Encourages students to talk to trusted adults for serious issues.<br>
            • Detects crisis-level distress and shows a safety message.<br>
            • Only mood counts per day are stored (no names or personal identity).<br>
            </div>
            """,
            unsafe_allow_html=True
        )


if __name__ == "__main__":
    main()
