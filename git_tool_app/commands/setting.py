import os
import argparse
from git_tool_app.core import ai
from git_tool_app.utils.config import load_config, save_config, CONFIG_FILE

def clear_screen():
    """Clears the Ubuntu/Linux terminal for a fresh scene render."""
    os.system('cls' if os.name == 'nt' else 'clear')

class SetupWizard:
    def __init__(self):
        self.config = load_config()
        self.scene = "welcome"
        self.models = []

    def run(self):
        """The main loop that renders scenes until the user exits."""
        while self.scene != "exit":
            clear_screen()
            if self.scene == "welcome":
                self.scene_welcome()
            elif self.scene == "model_config":
                self.scene_model_config()
            elif self.scene == "audio_config":
                self.scene_audio_config()
            elif self.scene == "save":
                self.scene_save()

    def scene_welcome(self):
        print("=========================================")
        print("█▀▀ ▀█▀ ▄▀█   █▀ █▀▀ ▀█▀ █ █ █▀█")
        print("█▄█  █  █▀█   ▄█ ██▄  █  █▄█ █▀▀")
        print("=========================================\n")
        print("Welcome to the Git Tool App Setup.")
        print("Let's configure your AI and audio hooks.\n")
        
        choice = input("[Press ENTER to start | Type 'q' to quit]: ").strip().lower()
        if choice == 'q':
            self.scene = "exit"
        else:
            self.scene = "model_config"

    def scene_model_config(self):
        print("-- SCENE 2: OLLAMA MODEL --\n")
        if not self.models:
            print("Scanning local Ollama instance...")
            self.models = ai.get_installed_models()

        print("Installed Models:")
        for idx, model in enumerate(self.models, 1):
            print(f"  [{idx}] {model}")
        print(f"\nCurrent Default: {self.config.get('model')}")
        
        choice = input("\nSelect a number to change, or press ENTER to keep current: ").strip()
        
        if choice.isdigit() and 1 <= int(choice) <= len(self.models):
            self.config["model"] = self.models[int(choice) - 1]
            
        self.scene = "audio_config"

    def scene_audio_config(self):
        print("-- SCENE 3: AUDIO HOOKS --\n")
        status = "ENABLED" if self.config.get("play_tags") else "DISABLED"
        print(f"Producer tags are currently: {status}\n")
        
        print("  [1] Enable Audio")
        print("  [2] Disable Audio")
        
        choice = input("\nSelect an option, or press ENTER to keep current: ").strip()
        
        if choice == '1':
            self.config["play_tags"] = True
        elif choice == '2':
            self.config["play_tags"] = False
            
        self.scene = "save"

    def scene_save(self):
        print("-- SAVING CONFIGURATION --\n")
        save_config("model", self.config["model"])
        save_config("play_tags", self.config["play_tags"])
        
        print("Settings applied successfully!")
        print(f"Saved to: {CONFIG_FILE}\n")
        input("Press ENTER to exit to terminal...")
        self.scene = "exit"


def run(args):
    """The entry point when 'gta setting' is executed."""
    parser = argparse.ArgumentParser(prog="gta setting", description="Launch the interactive setup wizard.")
    parser.parse_known_args(args)
    
    wizard = SetupWizard()
    wizard.run()