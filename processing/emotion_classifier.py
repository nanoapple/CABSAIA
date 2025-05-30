import re
from typing import Dict, Any, List, Tuple
from cabsaia.resources.emotion_dictionary import (
    EMOTION_KEYWORDS,
    EMOTION_INTENSITY,
    EMOTION_EXPRESSIONS,
    COUNSELING_THEMES
)

def clean_text(text: str) -> str:
    return re.sub(r'[^a-zA-Z\s]', '', text).lower()

def keyword_in_text(keyword: str, text: str) -> bool:
    return re.search(r'\b' + re.escape(keyword) + r'\b', text) is not None

def analyse_emotion_from_text(text: str) -> Dict[str, Any]:
    text = clean_text(text)
    keywords: List[Tuple[str, str]] = []
    valence_score = 0.0
    arousal_score = 0.0
    themes: List[str] = []

    # Analyse keywords and emotional scores
    for category, word_list in EMOTION_KEYWORDS.items():
        for word in word_list:
            if keyword_in_text(word, text):
                keywords.append((category, word))
                if category == "positive":
                    valence_score += 1.0
                    arousal_score += 0.5
                elif category == "negative":
                    valence_score -= 1.0
                    arousal_score -= 0.5

    # Analyse themes
    for theme, cues in COUNSELING_THEMES.items():
        if any(keyword_in_text(cue, text) for cue in cues):
            themes.append(theme)

    # Analyse expression and intensity
    expression = None
    intensity = "moderate"
    for style, markers in EMOTION_EXPRESSIONS.items():
        if any(keyword_in_text(m, text) for m in markers):
            expression = style
            break

    for level, triggers in EMOTION_INTENSITY.items():
        if any(keyword_in_text(m, text) for m in triggers):
            intensity = level
            break

    # Clamp scores
    valence_score = max(-1.0, min(1.0, valence_score))
    arousal_score = max(-1.0, min(1.0, arousal_score))

    # Deduplicate keywords
    seen = set()
    deduped_keywords = []
    for cat, word in keywords:
        if word not in seen:
            deduped_keywords.append((cat, word))
            seen.add(word)

    return {
        "valence": valence_score,
        "arousal": arousal_score,
        "keywords": [word for _, word in deduped_keywords],
        "themes": themes,
        "expression": expression or "unknown",
        "intensity": intensity
    }
