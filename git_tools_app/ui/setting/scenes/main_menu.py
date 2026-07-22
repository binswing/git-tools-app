import questionary
from git_tools_app.ui.setting.base_scene import BaseScene
from git_tools_app.utils.logger import get_logger

logger = get_logger(__name__)

class MainMenuScene(BaseScene):
    def run(self, config_context: dict) -> str:
        self.clear_screen()
        logger.info("=========================================")
        logger.info("█▀▀ ▀█▀ ▄▀█   █▀ █▀▀ ▀█▀ █ █ █▀█")
        logger.info("█▄█  █  █▀█   ▄█ ██▄  █  █▄█ █▀▀")
        logger.info("=========================================\n")

        choice = questionary.select(
            "Main Menu - Select a category to configure:",
            choices=[
                questionary.Choice("🤖 AI & Provider Settings", value="ai_config"),
                questionary.Choice("🔌 Addons Dashboard (Hooks)", value="addon_config"),
                questionary.Choice("⏱️  Execution Order (Events)", value="event_config"),
                questionary.Choice("💾 Save & Quit", value="quit_save"),
                questionary.Choice("❌ Discard & Quit", value="quit_discard")
            ]
        ).ask()

        return choice or "quit_discard"