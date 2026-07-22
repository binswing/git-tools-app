import sys
from git_tool_app.core.ai import get_active_provider
from git_tool_app.ai.prompts_template import load_commitgen_system_prompt_template
from git_tool_app.utils.logger import get_logger

logger = get_logger(__name__)

def generate_commit_message(model, prompt_guideline, diff_content):
    """Delegates the commit generation to the active provider."""
    provider = get_active_provider()
    
    # Ensure the provider actually implements the generation function
    if not hasattr(provider, 'generate_message'):
        logger.error(f"The active provider '{provider.__name__}' does not support message generation.")
        sys.exit(1)
        
    system_prompt = load_commitgen_system_prompt_template(prompt_guideline)
    
    logger.debug(f"Routing commit generation to provider: {provider.__name__}")
    
    return provider.generate_message(model, system_prompt, f"Code Diff: \n```\n{diff_content}\n```")