import os
# Keeps your Ubuntu terminal clean by hiding the Pygame welcome message
os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = "hide"
import pygame

def play_audio(audio_path):
    """Initializes the mixer and plays the audio file, blocking until finished."""
    if not os.path.exists(audio_path):
        print(f"[GTA] Audio file not found at: {audio_path}")
        return
        
    try:
        pygame.mixer.init()
        pygame.mixer.music.load(audio_path)
        pygame.mixer.music.play()
        
        # Keep the process alive while the audio plays
        while pygame.mixer.music.get_busy():
            pygame.time.Clock().tick(10)
    except Exception as e:
        print(f"[GTA] Could not play audio: {e}")