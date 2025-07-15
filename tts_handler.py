"""Simplified TTS handler with direct animation control"""

import pygame
import tempfile
import os
import threading
import time
import logging
from gtts import gTTS
from config import TTS_LANGUAGE, TTS_SLOW

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class SimplifiedTTSHandler:
    def __init__(self):
        pygame.mixer.init()
        self.is_speaking = False
        self.obs_controller = None
        
    def set_obs_controller(self, obs_controller):
        """Set reference to OBS controller"""
        self.obs_controller = obs_controller
        
    def text_to_speech(self, text, lang=TTS_LANGUAGE):
        """Convert text to speech"""
        if not text or not text.strip():
            return None
            
        try:
            logger.info(f"Converting to speech: {text}")
            tts = gTTS(text=text, lang=lang, slow=TTS_SLOW)
            
            with tempfile.NamedTemporaryFile(delete=False, suffix='.mp3') as tmp_file:
                tts.save(tmp_file.name)
                return tmp_file.name
                
        except Exception as e:
            logger.error(f"TTS Error: {e}")
            return None
    
    def play_speech(self, audio_file):
        """Play speech with simple animation"""
        if not audio_file or not os.path.exists(audio_file):
            return
            
        try:
            # Start animation
            if self.obs_controller:
                self.obs_controller.start_animation()
            
            # Play audio
            pygame.mixer.music.load(audio_file)
            pygame.mixer.music.play()
            
            self.is_speaking = True
            
            # Monitor playback
            while pygame.mixer.music.get_busy():
                time.sleep(0.1)
            
            self.is_speaking = False
            
            # Stop animation
            if self.obs_controller:
                self.obs_controller.stop_animation()
                
        except Exception as e:
            logger.error(f"Audio playback error: {e}")
        finally:
            # Cleanup
            if os.path.exists(audio_file):
                os.unlink(audio_file)
    
    def is_playing(self):
        """Check if playing"""
        return self.is_speaking
    
    def stop_speech(self):
        """Stop speech"""
        if self.is_speaking:
            pygame.mixer.music.stop()
            self.is_speaking = False
            if self.obs_controller:
                self.obs_controller.stop_animation()
