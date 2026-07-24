"""Claude AI Provider."""

import os
import sys

import requests

from git_tools_app.utils.logger import get_logger

logger = get_logger(__name__)

MODELS_URL = "https://api.anthropic.com/v1/models"
CHATS_URL = "https://api.anthropic.com/v1/messages"
API_KEY_FALLBACK = "ANTHROPIC_API_KEY"
API_KEY = "GTA_" + API_KEY_FALLBACK


def get_api_key():
    """Retrieve the API key from environment variables, with a fallback."""
    key = os.getenv(API_KEY)
    if not key:
        logger.debug(f"{API_KEY} environment variable is missing. Trying {API_KEY_FALLBACK} as a fallback.")
        key_fallback = os.getenv(API_KEY_FALLBACK)
        if not key_fallback:
            logger.error(f"Both {API_KEY} and {API_KEY_FALLBACK} are missing.")
            logger.error(f"Set it in your terminal: export {API_KEY}='your_api_key'")
            sys.exit(1)
        return key_fallback
    return key


def get_models():
    """Fetch available Claude models from the API."""
    api_key = get_api_key()
    url = MODELS_URL
    headers = {"x-api-key": api_key, "anthropic-version": "2023-06-01"}

    try:
        logger.debug(f"Fetching Claude models from {url}")
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        models = response.json().get("data", [])

        return [m["id"] for m in models if m.get("type") == "model"]
    except Exception as e:
        logger.error(f"Could not fetch Claude models: {e}", exc_info=True)
        sys.exit(1)


def generate_message(model, system_prompt, user_prompt):
    """Generate a message using the Claude API.

    Args:
    ----
        model (str): The model ID to use for generation.
        system_prompt (str): The system prompt to guide the model's behavior.
        user_prompt (str): The user's input prompt.

    Returns:
    -------
        str: The generated message from the model.

    """
    api_key = get_api_key()
    url = CHATS_URL

    headers = {"x-api-key": api_key, "anthropic-version": "2023-06-01", "content-type": "application/json"}

    payload = {
        "model": model,
        "max_tokens": 512,
        "system": system_prompt,
        "messages": [{"role": "user", "content": user_prompt}],
    }

    try:
        logger.debug(f"Sending generation request to Claude (Model: {model})")
        response = requests.post(url, headers=headers, json=payload)
        response.raise_for_status()
        data = response.json()
        return data["content"][0]["text"].strip()
    except Exception as e:
        logger.error(f"Failed to generate message from Claude: {e}", exc_info=True)
        sys.exit(1)
