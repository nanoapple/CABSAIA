# tests/test_role_engine.py

import time
import pytest
from cabsaia.behavior.role_engine import RoleEngine, dummy_state_for_test
from types import SimpleNamespace

@pytest.fixture
def mock_state():
    """创建用于测试的模拟状态对象"""
    state = SimpleNamespace()
    state.strategy_state = {
        "reflective_listening": {
            "recent_feedback": [-1, -1, -1],
            "cooldown": 3
        }
    }
    state.last_style = "calm"
    state.last_switch_time = time.time() - 100  # 模拟早于一分钟前
    return state

def test_cooling_mechanism():
    """测试冷却时间动态调整"""
    state = dummy_state_for_test()
    engine = RoleEngine(state)
    engine.update_strategy_cooldown("reflective_listening")
    assert state.strategy_state["reflective_listening"]["cooldown"] >= 4

def test_style_stability():
    """测试风格切换抑制"""
    state = dummy_state_for_test()
    engine = RoleEngine(state)

    # 同风格应返回 False
    assert engine.should_switch_style("calm") is False

    # 新风格相似度不足但时间足够，应允许切换
    assert engine.should_switch_style("moderate") is True

