from git_tool_app.utils.config import load_config, save_config, CONFIG_FILE
from git_tool_app.ui.setting.scenes.main_menu import MainMenuScene
from git_tool_app.ui.setting.scenes.ai_config import AIConfigScene
from git_tool_app.ui.setting.scenes.hook_config import HookConfigScene
from git_tool_app.utils.logger import get_logger

logger = get_logger(__name__)

class SceneManager:
    def __init__(self):
        logger.debug("Initializing SceneManager and loading config context...")
        self.config_context = load_config()
        
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
                logger.error(f"Scene '{self.current_scene_id}' not found.")
                break
                
            logger.debug(f"Transitioning to scene: {self.current_scene_id}")
            self.current_scene_id = scene_obj.run(self.config_context)

        # Handle exit state
        if self.current_scene_id == "quit_save":
            logger.debug("Saving settings from context...")
            save_config("ai_provider", self.config_context.get("ai_provider"))
            save_config("model", self.config_context.get("model"))
            save_config("play_tags", self.config_context.get("play_tags"))
            save_config("audio_hook_events", self.config_context.get("audio_hook_events"))
            logger.info("\nSettings applied successfully!")
            logger.info(f"Saved to: {CONFIG_FILE}\n")
        else:
            logger.info("\nDiscarded changes. Exiting...\n")