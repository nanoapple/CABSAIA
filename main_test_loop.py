# 📁 文件路径：cabsaia/main_test_loop.py

import time
from state.emotion_frr import frr_state, update_frr
from behavior.role_engine import RoleEngine
from core.llm_interface import LLMInterface
from config import CONFIG
from processing.emotion_classifier import infer_feedback_score


# 初始化
llm = LLMInterface(CONFIG)
role_engine = RoleEngine(frr_state)

if not llm.check_health():
    print("❌ Ollama 未运行或无法连接。请先启动 Ollama 并确认 11434 端口可用。")
    exit(1)


def simulate_feedback(state, feedback_score: float, energy: float = 0.8, count: int = 1):
    for _ in range(count):
        update_frr(state, "reflective_listening", feedback_score=feedback_score, system_energy=energy)
        time.sleep(0.1)


def main_loop():
    print("🧪 CABSAIA Prompt Style Test Console")
    print("Type your input, or use commands: [mild] [moderate] [severe] [reset] [exit]\n")

    while True:
        user_input = input("User: ").strip()

        if user_input.lower() == "exit":
            break

        if user_input.lower() == "reset":
            frr_state.emotion_debt = 0.0
            frr_state.energy = 1.0
            frr_state.resilience = 1.0
            frr_state.history.clear()
            frr_state.strategy_state.clear()
            # 这些字段是 role_engine 挂上的，重置也一并处理
            if hasattr(frr_state, "last_burst_level"):
                frr_state.last_burst_level = "baseline"
            if hasattr(frr_state, "last_prompt_style"):
                frr_state.last_prompt_style = "emotion_focused"
            if hasattr(frr_state, "last_style"):
                frr_state.last_style = "emotion_focused"
            print("🔄 State reset.\n")
            continue

        if user_input.lower() == "mild":
            simulate_feedback(frr_state, feedback_score=-1.0, energy=0.6, count=3)
            print("🟠 Simulated mild distress\n")
            continue

        if user_input.lower() == "moderate":
            simulate_feedback(frr_state, feedback_score=-1.0, energy=0.4, count=5)
            print("🔴 Simulated moderate distress\n")
            continue

        if user_input.lower() == "severe":
            simulate_feedback(frr_state, feedback_score=-1.0, energy=0.2, count=7)
            print("🚨 Simulated severe distress\n")
            continue

        # ⭐ 自动情绪反馈评分 + 状态更新（闭环）
        score = infer_feedback_score(user_input)
        update_frr(frr_state, "reflective_listening", feedback_score=score, system_energy=0.6)

        # ✅ 唯一人格决策入口（内部会写 state.last_burst_level / state.last_prompt_style）
        prompt = role_engine.decide_and_generate_prompt("reflective_listening")

        chosen_style = getattr(frr_state, "last_prompt_style", getattr(frr_state, "last_style", "emotion_focused"))
        burst_level = getattr(frr_state, "last_burst_level", "baseline")

        # 输出结构化调试信息（与 role_engine 一致）
        print("\n📋 Prompt Diagnostic Output")
        print("-" * 50)
        print(f"🧠 Coping Style   : {chosen_style}")
        print(f"🔥 Burst Level    : {burst_level}")
        print(f"🎯 Feedback Score : {score:.2f}")
        print(f"\n📝 Prompt:\n{prompt}")
        print("-" * 50)

        # 生成回应
        response = llm.generate(prompt + "\nUser: " + user_input)
        print("🤖 AI:", response)
        print("=" * 60)


if __name__ == "__main__":
    main_loop()