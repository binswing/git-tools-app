import os
import json
import shutil
import uuid
from pathlib import Path

PACKAGE_ROOT = Path(__file__).parent.parent
DEFAULT_GTA_DIR = PACKAGE_ROOT / ".gta"
GLOBAL_CONFIG_DIR = Path.home() / ".gta"
GLOBAL_CONFIG_FILE = GLOBAL_CONFIG_DIR / "config.json"

# Capture the current working directory's .gta folder
LOCAL_GTA_DIR = Path.cwd() / ".gta"
LOCAL_CONFIG_FILE = LOCAL_GTA_DIR / "config.json"

FOLDER_NAMES = ["assets", "templates"]

DEFAULT_CONFIG = {
    "environment": "development",
    "debug": True,
    "ai_provider": "ollama",
    "model": "llama3",
    "addons": [
        {
            "id": str(uuid.uuid4()),
            "name": "Producer Tag",
            "hook_type": "audio",
            "events": ["post-push", "post-merge"],
            "options": {
                "audio_path": "assets/producer_tag.wav"
            },
            "enabled": True
        }
    ]
}

def load_config():
    """Loads settings cascadingly: Defaults -> Global Override -> Local Override."""
    config = DEFAULT_CONFIG.copy()
    # 1. Merge Global Config
    if GLOBAL_CONFIG_FILE.exists():
        try:
            with open(GLOBAL_CONFIG_FILE, "r") as f:
                config.update(json.load(f))
        except json.JSONDecodeError:
            print("[GTA Warning] Corrupted global config.json file detected. Ignoring.")

    # 2. Merge Local Config (Overrides Global)
    if LOCAL_CONFIG_FILE.exists():
        try:
            with open(LOCAL_CONFIG_FILE, "r") as f:
                config.update(json.load(f))
        except json.JSONDecodeError:
            print(f"[GTA Warning] Corrupted local config.json in {LOCAL_GTA_DIR}. Ignoring.")

    # 3. Resolve Directory Paths (Local vs Global vs Default)
    for folder_name in FOLDER_NAMES:
        local_path = LOCAL_GTA_DIR / folder_name
        global_path = GLOBAL_CONFIG_DIR / folder_name
        default_path = DEFAULT_GTA_DIR / folder_name

        if local_path.exists() and local_path.is_dir():
            config[f"{folder_name}_dir"] = str(local_path)
        elif global_path.exists() and global_path.is_dir():
            config[f"{folder_name}_dir"] = str(global_path)
        else:
            config[f"{folder_name}_dir"] = str(default_path)

    config["commitmsg_prompt_path"] = str(Path(config["templates_dir"]) / "COMMITMSG.md")
    return config

def save_config(key, value):
    """
    Saves a setting. If a local .gta folder exists in the terminal's 
    current directory, it saves to the local config. Otherwise, it saves globally.
    """
    target_dir = LOCAL_GTA_DIR if LOCAL_GTA_DIR.exists() else GLOBAL_CONFIG_DIR
    target_file = target_dir / "config.json"
    
    target_dir.mkdir(parents=True, exist_ok=True)

    # Only load the specific target file, NOT the fully merged config.
    # This prevents accidentally writing all global settings into the local file.
    file_config = {}
    if target_file.exists():
        try:
            with open(target_file, "r") as f:
                file_config = json.load(f)
        except json.JSONDecodeError:
            pass 

    file_config[key] = value

    # Filter out dynamic directory paths to prevent them from being hardcoded
    dynamic_keys = [f"{name}_dir" for name in FOLDER_NAMES] + ["commitmsg_prompt_path"]
    static_config = {k: v for k, v in file_config.items() if k not in dynamic_keys}
    
    try:
        with open(target_file, "w") as f:
            json.dump(static_config, f, indent=4)
    except Exception as e:
        print(f"[GTA Error] Failed to write configuration to {target_file}: {e}")

def import_external_file(source_path: str, target_folder: str, target_filename: str) -> bool:
    source_file = Path(source_path).expanduser().resolve()
    if not source_file.exists() or not source_file.is_file():
        return False
    
    # Intelligently routes file imports to the local folder if it exists
    dest_dir = LOCAL_GTA_DIR / target_folder if (LOCAL_GTA_DIR.exists() and LOCAL_GTA_DIR.is_dir()) else GLOBAL_CONFIG_DIR / target_folder
    dest_dir.mkdir(parents=True, exist_ok=True)
    dest_file = dest_dir / target_filename
    
    try:
        shutil.copyfile(source_file, dest_file)
        return True
    except Exception:
        return False