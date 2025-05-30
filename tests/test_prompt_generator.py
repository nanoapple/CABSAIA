# cabsaia/tests/test_prompt_generator.py

import os
import sys
import pytest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from core.prompt_generator import PromptGenerator

class DummyEmotion:
    def __init__(self, valence=0.0, arousal=0.0, dominance=0.0, resilience=1.0, emotion_debt=0.0):
        self.valence = valence
        self.arousal = arousal
        self.dominance = dominance
        self.resilience = resilience
        self.emotion_debt = emotion_debt

@pytest.mark.parametrize("role, valence, arousal, dominance", [
    ("Empathizer", 0.7, 0.6, 0.4),
    ("Teaser", 0.5, 0.8, 0.2),
    ("Resigned", -0.6, 0.3, -0.2),
    ("Analyst", 0.3, 0.4, 0.7),
    ("Pleaser", 0.1, 0.5, 0.1),
])
def test_prompt_generation(role, valence, arousal, dominance):
    pg = PromptGenerator(config_path="config/roles.yaml")
    emotion = DummyEmotion(valence=valence, arousal=arousal, dominance=dominance)

    user_input = "I feel confused about my recent decisions."
    prompt = pg.build_prompt(user_input, role, emotion)

    print("\n----------------------------")
    print(f"🧪 Role: {role} | V:{valence} A:{arousal} D:{dominance}")
    print(prompt)
    print("----------------------------\n")

    assert role in prompt
    assert "User says" in prompt
    assert "Emotion Label" in prompt
