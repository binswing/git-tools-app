#this file is not for general use, it is for internal use only. It is used to configure the hooks that are available in the git-tools-app. The hooks are used to trigger events in the git-tools-app
import questionary
from git_tools_app.ui.setting.base_scene import BaseScene
from git_tools_app.utils.config import import_external_file
from git_tools_app.utils.logger import get_logger
from git_tools_app.core.events import SUPPORTED_EVENTS
logger = get_logger(__name__)

class HookConfigScene(BaseScene):
    def run(self, config_context: dict) -> str:
        current_view = "hook_menu"
        
        while True:
            if current_view == "hook_menu":
                current_view = self.view_hook_menu()
                
            elif current_view == "audio_config":
                current_view = self.view_audio_config(config_context)
                
            elif current_view == "audio_triggers":
                current_view = self.view_audio_triggers(config_context)
                
            elif current_view == "main_menu":
                return "main_menu"

    def view_hook_menu(self) -> str:
        self.clear_screen()
        print("=== HOOK SETTINGS ===\n")
        
        choice = questionary.select(
            "Select hook to configure:",
            choices=[
                questionary.Choice("Audio Tag Hook", value="audio_config"),
                questionary.Choice("Back", value="main_menu")
            ]
        ).ask()
        
        return choice or "main_menu"

    def view_audio_config(self, config_context: dict) -> str:
        self.clear_screen()
        print("=== AUDIO TAG CONFIGURATION ===\n")
        
        current_status = config_context.get("play_tags", True)
        status_label = "Disable" if current_status else "Enable"
        
        choices = [
            questionary.Choice(f"Toggle Audio ({status_label})", value="toggle"),
            questionary.Choice("Import Custom Audio (.wav)", value="import_audio"),
            questionary.Choice("Configure Trigger Events", value="audio_triggers"),
            questionary.Choice("Back", value="hook_menu")
        ]

        choice = questionary.select(
            "Select action:",
            choices=choices
        ).ask()
        
        if choice is None or choice == "hook_menu":
            return "hook_menu"
            
        if choice == "toggle":
            config_context["play_tags"] = not current_status
            return "audio_config"
            
        elif choice == "import_audio":
            self.import_audio_workflow()
            return "audio_config"
            
        elif choice == "audio_triggers":
            return "audio_triggers"

    def view_audio_triggers(self, config_context: dict) -> str:
        self.clear_screen()
        print("=== AUDIO TAG: TRIGGER EVENTS ===\n")
        
        current_events = config_context.get("audio_hook_events", ["post-push", "post-merge"])
        
        events_list = [
            questionary.Choice(
                f"{evt['id']:<15} | {evt['description']}", 
                value=evt["id"], 
                checked=evt["id"] in current_events
            )
            for evt in SUPPORTED_EVENTS
        ]
        
        selected_events = questionary.checkbox(
            "Select trigger events (Space to toggle):",
            choices=events_list
        ).ask()
        
        if selected_events is not None:
            config_context["audio_hook_events"] = selected_events
            
        return "audio_config"

    def import_audio_workflow(self):
        print()
        file_path = questionary.path(
            "Path to .wav file (Tab to autocomplete):"
        ).ask()
        
        if file_path:
            success = import_external_file(
                source_path=file_path, 
                target_folder="assets", 
                target_filename="producer_tag.wav"
            )
            if success:
                print("Audio import successful.")
            else:
                print("Import failed. Please check the file path.")
                
            input("\nPress ENTER to continue...")