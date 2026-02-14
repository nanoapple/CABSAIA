import requests
import json
import logging
from config import CONFIG
from typing import Optional


class LLMInterface:
    """
    Interface to communicate with a local LLM model via Ollama HTTP API.
    """

    def __init__(self, config):
        """
        Args:
            config: Configuration object, must contain at least LLM_TEMPERATURE
        """
        self.logger = logging.getLogger(__name__)
        self.config = config
        self.model = "mistral"  # Default Ollama model
        self.api_url = "http://localhost:11434/api/generate"

    def generate(self, prompt: str, temperature: Optional[float] = None) -> str:
        """
        Send a prompt to the local LLM and retrieve the response.

        Args:
            prompt (str): The user's input prompt
            temperature (float, optional): Sampling temperature

        Returns:
            str: Model-generated response, or error message
        """
        temp = temperature if temperature is not None else CONFIG.LLM_TEMPERATURE

        payload = {
            "model": self.model,
            "prompt": prompt,
            "temperature": temp,
            "stream": False
        }

        headers = {
            "Content-Type": "application/json"
        }

        try:
            response = requests.post(
                self.api_url,
                data=json.dumps(payload),
                headers=headers,
                timeout=60
            )
            response.raise_for_status()
            content = response.json().get("response", "").strip()

            if not content:
                self.logger.warning("[LLM] Empty response from Mistral model.")
                return "[LLM Notice] No response generated."

            return content

        except requests.exceptions.Timeout:
            self.logger.error("[LLM Error] Mistral request timed out.")
            return "[LLM Error] Timeout occurred while contacting the model."

        except requests.exceptions.ConnectionError:
            self.logger.error("[LLM Error] Unable to connect to Ollama server.")
            return "[LLM Error] Could not connect to local model. Is Ollama running?"

        except Exception as e:
            self.logger.exception(f"[LLM Error] Unexpected failure: {e}")
            return f"[LLM Error] Unexpected issue: {e}"

    def check_health(self) -> bool:
        """
        Check whether the Ollama server is online.

        Returns:
            bool: True if healthy, False otherwise
        """
        try:
            response = requests.get("http://localhost:11434")
            return response.status_code == 200
        except Exception:
            return False
