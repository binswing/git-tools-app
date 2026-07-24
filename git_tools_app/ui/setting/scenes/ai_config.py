"""Scene for configuring AI provider and model settings."""

import importlib
from typing import override

import questionary

from git_tools_app.ui.setting.base_scene import BaseScene
from git_tools_app.utils.logger import get_logger

logger = get_logger(__name__)


class AIConfigScene(BaseScene):
    """Scene for configuring AI provider and model settings."""

    def _prompt_provider(self, current_provider: str) -> str:
        """Prompts the user to select an AI provider."""
        providers = ["ollama", "openai", "gemini", "claude", "hf_inference"]
        provider_choices = [questionary.Choice(p, value=p) for p in providers]
        provider_choices.append(questionary.Choice("Back", value="main_menu"))

        return questionary.select(
            "Select AI Provider:",
            choices=provider_choices,
            default=current_provider if current_provider in providers else None,
        ).ask()

    def _fetch_models(self, provider_choice: str) -> list | None:
        """Dynamically imports the provider module and fetches available models."""
        print(f"\nFetching models for '{provider_choice}'...")
        try:
            logger.debug(f"Importing provider module: git_tools_app.ai.ai_providers.{provider_choice}")
            provider_module = importlib.import_module(f"git_tools_app.ai.ai_providers.{provider_choice}")
            return provider_module.get_models()
        except Exception as e:
            logger.error(f"Failed to fetch models for {provider_choice}: {e}", exc_info=True)
            print(f"Error fetching models: {e}")
            return None

    def _prompt_model(self, models: list, current_model: str) -> str:
        """Prompts the user to select a default model from the fetched list."""
        model_choices = [questionary.Choice(m, value=m) for m in models]
        model_choices.append(questionary.Choice("Back", value="main_menu"))

        return questionary.select(
            "Select Default Model:", choices=model_choices, default=current_model if current_model in models else None
        ).ask()

    @override
    def run(self, config_context: dict) -> str:
        """Runs the AI configuration scene, allowing users to select an AI provider and model."""
        self.clear_screen()
        print("=== AI & MODEL CONFIG ===\n")

        # 1. Select Provider
        provider_choice = self._prompt_provider(config_context.get("ai_provider", "ollama"))

        if not provider_choice or provider_choice == "main_menu":
            logger.debug("User selected Back from provider choice menu.")
            return "main_menu"

        config_context["ai_provider"] = provider_choice

        # 2. Fetch Models
        models = self._fetch_models(provider_choice)

        if models is None:
            # Exception occurred during fetch
            input("\nPress ENTER to return to Main Menu...")
            return "main_menu"

        if not models:
            # Fetch succeeded but returned empty list
            print(f"No available models found for provider '{provider_choice}'.")
            input("\nPress ENTER to return to Main Menu...")
            return "main_menu"

        # 3. Select Model
        model_choice = self._prompt_model(models, config_context.get("model", ""))

        if model_choice and model_choice != "main_menu":
            logger.debug(f"User set active model to: {model_choice}")
            config_context["model"] = model_choice

        return "main_menu"
