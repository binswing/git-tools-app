from git_tools_app.utils.config import load_config, save_config
from git_tools_app.ui.setting.scenes.main_menu import MainMenuScene
from git_tools_app.ui.setting.scenes.ai_config import AIConfigScene
from git_tools_app.ui.setting.scenes.addon_config import AddonConfigScene
from git_tools_app.ui.setting.scenes.event_config import EventConfigScene
from git_tools_app.utils.logger import get_logger

logger = get_logger(__name__)

class SceneManager:
    def __init__(self):
        self.config_context = load_config()
        self.scenes = {
            "main_menu": MainMenuScene(),
            "ai_config": AIConfigScene(),
            "addon_config": AddonConfigScene(),
            "event_config": EventConfigScene(),
        }
        self.current_scene_id = "main_menu"

    def run(self):
        while self.current_scene_id not in ["quit_save", "quit_discard"]:
            scene_obj = self.scenes.get(self.current_scene_id)
            if not scene_obj: break
            self.current_scene_id = scene_obj.run(self.config_context)

        if self.current_scene_id == "quit_save":
            save_config("ai_provider", self.config_context.get("ai_provider"))
            save_config("model", self.config_context.get("model"))
            # Save the new master addons list
            save_config("addons", self.config_context.get("addons"))
            logger.info("\nSettings applied successfully!")
        else:
            logger.info("\nDiscarded changes. Exiting...\n")