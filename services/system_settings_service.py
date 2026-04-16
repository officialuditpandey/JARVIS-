#!/usr/bin/env python3
"""
System Settings Control Service for JARVIS
Voice commands for WiFi, Internet Speed Tests, and Volume control
"""

import os
import sys
import time
import subprocess
import json
import socket
import psutil
from datetime import datetime
from typing import Dict, Any, List, Optional, Tuple

# Add JARVIS backend path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

try:
    import speedtest
    SPEEDTEST_AVAILABLE = True
except ImportError:
    print("speedtest-cli not available - Installing...")
    os.system("pip install speedtest-cli")
    try:
        import speedtest
        SPEEDTEST_AVAILABLE = True
    except ImportError:
        SPEEDTEST_AVAILABLE = False

try:
    import pywifi
    from pywifi import const
    PYWIFI_AVAILABLE = True
except ImportError:
    print("pywifi not available - Installing...")
    os.system("pip install pywifi")
    try:
        import pywifi
        from pywifi import const
        PYWIFI_AVAILABLE = True
    except ImportError:
        PYWIFI_AVAILABLE = False

try:
    import pycaw
    from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume
    from ctypes import cast, POINTER
    from comtypes import CLSCTX_ALL
    PYCAW_AVAILABLE = True
except ImportError:
    print("pycaw not available - Installing...")
    os.system("pip install pycaw")
    try:
        import pycaw
        from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume
        from ctypes import cast, POINTER
        from comtypes import CLSCTX_ALL
        PYCAW_AVAILABLE = True
    except ImportError:
        PYCAW_AVAILABLE = False

