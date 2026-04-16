"""
Local Automation Service for JARVIS Desktop GUI
Handles system automation like playing music, opening YouTube, etc.
"""

import os
import sys
import subprocess
import webbrowser
import time
from typing import Dict, List, Optional
from datetime import datetime
import asyncio  # Add asyncio import

# Add JARVIS backend path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

try:
    from .fuzzy_matcher import SmartCommandProcessor
    FUZZY_AVAILABLE = True
except ImportError as e:
    print(f"Fuzzy matcher not available: {e}")
    FUZZY_AVAILABLE = False

try:
    import pywhatkit
    WHATKIT_AVAILABLE = True
except ImportError as e:
    print(f"WhatKit not available: {e}")
    WHATKIT_AVAILABLE = False

try:
    import keyboard
    KEYBOARD_AVAILABLE = True
except ImportError as e:
    print(f"Keyboard not available: {e}")
    KEYBOARD_AVAILABLE = False

try:
    import pyautogui
    AUTOMATION_AVAILABLE = True
except ImportError as e:
    print(f"PyAutoGUI not available: {e}")
    AUTOMATION_AVAILABLE = False

class LocalAutomation:
    """Local automation service for system control"""
    
    def __init__(self):
        self.current_music = None
        self.browser_tabs = []
        self.automation_history = []
        
        # Initialize fuzzy matching
        if FUZZY_AVAILABLE:
            self.fuzzy_processor = SmartCommandProcessor(threshold=80.0)
        else:
            self.fuzzy_processor = None
        
        # Log initialization
        self._log_automation("SYSTEM", "Automation service initialized", "system")
        print(f"Automation service initialized - WhatKit: {WHATKIT_AVAILABLE}, Keyboard: {KEYBOARD_AVAILABLE}, PyAutoGUI: {AUTOMATION_AVAILABLE}")
    
    def is_available(self) -> bool:
        """Check if automation service is available"""
        return AUTOMATION_AVAILABLE or WHATKIT_AVAILABLE or KEYBOARD_AVAILABLE
    
    def get_status(self) -> Dict:
        """Get automation service status"""
        return {
            "whatkit_available": WHATKIT_AVAILABLE,
            "keyboard_available": KEYBOARD_AVAILABLE,
            "autogui_available": AUTOMATION_AVAILABLE,
            "current_music": self.current_music,
            "automation_count": len(self.automation_history)
        }
    
    def execute_command(self, command: str) -> str:
        """Execute automation command with fuzzy matching"""
        command_lower = command.lower().strip()
        
        try:
            # Apply fuzzy matching if available
            if self.fuzzy_processor:
                try:
                    # Process command with fuzzy matching (synchronous version)
                    normalized_command = self.fuzzy_processor.process_command(command)
                    
                    command_info = self.fuzzy_processor.get_command_info(command)
                    
                    print(f"Fuzzy matching: '{command}' -> '{normalized_command}' (confidence: {command_info['confidence']:.1f}%)")
                    
                    # Use normalized command for processing
                    command_lower = normalized_command.lower().strip()
                    
                except Exception as e:
                    print(f"Fuzzy matching failed: {e}")
                    # Fall back to original command
            
            # Memory commands
            if "remember" in command_lower and "that" in command_lower:
                fact = command_lower.replace("remember that", "").strip()
                return f"Remembered: {fact}"
            elif "what do you remember" in command_lower or "recall" in command_lower:
                return "Recalling stored memories..."
            elif "memory" in command_lower:
                return "Memory system activated"
            
            # Camera commands
            elif "camera" in command_lower:
                if "open" in command_lower or "start" in command_lower:
                    return self._handle_camera_command()
                elif "identify" in command_lower or "what" in command_lower or "look at" in command_lower:
                    return "Camera identification requires vision service integration"
                else:
                    return "Please say 'open camera' or 'identify objects in camera'"
            
            # Music commands
            elif self._is_music_command(command_lower):
                return self._handle_music_command(command)
            
            # YouTube commands
            elif self._is_youtube_command(command_lower):
                return self._handle_youtube_command(command)
            
            # Web browser commands
            elif self._is_browser_command(command_lower):
                return self._handle_browser_command(command)
            
            # System commands
            elif self._is_system_command(command_lower):
                return self._handle_system_command(command)
            
            # Application commands
            elif self._is_app_command(command_lower):
                return self._handle_app_command(command)
            
            # YouTube commands
            elif self._is_youtube_command(command_lower):
                return self._handle_youtube_command(command)
            
            else:
                return f"Command not recognized: {command}"
                
        except Exception as e:
            error_msg = f"Automation error: {e}"
            self._log_automation(command, error_msg, "error")
            return error_msg
    
    def _is_music_command(self, command: str) -> bool:
        """Check if command is music-related"""
        music_keywords = [
            "play", "music", "song", "track", "audio", "spotify", "itunes",
            "pause", "stop", "next", "previous", "volume"
        ]
        return any(keyword in command.lower() for keyword in music_keywords)
    
    def _is_youtube_command(self, command: str) -> bool:
        """Check if command is YouTube-related"""
        youtube_keywords = [
            "youtube", "video", "watch", "play video", "open youtube"
        ]
        return any(keyword in command.lower() for keyword in youtube_keywords)
    
    def _is_app_command(self, command: str) -> bool:
        """Check if command is application-related"""
        app_keywords = [
            "notepad", "calculator", "explorer", "task manager", "cmd", "terminal",
            "vs code", "word", "excel", "powerpoint", "photoshop"
        ]
        return any(keyword in command for keyword in app_keywords)
    
    def _is_browser_command(self, command: str) -> bool:
        """Check if command is browser-related"""
        browser_keywords = [
            "browser", "chrome", "firefox", "edge", "open browser", "web",
            "google", "bing", "search"
        ]
        return any(keyword in command.lower() for keyword in browser_keywords)
    
    def _is_system_command(self, command: str) -> bool:
        """Check if command is system-related"""
        system_keywords = [
            "volume", "brightness", "shutdown", "restart", "lock", "screenshot",
            "desktop", "minimize", "maximize", "close window"
        ]
        return any(keyword in command for keyword in system_keywords)
    
    def _handle_music_command(self, command: str) -> str:
        """Handle music-related commands"""
        if WHATKIT_AVAILABLE:
            try:
                # Extract song name from command
                song_name = self._extract_song_name(command)
                
                if "play" in command.lower() and song_name:
                    # Play specific song
                    pywhatkit.playonyt(song_name, 0, 30)
                    self.current_music = song_name
                    msg = f"Playing: {song_name}"
                elif "pause" in command.lower():
                    # Pause music (simulate with spacebar)
                    keyboard.press('space')
                    msg = "Music paused"
                elif "stop" in command.lower():
                    # Stop music (simulate with spacebar twice)
                    keyboard.press('space')
                    time.sleep(0.1)
                    keyboard.press('space')
                    self.current_music = None
                    msg = "Music stopped"
                elif "next" in command.lower():
                    # Next track
                    keyboard.press('nexttrack')
                    msg = "Next track"
                elif "previous" in command.lower() or "prev" in command.lower():
                    # Previous track
                    keyboard.press('prevtrack')
                    msg = "Previous track"
                else:
                    msg = "Music command recognized but action unclear"
                
                self._log_automation(command, msg, "music")
                return msg
                
            except Exception as e:
                return f"Music automation failed: {e}"
        else:
            return "Music automation not available - WhatKit not installed"
    
    def _handle_youtube_command(self, command: str) -> str:
        """Handle YouTube-related commands"""
        try:
            # Extract video/song name
            video_name = self._extract_video_name(command)
            
            if video_name:
                # Open YouTube with video
                url = f"https://www.youtube.com/results?search_query={video_name.replace(' ', '+')}"
                webbrowser.open(url)
                msg = f"Opened YouTube: {video_name}"
                self.browser_tabs.append(url)
            else:
                # Just open YouTube
                webbrowser.open("https://www.youtube.com")
                msg = "Opened YouTube"
                self.browser_tabs.append("https://www.youtube.com")
            
            self._log_automation(command, msg, "youtube")
            return msg
            
        except Exception as e:
            return f"YouTube automation failed: {e}"
    
    def _handle_browser_command(self, command: str) -> str:
        """Handle browser-related commands"""
        try:
            # Use system default browser for all cases
            if "chrome" in command.lower():
                webbrowser.open("https://www.google.com")
                msg = "Opened browser with Google"
            elif "firefox" in command.lower():
                webbrowser.open("https://www.google.com")
                msg = "Opened browser with Google"
            elif "edge" in command.lower():
                webbrowser.open("https://www.google.com")
                msg = "Opened browser with Google"
            else:
                webbrowser.open("https://www.google.com")
                msg = "Opened default browser"
            
            self._log_automation(command, msg, "browser")
            return msg
            
        except Exception as e:
            return f"Browser automation failed: {e}"
    
    def _handle_system_command(self, command: str) -> str:
        """Handle system-related commands"""
        try:
            if "volume" in command.lower():
                if "up" in command.lower():
                    keyboard.press('volumeup')
                    msg = "Volume increased"
                elif "down" in command.lower():
                    keyboard.press('volumedown')
                    msg = "Volume decreased"
                elif "mute" in command.lower():
                    keyboard.press('volumemute')
                    msg = "Volume muted"
                else:
                    msg = "Volume command recognized"
            
            elif "brightness" in command.lower():
                if "up" in command.lower():
                    keyboard.press('brightnessup')
                    msg = "Brightness increased"
                elif "down" in command.lower():
                    keyboard.press('brightnessdown')
                    msg = "Brightness decreased"
                else:
                    msg = "Brightness command recognized"
            
            elif "screenshot" in command.lower():
                if AUTOMATION_AVAILABLE:
                    screenshot = pyautogui.screenshot()
                    filename = f"screenshot_{int(time.time())}.png"
                    screenshot.save(filename)
                    msg = f"Screenshot saved: {filename}"
                else:
                    msg = "Screenshot not available"
            
            elif "shutdown" in command.lower():
                os.system("shutdown /s /t 10")
                msg = "System shutting down in 10 seconds"
            
            elif "restart" in command.lower():
                os.system("shutdown /r /t 10")
                msg = "System restarting in 10 seconds"
            
            elif "weather" in command.lower():
                msg = self._get_weather()
            
            elif "search" in command.lower() or "web" in command.lower():
                search_term = command.replace("search", "").replace("web", "").replace("for", "").strip()
                if search_term:
                    url = f"https://www.google.com/search?q={search_term.replace(' ', '+')}"
                    webbrowser.open(url)
                    msg = f"Searching for: {search_term}"
                else:
                    msg = "Please specify what to search for"
            
            else:
                msg = "System command recognized"
            
            self._log_automation(command, msg, "system")
            return msg
            
        except Exception as e:
            return f"System automation failed: {e}"
    
    def _get_weather(self) -> str:
        """Get weather information"""
        try:
            import requests
            response = requests.get("https://wttr.in/auto:ip?format=3", timeout=5)
            if response.status_code == 200:
                return f"Weather: {response.text.strip()}"
            else:
                return "Weather service unavailable"
        except Exception as e:
            return f"Weather error: {e}"
    
    def _handle_app_command(self, command: str) -> str:
        """Handle application-related commands with Windows URI schemes"""
        try:
            # Windows system apps with proper URI schemes
            system_apps = {
                "notepad": "notepad:",
                "calculator": "calculator:",
                "camera": "microsoft.windows.camera:",
                "settings": "ms-settings:",
                "explorer": "explorer:",
                "task manager": "taskmgr:",
                "cmd": "cmd:",
                "terminal": "wt:",
                "control panel": "control:",
                "chrome": "chrome:",
                "firefox": "firefox:",
                "edge": "msedge:",
                "whatsapp": "whatsapp:"
            }
            
            command_lower = command.lower()
            
            # Check for system apps first
            for app_name, uri_scheme in system_apps.items():
                if app_name in command_lower:
                    try:
                        webbrowser.open(uri_scheme)
                        msg = f"Opened {app_name.title()} via system URI"
                        self._log_automation(command, msg, "system_app")
                        return msg
                    except Exception as e:
                        msg = f"Failed to open {app_name}: {e}"
            
            # Fallback to traditional file launching for non-system apps
            if "notepad" in command_lower:
                os.startfile("notepad.exe")
                msg = "Opened Notepad"
            elif "calculator" in command_lower:
                os.startfile("calculator.exe")
                msg = "Opened Calculator"
            else:
                # Handle music commands with patterns
                patterns = [
                    "play ",
                    "song ",
                    "track ",
                    "play: song ",
                    "play: music "
                ]
                
                for pattern in patterns:
                    if pattern in command.lower():
                        song_part = command.lower().split(pattern, 1)[-1].strip()
                        if song_part and len(song_part) > 2:
                            return song_part
            
            self._log_automation(command, msg, "app")
            return msg
            
        except Exception as e:
            return f"App automation failed: {e}"
    
    def _extract_song_name(self, command: str) -> Optional[str]:
        """Extract song name from command"""
        # Simple extraction for music
        patterns = [
            "music ",
            "song ",
            "track ",
            "play the song ",
            "play the music "
        ]
        
        for pattern in patterns:
            if pattern in command.lower():
                song_part = command.lower().split(pattern, 1)[-1].strip()
                if song_part and len(song_part) > 2:
                    return song_part
        
        return None
    
    def _extract_video_name(self, command: str) -> Optional[str]:
        """Extract video name from command"""
        # Simple extraction for YouTube
        patterns = [
            "play ",
            "watch ",
            "video ",
            "open youtube ",
            "youtube ",
            "search youtube "
        ]
        
        for pattern in patterns:
            if pattern in command.lower():
                video_part = command.lower().split(pattern, 1)[-1].strip()
                if video_part and len(video_part) > 2:
                    return video_part
        
        return None
    
    def _log_automation(self, command: str, result: str, category: str):
        """Log automation action"""
        log_entry = {
            "command": command,
            "result": result,
            "category": category,
            "timestamp": datetime.now().isoformat()
        }
        self.automation_history.append(log_entry)
        
        # Keep only last 100 entries
        if len(self.automation_history) > 100:
            self.automation_history = self.automation_history[-100:]
    
    def get_automation_history(self, limit: int = 20) -> List[Dict]:
        """Get recent automation history"""
        return self.automation_history[-limit:]
    
    def clear_history(self):
        """Clear automation history"""
        self.automation_history = []
