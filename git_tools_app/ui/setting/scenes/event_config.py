"""Scene for configuring event pipelines and managing addons."""

import time
import uuid
from pathlib import Path
from typing import override

import questionary

from git_tools_app.core.hook_api import get_available_hooks
from git_tools_app.ui.setting.base_scene import BaseScene
from git_tools_app.utils.config import import_external_file


class EventConfigScene(BaseScene):
    """Scene for configuring event pipelines and managing addons."""

    def _prompt_command(self) -> str | None:
        """Helper to render the command selection menu."""
        commands = ["commit", "push", "checkout", "merge", "pull"]
        choices = [questionary.Choice(cmd, value=cmd) for cmd in commands]
        choices.append(questionary.Choice("Back", value="main_menu"))

        return questionary.select("", choices=choices, instruction="(Use arrow keys to select a command)").ask()

    def _prompt_manage_action(self, event: str, event_addons: list):
        """Helper to prompt the user for their next action in the manage menu."""
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

        instruction = "Select addon to reorder/unregister, or create a new one:" if event_addons else "Select action:"

        return questionary.select(instruction, choices=choices).ask()

    def _unregister_addon(self, addons: list, selected_idx: int, event: str):
        """Helper to unregister an addon from a specific event."""
        addon_name = addons[selected_idx]["name"]
        if event in addons[selected_idx]["events"]:
            addons[selected_idx]["events"].remove(event)
        print(f"\nUnregistered '{addon_name}' from the {event} pipeline.")
        time.sleep(1)

    def _get_reorder_choices(self, event_addons: list, current_pos: int) -> list:
        """Helper to generate the position choices for the reordering prompt."""
        choices = []
        for i, (_, addon) in enumerate(event_addons):
            label = f"[{i + 1}] {addon['name']}"
            if i == current_pos:
                label += " (Current)"
            choices.append(questionary.Choice(label, value=i))

        choices.append(questionary.Choice("Cancel", value="cancel"))
        return choices

    def _execute_reorder(self, addons: list, selected_idx: int, new_pos: int, event: str):
        """Helper to physically move the addon to the newly selected position in the master list."""
        addon_to_move = addons.pop(selected_idx)

        # Re-evaluate remaining event-specific addons after the pop
        remaining = [(idx, a) for idx, a in enumerate(addons) if event in a.get("events", [])]

        if new_pos < len(remaining):
            target_master_idx = remaining[new_pos][0]
            addons.insert(target_master_idx, addon_to_move)
        else:
            target_master_idx = remaining[-1][0]
            addons.insert(target_master_idx + 1, addon_to_move)

    def _reorder_addon(self, addons: list, selected_idx: int, event: str, event_addons: list):
        """Helper to surgically reorder an addon within the pipeline."""
        addon_name = addons[selected_idx]["name"]

        # Determine current position relative to event_addons list
        current_pos = next(i for i, (m_idx, _) in enumerate(event_addons) if m_idx == selected_idx)

        # Build choices and prompt user
        pos_choices = self._get_reorder_choices(event_addons, current_pos)
        new_pos = questionary.select(f"Move '{addon_name}' to the position of:", choices=pos_choices).ask()

        # Guard clause: Abort if user cancelled, closed the prompt, or picked the same spot
        if new_pos in ("cancel", None, current_pos):
            return

        # Execute the actual list manipulation
        self._execute_reorder(addons, selected_idx, new_pos, event)

    def _process_file_option(self, addon_id: str, opt: dict, val: str) -> str:
        """Helper to process file selection schemas via Guard Clauses."""
        if not val or not Path(val).exists():
            return val

        if not opt.get("copy", True):
            return str(Path(val).expanduser().resolve())

        target_folder = opt.get("target_folder", "assets")
        if target_folder in val:
            return val

        prefix = opt.get("target_name_prefix", "file_")
        file_ext = Path(val).suffix
        target_filename = f"{prefix}{addon_id}{file_ext}"

        success = import_external_file(val, target_folder, target_filename)
        if success:
            return f"{target_folder}/{target_filename}"

        return str(Path(val).expanduser().resolve())

    def _get_event_addons(self, addons: list, event: str) -> list:
        """Helper to filter and enumerate addons for a specific event."""
        return [(idx, a) for idx, a in enumerate(addons) if event in a.get("events", [])]

    def _handle_addon_action(self, addons: list, selected_idx: int, event: str, event_addons: list):
        """Helper to prompt and route the user's action for a selected addon."""
        addon_name = addons[selected_idx]["name"]

        action = questionary.select(
            f"Action for '{addon_name}':",
            choices=[
                questionary.Choice("Reorder", value="reorder"),
                questionary.Choice(f"Unregister from {event}", value="unregister"),
                questionary.Choice("Cancel", value="cancel"),
            ],
        ).ask()

        # Guard clause: grouped conditions reduce complexity
        if action in ("cancel", None):
            return

        if action == "unregister":
            self._unregister_addon(addons, selected_idx, event)
        elif action == "reorder":
            self._reorder_addon(addons, selected_idx, event, event_addons)

    @override
    def run(self, config_context: dict) -> str:
        """Run the event configuration scene, allowing users to manage addons for different command events."""
        while True:
            self.clear_screen()
            print("=== EVENT PIPELINE ===\n")
            print("  COMMAND ")
            print("  " + "-" * 42)

            selected_cmd = self._prompt_command()

            if selected_cmd == "main_menu" or selected_cmd is None:
                return "main_menu"

            self._select_phase(config_context, selected_cmd)

    def _select_phase(self, config_context: dict, cmd: str):
        """Allow the user to select a phase (pre or post) for a specific command and manage its addons."""
        while True:
            self.clear_screen()
            print(f"=== {cmd.upper()} PIPELINE ===\n")

            pre_evt = f"pre-{cmd}"
            post_evt = f"post-{cmd}"

            choices = [
                questionary.Choice(f"{pre_evt:<15} (Before execution)", value=pre_evt),
                questionary.Choice(f"{post_evt:<15} (After execution)", value=post_evt),
                questionary.Choice("Back", value="back"),
            ]

            event_id = questionary.select("Select phase:", choices=choices).ask()

            if event_id == "back" or event_id is None:
                return

            self.manage_event_order(config_context, event_id)

    def manage_event_order(self, config_context: dict, event: str):
        """Manages the order of addons for a specific event, allowing users to reorder, unregister, or create new addons."""
        addons = config_context.setdefault("addons", [])

        while True:
            self.clear_screen()
            print(f"=== PIPELINE ORDER: {event} ===\n")

            event_addons = self._get_event_addons(addons, event)
            selected_idx = self._prompt_manage_action(event, event_addons)

            # Grouped condition reduces complexity
            if selected_idx in ("back", None):
                return

            if selected_idx == "create":
                self._create_addon_for_event(config_context, event)
                continue

            # Delegate the secondary prompt and routing
            self._handle_addon_action(addons, selected_idx, event, event_addons)

    def _create_addon_for_event(self, config_context: dict, event: str):
        """Create a new addon for a specific event, prompting the user for necessary details and options."""
        available_hooks = get_available_hooks()

        self.clear_screen()
        print(f"=== CREATE ADDON FOR: {event.upper()} ===\n")

        if not available_hooks:
            print("No hooks available in registry.")
            input("\nPress ENTER to return...")
            return

        name = questionary.text("Addon Name:").ask()
        if not name:
            return

        max_pad = max((len(h_id) for h_id in available_hooks.keys()), default=15)

        hook_choices = [
            questionary.Choice(f"{h_id:<{max_pad}} | {data['schema']['name']}", value=h_id)
            for h_id, data in available_hooks.items()
        ]
        hook_type = questionary.select("Select Hook Type:", choices=hook_choices).ask()
        if not hook_type:
            return

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
            "enabled": True,
        }

        config_context["addons"].append(new_addon)
        print(f"\nSuccessfully attached '{name}' to the {event} pipeline!")

        time.sleep(1.2)

    def _prompt_dynamic_schema(self, addon_id, schema_options):
        """Prompt the user for dynamic schema options based on the provided schema configuration."""
        new_opts = {}

        for opt in schema_options:
            default_val = opt.get("default", "")

            if opt["type"] == "file":
                raw_val = questionary.path(f"{opt['label']}:", default=default_val).ask()
                val = self._process_file_option(addon_id, opt, raw_val)

            elif opt["type"] == "text":
                val = questionary.text(f"{opt['label']}:", default=default_val).ask()

            else:
                val = default_val

            new_opts[opt["key"]] = val or default_val

        return new_opts
