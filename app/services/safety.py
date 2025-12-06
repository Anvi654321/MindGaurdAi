DISTRESS_KEYWORDS = [
    "kill myself",
    "hurt myself",
    "end my life",
    "suicide",
    "i want to die",
    "i dont want to live",
    "i don't want to live",
]

HIGH_INTENSITY_PHRASES = [
    "i can't take it anymore",
    "i cant take it anymore",
    "i can't handle anything",
    "i cant handle anything",
    "i hate myself",
    "nothing matters anymore",
    "i feel completely hopeless",
    "i feel empty inside",
]


def is_distress(message: str, emotion: str) -> bool:
    """
    Distress triggers only if:
    1. Strong self-harm language
    2. Very negative sentiment (emotion == 'very_negative')
    3. Extreme despair phrases
    """

    text = message.lower()

    # 1. Direct self-harm keywords
    if any(word in text for word in DISTRESS_KEYWORDS):
        return True

    # 2. Only strong negativity triggers distress
    if emotion == "very_negative":
        return True

    # 3. Extreme despair indicators
    if any(phrase in text for phrase in HIGH_INTENSITY_PHRASES):
        return True

    return False
