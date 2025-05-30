"""
test_emotion_trigger.py
────────────────────────────────────────────────────────────────────────
针对 emotion_trigger.py 中新增的
    ① 非线性债务映射 calculate_nonlinear_debt
    ② 带权历史平均 get_recent_feedback_avg
    ③ 多级爆发判定 trigger_burst
    ④ 爆发后恢复 apply_burst_recovery
四大函数进行边界-与功能测试。

运行方式:  pytest cabsaia/tests/test_emotion_trigger.py -s
"""

import time
import math

from cabsaia.state.emotion_frr import FRRState
from cabsaia.state.emotion_trigger import (
    calculate_nonlinear_debt,
    get_recent_feedback_avg,
    trigger_burst,
    apply_burst_recovery,
)

# ──────────────────────────────────────────────────────────────────────
# 1. 非线性债务映射测试
# ──────────────────────────────────────────────────────────────────────
def test_nonlinear_debt_mapping():
    """债务 <=1 线性；>3 指数段明显大于线性外推"""
    lin = calculate_nonlinear_debt(0.8)
    assert math.isclose(lin, 0.8)

    mid = calculate_nonlinear_debt(2.0)
    assert 2.0 < mid < 2.5          # 轻微加速段

    high = calculate_nonlinear_debt(4.0)
    assert high >= 4.5         # 指数段应显著抬升


# ──────────────────────────────────────────────────────────────────────
# 2. 带权历史平均测试
# ──────────────────────────────────────────────────────────────────────
def test_weighted_average_and_trend():
    """最近值权重最大，递减趋势应拉低均值"""
    s = FRRState()
    strat = "probe"
    now = time.time()
    # 历史反馈：1.0 → 0.5 → -1.0  （明显下滑）
    s.history[strat] = [
        {"feedback": 1.0,  "timestamp": now - 60},
        {"feedback": 0.5,  "timestamp": now - 40},
        {"feedback": -1.0, "timestamp": now - 10},
    ]
    avg = get_recent_feedback_avg(s, strat, window=3)
    # 理论权重均值 = 1.0*0.6 + 0.5*0.3 + (-1.0)*0.1 = 0.35
    # 再减趋势修正(负)后应 < 0.35
    assert avg < 0.35


# ──────────────────────────────────────────────────────────────────────
# 3. 多级爆发 & 恢复逻辑测试
# ──────────────────────────────────────────────────────────────────────
def _seed_state_for_burst(level: str) -> FRRState:
    """根据爆发等级预设 energy / debt 组合"""
    cfg = {
        "mild":      (0.65, 2.1),
        "moderate":  (0.45, 3.5),
        "severe":    (0.25, 5.5),
    }
    energy, debt = cfg[level]
    st = FRRState(energy=energy, emotion_debt=debt)
    strat = "echo"
    st.history[strat] = [{"feedback": -1.0, "timestamp": time.time()}]
    return st

def test_trigger_burst_levels():
    """不同 debt+energy 应命中对应爆发等级"""
    for lvl in ("mild", "moderate", "severe"):
        st = _seed_state_for_burst(lvl)
        assert trigger_burst(st, "echo") == lvl

def test_burst_recovery_effect():
    """apply_burst_recovery 应降低债务 & 提升能量"""
    st = _seed_state_for_burst("moderate")
    prior_energy = st.energy
    prior_debt   = st.emotion_debt

    apply_burst_recovery(st, "moderate")

    assert st.energy > prior_energy
    assert st.emotion_debt < prior_debt
    # 冷却期字段应存在且==2
    assert getattr(st, "cooling_period", 0) == 2
