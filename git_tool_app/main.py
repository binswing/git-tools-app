import sys
import importlib
import pkgutil
import git_tool_app.commands
import git_tool_app.hooks
from git_tool_app.core.git import pass_through_to_git
from git_tool_app.utils.config import CONFIG_FILE

def load_modules(package):
    """Dynamically loads submodules and returns those with a 'run' function."""
    registry = {}
    for _, module_name, _ in pkgutil.iter_modules(package.__path__):
        module = importlib.import_module(f"{package.__name__}.{module_name}")
        if hasattr(module, 'run'):
            registry[module_name] = module.run
    return registry

def main():
    # 1. Load hooks so they silently register to events in the background
    if not CONFIG_FILE.exists():
        print("First run detected! Launching setup wizard...")
        # Dynamically import the setting command and run it
        from git_tool_app.commands import setting
        setting.run([])
        # Exit after setup so they have a clean slate for their next command
        return
    
    load_modules(git_tool_app.hooks)
    
    # 2. Load commands to handle the user routing
    commands_registry = load_modules(git_tool_app.commands)
    
    # 3. Handle naked command `gta`
    if len(sys.argv) < 2:
        pass_through_to_git([])
        return

    command = sys.argv[1]
    args = sys.argv[2:]

    # 4. Route the execution
    if command in commands_registry:
        commands_registry[command](args)
    else:
        # Fallback to standard Git commands (status, log, rebase, etc.)
        pass_through_to_git(sys.argv[1:])

if __name__ == "__main__":
    main()