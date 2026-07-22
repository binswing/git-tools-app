import questionary
import importlib
from git_tools_app.ui.setting.base_scene import BaseScene
from git_tools_app.utils.logger import get_logger

logger = get_logger(__name__)

class AIConfigScene(BaseScene):
    def run(self, config_context: dict) -> str:
        self.clear_screen()
        logger.info("-- AI & PROVIDER SETTINGS --\n")

        providers = ["ollama", "openai", "gemini", "claude", "hf_inference"]
        current_provider = config_context.get("ai_provider", "ollama")

        provider_choices = [
            questionary.Choice(title=f"  {p}", value=p) for p in providers
        ]
        provider_choices.append(questionary.Choice(title="⬅️  Go Back", value="main_menu"))

        provider_choice = questionary.select(
            "Select AI Provider:",
            choices=provider_choices,
            default=current_provider if current_provider in providers else None
        ).ask()

        if not provider_choice or provider_choice == "main_menu":
            logger.debug("User selected Go Back from provider choice menu.")
            return "main_menu"

        config_context["ai_provider"] = provider_choice

        logger.info(f"\nFetching models for '{provider_choice}' via API...")
        try:
            logger.debug(f"Importing provider module: git_tools_app.ai.ai_providers.{provider_choice}")
            provider_module = importlib.import_module(f"git_tools_app.ai.ai_providers.{provider_choice}")
            models = provider_module.get_models()
        except Exception as e:
            logger.error(f"Failed to fetch models for {provider_choice}: {e}", exc_info=True)
            input("\nPress ENTER to return to Main Menu...")
            return "main_menu"

        if not models:
            logger.warning(f"No available models found for provider '{provider_choice}'.")
            input("\nPress ENTER to return to Main Menu...")
            return "main_menu"

        current_model = config_context.get("model")
        model_choices = [
            questionary.Choice(title=f"  {m}", value=m) for m in models
        ]
        model_choices.append(questionary.Choice(title="⬅️  Go Back", value="main_menu"))

        model_choice = questionary.select(
            "Select Default Model:",
            choices=model_choices,
            default=current_model if current_model in models else None
        ).ask()

        if model_choice and model_choice != "main_menu":
            logger.debug(f"User set active model to: {model_choice}")
            config_context["model"] = model_choice

        return "main_menu"