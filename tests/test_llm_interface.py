# cabsaia/tests/test_llm_interface.py

import os
import sys
import pytest
import logging

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from core.llm_interface import LLMInterface
from config import CABSAIAConfig


@pytest.fixture(scope="module")
def llm():
    logging.basicConfig(level=logging.INFO)
    config = CABSAIAConfig()
    return LLMInterface(config)


def test_health_check(llm):
    assert isinstance(llm.check_health(), bool), "check_health() should return a boolean"
    print(f"Ollama health: {'✅ online' if llm.check_health() else '❌ offline'}")


def test_generate_success(llm):
    if not llm.check_health():
        pytest.skip("Ollama is not running; skipping generation test.")
    
    prompt = "Explain what emotional resilience means for a trauma survivor."
    response = llm.generate(prompt)
    print("Model response:", response)
    
    assert isinstance(response, str)
    assert len(response) > 10, "Response too short, possibly malformed"


def test_generate_connection_error():
    # Fake config with wrong port to simulate connection error
    class DummyConfig:
        LLM_TEMPERATURE = 0.7
    
    broken_llm = LLMInterface(DummyConfig())
    broken_llm.api_url = "http://localhost:9999/api/generate"  # Deliberately wrong port
    
    result = broken_llm.generate("Hello")
    print("Connection Error Test Output:", result)
    
    assert "[LLM Error]" in result
