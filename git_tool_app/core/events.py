""" Event manager module. """
from git_tool_app.utils.logger import get_logger

logger = get_logger(__name__)

_subscribers = {}

def subscribe(event_name, callback):
    """Hooks use this to listen for specific Git events."""
    if event_name not in _subscribers:
        _subscribers[event_name] = []
    _subscribers[event_name].append(callback)
    logger.debug(f"Hook '{callback.__name__}' subscribed to event '{event_name}'")

def trigger(event_name, *args, **kwargs):
    """Commands use this to announce that an event just happened."""
    logger.debug(f"Triggering event: {event_name}")
    if event_name in _subscribers:
        for callback in _subscribers[event_name]:
            try:
                callback(*args, **kwargs)
            except Exception as e:
                logger.error(f"Error executing hook [{callback.__name__}]: {e}", exc_info=True)