# cabsaia/tests/test_emotion_classifier.py

import pytest
from cabsaia.processing.emotion_classifier import analyse_emotion_from_text

def test_positive_emotion():
    result = analyse_emotion_from_text("I feel very happy and grateful today")
    assert result["valence"] > 0
    assert "positive" in [cat for cat, _ in result["keywords"]]
    assert result["intensity"] == "intense"
    assert result["expression"] == "direct"

def test_negative_emotion():
    result = analyse_emotion_from_text("I'm completely devastated and hopeless")
    assert result["valence"] < 0
    assert "negative" in [cat for cat, _ in result["keywords"]]
    assert result["intensity"] == "severe"

def test_mixed_emotion():
    result = analyse_emotion_from_text("I'm proud but also overwhelmed and tired")
    assert "positive" in [cat for cat, _ in result["keywords"]]
    assert "negative" in [cat for cat, _ in result["keywords"]]
    assert isinstance(result["valence"], float)
    assert isinstance(result["arousal"], float)
    assert isinstance(result["dominance"], float)

def test_trauma_theme_detection():
    result = analyse_emotion_from_text("I've been having flashbacks and feel unsafe lately")
    assert "trauma" in result["themes"]

def test_no_emotion_detected():
    result = analyse_emotion_from_text("I walked my dog and watered the plants")
    assert result["keywords"] == []
    assert result["themes"] == []
    assert result["valence"] == 0.0
