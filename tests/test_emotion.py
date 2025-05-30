# cabsaia/tests/test_emotion.py

import pytest
from cabsaia.state.emotion import EmotionalState

def test_emotion_update():
    state = EmotionalState(personality_type="neurotic")
    state.update(delta_valence=-0.4, delta_arousal=0.3, delta_dominance=0.2)
    
    assert -1.0 <= state.valence <= 1.0
    assert 0.0 <= state.arousal <= 1.0
    assert 0.0 <= state.dominance <= 1.0
    assert state.emotion_debt > 0

def test_emotion_recovery():
    state = EmotionalState(personality_type="introvert")
    state.update(delta_valence=-0.6)
    pre_valence = state.valence
    pre_debt = state.emotion_debt

    state.apply_emotional_maintenance(time_passed=5)

    assert abs(state.valence) < abs(pre_valence)
    assert state.emotion_debt < pre_debt
    assert 0.0 <= state.arousal <= 1.0

def test_burnout_detection():
    state = EmotionalState()
    state.emotion_debt = 6.0  # 超过burnout阈值
    triggered = state.check_burnout_risk()
    assert triggered is True
    assert state.resilience <= 1.0

def test_coping_strategy_selection():
    state = EmotionalState(valence=-0.7, dominance=0.6)
    strategy = state.select_coping_strategy()
    assert strategy == "problem_focused"

def test_emotion_projection():
    state = EmotionalState(valence=0.5, arousal=0.4, dominance=0.6)
    proj = state.get_2d_projection()
    assert isinstance(proj, dict)
    assert "x" in proj and "y" in proj
