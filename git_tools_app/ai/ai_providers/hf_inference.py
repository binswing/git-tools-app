import os
import requests
import sys
from git_tools_app.utils.logger import get_logger

logger = get_logger(__name__)

MODELS_URL = "https://huggingface.co/api/models"
CHATS_URL = "https://api-inference.huggingface.co/models/{model}"
API_KEY_FALLBACK = "HF_TOKEN"
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
    url = MODELS_URL
    params = {
        "pipeline_tag": "text-generation",
        "sort": "trending",
        "limit": 15
    }
    
    try:
        logger.debug("Fetching trending Hugging Face models...")
        response = requests.get(url, params=params)
        response.raise_for_status()
        models = response.json()
        return [m["id"] for m in models]
    except Exception as e:
        logger.error(f"Could not fetch Hugging Face models: {e}", exc_info=True)
        sys.exit(1)

def generate_message(model, system_prompt, user_prompt):
    api_key = get_api_key()
    url = CHATS_URL.format(model=model)
    
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    
    prompt = f"{system_prompt}\n{user_prompt}"
    
    payload = {
        "inputs": prompt,
        "parameters": {
            "max_new_tokens": 100,
            "return_full_text": False,
            "temperature": 0.2
        }
    }
    
    try:
        logger.debug(f"Sending generation request to Hugging Face Inference (Model: {model})")
        response = requests.post(url, headers=headers, json=payload)
        response.raise_for_status()
        data = response.json()
        
        if isinstance(data, list) and len(data) > 0:
            return data[0].get("generated_text", "").strip()
        elif isinstance(data, dict):
            return data.get("generated_text", "").strip()
            
        return str(data)
        
    except requests.exceptions.HTTPError as e:
        logger.error(f"Hugging Face API Error: {e.response.status_code}")
        logger.debug(f"HF Error Details: {e.response.text}")
        logger.info("Note: HF Serverless models sometimes take a minute to load. Try again shortly.")
        sys.exit(1)
    except Exception as e:
        logger.error(f"Failed to generate message from HF: {e}", exc_info=True)
        sys.exit(1)