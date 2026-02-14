"""
emotion_trigger.py
------------------
Extended Feedback-Reference Regulator (FRR) utilities:

1. Non-linear emotion-debt model
2. Time-decayed weighted feedback average
3. Multi-level burst detector
4. Burst recovery & cooling handler
"""

from __future__ import annotations
import logging
import math
from datetime import datetime, timezone
from statistics import pstdev
from typing import List, Dict

from state.emotion_frr import FRRState


# ──────────────────────────────────────────────────────────────────────
# 1. 非线性债务映射
# ──────────────────────────────────────────────────────────────────────
def calculate_nonlinear_debt(raw_debt: float) -> float:
    """
    对 emotion_debt 进行非线性映射，以模拟边际痛苦递增曲线。

    - debt ≤1     : 维持线性（细微负荷）
    - 1< debt ≤3  : 轻微加速（但仍近似线性）
    - debt  >3    : 指数加速，体现“情绪崩盘”风险
    """
    if raw_debt <= 1.0:
        return raw_debt
    if raw_debt <= 3.0:
        return raw_debt + 0.2 * (raw_debt - 1.0)  # 轻微加速段
    # 指数增长段
    return raw_debt + 0.5 * (raw_debt - 3.0) ** 2


# ──────────────────────────────────────────────────────────────────────
# 2. 带权历史平均 & 统计工具
# ──────────────────────────────────────────────────────────────────────
def _calculate_regression_slope(xs: List[int], ys: List[float]) -> float:
    """最简单的一元线性回归斜率（用于趋势修正）"""
    n = len(xs)
    if n < 2:
        return 0.0
    avg_x = sum(xs) / n
    avg_y = sum(ys) / n
    num = sum((x - avg_x) * (y - avg_y) for x, y in zip(xs, ys))
    den = sum((x - avg_x) ** 2 for x in xs) or 1e-6
    return num / den


def _calculate_std_dev(data: List[float]) -> float:
    """总体标准差；空数据返回 0"""
    return pstdev(data) if len(data) >= 2 else 0.0


def get_recent_feedback_avg(
    state: FRRState,
    strategy: str,
    window: int = 3,
    apply_trend: bool = True,
) -> float:
    """
    加权历史平均，权重默认 [0.6, 0.3, 0.1]（从近到远）。

    返回值范围约 [-1, 1]。提供参数校验 & 日志。
    """
    if not hasattr(state, "history"):
        logging.error("[FRR] State对象缺少history属性")
        return 0.0
    if not isinstance(strategy, str):
        logging.error(f"[FRR] 无效策略类型: {type(strategy)}")
        return 0.0

    history = state.history.get(strategy, [])[-window:]
    if not history:
        return 0.0

    # 取 feedback 列表
    fb_vals = [item["feedback"] for item in history]
    weights = [0.6, 0.3, 0.1][: len(fb_vals)]
    weighted_avg = sum(v * w for v, w in zip(fb_vals, weights))

    if apply_trend and len(fb_vals) >= 2:
        xs = list(range(len(fb_vals)))
        slope = _calculate_regression_slope(xs, fb_vals)
        trend_adjust = slope * 0.3  # 趋势修正系数
        weighted_avg += trend_adjust

    return weighted_avg


# ──────────────────────────────────────────────────────────────────────
# 3. 爆发分级阈值 & 触发
# ──────────────────────────────────────────────────────────────────────
BURST_LEVELS = {
    "mild": {
        "energy_threshold": 0.7,
        "debt_threshold": 2.0
    },
    "moderate": {
        "energy_threshold": 0.5,
        "debt_threshold": 3.0
    },
    "severe": {
        "energy_threshold": 0.3,
        "debt_threshold": 5.0
    }
}


def trigger_burst(state: FRRState, strategy: str) -> str:
    """
    判定是否触发爆发；返回爆发等级字符串或空字符串。

    条件：能量低 + 最近平均反馈负向 + 债务高
    """
    recent_avg = get_recent_feedback_avg(state, strategy)
    for level in sorted(BURST_LEVELS.keys(), key=lambda x: BURST_LEVELS[x]['debt_threshold'], reverse=True):
        thresholds = BURST_LEVELS[level]
        if (state.energy < thresholds["energy_threshold"] and 
            recent_avg < 0 and 
            state.emotion_debt >= thresholds["debt_threshold"]):
            return level

    return ""


# ──────────────────────────────────────────────────────────────────────
# 4. 爆发后恢复机制
# ──────────────────────────────────────────────────────────────────────
def apply_burst_recovery(state: FRRState, burst_level: str) -> None:
    """
    根据爆发等级恢复能量 & 衰减债务，并记录冷却期标记。
    """
    recovery_map = {
        "mild": {"energy_rec": 0.2, "debt_decay": 0.7},
        "moderate": {"energy_rec": 0.1, "debt_decay": 0.5},
        "severe": {"energy_rec": 0.05, "debt_decay": 0.3},
    }
    if burst_level not in recovery_map:
        return

    rec = recovery_map[burst_level]
    state.energy = min(1.0, state.energy + rec["energy_rec"])
    state.emotion_debt *= rec["debt_decay"]

    # 标记冷却周期
    cooling = {"mild": 1, "moderate": 2, "severe": 3}[burst_level]
    setattr(state, "cooling_period", cooling)  # 动态注入字段


# ──────────────────────────────────────────────────────────────────────
# 5.  辅助：综合策略评估（先保留简单实现，可后续扩展）
# ──────────────────────────────────────────────────────────────────────
def evaluate_strategy(state: FRRState, strategy: str) -> Dict[str, float]:
    """
    返回策略效能综合评分，用于未来多策略竞争。
    composite = efficacy*0.6 + stability*0.2 + trend*0.2
    """
    history = [item["feedback"] for item in state.history.get(strategy, [])]
    if not history:
        return dict(efficacy=0.0, stability=0.0, trend=0.0, composite=0.0)

    efficacy = get_recent_feedback_avg(state, strategy)
    volatility = _calculate_std_dev(history)
    stability = 1 - min(1.0, volatility)  # 映射到 [0,1]
    trend = math.tanh(_calculate_regression_slope(list(range(len(history))), history))  # [-1,1]

    composite = efficacy * 0.6 + stability * 0.2 + (trend + 1) / 2 * 0.2
    return dict(efficacy=efficacy, stability=stability, trend=trend, composite=composite)
