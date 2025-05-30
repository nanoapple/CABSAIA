# cabsaia/main.py

import datetime
from cabsaia.core.llm_interface import LLMInterface
from cabsaia.processing.emotion_classifier import analyse_emotion_from_text
from cabsaia.state.emotion import EmotionalState
from cabsaia.state.emotion_frr import FRRState
from cabsaia.behavior.role_engine import RoleEngine
from cabsaia import config  # 确保你有这个 config 模块

def print_intro():
    print("=" * 50)
    print("\U0001F916 CABSAIA: Cognitive-Affective Agent (CLI Mode)")
    print(f"\U0001F4C6 Session started: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M')}")
    print("=" * 50)

def main():
    print_intro()

    # 初始化组件
    llm = LLMInterface(config)
    emotion_state = EmotionalState()
    frr_state = FRRState()
    role_engine = RoleEngine(frr_state)

    # 使用默认策略名（可后续动态选择）
    strategy = "reflective_listening"

    while True:
        user_input = input("\n\U0001F5E3️  You: ").strip()
        if user_input.lower() in ["exit", "quit"]:
            print("\nExiting CABSAIA. Goodbye!")
            break

        # 生成系统角色提示词（基于当前状态）
        system_prompt = role_engine.decide_and_generate_prompt(strategy)
        full_prompt = f"{system_prompt}\nUser: {user_input}"

        # 模型回复
        reply = llm.generate(full_prompt)

        # 情绪分析（用于 valence-arousal 投射）
        emotion_result = analyse_emotion_from_text(user_input)
        emotion_state.apply_valence_arousal(
            valence=emotion_result["valence"],
            arousal=emotion_result["arousal"]
        )

        # 显示模型回复和分析结果
        print(f"\n\U0001F916 CABSAIA (Empathizer): {reply}")
        print("\n\U0001F9E0 Emotion Analysis:")
        print(f"   Keywords: {emotion_result['keywords']}")
        print(f"   Valence: {emotion_result['valence']:.2f}, Arousal: {emotion_result['arousal']:.2f}")
        print(f"   Themes: {emotion_result['themes']}")
        print(f"   Expression: {emotion_result['expression']}, Intensity: {emotion_result['intensity']}")
        print(f"   Projected Mood Point: ({emotion_result['valence']:.2f}, {emotion_result['arousal']:.2f})")

        # 模拟反馈打分
        try:
            feedback = float(input("\n\U0001F4DD Please rate the bot's helpfulness (-1.0 to 1.0): "))
        except ValueError:
            feedback = 0.0
            print("   Invalid feedback. Defaulted to 0.0")

        frr_state.update_feedback(strategy, feedback)

if __name__ == "__main__":
    main()
