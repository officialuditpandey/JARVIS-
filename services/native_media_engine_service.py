#!/usr/bin/env python3
"""
Native Media Engine Service for JARVIS
Play songs/videos directly without needing to search YouTube every time
"""

import os
import sys
import time
import threading
import json
import subprocess
import glob
from datetime import datetime
from typing import Dict, Any, List, Optional, Tuple
import pygame

# Add JARVIS backend path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

try:
    import vlc
    VLC_AVAILABLE = True
except ImportError:
    print("VLC not available - Installing...")
    os.system("pip install python-vlc")
    try:
        import vlc
        VLC_AVAILABLE = True
    except ImportError:
        VLC_AVAILABLE = False

try:
    import moviepy.editor as mp
    MOVIEPY_AVAILABLE = True
except ImportError:
    print("MoviePy not available - Installing...")
    os.system("pip install moviepy")
    try:
        import moviepy.editor as mp
        MOVIEPY_AVAILABLE = True
    except ImportError:
        MOVIEPY_AVAILABLE = False

class NativeMediaEngineService:
    """Native Media Engine service for local media playback"""
    
    def __init__(self):
        self.is_active = False
        self.current_media = None
        self.media_library = {}
        self.playback_history = []
        self.playlists = {}
        
        # Media directories
        self.media_directories = [
            "media/music",
            "media/videos",
            "media/podcasts",
            "media/audiobooks",
            "downloads",
            "music",
            "videos"
        ]
        
        # Supported formats
        self.audio_formats = ['.mp3', '.wav', '.flac', '.aac', '.ogg', '.m4a', '.wma']
        self.video_formats = ['.mp4', '.avi', '.mkv', '.mov', '.wmv', '.flv', '.webm']
        
        # Playback state
        self.is_playing = False
        self.is_paused = False
        self.current_position = 0
        self.volume = 0.7
        self.repeat_mode = 'none'  # none, one, all
        
        # VLC instance
        self.vlc_instance = None
        self.vlc_player = None
        
        # Performance metrics
        self.tracks_played = 0
        self.total_playtime = 0
        self.start_time = time.time()
        
        # Initialize
        self._initialize_media_engine()
        
        print("Native Media Engine Service initialized")
    
    def _initialize_media_engine(self):
        """Initialize media engine components"""
        try:
            # Initialize VLC
            if VLC_AVAILABLE:
                self.vlc_instance = vlc.Instance()
                self.vlc_player = self.vlc_instance.media_player_new()
                print("VLC player initialized")
            
            # Initialize pygame for audio fallback
            try:
                pygame.mixer.init()
                print("Pygame mixer initialized")
            except:
                print("Pygame mixer initialization failed")
            
            # Create media directories
            for directory in self.media_directories:
                os.makedirs(directory, exist_ok=True)
            
            # Scan media library
            self._scan_media_library()
            
        except Exception as e:
            print(f"Media engine initialization failed: {e}")
    
    def _scan_media_library(self):
        """Scan media directories and build library"""
        try:
            print("Scanning media library...")
            
            for directory in self.media_directories:
                if not os.path.exists(directory):
                    continue
                
                # Scan for audio files
                for format_ext in self.audio_formats:
                    pattern = os.path.join(directory, f"*{format_ext}")
                    files = glob.glob(pattern)
                    
                    for file_path in files:
                        self._add_media_to_library(file_path, 'audio')
                
                # Scan for video files
                for format_ext in self.video_formats:
                    pattern = os.path.join(directory, f"*{format_ext}")
                    files = glob.glob(pattern)
                    
                    for file_path in files:
                        self._add_media_to_library(file_path, 'video')
            
            print(f"Media library scanned: {len(self.media_library)} files found")
            
        except Exception as e:
            print(f"Media library scan failed: {e}")
    
    def _add_media_to_library(self, file_path: str, media_type: str):
        """Add media file to library"""
        try:
            # Extract metadata
            filename = os.path.basename(file_path)
            name, ext = os.path.splitext(filename)
            
            # Get file size and modification time
            file_size = os.path.getsize(file_path)
            file_time = os.path.getmtime(file_path)
            
            media_info = {
                'file_path': file_path,
                'filename': filename,
                'name': name,
                'type': media_type,
                'format': ext,
                'size': file_size,
                'added_time': file_time,
                'duration': None,  # Will be filled when played
                'play_count': 0,
                'last_played': None
            }
            
            self.media_library[filename] = media_info
            
        except Exception as e:
            print(f"Failed to add media to library: {e}")
    
    def play_media(self, filename: str, start_position: float = 0) -> Dict[str, Any]:
        """Play media file"""
        try:
            if filename not in self.media_library:
                return {
                    'success': False,
                    'error': f'Media file {filename} not found in library'
                }
            
            media_info = self.media_library[filename]
            file_path = media_info['file_path']
            
            if not os.path.exists(file_path):
                return {
                    'success': False,
                    'error': f'Media file {file_path} not found'
                }
            
            # Stop current playback
            if self.is_playing:
                self.stop_media()
            
            # Play using VLC if available
            if VLC_AVAILABLE and self.vlc_player:
                result = self._play_with_vlc(file_path, start_position)
            else:
                # Fallback to system default player
                result = self._play_with_system(file_path)
            
            if result['success']:
                self.current_media = media_info
                self.is_playing = True
                self.is_paused = False
                self.current_position = start_position
                
                # Update play count
                media_info['play_count'] += 1
                media_info['last_played'] = datetime.now().isoformat()
                
                # Add to history
                history_entry = {
                    'filename': filename,
                    'played_at': datetime.now().isoformat(),
                    'start_position': start_position
                }
                self.playback_history.append(history_entry)
                
                # Keep only last 100 entries
                if len(self.playback_history) > 100:
                    self.playback_history = self.playback_history[-100:]
                
                self.tracks_played += 1
            
            return result
            
        except Exception as e:
            return {
                'success': False,
                'error': f'Media playback failed: {str(e)}'
            }
    
    def _play_with_vlc(self, file_path: str, start_position: float) -> Dict[str, Any]:
        """Play media using VLC"""
        try:
            # Create media
            media = self.vlc_instance.media_new(file_path)
            
            # Set media to player
            self.vlc_player.set_media(media)
            
            # Set volume
            self.vlc_player.audio_set_volume(int(self.volume * 100))
            
            # Play
            self.vlc_player.play()
            
            # Wait for media to start
            time.sleep(0.5)
            
            # Set position if specified
            if start_position > 0:
                self.vlc_player.set_position(start_position)
            
            return {
                'success': True,
                'player': 'VLC',
                'file_path': file_path,
                'message': f'Playing {os.path.basename(file_path)}'
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': f'VLC playback failed: {str(e)}'
            }
    
    def _play_with_system(self, file_path: str) -> Dict[str, Any]:
        """Play media using system default player"""
        try:
            # Use subprocess to open with default application
            if sys.platform == 'win32':
                os.startfile(file_path)
            elif sys.platform == 'darwin':
                subprocess.run(['open', file_path])
            else:
                subprocess.run(['xdg-open', file_path])
            
            return {
                'success': True,
                'player': 'system',
                'file_path': file_path,
                'message': f'Opened {os.path.basename(file_path)} with default player'
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': f'System playback failed: {str(e)}'
            }
    
    def pause_media(self) -> Dict[str, Any]:
        """Pause current media playback"""
        try:
            if not self.is_playing:
                return {
                    'success': False,
                    'error': 'No media currently playing'
                }
            
            if VLC_AVAILABLE and self.vlc_player:
                self.vlc_player.pause()
                self.is_paused = True
            else:
                # Cannot pause system player
                return {
                    'success': False,
                    'error': 'Cannot pause system player - use VLC for full control'
                }
            
            return {
                'success': True,
                'message': 'Media paused'
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': f'Pause failed: {str(e)}'
            }
    
    def resume_media(self) -> Dict[str, Any]:
        """Resume paused media"""
        try:
            if not self.is_paused:
                return {
                    'success': False,
                    'error': 'Media is not paused'
                }
            
            if VLC_AVAILABLE and self.vlc_player:
                self.vlc_player.pause()
                self.is_paused = False
            else:
                return {
                    'success': False,
                    'error': 'Cannot resume system player'
                }
            
            return {
                'success': True,
                'message': 'Media resumed'
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': f'Resume failed: {str(e)}'
            }
    
    def stop_media(self) -> Dict[str, Any]:
        """Stop media playback"""
        try:
            if not self.is_playing:
                return {
                    'success': False,
                    'error': 'No media currently playing'
                }
            
            if VLC_AVAILABLE and self.vlc_player:
                self.vlc_player.stop()
            
            self.is_playing = False
            self.is_paused = False
            self.current_media = None
            self.current_position = 0
            
            return {
                'success': True,
                'message': 'Media stopped'
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': f'Stop failed: {str(e)}'
            }
    
    def set_volume(self, volume: float) -> Dict[str, Any]:
        """Set playback volume (0.0 to 1.0)"""
        try:
            volume = max(0.0, min(1.0, volume))
            
            if VLC_AVAILABLE and self.vlc_player:
                self.vlc_player.audio_set_volume(int(volume * 100))
            
            self.volume = volume
            
            return {
                'success': True,
                'volume': volume,
                'message': f'Volume set to {int(volume * 100)}%'
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': f'Volume control failed: {str(e)}'
            }
    
    def seek_to(self, position: float) -> Dict[str, Any]:
        """Seek to specific position (0.0 to 1.0)"""
        try:
            if not self.is_playing or not VLC_AVAILABLE:
                return {
                    'success': False,
                    'error': 'Seeking requires VLC player'
                }
            
            position = max(0.0, min(1.0, position))
            self.vlc_player.set_position(position)
            self.current_position = position
            
            return {
                'success': True,
                'position': position,
                'message': f'Seeked to {int(position * 100)}%'
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': f'Seek failed: {str(e)}'
            }
    
    def get_media_info(self, filename: str) -> Dict[str, Any]:
        """Get detailed information about media file"""
        try:
            if filename not in self.media_library:
                return {
                    'success': False,
                    'error': f'Media file {filename} not found'
                }
            
            media_info = self.media_library[filename].copy()
            
            # Get duration if available
            if media_info['duration'] is None and MOVIEPY_AVAILABLE:
                try:
                    if media_info['type'] == 'video':
                        clip = mp.VideoFileClip(media_info['file_path'])
                        media_info['duration'] = clip.duration
                        clip.close()
                    elif media_info['type'] == 'audio':
                        clip = mp.AudioFileClip(media_info['file_path'])
                        media_info['duration'] = clip.duration
                        clip.close()
                except:
                    pass  # Duration extraction failed
            
            return {
                'success': True,
                'media_info': media_info
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': f'Media info retrieval failed: {str(e)}'
            }
    
    def search_media(self, query: str, media_type: str = None) -> List[Dict[str, Any]]:
        """Search media library"""
        try:
            results = []
            query_lower = query.lower()
            
            for filename, media_info in self.media_library.items():
                # Filter by media type if specified
                if media_type and media_info['type'] != media_type:
                    continue
                
                # Search in filename and name
                if (query_lower in filename.lower() or 
                    query_lower in media_info['name'].lower()):
                    results.append(media_info.copy())
            
            return results
            
        except Exception as e:
            print(f"Media search failed: {e}")
            return []
    
    def create_playlist(self, name: str, filenames: List[str]) -> Dict[str, Any]:
        """Create a playlist"""
        try:
            # Validate files exist in library
            playlist_files = []
            for filename in filenames:
                if filename in self.media_library:
                    playlist_files.append(filename)
                else:
                    print(f"Warning: {filename} not found in library")
            
            if not playlist_files:
                return {
                    'success': False,
                    'error': 'No valid files found for playlist'
                }
            
            # Create playlist
            playlist = {
                'name': name,
                'files': playlist_files,
                'created_at': datetime.now().isoformat(),
                'play_count': 0
            }
            
            self.playlists[name] = playlist
            
            return {
                'success': True,
                'playlist_name': name,
                'files_count': len(playlist_files),
                'message': f'Playlist {name} created with {len(playlist_files)} files'
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': f'Playlist creation failed: {str(e)}'
            }
    
    def play_playlist(self, name: str, shuffle: bool = False) -> Dict[str, Any]:
        """Play a playlist"""
        try:
            if name not in self.playlists:
                return {
                    'success': False,
                    'error': f'Playlist {name} not found'
                }
            
            playlist = self.playlists[name]
            files = playlist['files'].copy()
            
            if shuffle:
                import random
                random.shuffle(files)
            
            # Start playing first file
            if files:
                result = self.play_media(files[0])
                
                if result['success']:
                    # Store remaining files for continuous playback
                    self.current_playlist = {
                        'name': name,
                        'files': files[1:],
                        'current_index': 0,
                        'shuffle': shuffle
                    }
                    
                    return {
                        'success': True,
                        'playlist_name': name,
                        'current_file': files[0],
                        'remaining_files': len(files) - 1,
                        'message': f'Playing playlist {name} - {len(files)} files'
                    }
            
            return result
            
        except Exception as e:
            return {
                'success': False,
                'error': f'Playlist playback failed: {str(e)}'
            }
    
    def get_playback_status(self) -> Dict[str, Any]:
        """Get current playback status"""
        try:
            status = {
                'is_playing': self.is_playing,
                'is_paused': self.is_paused,
                'current_media': None,
                'position': self.current_position,
                'volume': self.volume,
                'repeat_mode': self.repeat_mode
            }
            
            if self.current_media:
                status['current_media'] = {
                    'filename': self.current_media['filename'],
                    'name': self.current_media['name'],
                    'type': self.current_media['type']
                }
                
                # Get current position from VLC if available
                if VLC_AVAILABLE and self.vlc_player and self.is_playing:
                    try:
                        status['position'] = self.vlc_player.get_position()
                        status['length'] = self.vlc_player.get_length() / 1000  # Convert to seconds
                    except:
                        pass
            
            return status
            
        except Exception as e:
            return {
                'error': f'Status retrieval failed: {str(e)}'
            }
    
    def get_library_stats(self) -> Dict[str, Any]:
        """Get media library statistics"""
        try:
            audio_count = sum(1 for info in self.media_library.values() if info['type'] == 'audio')
            video_count = sum(1 for info in self.media_library.values() if info['type'] == 'video')
            total_size = sum(info['size'] for info in self.media_library.values())
            
            return {
                'total_files': len(self.media_library),
                'audio_files': audio_count,
                'video_files': video_count,
                'total_size_bytes': total_size,
                'total_size_mb': total_size / (1024 * 1024),
                'playlists_count': len(self.playlists),
                'tracks_played': self.tracks_played,
                'total_playtime': self.total_playtime
            }
            
        except Exception as e:
            return {
                'error': f'Stats retrieval failed: {str(e)}'
            }
    
    def get_status(self) -> Dict[str, Any]:
        """Get native media engine service status"""
        return {
            'is_active': self.is_active,
            'is_playing': self.is_playing,
            'is_paused': self.is_paused,
            'current_media': self.current_media['filename'] if self.current_media else None,
            'library_size': len(self.media_library),
            'playlists_count': len(self.playlists),
            'vlc_available': VLC_AVAILABLE,
            'moviepy_available': MOVIEPY_AVAILABLE,
            'tracks_played': self.tracks_played,
            'volume': self.volume,
            'last_updated': datetime.now().isoformat()
        }
