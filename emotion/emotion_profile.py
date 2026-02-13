
import json
import os
from typing import Dict, Tuple, Optional, List
from math import sqrt
import numpy as np

class EmotionProfile:
    def __init__(self, vad_path: str = "data/vad_scores.json"):
        if not os.path.exists(vad_path):
            raise FileNotFoundError(f"VAD file not found at: {vad_path}")
        with open(vad_path, "r") as f:
            self.vad_scores: Dict[str, Tuple[float, float, float]] = json.load(f)
        self._normalise_vectors()

    def _normalise_vectors(self):
        for key, vec in self.vad_scores.items():
            norm = sqrt(sum(v ** 2 for v in vec)) or 1.0
            self.vad_scores[key] = tuple(v / norm for v in vec)

    def get_vad(self, emotion: str) -> Optional[Tuple[float, float, float]]:
        return self.vad_scores.get(emotion.lower())

    def similarity(self, emo1: str, emo2: str) -> float:
        v1 = self.get_vad(emo1)
        v2 = self.get_vad(emo2)
        if not v1 or not v2:
            return 0.0
        vec1 = np.array(v1)
        vec2 = np.array(v2)
        sim = np.dot(vec1, vec2) / (np.linalg.norm(vec1) * np.linalg.norm(vec2))
        return float(sim)

    def closest_match(self, emotion: str, candidates: List[str]) -> str:
        best_score = -1.0
        best_match = None
        for cand in candidates:
            score = self.similarity(emotion, cand)
            if score > best_score:
                best_score = score
                best_match = cand
        return best_match if best_match else candidates[0]
