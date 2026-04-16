"""
Local Voice Service for Cloud Cowork HUD
Uses Faster-Whisper for listening and Edge-TTS for speaking (all local)
"""

import os
import sys
import asyncio
import threading
import queue
import subprocess
from typing import Optional, Dict, List
from datetime import datetime

# Add JARVIS backend path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

try:
    import speech_recognition as sr
    SPEECH_RECOGNITION_AVAILABLE = True
except ImportError as e:
    print(f"Speech recognition not available: {e}")
    SPEECH_RECOGNITION_AVAILABLE = False

try:
    import pyttsx3
    TTS_AVAILABLE = True
except ImportError as e:
    print(f"TTS not available: {e}")
    TTS_AVAILABLE = False

try:
    import pyaudio
    PYAUDIO_AVAILABLE = True
except ImportError as e:
    print(f"PyAudio not available: {e}")
    PYAUDIO_AVAILABLE = False

class LocalVoice:
    """Local voice service using speech recognition and PowerShell TTS"""
    
    def __init__(self):
        self.recognizer = None
        self.microphone = None
        self.current_tts_process = None
        self.stop_event = threading.Event()
        self.is_listening = False
        self.is_speaking = False
        self.speech_queue = queue.Queue()
        self.tts_thread = None
        
        self._init_speech_recognition()
        self._start_tts_worker()
        print("Local voice initialized with PowerShell TTS")
    
    def _start_tts_worker(self):
        """Start TTS worker thread"""
        if self.tts_thread is None or not self.tts_thread.is_alive():
            self.tts_thread = threading.Thread(target=self._tts_worker, daemon=True)
            self.tts_thread.start()
    
    def _init_speech_recognition(self):
        """Initialize speech recognition"""
        try:
            self.recognizer = sr.Recognizer()
            self.microphone = sr.Microphone()
            
            # Adjust recognizer settings
            with self.microphone as source:
                self.recognizer.adjust_for_ambient_noise(source, duration=1)
            
            print("Speech recognition initialized successfully")
        except Exception as e:
            print(f"Speech recognition initialization failed: {e}")
    
    def is_available(self) -> bool:
        """Check if voice service is available"""
        return self.recognizer is not None and self.microphone is not None
    
    def speak(self, text: str, blocking: bool = False) -> bool:
        """Speak text using PowerShell TTS (same as jarvis_final.py)"""
        self.stop_event.clear()
        print(f"Speaking: {text}")
        
        try:
            # Prefer Windows PowerShell TTS for reliability (same as jarvis_final.py)
            print("Using PowerShell TTS")
            safe_text = text.replace('"', '`"')
            ps_command = (
                'Add-Type -AssemblyName System.Speech; '
                '$speak = New-Object System.Speech.Synthesis.SpeechSynthesizer; '
                f'$speak.Speak("{safe_text}")'
            )
            self.current_tts_process = subprocess.Popen(
                ["powershell", "-NoProfile", "-Command", ps_command],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
            )
            stdout, stderr = self.current_tts_process.communicate()
            if self.current_tts_process.returncode == 0:
                print("PowerShell TTS completed")
                self.current_tts_process = None
                return True
            print(f"PowerShell TTS returned {self.current_tts_process.returncode}")
            print(stderr)
        except Exception as e:
            print(f"PowerShell TTS error: {e}")
            self.current_tts_process = None

        print("No TTS method succeeded")
        return False
    
    def stop_speaking(self):
        """Stop current TTS"""
        self.stop_event.set()
        try:
            if self.current_tts_process and self.current_tts_process.poll() is None:
                self.current_tts_process.kill()
                print("Stopped PowerShell TTS process")
        except Exception as e:
            print(f"Could not stop TTS process: {e}")
    
    def start_listening(self, timeout: int = 5) -> Optional[str]:
        """Start listening for voice commands"""
        if not self.recognizer or not self.microphone:
            return None
        
        try:
            self.is_listening = True
            print("Listening...")
            
            with self.microphone as source:
                # Listen for audio
                audio = self.recognizer.listen(source, timeout=timeout, phrase_time_limit=10)
            
            # Recognize speech
            text = self.recognizer.recognize_google(audio)
            print(f"Recognized: {text}")
            
            self.is_listening = False
            return text
            
        except sr.UnknownValueError:
            print("Could not understand audio")
            self.is_listening = False
            return None
            
        except sr.RequestError as e:
            print(f"Speech recognition error: {e}")
            self.is_listening = False
            return None
                    
        except sr.WaitTimeoutError:
            return "Listening timeout"
        except Exception as e:
            print(f"Listening error: {e}")
            return f"Listening error: {e}"
        finally:
            self.is_listening = False
    
    def speak(self, text: str, blocking: bool = False) -> bool:
        """Speak text using local TTS"""
        if not self.is_available():
            return False
        
        if not text.strip():
            return False
        
        if blocking:
            return self._speak_immediate(text)
        else:
            self.speech_queue.put(text)
            return True
    
    def _speak_immediate(self, text: str) -> bool:
        """Speak text immediately (blocking) using PowerShell TTS"""
        try:
            self.is_speaking = True
            print(f"Speaking: {text}")
            
            # Use PowerShell TTS directly
            safe_text = text.replace('"', '`"')
            ps_command = (
                'Add-Type -AssemblyName System.Speech; '
                '$speak = New-Object System.Speech.Synthesis.SpeechSynthesizer; '
                f'$speak.Speak("{safe_text}")'
            )
            result = subprocess.run(
                ["powershell", "-NoProfile", "-Command", ps_command],
                capture_output=True,
                text=True,
            )
            
            return result.returncode == 0
        except Exception as e:
            print(f"TTS error: {e}")
            return False
        finally:
            self.is_speaking = False
    
    def _tts_worker(self):
        """TTS worker thread"""
        while True:
            try:
                text = self.speech_queue.get(timeout=1)
                if text:
                    self._speak_immediate(text)
                self.speech_queue.task_done()
            except queue.Empty:
                continue
            except Exception as e:
                print(f"TTS worker error: {e}")
    
    def stop_speaking(self):
        """Stop current speech"""
        if self.tts_engine:
            try:
                self.tts_engine.stop()
            except:
                pass
        
        # Clear queue
        while not self.speech_queue.empty():
            try:
                self.speech_queue.get_nowait()
                self.speech_queue.task_done()
            except queue.Empty:
                break
    
    def get_microphones(self) -> List[str]:
        """Get list of available microphones"""
        return self.microphone_list
    
    def set_voice_properties(self, rate: int = None, volume: float = None, voice_id: str = None):
        """Set TTS voice properties"""
        if not self.tts_engine:
            return False
        
        try:
            if rate is not None:
                self.tts_engine.setProperty('rate', rate)
            if volume is not None:
                self.tts_engine.setProperty('volume', max(0.0, min(1.0, volume)))
            if voice_id is not None:
                self.tts_engine.setProperty('voice', voice_id)
            return True
        except Exception as e:
            print(f"Error setting voice properties: {e}")
            return False
    
    def get_available_voices(self) -> List[Dict]:
        """Get available TTS voices"""
        if not self.tts_engine:
            return []
        
        try:
            voices = self.tts_engine.getProperty('voices')
            return [
                {
                    'id': voice.id,
                    'name': voice.name,
                    'languages': voice.languages,
                    'gender': voice.gender
                }
                for voice in voices
            ]
        except:
            return []
    
    def test_microphone(self) -> bool:
        """Test microphone functionality"""
        if not self.is_available():
            return False
        
        try:
            with self.microphone as source:
                self.recognizer.adjust_for_ambient_noise(source, duration=0.5)
                audio = self.recognizer.listen(source, timeout=1, phrase_time_limit=2)
            
            # Try to detect if we got audio
            if audio.get_sample_rate() > 0:
                return True
            return False
        except:
            return False
    
    def calibrate_microphone(self, duration: int = 3) -> bool:
        """Calibrate microphone for ambient noise"""
        if not self.is_available():
            return False
        
        try:
            with self.microphone as source:
                print(f"Calibrating microphone for {duration} seconds...")
                self.recognizer.adjust_for_ambient_noise(source, duration=duration)
            print("Microphone calibrated")
            return True
        except Exception as e:
            print(f"Calibration failed: {e}")
            return False
