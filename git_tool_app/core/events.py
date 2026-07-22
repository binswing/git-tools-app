from git_tool_app.utils.config import load_config
from git_tool_app.core.hook_api import get_available_hooks
from git_tool_app.utils.logger import get_logger

logger = get_logger(__name__)

def trigger(event_name, *args, **kwargs):
    """Sequentially processes user addons assigned to the triggered event."""
    logger.debug(f"Triggering event: {event_name}")
    
    config = load_config()
    addons = config.get("addons", [])
    available_hooks = get_available_hooks()
    parsed_args = args[0] if len(args) > 0 else None
    for addon in addons:
        # Check if the addon is active and assigned to this event
        if addon.get("enabled", False) and event_name in addon.get("events", []):
            hook_type = addon.get("hook_type")
            hook_registry = available_hooks.get(hook_type)
            
            if not hook_registry:
                logger.error(f"Addon '{addon.get('name')}' relies on missing hook: {hook_type}")
                continue
                
            try:
                logger.debug(f"Executing addon '{addon.get('name')}' (Type: {hook_type})")
                module = hook_registry["module"]
                # Pass the addon's specific options to the hook template
                module.execute(addon.get("options", {}), parsed_args, config)
            except Exception as e:
                logger.error(f"Addon '{addon.get('name')}' failed during execution: {e}", exc_info=True)