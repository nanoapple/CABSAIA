# CABSAIA

**Cognitive-Affective Bifurcated-System Agent for Interactive Adaptation**

An experimental sandbox that explores psychologically grounded agent behaviour using a lightweight internal state model (e.g., emotion debt, resilience, energy, burst levels) and coping-style driven prompting.

> **⚠️ Research Prototype**: This repository is under active development. APIs, modules, and behaviours may change frequently.

---

## What it does (high level)

- Tracks an internal state across turns (emotion debt, resilience, energy, feedback history)
- Detects "burst" conditions (mild/moderate/severe) based on recent feedback + debt + energy
- Selects coping styles (e.g., emotion-focused, problem-focused, avoidance, resentful)
- Generates prompts from role/style configuration and sends them to an LLM backend
- Runs a simple loop for experimentation and testing

---

## Project structure
cabsaia/
├── processing/     # Text signals → features (e.g., valence/arousal, keywords)
├── state/          # Internal state (FRR/emotion debt, resilience, energy) and burst logic
├── behavior/       # Coping style selection and prompt style mapping
├── core/           # LLM interface and prompt generation utilities
├── tests/          # Unit tests and behavioural regression checks
└── data/           # Experimental resources (e.g., VAD/Darwin mappings, logs)


---

## Requirements

Create and activate a virtual environment (recommended), then install dependencies:

```bash
pip install -r requirements.txt

Minimum dependencies typically include:
requests
PyYAML
pytest (for running tests)

## LLM backend (local Ollama)
By default, the project is configured to use a local Ollama server.
Install and start Ollama
Ensure the model is available (default: mistral):

ollama pull mistral

---

Running
Quick smoke run (test loop):
python main_test_loop.py

Run tests:
pytest -q