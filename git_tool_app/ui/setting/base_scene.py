import os
from abc import ABC, abstractmethod

class BaseScene(ABC):
    def clear_screen(self):
        """Cross-platform terminal clear."""
        os.system('clear' if os.name == 'posix' else 'cls')

    @abstractmethod
    def run(self, config_context: dict) -> str:
        """
        Executes the scene UI.
        Must return a string representing the ID of the next scene.
        """
        pass