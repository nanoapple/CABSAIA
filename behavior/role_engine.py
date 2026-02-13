"""
role_engine.py
──────────────
负责 ①根据 FRRState 选择应对风格（coping style）
    ②在爆发等级/冷却期等条件下抑制高频切换
    ③动态维护各策略的冷却时间
    ④生成 prompt（可缓存）供上层调用
"""

import time
import logging
from collections import deque
from functools import lru_cache
from typing import Dict, List

from cabsaia.state.emotion_frr import FRRState
from cabsaia.state.emotion_trigger import trigger_burst, apply_burst_recovery
from cabsaia.emotion.emotion_profile import EmotionProfile


# Coping style 定义
COPING_STYLES: Dict[str, Dict] = {
    "emotion_focused": {
        "traits": ["soothing", "validating", "reassuring", "empathetic", "affirmative"],
        "preferred_debt": (0.5, 2.0),
    },
    "problem_focused": {
        "traits": ["actionable", "directive", "solution-oriented", "strategic"],
        "preferred_debt": (2.0, 5.0),
    },
    "avoidance": {
        "traits": ["diverting", "distracting", "avoidant", "distant", "silent"],
        "emergency": True,
    },
    "resentful": {
        "traits": ["anxious", "passive-aggressive", "withdrawn", "aggressive", "disdainful"],
        "preferred_debt": (4.0, 10.0),
        "negative_expressions": True,
        "breakdown_signs": True
    },
}

PROMPT_STYLE_MAP: Dict[str, str] = {
    "baseline": "Calm and conversational",
    "mild": "Brief, slightly irritated, but polite",
    "moderate": "Frustrated, reactive, emotionally tired, mild anxious",
    "severe": "Exhausted, disinterested, passive-aggressive, defensive",
}


class RoleEngine:
    def __init__(self, state: FRRState):
        self.state = state

    def update_strategy_cooldown(self, strategy: str) -> None:
        ss = self.state.strategy_state.setdefault(
            strategy, {"cooldown": 1, "recent_feedback": deque(maxlen=5)}
        )
        feedback = ss["recent_feedback"]
        if not feedback:
            return
        avg = sum(feedback) / len(feedback)
        if avg < -0.5:
            ss["cooldown"] = min(10, ss["cooldown"] + 2)
        elif avg < 0:
            ss["cooldown"] = max(1, ss["cooldown"] - 1)

    def should_switch_style(self, next_style: str) -> bool:
        curr = self.state.last_style
        if next_style == curr:
            return False
        similarity = self._style_similarity(curr, next_style)
        elapsed = time.time() - self.state.last_switch_time
        if similarity < 0.6 and elapsed > 60:
            self.state.last_switch_time = time.time()
            self.state.last_style = next_style
            return True
        return False

    @staticmethod
    def _style_similarity(a: str, b: str) -> float:
        set_a, set_b = set(a.split()), set(b.split())
        inter = len(set_a & set_b)
        union = len(set_a | set_b) or 1
        return inter / union

    @lru_cache(maxsize=128)
    def _build_prompt(self, coping_style: str, burst_level: str) -> str:
        traits = ", ".join(COPING_STYLES[coping_style]["traits"])
        tone = PROMPT_STYLE_MAP.get(burst_level, PROMPT_STYLE_MAP["baseline"])
        return (
            f"You are an AI assistant adopting a {coping_style} strategy "
            f"({traits}). Respond with a tone that is {tone}."
        )

    def get_prompt(self, coping_style: str, burst_level: str) -> str:
        return self._build_prompt(coping_style, burst_level)

    def decide_coping_style(self, strategy: str) -> str:
        feedback_score = self.state.recent_avg_feedback(strategy)
        debt = self.state.emotion_debt
        energy = self.state.energy

        if debt > 3 or feedback_score < -0.8:
            burst_level = "severe"
        elif debt > 2.5 or feedback_score < -0.6:
            burst_level = "moderate"
        elif debt > 1.5 or feedback_score < -0.3:
            burst_level = "mild"
        else:
            burst_level = "baseline"

        if burst_level == "severe":
            style = "resentful"  
        elif burst_level == "moderate":
            style = "avoidance"
        elif burst_level == "mild":
            style = "problem_focused"
        else:
            style = "emotion_focused"

        # TRACE
        print("\n🔎 [TRACE] Coping Style Decision")
        print(f"    🧠 Feedback Avg : {feedback_score:.2f}")
        print(f"    🔥 Emotion Debt : {debt:.2f}")
        print(f"    ⚡️ Energy Level : {energy:.2f}")
        print(f"    📈 Burst Level  : {burst_level}")
        print(f"    🎭 Chosen Style : {style}\n")

        self.state.last_style = style
        return style


    def decide_and_generate_prompt(self, last_strategy: str = "reflective_listening") -> str:
        burst_lvl = trigger_burst(self.state, last_strategy)
        if burst_lvl:
            apply_burst_recovery(self.state, burst_lvl)
        else:
            burst_lvl = "baseline"

        style = self.decide_coping_style(last_strategy)

        if not self.should_switch_style(style):
            style = self.state.last_style

        prompt = self.get_prompt(style, burst_lvl)
        logging.debug(f"[RoleEngine] prompt_style={style}, burst={burst_lvl}")
        return prompt


# 测试辅助函数
def dummy_state_for_test() -> FRRState:
    from collections import deque
    state = FRRState()
    state.strategy_state = {
        "reflective_listening": {
            "cooldown": 2,
            "recent_feedback": deque([-1.0, -0.5, -1.0], maxlen=5)
        }
    }
    state.last_style = "calm"
    state.last_switch_time = time.time() - 100
    return state


__all__ = [
    "RoleEngine",
    "COPING_STYLES",
    "PROMPT_STYLE_MAP",
    "dummy_state_for_test",
]
