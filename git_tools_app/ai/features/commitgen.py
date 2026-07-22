import sys
from git_tools_app.core.ai import get_active_provider
from git_tools_app.ai.prompts_template import load_commitgen_system_prompt_template
from git_tools_app.utils.logger import get_logger

logger = get_logger(__name__)

def generate_commit_message(model, prompt_guideline, diff_content, recent_commits=""):
    """Delegates the commit generation to the active provider."""
    provider = get_active_provider()
    
    if not hasattr(provider, 'generate_message'):
        logger.error(f"The active provider '{provider.__name__}' does not support message generation.")
        sys.exit(1)
        
    system_prompt = load_commitgen_system_prompt_template(prompt_guideline)
    user_prompt = (
        f"Repository's Recent Commit History (For Style Context):\n"
        f"```\n{recent_commits}\n```\n\n"
        f"Current Staged Code Diff:\n"
        f"```\n{diff_content}\n```"
    )
    
    logger.debug(f"Routing commit generation to provider: {provider.__name__}")
    
    return provider.generate_message(model, system_prompt, user_prompt)