import subprocess
import sys

def run_git_command(command, capture_output=False):
    try:
        result = subprocess.run(
            ["git"] + command, 
            capture_output=capture_output, 
            text=True, 
            check=True
        )
        return result.stdout if capture_output else None
    except subprocess.CalledProcessError as e:
        print(f"Git command failed: {e.stderr if e.stderr else ''}")
        sys.exit(1)

def get_staged_diff():
    diff = run_git_command(["diff", "--cached"], capture_output=True)
    if not diff.strip():
        print("No staged changes found. Did you forget to `git add`?")
        sys.exit(1)
    return diff

def execute_commit(message):
    run_git_command(["commit", "-m", message])