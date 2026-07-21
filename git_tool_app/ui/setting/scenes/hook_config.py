import questionary
from git_tool_app.ui.setting.base_scene import BaseScene
from git_tool_app.utils.config import import_external_file

class HookConfigScene(BaseScene):
    def run(self, config_context: dict) -> str:
        current_view = "hook_menu"
        
        while True:
            if current_view == "hook_menu":
                current_view = self.view_hook_menu()
                
            elif current_view == "audio_config":
                current_view = self.view_audio_config(config_context)
                
            elif current_view == "main_menu":
                return "main_menu"

    def view_hook_menu(self) -> str:
        self.clear_screen()
        print("-- HOOK SETTINGS --\n")
        
        choice = questionary.select(
            "Select a hook to configure:",
            choices=[
                questionary.Choice("🎵 Audio Tag Hook", value="audio_config"),
                questionary.Choice("⬅️  Go Back to Main Menu", value="main_menu")
            ]
        ).ask()
        
        return choice or "main_menu"

    def view_audio_config(self, config_context: dict) -> str:
        self.clear_screen()
        print("-- AUDIO TAG HOOK CONFIGURATION --\n")
        
        current_status = config_context.get("play_tags", True)
        
        # We assign specific string values to handle the routing logic below
        choices = [
            questionary.Choice("🔊 Enable Audio (Play Tags)", value="enable"),
            questionary.Choice("🔇 Disable Audio (Silent Mode)", value="disable"),
            questionary.Choice("📂 Import Custom Audio Tag (.wav)", value="import_audio"),
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
            config_context["play_tags"] = True
            return "hook_menu"
            
        elif choice == "disable":
            config_context["play_tags"] = False
            return "hook_menu"
            
        elif choice == "import_audio":
            self.import_audio_workflow()
            # Return to this exact same view after the import finishes
            return "audio_config"

    def import_audio_workflow(self):
        """Handles the path auto-completion and file copying logic."""
        print()
        # questionary.path provides native terminal tab-completion!
        file_path = questionary.path(
            "Enter the path to your .wav file (Tab to autocomplete):"
        ).ask()
        
        if file_path:
            # We enforce the naming convention "producer_tag.wav" and put it in "assets"
            import_external_file(
                source_path=file_path, 
                target_folder="assets", 
                target_filename="producer_tag.wav"
            )
            input("Press ENTER to continue...")