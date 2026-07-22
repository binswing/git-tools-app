from git_tool_app.core import events, audio
from git_tool_app.utils.config import load_config
from git_tool_app.utils.logger import get_logger

logger = get_logger(__name__)

def play_tag(parsed_args):
    """Reads user config and plays the tag if enabled."""
    config = load_config()
    
    if config.get("play_tags", True):
        audio_path = config.get("producer_tag_path")
        logger.debug(f"Audio tag trigger activated. Target file: {audio_path}")
        audio.play_audio(audio_path)
    else:
        logger.debug("Audio tag trigger ignored (Audio tags are disabled in settings).")

# ==========================================
# Dynamic Event Subscription
# ==========================================
config = load_config()
active_events = config.get("audio_hook_events", ["post-push", "post-merge"])

for git_event in active_events:
    events.subscribe(git_event, play_tag)
    logger.debug(f"Audio tag hook automatically subscribed to '{git_event}'")