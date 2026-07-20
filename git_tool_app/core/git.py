import subprocess
import sys

def pass_through_to_git(args):
    """Executes a native git command and streams stdout/stderr straight to the Ubuntu terminal."""
    try:
        # Using call() blocks and binds directly to the terminal UI
        exit_code = subprocess.call(["git"] + args)
        sys.exit(exit_code)
    except KeyboardInterrupt:
        sys.exit(130)
    except Exception as e:
        print(f"Fatal error executing git: {e}")
        sys.exit(1)

def get_staged_diff():
    """Captures the output of git diff --cached for Ollama prompts."""
    try:
        result = subprocess.run(
            ["git", "diff", "--cached"], 
            capture_output=True, 
            text=True, 
            check=True
        )
        if not result.stdout.strip():
            print("No staged changes found. Did you forget to `git add`?")
            sys.exit(1)
        return result.stdout
    except subprocess.CalledProcessError as e:
        print(f"Git command failed: {e.stderr}")
        sys.exit(1)

def execute_commit(message):
    """Commits staged changes with the AI-generated message."""
    try:
        subprocess.run(["git", "commit", "-m", message], check=True)
    except subprocess.CalledProcessError as e:
        print(f"Commit failed. Ensure changes are staged.")
        sys.exit(1)