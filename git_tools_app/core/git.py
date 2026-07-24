"""Core Git functionality for Git Tools App."""

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
    """Fetches the staged changes, handling initial commits and UTF-8 encodings safely."""
    try:
        # Check if HEAD exists (it won't on an initial commit)
        head_check = subprocess.run(
            ["git", "rev-parse", "--verify", "HEAD"],
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
        )

        if head_check.returncode != 0:
            logger.debug("Initial commit detected. Diffing against the empty tree hash.")
            diff_cmd = ["git", "diff", "--cached", "4b825dc642cb6eb9a060e54bf8d69288fbee4904"]
        else:
            diff_cmd = ["git", "diff", "--cached"]

        result = subprocess.run(
            diff_cmd, capture_output=True, text=True, encoding="utf-8", errors="replace", check=True
        )

        # Guard against NoneType before calling strip()
        diff_output = (result.stdout or "").strip()

        if not diff_output:
            logger.warning("No staged changes found. Did you forget to run `git add`?")

        return diff_output
    except subprocess.CalledProcessError as e:
        logger.error(f"Failed to fetch staged diff: {e}")
        return ""
    except Exception as e:
        logger.error(f"Unexpected error while getting staged diff: {e}")
        return ""


def get_recent_commits(limit=5):
    """Fetches recent commit history for AI context."""
    try:
        logger.debug(f"Fetching last {limit} commits for AI context...")
        result = subprocess.run(
            ["git", "log", "-n", str(limit), "--oneline"],
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
        )
        return (result.stdout or "").strip()
    except Exception as e:
        logger.error(f"Failed to fetch recent commits: {e}")
        return ""


def execute_commit(message, extra_args=None):
    """Executes the git commit command, passing through extra flags."""
    if extra_args is None:
        extra_args = []

    command = ["git", "commit", "-m", message] + extra_args
    logger.debug(f"Executing commit command: {' '.join(command)}")

    try:
        subprocess.run(command, check=True, text=True, encoding="utf-8", errors="replace")
    except subprocess.CalledProcessError as e:
        logger.error(f"Git commit failed: {e}")
        raise
