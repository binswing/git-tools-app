"""Pull Command."""

import argparse
import subprocess

from git_tools_app.core import events
from git_tools_app.utils.logger import get_logger

logger = get_logger(__name__)


def run(args):
    """Serve as the entry point when 'gta pull' is executed."""
    logger.debug(f"Running gta pull with args: {args}")
    parser = argparse.ArgumentParser(prog="gta pull", description="Pull from remote.")
    parser.add_argument("--no-hooks", action="store_true", help="Skip all post-execution features")
    parsed_args, extra_git_args = parser.parse_known_args(args)

    if not parsed_args.no_hooks:
        events.trigger("pre-pull", parsed_args)

    logger.info(f"Executing: git pull {' '.join(extra_git_args)}")
    result = subprocess.run(["git", "pull"] + extra_git_args)

    if result.returncode == 0 and not parsed_args.no_hooks:
        events.trigger("post-pull", parsed_args)
