import sys
import shlex
import subprocess
from pathlib import Path
from git_tools_app.utils.logger import get_logger

logger = get_logger(__name__)

# The Developer Schema for Dynamic UI Generation
HOOK_SCHEMA = {
    "name": "Custom Python Script",
    "description": "Executes an arbitrary Python script during the pipeline.",
    "options": [
        {
            "key": "script_path",
            "type": "file",
            "label": "Path to Python script (.py)",
            "target_folder": "assets",
            "target_name_prefix": "script_",
            "default": ""
        },
        {
            "key": "script_args",
            "type": "text",
            "label": "Optional arguments (e.g., --verbose -f)",
            "default": ""
        }
    ]
}

def execute(addon_options, parsed_args, config_context):
    """The execution logic called by the event dispatcher."""
    raw_path = addon_options.get("script_path", "")
    
    if not raw_path:
        logger.warning("Custom Script Hook aborted: No script path provided.")
        return

    # Resolve against the active assets directory if it's a relative imported path
    if raw_path.startswith("assets/"):
        filename = raw_path.split("/")[-1]
        resolved_path = Path(config_context.get("assets_dir", "")) / filename
    else:
        resolved_path = Path(raw_path).expanduser().resolve()

    if not resolved_path.exists():
        logger.error(f"Custom Script Hook aborted: File not found at {resolved_path}")
        return

    logger.debug(f"Custom Script Hook executing: {resolved_path}")
    
    # Safely parse string arguments into a list (e.g., "--verbose -p 80" -> ["--verbose", "-p", "80"])
    args_string = addon_options.get("script_args", "")
    extra_args = shlex.split(args_string)

    # Use sys.executable to run the script using the current Python environment
    command = [sys.executable, str(resolved_path)] + extra_args
    
    print(f"\n--- Running Custom Script: {resolved_path.name} ---")
    try:
        # We let the script print directly to the user's terminal
        subprocess.run(command, check=True)
        print("-" * (27 + len(resolved_path.name)) + "\n")
    except subprocess.CalledProcessError as e:
        logger.error(f"Custom script '{resolved_path.name}' failed with exit code {e.returncode}")
        print(f"--- Script Failed (Code: {e.returncode}) ---\n")
    except Exception as e:
        logger.error(f"Unexpected error executing custom script: {e}")
        print(f"--- Script Execution Error ---\n")