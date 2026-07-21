import subprocess
import sys

def run(args):
    """Overrides the default git help command to show GTA features first."""
    
    # If no arguments are provided, show the GTA custom help menu
    if not args:
        print("=========================================")
        print("█▀▀ ▀█▀ ▄▀█   █▀ █▀▀ ▀█▀ █ █ █▀█")
        print("█▄█  █  █▀█   ▄█ ██▄  █  █▄█ █▀▀")
        print("=========================================\n")
        print("GTA (Git Tool App)\n")
        
        print("GTA wraps standard Git. Any normal Git command (e.g., `gta status`, `gta rebase`)")
        print("will work exactly as expected by passing through to your system's Git.\n")
        
        print("Custom GTA Commands:")
        print("  setting     Launch the interactive UI to configure AI and Hooks")
        print("  help        Show this help message\n")
        
        print("To get standard Git help for a specific command, use: `gta help <command>`\n")
        
    # If an argument is provided (e.g., `gta help rebase`), pass it to standard Git
    else:
        try:
            subprocess.run(["git", "help"] + args)
        except KeyboardInterrupt:
            sys.exit(130)
        except Exception as e:
            print(f"Error executing git help: {e}")
            sys.exit(1)