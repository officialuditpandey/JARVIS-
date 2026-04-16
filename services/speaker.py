#!/usr/bin/env python3
"""
JARVIS Speaker Service - High-Fidelity Voice System
Uses Edge-TTS for generation and pygame for reliable playback
"""

import os
import sys
import asyncio
import threading
import queue
from typing import Optional, Dict, List, Any
from datetime import datetime

# Add JARVIS backend path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

try:
    import subprocess
    SUBPROCESS_AVAILABLE = True
except ImportError:
    print("subprocess not available - speaker service may have limited functionality")
    SUBPROCESS_AVAILABLE = False

try:
    import pygame
    PYGAME_AVAILABLE = True
except ImportError:
    print("pygame not available - falling back to basic audio")
    PYGAME_AVAILABLE = False

class SpeakerService:
    """High-fidelity speaker service with Edge-TTS and pygame"""
    
    def __init__(self):
        self.current_tts_process = None
        self.audio_queue = queue.Queue()
        self.is_speaking = False
        self.stop_event = threading.Event()
        
        print("Speaker service initialized with pygame support" if PYGAME_AVAILABLE else "Speaker service initialized (pygame fallback)")
    
    async def speak_async(self, text: str) -> bool:
        """Asynchronous speech synthesis with Edge-TTS"""
        if not text.strip():
            return False
        
        try:
            # Generate speech using Edge-TTS
            import edge_tts
            
            communicate = edge_tts.Communicate(text, "en-US-JennyNeural")
            
            # Generate audio file
            await communicate.save("temp_speech.mp3")
            
            # Play audio using pygame
            if PYGAME_AVAILABLE:
                pygame.mixer.init()
                pygame.mixer.music.load("temp_speech.mp3")
                pygame.mixer.music.play()
                
                # Wait for playback to complete
                while pygame.mixer.music.get_busy():
                    await asyncio.sleep(0.1)
                
                pygame.mixer.quit()
                print("Edge-TTS playback completed with pygame")
                return True
            else:
                print("pygame not available - Edge-TTS generated but not played")
                return True
                
        except Exception as e:
            print(f"Edge-TTS error: {e}")
            return False
    
    def speak(self, text: str) -> bool:
        """Synchronous speech synthesis wrapper"""
        if self.is_speaking:
            print("Already speaking, queuing...")
            self.audio_queue.put(text)
            return True
        
        # Run async speech in background thread
        def run_speech():
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            
            try:
                loop.run_until_complete(self.speak_async(text))
            finally:
                loop.close()
        
        speech_thread = threading.Thread(target=run_speech, daemon=True)
        speech_thread.start()
        
        return True
    
    def stop_speaking(self):
        """Stop current speech"""
        self.stop_event.set()
        
        if self.current_tts_process:
            try:
                self.current_tts_process.terminate()
                self.current_tts_process = None
            except:
                pass
        
        # Clear audio queue
        while not self.audio_queue.empty():
            try:
                self.audio_queue.get_nowait()
            except:
                break
        
        self.is_speaking = False
    
    def get_status(self) -> Dict[str, Any]:
        """Get speaker service status"""
        return {
            'pygame_available': PYGAME_AVAILABLE,
            'subprocess_available': SUBPROCESS_AVAILABLE,
            'is_speaking': self.is_speaking,
            'queue_size': self.audio_queue.qsize()
        }
    
    def cleanup(self):
        """Cleanup temporary files and resources"""
        try:
            if os.path.exists("temp_speech.mp3"):
                os.remove("temp_speech.mp3")
                print("Cleaned up temporary speech file")
        except Exception as e:
            print(f"Cleanup error: {e}")
