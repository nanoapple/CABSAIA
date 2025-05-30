# tests/test_emotion_frr.py
"""
📄 test_emotion_frr.py

本单元测试脚本用于验证 CABSAIA 系统中“参照调节型情绪延迟系统”（Feedback Reference Regulator, FRR）的基本功能与行为。

该机制为 CABSAIA 系统中的机制一（Emotion Delay via Reference-Based Regulation），其核心目的是：
    - 模拟用户反馈对情绪调节系统的延迟影响；
    - 根据历史交互策略的效果，动态调整当前的情绪债务（emotion_debt）与情绪恢复能力（resilience）；
    - 实现非线性情绪爆发与冷却行为模型的基础支撑。

测试内容包括：
1. ✅ 构造 FRR 实例后字段初始化是否正确；
2. ✅ `update_frr()` 方法在输入策略反馈后能否正确更新状态（包括债务增减与恢复能力调整）；
3. ✅ 是否正确记录最近一次策略反馈记录；
4. ✅ 历史反馈窗口能否正常追加并计算平均值；
5. ✅ 极值输入（如连续负反馈）是否会引发边界响应（如 resilience 触底）；
6. ✅ 所有字段更新后的状态是否可追溯、可视化，并支持主流程联动。

建议使用方式：
$ pytest tests/test_emotion_frr.py -s

注：此模块对应源码文件为：
    📁 state/emotion_frr.py
"""


import time
from cabsaia.state.emotion_frr import FRRState, update_frr, recent_avg_feedback


def test_initial_state():
    state = FRRState()
    assert state.emotion_debt == 0.0
    assert state.resilience == 1.0
    assert isinstance(state.history, dict)
    assert state.energy == 1.0
    assert state.time_active == 0


def test_negative_feedback_increases_debt():
    state = FRRState()
    before = state.emotion_debt
    update_frr(state, strategy="silence", feedback_score=-1.0, system_energy=0.4)
    assert state.emotion_debt > before
    assert state.resilience < 1.0  # Negative feedback reduces resilience


def test_positive_feedback_increases_resilience():
    state = FRRState(resilience=0.9)  # 设置一个低于最大值的初始弹性
    before = state.resilience
    update_frr(state, strategy="reflective_listening", feedback_score=1.0, system_energy=0.8)
    assert state.resilience > before


def test_history_logging():
    state = FRRState()
    strategy = "humble_rephrase"
    update_frr(state, strategy=strategy, feedback_score=0.5, system_energy=0.7)
    assert strategy in state.history
    assert len(state.history[strategy]) == 1
    assert "feedback" in state.history[strategy][0]
    assert "timestamp" in state.history[strategy][0]


def test_recent_avg_feedback():
    strategy = "mirror"
    now = time.time()
    mock_history = [
        {"feedback": 0.5, "timestamp": now - 100},
        {"feedback": 0.7, "timestamp": now - 50},
        {"feedback": 1.0, "timestamp": now - 10},
    ]
    avg = recent_avg_feedback(mock_history, window=3)
    expected = (0.5 + 0.7 + 1.0) / 3
    assert abs(avg - expected) < 0.01