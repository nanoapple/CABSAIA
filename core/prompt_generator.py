import yaml
import logging
import random
from typing import Any

class PromptGenerator:
    """
    Constructs prompts for the CABSAIA agent based on emotional state and role configuration.
    Loads role descriptions from a YAML file and supports multi-dimensional emotion labeling.
    """

    def __init__(self, config_path: str = "config/roles.yaml"):
        self.logger = logging.getLogger(__name__)
        try:
            with open(config_path, 'r') as f:
                self.role_config = yaml.safe_load(f)['roles']
        except Exception as e:
            self.logger.error(f"Failed to load role config: {e}")
            self.role_config = {}

        self.default_instruction = (
            "You are a cognitively and emotionally self-regulating AI agent. "
            "You respond to users based on your current emotional state and a dynamic personality role. "
            "Your tone should be empathetic, clear, and adjusted according to the situation."
        )

    def _get_emotion_label(self, valence: float, arousal: float, dominance: float) -> str:
        """Return a categorical label based on multidimensional emotion state."""
        if valence > 0.5 and arousal > 0.5:
            return "Excited"
        elif valence < -0.5 and arousal > 0.5:
            return "Angry"
        elif valence < -0.5 and arousal < 0.5:
            return "Depressed"
        elif dominance > 0.5 and valence > 0:
            return "Confident"
        else:
            return "Neutral"

    def get_role_description(self, role: str) -> str:
        """Retrieve the description for a given role."""
        return self.role_config.get(role, {}).get('description', "clear and informative, without emotional leaning")

    def build_prompt(self, user_input: str, role: str, emotion_state: Any) -> str:
        """
        Build a language model prompt based on input, role and emotional state.

        Args:
            user_input (str): The user input string
            role (str): The current personality role
            emotion_state (Any): Object with valence, arousal, dominance, resilience, emotion_debt

        Returns:
            str: The constructed prompt string
        """
        try:
            valence = float(getattr(emotion_state, 'valence', 0.0))
            arousal = float(getattr(emotion_state, 'arousal', 0.0))
            dominance = float(getattr(emotion_state, 'dominance', 0.0))
            resilience = float(getattr(emotion_state, 'resilience', 1.0))
            emotion_debt = float(getattr(emotion_state, 'emotion_debt', 0.0))
        except Exception as e:
            self.logger.warning(f"Emotion state parsing failed: {e}")
            valence, arousal, dominance, resilience, emotion_debt = 0.0, 0.0, 0.0, 1.0, 0.0

        emotion_label = self._get_emotion_label(valence, arousal, dominance)
        role_style = self.get_role_description(role)

        prompt_parts = [
            self.default_instruction,
            f"[Role]: {role} ({role_style})",
            f"[Emotion]: V={valence:.2f}, A={arousal:.2f}, D={dominance:.2f}, R={resilience:.2f}, Debt={emotion_debt:.2f}",
            f"[Emotion Label]: {emotion_label}",
            f"User says: {user_input}",
            f"Respond in the tone of a {role}."
        ]

        return "\n".join(prompt_parts)
