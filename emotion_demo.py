# emotion_demo.py

# cabsaia/emotion_demo.py
import matplotlib.pyplot as plt
from cabsaia.state.emotion import EmotionalState

def simulate_emotion_trajectory(personality_type: str, steps: int = 10, time_step: float = 1.0):
    """模拟指定人格类型在一段时间内的情绪轨迹"""
    state = EmotionalState(personality_type=personality_type)
    x_vals, y_vals = [], []

    print(f"\n模拟开始：人格 = {personality_type}")
    for i in range(steps):
        # 模拟逐步负面事件冲击 + 恢复
        delta_d = {
            "introvert": 0.01,
            "extrovert": 0.05,
            "neurotic":  -0.02
        }[personality_type]
        state.update(delta_valence=-0.2 + 0.05 * i, delta_arousal=0.1, delta_dominance=delta_d)
        state.apply_emotional_maintenance(time_passed=time_step)
        projection = state.get_2d_projection()
        x_vals.append(projection["x"])
        y_vals.append(projection["y"])
        print(f"Step {i+1}: Valence={state.valence:.2f}, Arousal={state.arousal:.2f}, Projection=({projection['x']:.2f}, {projection['y']:.2f})")

    return x_vals, y_vals

# 模拟三种人格
trajectories = {}
for p_type in ["introvert", "extrovert", "neurotic"]:
    x, y = simulate_emotion_trajectory(p_type)
    trajectories[p_type] = (x, y)

# 可视化轨迹
for p_type, (x_vals, y_vals) in trajectories.items():
    plt.plot(x_vals, y_vals, marker='o', label=p_type)

plt.title("🎯 情绪轨迹（不同人格类型）")
plt.xlabel("Valence × Arousal")
plt.ylabel("Dominance × (1 - |Valence|)")
plt.grid(True)
plt.legend()
plt.tight_layout()

# 显式显示窗口
print("\n✅ 模拟完成，即将显示图像窗口...")
plt.show()
