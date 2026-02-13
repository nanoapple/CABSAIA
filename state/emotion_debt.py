# 文件：cabsaia/state/emotion_debt.py

def calculate_nonlinear_debt(current_debt: float, feedback_strength: float) -> float:
    """
    非线性情绪债务累积模型：
    Dₙ = Dₙ₋₁ + (1 - Dₙ₋₁/θ) * α * S
    """
    threshold = 5.0
    base_growth = 0.5
    intensity_coeff = 0.5 + abs(feedback_strength) * 1.0
    return current_debt + (1 - current_debt / threshold) * base_growth * intensity_coeff


def determine_burst_level(debt: float) -> str:
    """根据情绪债务判定爆发等级"""
    if debt >= 2.5:
        return "severe"
    elif debt >= 1.5:
        return "moderate"
    elif debt > 0.5:
        return "mild"
    else:
        return "baseline"
