import os
import json
import shutil
from pathlib import Path

# 1. Lowest Priority: The default files shipped with the pip package
PROJECT_ROOT = Path(__file__).parent.parent.parent
DEFAULT_GTA_DIR = PROJECT_ROOT / ".gta"

# 2. Medium Priority: The global user preferences
CONFIG_DIR = Path.home() / ".gta"
CONFIG_FILE = CONFIG_DIR / "config.json"

DEFAULT_CONFIG = {
    "ai_provider": "ollama",
    "model": "llama3",
    "play_tags": True
}
FOLDER_NAMES = ["assets", "templates"]

def load_config():
    """Reads user config and resolves assets/templates using a 3-tier priority system."""
    # Load baseline JSON options
    if CONFIG_FILE.exists():
        try:
            with open(CONFIG_FILE, "r") as f:
                user_config = json.load(f)
                config = {**DEFAULT_CONFIG, **user_config}
        except json.JSONDecodeError:
            config = DEFAULT_CONFIG.copy()
    else:
        config = DEFAULT_CONFIG.copy()

    # 3. Highest Priority: The current working directory (Local Workspace)
    local_gta_dir = Path.cwd() / ".gta"

    # Resolve the active directories using the 3-Tier Hierarchy
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

    # Map default target files relative to the resolved directories
    config["producer_tag_path"] = str(Path(config["assets_dir"]) / "producer_tag.wav")
    config["commitmsg_prompt_path"] = str(Path(config["templates_dir"]) / "COMMITMSG.md")

    return config

def save_config(key, value):
    """Updates a single key in the global config file."""
    # Ensure the global ~/.gta directory exists before saving
    CONFIG_DIR.mkdir(parents=True, exist_ok=True)
    
    config = load_config()
    config[key] = value

    # Strip out dynamic run-time paths before saving so the JSON stays clean
    dynamic_keys = FOLDER_NAMES + ["producer_tag_path", "commitmsg_prompt_path"]
    static_config = {k: v for k, v in config.items() if k not in dynamic_keys}
    
    with open(CONFIG_FILE, "w") as f:
        json.dump(static_config, f, indent=4)

def import_external_file(source_path: str, target_folder: str, target_filename: str) -> bool:
    """
    Copies an external file into the local or global .gta workspace.
    """
    # expanduser allows paths like "~/Downloads/my_tag.wav"
    source_file = Path(source_path).expanduser().resolve()
    
    if not source_file.exists() or not source_file.is_file():
        print(f"\n[GTA Error] File not found at: {source_file}")
        return False

    local_gta = Path.cwd() / ".gta"
    
    # 1. Check if the local project workspace exists
    if local_gta.exists() and local_gta.is_dir():
        dest_dir = local_gta / target_folder
        scope = "Local Project"
    else:
        # 2. Fallback to the global user workspace
        dest_dir = CONFIG_DIR / target_folder
        scope = "Global User"
        
    dest_dir.mkdir(parents=True, exist_ok=True)
    dest_file = dest_dir / target_filename
    
    try:
        shutil.copyfile(source_file, dest_file)
        print(f"\n✅ Successfully imported into {scope} workspace!")
        print(f"📁 Saved to: {dest_file}\n")
        return True
    except Exception as e:
        print(f"\n[GTA Error] Failed to copy file: {e}")
        return False