import argparse
import subprocess
from git_tool_app.core import events

def run(args):
    parser = argparse.ArgumentParser(prog="gta merge", description="Merge branches.")
    parser.add_argument("--no-hooks", action="store_true", help="Skip all post-execution features")
    parsed_args, extra_git_args = parser.parse_known_args(args)
    
    if not parsed_args.no_hooks:
        events.trigger("pre-merge", parsed_args)

    print(f"Executing: git merge {' '.join(extra_git_args)}")
    result = subprocess.run(["git", "merge"] + extra_git_args)
    
    if result.returncode == 0 and not parsed_args.no_hooks:
        events.trigger("post-merge", parsed_args)