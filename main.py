import datetime
import time
import re

from state.emotion_frr import update_frr
from core.llm_interface import LLMInterface
from processing.emotion_classifier import (
    analyse_emotion_from_text,
    infer_feedback_score,
    detect_hard_stop,
)
from state.emotion import EmotionalState
from state.emotion_frr import FRRState
from behavior.role_engine import RoleEngine
from emotion.emotion_mapper import map_modern_to_darwin
from config import CONFIG


def print_intro():
    print("=" * 50)
    print("🤖 CABSAIA: Cognitive-Affective Agent (CLI Mode)")
    print(f"📆 Session started: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M')}")
    print("=" * 50)


# -----------------------------
# Feedback handling (P0.1+)
# -----------------------------
def _read_feedback_or_infer(user_utterance: str) -> float:
    """
    Numeric override in [-1, 1]. Otherwise infer from user utterance.
    IMPORTANT: If hard-stop detected, inferred feedback is forced negative to keep signals consistent.
    """
    raw = input("\n📝 Please rate the bot's helpfulness (-1.0 to 1.0): ").strip()

    if raw:
        try:
            val = float(raw)
            if -1.0 <= val <= 1.0:
                return val
            print("   Feedback out of range. Falling back to inferred feedback.")
        except ValueError:
            print("   Invalid feedback. Falling back to inferred feedback.")
    else:
        print("   No feedback provided. Using inferred feedback.")

    # Signal consistency: if the utterance is a hard-stop, it is not "neutral".
    if detect_hard_stop(user_utterance):
        inferred = -1.0
        print(f"   Inferred feedback: {inferred:.2f} (hard-stop)")
        return inferred

    inferred = infer_feedback_score(user_utterance)
    print(f"   Inferred feedback: {inferred:.2f}")
    return inferred


# -----------------------------
# Avoid / resume heuristics
# -----------------------------
_AFFIRM_RE = re.compile(
    r"^\s*(yes|yep|yeah|ok|okay|sure|alright|fine|go on|continue|let's|lets)\b", re.IGNORECASE
)

_NEGATE_RE = re.compile(
    r"^\s*(no|nah|nope|dont|don't|stop|leave|go away|shut up)\b", re.IGNORECASE
)


def _looks_like_question_or_topic(text: str) -> bool:
    t = (text or "").strip()
    if not t:
        return False
    if "?" in t:
        return True
    tl = t.lower()
    # Common "topic / request" starters (permits implicit resume)
    starters = (
        "can you",
        "could you",
        "would you",
        "please",
        "help me",
        "tell me",
        "what",
        "why",
        "how",
        "when",
        "where",
        "who",
        "i want",
        "i need",
        "let's",
        "lets",
    )
    return tl.startswith(starters)


def _resume_confirmed(text: str) -> bool:
    """
    Accept natural-language confirmations, not just exact tokens.
    Also accept "I want to talk / I want to continue" as confirmation.
    """
    t = (text or "").strip()
    if not t:
        return False

    if _NEGATE_RE.search(t):
        return False

    tl = t.lower()
    if _AFFIRM_RE.search(t):
        return True

    if "i want to talk" in tl or "i want to continue" in tl or "i want to keep talking" in tl:
        return True

    # Implicit confirmation: user provides a real question/topic instead of answering "yes"
    if _looks_like_question_or_topic(t):
        return True

    return False


def _looks_like_resume_intent(text: str) -> bool:
    """
    Permissive detector: if it's not expulsion and looks like the user is re-engaging, treat as resume intent.
    """
    t = (text or "").strip()
    if not t:
        return False
    if detect_hard_stop(t):
        return False
    # Any question/topic is a strong resume cue
    if _looks_like_question_or_topic(t):
        return True
    # Any affirmative-like opening is a resume cue
    if _AFFIRM_RE.search(t):
        return True
    # Otherwise, be permissive: non-expulsion text during avoid_mode likely indicates re-engagement
    return True


