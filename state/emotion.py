# cabsaia/state/emotion.py

from dataclasses import dataclass
import math
import random
from typing import Dict

THRESHOLDS = {
    'burnout': 5.0,                # 超过此债务阈值即进入情绪耗竭状态
    'resilience_floor': 0.2        # 弹性最低保护限
}

@dataclass
class EmotionalState:
    """
    增强型情绪状态类：支持动态恢复、人格建模、应对策略选择
    """
    valence: float = 0.0            # 情绪正负性（-1~1）
    arousal: float = 0.0            # 激活水平（0~1）
    dominance: float = 0.0          # 控制感（0~1）
    resilience: float = 1.0         # 情绪弹性（越高越易恢复）
    emotion_debt: float = 0.0       # 情绪负荷（累计的负面影响）
    personality_type: str = "neutral"  # 人格类型
    last_update: float = 0.0        # 最近一次更新时间（未来拓展用）

    def __post_init__(self):
        """初始化后载入人格配置和恢复模型参数"""
        self._load_personality_params()
        self._init_recovery_model()

    def _load_personality_params(self):
        """加载人格类型对应的情绪恢复参数"""
        self.personality_params = {
            "introvert":  {"recovery_rate": 0.05, "arousal_base": 0.3, "dominance_decay": 0.95},
            "extrovert":  {"recovery_rate": 0.10, "arousal_base": 0.7, "dominance_decay": 0.85},
            "neurotic":   {"recovery_rate": 0.02, "arousal_base": 0.5, "dominance_decay": 0.9},
            "neutral":    {"recovery_rate": 0.07, "arousal_base": 0.5, "dominance_decay": 0.9},
        }
        self.params = self.personality_params[self.personality_type]

    def _init_recovery_model(self):
        """初始化恢复模型的时间影响系数"""
        self.time_factor = 0.1
        self.debt_recovery_rate = 0.05
    
    def apply_valence_arousal(self, valence: float, arousal: float, dominance: float = 0.0, weight: float = 1.0):
        """直接设置 valence/arousal/dominance（可选）为新值（带权重），用于与LLM等外部模块交互"""
        self.valence = self._clamp(self.valence * (1 - weight) + valence * weight, -1.0, 1.0)
        self.arousal = self._clamp(self.arousal * (1 - weight) + arousal * weight, 0.0, 1.0)
        self.dominance = self._clamp(self.dominance * (1 - weight) + dominance * weight, 0.0, 1.0)

    def update(self, delta_valence: float, delta_arousal: float = 0.0, delta_dominance: float = 0.0):
        """
        应用一次情绪变化事件：更新valence/arousal/dominance 并计算债务与弹性
        """
        self.valence = self._clamp(self.valence + delta_valence, -1.0, 1.0)
        self.arousal = self._clamp(self.arousal + delta_arousal, 0.0, 1.0)
        self.dominance = self._clamp(self.dominance + delta_dominance, 0.0, 1.0)

        self.emotion_debt += abs(delta_valence)  # 累计负面事件造成的心理负荷

        # 调整弹性，情绪负荷越高则恢复能力下降
        self.resilience = max(
            THRESHOLDS['resilience_floor'],
            1.0 - (self.emotion_debt / 10) * (1.0 - self.params['dominance_decay'])
        )

    def apply_emotional_maintenance(self, time_passed: float):
        """
        应用一段时间过去后的情绪自然恢复过程
        """
        self.valence = self._exponential_decay(self.valence, self.params['recovery_rate'] * time_passed)
        self.arousal = self._linear_interpolate(self.arousal, self.params['arousal_base'], self.params['recovery_rate'] * time_passed)
        self.emotion_debt = max(0, self.emotion_debt - time_passed * self.debt_recovery_rate)
        self.resilience = min(1.0, self.resilience + time_passed * self.params['recovery_rate'] * 0.1)

    def check_burnout_risk(self) -> bool:
        """情绪负荷是否已达到耗竭风险阈值"""
        if self.emotion_debt > THRESHOLDS['burnout']:
            self._trigger_coping_mechanism()
            return True
        return False

    def _trigger_coping_mechanism(self):
        """根据当前状态触发自我应对机制"""
        strategy = self.select_coping_strategy()
        if strategy == "problem_focused":
            self.valence *= 0.5
            self.dominance *= 0.7
        elif strategy == "emotion_focused":
            self.valence = self._exponential_decay(self.valence, 0.2)
            self.resilience *= 0.8
        elif strategy == "relaxation":
            self.arousal = self._exponential_decay(self.arousal, 0.3)
            self.emotion_debt = max(0, self.emotion_debt - 1.0)

    def select_coping_strategy(self) -> str:
        """策略选择逻辑：根据当前 valence / dominance / arousal 决定应对类型"""
        if self.valence < -0.5 and self.dominance > 0.5:
            return "problem_focused"
        elif self.valence < -0.5 and self.dominance < 0.5:
            return "emotion_focused"
        elif self.arousal > 0.8:
            return "relaxation"
        return "none"

    def get_2d_projection(self) -> Dict[str, float]:
        """将当前情绪状态映射到二维空间（用于可视化）"""
        x = self.valence * self.arousal
        y = self.dominance * (1 - abs(self.valence))
        return {"x": x, "y": y}

    def reset(self):
        """重置情绪状态为初始值"""
        self.valence = 0.0
        self.arousal = 0.0
        self.dominance = 0.0
        self.resilience = 1.0
        self.emotion_debt = 0.0

    # 工具函数
    def _clamp(self, value: float, min_val: float, max_val: float) -> float:
        return max(min_val, min(value, max_val))

    def _exponential_decay(self, value: float, decay_rate: float) -> float:
        return value * math.exp(-decay_rate)

    def _linear_interpolate(self, start: float, end: float, factor: float) -> float:
        return start + (end - start) * factor
