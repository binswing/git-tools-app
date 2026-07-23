import questionary
from git_tools_app.ui.setting.base_scene import BaseScene

class MainMenuScene(BaseScene):
    def run(self, config_context: dict) -> str:
        self.clear_screen()
        print("=== GTA CONFIGURATION ===\n")
        
        choices = [
            questionary.Choice("AI", value="ai_config"),
            questionary.Choice("Addons", value="addon_config"),
            questionary.Choice("Events", value="event_config"),
            questionary.Choice("Save & Exit", value="quit_save"),
            questionary.Choice("Discard & Exit", value="quit_discard")
        ]
        
        return questionary.select("Select category:", choices=choices).ask()