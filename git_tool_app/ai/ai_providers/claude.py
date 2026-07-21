import os
import requests
import sys
MODELS_URL = "https://api.anthropic.com/v1/models"
CHATS_URL = "https://api.anthropic.com/v1/messages"
API_KEY_FALLBACK = "ANTHROPIC_API_KEY"
API_KEY = "GTA_" + API_KEY_FALLBACK
def get_api_key():
    key = os.getenv(API_KEY)
    if not key:
        print(f"[GTA Error] {API_KEY} environment variable is missing.")
        print(f"[GTA] Trying {API_KEY_FALLBACK} environment variable as a fallback.")
        key_fallback = os.getenv(API_KEY_FALLBACK)
        if not key_fallback:
            print(f"[GTA Error] {API_KEY_FALLBACK} environment variable is missing.")
            print(f"Set it in your terminal: export {API_KEY}='your_api_key'")
            sys.exit(1)
        return key_fallback
    return key

def get_models():
    api_key = get_api_key()
    url = MODELS_URL
    headers = {
        "x-api-key": api_key,
        "anthropic-version": "2023-06-01"
    }
    
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        models = response.json().get("data", [])
        
        return [m["id"] for m in models if m.get("type") == "model"]
    except Exception as e:
        print(f"[GTA Error] Could not fetch Claude models: {e}")
        sys.exit(1)

def generate_message(model, system_prompt, user_prompt):
    api_key = get_api_key()
    url = CHATS_URL
    
    headers = {
        "x-api-key": api_key,
        "anthropic-version": "2023-06-01",
        "content-type": "application/json"
    }
    
    payload = {
        "model": model,
        "max_tokens": 512,
        "system": system_prompt,
        "messages": [
            {"role": "user", "content": user_prompt}
        ]
    }
    
    try:
        response = requests.post(url, headers=headers, json=payload)
        response.raise_for_status()
        data = response.json()
        return data["content"][0]["text"].strip()
    except Exception as e:
        print(f"[GTA Error] Failed to generate message from Claude: {e}")
        sys.exit(1)