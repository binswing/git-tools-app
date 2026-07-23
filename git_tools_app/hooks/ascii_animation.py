import time
import sys
from git_tools_app.utils.logger import get_logger

logger = get_logger(__name__)

# The Developer Schema for Dynamic UI Generation
HOOK_SCHEMA = {
    "name": "ASCII Animation",
    "description": "Plays a fun ASCII animation in the terminal.",
    "options": [
        {
            "key": "style",
            "type": "text",
            "label": "Animation Style (rocket / train)",
            "default": "rocket"
        },
        {
            "key": "speed",
            "type": "text",
            "label": "Frame Delay in seconds (e.g., 0.08)",
            "default": "0.08"
        }
    ]
}

def _clear_screen():
    """Uses ANSI escape codes to instantly clear the screen and move the cursor home."""
    sys.stdout.write("\033[2J\033[H")
    sys.stdout.flush()

def play_rocket(speed: float):
    """Animates a rocket launching upwards."""
    rocket_body = [
        "    ^    ",
        "   / \\   ",
        "  /___\\  ",
        "  |   |  ",
        "  |___|  ",
        "  /   \\  ",
        " /|   |\\ ",
        "  |___|  "
    ]
    
    # Move the rocket up by decreasing the top padding
    for padding in range(25, -5, -1):
        _clear_screen()
        print("\n" * padding)
        
        for line in rocket_body:
            print(line)
            
        # Alternate the exhaust flame for a flicker effect
        if padding % 2 == 0:
            print("   ***   ")
            print("  *****  ")
        else:
            print("  *****  ")
            print("   ***   ")
            
        time.sleep(speed)

def play_train(speed: float):
    """Animates a train driving across the screen from right to left."""
    train_frames = [
        "      o O ___ _________ ",
        "    _][__|o| |O O O O| ",
        "   <_______|-|_______| ",
        "    /O-O-O     o   o   "
    ]
    
    # The train is facing left (<), so it needs to move right-to-left!
    # Decrease the padding to drive it forward.
    for padding in range(70, -1, -1):
        _clear_screen()
        print("\n" * 10) # Center it vertically
        
        for line in train_frames:
            print(" " * padding + line)
            
        time.sleep(speed)

def execute(addon_options, parsed_args, config_context):
    """The execution logic called by the event dispatcher."""
    style = addon_options.get("style", "rocket").lower()
    
    try:
        speed = float(addon_options.get("speed", "0.08"))
    except ValueError:
        speed = 0.08

    logger.debug(f"ASCII Animation Hook playing style: {style}")
    
    # Hide the terminal cursor during animation to prevent flickering
    sys.stdout.write("\033[?25l")
    sys.stdout.flush()
    
    try:
        if style == "train":
            play_train(speed)
        else:
            play_rocket(speed)
    finally:
        # Guarantee the screen is cleared and the cursor is restored, even if the user hits Ctrl+C
        _clear_screen()
        sys.stdout.write("\033[?25h")
        sys.stdout.flush()