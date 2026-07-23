import uuid
from pathlib import Path
import questionary
from git_tools_app.ui.setting.base_scene import BaseScene
from git_tools_app.core.hook_api import get_available_hooks
from git_tools_app.core.events import SUPPORTED_EVENTS
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
        logger.info("-- ADDON DASHBOARD --\n")
        
        addons = config_context.setdefault("addons", [])
        choices = []
        
        for index, addon in enumerate(addons):
            status = "✅ ON" if addon.get("enabled") else "❌ OFF"
            choices.append(questionary.Choice(f"[{status}] {addon['name']} ({addon['hook_type']})", value=index))
            
        choices.append(questionary.Choice("➕ Create New Addon", value="create"))
        choices.append(questionary.Choice("⬅️  Go Back to Main Menu", value="main_menu"))

        choice = questionary.select("Select an addon to edit, or create a new one:", choices=choices).ask()
        
        if choice == "main_menu" or choice is None:
            return "main_menu"
        elif choice == "create":
            return "create_addon"
        else:
            return self.view_edit_addon(config_context, choice)

    def _prompt_dynamic_schema(self, addon_id, schema_options, existing_options=None):
        """Generates UI prompts dynamically. File handling is completely dictated by the schema."""
        existing_options = existing_options or {}
        new_opts = {}
        
        for opt in schema_options:
            default_val = existing_options.get(opt["key"], opt.get("default", ""))
            
            if opt["type"] == "file":
                logger.info("")
                val = questionary.path(f"Configure {opt['label']} (Tab to autocomplete):", default=default_val).ask()
                
                # If they provided a path, it isn't already in our managed folder, and the file exists
                if val and opt.get("target_folder", "") not in val and Path(val).exists():
                    target_folder = opt.get("target_folder", "assets")
                    prefix = opt.get("target_name_prefix", "file_")
                    file_ext = Path(val).suffix
                    
                    # Create a completely unique, schema-driven filename (e.g., audio_b4f9...2a.wav)
                    target_filename = f"{prefix}{addon_id}{file_ext}"
                    
                    success = import_external_file(val, target_folder, target_filename)
                    if success:
                        val = f"{target_folder}/{target_filename}"
                        
            elif opt["type"] == "text":
                val = questionary.text(f"Configure {opt['label']}:", default=default_val).ask()
                
            new_opts[opt["key"]] = val or default_val
            
        return new_opts

    def _prompt_events(self, existing_events=None):
        existing_events = existing_events or []
        
        # Dynamically build choice list from the master event registry
        events_list = [
            questionary.Choice(
                item["label"], 
                value=item["id"], 
                checked=item["id"] in existing_events
            )
            for item in SUPPORTED_EVENTS
        ]
        return questionary.checkbox("Select trigger events:", choices=events_list).ask() or []

    def view_create_addon(self, config_context: dict) -> str:
        self.clear_screen()
        logger.info("-- CREATE NEW ADDON --\n")
        
        if not self.available_hooks:
            logger.info("No hooks found in the system.")
            input("Press ENTER to return...")
            return "addon_list"

        name = questionary.text("Addon Name:").ask()
        if not name: return "addon_list"

        hook_choices = [questionary.Choice(f"{h_id} - {data['schema']['name']}", value=h_id) for h_id, data in self.available_hooks.items()]
        hook_type = questionary.select("Select Hook Capability:", choices=hook_choices).ask()
        if not hook_type: return "addon_list"

        events = self._prompt_events()
        
        # Generate the UUID FIRST, so the dynamic schema prompter can use it for file handling
        new_addon_id = str(uuid.uuid4())
        
        logger.info("\n-- Configure Addon Options --")
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
        logger.info(f"-- EDITING: {addon['name']} --\n")
        
        status_label = "Disable" if addon["enabled"] else "Enable"
        
        choices = [
            questionary.Choice(f"🔄 Toggle Status ({status_label})", value="toggle"),
            questionary.Choice("⚙️  Reconfigure Options", value="reconfigure"),
            questionary.Choice("📅 Edit Triggers", value="triggers"),
            questionary.Choice("🗑️  Delete Addon", value="delete"),
            questionary.Choice("⬅️  Go Back", value="addon_list")
        ]
        
        action = questionary.select("Action:", choices=choices).ask()
        
        if action == "toggle":
            addon["enabled"] = not addon["enabled"]
        elif action == "reconfigure":
            schema_options = self.available_hooks.get(addon["hook_type"], {}).get("schema", {}).get("options", [])
            addon["options"] = self._prompt_dynamic_schema(addon_id, schema_options, addon["options"])
        elif action == "triggers":
            addon["events"] = self._prompt_events(addon["events"])
        elif action == "delete":
            if questionary.confirm(f"Are you sure you want to delete '{addon['name']}'?").ask():
                config_context["addons"].pop(addon_index)
                
        return "addon_list"