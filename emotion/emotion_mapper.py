"""
emotion_mapper.py
─────────────────
将“现代 27 情绪”映射到“达尔文 34 情绪”。

• 数据来源
  - vad_scores.json   : 每个情绪的 (Valence, Arousal, Dominance) 归一化向量
  - darwin_labels.json: 达尔文 34 情绪标签列表（顺序无关）

• 方法
  1. 读取 VAD 词典，构造现代-达尔文两个矩阵。
  2. 使用余弦相似度计算现代情绪与全部达尔文情绪的相似度。
  3. 返回最相近标签及其分数（0-1）。
  4. 若相似度低于阈值 (0.55)，返回 "Unknown" 以提示人工校正。

• 依赖
  - numpy
  - scikit-learn   （只用 pairwise cosine_similarity；对运行环境零侵入）
"""

from pathlib import Path
import json
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity

# --------------------------------------------------------------------------- #
# ❶ 读取数据文件
# --------------------------------------------------------------------------- #
BASE_DIR = Path(__file__).resolve().parent.parent  # = cabsaia/
DATA_DIR = BASE_DIR / "data"                 # 你可改成其它文件夹

VAD_PATH = BASE_DIR / "data" / "vad_scores.json"
DARWIN_PATH = BASE_DIR / "data" / "darwin_labels.json"

with open(VAD_PATH, "r", encoding="utf-8") as f:
    _VAD = json.load(f)                     # dict[str, [v, a, d]]

with open(DARWIN_PATH, "r", encoding="utf-8") as f:
    _DARWIN_LIST = json.load(f)             # list[str]

# 为了方便检索，提取达尔文向量子集（如果缺则降级为零向量）
_darwin_vecs = []
_missing = []
for lbl in _DARWIN_LIST:
    if lbl in _VAD:
        _darwin_vecs.append(_VAD[lbl])
    else:          # 少数行为性词条没有 VAD 分数，填零向量保证维度统一
        _missing.append(lbl)
        _darwin_vecs.append([0.0, 0.0, 0.0])
_DARWIN_MAT = np.array(_darwin_vecs)  # shape = (34, 3)

# --------------------------------------------------------------------------- #
# ❷ 主函数
# --------------------------------------------------------------------------- #
def map_modern_to_darwin(modern_emotion: str, *, threshold: float = 0.55):
    """
    Args
    ----
    modern_emotion : str
        现代 27 情绪标签（区分大小写，需与 vad_scores.json 键一致）
    threshold : float
        相似度下限；低于该值视为“未知/需人工”。
    
    Returns
    -------
    tuple[str, float]
        (最佳匹配达尔文标签 或 "Unknown",  相似度分数)
    """
    if modern_emotion not in _VAD:
        raise ValueError(f"Unknown modern emotion: {modern_emotion!r}")

    vec = np.array(_VAD[modern_emotion]).reshape(1, -1)  # (1, 3)
    sims = cosine_similarity(vec, _DARWIN_MAT)[0]        # (34,)

    idx = int(np.argmax(sims))
    best_sim = float(sims[idx])
    best_label = _DARWIN_LIST[idx]

    # 若本标签缺失 VAD 或分数太低 → Unknown
    if best_label in _missing or best_sim < threshold:
        return "Unknown", best_sim
    return best_label, best_sim


# --------------------------------------------------------------------------- #
# ❸ CLI 简易测试
# --------------------------------------------------------------------------- #
if __name__ == "__main__":
    for emo in ("Awe", "Nostalgia", "Triumph", "Disgust"):
        lbl, score = map_modern_to_darwin(emo)
        print(f"{emo:15s} → {lbl:15s}  ({score:.2f})")
