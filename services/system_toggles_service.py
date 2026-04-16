#!/usr/bin/env python3
"""
System Toggles Service for JARVIS
Voice commands for WiFi, Volume, and real-time speedtest-cli integration
"""

import os
import sys
import time
import threading
import json
import subprocess
from datetime import datetime
from typing import Dict, Any, List, Optional, Tuple
import psutil

# Add JARVIS backend path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

try:
    import pyautogui
    PYAUTOGUI_AVAILABLE = True
except ImportError:
    PYAUTOGUI_AVAILABLE = False
    print("PyAutoGui not available - Installing...")
    os.system("pip install pyautogui")

try:
    import speedtest
    SPEEDTEST_AVAILABLE = True
except ImportError:
    SPEEDTEST_AVAILABLE = False
    print("Speedtest-cli not available - Installing...")
    os.system("pip install speedtest-cli")

class SystemTogglesService:
    """System toggles service for system control and monitoring"""
    
    def __init__(self):
        self.is_active = False
        self.speedtest_running = False
        self.speedtest_thread = None
        self.speedtest_results = {}
        
        # Network interfaces
        self.network_interfaces = {}
        self.wifi_adapter = None
        
        # Volume control
        self.current_volume = 0.5
        self.volume_step = 0.1
        
        # Initialize
        self._initialize_system_toggles()
        
        print("System Toggles Service initialized")
    
    def _initialize_system_toggles(self):
        """Initialize system toggles"""
        try:
            # Detect network interfaces
            self._detect_network_interfaces()
            
            # Get current volume
            self._get_current_volume()
            
            self.is_active = True
            
        except Exception as e:
            print(f"System toggles initialization failed: {e}")
    
    def _detect_network_interfaces(self):
        """Detect network interfaces and WiFi adapter"""
        try:
            interfaces = psutil.net_if_addrs()
            stats = psutil.net_if_stats()
            
            for interface_name, addresses in interfaces.items():
                if interface_name in stats:
                    interface_info = {
                        'name': interface_name,
                        'is_up': stats[interface_name].isup,
                        'speed': stats[interface_name].speed,
                        'addresses': [addr.address for addr in addresses]
                    }
                    
                    self.network_interfaces[interface_name] = interface_info
                    
                    # Detect WiFi adapter (common naming patterns)
                    if any(keyword in interface_name.lower() for keyword in ['wi-fi', 'wifi', 'wireless', 'wlan']):
                        self.wifi_adapter = interface_name
            
            print(f"Detected {len(self.network_interfaces)} network interfaces")
            if self.wifi_adapter:
                print(f"WiFi adapter detected: {self.wifi_adapter}")
            
        except Exception as e:
            print(f"Network interface detection failed: {e}")
    
    def _get_current_volume(self):
        """Get current system volume"""
        try:
            if sys.platform == 'win32':
                # Windows volume control
                from ctypes import cast, POINTER
                from comtypes import CLSCTX_ALL
                from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume
                
                devices = AudioUtilities.GetSpeakers()
                interface = devices.Activate(IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
                volume = cast(interface, POINTER(IAudioEndpointVolume))
                
                # Get current volume
                current_volume = volume.GetMasterVolumeLevelScalar()
                self.current_volume = current_volume
                
        except Exception as e:
            print(f"Volume detection failed: {e}")
            # Fallback to default
            self.current_volume = 0.5
    
    def toggle_wifi(self, action: str = 'toggle') -> Dict[str, Any]:
        """Toggle WiFi connection"""
        try:
            if not self.wifi_adapter:
                return {
                    'success': False,
                    'error': 'No WiFi adapter detected'
                }
            
            if sys.platform == 'win32':
                # Windows WiFi control
                if action == 'toggle':
                    # Check current status
                    is_up = self.network_interfaces[self.wifi_adapter]['is_up']
                    if is_up:
                        return self._disable_wifi_windows()
                    else:
                        return self._enable_wifi_windows()
                elif action == 'enable':
                    return self._enable_wifi_windows()
                elif action == 'disable':
                    return self._disable_wifi_windows()
                else:
                    return {
                        'success': False,
                        'error': f'Unknown action: {action}'
                    }
            
            else:
                # Linux/Mac WiFi control
                return self._toggle_wifi_unix(action)
                
        except Exception as e:
            return {
                'success': False,
                'error': f'WiFi toggle failed: {str(e)}'
            }
    
    def _enable_wifi_windows(self) -> Dict[str, Any]:
        """Enable WiFi on Windows"""
        try:
            # Use netsh to enable WiFi
            result = subprocess.run(
                ['netsh', 'interface', 'set', 'interface', self.wifi_adapter, 'enabled'],
                capture_output=True,
                text=True,
                timeout=10
            )
            
            if result.returncode == 0:
                # Update interface status
                self._detect_network_interfaces()
                return {
                    'success': True,
                    'action': 'enable',
                    'adapter': self.wifi_adapter,
                    'message': f'WiFi enabled: {self.wifi_adapter}'
                }
            else:
                return {
                    'success': False,
                    'error': f'Failed to enable WiFi: {result.stderr}'
                }
                
        except Exception as e:
            return {
                'success': False,
                'error': f'Enable WiFi failed: {str(e)}'
            }
    
    def _disable_wifi_windows(self) -> Dict[str, Any]:
        """Disable WiFi on Windows"""
        try:
            # Use netsh to disable WiFi
            result = subprocess.run(
                ['netsh', 'interface', 'set', 'interface', self.wifi_adapter, 'disabled'],
                capture_output=True,
                text=True,
                timeout=10
            )
            
            if result.returncode == 0:
                # Update interface status
                self._detect_network_interfaces()
                return {
                    'success': True,
                    'action': 'disable',
                    'adapter': self.wifi_adapter,
                    'message': f'WiFi disabled: {self.wifi_adapter}'
                }
            else:
                return {
                    'success': False,
                    'error': f'Failed to disable WiFi: {result.stderr}'
                }
                
        except Exception as e:
            return {
                'success': False,
                'error': f'Disable WiFi failed: {str(e)}'
            }
    
    def _toggle_wifi_unix(self, action: str) -> Dict[str, Any]:
        """Toggle WiFi on Unix systems"""
        try:
            if action == 'toggle':
                # Check current status
                is_up = self.network_interfaces[self.wifi_adapter]['is_up']
                if is_up:
                    cmd = ['sudo', 'ifconfig', self.wifi_adapter, 'down']
                else:
                    cmd = ['sudo', 'ifconfig', self.wifi_adapter, 'up']
            elif action == 'enable':
                cmd = ['sudo', 'ifconfig', self.wifi_adapter, 'up']
            elif action == 'disable':
                cmd = ['sudo', 'ifconfig', self.wifi_adapter, 'down']
            else:
                return {
                    'success': False,
                    'error': f'Unknown action: {action}'
                }
            
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
            
            if result.returncode == 0:
                # Update interface status
                self._detect_network_interfaces()
                return {
                    'success': True,
                    'action': action,
                    'adapter': self.wifi_adapter,
                    'message': f'WiFi {action}d: {self.wifi_adapter}'
                }
            else:
                return {
                    'success': False,
                    'error': f'Failed to {action} WiFi: {result.stderr}'
                }
                
        except Exception as e:
            return {
                'success': False,
                'error': f'WiFi toggle failed: {str(e)}'
            }
    
    def set_volume(self, volume: float) -> Dict[str, Any]:
        """Set system volume (0.0 to 1.0)"""
        try:
            volume = max(0.0, min(1.0, volume))
            
            if sys.platform == 'win32':
                # Windows volume control
                from ctypes import cast, POINTER
                from comtypes import CLSCTX_ALL
                from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume
                
                devices = AudioUtilities.GetSpeakers()
                interface = devices.Activate(IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
                volume_control = cast(interface, POINTER(IAudioEndpointVolume))
                
                # Set volume
                volume_control.SetMasterVolumeLevelScalar(volume, None)
                self.current_volume = volume
                
                return {
                    'success': True,
                    'volume': volume,
                    'percentage': int(volume * 100),
                    'message': f'Volume set to {int(volume * 100)}%'
                }
            
            else:
                # Unix volume control (using amixer)
                percentage = int(volume * 100)
                result = subprocess.run(
                    ['amixer', 'sset', 'Master', f'{percentage}%'],
                    capture_output=True,
                    text=True,
                    timeout=5
                )
                
                if result.returncode == 0:
                    self.current_volume = volume
                    return {
                        'success': True,
                        'volume': volume,
                        'percentage': percentage,
                        'message': f'Volume set to {percentage}%'
                    }
                else:
                    return {
                        'success': False,
                        'error': f'Failed to set volume: {result.stderr}'
                    }
                    
        except Exception as e:
            return {
                'success': False,
                'error': f'Volume control failed: {str(e)}'
            }
    
    def increase_volume(self, steps: int = 1) -> Dict[str, Any]:
        """Increase volume by steps"""
        new_volume = min(1.0, self.current_volume + (steps * self.volume_step))
        return self.set_volume(new_volume)
    
    def decrease_volume(self, steps: int = 1) -> Dict[str, Any]:
        """Decrease volume by steps"""
        new_volume = max(0.0, self.current_volume - (steps * self.volume_step))
        return self.set_volume(new_volume)
    
    def mute_volume(self) -> Dict[str, Any]:
        """Mute system volume"""
        try:
            if sys.platform == 'win32':
                # Windows mute
                from ctypes import cast, POINTER
                from comtypes import CLSCTX_ALL
                from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume
                
                devices = AudioUtilities.GetSpeakers()
                interface = devices.Activate(IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
                volume_control = cast(interface, POINTER(IAudioEndpointVolume))
                
                # Mute
                volume_control.SetMute(1, None)
                
                return {
                    'success': True,
                    'action': 'mute',
                    'message': 'Volume muted'
                }
            
            else:
                # Unix mute
                result = subprocess.run(
                    ['amixer', 'sset', 'Master', 'mute'],
                    capture_output=True,
                    text=True,
                    timeout=5
                )
                
                if result.returncode == 0:
                    return {
                        'success': True,
                        'action': 'mute',
                        'message': 'Volume muted'
                    }
                else:
                    return {
                        'success': False,
                        'error': f'Failed to mute: {result.stderr}'
                    }
                    
        except Exception as e:
            return {
                'success': False,
                'error': f'Mute failed: {str(e)}'
            }
    
    def unmute_volume(self) -> Dict[str, Any]:
        """Unmute system volume"""
        try:
            if sys.platform == 'win32':
                # Windows unmute
                from ctypes import cast, POINTER
                from comtypes import CLSCTX_ALL
                from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume
                
                devices = AudioUtilities.GetSpeakers()
                interface = devices.Activate(IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
                volume_control = cast(interface, POINTER(IAudioEndpointVolume))
                
                # Unmute
                volume_control.SetMute(0, None)
                
                return {
                    'success': True,
                    'action': 'unmute',
                    'message': 'Volume unmuted'
                }
            
            else:
                # Unix unmute
                result = subprocess.run(
                    ['amixer', 'sset', 'Master', 'unmute'],
                    capture_output=True,
                    text=True,
                    timeout=5
                )
                
                if result.returncode == 0:
                    return {
                        'success': True,
                        'action': 'unmute',
                        'message': 'Volume unmuted'
                    }
                else:
                    return {
                        'success': False,
                        'error': f'Failed to unmute: {result.stderr}'
                    }
                    
        except Exception as e:
            return {
                'success': False,
                'error': f'Unmute failed: {str(e)}'
            }
    
    def run_speedtest(self) -> Dict[str, Any]:
        """Run speedtest-cli in background thread"""
        try:
            if not SPEEDTEST_AVAILABLE:
                return {
                    'success': False,
                    'error': 'Speedtest-cli not available'
                }
            
            if self.speedtest_running:
                return {
                    'success': False,
                    'error': 'Speedtest already running'
                }
            
            # Start speedtest in background thread
            self.speedtest_thread = threading.Thread(
                target=self._run_speedtest_background,
                daemon=True
            )
            self.speedtest_thread.start()
            
            return {
                'success': True,
                'message': 'Speedtest started in background',
                'status': 'running'
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': f'Speedtest failed to start: {str(e)}'
            }
    
    def _run_speedtest_background(self):
        """Run speedtest in background"""
        try:
            self.speedtest_running = True
            
            # Run speedtest
            st = speedtest.Speedtest()
            
            # Get best server
            st.get_best_server()
            
            # Download test
            download_speed = st.download()
            
            # Upload test
            upload_speed = st.upload()
            
            # Ping test
            ping = st.results.ping
            
            # Store results
            self.speedtest_results = {
                'download_speed': download_speed / 1_000_000,  # Convert to Mbps
                'upload_speed': upload_speed / 1_000_000,      # Convert to Mbps
                'ping': ping,
                'timestamp': datetime.now().isoformat(),
                'server': {
                    'name': st.results.server['name'],
                    'country': st.results.server['country'],
                    'sponsor': st.results.server['sponsor']
                },
                'client': {
                    'ip': st.results.client['ip'],
                    'isp': st.results.client['isp']
                }
            }
            
            print(f"Speedtest completed: {self.speedtest_results['download_speed']:.2f} Mbps down, {self.speedtest_results['upload_speed']:.2f} Mbps up, {self.speedtest_results['ping']:.0f} ms ping")
            
        except Exception as e:
            print(f"Speedtest failed: {e}")
            self.speedtest_results = {
                'error': str(e),
                'timestamp': datetime.now().isoformat()
            }
        finally:
            self.speedtest_running = False
    
    def get_speedtest_results(self) -> Dict[str, Any]:
        """Get speedtest results"""
        if self.speedtest_running:
            return {
                'status': 'running',
                'message': 'Speedtest in progress...'
            }
        elif self.speedtest_results:
            return {
                'status': 'completed',
                'results': self.speedtest_results
            }
        else:
            return {
                'status': 'not_run',
                'message': 'No speedtest results available'
            }
    
    def get_network_status(self) -> Dict[str, Any]:
        """Get current network status"""
        try:
            # Get network I/O stats
            net_io = psutil.net_io_counters()
            
            # Get network interfaces
            interfaces = {}
            for name, info in self.network_interfaces.items():
                interfaces[name] = {
                    'is_up': info['is_up'],
                    'speed': info['speed'],
                    'is_wifi': name == self.wifi_adapter
                }
            
            return {
                'interfaces': interfaces,
                'wifi_adapter': self.wifi_adapter,
                'bytes_sent': net_io.bytes_sent,
                'bytes_recv': net_io.bytes_recv,
                'packets_sent': net_io.packets_sent,
                'packets_recv': net_io.packets_recv,
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            return {
                'error': f'Network status failed: {str(e)}'
            }
    
    def get_status(self) -> Dict[str, Any]:
        """Get system toggles service status"""
        return {
            'is_active': self.is_active,
            'wifi_adapter': self.wifi_adapter,
            'current_volume': self.current_volume,
            'volume_percentage': int(self.current_volume * 100),
            'speedtest_running': self.speedtest_running,
            'speedtest_available': SPEEDTEST_AVAILABLE,
            'network_interfaces_count': len(self.network_interfaces),
            'last_updated': datetime.now().isoformat()
        }

    def get_status(self):
        return {
            'is_active': True,
            'wifi_available': True,
            'volume_available': True
        }
