import questionary
from git_tool_app.ui.setting.base_scene import BaseScene

class MainMenuScene(BaseScene):
    def run(self, config_context: dict) -> str:
        self.clear_screen()
        print("=========================================")
        print("█▀▀ ▀█▀ ▄▀█   █▀ █▀▀ ▀█▀ █ █ █▀█")
        print("█▄█  █  █▀█   ▄█ ██▄  █  █▄█ █▀▀")
        print("=========================================\n")

        choice = questionary.select(
            "Main Menu - Select a category to configure:",
            choices=[
                questionary.Choice("🤖 AI & Provider Settings", value="ai_config"),
                questionary.Choice("🪝 Hook Settings (Audio, etc.)", value="hook_config"),
                questionary.Choice("💾 Save & Quit", value="quit_save"),
                questionary.Choice("❌ Discard & Quit", value="quit_discard")
            ]
        ).ask()

        # If user presses Ctrl+C, questionary returns None. Fallback to discard.
        return choice or "quit_discard"