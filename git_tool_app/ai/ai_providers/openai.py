import os
import requests
import sys
from git_tool_app.utils.logger import get_logger

logger = get_logger(__name__)

MODELS_URL = "https://api.openai.com/v1/models"
CHATS_URL = "https://api.openai.com/v1/chat/completions"
API_KEY_FALLBACK = "OPENAI_API_KEY"
API_KEY = "GTA_" + API_KEY_FALLBACK

def get_api_key():
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
    api_key = get_api_key()
    url = MODELS_URL
    headers = {"Authorization": f"Bearer {api_key}"}
    
    try:
        logger.debug("Fetching OpenAI models...")
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        models = response.json().get("data", [])
        
        chat_models = sorted([m["id"] for m in models if "gpt" in m["id"]])
        return chat_models
    except Exception as e:
        logger.error(f"Could not fetch OpenAI models: {e}", exc_info=True)
        sys.exit(1)

def generate_message(model, system_prompt, user_prompt):
    api_key = get_api_key()
    url = CHATS_URL
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    payload = {
        "model": model,
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ]
    }
    try:
        logger.debug(f"Sending generation request to OpenAI (Model: {model})")
        response = requests.post(url, headers=headers, json=payload)
        response.raise_for_status()
        data = response.json()
        return data["choices"][0]["message"]["content"].strip()
    except Exception as e:
        logger.error(f"Failed to generate message from OpenAI: {e}", exc_info=True)
        sys.exit(1)