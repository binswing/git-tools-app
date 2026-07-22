import subprocess
import sys
from git_tools_app.utils.logger import get_logger

logger = get_logger(__name__)

def pass_through_to_git(args):
    """Executes a native git command and streams output straight to terminal."""
    try:
        logger.debug(f"Passing raw command through to native git: git {' '.join(args)}")
        exit_code = subprocess.call(["git"] + args)
        sys.exit(exit_code)
    except KeyboardInterrupt:
        sys.exit(130)
    except Exception as e:
        logger.error(f"Fatal error executing standard git command: {e}", exc_info=True)
        sys.exit(1)

def get_staged_diff():
    """Captures staged diff with UTF-8 encoding handling."""
    try:
        logger.debug("Fetching staged changes via `git diff --cached`...")
        result = subprocess.run(
            ["git", "diff", "--cached"], 
            capture_output=True, 
            encoding="utf-8",
            errors="replace",
            text=True
        )
        
        if result.returncode != 0:
            logger.error(f"Git failed to retrieve diff: {result.stderr}")
            sys.exit(1)

        if not result.stdout or not result.stdout.strip():
            logger.warning("No staged changes found. Did you forget to run `git add`?")
            sys.exit(0)
            
        return result.stdout.strip()
    except Exception as e:
        logger.error(f"Failed to execute git diff: {e}", exc_info=True)
        sys.exit(1)

def execute_commit(message, extra_args=None):
    """Executes the git commit command, passing through any extra flags."""
    if extra_args is None:
        extra_args = []
        
    # Construct the base command and append any extra flags (like --no-verify)
    command = ["git", "commit", "-m", message] + extra_args
    logger.debug(f"Executing commit command: {' '.join(command)}")
    
    try:
        subprocess.run(command, check=True)
    except subprocess.CalledProcessError as e:
        logger.error(f"Git commit failed: {e}")
        raise

def get_recent_commits(limit=5):
    """Fetches the recent commit history to provide context for the AI."""
    try:
        logger.debug(f"Fetching last {limit} commits for AI context...")
        result = subprocess.run(
            ["git", "log", "-n", str(limit), "--oneline"],
            capture_output=True,
            encoding="utf-8",
            errors="replace",
            text=True
        )
        
        if result.returncode == 0 and result.stdout.strip():
            return result.stdout.strip()
            
        logger.debug("No previous commit history found (might be a new repository).")
        return "No previous commits found."
        
    except Exception as e:
        logger.warning(f"Failed to fetch commit history: {e}", exc_info=True)
        return "Could not retrieve commit history."