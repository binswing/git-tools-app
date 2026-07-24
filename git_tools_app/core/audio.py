"""Core audio functionality for Git Tools App."""

import os

import pygame

from git_tools_app.utils.logger import get_logger

os.environ["PYGAME_HIDE_SUPPORT_PROMPT"] = "hide"

logger = get_logger(__name__)


def play_audio(audio_path):
    """Initializes the mixer and plays the audio file, blocking until finished."""
    if not audio_path or not os.path.exists(audio_path):
        logger.warning(f"Audio file not found at: {audio_path}")
        return

    try:
        logger.debug(f"Initializing Pygame audio mixer for file: {audio_path}")
        pygame.mixer.init()
        pygame.mixer.music.load(audio_path)
        pygame.mixer.music.play()

        while pygame.mixer.music.get_busy():
            pygame.time.Clock().tick(10)
        logger.debug("Finished audio playback.")
    except Exception as e:
        logger.error(f"Could not play audio tag: {e}", exc_info=True)
