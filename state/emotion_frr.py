# 📁 cabsaia/state/emotion_frr.py

from __future__ import annotations
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Dict, List, Optional
from cabsaia.state.emotion_debt import calculate_nonlinear_debt


# 默认阈值基准
BASE_THRESHOLDS = {
    "energy": 1.0,
    "debt": 2.5
}

class UserProfile:
    """简化版用户画像，可扩展"""
    def __init__(self, personality: str = "neutral"):
        self.personality = personality


@dataclass
class FRRState:
    """
    情绪参照调节器状态对象
    """
    emotion_debt: float = 0.0
    resilience: float = 1.0
    history: Dict[str, List[Dict[str, Any]]] = field(default_factory=dict)
    energy: float = 1.0
    time_active: int = 0
    user_profile: UserProfile = field(default_factory=UserProfile)
    last_style: str = "baseline"
    last_switch_time: float = 0.0
    strategy_state: Dict[str, Dict[str, Any]] = field(default_factory=dict)
    burst_thresholds: Dict[str, float] = field(init=False)

    def __post_init__(self):
        self.burst_thresholds = {
            "energy": self._calc_threshold("energy"),
            "debt": self._calc_threshold("debt"),
        }

    def _calc_threshold(self, metric: str) -> float:
        base = BASE_THRESHOLDS[metric]
        p = self.user_profile.personality
        if p == "resilient":
            return base * 0.8
        if p == "neurotic":
            return base * 1.2
        return base

    def recent_avg_feedback(self, strategy: str, window_secs: int = 300) -> float:
        if strategy not in self.history:
            return 0.0
        now = datetime.utcnow().timestamp()
        relevant = [
            item for item in self.history[strategy]
            if now - item["timestamp"] <= window_secs
        ]
        if not relevant:
            return 0.0
        return sum(item["feedback"] for item in relevant) / len(relevant)


# 🌐 全局状态（可选）
frr_state = FRRState()


# 独立函数：更新状态
def update_frr(state: FRRState, strategy: str, feedback_score: float, system_energy: float):
    now = datetime.utcnow()

    if strategy not in state.history:
        state.history[strategy] = []

    state.history[strategy].append({
        "feedback": feedback_score,
        "timestamp": now.timestamp()
    })

    state.emotion_debt = calculate_nonlinear_debt(state.emotion_debt, feedback_score)

    if feedback_score > 0:
        state.resilience = min(1.0, state.resilience + 0.05)
    elif feedback_score < 0:
        state.resilience = max(0.2, state.resilience - 0.03)
        state.resilience = max(0.2, state.resilience - 0.005)
    else:
        state.resilience = max(0.2, state.resilience - 0.005)


# 备用函数：仅用于其他机制调用
def recent_avg_feedback(history: List[Dict[str, Any]], window: int = 3) -> float:
    if not history:
        return 0.0
    recent = history[-window:]
    total = sum(entry.get("feedback", 0.0) for entry in recent)
    return total / len(recent)
