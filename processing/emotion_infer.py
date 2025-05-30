# cabsaia/core/emotion_infer.py

from typing import Dict
from cabsaia.resources.emotion_dictionary import EMOTION_KEYWORDS, EMOTION_INTENSITY


def infer_emotion_from_text(text: str) -> Dict[str, float]:
    """从 LLM 回复中提取情绪变化量（valence, arousal, dominance）"""
    text = text.lower()
    delta = {"valence": 0.0, "arousal": 0.0, "dominance": 0.0}

    # 处理强度修饰词
    intensity_score = 1.0
    for level, words in EMOTION_INTENSITY.items():
        if any(w in text for w in words):
            if level == "mild": intensity_score = 0.3
            elif level == "moderate": intensity_score = 0.6
            elif level == "intense": intensity_score = 1.0
            elif level == "severe": intensity_score = 1.2
            break

    # 映射维度得分
    mapping = {
        "positive": ("valence", +0.4),
        "negative": ("valence", -0.4),
        "arousal_high": ("arousal", +0.6),
        "arousal_low": ("arousal", -0.4),
        "dominant": ("dominance", +0.5),
        "submissive": ("dominance", -0.5),
    }

    for category, (dim, base_score) in mapping.items():
        for keyword in EMOTION_KEYWORDS.get(category, []):
            if keyword in text:
                delta[dim] += base_score * intensity_score

    # 范围限制
    for k in delta:
        if k == "valence":
            delta[k] = max(min(delta[k], 1.0), -1.0)
        else:
            delta[k] = max(min(delta[k], 1.0), 0.0)

    return delta
