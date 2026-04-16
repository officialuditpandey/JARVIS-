#!/usr/bin/env python3
"""
Resource Monitor Service for JARVIS - Feature 14
Monitor storage size of chroma_db and ollama models
"""

import os
import sys
import time
import json
import threading
from datetime import datetime
from typing import Dict, Any, List, Optional, Tuple
import psutil
import shutil

# Add JARVIS backend path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

class ResourceMonitorService:
    """Resource monitor service for storage and system resources"""
    
    def __init__(self):
        self.is_active = False
        self.monitoring_thread = None
        self.stop_event = threading.Event()
        self.resource_history = []
        
        # Monitoring paths
        self.monitor_paths = {
            'chroma_db': [
                './chroma_db',
                './data/chroma_db',
                os.path.expanduser('~/.chroma_db'),
                'C:/chroma_db'
            ],
            'ollama_models': [
                './ollama/models',
                './data/ollama',
                os.path.expanduser('~/.ollama/models'),
                'C:/ollama/models'
            ],
            'jarvis_data': [
                './data',
                './logs',
                './downloads',
                os.getcwd()
            ]
        }
        
        # Storage info
        self.storage_info = {}
        self.model_info = {}
        
        # Monitoring settings
        self.update_interval = 60  # Update every minute
        self.max_history = 1000
        
        # Initialize
        self._initialize_resource_monitor()
        
        print("Resource Monitor Service initialized")
    
    def _initialize_resource_monitor(self):
        """Initialize resource monitoring"""
        try:
            # Initial scan
            self._scan_all_resources()
            
            # Start monitoring thread
            self._start_monitoring()
            
            self.is_active = True
            
        except Exception as e:
            print(f"Resource monitor initialization failed: {e}")
    
    def _start_monitoring(self):
        """Start resource monitoring thread"""
        try:
            self.monitoring_thread = threading.Thread(
                target=self._monitoring_loop,
                daemon=True
            )
            self.monitoring_thread.start()
            print("Resource monitoring started")
        except Exception as e:
            print(f"Failed to start resource monitoring: {e}")
    
    def _monitoring_loop(self):
        """Main monitoring loop"""
        while self.is_active and not self.stop_event.is_set():
            try:
                # Scan all resources
                self._scan_all_resources()
                
                # Update history
                self._update_history()
                
                # Wait for next update
                self.stop_event.wait(self.update_interval)
                
            except Exception as e:
                print(f"Resource monitoring error: {e}")
                time.sleep(30)
    
    def _scan_all_resources(self):
        """Scan all monitored resources"""
        try:
            timestamp = datetime.now().isoformat()
            
            # Scan each category
            for category, paths in self.monitor_paths.items():
                category_info = self._scan_category_paths(category, paths, timestamp)
                self.storage_info[category] = category_info
            
            # Get system disk info
            self.storage_info['system_disk'] = self._get_disk_info()
            
            # Get memory info
            self.storage_info['memory'] = self._get_memory_info()
            
        except Exception as e:
            print(f"Resource scan failed: {e}")
    
    def _scan_category_paths(self, category: str, paths: List[str], timestamp: str) -> Dict[str, Any]:
        """Scan paths for a specific category"""
        category_info = {
            'total_size': 0,
            'file_count': 0,
            'directory_count': 0,
            'paths': {},
            'timestamp': timestamp
        }
        
        for path in paths:
            path_info = self._scan_path(path)
            if path_info['exists']:
                category_info['paths'][path] = path_info
                category_info['total_size'] += path_info['size']
                category_info['file_count'] += path_info['file_count']
                category_info['directory_count'] += path_info['directory_count']
        
        return category_info
    
    def _scan_path(self, path: str) -> Dict[str, Any]:
        """Scan a single path"""
        try:
            if not os.path.exists(path):
                return {
                    'exists': False,
                    'path': path,
                    'error': 'Path does not exist'
                }
            
            total_size = 0
            file_count = 0
            directory_count = 0
            largest_files = []
            file_types = {}
            
            if os.path.isfile(path):
                # Single file
                total_size = os.path.getsize(path)
                file_count = 1
                file_ext = os.path.splitext(path)[1].lower()
                file_types[file_ext] = 1
                largest_files = [{'path': path, 'size': total_size}]
            else:
                # Directory
                for root, dirs, files in os.walk(path):
                    directory_count += len(dirs)
                    
                    for file in files:
                        try:
                            file_path = os.path.join(root, file)
                            file_size = os.path.getsize(file_path)
                            total_size += file_size
                            file_count += 1
                            
                            # Track file types
                            file_ext = os.path.splitext(file)[1].lower()
                            file_types[file_ext] = file_types.get(file_ext, 0) + 1
                            
                            # Track largest files
                            largest_files.append({'path': file_path, 'size': file_size})
                            
                        except (OSError, PermissionError):
                            continue
            
            # Sort largest files
            largest_files.sort(key=lambda x: x['size'], reverse=True)
            largest_files = largest_files[:10]  # Top 10 largest
            
            return {
                'exists': True,
                'path': path,
                'size': total_size,
                'size_mb': total_size / (1024 * 1024),
                'size_gb': total_size / (1024 * 1024 * 1024),
                'file_count': file_count,
                'directory_count': directory_count,
                'file_types': file_types,
                'largest_files': largest_files[:5],  # Top 5
                'last_modified': self._get_last_modified(path)
            }
            
        except Exception as e:
            return {
                'exists': False,
                'path': path,
                'error': str(e)
            }
    
    def _get_last_modified(self, path: str) -> Optional[str]:
        """Get last modified time for path"""
        try:
            if os.path.isfile(path):
                return datetime.fromtimestamp(os.path.getmtime(path)).isoformat()
            else:
                # For directories, get the most recent file
                latest_time = 0
                for root, dirs, files in os.walk(path):
                    for file in files:
                        file_path = os.path.join(root, file)
                        try:
                            file_time = os.path.getmtime(file_path)
                            if file_time > latest_time:
                                latest_time = file_time
                        except (OSError, PermissionError):
                            continue
                
                if latest_time > 0:
                    return datetime.fromtimestamp(latest_time).isoformat()
                return None
                
        except:
            return None
    
    def _get_disk_info(self) -> Dict[str, Any]:
        """Get disk usage information"""
        try:
            disk_info = {}
            
            # Get all disk partitions
            partitions = psutil.disk_partitions()
            
            for partition in partitions:
                try:
                    usage = psutil.disk_usage(partition.mountpoint)
                    disk_info[partition.mountpoint] = {
                        'total': usage.total,
                        'total_gb': usage.total / (1024 * 1024 * 1024),
                        'used': usage.used,
                        'used_gb': usage.used / (1024 * 1024 * 1024),
                        'free': usage.free,
                        'free_gb': usage.free / (1024 * 1024 * 1024),
                        'percent_used': (usage.used / usage.total) * 100,
                        'filesystem': partition.fstype,
                        'mountpoint': partition.mountpoint
                    }
                except (OSError, PermissionError):
                    continue
            
            return disk_info
            
        except Exception as e:
            return {'error': f'Disk info failed: {str(e)}'}
    
    def _get_memory_info(self) -> Dict[str, Any]:
        """Get memory usage information"""
        try:
            memory = psutil.virtual_memory()
            swap = psutil.swap_memory()
            
            return {
                'ram': {
                    'total': memory.total,
                    'total_gb': memory.total / (1024 * 1024 * 1024),
                    'used': memory.used,
                    'used_gb': memory.used / (1024 * 1024 * 1024),
                    'available': memory.available,
                    'available_gb': memory.available / (1024 * 1024 * 1024),
                    'percent_used': memory.percent
                },
                'swap': {
                    'total': swap.total,
                    'total_gb': swap.total / (1024 * 1024 * 1024),
                    'used': swap.used,
                    'used_gb': swap.used / (1024 * 1024 * 1024),
                    'free': swap.free,
                    'free_gb': swap.free / (1024 * 1024 * 1024),
                    'percent_used': swap.percent
                }
            }
            
        except Exception as e:
            return {'error': f'Memory info failed: {str(e)}'}
    
    def _update_history(self):
        """Update resource history"""
        try:
            history_entry = {
                'timestamp': datetime.now().isoformat(),
                'storage_info': self.storage_info.copy()
            }
            
            self.resource_history.append(history_entry)
            
            # Limit history size
            if len(self.resource_history) > self.max_history:
                self.resource_history = self.resource_history[-self.max_history:]
                
        except Exception as e:
            print(f"History update failed: {e}")
    
    def get_chroma_db_info(self) -> Dict[str, Any]:
        """Get specific chroma_db storage information"""
        try:
            chroma_info = self.storage_info.get('chroma_db', {})
            
            # Additional chroma-specific analysis
            analysis = {
                'total_size_mb': chroma_info.get('total_size', 0) / (1024 * 1024),
                'total_size_gb': chroma_info.get('total_size', 0) / (1024 * 1024 * 1024),
                'file_count': chroma_info.get('file_count', 0),
                'active_paths': [path for path, info in chroma_info.get('paths', {}).items() if info.get('exists', False)],
                'largest_collections': []
            }
            
            # Analyze largest files (likely collections)
            for path_info in chroma_info.get('paths', {}).values():
                if path_info.get('exists') and path_info.get('largest_files'):
                    for file_info in path_info['largest_files'][:3]:
                        file_name = os.path.basename(file_info['path'])
                        if any(keyword in file_name.lower() for keyword in ['collection', 'index', 'data']):
                            analysis['largest_collections'].append({
                                'file': file_name,
                                'size_mb': file_info['size'] / (1024 * 1024),
                                'path': file_info['path']
                            })
            
            return {
                'success': True,
                'chroma_db': analysis,
                'timestamp': chroma_info.get('timestamp')
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': f'Chroma DB info failed: {str(e)}'
            }
    
    def get_ollama_models_info(self) -> Dict[str, Any]:
        """Get specific ollama models storage information"""
        try:
            ollama_info = self.storage_info.get('ollama_models', {})
            
            # Additional ollama-specific analysis
            analysis = {
                'total_size_mb': ollama_info.get('total_size', 0) / (1024 * 1024),
                'total_size_gb': ollama_info.get('total_size', 0) / (1024 * 1024 * 1024),
                'model_count': 0,
                'models': [],
                'active_paths': [path for path, info in ollama_info.get('paths', {}).items() if info.get('exists', False)]
            }
            
            # Identify model files
            for path_info in ollama_info.get('paths', {}).values():
                if path_info.get('exists') and path_info.get('largest_files'):
                    for file_info in path_info['largest_files']:
                        file_name = os.path.basename(file_info['path'])
                        file_path = file_info['path']
                        
                        # Likely model files (large files in ollama directory)
                        if file_info['size'] > 100 * 1024 * 1024:  # Larger than 100MB
                            model_name = self._extract_model_name(file_path, file_name)
                            analysis['models'].append({
                                'name': model_name,
                                'size_mb': file_info['size'] / (1024 * 1024),
                                'size_gb': file_info['size'] / (1024 * 1024 * 1024),
                                'path': file_path,
                                'file': file_name
                            })
                            analysis['model_count'] += 1
            
            # Sort models by size
            analysis['models'].sort(key=lambda x: x['size_gb'], reverse=True)
            
            return {
                'success': True,
                'ollama_models': analysis,
                'timestamp': ollama_info.get('timestamp')
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': f'Ollama models info failed: {str(e)}'
            }
    
    def _extract_model_name(self, file_path: str, file_name: str) -> str:
        """Extract model name from file path"""
        try:
            # Try to extract model name from path structure
            parts = file_path.split(os.sep)
            
            # Look for common ollama path patterns
            for i, part in enumerate(parts):
                if part == 'models' and i + 1 < len(parts):
                    return parts[i + 1]
            
            # Fallback to file name without extension
            name = os.path.splitext(file_name)[0]
            
            # Remove common suffixes
            for suffix in ['-gguf', '-q4', '-q8', '.bin']:
                if suffix in name:
                    name = name.replace(suffix, '')
            
            return name
            
        except:
            return file_name
    
    def get_storage_summary(self) -> Dict[str, Any]:
        """Get comprehensive storage summary"""
        try:
            summary = {
                'timestamp': datetime.now().isoformat(),
                'categories': {},
                'total_usage': 0,
                'system_disk': self.storage_info.get('system_disk', {}),
                'memory': self.storage_info.get('memory', {})
            }
            
            # Summarize each category
            for category, info in self.storage_info.items():
                if category in ['system_disk', 'memory']:
                    continue
                
                summary['categories'][category] = {
                    'size_mb': info.get('total_size', 0) / (1024 * 1024),
                    'size_gb': info.get('total_size', 0) / (1024 * 1024 * 1024),
                    'file_count': info.get('file_count', 0),
                    'active_paths': len([p for p in info.get('paths', {}).values() if p.get('exists', False)])
                }
                
                summary['total_usage'] += info.get('total_size', 0)
            
            summary['total_usage_mb'] = summary['total_usage'] / (1024 * 1024)
            summary['total_usage_gb'] = summary['total_usage'] / (1024 * 1024 * 1024)
            
            return summary
            
        except Exception as e:
            return {
                'success': False,
                'error': f'Storage summary failed: {str(e)}'
            }
    
    def cleanup_recommendations(self) -> Dict[str, Any]:
        """Get cleanup recommendations"""
        try:
            recommendations = []
            
            # Check chroma_db size
            chroma_info = self.get_chroma_db_info()
            if chroma_info['success']:
                chroma_size_gb = chroma_info['chroma_db'].get('total_size_gb', 0)
                if chroma_size_gb > 5:  # More than 5GB
                    recommendations.append({
                        'category': 'chroma_db',
                        'priority': 'high' if chroma_size_gb > 10 else 'medium',
                        'action': 'Consider cleaning old embeddings or unused collections',
                        'current_size_gb': chroma_size_gb
                    })
            
            # Check ollama models
            ollama_info = self.get_ollama_models_info()
            if ollama_info['success']:
                ollama_size_gb = ollama_info['ollama_models'].get('total_size_gb', 0)
                if ollama_size_gb > 20:  # More than 20GB
                    recommendations.append({
                        'category': 'ollama_models',
                        'priority': 'high' if ollama_size_gb > 50 else 'medium',
                        'action': 'Consider removing unused models',
                        'current_size_gb': ollama_size_gb,
                        'model_count': ollama_info['ollama_models'].get('model_count', 0)
                    })
            
            # Check disk space
            disk_info = self.storage_info.get('system_disk', {})
            for mountpoint, info in disk_info.items():
                if isinstance(info, dict) and info.get('percent_used', 0) > 80:
                    recommendations.append({
                        'category': 'disk_space',
                        'priority': 'high',
                        'action': f'Disk {mountpoint} is {info.get("percent_used", 0):.1f}% full',
                        'mountpoint': mountpoint,
                        'free_gb': info.get('free_gb', 0)
                    })
            
            return {
                'success': True,
                'recommendations': recommendations,
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': f'Cleanup recommendations failed: {str(e)}'
            }
    
    def get_status(self) -> Dict[str, Any]:
        """Get resource monitor service status"""
        return {
            'is_active': self.is_active,
            'monitoring_thread_alive': self.monitoring_thread and self.monitoring_thread.is_alive(),
            'update_interval': self.update_interval,
            'history_count': len(self.resource_history),
            'monitored_categories': list(self.monitor_paths.keys()),
            'last_updated': datetime.now().isoformat()
        }
