"""Hook implementation for executing custom Python scripts."""

import shlex
import subprocess
import sys
from pathlib import Path

from git_tools_app.utils.logger import get_logger

logger = get_logger(__name__)

# The Developer Schema for Dynamic UI Generation
HOOK_SCHEMA = {
    "name": "Custom Python Script",
    "description": "Executes an arbitrary Python script directly from its source directory.",
    "options": [
        {"key": "script_path", "type": "file", "copy": False, "label": "Path to Python script (.py)", "default": ""},
        {"key": "script_args", "type": "text", "label": "Optional arguments (e.g., --verbose -f)", "default": ""},
    ],
}


def execute(addon_options, parsed_args, config_context):
    """The execution logic called by the event dispatcher."""
    raw_path = addon_options.get("script_path", "")

    if not raw_path:
        logger.warning("Custom Script Hook aborted: No script path provided.")
        return

    resolved_path = Path(raw_path)

    if not resolved_path.exists():
        logger.error(f"Custom Script Hook aborted: File not found at {resolved_path}")
        return

    logger.debug(f"Custom Script Hook executing: {resolved_path}")

    # Safely parse string arguments into a list
    args_string = addon_options.get("script_args", "")
    extra_args = shlex.split(args_string)

    # Execute it using the active Python environment
    command = [sys.executable, str(resolved_path)] + extra_args

    print(f"\n--- Running Custom Script: {resolved_path.name} ---")
    try:
        # cwd ensures the script executes inside its own original directory context
        subprocess.run(command, cwd=resolved_path.parent, check=True)
        print("-" * (27 + len(resolved_path.name)) + "\n")
    except subprocess.CalledProcessError as e:
        logger.error(f"Custom script '{resolved_path.name}' failed with exit code {e.returncode}")
        print(f"--- Script Failed (Code: {e.returncode}) ---\n")
    except Exception as e:
        logger.error(f"Unexpected error executing custom script: {e}")
        print("--- Script Execution Error ---\n")
