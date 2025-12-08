import os
from typing import List, Tuple

from dotenv import load_dotenv
from groq import Groq

load_dotenv()
GROQ_KEY = os.getenv("GROQ_API_KEY")
client = Groq(api_key=GROQ_KEY) if GROQ_KEY else None


def fallback_reply(user_msg: str, emotion: str) -> str:
    """
    Rule-based backup for when the API fails or returns nothing.
    """

    msg = user_msg.lower()

    if "sad" in msg:
        return (
            "I am sorry that you are feeling sad. "
            "It is okay to feel this way sometimes. "
            "Doing something small that you enjoy or talking to someone you trust "
            "can help you feel a little lighter."
        )

    if "angry" in msg:
        return (
            "Feeling angry can be very intense. "
            "Taking a few deep breaths, counting slowly, or stepping away for a short break may help. "
            "You deserve some calm time for yourself."
        )

    if "friend" in msg:
        return (
            "Friendship problems can really hurt. "
            "It is normal to feel upset when things are not going well with friends. "
            "You might feel better by calmly sharing your feelings with them "
            "or talking to a trusted adult."
        )

    if "exam" in msg or "test" in msg:
        return (
            "Exams can feel stressful for many students. "
            "Breaking your study time into small parts and taking short breaks "
            "can make it feel more manageable."
        )

    if "happy" in msg or "hapy" in msg or emotion == "positive":
        return (
            "That is wonderful to hear. "
            "Enjoy this happy moment and keep doing the things that make you feel good and relaxed."
        )

    # General fallback
    if emotion in ("negative", "very_negative"):
        return (
            f"You said: “{user_msg}”. "
            "I am sorry that this is bothering you. "
            "Writing your thoughts in a journal or talking to a trusted adult "
            "may help you feel more supported."
        )
    else:
        return (
            f"You said: “{user_msg}”. "
            "Thank you for sharing how you feel."
        )


def _format_history(history: List[Tuple[str, str]]) -> str:
    if not history:
        return "None."
    return "\n".join([f"{r}: {m}" for r, m in history[-4:]])


def generate_ai_reply(user_msg: str, emotion: str, history: List[Tuple[str, str]]) -> str:
    """
    Conversational reply using Groq (LLaMA 3) with safety rules.
    More expressive and less repetitive, but still safe.
    """

    if client is None:
        return fallback_reply(user_msg, emotion)

    system_prompt = """
You are MindGuard AI, a friendly emotional support companion for teenagers.

Safety rules:
- Do NOT give medical, psychological, or mental health advice.
- Do NOT diagnose any condition.
- Do NOT recommend medicines, therapy, or treatment.
- Do NOT mention hotlines or specific organisations.
- Use simple, warm, age-appropriate language.
- Be supportive, non-judgmental, and respectful.
- Encourage only safe actions: deep breaths, a short break, drinking water,
  gentle movement, journaling, listening to calming music, or talking to a trusted adult.
- Never promise secrecy.
- Do NOT say that you are an AI or language model.

Style rules:
- Write like a kind, understanding senior who is gently supporting a younger student.
- Use 4–10 short sentences, up to about 180–220 words.
- You may use small friendly emojis like 🙂, 🌱, 💙, but use them sparingly.
- Vary your wording from message to message. Do not repeat the same sentences every time.
- You may ask ONE gentle follow-up question ONLY when the student seems upset,
  confused, or needs to open up more (usually when emotion is negative or very_negative).
- For positive or neutral emotions, a follow-up question is usually not needed.
"""

    user_prompt = f"""
Detected emotion: {emotion}
Student message: "{user_msg}"

Recent conversation:
{_format_history(history)}

Please respond with:
- A kind, personalized message that clearly reacts to what the student said.
- One or two simple, healthy suggestions if helpful.
- At most ONE gentle follow-up question, and only if the student seems upset or might want to share more.
Try to keep the whole reply within 4–10 sentences.
"""

    try:
        response = client.chat.completions.create(
            model="llama3-8b-8192",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user",  "content": user_prompt},
            ],
            max_tokens=260,
            temperature=0.7,
        )

        # Groq client: content is here
        reply = response.choices[0].message.content.strip()

        if not reply:
            return fallback_reply(user_msg, emotion)

        return reply

    except Exception:
        # Any error → safe fallback
        return fallback_reply(user_msg, emotion)
