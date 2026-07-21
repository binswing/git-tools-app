import argparse
from git_tool_app.ui.setting.manager import SceneManager

def run(args):
    """The entry point when 'gta setting' is executed."""
    parser = argparse.ArgumentParser(prog="gta setting", description="Launch the interactive setup UI.")
    parser.parse_known_args(args)
    
    manager = SceneManager()
    manager.run()