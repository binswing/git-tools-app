import uuid
from pathlib import Path
import questionary
from git_tools_app.ui.setting.base_scene import BaseScene
from git_tools_app.core.hook_api import get_available_hooks
from git_tools_app.utils.logger import get_logger
from git_tools_app.utils.config import import_external_file

logger = get_logger(__name__)

class AddonConfigScene(BaseScene):
    def run(self, config_context: dict) -> str:
        current_view = "addon_list"
        self.available_hooks = get_available_hooks()
        
        while True:
            if current_view == "addon_list":
                current_view = self.view_addon_list(config_context)
            elif current_view == "create_addon":
                current_view = self.view_create_addon(config_context)
            elif current_view == "main_menu":
                return "main_menu"

    def view_addon_list(self, config_context: dict) -> str:
        self.clear_screen()
        print("=== ADDON MANAGEMENT ===\n")
        
        addons = config_context.setdefault("addons", [])
        choices = []
        
        for index, addon in enumerate(addons):
            status = "ON " if addon.get("enabled") else "OFF"
            label = f"[{status}] {addon['name']:<20} ({addon['hook_type']})"
            choices.append(questionary.Choice(label, value=index))
            
        choices.append(questionary.Choice("Create New Addon", value="create"))
        choices.append(questionary.Choice("Back", value="main_menu"))

        choice = questionary.select("Select addon to configure:", choices=choices).ask()
        
        if choice == "main_menu" or choice is None:
            return "main_menu"
        elif choice == "create":
            return "create_addon"
        else:
            return self.view_edit_addon(config_context, choice)

    def _prompt_dynamic_schema(self, addon_id, schema_options, existing_options=None):
        existing_options = existing_options or {}
        new_opts = {}
        
        for opt in schema_options:
            default_val = existing_options.get(opt["key"], opt.get("default", ""))
            
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

    def _prompt_events(self, existing_events=None):
        """Step 1: Selecting the Git Command for the Addon Triggers"""
        commands = ["commit", "push", "checkout", "merge", "pull"]
        selected_events = set(existing_events or [])

        while True:
            self.clear_screen()
            print("=== ASSIGN TRIGGER EVENTS ===\n")
            print(f"  {'COMMAND':<12} {'ACTIVE TRIGGERS'}")
            print("  " + "-" * 42)

            choices = []
            for cmd in commands:
                pre_evt = f"pre-{cmd}"
                post_evt = f"post-{cmd}"
                
                # Check current status to populate the right column
                active = []
                if pre_evt in selected_events: active.append("pre")
                if post_evt in selected_events: active.append("post")
                
                status = f"[{', '.join(active)}]" if active else "[-]"
                label = f"{cmd:<12} {status}"
                
                choices.append(questionary.Choice(label, value=cmd))

            choices.append(questionary.Choice("Done", value="done"))

            selected_cmd = questionary.select(
                "",
                choices=choices,
                instruction="(Use arrow keys to select a command)"
            ).ask()

            if selected_cmd == "done" or selected_cmd is None:
                return list(selected_events)

            self._configure_command_events(selected_cmd, selected_events)

    def _configure_command_events(self, cmd: str, selected_events: set):
        """Step 2: Toggling Pre and Post phases for the selected command"""
        self.clear_screen()
        print(f"=== {cmd.upper()} TRIGGERS ===\n")

        pre_evt = f"pre-{cmd}"
        post_evt = f"post-{cmd}"

        choices = [
            questionary.Choice(
                f"{pre_evt:<15} (Before execution)", 
                value=pre_evt, 
                checked=pre_evt in selected_events
            ),
            questionary.Choice(
                f"{post_evt:<15} (After execution)", 
                value=post_evt, 
                checked=post_evt in selected_events
            )
        ]

        result = questionary.checkbox(
            "Select triggers (Space to toggle, Enter to confirm):", 
            choices=choices
        ).ask()

        if result is not None:
            # Remove previous selections for this command to prevent ghosting
            selected_events.discard(pre_evt)
            selected_events.discard(post_evt)
            # Re-apply the newly checked triggers
            for evt in result:
                selected_events.add(evt)

    def view_create_addon(self, config_context: dict) -> str:
        self.clear_screen()
        print("=== CREATE ADDON ===\n")
        
        if not self.available_hooks:
            print("No hooks available.")
            input("\nPress ENTER to return...")
            return "addon_list"

        name = questionary.text("Addon Name:").ask()
        if not name: return "addon_list"

        hook_choices = [
            questionary.Choice(f"{h_id:<12} | {data['schema']['name']}", value=h_id) 
            for h_id, data in self.available_hooks.items()
        ]
        hook_type = questionary.select("Select Hook Type:", choices=hook_choices).ask()
        if not hook_type: return "addon_list"

        events = self._prompt_events()
        
        new_addon_id = str(uuid.uuid4())
        
        # Clear the screen again so the schema prompts have a clean slate 
        # after exiting the event drill-down loop.
        self.clear_screen()
        print(f"=== CONFIGURE OPTIONS: {name.upper()} ===\n")
        
        schema_options = self.available_hooks[hook_type]["schema"].get("options", [])
        options = self._prompt_dynamic_schema(new_addon_id, schema_options)

        new_addon = {
            "id": new_addon_id,
            "name": name,
            "hook_type": hook_type,
            "events": events,
            "options": options,
            "enabled": True
        }
        
        config_context["addons"].append(new_addon)
        return "addon_list"

    def view_edit_addon(self, config_context: dict, addon_index: int) -> str:
        addon = config_context["addons"][addon_index]
        addon_id = addon["id"]
        
        self.clear_screen()
        print(f"=== EDIT ADDON: {addon['name'].upper()} ===\n")
        
        status_label = "Disable" if addon["enabled"] else "Enable"
        
        choices = [
            questionary.Choice(f"Toggle Status ({status_label})", value="toggle"),
            questionary.Choice("Reconfigure Options", value="reconfigure"),
            questionary.Choice("Edit Trigger Events", value="triggers"),
            questionary.Choice("Delete Addon", value="delete"),
            questionary.Choice("Back", value="addon_list")
        ]
        
        action = questionary.select("Action:", choices=choices).ask()
        
        if action == "toggle":
            addon["enabled"] = not addon["enabled"]
        elif action == "reconfigure":
            self.clear_screen()
            print(f"=== RECONFIGURE OPTIONS: {addon['name'].upper()} ===\n")
            schema_options = self.available_hooks.get(addon["hook_type"], {}).get("schema", {}).get("options", [])
            addon["options"] = self._prompt_dynamic_schema(addon_id, schema_options, addon["options"])
        elif action == "triggers":
            addon["events"] = self._prompt_events(addon["events"])
        elif action == "delete":
            if questionary.confirm(f"Delete '{addon['name']}'?").ask():
                config_context["addons"].pop(addon_index)
                
        return "addon_list"