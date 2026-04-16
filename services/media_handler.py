#!/usr/bin/env python3
"""
Local Media Handler Service for JARVIS
Native media player with stop command for both video and audio
"""

import os
import sys
import time
import threading
import json
import subprocess
from datetime import datetime
from typing import Dict, Any, List, Optional, Tuple
import pygame
import vlc

# Add JARVIS backend path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

try:
    import pygame
    PYGAME_AVAILABLE = True
except ImportError:
    PYGAME_AVAILABLE = False
    print("Pygame not available - Installing...")
    os.system("pip install pygame")

try:
    import vlc
    VLC_AVAILABLE = True
except ImportError:
    VLC_AVAILABLE = False
    print("VLC not available - Installing...")
    os.system("pip install python-vlc")

class MediaHandler:
    """Local media handler service for native media playback"""
    
    def __init__(self):
        self.is_active = False
        self.current_media = None
        self.media_type = None  # 'video', 'audio', 'image'
        self.is_playing = False
        self.is_paused = False
        self.volume = 0.7
        
        # VLC setup
        self.vlc_instance = None
        self.vlc_player = None
        
        # Pygame setup
        pygame.mixer.init() if PYGAME_AVAILABLE else None
        
        # Media library
        self.media_library = {}
        self.supported_formats = {
            'video': ['.mp4', '.avi', '.mkv', '.mov', '.wmv', '.flv', '.webm'],
            'audio': ['.mp3', '.wav', '.flac', '.aac', '.ogg', '.m4a', '.wma'],
            'image': ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.tiff', '.webp']
        }
        
        # Initialize
        self._initialize_media_handler()
        
        print("Local Media Handler Service initialized")
    
    def _initialize_media_handler(self):
        """Initialize media handler components"""
        try:
            # Initialize VLC
            if VLC_AVAILABLE:
                self.vlc_instance = vlc.Instance()
                self.vlc_player = self.vlc_instance.media_player_new()
            
            # Scan for media files
            self._scan_media_library()
            
            self.is_active = True
            
        except Exception as e:
            print(f"Media handler initialization failed: {e}")
    
    def _scan_media_library(self):
        """Scan common directories for media files"""
        try:
            user_home = os.path.expanduser('~')
            scan_dirs = [
                os.path.join(user_home, 'Videos'),
                os.path.join(user_home, 'Music'),
                os.path.join(user_home, 'Pictures'),
                os.path.join(user_home, 'Downloads'),
                os.path.join(user_home, 'Desktop')
            ]
            
            for scan_dir in scan_dirs:
                if os.path.exists(scan_dir):
                    self._scan_directory(scan_dir)
            
            print(f"Media library scanned: {len(self.media_library)} files found")
            
        except Exception as e:
            print(f"Media library scan failed: {e}")
    
    def _scan_directory(self, directory: str):
        """Scan directory for media files"""
        try:
            for root, dirs, files in os.walk(directory):
                for file in files:
                    file_path = os.path.join(root, file)
                    file_ext = os.path.splitext(file)[1].lower()
                    
                    # Determine media type
                    for media_type, extensions in self.supported_formats.items():
                        if file_ext in extensions:
                            self.media_library[file_path] = {
                                'name': file,
                                'path': file_path,
                                'type': media_type,
                                'size': os.path.getsize(file_path),
                                'modified': os.path.getmtime(file_path)
                            }
                            break
                            
        except Exception as e:
            print(f"Directory scan failed for {directory}: {e}")
    
    def play_media(self, media_path: str = None, media_name: str = None) -> Dict[str, Any]:
        """Play media file"""
        try:
            # Find media file
            if media_name:
                media_path = self._find_media_by_name(media_name)
            elif not media_path:
                return {
                    'success': False,
                    'error': 'No media path or name provided'
                }
            
            if not os.path.exists(media_path):
                return {
                    'success': False,
                    'error': f'Media file not found: {media_path}'
                }
            
            # Determine media type
            media_type = self._determine_media_type(media_path)
            
            # Stop current playback
            if self.is_playing:
                self.stop_media()
            
            # Play based on media type
            if media_type == 'video':
                result = self._play_video(media_path)
            elif media_type == 'audio':
                result = self._play_audio(media_path)
            elif media_type == 'image':
                result = self._show_image(media_path)
            else:
                return {
                    'success': False,
                    'error': f'Unsupported media type: {media_type}'
                }
            
            if result['success']:
                self.current_media = media_path
                self.media_type = media_type
                self.is_playing = True
                self.is_paused = False
            
            return result
            
        except Exception as e:
            return {
                'success': False,
                'error': f'Play media failed: {str(e)}'
            }
    
    def _play_video(self, video_path: str) -> Dict[str, Any]:
        """Play video using VLC"""
        try:
            if not VLC_AVAILABLE:
                # Fallback to system default
                subprocess.Popen([video_path], shell=True)
                return {
                    'success': True,
                    'method': 'system_default',
                    'message': 'Video opened with system default player'
                }
            
            # Create media
            media = self.vlc_instance.media_new(video_path)
            self.vlc_player.set_media(media)
            
            # Set volume
            self.vlc_player.audio_set_volume(int(self.volume * 100))
            
            # Play
            self.vlc_player.play()
            
            return {
                'success': True,
                'method': 'vlc',
                'message': 'Video playing with VLC'
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': f'Video playback failed: {str(e)}'
            }
    
    def _play_audio(self, audio_path: str) -> Dict[str, Any]:
        """Play audio using pygame or VLC"""
        try:
            if PYGAME_AVAILABLE:
                # Use pygame for audio
                pygame.mixer.music.load(audio_path)
                pygame.mixer.music.set_volume(self.volume)
                pygame.mixer.music.play()
                
                return {
                    'success': True,
                    'method': 'pygame',
                    'message': 'Audio playing with pygame'
                }
            elif VLC_AVAILABLE:
                # Use VLC for audio
                media = self.vlc_instance.media_new(audio_path)
                self.vlc_player.set_media(media)
                self.vlc_player.audio_set_volume(int(self.volume * 100))
                self.vlc_player.play()
                
                return {
                    'success': True,
                    'method': 'vlc',
                    'message': 'Audio playing with VLC'
                }
            else:
                # Fallback to system default
                subprocess.Popen([audio_path], shell=True)
                return {
                    'success': True,
                    'method': 'system_default',
                    'message': 'Audio opened with system default player'
                }
                
        except Exception as e:
            return {
                'success': False,
                'error': f'Audio playback failed: {str(e)}'
            }
    
    def _show_image(self, image_path: str) -> Dict[str, Any]:
        """Show image using system default viewer"""
        try:
            if sys.platform == 'win32':
                os.startfile(image_path)
            elif sys.platform == 'darwin':
                subprocess.run(['open', image_path])
            else:
                subprocess.run(['xdg-open', image_path])
            
            return {
                'success': True,
                'method': 'system_default',
                'message': 'Image opened with system viewer'
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': f'Image display failed: {str(e)}'
            }
    
    def stop_media(self) -> Dict[str, Any]:
        """Stop media playback - WORKS FOR BOTH VIDEO AND AUDIO"""
        try:
            if not self.is_playing:
                return {
                    'success': True,
                    'message': 'No media playing'
                }
            
            # Stop based on current method
            if self.media_type == 'video' and VLC_AVAILABLE and self.vlc_player:
                self.vlc_player.stop()
            elif self.media_type == 'audio' and PYGAME_AVAILABLE:
                pygame.mixer.music.stop()
                pygame.mixer.quit()
                pygame.mixer.init()
            elif VLC_AVAILABLE and self.vlc_player:
                self.vlc_player.stop()
            else:
                # Try to stop system processes
                if sys.platform == 'win32':
                    subprocess.run(['taskkill', '/F', '/IM', 'vlc.exe'], capture_output=True)
                    subprocess.run(['taskkill', '/F', '/IM', 'wmplayer.exe'], capture_output=True)
            
            # Reset state
            self.is_playing = False
            self.is_paused = False
            self.current_media = None
            self.media_type = None
            
            return {
                'success': True,
                'message': 'Media stopped successfully'
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': f'Stop media failed: {str(e)}'
            }
    
    def pause_media(self) -> Dict[str, Any]:
        """Pause media playback"""
        try:
            if not self.is_playing or self.is_paused:
                return {
                    'success': False,
                    'error': 'No media playing or already paused'
                }
            
            # Pause based on current method
            if self.media_type == 'video' and VLC_AVAILABLE and self.vlc_player:
                self.vlc_player.pause()
            elif self.media_type == 'audio' and PYGAME_AVAILABLE:
                pygame.mixer.music.pause()
            elif VLC_AVAILABLE and self.vlc_player:
                self.vlc_player.pause()
            
            self.is_paused = True
            
            return {
                'success': True,
                'message': 'Media paused'
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': f'Pause media failed: {str(e)}'
            }
    
    def resume_media(self) -> Dict[str, Any]:
        """Resume media playback"""
        try:
            if not self.is_playing or not self.is_paused:
                return {
                    'success': False,
                    'error': 'No media paused to resume'
                }
            
            # Resume based on current method
            if self.media_type == 'video' and VLC_AVAILABLE and self.vlc_player:
                self.vlc_player.pause()  # VLC toggle pause
            elif self.media_type == 'audio' and PYGAME_AVAILABLE:
                pygame.mixer.music.unpause()
            elif VLC_AVAILABLE and self.vlc_player:
                self.vlc_player.pause()  # VLC toggle pause
            
            self.is_paused = False
            
            return {
                'success': True,
                'message': 'Media resumed'
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': f'Resume media failed: {str(e)}'
            }
    
    def set_volume(self, volume: float) -> Dict[str, Any]:
        """Set volume (0.0 to 1.0)"""
        try:
            volume = max(0.0, min(1.0, volume))
            self.volume = volume
            
            # Apply to current playback
            if VLC_AVAILABLE and self.vlc_player:
                self.vlc_player.audio_set_volume(int(volume * 100))
            
            if PYGAME_AVAILABLE:
                pygame.mixer.music.set_volume(volume)
            
            return {
                'success': True,
                'volume': volume,
                'message': f'Volume set to {int(volume * 100)}%'
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': f'Set volume failed: {str(e)}'
            }
    
    def _find_media_by_name(self, name: str) -> Optional[str]:
        """Find media file by name"""
        name_lower = name.lower()
        
        for path, info in self.media_library.items():
            if name_lower in info['name'].lower():
                return path
        
        return None
    
    def _determine_media_type(self, file_path: str) -> Optional[str]:
        """Determine media type from file extension"""
        file_ext = os.path.splitext(file_path)[1].lower()
        
        for media_type, extensions in self.supported_formats.items():
            if file_ext in extensions:
                return media_type
        
        return None
    
    def search_media(self, query: str) -> List[Dict[str, Any]]:
        """Search media library"""
        try:
            query_lower = query.lower()
            results = []
            
            for path, info in self.media_library.items():
                if query_lower in info['name'].lower():
                    results.append(info)
            
            return results
            
        except Exception as e:
            print(f"Media search failed: {e}")
            return []
    
    def get_media_library(self) -> Dict[str, Any]:
        """Get media library"""
        return {
            'total_files': len(self.media_library),
            'media_types': {
                media_type: len([info for info in self.media_library.values() if info['type'] == media_type])
                for media_type in self.supported_formats.keys()
            },
            'files': list(self.media_library.values())[:20]  # First 20 files
        }
    
    def get_status(self) -> Dict[str, Any]:
        """Get media handler status"""
        return {
            'is_active': self.is_active,
            'is_playing': self.is_playing,
            'is_paused': self.is_paused,
            'current_media': self.current_media,
            'media_type': self.media_type,
            'volume': self.volume,
            'library_size': len(self.media_library),
            'vlc_available': VLC_AVAILABLE,
            'pygame_available': PYGAME_AVAILABLE,
            'supported_formats': self.supported_formats,
            'last_updated': datetime.now().isoformat()
        }

    def get_status(self):
        return {
            'is_active': True,
            'supported_formats': ['mp3', 'wav', 'mp4', 'avi']
        }
