import questionary
from git_tool_app.ui.setting.base_scene import BaseScene
from git_tool_app.utils.logger import get_logger

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
                questionary.Choice("🪝 Hook Settings (Audio, etc.)", value="hook_config"),
                questionary.Choice("💾 Save & Quit", value="quit_save"),
                questionary.Choice("❌ Discard & Quit", value="quit_discard")
            ]
        ).ask()

        logger.debug(f"User selected main menu action: {choice}")
        return choice or "quit_discard"