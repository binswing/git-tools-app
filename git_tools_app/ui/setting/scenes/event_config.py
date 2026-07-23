import uuid
from pathlib import Path
import questionary
from git_tools_app.ui.setting.base_scene import BaseScene
from git_tools_app.core.hook_api import get_available_hooks
from git_tools_app.utils.config import import_external_file

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
            
            selected_cmd = questionary.select(
                "", 
                choices=choices,
                instruction="(Use arrow keys to select a command)"
            ).ask()
            
            if selected_cmd == "main_menu" or selected_cmd is None:
                return "main_menu"
                
            self._select_phase(config_context, selected_cmd)

    def _select_phase(self, config_context: dict, cmd: str):
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
        addons = config_context.setdefault("addons", [])
        
        while True:
            self.clear_screen()
            print(f"=== PIPELINE ORDER: {event} ===\n")
            
            event_addons = [(idx, a) for idx, a in enumerate(addons) if event in a.get("events", [])]
            
            choices = []
            if not event_addons:
                print(f"No addons currently registered for '{event}'.\n")
            else:
                for position, (original_idx, addon) in enumerate(event_addons):
                    status = "ON" if addon.get("enabled") else "OFF"
                    label = f"[{position + 1}] [{status}] {addon['name']} ({addon['hook_type']})"
                    choices.append(questionary.Choice(label, value=original_idx))
                
            choices.append(questionary.Choice("Create New Addon for this Event", value="create"))
            choices.append(questionary.Choice("Back", value="back"))
            
            instruction = "Select addon to reorder, or create a new one:" if event_addons else "Select action:"
            
            selected_idx = questionary.select(instruction, choices=choices).ask()
            
            if selected_idx == "back" or selected_idx is None:
                return
                
            if selected_idx == "create":
                self._create_addon_for_event(config_context, event)
                continue
                
            # Determine the selected addon's current relative position (0, 1, 2...)
            current_pos = next(i for i, (m_idx, _) in enumerate(event_addons) if m_idx == selected_idx)
            
            # Generate the list of new target positions using actual addon names
            pos_choices = []
            for i in range(len(event_addons)):
                target_name = event_addons[i][1]["name"]
                if i == current_pos:
                    pos_choices.append(questionary.Choice(f"[{i + 1}] {target_name} (Current)", value=i))
                else:
                    pos_choices.append(questionary.Choice(f"[{i + 1}] {target_name}", value=i))
                    
            pos_choices.append(questionary.Choice("Cancel", value="cancel"))
            
            new_pos = questionary.select(
                f"Move '{addons[selected_idx]['name']}' to the position of:", 
                choices=pos_choices
            ).ask()
            
            if new_pos == "cancel" or new_pos is None or new_pos == current_pos:
                continue
                
            # SURGICAL REORDERING
            addon_to_move = addons.pop(selected_idx)
            
            # Recalculate remaining event indices because popping changed the master array lengths
            remaining_event_addons = [(idx, a) for idx, a in enumerate(addons) if event in a.get("events", [])]
            
            if new_pos < len(remaining_event_addons):
                # Insert directly before the addon that currently occupies the target position
                target_master_idx = remaining_event_addons[new_pos][0]
                addons.insert(target_master_idx, addon_to_move)
            else:
                # If moved to the very bottom, insert it right after the last related addon
                target_master_idx = remaining_event_addons[-1][0]
                addons.insert(target_master_idx + 1, addon_to_move)

    def _create_addon_for_event(self, config_context: dict, event: str):
        """Creates a new addon and automatically attaches it to the current event context."""
        available_hooks = get_available_hooks()
        
        self.clear_screen()
        print(f"=== CREATE ADDON FOR: {event.upper()} ===\n")
        
        if not available_hooks:
            print("No hooks available in registry.")
            input("\nPress ENTER to return...")
            return

        name = questionary.text("Addon Name:").ask()
        if not name: return

        hook_choices = [
            questionary.Choice(f"{h_id:<12} | {data['schema']['name']}", value=h_id) 
            for h_id, data in available_hooks.items()
        ]
        hook_type = questionary.select("Select Hook Type:", choices=hook_choices).ask()
        if not hook_type: return

        new_addon_id = str(uuid.uuid4())
        
        self.clear_screen()
        print(f"=== CONFIGURE OPTIONS: {name.upper()} ===\n")
        
        schema_options = available_hooks[hook_type]["schema"].get("options", [])
        options = self._prompt_dynamic_schema(new_addon_id, schema_options)

        new_addon = {
            "id": new_addon_id,
            "name": name,
            "hook_type": hook_type,
            "events": [event], 
            "options": options,
            "enabled": True
        }
        
        config_context["addons"].append(new_addon)
        print(f"\nSuccessfully attached '{name}' to the {event} pipeline!")
        
        import time
        time.sleep(1.2)

    def _prompt_dynamic_schema(self, addon_id, schema_options):
        """Processes dynamic fields based on the hook developer's schema."""
        new_opts = {}
        for opt in schema_options:
            default_val = opt.get("default", "")
            
            if opt["type"] == "file":
                val = questionary.path(f"{opt['label']}:", default=default_val).ask()
                
                if val and opt.get("target_folder", "") not in val and Path(val).exists():
                    target_folder = opt.get("target_folder", "assets")
                    prefix = opt.get("target_name_prefix", "file_")
                    file_ext = Path(val).suffix
                    
                    target_filename = f"{prefix}{addon_id}{file_ext}"
                    
                    success = import_external_file(val, target_folder, target_filename)
                    if success:
                        val = f"{target_folder}/{target_filename}"
                        
            elif opt["type"] == "text":
                val = questionary.text(f"{opt['label']}:", default=default_val).ask()
                
            new_opts[opt["key"]] = val or default_val
            
        return new_opts