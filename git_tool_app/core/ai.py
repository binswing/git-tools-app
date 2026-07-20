import requests
import sys

OLLAMA_URL = "http://localhost:11434/api"

def get_installed_models():
    """Fetches a list of available models from the local Ollama instance."""
    try:
        response = requests.get(f"{OLLAMA_URL}/tags")
        response.raise_for_status()
        return [model['name'] for model in response.json().get('models', [])]
    except requests.exceptions.RequestException:
        print("Error: Could not connect to local Ollama. Is the service running?")
        sys.exit(1)

def generate_commit_message(model, prompt_guideline, diff_content):
    """Sends the diff to Ollama and returns the generated message."""
    full_prompt = (
        f"{prompt_guideline}\n\n"
        f"Here are the working project changes:\n```\n{diff_content}\n```\n\n"
        "Generate ONLY the commit message. No intro, no markdown formatting."
    )
    
    payload = {
        "model": model,
        "prompt": full_prompt,
        "stream": False
    }
    
    try:
        response = requests.post(f"{OLLAMA_URL}/generate", json=payload)
        response.raise_for_status()
        return response.json().get("response", "").strip()
    except requests.exceptions.RequestException as e:
        print(f"Error generating message from Ollama: {e}")
        sys.exit(1)