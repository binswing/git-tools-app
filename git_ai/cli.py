import argparse
import os
from . import ai, git_utils, audio

DEFAULT_PROMPT = "Write a concise, conventional Git commit message for the following diff."

def get_commit_prompt():
    if os.path.exists("COMMITMSG.md"):
        with open("COMMITMSG.md", "r") as f:
            return f.read()
    return DEFAULT_PROMPT

def main():
    parser = argparse.ArgumentParser(description="Git CLI with Local AI & Producer Tags")
    subparsers = parser.add_subparsers(dest="command", required=True)

    # Command: commit
    commit_parser = subparsers.add_parser("commit", help="Generate AI commit message")
    commit_parser.add_argument("--model", type=str, help="Ollama model to use")

    # Command: push
    push_parser = subparsers.add_parser("push", help="Push to remote and play producer tag")
    push_parser.add_argument("--no-tag", action="store_true", help="Disable the producer tag")

    # Command: merge (Branch removed as a strict requirement so we can pass ALL flags down to git)
    merge_parser = subparsers.add_parser("merge", help="Merge branch and play producer tag")
    merge_parser.add_argument("--no-tag", action="store_true", help="Disable the producer tag")

    # Using parse_known_args allows us to capture native git arguments (like --set-upstream)
    args, extra_git_args = parser.parse_known_args()

    if args.command == "commit":
        models = ai.get_installed_models()
        model_to_use = args.model

        if not model_to_use:
            print("Available models:", ", ".join(models))
            model_to_use = input("Enter model to use: ").strip()
            
        if model_to_use not in models:
            print(f"Model '{model_to_use}' not found in Ollama.")
            return

        diff = git_utils.get_staged_diff()
        prompt = get_commit_prompt()
        
        print(f"Generating commit message using {model_to_use}...")
        message = ai.generate_commit_message(model_to_use, prompt, diff)
        
        print(f"\nGenerated Message:\n{message}\n")
        confirm = input("Do you want to commit with this message? (y/n): ")
        
        if confirm.lower() == 'y':
            git_utils.execute_commit(message)
            print("Commit successful!")
        else:
            print("Commit aborted.")

    elif args.command == "push":
        # Pass the extra arguments straight to git push
        git_utils.run_git_command(["push"] + extra_git_args)
        audio.play_producer_tag("producer_tag.wav", disabled=args.no_tag)
        print("Push completed.")

    elif args.command == "merge":
        # Pass the extra arguments straight to git merge
        git_utils.run_git_command(["merge"] + extra_git_args)
        audio.play_producer_tag("producer_tag.wav", disabled=args.no_tag)
        print("Merge command executed.")

if __name__ == "__main__":
    main()