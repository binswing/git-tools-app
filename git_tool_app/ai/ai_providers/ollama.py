import requests
import sys

OLLAMA_URL = "http://localhost:11434/api"

def get_models():
    try:
        response = requests.get(f"{OLLAMA_URL}/tags")
        response.raise_for_status()
        return [model['name'] for model in response.json().get('models', [])]
    except requests.exceptions.RequestException:
        print("Error: Could not connect to local Ollama. Is it running?")
        sys.exit(1)

def generate_message(model, system_prompt, user_prompt):
    full_prompt = f"{system_prompt}\n{user_prompt}"
    payload = {"model": model, "prompt": full_prompt, "stream": False}
    
    response = requests.post(f"{OLLAMA_URL}/generate", json=payload)
    response.raise_for_status()
    return response.json().get("response", "").strip()