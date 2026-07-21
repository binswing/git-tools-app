import sys
from git_tool_app.core.ai import get_active_provider
from git_tool_app.ai.prompts_template import load_commitgen_system_prompt_template

def generate_commit_message(model, prompt_guideline, diff_content):
    """Delegates the commit generation to the active provider."""
    provider = get_active_provider()
    
    # Ensure the provider actually implements the generation function
    if not hasattr(provider, 'generate_message'):
        print(f"[GTA Error] The active provider does not support message generation.")
        sys.exit(1)
    system_prompt = load_commitgen_system_prompt_template(prompt_guideline)
    return provider.generate_message(model, system_prompt, f"Code Diff: \n```\n{diff_content}\n```")