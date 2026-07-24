"""Core event handling for Git Tools App."""

from git_tools_app.core.hook_api import get_available_hooks
from git_tools_app.utils.config import load_config
from git_tools_app.utils.logger import get_logger

logger = get_logger(__name__)

# Master registry of supported event triggers
SUPPORTED_EVENTS = [
    {"id": "pre-commit", "label": "pre-commit", "description": "Before commit executes"},
    {"id": "post-commit", "label": "post-commit", "description": "After commit succeeds"},
    {"id": "pre-push", "label": "pre-push", "description": "Before pushing to remote"},
    {"id": "post-push", "label": "post-push", "description": "After push succeeds"},
    {"id": "pre-checkout", "label": "pre-checkout", "description": "Before switching branches"},
    {"id": "post-checkout", "label": "post-checkout", "description": "After switching branches"},
    {"id": "pre-merge", "label": "pre-merge", "description": "Before branch merge"},
    {"id": "post-merge", "label": "post-merge", "description": "After branch merge"},
    {"id": "pre-pull", "label": "pre-pull", "description": "Before pulling changes"},
    {"id": "post-pull", "label": "post-pull", "description": "After pulling changes"},
]


def trigger(event_name, *args, **kwargs):
    """Sequentially processes user addons assigned to the triggered event."""
    logger.debug(f"Triggering event: {event_name}")

    config = load_config()
    addons = config.get("addons", [])
    available_hooks = get_available_hooks()

    parsed_args = args[0] if len(args) > 0 else None

    for addon in addons:
        if addon.get("enabled", False) and event_name in addon.get("events", []):
            hook_type = addon.get("hook_type")
            hook_registry = available_hooks.get(hook_type)

            if not hook_registry:
                logger.error(f"Addon '{addon.get('name')}' relies on missing hook: {hook_type}")
                continue

            try:
                logger.debug(f"Executing addon '{addon.get('name')}' (Type: {hook_type})")
                module = hook_registry["module"]
                module.execute(addon.get("options", {}), parsed_args, config)
            except Exception as e:
                logger.error(f"Addon '{addon.get('name')}' failed during execution: {e}", exc_info=True)
