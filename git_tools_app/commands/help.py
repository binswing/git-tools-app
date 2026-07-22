import subprocess
import sys
from git_tools_app.utils.logger import get_logger

logger = get_logger(__name__)

def run(args):
    """Overrides the default git help command to show GTA features first."""
    logger.debug(f"Running help command with args: {args}")
    
    if not args:
        # User CLI help menu
        logger.info("=========================================")
        logger.info("█▀▀ ▀█▀ ▄▀█   █▀ █▀▀ ▀█▀ █ █ █▀█")
        logger.info("█▄█  █  █▀█   ▄█ ██▄  █  █▄█ █▀▀")
        logger.info("=========================================\n")
        logger.info("GTA (Git Tool App)\n")
        logger.info("GTA wraps standard Git. Any normal Git command (e.g., `gta status`, `gta rebase`)")
        logger.info("will work exactly as expected by passing through to your system's Git.\n")
        logger.info("Custom GTA Commands:")
        logger.info("  commit      Generate an AI commit message based on staged changes")
        logger.info("  push        Push commits to remote (Triggers post-push hooks)")
        logger.info("  merge       Merge branches (Triggers post-merge hooks)")
        logger.info("  setting     Launch the interactive UI to configure AI and Hooks")
        logger.info("  help        Show this help message\n")
        logger.info("To get standard Git help for a specific command, use: `gta help <command>`\n")
    else:
        try:
            logger.debug(f"Passing help query to native git: git help {' '.join(args)}")
            subprocess.run(["git", "help"] + args)
        except KeyboardInterrupt:
            sys.exit(130)
        except Exception as e:
            logger.error(f"Error executing git help: {e}", exc_info=True)
            sys.exit(1)