class SystemSettingsService:
    """System Settings Control service for system management"""
    
    def __init__(self):
        self.is_active = False
        self.settings_history = []
        self.current_settings = {}
        
        # WiFi settings
        self.wifi_interface = None
        self.available_networks = []
        self.current_network = None
        
        # Audio settings
        self.audio_devices = []
        self.current_volume = 0.5
        
        # Network settings
        self.network_info = {}
        self.speed_test_results = []
        
        # Initialize
        self._initialize_system_control()
        
        print("System Settings Control Service initialized")
    
    def _initialize_system_control(self):
        """Initialize system control components"""
        try:
            # Initialize WiFi
            if PYWIFI_AVAILABLE:
                self._initialize_wifi()
            
            # Initialize Audio
            if PYCAW_AVAILABLE:
                self._initialize_audio()
            
            # Get current network info
            self._update_network_info()
            
            # Get current system settings
            self._update_current_settings()
            
        except Exception as e:
            print(f"System control initialization failed: {e}")
    
    def _initialize_wifi(self):
        """Initialize WiFi control"""
        try:
            wifi = pywifi.Control()
            interfaces = wifi.interfaces()
            
            if interfaces:
                self.wifi_interface = interfaces[0]
                print(f"WiFi interface initialized: {self.wifi_interface.name()}")
            else:
                print("No WiFi interfaces found")
                
        except Exception as e:
            print(f"WiFi initialization failed: {e}")
    
    def _initialize_audio(self):
        """Initialize audio control"""
        try:
            devices = AudioUtilities.GetSpeakers()
            interface = devices.Activate(IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
            volume = cast(interface, POINTER(IAudioEndpointVolume))
            
            self.current_volume = volume.GetMasterVolumeLevelScalar()
            self.audio_devices = [devices]
            
            print("Audio control initialized")
            
        except Exception as e:
            print(f"Audio initialization failed: {e}")
    
    def _update_network_info(self):
        """Update network information"""
        try:
            # Get local IP
            hostname = socket.gethostname()
            local_ip = socket.gethostbyname(hostname)
            
            # Get network interfaces
            interfaces = psutil.net_if_addrs()
            network_stats = psutil.net_if_stats()
            
            self.network_info = {
                'hostname': hostname,
                'local_ip': local_ip,
                'interfaces': list(interfaces.keys()),
                'interface_stats': {name: {
                    'isup': stats.isup,
                    'speed': stats.speed,
                    'mtu': stats.mtu
                } for name, stats in network_stats.items()},
                'last_updated': datetime.now().isoformat()
            }
            
        except Exception as e:
            print(f"Network info update failed: {e}")
    
    def _update_current_settings(self):
        """Update current system settings"""
        try:
            self.current_settings = {
                'volume': self.current_volume,
                'network_info': self.network_info,
                'system_info': {
                    'cpu_percent': psutil.cpu_percent(),
                    'memory_percent': psutil.virtual_memory().percent,
                    'disk_usage': psutil.disk_usage('/').percent,
                    'boot_time': psutil.boot_time()
                },
                'last_updated': datetime.now().isoformat()
            }
            
        except Exception as e:
            print(f"Settings update failed: {e}")
    
    def scan_wifi_networks(self) -> Dict[str, Any]:
        """Scan for available WiFi networks"""
        try:
            if not PYWIFI_AVAILABLE or not self.wifi_interface:
                return {
                    'success': False,
                    'error': 'WiFi control not available'
                }
            
            # Scan for networks
            self.wifi_interface.scan()
            time.sleep(2)  # Wait for scan to complete
            
            # Get scan results
            scan_results = self.wifi_interface.scan_results()
            
            networks = []
            for result in scan_results:
                network_info = {
                    'ssid': result.ssid,
                    'bssid': result.bssid,
                    'signal_strength': result.signal,
                    'frequency': result.freq,
                    'encrypted': bool(result.akm),
                    'auth': result.akm
                }
                networks.append(network_info)
            
            # Sort by signal strength
            networks.sort(key=lambda x: x['signal_strength'], reverse=True)
            
            self.available_networks = networks
            
            return {
                'success': True,
                'networks_found': len(networks),
                'networks': networks[:10],  # Return top 10
                'message': f'Found {len(networks)} WiFi networks'
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': f'WiFi scan failed: {str(e)}'
            }
    
    def connect_wifi(self, ssid: str, password: str = None) -> Dict[str, Any]:
        """Connect to WiFi network"""
        try:
            if not PYWIFI_AVAILABLE or not self.wifi_interface:
                return {
                    'success': False,
                    'error': 'WiFi control not available'
                }
            
            # Find network in scan results
            profile = None
            for result in self.wifi_interface.scan_results():
                if result.ssid == ssid:
                    profile = pywifi.Profile()
                    profile.ssid = result.ssid
                    profile.auth = const.AUTH_ALG_OPEN
                    profile.akm.append(const.AKM_TYPE_WPA2PSK)
                    profile.cipher = const.CIPHER_TYPE_CCMP
                    
                    if password:
                        profile.key = password
                    
                    break
            
            if not profile:
                return {
                    'success': False,
                    'error': f'Network {ssid} not found'
                }
            
            # Remove existing profiles for this network
            self.wifi_interface.remove_all_network_profiles()
            
            # Add new profile
            temp_profile = self.wifi_interface.add_network_profile(profile)
            
            # Connect
            self.wifi_interface.connect(temp_profile)
            
            # Wait for connection
            time.sleep(5)
            
            # Check connection status
            if self.wifi_interface.status() in [const.IFACE_CONNECTED, const.IFACE_CONNECTING]:
                self.current_network = ssid
                
                # Update network info
                self._update_network_info()
                
                return {
                    'success': True,
                    'network': ssid,
                    'status': 'connected',
                    'message': f'Connected to {ssid}'
                }
            else:
                return {
                    'success': False,
                    'error': f'Failed to connect to {ssid}'
                }
                
        except Exception as e:
            return {
                'success': False,
                'error': f'WiFi connection failed: {str(e)}'
            }
    
    def disconnect_wifi(self) -> Dict[str, Any]:
        """Disconnect from current WiFi network"""
        try:
            if not PYWIFI_AVAILABLE or not self.wifi_interface:
                return {
                    'success': False,
                    'error': 'WiFi control not available'
                }
            
            self.wifi_interface.disconnect()
            time.sleep(2)
            
            self.current_network = None
            
            return {
                'success': True,
                'message': 'Disconnected from WiFi'
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': f'WiFi disconnection failed: {str(e)}'
            }
    
    def get_wifi_status(self) -> Dict[str, Any]:
        """Get current WiFi status"""
        try:
            if not PYWIFI_AVAILABLE or not self.wifi_interface:
                return {
                    'success': False,
                    'error': 'WiFi control not available'
                }
            
            status = self.wifi_interface.status()
            status_map = {
                const.IFACE_DISCONNECTED: 'disconnected',
                const.IFACE_SCANNING: 'scanning',
                const.IFACE_INACTIVE: 'inactive',
                const.IFACE_CONNECTING: 'connecting',
                const.IFACE_CONNECTED: 'connected'
            }
            
            return {
                'success': True,
                'status': status_map.get(status, 'unknown'),
                'current_network': self.current_network,
                'interface_name': self.wifi_interface.name(),
                'available_networks': len(self.available_networks)
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': f'WiFi status check failed: {str(e)}'
            }
    
    def run_speed_test(self) -> Dict[str, Any]:
        """Run internet speed test"""
        try:
            if not SPEEDTEST_AVAILABLE:
                return {
                    'success': False,
                    'error': 'Speed test not available'
                }
            
            print("Running speed test...")
            
            # Create speed test instance
            st = speedtest.Speedtest()
            
            # Get best server
            st.get_best_server()
            
            # Download speed test
            download_speed = st.download()
            
            # Upload speed test
            upload_speed = st.upload()
            
            # Ping test
            ping = st.results.ping
            
            # Create result
            result = {
                'download_mbps': download_speed / 1_000_000,  # Convert to Mbps
                'upload_mbps': upload_speed / 1_000_000,    # Convert to Mbps
                'ping_ms': ping,
                'server': {
                    'name': st.results.server['name'],
                    'country': st.results.server['country'],
                    'sponsor': st.results.server['sponsor']
                },
                'timestamp': st.results.timestamp,
                'client': {
                    'ip': st.results.client['ip'],
                    'isp': st.results.client['isp']
                }
            }
            
            # Store result
            self.speed_test_results.append(result)
            if len(self.speed_test_results) > 50:
                self.speed_test_results = self.speed_test_results[-50:]
            
            return {
                'success': True,
                'result': result,
                'message': f'Download: {result["download_mbps"]:.2f} Mbps, Upload: {result["upload_mbps"]:.2f} Mbps, Ping: {ping} ms'
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': f'Speed test failed: {str(e)}'
            }
    
    def set_volume(self, volume: float) -> Dict[str, Any]:
        """Set system volume (0.0 to 1.0)"""
        try:
            if not PYCAW_AVAILABLE:
                return {
                    'success': False,
                    'error': 'Audio control not available'
                }
            
            volume = max(0.0, min(1.0, volume))
            
            # Get audio endpoint
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
            
        except Exception as e:
            return {
                'success': False,
                'error': f'Volume control failed: {str(e)}'
            }
    
    def get_volume(self) -> Dict[str, Any]:
        """Get current system volume"""
        try:
            if not PYCAW_AVAILABLE:
                return {
                    'success': False,
                    'error': 'Audio control not available'
                }
            
            # Get audio endpoint
            devices = AudioUtilities.GetSpeakers()
            interface = devices.Activate(IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
            volume_control = cast(interface, POINTER(IAudioEndpointVolume))
            
            # Get volume
            current_volume = volume_control.GetMasterVolumeLevelScalar()
            self.current_volume = current_volume
            
            return {
                'success': True,
                'volume': current_volume,
                'percentage': int(current_volume * 100),
                'is_muted': volume_control.GetMute()
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': f'Volume retrieval failed: {str(e)}'
            }
    
    def mute_volume(self, mute: bool = True) -> Dict[str, Any]:
        """Mute or unmute system volume"""
        try:
            if not PYCAW_AVAILABLE:
                return {
                    'success': False,
                    'error': 'Audio control not available'
                }
            
            # Get audio endpoint
            devices = AudioUtilities.GetSpeakers()
            interface = devices.Activate(IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
            volume_control = cast(interface, POINTER(IAudioEndpointVolume))
            
            # Set mute state
            volume_control.SetMute(mute, None)
            
            return {
                'success': True,
                'muted': mute,
                'message': f'Volume {"muted" if mute else "unmuted"}'
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': f'Mute control failed: {str(e)}'
            }
    
    def get_system_info(self) -> Dict[str, Any]:
        """Get comprehensive system information"""
        try:
            # CPU info
            cpu_info = {
                'percent': psutil.cpu_percent(interval=1),
                'count': psutil.cpu_count(),
                'freq': psutil.cpu_freq()._asdict() if psutil.cpu_freq() else None
            }
            
            # Memory info
            memory = psutil.virtual_memory()
            memory_info = {
                'total': memory.total,
                'available': memory.available,
                'percent': memory.percent,
                'used': memory.used,
                'free': memory.free
            }
            
            # Disk info
            disk = psutil.disk_usage('/')
            disk_info = {
                'total': disk.total,
                'used': disk.used,
                'free': disk.free,
                'percent': disk.percent
            }
            
            # Network info
            network = psutil.net_io_counters()
            network_info = {
                'bytes_sent': network.bytes_sent,
                'bytes_recv': network.bytes_recv,
                'packets_sent': network.packets_sent,
                'packets_recv': network.packets_recv
            }
            
            # Boot time
            boot_time = psutil.boot_time()
            boot_datetime = datetime.fromtimestamp(boot_time)
            
            return {
                'success': True,
                'system_info': {
                    'cpu': cpu_info,
                    'memory': memory_info,
                    'disk': disk_info,
                    'network': network_info,
                    'boot_time': boot_time,
                    'boot_datetime': boot_datetime.isoformat(),
                    'uptime_hours': (time.time() - boot_time) / 3600
                },
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': f'System info retrieval failed: {str(e)}'
            }
    
    def get_network_diagnostics(self) -> Dict[str, Any]:
        """Run network diagnostics"""
        try:
            diagnostics = {}
            
            # Test local connectivity
            try:
                socket.create_connection(("8.8.8.8", 53), timeout=3)
                diagnostics['internet_reachable'] = True
            except:
                diagnostics['internet_reachable'] = False
            
            # Test DNS resolution
            try:
                socket.gethostbyname("google.com")
                diagnostics['dns_working'] = True
            except:
                diagnostics['dns_working'] = False
            
            # Get network interfaces
            interfaces = psutil.net_if_addrs()
            interface_stats = psutil.net_if_stats()
            
            diagnostics['interfaces'] = {}
            for name in interfaces:
                stats = interface_stats.get(name)
                if stats:
                    diagnostics['interfaces'][name] = {
                        'isup': stats.isup,
                        'speed': stats.speed,
                        'duplex': stats.duplex,
                        'mtu': stats.mtu
                    }
            
            # Get current connections
            connections = psutil.net_connections()
            diagnostics['active_connections'] = len(connections)
            
            return {
                'success': True,
                'diagnostics': diagnostics,
                'message': 'Network diagnostics completed'
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': f'Network diagnostics failed: {str(e)}'
            }
    
    def get_speed_test_history(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get speed test history"""
        return self.speed_test_results[-limit:]
    
    def get_settings_history(self, limit: int = 20) -> List[Dict[str, Any]]:
        """Get settings change history"""
        return self.settings_history[-limit:]
    
    def get_status(self) -> Dict[str, Any]:
        """Get system settings service status"""
        return {
            'is_active': self.is_active,
            'wifi_available': PYWIFI_AVAILABLE,
            'speedtest_available': SPEEDTEST_AVAILABLE,
            'audio_available': PYCAW_AVAILABLE,
            'current_network': self.current_network,
            'current_volume': self.current_volume,
            'available_networks': len(self.available_networks),
            'speed_test_count': len(self.speed_test_results),
            'last_updated': datetime.now().isoformat()
        }
