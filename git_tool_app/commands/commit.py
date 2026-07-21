import os
import argparse
from git_tool_app.core import ai, git
from git_tool_app.ai.features import commitgen
from git_tool_app.utils.config import load_config

def get_commit_prompt(config):
    prompt_path = config.get("commitmsg_prompt_path")
    if os.path.exists(prompt_path):
        with open(prompt_path, "r") as f:
            return f.read()
    return "Write a concise, conventional Git commit message for the following diff."

def run(args):
    parser = argparse.ArgumentParser(prog="gta commit", description="Generate an AI commit message.")
    parser.add_argument("--model", type=str, help="Override the default Ollama model")
    parsed_args, _ = parser.parse_known_args(args)

    config = load_config()
    models = ai.get_installed_models()
    
    # Use the passed flag, or fallback to the config default
    model_to_use = parsed_args.model or config.get("model")

    # If the configured model isn't installed, prompt the user
    if model_to_use not in models:
        print(f"Model '{model_to_use}' not found. Available models: {', '.join(models)}")
        model_to_use = input("Enter model to use: ").strip()
        if model_to_use not in models:
            print("Invalid model selected. Aborting.")
            return

    diff = git.get_staged_diff()
    prompt = get_commit_prompt(config)
    
    print(f"Generating commit message using {model_to_use}...")
    message = commitgen.generate_commit_message(model_to_use, prompt, diff)
    
    print(f"\nGenerated Message:\n{message}\n")
    confirm = input("Do you want to commit with this message? (y/n): ")
    
    if confirm.lower() == 'y':
        git.execute_commit(message)
        print("Commit successful!")
    else:
        print("Commit aborted.")