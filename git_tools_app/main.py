import sys
import importlib
import pkgutil
import git_tools_app.commands
import git_tools_app.hooks
from git_tools_app.core.git import pass_through_to_git
from git_tools_app.utils.logger import get_logger
from dotenv import load_dotenv

load_dotenv()
logger = get_logger(__name__)

def load_modules(package):
    """Dynamically loads submodules and returns those with a 'run' function."""
    registry = {}
    for _, module_name, _ in pkgutil.iter_modules(package.__path__):
        try:
            module = importlib.import_module(f"{package.__name__}.{module_name}")
            if hasattr(module, 'run'):
                registry[module_name] = module.run
                logger.debug(f"Loaded module '{module_name}' from package '{package.__name__}'")
        except Exception as e:
            logger.error(f"Failed to load module '{module_name}' from '{package.__name__}': {e}", exc_info=True)
    return registry

def main():
    logger.debug("Starting GTA CLI application execution...")
    
    # 1. Load hooks to register events silently in background
    load_modules(git_tools_app.hooks)
    
    # 2. Load custom GTA commands
    commands_registry = load_modules(git_tools_app.commands)
    
    # 3. Handle naked command `gta`
    if len(sys.argv) < 2:
        logger.debug("No subcommand specified. Passing through to native git...")
        pass_through_to_git([])
        return

    command = sys.argv[1]
    args = sys.argv[2:]

    # 4. Route command execution
    if command in commands_registry:
        logger.debug(f"Routing to registered GTA command: {command}")
        commands_registry[command](args)
    else:
        logger.debug(f"Subcommand '{command}' not in GTA registry. Passing through to native git...")
        pass_through_to_git(sys.argv[1:])

if __name__ == "__main__":
    main()