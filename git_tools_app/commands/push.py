import argparse
import subprocess
from git_tools_app.core import events
from git_tools_app.utils.logger import get_logger

logger = get_logger(__name__)

def run(args):
    logger.debug(f"Running gta push with args: {args}")
    parser = argparse.ArgumentParser(prog="gta push", description="Push to remote.")
    parser.add_argument("--no-hooks", action="store_true", help="Skip all post-execution features")
    parsed_args, extra_git_args = parser.parse_known_args(args)
    
    if not parsed_args.no_hooks:
        events.trigger("pre-push", parsed_args)

    logger.info(f"Executing: git push {' '.join(extra_git_args)}")
    result = subprocess.run(["git", "push"] + extra_git_args)
    
    if result.returncode == 0 and not parsed_args.no_hooks:
        events.trigger("post-push", parsed_args)