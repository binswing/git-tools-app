"""Ollama AI Provider."""

import sys

import requests

from git_tools_app.utils.logger import get_logger

logger = get_logger(__name__)
OLLAMA_URL = "http://localhost:11434/api"


def get_models():
    """Fetch available Ollama models from the local API."""
    try:
        logger.debug("Fetching local Ollama models...")
        response = requests.get(f"{OLLAMA_URL}/tags")
        response.raise_for_status()
        return [model["name"] for model in response.json().get("models", [])]
    except requests.exceptions.RequestException:
        logger.error("Could not connect to local Ollama. Is the service running?", exc_info=True)
        sys.exit(1)


def generate_message(model, system_prompt, user_prompt):
    """
    Generate a message using the Ollama API.

    Args:
        model (str): The model ID to use for generation.
        system_prompt (str): The system prompt to guide the model's behavior.
        user_prompt (str): The user's input prompt.

    Returns:
        str: The generated message from the model.

    """
    full_prompt = f"{system_prompt}\n{user_prompt}"
    payload = {"model": model, "prompt": full_prompt, "stream": False}

    try:
        logger.debug(f"Sending generation request to local Ollama (Model: {model})")
        response = requests.post(f"{OLLAMA_URL}/generate", json=payload)
        response.raise_for_status()
        return response.json().get("response", "").strip()
    except Exception as e:
        logger.error(f"Failed to generate message from Ollama: {e}", exc_info=True)
        sys.exit(1)
