import os
import requests
import sys
MODELS_URL = "https://generativelanguage.googleapis.com/v1beta/models?key={api_key}"
CHATS_URL = "https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={api_key}"
API_KEY_FALLBACK = "GEMINI_API_KEY"
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
    url = MODELS_URL.format(api_key=api_key)
    
    try:
        response = requests.get(url)
        response.raise_for_status()
        models = response.json().get("models", [])
        
        # Filter for text-generation models and clean up the names
        chat_models = [
            m["name"].replace("models/", "") 
            for m in models 
            if "generateContent" in m.get("supportedGenerationMethods", [])
        ]
        return chat_models
    except Exception as e:
        print(f"[GTA Error] Could not fetch Gemini models: {e}")
        sys.exit(1)

def generate_message(model, system_prompt, user_prompt):
    api_key = get_api_key()
    url = CHATS_URL.format(
        model=model,
        api_key=api_key
    )
    
    headers = {"Content-Type": "application/json"}
    payload = {
        "contents": [{
            "parts": [
                {"text": f"{system_prompt}\n{user_prompt}"}
            ]
        }]
    }
    
    try:
        response = requests.post(url, headers=headers, json=payload)
        response.raise_for_status()
        data = response.json()
        return data["candidates"][0]["content"]["parts"][0]["text"].strip()
    except Exception as e:
        print(f"[GTA Error] Failed to generate message from Gemini: {e}")
        sys.exit(1)