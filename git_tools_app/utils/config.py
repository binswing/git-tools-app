import os
import json
import shutil
import uuid
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent.parent
DEFAULT_GTA_DIR = PROJECT_ROOT / ".gta"
CONFIG_DIR = Path.home() / ".gta"
CONFIG_FILE = CONFIG_DIR / "config.json"
FOLDER_NAMES = ["assets", "templates"]

DEFAULT_CONFIG = {
    "environment": "development",
    "debug": True,
    "ai_provider": "ollama",
    "model": "llama3",
    # The new dynamic addon architecture
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
    if CONFIG_FILE.exists():
        try:
            with open(CONFIG_FILE, "r") as f:
                user_config = json.load(f)
                config = {**DEFAULT_CONFIG, **user_config}
        except json.JSONDecodeError:
            print("[GTA Warning] Corrupted config.json file detected. Falling back to defaults.")
            config = DEFAULT_CONFIG.copy()
    else:
        config = DEFAULT_CONFIG.copy()

    local_gta_dir = Path.cwd() / ".gta"
    for folder_name in FOLDER_NAMES:
        local_path = local_gta_dir / folder_name
        global_path = CONFIG_DIR / folder_name
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
    CONFIG_DIR.mkdir(parents=True, exist_ok=True)
    config = load_config()
    config[key] = value

    dynamic_keys = [f"{name}_dir" for name in FOLDER_NAMES] + ["commitmsg_prompt_path"]
    static_config = {k: v for k, v in config.items() if k not in dynamic_keys}
    
    try:
        with open(CONFIG_FILE, "w") as f:
            json.dump(static_config, f, indent=4)
    except Exception as e:
        print(f"[GTA Error] Failed to write configuration to {CONFIG_FILE}: {e}")

def import_external_file(source_path: str, target_folder: str, target_filename: str) -> bool:
    source_file = Path(source_path).expanduser().resolve()
    if not source_file.exists() or not source_file.is_file():
        return False
    
    local_gta = Path.cwd() / ".gta"
    dest_dir = local_gta / target_folder if (local_gta.exists() and local_gta.is_dir()) else CONFIG_DIR / target_folder
    dest_dir.mkdir(parents=True, exist_ok=True)
    dest_file = dest_dir / target_filename
    
    try:
        shutil.copyfile(source_file, dest_file)
        return True
    except Exception:
        return False