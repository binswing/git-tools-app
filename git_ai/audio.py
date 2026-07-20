import os
os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = "hide"
import pygame

def play_producer_tag(audio_path="producer_tag.wav", disabled=False):
    if disabled or not os.path.exists(audio_path):
        return
        
    try:
        pygame.mixer.init()
        pygame.mixer.music.load(audio_path)
        pygame.mixer.music.play()
        
        # Keep script alive just long enough for the tag to finish playing
        while pygame.mixer.music.get_busy():
            pygame.time.Clock().tick(10)
    except Exception as e:
        print(f"Could not play producer tag: {e}")