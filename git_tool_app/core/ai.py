import importlib
import sys
from git_tool_app.utils.config import load_config

def get_active_provider():
    """Dynamically loads the provider script based on the config file."""
    config = load_config()
    # Default to ollama if not specified
    provider_name = config.get("ai_provider", "ollama") 
    
    try:
        provider_module = importlib.import_module(f"git_tool_app.ai.ai_providers.{provider_name}")
        return provider_module
    except ImportError:
        print(f"[GTA Error] AI Provider '{provider_name}' is not installed or configured correctly.")
        sys.exit(1)

def get_installed_models():
    """Delegates the model listing to the active provider (if supported)."""
    provider = get_active_provider()
    if hasattr(provider, 'get_models'):
        return provider.get_models()
    return []