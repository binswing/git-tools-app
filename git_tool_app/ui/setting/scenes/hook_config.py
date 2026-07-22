import questionary
from git_tool_app.ui.setting.base_scene import BaseScene
from git_tool_app.utils.config import import_external_file
from git_tool_app.utils.logger import get_logger

logger = get_logger(__name__)

class HookConfigScene(BaseScene):
    def run(self, config_context: dict) -> str:
        current_view = "hook_menu"
        
        while True:
            if current_view == "hook_menu":
                current_view = self.view_hook_menu()
                
            elif current_view == "audio_config":
                current_view = self.view_audio_config(config_context)
                
            # NEW: The routing state for the triggers menu
            elif current_view == "audio_triggers":
                current_view = self.view_audio_triggers(config_context)
                
            elif current_view == "main_menu":
                return "main_menu"

    def view_hook_menu(self) -> str:
        self.clear_screen()
        logger.info("-- HOOK SETTINGS --\n")
        
        choice = questionary.select(
            "Select a hook to configure:",
            choices=[
                questionary.Choice("🎵 Audio Tag Hook", value="audio_config"),
                questionary.Choice("⬅️  Go Back to Main Menu", value="main_menu")
            ]
        ).ask()
        
        logger.debug(f"Hook menu choice: {choice}")
        return choice or "main_menu"

    def view_audio_config(self, config_context: dict) -> str:
        self.clear_screen()
        logger.info("-- AUDIO TAG HOOK CONFIGURATION --\n")
        
        current_status = config_context.get("play_tags", True)
        
        choices = [
            questionary.Choice("🔊 Enable Audio (Play Tags)", value="enable"),
            questionary.Choice("🔇 Disable Audio (Silent Mode)", value="disable"),
            questionary.Choice("📂 Import Custom Audio Tag (.wav)", value="import_audio"),
            # NEW: Menu option to configure events
            questionary.Choice("⚙️  Configure Trigger Events", value="audio_triggers"),
            questionary.Choice("⬅️  Go Back to Hooks Menu", value="hook_menu")
        ]
        
        default_choice = choices[0] if current_status else choices[1]

        choice = questionary.select(
            "What would you like to do?",
            choices=choices,
            default=default_choice
        ).ask()
        
        if choice is None or choice == "hook_menu":
            return "hook_menu"
            
        if choice == "enable":
            logger.debug("Audio tags toggled ON in config context.")
            config_context["play_tags"] = True
            return "audio_config" # Stays on this menu
            
        elif choice == "disable":
            logger.debug("Audio tags toggled OFF in config context.")
            config_context["play_tags"] = False
            return "audio_config" # Stays on this menu
            
        elif choice == "import_audio":
            self.import_audio_workflow()
            return "audio_config"
            
        elif choice == "audio_triggers":
            return "audio_triggers"

    def view_audio_triggers(self, config_context: dict) -> str:
        """The checkbox view to select which Git commands trigger the audio."""
        self.clear_screen()
        logger.info("-- AUDIO TAG: TRIGGER EVENTS --\n")
        
        # Load the current context to figure out which boxes should be pre-checked
        current_events = config_context.get("audio_hook_events", ["post-push", "post-merge"])
        
        choices = [
            questionary.Choice("Post-Commit (Plays after AI generation)", value="post-commit", checked="post-commit" in current_events),
            questionary.Choice("Post-Merge (Plays on successful merge)", value="post-merge", checked="post-merge" in current_events),
            questionary.Choice("Post-Push (Plays when pushed to remote)", value="post-push", checked="post-push" in current_events),
        ]
        
        selected_events = questionary.checkbox(
            "Select Git events to trigger the tag (Space to toggle, Enter to confirm):",
            choices=choices
        ).ask()
        
        # If the user didn't press Ctrl+C, save the array
        if selected_events is not None:
            logger.debug(f"Audio trigger events updated to: {selected_events}")
            config_context["audio_hook_events"] = selected_events
            
        # Drop them back into the audio config hub
        return "audio_config"

    def import_audio_workflow(self):
        logger.info("")
        file_path = questionary.path(
            "Enter the path to your .wav file (Tab to autocomplete):"
        ).ask()
        
        if file_path:
            logger.debug(f"Initiating audio file import from path: {file_path}")
            import_external_file(
                source_path=file_path, 
                target_folder="assets", 
                target_filename="producer_tag.wav"
            )
            input("Press ENTER to continue...")