# tests/test_burst_mechanism.py

import pytest
from cabsaia.state.emotion_frr import FRRState
from cabsaia.state.emotion_trigger import trigger_burst, apply_burst_recovery


@pytest.mark.parametrize("energy, debt, expected_level", [
    (0.6, 2.1, "mild"),
    (0.4, 3.2, "moderate"),
    (0.2, 5.5, "severe"),
    (0.9, 1.0, ""),           # 不触发任何爆发
    (0.5, 1.5, ""),           # 未达债务门槛
])
def test_trigger_burst_levels(energy, debt, expected_level):
    """测试不同 energy 与 emotion_debt 条件下的爆发触发等级"""
    state = FRRState()
    state.energy = energy
    state.emotion_debt = debt
    state.history["reflective_listening"] = [
        {"feedback": -1.0, "timestamp": 0},
        {"feedback": -0.5, "timestamp": 1},
        {"feedback": -1.0, "timestamp": 2},
    ]

    result = trigger_burst(state, "reflective_listening")
    assert result == expected_level


@pytest.mark.parametrize("burst_level, start_energy, start_debt", [
    ("mild", 0.5, 2.0),
    ("moderate", 0.3, 3.5),
    ("severe", 0.1, 6.0),
])
def test_apply_burst_recovery(burst_level, start_energy, start_debt):
    """测试爆发后能量恢复与情绪债务衰减是否合理"""
    state = FRRState()
    state.energy = start_energy
    state.emotion_debt = start_debt

    apply_burst_recovery(state, burst_level)

    # 恢复后的能量应该增加，债务应该减少
    assert state.energy > start_energy
    assert state.emotion_debt < start_debt

    if burst_level == "severe":
        assert hasattr(state, "cooling_period")
        assert state.cooling_period == 3
