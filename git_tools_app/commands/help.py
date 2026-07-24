"""Help Command."""

import subprocess
import sys

from git_tools_app.utils.logger import get_logger

logger = get_logger(__name__)


def run(args):
    """Override the default git help command to show GTA features first."""
    logger.debug(f"Running help command with args: {args}")

    if not args:
        # User CLI help menu
        print("GTA (Git Tools App)\n")
        print("GTA wraps standard Git. Any normal Git command (e.g., `gta status`, `gta rebase`)")
        print("will work exactly as expected by passing through to your system's Git.\n")
        print("Custom GTA Commands:")
        print("  setting     Launch the interactive UI to configure AI and Hooks")
        print("  help        Show this help message\n")
        print("To get standard Git help for a specific command, use: `gta help <command>`\n")
    else:
        try:
            logger.debug(f"Passing help query to native git: git help {' '.join(args)}")
            subprocess.run(["git", "help"] + args)
        except KeyboardInterrupt:
            sys.exit(130)
        except Exception as e:
            logger.error(f"Error executing git help: {e}", exc_info=True)
            sys.exit(1)
