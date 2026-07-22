import pkgutil
import importlib
import git_tools_app.hooks
from git_tools_app.utils.logger import get_logger

logger = get_logger(__name__)

def get_available_hooks():
    """Scans the hooks directory for valid Developer Schemas."""
    hooks = {}
    for _, module_name, _ in pkgutil.iter_modules(git_tools_app.hooks.__path__):
        try:
            module = importlib.import_module(f"git_tools_app.hooks.{module_name}")
            if hasattr(module, 'HOOK_SCHEMA') and hasattr(module, 'execute'):
                hooks[module_name] = {
                    "schema": module.HOOK_SCHEMA,
                    "module": module
                }
        except Exception as e:
            logger.error(f"Failed to load hook '{module_name}': {e}", exc_info=True)
    return hooks