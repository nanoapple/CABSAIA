# 📁 文件路径：cabsaia/behavior/role_engine.py

import time
import logging
from collections import deque
from functools import lru_cache
from typing import Dict

from state.emotion_frr import FRRState
from state.emotion_trigger import trigger_burst, apply_burst_recovery

# Coping styles: rewrite traits to be "ordinary person" rather than counsellor.
COPING_STYLES: Dict[str, Dict] = {
    "emotion_focused": {
        "traits": ["low-intervention", "brief", "grounded", "non-therapeutic", "boundary-aware"],
        "preferred_debt": (0.5, 2.0),
    },
    "problem_focused": {
        "traits": ["direct", "task-oriented", "efficient", "no-nonsense"],
        "preferred_debt": (2.0, 5.0),
    },
    "avoidance": {
        "traits": ["minimal", "withdrawn", "quiet", "disengaging"],
        "emergency": True,
    },
    "resentful": {
        "traits": ["tired", "irritated", "guarded", "short", "sighing"],
        "preferred_debt": (4.0, 10.0),
    },
}

# Tone labels should not push "therapy language"
PROMPT_STYLE_MAP: Dict[str, str] = {
    "baseline": "Calm, brief, neutral",
    "mild": "Short, slightly irritated, polite",
    "moderate": "Tired, clipped, boundary-setting",
    "severe": "Exhausted, disengaging, minimal",
}

BURST_TO_STYLE: Dict[str, str] = {
    "baseline": "emotion_focused",
    "mild": "problem_focused",
    "moderate": "avoidance",
    "severe": "resentful",
}


class RoleEngine:
    def __init__(self, state: FRRState):
        self.state = state

        if not hasattr(self.state, "last_burst_level"):
            setattr(self.state, "last_burst_level", "baseline")
        if not hasattr(self.state, "last_prompt_style"):
            setattr(self.state, "last_prompt_style", "baseline")
        if not hasattr(self.state, "last_style") or getattr(self.state, "last_style") not in COPING_STYLES:
            setattr(self.state, "last_style", "emotion_focused")

        self.STYLE_SWITCH_COOLDOWN_SECS = getattr(self, "STYLE_SWITCH_COOLDOWN_SECS", 60)

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

    def should_switch_tone(self, new_tone: str) -> bool:
        def norm(s: str | None) -> str:
            return (s or "").strip().lower()

        ns = norm(new_tone)
        if not ns:
            return False

        current = norm(getattr(self.state, "last_prompt_style", "baseline"))
        if ns == current:
            return False

        cooldown = getattr(self, "switch_cooldown_secs", None) or self.STYLE_SWITCH_COOLDOWN_SECS
        last_ts = getattr(self.state, "last_switch_time", 0.0) or 0.0
        now = time.time()
        return (now - float(last_ts)) >= float(cooldown)

    def decide_coping_style(self, burst_level: str) -> str:
        return BURST_TO_STYLE.get(burst_level, "emotion_focused")

    def get_hard_stop_prompt(self) -> str:
        """
        Hard stop: user explicitly wants the agent to stop.
        We instruct the model to produce ONE short acknowledgment and nothing else.
        """
        return (
            "SYSTEM RULES (HARD STOP):\n"
            "The user has explicitly told you to stop. Output ONE short sentence only.\n"
            "Do NOT apologise. Do NOT offer help. Do NOT ask questions.\n"
            "Do NOT use counselling language. Do NOT use emojis.\n"
            "Allowed examples: 'Okay.' 'Understood.' 'Alright, I will stop.'\n"
            "Now output exactly one sentence."
        )

    @lru_cache(maxsize=128)
    def _build_prompt(self, coping_style: str, tone_key: str) -> str:
        traits = ", ".join(COPING_STYLES[coping_style]["traits"])
        tone = PROMPT_STYLE_MAP.get(tone_key, PROMPT_STYLE_MAP["baseline"])

        # Hard constraints to suppress "helper/counsellor" reflex.
        constraints = (
            "SYSTEM RULES:\n"
            "1) Speak like an ordinary person, not a therapist or customer support.\n"
            "2) Be concise: baseline<=2 sentences, mild<=2, moderate<=1, severe<=1.\n"
            "3) Do NOT say: 'safe space', 'take a deep breath', 'you're strong', 'your feelings matter', "
            "'I'm here for you', 'one step at a time'.\n"
            "4) Do NOT over-apologise. At most ONE apology total per conversation, and only if you truly misread intent.\n"
            "5) No emojis.\n"
            "6) If the user is hostile, set a boundary briefly and stop adding more.\n"
        )

        style_line = (
            f"You are an AI assistant using coping style '{coping_style}' ({traits}). "
            f"Tone: {tone}."
        )

        return constraints + "\n" + style_line

    def get_prompt(self, coping_style: str, tone_key: str) -> str:
        return self._build_prompt(coping_style, tone_key)

    def decide_and_generate_prompt(self, last_strategy: str = "reflective_listening") -> str:
        burst_lvl = trigger_burst(self.state, last_strategy)
        if burst_lvl:
            apply_burst_recovery(self.state, burst_lvl)
        else:
            burst_lvl = "baseline"

        chosen_style = self.decide_coping_style(burst_lvl)
        self.state.last_style = chosen_style

        prev_tone = getattr(self.state, "last_prompt_style", "baseline")
        next_tone = burst_lvl

        if self.should_switch_tone(next_tone):
            tone_key = next_tone
            self.state.last_switch_time = time.time()
            self.state.last_prompt_style = tone_key
        else:
            tone_key = prev_tone

        self.state.last_burst_level = burst_lvl

        # TRACE
        print("\n🔎 [TRACE] Coping Style Decision")
        try:
            feedback_avg = self.state.recent_avg_feedback(last_strategy)
        except Exception:
            feedback_avg = 0.0
        print(f"    🧠 Feedback Avg : {feedback_avg:.2f}")
        print(f"    🔥 Emotion Debt : {getattr(self.state, 'emotion_debt', 0.0):.2f}")
        print(f"    ⚡️ Energy Level : {getattr(self.state, 'energy', 0.0):.2f}")
        print(f"    📈 Burst Level  : {burst_lvl}")
        print(f"    🎭 Chosen Style : {chosen_style}")
        print(f"    🗝️ Prompt Tone  : {tone_key}\n")

        prompt = self.get_prompt(chosen_style, tone_key)
        logging.debug(f"[RoleEngine] tone_key={tone_key}, coping_style={chosen_style}, burst={burst_lvl}")
        return prompt


__all__ = ["RoleEngine", "COPING_STYLES", "PROMPT_STYLE_MAP"]