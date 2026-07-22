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

# Register subscriptions
events.subscribe("post-push", play_tag)
events.subscribe("post-merge", play_tag)