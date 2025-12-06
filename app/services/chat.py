import os
from typing import List, Tuple

from dotenv import load_dotenv
from groq import Groq

load_dotenv()
GROQ_KEY = os.getenv("GROQ_API_KEY")
client = Groq(api_key=GROQ_KEY) if GROQ_KEY else None


def fallback_reply(user_msg: str, emotion: str) -> str:
    """
    Rule-based backup.
    Includes logical follow-up questions.
    """

    msg = user_msg.lower()

    if "sad" in msg:
        return (
            "I'm really sorry you're feeling sad. "
            "Sometimes sharing your feelings can make things feel lighter. "
            "Would you like to tell me what made you feel this way?"
        )

    if "angry" in msg:
        return (
            "Feeling angry can be tough. "
            "Taking a few deep breaths or taking a short break can sometimes help. "
            "Do you want to tell me what made you feel angry?"
        )

    if "friend" in msg:
        return (
            "Friendship issues can really hurt. "
            "It's okay to feel upset about it. "
            "What happened with your friends?"
        )

    if "exam" in msg:
        return (
            "Exams can definitely feel stressful. "
            "Breaking your study into small parts may help you feel more in control. "
            "Which subject is worrying you the most?"
        )

    if "happy" in msg or "hapy" in msg:
        return (
            "That's wonderful! It's great to hear you're feeling happy. "
            "What made your day better?"
        )

    # General fallback
    return (
        f"You said: “{user_msg}”. "
        "Thank you for sharing. How are you feeling about this?"
    )


def _format_history(history: List[Tuple[str, str]]) -> str:
    if not history:
        return "None."
    return "\n".join([f"{r}: {m}" for r, m in history[-4:]])


def generate_ai_reply(user_msg: str, emotion: str, history: List[Tuple[str, str]]) -> str:
    if client is None:
        return fallback_reply(user_msg, emotion)

    system_prompt = """
You are MindGuard AI, a friendly emotional support companion for teenagers.

Rules:
- No medical or psychological advice.
- No diagnosis.
- No therapy recommendations.
- Use simple, warm, short responses.
- Always add ONE kind follow-up question.
- Encourage only safe actions: deep breaths, water, break, journaling, or talk to trusted adult.
- Never promise secrecy.
- Never say you are an AI.
"""

    user_prompt = f"""
Emotion detected: {emotion}
Student said: "{user_msg}"

Conversation history:
{_format_history(history)}

Respond with:
1. A warm, personalized message.
2. One supportive, safe suggestion.
3. ONE gentle follow-up question (mandatory).
Max 80 words.
"""

    try:
        response = client.chat.completions.create(
            model="llama3-8b-8192",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            max_tokens=150,
            temperature=0.4,
        )
        reply = response.choices[0].message["content"].strip()
        if not reply:
            return fallback_reply(user_msg, emotion)
        return reply

    except:
        return fallback_reply(user_msg, emotion)
