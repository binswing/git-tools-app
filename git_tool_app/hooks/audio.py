import os
from pathlib import Path
from git_tool_app.core import audio
from git_tool_app.utils.logger import get_logger

logger = get_logger(__name__)

# The Developer Schema for Dynamic UI Generation
HOOK_SCHEMA = {
    "name": "Audio Player",
    "description": "Plays a .wav file to hype up your commits and pushes.",
    "options": [
        {
            "key": "audio_path",
            "type": "file",
            "label": "Path to audio file (.wav)",
            "default": "assets/producer_tag.wav"
        }
    ]
}

def execute(addon_options, parsed_args, config_context):
    """The execution logic called by the event dispatcher."""
    raw_path = addon_options.get("audio_path", "")
    
    # Resolve against the active assets directory if it's a relative default path
    if raw_path.startswith("assets/"):
        filename = raw_path.split("/")[-1]
        resolved_path = Path(config_context.get("assets_dir", "")) / filename
    else:
        resolved_path = Path(raw_path).expanduser().resolve()

    logger.debug(f"Audio Hook playing file: {resolved_path}")
    audio.play_audio(str(resolved_path))