import importlib
import sys
from git_tool_app.utils.config import load_config
from git_tool_app.utils.logger import get_logger

logger = get_logger(__name__)

def get_active_provider():
    """Dynamically loads the provider script based on the config file."""
    config = load_config()
    provider_name = config.get("ai_provider", "ollama") 
    
    try:
        logger.debug(f"Attempting to load AI provider module: git_tool_app.ai.ai_providers.{provider_name}")
        provider_module = importlib.import_module(f"git_tool_app.ai.ai_providers.{provider_name}")
        return provider_module
    except ImportError as e:
        logger.error(f"AI Provider '{provider_name}' is not installed or configured correctly.", exc_info=True)
        sys.exit(1)

def get_installed_models():
    """Delegates the model listing to the active provider (if supported)."""
    provider = get_active_provider()
    if hasattr(provider, 'get_models'):
        logger.debug(f"Querying models from provider '{provider.__name__}'")
        return provider.get_models()
    logger.warning(f"Provider '{provider.__name__}' does not support fetching model list.")
    return []