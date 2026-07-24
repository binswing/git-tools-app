"""Gemini AI Provider."""

import os
import sys

import requests

from git_tools_app.utils.logger import get_logger

logger = get_logger(__name__)

MODELS_URL = "https://generativelanguage.googleapis.com/v1beta/models?key={api_key}"
CHATS_URL = "https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={api_key}"
API_KEY_FALLBACK = "GEMINI_API_KEY"
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
    """Fetch available Gemini models from the API."""
    api_key = get_api_key()
    url = MODELS_URL.format(api_key=api_key)

    try:
        logger.debug("Fetching Gemini models...")
        response = requests.get(url)
        response.raise_for_status()
        models = response.json().get("models", [])

        chat_models = [
            m["name"].replace("models/", "")
            for m in models
            if "generateContent" in m.get("supportedGenerationMethods", [])
        ]
        return chat_models
    except Exception as e:
        logger.error(f"Could not fetch Gemini models: {e}", exc_info=True)
        sys.exit(1)


def generate_message(model, system_prompt, user_prompt):
    """Generate a message using the Gemini API.

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
    url = CHATS_URL.format(model=model, api_key=api_key)

    headers = {"Content-Type": "application/json"}
    payload = {"contents": [{"parts": [{"text": f"{system_prompt}\n{user_prompt}"}]}]}

    try:
        logger.debug(f"Sending generation request to Gemini (Model: {model})")
        response = requests.post(url, headers=headers, json=payload)
        response.raise_for_status()
        data = response.json()
        return data["candidates"][0]["content"]["parts"][0]["text"].strip()
    except Exception as e:
        logger.error(f"Failed to generate message from Gemini: {e}", exc_info=True)
        sys.exit(1)
