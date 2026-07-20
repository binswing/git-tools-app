import os
import json
from pathlib import Path

# Absolute path to the global package root
PROJECT_ROOT = Path(__file__).parent.parent.parent
LOCAL_CONFIG_PATH = PROJECT_ROOT / ".gta"
# Global fallback config path for user preferences
CONFIG_DIR = Path.home() / ".config" / "gta"
CONFIG_FILE = CONFIG_DIR / "config.json"

DEFAULT_CONFIG = {
    "model": "llama3",
    "play_tags": True
}

def load_local_folders():
    local_gta = Path.cwd() / ".gta"
    local_folders = [
        {
            "name": "assets",
            "path": local_gta / "assets"
        },
        {
            "name": "templates",
            "path": local_gta / "templates"
        }
    ]
    return local_folders

def load_config():
    """Reads user config and dynamically shifts the assets and templates directories 
    if a local .gta workspace is detected.
    """
    # 1. Load global baseline options
    if CONFIG_FILE.exists():
        try:
            with open(CONFIG_FILE, "r") as f:
                user_config = json.load(f)
                config = {**DEFAULT_CONFIG, **user_config}
        except json.JSONDecodeError:
            config = DEFAULT_CONFIG.copy()
    else:
        config = DEFAULT_CONFIG.copy()

    # 2. Define potential workspace local paths
    local_folders = load_local_folders()

    # 3. Resolve the active directories for the entire application
    for local_folder in local_folders:
        folder_name = local_folder["name"]
        if local_folder["path"].exists() and local_folder["path"].is_dir():
            config[f"{folder_name}_dir"] = str(local_folder["path"])
        else:
            config[f"{folder_name}_dir"] = str(LOCAL_CONFIG_PATH / folder_name)

    # 4. Map default target files relative to the resolved directories
    config["producer_tag_path"] = str(Path(config["assets_dir"]) / "producer_tag.wav")
    config["default_prompt_path"] = str(Path(config["templates_dir"]) / "COMMITMSG.md")

    return config

def save_config(key, value):
    """Updates a single key in the global config file."""
    CONFIG_DIR.mkdir(parents=True, exist_ok=True)
    config = load_config()
    config[key] = value

    # We strip out dynamic run-time paths before saving so the file stays clean
    local_folders = load_local_folders()
    
    dynamic_keys = [f"{folder['name']}_dir" for folder in local_folders] + [
        "producer_tag_path", 
        "default_prompt_path"
    ]
    
    static_config = {k: v for k, v in config.items() if k not in dynamic_keys}
    
    with open(CONFIG_FILE, "w") as f:
        json.dump(static_config, f, indent=4)