"""Base scene class."""

import os
import subprocess
from abc import (
    ABC,
    abstractmethod,
)

from git_tools_app.utils.logger import get_logger

logger = get_logger(__name__)


class BaseScene(ABC):
    """Abstract base class for all UI scenes."""

    def clear_screen(self):
        """Cross-platform terminal clear."""
        logger.debug("Clearing terminal screen...")

        subprocess.run("clear" if os.name == "posix" else "cls", shell=True)

    @abstractmethod
    def run(self, config_context: dict) -> str:
        """
        Executes the scene UI.

        Must return a string representing the ID of the next scene.
        """
        pass
