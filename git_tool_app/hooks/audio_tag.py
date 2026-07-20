from git_tool_app.core import events, audio
from git_tool_app.utils.config import load_config

def play_tag(parsed_args):
    """Reads user config and plays the tag if globally enabled."""
    config = load_config()
    
    if config.get("play_tags", True):
        audio_path = config.get("producer_tag_path")
        audio.play_audio(audio_path)

# Bind this single function to multiple Git events
events.subscribe("post-push", play_tag)
events.subscribe("post-merge", play_tag)
