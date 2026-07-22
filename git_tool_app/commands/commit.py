import os
import argparse
from git_tool_app.core import ai, git
from git_tool_app.ai.features import commitgen
from git_tool_app.utils.config import load_config
from git_tool_app.utils.logger import get_logger

logger = get_logger(__name__)

def get_commit_prompt(config):
    prompt_path = config.get("default_prompt_path")
    if prompt_path and os.path.exists(prompt_path):
        logger.debug(f"Loading commit prompt template from: {prompt_path}")
        with open(prompt_path, "r") as f:
            return f.read()
    logger.debug("Default prompt file not found. Falling back to inline default prompt.")
    return "Write a concise, conventional Git commit message for the following diff."

def run(args):
    logger.debug(f"Running gta commit with args: {args}")
    parser = argparse.ArgumentParser(prog="gta commit", description="Generate an AI commit message.")
    parser.add_argument("--model", type=str, help="Override default model")
    parsed_args, _ = parser.parse_known_args(args)

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
    prompt = get_commit_prompt(config)
    
    logger.info(f"Generating commit message using {model_to_use}...")
    message = commitgen.generate_commit_message(model_to_use, prompt, diff)
    
    logger.info(f"\nGenerated Message:\n{message}\n")
    confirm = input("Do you want to commit with this message? (y/n): ")
    
    if confirm.lower() == 'y':
        git.execute_commit(message)
        logger.info("Commit successful!")
    else:
        logger.info("Commit aborted by user.")