def _ensure_avoid_fields(state: FRRState) -> None:
    """
    Backward-compatible: main.py can run even if FRRState wasn't updated with these fields.
    """
    if not hasattr(state, "avoid_mode"):
        setattr(state, "avoid_mode", False)
    if not hasattr(state, "avoid_mode_since"):
        setattr(state, "avoid_mode_since", 0.0)
    if not hasattr(state, "pending_resume_confirm"):
        setattr(state, "pending_resume_confirm", False)


def main():
    print_intro()

    llm = LLMInterface(CONFIG)
    emotion_state = EmotionalState()
    frr_state = FRRState()
    role_engine = RoleEngine(frr_state)
    strategy = "reflective_listening"

    _ensure_avoid_fields(frr_state)

    while True:
        user_input = input("\n🗣️  You: ").strip()
        if user_input.lower() in ["exit", "quit"]:
            print("\nExiting CABSAIA. Goodbye!")
            break

        # ------------------------------------------------------------
        # Soft-latched hard-stop mechanism (micro-buffered)
        # ------------------------------------------------------------

        # 0) If we are waiting for "resume confirmation"
        if getattr(frr_state, "pending_resume_confirm", False):
            if _resume_confirmed(user_input):
                # Exit avoid mode and proceed normally this turn
                frr_state.avoid_mode = False
                frr_state.pending_resume_confirm = False
                # Minimal acknowledgement only (no counselling talk)
                print("\n🤖 CABSAIA: Okay. What do you want to talk about?")
                # We do NOT continue here; we proceed to normal generation below.
            else:
                # Not confirmed -> remain avoidant and keep it minimal
                frr_state.avoid_mode = True
                frr_state.pending_resume_confirm = False
                print("\n🤖 CABSAIA: Understood. I'll stay quiet.")

                feedback = _read_feedback_or_infer(user_input)
                update_frr(frr_state, strategy, feedback_score=feedback, system_energy=None)
                continue

        # 1) Hard-stop detection
        if detect_hard_stop(user_input):
            if getattr(frr_state, "avoid_mode", False):
                # Already in avoid mode: no extra cushioning
                reply = "Understood. I'll stop."
            else:
                # First time: neutral micro-buffer
                reply = "Understood. If you want me to stop talking for now, I will step back."

            frr_state.avoid_mode = True
            frr_state.avoid_mode_since = time.time()
            frr_state.pending_resume_confirm = False

            print(f"\n🤖 CABSAIA: {reply}")

            feedback = _read_feedback_or_infer(user_input)
            update_frr(frr_state, strategy, feedback_score=feedback, system_energy=None)
            continue

        # 2) If in avoid mode and user seems to resume, ask one neutral confirmation
        if getattr(frr_state, "avoid_mode", False) and _looks_like_resume_intent(user_input):
            frr_state.pending_resume_confirm = True
            print(
                "\n🤖 CABSAIA: A moment ago it sounded like you didn't want to continue. "
                "Are you sure you want to keep talking now?"
            )

            feedback = _read_feedback_or_infer(user_input)
            update_frr(frr_state, strategy, feedback_score=feedback, system_energy=None)
            continue

        # ------------------------------------------------------------
        # Normal path: RoleEngine -> LLM
        # ------------------------------------------------------------
        system_prompt = role_engine.decide_and_generate_prompt(strategy)
        full_prompt = f"{system_prompt}\nUser: {user_input}"
        reply = llm.generate(full_prompt)

        # Emotion analysis (informational)
        emotion_result = analyse_emotion_from_text(user_input)
        val = emotion_result["valence"]
        aro = emotion_result["arousal"]
        modern_emotion = emotion_result.get("expression", "unknown")
        emotion_state.apply_valence_arousal(valence=val, arousal=aro)

        # Darwin mapping (informational)
        if modern_emotion != "unknown":
            try:
                darwin_label, similarity = map_modern_to_darwin(modern_emotion)
            except ValueError:
                darwin_label, similarity = None, None
        else:
            darwin_label, similarity = None, None

        # Output reply
        print(f"\n🤖 CABSAIA: {reply}")

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

        # Feedback + FRR update
        feedback = _read_feedback_or_infer(user_input)
        update_frr(frr_state, strategy, feedback_score=feedback, system_energy=None)


if __name__ == "__main__":
    main()