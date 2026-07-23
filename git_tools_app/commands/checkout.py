import argparse
import subprocess
from git_tools_app.core import events
from git_tools_app.utils.logger import get_logger

logger = get_logger(__name__)

def run(args):
    logger.debug(f"Running gta checkout with args: {args}")
    parser = argparse.ArgumentParser(prog="gta checkout", description="Checkout branches.")
    parser.add_argument("--no-hooks", action="store_true", help="Skip all post-execution features")
    parsed_args, extra_git_args = parser.parse_known_args(args)
    
    if not parsed_args.no_hooks:
        events.trigger("pre-checkout", parsed_args)

    logger.info(f"Executing: git checkout {' '.join(extra_git_args)}")
    result = subprocess.run(["git", "checkout"] + extra_git_args)
    
    if result.returncode == 0 and not parsed_args.no_hooks:
        events.trigger("post-checkout", parsed_args)