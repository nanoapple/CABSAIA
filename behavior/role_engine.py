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

# ──────────────────────────────────────────────────────────────────────
# 1. Coping-Style 词典（可自行扩充）
# ──────────────────────────────────────────────────────────────────────
COPING_STYLES: Dict[str, Dict] = {
    "emotion_focused": {
        "traits": ["soothing", "validating", "reassuring"],
        "preferred_debt": (0.5, 2.0),
    },
    "problem_focused": {
        "traits": ["actionable", "directive", "solution-oriented"],
        "preferred_debt": (2.0, 5.0),
    },
    "avoidance": {  # 紧急回避
        "traits": ["diverting", "distracting"],
        "emergency": True,
    },
}

# Prompt 语气映射表（可配合 burst_level 使用）
PROMPT_STYLE_MAP: Dict[str, str] = {
    "baseline": "Calm and empathetic",
    "mild": "Slightly assertive, but still polite",
    "moderate": "Firm and urgent, prioritising user safety",
    "severe": "Direct and commanding, immediate action required",
}

# ──────────────────────────────────────────────────────────────────────
# 2. RoleEngine 主体
# ──────────────────────────────────────────────────────────────────────
class RoleEngine:
    def __init__(self, state: FRRState):
        self.state = state

    # ---------- 冷却 & 反馈维护 ----------
    def update_strategy_cooldown(self, strategy: str) -> None:
        """根据近期反馈动态调整冷却期"""
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

    # ---------- 风格切换抑制 ----------
    def should_switch_style(self, next_style: str) -> bool:
        """
        防止频繁切换；若同风格或冷却期未到，返回 False。
        相似度可简化为文本重合率；此处示范用字符串交集长度。
        """
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

    # ---------- Prompt 生成（带缓存） ----------
    @lru_cache(maxsize=128)
    def _build_prompt(self, coping_style: str, burst_level: str) -> str:
        traits = ", ".join(COPING_STYLES[coping_style]["traits"])
        tone   = PROMPT_STYLE_MAP.get(burst_level, PROMPT_STYLE_MAP["baseline"])
        return (
            f"You are an AI assistant adopting a {coping_style} strategy "
            f"({traits}). Respond with a tone that is {tone}."
        )

    def get_prompt(self, coping_style: str, burst_level: str) -> str:
        return self._build_prompt(coping_style, burst_level)

    # ---------- 主入口：根据当前状态给出 prompt ----------
    def decide_and_generate_prompt(self, last_strategy: str = "reflective_listening") -> str:
        # ① 触发爆发检测
        burst_lvl = trigger_burst(self.state, last_strategy)
        if burst_lvl:
            apply_burst_recovery(self.state, burst_lvl)
        else:
            burst_lvl = "baseline"

        # ② 选择 coping_style
        debt = self.state.emotion_debt
        chosen_style = "emotion_focused"  # 默认
        for style, cfg in COPING_STYLES.items():
            if cfg.get("emergency") and burst_lvl in ("moderate", "severe"):
                chosen_style = style
                break
            lo, hi = cfg.get("preferred_debt", (0, 10))
            if lo <= debt <= hi:
                chosen_style = style
                break

        # ③ 风格切换抑制
        if not self.should_switch_style(chosen_style):
            chosen_style = self.state.last_style

        # ④ 生成 prompt
        prompt = self.get_prompt(chosen_style, burst_lvl)
        logging.debug(f"[RoleEngine] prompt_style={chosen_style}, burst={burst_lvl}")
        return prompt

# 如果你希望 test_role_engine.py 能直接导入这两个函数
def dummy_state_for_test() -> FRRState:
    """
    用于测试目的创建的 FRRState 示例
    """
    state = FRRState()
    state.strategy_state = {
        "reflective_listening": {
            "cooldown": 2,
            "recent_feedback": deque([-1.0, -0.5, -1.0], maxlen=5)
        }
    }
    state.last_style = "calm"
    state.last_switch_time = time.time() - 100  # 模拟之前已切换过
    return state

__all__ = [
    "RoleEngine",
    "COPING_STYLES",
    "PROMPT_STYLE_MAP",
    "dummy_state_for_test",
]
