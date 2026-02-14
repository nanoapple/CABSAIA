from __future__ import annotations

import time
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

from state.emotion_debt import calculate_nonlinear_debt

# Default threshold baselines (can be expanded later)
BASE_THRESHOLDS: Dict[str, float] = {
    "energy": 1.0,
    "debt": 2.5,
}


class UserProfile:
    """Minimal user profile; extendable."""
    def __init__(self, personality: str = "neutral"):
        self.personality = personality


@dataclass
class FRRState:
    """
    Feedback-Reference-Regulator (FRR) state.

    Design goals:
    - Maintain stable, simple state variables (debt/resilience/energy).
    - Log feedback history with timestamps for short-window statistics.
    - Provide a *method* recent_avg_feedback() consumed by RoleEngine.
    """
    emotion_debt: float = 0.0
    resilience: float = 1.0

    # History bucketed by strategy (backward compatible with your current code/tests)
    history: Dict[str, List[Dict[str, Any]]] = field(default_factory=dict)

    energy: float = 1.0
    time_active: int = 0

    avoid_mode: bool = False
    avoid_mode_since: float = 0.0
    pending_resume_confirm: bool = False

    user_profile: UserProfile = field(default_factory=UserProfile)

    # NOTE: last_style should be coping style token, not burst key.
    last_style: str = "baseline"
    last_switch_time: float = 0.0  # epoch seconds (used for prompt tone cooldown)

    strategy_state: Dict[str, Dict[str, Any]] = field(default_factory=dict)

    burst_thresholds: Dict[str, float] = field(init=False)

    def __post_init__(self) -> None:
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

    def recent_avg_feedback(self, strategy: str, window_secs: int = 60) -> float:
        """
        Time-windowed average feedback for a given strategy.

        IMPORTANT:
        - Uses epoch timestamps (float) to avoid datetime/float subtraction bugs.
        - Expects history[strategy] entries to have {"feedback": float, "timestamp": float}.
        """
        events = self.history.get(strategy, [])
        if not events:
            return 0.0

        now = time.time()
        recent_scores: List[float] = []
        for item in events:
            ts = item.get("timestamp")
            fb = item.get("feedback", 0.0)
            if isinstance(ts, (int, float)) and (now - float(ts)) <= window_secs:
                recent_scores.append(float(fb))

        return (sum(recent_scores) / len(recent_scores)) if recent_scores else 0.0


# Optional global state instance (as in your original file)
frr_state = FRRState()


def _clamp(x: float, lo: float = 0.0, hi: float = 1.0) -> float:
    return max(lo, min(hi, x))


def _update_energy_internal(state: FRRState, feedback_score: float, external_energy: Optional[float]) -> float:
    """
    P0.2: Energy must be a real state variable, not a constant passthrough.

    - external_energy: optional "system resource" baseline. If None, use state.energy.
    - Negative feedback drains energy (more drain when resilience is low).
    - Positive feedback recovers energy modestly.
    - Neutral slowly decays a bit (small fatigue / inertia).
    """
    base = float(state.energy if external_energy is None else external_energy)

    fb = float(feedback_score)
    res = float(state.resilience)

    if fb < 0:
        # Drain: stronger when resilience is low.
        # fb in [-1,0): abs(fb) in (0,1]
        drain = 0.10 + 0.10 * abs(fb)          # -1 => 0.20
        mod = 1.0 + 0.60 * (1.0 - res)         # res=1 => 1.0, res=0.2 => 1.48
        base -= drain * mod
    elif fb > 0:
        # Recover: slower than drain.
        recover = 0.04 * fb + 0.02 * res       # +1 => up to 0.06
        base += recover
    else:
        # Mild fatigue drift; slightly worse if resilience is low.
        base -= 0.01 * (1.0 + 0.30 * (1.0 - res))

    return _clamp(base, 0.0, 1.0)


def update_frr(
    state: FRRState,
    strategy: str,
    feedback_score: float,
    system_energy: Optional[float] = None,
) -> None:
    """
    Update FRR state with a new feedback sample.

    P0.2 changes:
    - energy is updated internally based on feedback + resilience (and optional external system_energy).
    - caller should pass system_energy=None for normal operation (CLI tests).
    - kept signature backward compatible: system_energy is optional.

    Notes:
    - Stores timestamps as epoch seconds (float) for consistency.
    - Keeps history bucketed by strategy to preserve existing behaviour.
    """
    # Ensure bucket
    if strategy not in state.history:
        state.history[strategy] = []

    fb = float(feedback_score)

    # Update resilience FIRST (so energy modulation can read the updated resilience if you prefer)
    if fb > 0:
        state.resilience = min(1.0, state.resilience + 0.05)
    elif fb < 0:
        state.resilience = max(0.2, state.resilience - 0.03)
    else:
        state.resilience = max(0.2, state.resilience - 0.005)

    # Update energy (dynamic)
    state.energy = _update_energy_internal(state, fb, system_energy)

    # Update emotion debt (delegate to your debt function)
    state.emotion_debt = calculate_nonlinear_debt(state.emotion_debt, fb)

    # Log event (store UPDATED energy)
    state.history[strategy].append(
        {
            "feedback": fb,
            "timestamp": float(time.time()),
            "energy": float(state.energy),
        }
    )


def recent_avg_feedback(events: List[Dict[str, Any]], window: int = 3) -> float:
    """
    Fallback helper for other mechanisms that operate on a plain list of events.
    Kept for compatibility.
    """
    if not events:
        return 0.0
    recent = events[-window:]
    total = sum(float(entry.get("feedback", 0.0)) for entry in recent)
    return total / len(recent)