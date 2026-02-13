"""
cabsaia.emotion  —  Emotion-mapping sub-package
------------------------------------------------
统一对外暴露：
    • map_modern_to_darwin(label)   → (darwin_label, similarity)
    • EmotionMapper()              → 类接口（含批量映射等方法）
"""

from .emotion_mapper import map_modern_to_darwin

__all__ = [
    "map_modern_to_darwin",
    "EmotionMapper",
]
