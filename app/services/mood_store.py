import json
from datetime import date
from pathlib import Path

# data/moods.json inside project
BASE_DIR = Path(__file__).resolve().parent.parent.parent
DATA_DIR = BASE_DIR / "data"
DATA_DIR.mkdir(exist_ok=True)

MOOD_FILE = DATA_DIR / "moods.json"

def log_mood(emotion: str) -> None:
    """
    Store daily mood counts in a JSON file.
    Structure:
    {
      "2025-02-10": {"positive": 3, "neutral": 1, "negative": 2},
      ...
    }
    """
    today = str(date.today())

    try:
        with MOOD_FILE.open("r") as f:
            data = json.load(f)
    except FileNotFoundError:
        data = {}

    if today not in data:
        data[today] = {"positive": 0, "neutral": 0, "negative": 0}

    if emotion in data[today]:
        data[today][emotion] += 1

    with MOOD_FILE.open("w") as f:
        json.dump(data, f, indent=2)


def load_mood_data():
    """
    Load full mood history. Returns {} if file missing.
    """
    try:
        with MOOD_FILE.open("r") as f:
            return json.load(f)
    except FileNotFoundError:
        return {}
