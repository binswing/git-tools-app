import os

_PROMPTS_TEMPLATE_DIR = os.path.dirname(__file__)

with open(os.path.join(_PROMPTS_TEMPLATE_DIR, "COMMITGENSYSTEM.md"), "r") as _f:
    _COMMITGENSYSTEM_PROMPT_TEMPLATE = _f.read()

def load_commitgen_system_prompt_template(prompt_guideline: str) -> str:
    """Load the commit generation system prompt template."""
    return _COMMITGENSYSTEM_PROMPT_TEMPLATE.format(prompt_guideline=prompt_guideline)