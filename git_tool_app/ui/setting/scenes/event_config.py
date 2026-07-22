import questionary
from git_tool_app.ui.setting.base_scene import BaseScene
from git_tool_app.utils.logger import get_logger

logger = get_logger(__name__)

class EventConfigScene(BaseScene):
    def run(self, config_context: dict) -> str:
        while True:
            self.clear_screen()
            logger.info("-- EXECUTION ORDER MANAGER --\n")
            logger.info("Because addons run sequentially, you can change their execution order here.\n")
            
            events = ["post-commit", "post-merge", "post-push"]
            choices = [questionary.Choice(e, value=e) for e in events]
            choices.append(questionary.Choice("⬅️  Go Back", value="main_menu"))
            
            event = questionary.select("Select an event to manage order:", choices=choices).ask()
            
            if event == "main_menu" or event is None:
                return "main_menu"
                
            self.manage_event_order(config_context, event)

    def manage_event_order(self, config_context: dict, event: str):
        addons = config_context.setdefault("addons", [])
        
        while True:
            self.clear_screen()
            logger.info(f"-- ORDER FOR: {event.upper()} --\n")
            
            # Filter addons that trigger on this specific event
            event_addons = [(idx, a) for idx, a in enumerate(addons) if event in a.get("events", [])]
            
            if not event_addons:
                logger.info("No addons assigned to this event.")
                input("Press ENTER to return...")
                return
                
            choices = []
            for position, (original_idx, addon) in enumerate(event_addons):
                choices.append(questionary.Choice(f"{position + 1}. {addon['name']} ({addon['hook_type']})", value=original_idx))
                
            choices.append(questionary.Choice("⬅️  Go Back", value="back"))
            
            selected_idx = questionary.select("Select an addon to shift its position:", choices=choices).ask()
            
            if selected_idx == "back" or selected_idx is None:
                return
                
            action = questionary.select("Move Addon:", choices=[
                questionary.Choice("⬆️ Move Up (Run Earlier)", value="up"),
                questionary.Choice("⬇️ Move Down (Run Later)", value="down"),
                questionary.Choice("❌ Cancel", value="cancel")
            ]).ask()
            
            if action == "up" and selected_idx > 0:
                # Swap in the master array
                addons[selected_idx], addons[selected_idx - 1] = addons[selected_idx - 1], addons[selected_idx]
            elif action == "down" and selected_idx < len(addons) - 1:
                addons[selected_idx], addons[selected_idx + 1] = addons[selected_idx + 1], addons[selected_idx]