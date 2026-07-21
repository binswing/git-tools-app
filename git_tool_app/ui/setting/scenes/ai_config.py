import questionary
import importlib
from git_tool_app.ui.setting.base_scene import BaseScene

class AIConfigScene(BaseScene):
    def run(self, config_context: dict) -> str:
        self.clear_screen()
        print("-- AI & PROVIDER SETTINGS --\n")

        providers = ["ollama", "openai", "gemini", "claude", "hf_inference"]
        current_provider = config_context.get("ai_provider", "ollama")

        # 1. Build Provider Choices with "Go Back"
        provider_choices = [
            questionary.Choice(title=f"  {p}", value=p) for p in providers
        ]
        provider_choices.append(questionary.Choice(title="⬅️  Go Back", value="main_menu"))

        provider_choice = questionary.select(
            "Select AI Provider:",
            choices=provider_choices,
            default=current_provider if current_provider in providers else None
        ).ask()

        # Handle Ctrl+C or selecting "Go Back"
        if not provider_choice or provider_choice == "main_menu":
            return "main_menu"

        config_context["ai_provider"] = provider_choice

        # 2. Fetch Models for Selected Provider
        print(f"\nFetching models for '{provider_choice}' via API...")
        try:
            provider_module = importlib.import_module(f"git_tool_app.ai.ai_providers.{provider_choice}")
            models = provider_module.get_models()
        except Exception as e:
            print(f"\n[Error] Failed to fetch models: {e}")
            input("\nPress ENTER to return to Main Menu...")
            return "main_menu"

        if not models:
            print("\nNo models found. Please check your API keys or local setup.")
            input("\nPress ENTER to return to Main Menu...")
            return "main_menu"

        # 3. Build Model Choices with "Go Back"
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

        # Save model choice only if the user didn't choose to Go Back
        if model_choice and model_choice != "main_menu":
            config_context["model"] = model_choice

        return "main_menu"