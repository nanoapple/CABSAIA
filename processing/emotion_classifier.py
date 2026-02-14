import re
from typing import Dict, Any, List, Tuple, Literal

from resources.emotion_dictionary import (
    EMOTION_KEYWORDS,
    EMOTION_INTENSITY,
    EMOTION_EXPRESSIONS,
    COUNSELING_THEMES
)
from processing.context_negators import detect_negators

SentimentType = Literal["positive", "negative", "neutral"]


def clean_text(raw: str) -> str:
    """Lowercase, normalise apostrophes, remove punctuation (keep apostrophes), collapse whitespace."""
    text = (raw or "").lower().strip()
    text = text.replace("\u2019", "'").replace("\u2018", "'").replace("`", "'")
    text = re.sub(r"[^\w\s']", " ", text)
    text = re.sub(r"\s+", " ", text).strip()
    return text


def keyword_in_text(word: str, text: str) -> bool:
    """Whole-word match."""
    if not word or not text:
        return False
    return bool(re.search(r"\b" + re.escape(word) + r"\b", text))


def get_negator_hits(text: str) -> List[str]:
    """
    Return list of negator hits (strings) if available.
    detect_negators() signature depends on your context_negators module.
    We defensively coerce to List[str].
    """
    hits = detect_negators(text)
    if not hits:
        return []
    if isinstance(hits, list):
        return [str(h) for h in hits]
    # fallback: single hit object -> string
    return [str(hits)]


def detect_hard_stop(text: str) -> bool:
    """
    High-priority "stop talking / go away" detection.
    This is stricter than general negativity: it means user explicitly wants the agent to stop.

    Returns True if hard-stop should short-circuit the LLM reply.
    """
    cleaned = clean_text(text)
    if not cleaned:
        return False

    # 1) If your context_negators is good, this catches most expulsion cues
    hits = get_negator_hits(text)
    if hits:
        # We only treat as hard-stop if the negator looks like expulsion/stop.
        # Because detect_negators may include other interactional negation signals.
        expulsion_markers = [
            "shut up",
            "stop talking",
            "go away",
            "leave me alone",
            "get away",
            "back off",
            "fuck off",
            "piss off",
            "dont talk to me",
            "don't talk to me",
            "not talking to you",
        ]
        for m in expulsion_markers:
            if m in cleaned:
                return True

    # 2) Direct phrase matches (fast path)
    HARD_STOP_PHRASES = [
        "shut up",
        "stop talking",
        "go away",
        "leave me alone",
        "get away",
        "back off",
        "fuck off",
        "piss off",
        "dont talk to me",
        "don't talk to me",
        "not talking to you",
    ]
    return any(p in cleaned for p in HARD_STOP_PHRASES)


def analyse_emotion_from_text(text: str) -> Dict[str, Any]:
    text = clean_text(text)

    keywords: List[Tuple[str, str]] = []
    valence_score = 0.0
    arousal_score = 0.0
    themes: List[str] = []

    for category, word_list in EMOTION_KEYWORDS.items():
        for word in word_list:
            if keyword_in_text(word, text):
                keywords.append((category, word))
                if category == "positive":
                    valence_score += 1.0
                    arousal_score += 0.3
                elif category == "negative":
                    valence_score -= 1.0
                    arousal_score -= 0.3

    for theme, cues in COUNSELING_THEMES.items():
        if any(keyword_in_text(cue, text) for cue in cues):
            themes.append(theme)

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

    valence_score = max(-1.0, min(1.0, valence_score))
    arousal_score = max(-1.0, min(1.0, arousal_score))

    dominance = 0.5 * valence_score - 0.5 * arousal_score
    dominance = max(-1.0, min(1.0, float(dominance)))

    seen = set()
    deduped_keywords: List[Tuple[str, str]] = []
    for cat, word in keywords:
        if word not in seen:
            deduped_keywords.append((cat, word))
            seen.add(word)

    if expression is None:
        expression = "direct" if deduped_keywords else "unknown"

    intensity_canonical = {
        "mild": "mild",
        "moderate": "moderate",
        "strong": "intense",
        "intense": "intense",
        "extreme": "severe",
        "severe": "severe",
    }
    intensity = intensity_canonical.get(intensity, intensity)

    return {
        "valence": float(valence_score),
        "arousal": float(arousal_score),
        "dominance": dominance,
        "keywords": deduped_keywords,
        "themes": themes,
        "expression": expression,
        "intensity": intensity,
    }


def infer_feedback_score(text: str) -> float:
    cleaned = clean_text(text)
    if not cleaned:
        return 0.0

    hits = detect_negators(text)
    if hits:
        return -1.0

    NEG_PHRASES = [
        "shut up",
        "go away",
        "leave me alone",
        "get lost",
        "back off",
        "get out",
        "fuck off",
        "piss off",
        "go to hell",
        "screw you",
        "stop talking",
        "don't talk to me",
        "dont talk to me",
        "not talking to you",
        "i'm done with you",
        "im done with you",
        "waste of time",
        "thanks for nothing",
        "you're no help",
        "youre no help",
    ]

    NEG_WORDS = [
        "stupid",
        "idiot",
        "moron",
        "dumb",
        "jerk",
        "useless",
        "liar",
        "asshole",
        "dickhead",
    ]

    POS_PHRASES = [
        "thank you",
        "thanks",
        "appreciate it",
        "i appreciate",
        "much appreciated",
        "that helps",
        "that helped",
        "that was helpful",
        "that fixed it",
        "problem solved",
    ]

    POS_NEGATORS = [
        "fake",
        "pretend",
        "lying",
        "liar",
        "mask",
        "whatever",
        "if you say so",
        "sure whatever",
        "yeah right",
        "for nothing",
        "real helpful",
        "don't care",
        "dont care",
        "i'm done",
        "im done",
        "who cares",
        "pointless",
        "fuck",
        "shit",
    ]

    for p in NEG_PHRASES:
        if p in cleaned:
            return -1.0

    for w in NEG_WORDS:
        if keyword_in_text(w, cleaned):
            return -1.0

    if not any(n in cleaned for n in POS_NEGATORS):
        for p in POS_PHRASES:
            if p in cleaned:
                return 1.0

    return 0.0