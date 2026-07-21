import questionary
from git_tool_app.ui.setting.base_scene import BaseScene
class HookConfigScene(BaseScene):
    def run(self, config_context: dict) -> str:
        # Start at the hook selection menu
        current_view = "hook_menu"
        
        # Internal state machine to route between different hook configurations
        while True:
            if current_view == "hook_menu":
                current_view = self.view_hook_menu()
                
            elif current_view == "audio_config":
                current_view = self.view_audio_config(config_context)
                
            # Easily add new hook views here in the future
            # elif current_view == "rerunner_config":
            #     current_view = self.view_rerunner_config(config_context)
                
            # If the user chooses to leave the hook hub entirely, exit back to SceneManager
            elif current_view == "main_menu":
                return "main_menu"

    def view_hook_menu(self) -> str:
        """The main hub for selecting which hook to configure."""
        self.clear_screen()
        print("-- HOOK SETTINGS --\n")
        
        choice = questionary.select(
            "Select a hook to configure:",
            choices=[
                questionary.Choice("🎵 Audio Tag Hook", value="audio_config"),
                # Drop future hooks right here:
                # questionary.Choice("🔄 Program Rerunner Hook", value="rerunner_config"),
                questionary.Choice("⬅️  Go Back to Main Menu", value="main_menu")
            ]
        ).ask()
        
        # Return the selected view, or main_menu if Ctrl+C is pressed
        return choice or "main_menu"

    def view_audio_config(self, config_context: dict) -> str:
        """The isolated configuration screen specifically for the Audio hook."""
        self.clear_screen()
        print("-- AUDIO TAG HOOK CONFIGURATION --\n")
        
        current_status = config_context.get("play_tags", True)
        
        choices = [
            questionary.Choice("🔊 Enable Audio (Play Tags)", value=True),
            questionary.Choice("🔇 Disable Audio (Silent Mode)", value=False),
            questionary.Choice("⬅️  Go Back to Hooks Menu", value="hook_menu")
        ]
        
        default_choice = choices[0] if current_status else choices[1]

        choice = questionary.select(
            "Should GTA play producer tags on push and merge?",
            choices=choices,
            default=default_choice
        ).ask()
        
        # Handle Ctrl+C or Go Back
        if choice == "hook_menu" or choice is None:
            return "hook_menu"
            
        # Save the setting to the temporary context
        config_context["play_tags"] = choice
        
        # Send the user back to the hook hub so they can configure something else
        return "hook_menu"