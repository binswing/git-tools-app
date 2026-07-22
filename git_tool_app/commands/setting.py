import argparse
from git_tool_app.ui.setting.manager import SceneManager
from git_tool_app.utils.logger import get_logger

logger = get_logger(__name__)

def run(args):
    """The entry point when 'gta setting' is executed."""
    logger.debug(f"Initializing interactive settings manager with args: {args}")
    parser = argparse.ArgumentParser(prog="gta setting", description="Launch the interactive setup UI.")
    parser.parse_known_args(args)
    
    manager = SceneManager()
    manager.run()