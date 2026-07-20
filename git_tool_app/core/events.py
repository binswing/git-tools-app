""" Event file. """

# A dictionary mapping event names (strings) to lists of callback functions
_subscribers = {}

def subscribe(event_name, callback):
    """Hooks use this to listen for specific Git events."""
    if event_name not in _subscribers:
        _subscribers[event_name] = []
    _subscribers[event_name].append(callback)

def trigger(event_name, *args, **kwargs):
    """Commands use this to announce that an event just happened."""
    if event_name in _subscribers:
        for callback in _subscribers[event_name]:
            try:
                callback(*args, **kwargs)
            except Exception as e:
                print(f"Error executing hook [{callback.__name__}]: {e}")