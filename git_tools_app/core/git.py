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
    """Fetches the staged changes, handling the initial commit edge case."""
    try:
        # Check if HEAD exists (it won't on the very first commit of a new repo)
        head_check = subprocess.run(["git", "rev-parse", "--verify", "HEAD"], capture_output=True, text=True)
        
        if head_check.returncode != 0:
            logger.debug("Initial commit detected. Diffing against the empty tree hash.")
            # This magic hash represents a completely empty Git tree
            diff_cmd = ["git", "diff", "--cached", "4b825dc642cb6eb9a060e54bf8d69288fbee4904"]
        else:
            diff_cmd = ["git", "diff", "--cached"]

        result = subprocess.run(diff_cmd, capture_output=True, text=True, check=True)
        diff_output = result.stdout.strip()
        
        if not diff_output:
            logger.warning("No staged changes found. Did you forget to run `git add`?")
            
        return diff_output
    except subprocess.CalledProcessError as e:
        logger.error(f"Failed to fetch staged diff: {e}")
        return ""

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