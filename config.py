import os
import yaml
from pathlib import Path

class CABSAIAConfig:
    """
    Global configuration for the CABSAIA agent system.
    Includes LLM parameters, emotional model settings, personality traits,
    ethical filters, prompt roles, and resource management.
    """

    def __init__(self):
        # === Basic Paths ===
        self.ROOT_DIR = Path(__file__).resolve().parent
        self.DATA_DIR = self.ROOT_DIR / "data"
        self.LOG_DIR = self.DATA_DIR / "logs"
        self.MODEL_DIR = self.ROOT_DIR / "models"
        self.CONFIG_DIR = self.ROOT_DIR / "config"
        self.PLUGIN_FOLDER = self.ROOT_DIR / "plugins"
        self.PROMPT_DIR = self.ROOT_DIR / "prompts"

        # === Runtime Options ===
        self.DEBUG = True
        self.LOG_LEVEL = "INFO"

        # === LLM Settings ===
        self.DEFAULT_LLM = "gpt-3.5-turbo"
        self.LLM_TEMPERATURE = 0.7
        self.MAX_TOKENS = 1024
        self.ENABLE_CHAIN_OF_THOUGHT = True
        self.COT_TEMPLATE_PATH = self.PROMPT_DIR / "cot_prompt.txt"

        # === Psychological Model ===
        self.PERSONALITY_TYPE = "introvert"
        self.EMOTIONAL_GRANULARITY = 27
        self.RESILIENCE_PROFILE_PATH = self.MODEL_DIR / "resilience_curves.json"
        self.EMOTION_BUFFER_SIZE = 7
        self.INERTIA_DECAY = 0.85
        self.ACTIVATION_DECAY_RATE = 0.92
        self.STRESS_HALFLIFE = 3

        # === Ethics & Filtering ===
        self.ENABLE_ETHICS_FILTER = True
        self.ETHICS_THRESHOLD = 0.7
        self.TABOO_EXPIRY_SECS = 3600

        # === UI / Visualization ===
        self.ENABLE_DASHBOARD = True
        self.DASHBOARD_REFRESH_SECS = 5
        self.UI_THEME = "light"

        # === Memory / Embedding Store ===
        self.MEMORY_PATH = self.DATA_DIR / "memory.json"
        self.VECTOR_STORE_PATH = self.DATA_DIR / "vector_store.faiss"

        # === Role / Prompt Configuration ===
        self.ROLES_PATH = self.CONFIG_DIR / "roles.yaml"
        self.ROLES = self._load_roles()

    def _load_roles(self):
        """Load roles.yaml if it exists, otherwise return an empty dict."""
        if self.ROLES_PATH.exists():
            try:
                with open(self.ROLES_PATH, "r", encoding="utf-8") as f:
                    content = yaml.safe_load(f)
                    return content.get("roles", {})
            except Exception as e:
                print(f"[WARNING] Failed to load roles.yaml: {e}")
        return {}

    def as_dict(self):
        """Return all configuration as a dictionary."""
        return self.__dict__

    def update(self, **kwargs):
        """Dynamically update configuration values."""
        for key, value in kwargs.items():
            if hasattr(self, key):
                setattr(self, key, value)

# Global singleton for system-wide usage
CONFIG = CABSAIAConfig()
