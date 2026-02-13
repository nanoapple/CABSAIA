# cabsaia/main.py

import datetime
from cabsaia.state.emotion_frr import update_frr
from cabsaia.core.llm_interface import LLMInterface
from cabsaia.processing.emotion_classifier import analyse_emotion_from_text
from cabsaia.state.emotion import EmotionalState
from cabsaia.state.emotion_frr import FRRState
from cabsaia.behavior.role_engine import RoleEngine
from cabsaia.emotion.emotion_mapper import map_modern_to_darwin
from cabsaia import config

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
    strategy = "reflective_listening"

    while True:
        user_input = input("\n\U0001F5E3️  You: ").strip()
        if user_input.lower() in ["exit", "quit"]:
            print("\nExiting CABSAIA. Goodbye!")
            break

        # 模型回复
        system_prompt = role_engine.decide_and_generate_prompt(strategy)
        full_prompt = f"{system_prompt}\nUser: {user_input}"
        reply = llm.generate(full_prompt)

        # 情绪分析
        emotion_result = analyse_emotion_from_text(user_input)
        val = emotion_result["valence"]
        aro = emotion_result["arousal"]
        modern_emotion = emotion_result.get("expression", "unknown")

        emotion_state.apply_valence_arousal(valence=val, arousal=aro)

        # 映射到 Darwin 标签
        if modern_emotion != "unknown":
            try:
                darwin_label, similarity = map_modern_to_darwin(modern_emotion)
            except ValueError:
                darwin_label, similarity = None, None
        else:
            darwin_label, similarity = None, None

        # 输出回应
        print(f"\n🤖 CABSAIA (Empathizer): {reply}")

        print("\n🧠 Emotion Analysis:")
        print(f"   Keywords: {emotion_result.get('keywords', [])}")
        print(f"   Valence: {val:.2f}, Arousal: {aro:.2f}")
        print(f"   Themes: {emotion_result.get('themes', [])}")
        print(f"   Expression: {modern_emotion}, Intensity: {emotion_result.get('intensity')}")
        print(f"   Projected Mood Point: ({val:.2f}, {aro:.2f})")

        if similarity is not None:
            print(f"   Mapped Darwin Label: {darwin_label} (Similarity: {similarity:.2f})")
        else:
            print("   Darwin Mapping: ❗ Emotion not recognised in modern-27 set.")

        # 用户反馈
        try:
            feedback = float(input("\n📝 Please rate the bot's helpfulness (-1.0 to 1.0): "))
        except ValueError:
            feedback = 0.0
            print("   Invalid feedback. Defaulted to 0.0")

        update_frr(frr_state, strategy, feedback_score=feedback, system_energy=0.8)


if __name__ == "__main__":
    main()
