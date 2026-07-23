import questionary
from git_tools_app.ui.setting.base_scene import BaseScene

class EventConfigScene(BaseScene):
    def run(self, config_context: dict) -> str:
        commands = ["commit", "push", "checkout", "merge", "pull"]
        
        while True:
            self.clear_screen()
            print("=== EVENT PIPELINE ===\n")
            
            # Align header to match Questionary's selection pointer
            print("  COMMAND ")
            print("  " + "-" * 42)
            
            choices = []
            for cmd in commands:
                label = f"{cmd}"
                choices.append(questionary.Choice(label, value=cmd))
                
            choices.append(questionary.Choice("Back", value="main_menu"))
            
            # Instruction hidden to keep the table clean
            selected_cmd = questionary.select(
                "", 
                choices=choices,
                instruction="(Use arrow keys to select a command)"
            ).ask()
            
            if selected_cmd == "main_menu" or selected_cmd is None:
                return "main_menu"
                
            self._select_phase(config_context, selected_cmd)

    def _select_phase(self, config_context: dict, cmd: str):
        """Step 2: Selecting the 'Cell' (Pre or Post)"""
        while True:
            self.clear_screen()
            print(f"=== {cmd.upper()} PIPELINE ===\n")
            
            pre_evt = f"pre-{cmd}"
            post_evt = f"post-{cmd}"
            
            choices = [
                questionary.Choice(f"{pre_evt:<15} (Before execution)", value=pre_evt),
                questionary.Choice(f"{post_evt:<15} (After execution)", value=post_evt),
                questionary.Choice("Back", value="back")
            ]
            
            event_id = questionary.select("Select phase:", choices=choices).ask()
            
            if event_id == "back" or event_id is None:
                return
                
            self.manage_event_order(config_context, event_id)

    def manage_event_order(self, config_context: dict, event: str):
        """Step 3: Reordering addons for the selected cell"""
        addons = config_context.setdefault("addons", [])
        
        while True:
            self.clear_screen()
            print(f"=== PIPELINE ORDER: {event} ===\n")
            
            event_addons = [(idx, a) for idx, a in enumerate(addons) if event in a.get("events", [])]
            
            if not event_addons:
                print(f"No addons currently registered for '{event}'.")
                input("\nPress ENTER to return...")
                return
                
            choices = []
            for position, (original_idx, addon) in enumerate(event_addons):
                status = "ON" if addon.get("enabled") else "OFF"
                label = f"[{position + 1}] [{status}] {addon['name']} ({addon['hook_type']})"
                choices.append(questionary.Choice(label, value=original_idx))
                
            choices.append(questionary.Choice("Back", value="back"))
            
            selected_idx = questionary.select("Select addon to shift priority:", choices=choices).ask()
            
            if selected_idx == "back" or selected_idx is None:
                return
                
            action = questionary.select("Priority Shift:", choices=[
                questionary.Choice("Move Up   (Run Earlier)", value="up"),
                questionary.Choice("Move Down (Run Later)", value="down"),
                questionary.Choice("Cancel", value="cancel")
            ]).ask()
            
            if action == "up" and selected_idx > 0:
                addons[selected_idx], addons[selected_idx - 1] = addons[selected_idx - 1], addons[selected_idx]
            elif action == "down" and selected_idx < len(addons) - 1:
                addons[selected_idx], addons[selected_idx + 1] = addons[selected_idx + 1], addons[selected_idx]