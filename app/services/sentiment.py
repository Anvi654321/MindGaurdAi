from textblob import TextBlob

def detect_emotion(text: str) -> str:
    """
    Improved emotion classifier.
    Returns one of:
    - 'very_negative'
    - 'negative'
    - 'neutral'
    - 'positive'
    """

    polarity = TextBlob(text).sentiment.polarity

    # Only VERY extreme negativity is considered distress-level
    if polarity <= -0.7:
        return "very_negative"

    # Standard negative emotion
    if polarity < 0:
        return "negative"

    # Positive
    if polarity > 0.2:
        return "positive"

    return "neutral"
