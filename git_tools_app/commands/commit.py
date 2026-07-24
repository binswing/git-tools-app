"""Commit Command."""

import argparse
import os

from git_tools_app.ai.features import commitgen
from git_tools_app.core import (
    ai,
    events,
    git,
)
from git_tools_app.utils.config import load_config
from git_tools_app.utils.logger import get_logger

logger = get_logger(__name__)


def get_commit_prompt(config):
    """Load the commit prompt template from the config or use the default."""
    prompt_path = config.get("commitmsg_prompt_path")
    if prompt_path and os.path.exists(prompt_path):
        logger.debug(f"Loading commit prompt template from: {prompt_path}")
        with open(prompt_path, "r") as f:
            return f.read()
    logger.debug("Default prompt file not found. Falling back to inline default prompt.")
    return "Write a concise, conventional Git commit message for the following diff."


def run(args):
    """Serve as the entry point when 'gta commit' is executed."""
    logger.debug(f"Running gta commit with args: {args}")
    parser = argparse.ArgumentParser(prog="gta commit", description="Generate an AI commit message.")
    parser.add_argument("--model", type=str, help="Override default model")
    parser.add_argument("--no-hooks", action="store_true", help="Skip all post-execution features")
    parsed_args, extra_git_args = parser.parse_known_args(args)

    config = load_config()
    models = ai.get_installed_models()

    model_to_use = parsed_args.model or config.get("model")

    if model_to_use not in models:
        logger.warning(f"Model '{model_to_use}' not found in active provider. Available: {', '.join(models)}")
        model_to_use = input("Enter model to use: ").strip()
        if model_to_use not in models:
            logger.error("Invalid model selected. Aborting commit generation.")
            return

    diff = git.get_staged_diff()
    if not diff:
        if "--allow-empty" in extra_git_args:
            logger.info("Empty diff detected, but --allow-empty flag was passed.")
            diff = "[No code changes. This is an empty commit forced by the user.]"
        else:
            logger.error("Nothing to commit. Please run `git add` to stage your changes first.")
            return

    recent_commits = git.get_recent_commits(limit=5)
    prompt = get_commit_prompt(config)

    logger.info(f"Generating commit message using {model_to_use}...")
    message = commitgen.generate_commit_message(model_to_use, prompt, diff, recent_commits)

    logger.info(f"\nGenerated Message:\n{message}\n")
    confirm = input("Do you want to commit with this message? (y/n): ")

    if confirm.lower() == "y":
        if not parsed_args.no_hooks:
            events.trigger("pre-commit", parsed_args)

        git.execute_commit(message, extra_git_args)
        logger.info("Commit successful!")

        if not parsed_args.no_hooks:
            events.trigger("post-commit", parsed_args)

    else:
        logger.info("Commit aborted by user.")
