import os
import requests
import sys
MODELS_URL = "https://huggingface.co/api/models"
CHATS_URL = "https://api-inference.huggingface.co/models/{model}"
API_KEY_FALLBACK = "HF_TOKEN"
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
    """Fetches the top 15 trending text-generation models from the HF Hub."""
    url = MODELS_URL
    params = {
        "pipeline_tag": "text-generation",
        "sort": "trending",
        "limit": 15
    }
    
    try:
        response = requests.get(url, params=params)
        response.raise_for_status()
        models = response.json()
        return [m["id"] for m in models]
    except Exception as e:
        print(f"[GTA Error] Could not fetch Hugging Face models: {e}")
        sys.exit(1)

def generate_message(model, system_prompt, user_prompt):
    api_key = get_api_key()
    url = CHATS_URL.format(model=model)
    
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    
    # Constructing a standard prompt format. 
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
        response = requests.post(url, headers=headers, json=payload)
        response.raise_for_status()
        data = response.json()
        
        # The HF Inference API usually returns a list of dictionaries for text generation
        if isinstance(data, list) and len(data) > 0:
            return data[0].get("generated_text", "").strip()
        elif isinstance(data, dict):
            return data.get("generated_text", "").strip()
            
        return str(data)
        
    except requests.exceptions.HTTPError as e:
        # HF often throws 503s if the model is currently loading into serverless memory
        print(f"\n[GTA Error] Hugging Face API Error: {e.response.status_code}")
        print(f"Details: {e.response.text}")
        print("Note: HF Serverless models sometimes take a minute to load. Try again shortly.")
        sys.exit(1)
    except Exception as e:
        print(f"\n[GTA Error] Failed to generate message from HF: {e}")
        sys.exit(1)