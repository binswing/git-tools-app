from git_tool_app.utils.config import load_config, save_config, CONFIG_FILE
from git_tool_app.ui.setting.scenes.main_menu import MainMenuScene
from git_tool_app.ui.setting.scenes.ai_config import AIConfigScene
from git_tool_app.ui.setting.scenes.hook_config import HookConfigScene

class SceneManager:
    def __init__(self):
        # Load the configuration into a temporary context dictionary
        self.config_context = load_config()
        
        # Instantiate the scene objects
        self.scenes = {
            "main_menu": MainMenuScene(),
            "ai_config": AIConfigScene(),
            "hook_config": HookConfigScene()
        }
        self.current_scene_id = "main_menu"

    def run(self):
        """The main game loop for the terminal UI."""
        while self.current_scene_id not in ["quit_save", "quit_discard"]:
            scene_obj = self.scenes.get(self.current_scene_id)
            if not scene_obj:
                print(f"Error: Scene '{self.current_scene_id}' not found.")
                break
                
            # Execute the scene and capture where the user wants to go next
            self.current_scene_id = scene_obj.run(self.config_context)

        # Handle the exit state
        if self.current_scene_id == "quit_save":
            save_config("ai_provider", self.config_context.get("ai_provider"))
            save_config("model", self.config_context.get("model"))
            save_config("play_tags", self.config_context.get("play_tags"))
            print(f"\nSettings applied successfully!")
            print(f"Saved to: {CONFIG_FILE}\n")
        else:
            print("\nDiscarded changes. Exiting...\n")