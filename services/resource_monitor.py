#!/usr/bin/env python3
"""
Resource Monitor Service for JARVIS - Requirement #14
Calculate total disk usage for JARVIS components
"""

import os
import sys
import time
from datetime import datetime
from typing import Dict, Any, List, Optional, Tuple
import shutil
import platform

# Add JARVIS backend path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

class ResourceMonitor:
    """Resource monitor for JARVIS disk usage calculation"""
    
    def __init__(self):
        self.is_active = True
        
        # Platform-specific paths
        if platform.system() == 'Windows':
            self.ollama_models_path = os.path.join(os.path.expanduser('~'), '.ollama', 'models')
        else:
            self.ollama_models_path = os.path.join(os.path.expanduser('~'), '.ollama', 'models')
        
        # JARVIS project paths
        self.project_root = os.path.dirname(os.path.dirname(__file__))
        self.chromadb_path = os.path.join(self.project_root, 'chroma_db')
        self.logs_path = os.path.join(self.project_root, 'logs')
        self.cache_path = os.path.join(self.project_root, 'cache')
        
        # Storage threshold for warning (50GB)
        self.warning_threshold_gb = 50
        
        print("Resource Monitor Service initialized")
    
    def get_directory_size(self, path: str) -> Dict[str, Any]:
        """Calculate total size of a directory"""
        try:
            if not os.path.exists(path):
                return {
                    'path': path,
                    'exists': False,
                    'size_bytes': 0,
                    'size_mb': 0,
                    'size_gb': 0,
                    'file_count': 0,
                    'error': 'Directory does not exist'
                }
            
            total_size = 0
            file_count = 0
            
            for root, dirs, files in os.walk(path):
                for file in files:
                    try:
                        file_path = os.path.join(root, file)
                        file_size = os.path.getsize(file_path)
                        total_size += file_size
                        file_count += 1
                    except (OSError, PermissionError):
                        continue
            
            return {
                'path': path,
                'exists': True,
                'size_bytes': total_size,
                'size_mb': total_size / (1024 * 1024),
                'size_gb': total_size / (1024 * 1024 * 1024),
                'file_count': file_count
            }
            
        except Exception as e:
            return {
                'path': path,
                'exists': False,
                'size_bytes': 0,
                'size_mb': 0,
                'size_gb': 0,
                'file_count': 0,
                'error': str(e)
            }
    
    def get_ollama_models_size(self) -> Dict[str, Any]:
        """Calculate Ollama models directory size"""
        return self.get_directory_size(self.ollama_models_path)
    
    def get_chromadb_size(self) -> Dict[str, Any]:
        """Calculate ChromaDB directory size"""
        return self.get_directory_size(self.chromadb_path)
    
    def get_logs_cache_size(self) -> Dict[str, Any]:
        """Calculate logs and cache directory sizes"""
        logs_info = self.get_directory_size(self.logs_path)
        cache_info = self.get_directory_size(self.cache_path)
        
        total_size = logs_info['size_bytes'] + cache_info['size_bytes']
        total_files = logs_info['file_count'] + cache_info['file_count']
        
        return {
            'logs': logs_info,
            'cache': cache_info,
            'total_size_bytes': total_size,
            'total_size_mb': total_size / (1024 * 1024),
            'total_size_gb': total_size / (1024 * 1024 * 1024),
            'total_file_count': total_files
        }
    
    def get_project_files_size(self) -> Dict[str, Any]:
        """Calculate total project directory size"""
        return self.get_directory_size(self.project_root)
    
    def get_system_status(self) -> Dict[str, Any]:
        """Get complete system storage status"""
        try:
            # Get individual component sizes
            ollama_info = self.get_ollama_models_size()
            chromadb_info = self.get_chromadb_size()
            logs_cache_info = self.get_logs_cache_size()
            project_info = self.get_project_files_size()
            
            # Calculate total storage used
            total_storage_bytes = (
                ollama_info['size_bytes'] + 
                chromadb_info['size_bytes'] + 
                logs_cache_info['total_size_bytes']
            )
            
            total_storage_gb = total_storage_bytes / (1024 * 1024 * 1024)
            
            # Check for warning
            warning = None
            if total_storage_gb > self.warning_threshold_gb:
                warning = f"Sir, storage is getting high; consider pruning unused models."
            
            return {
                'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                'ollama_models': {
                    'path': ollama_info['path'],
                    'size_mb': ollama_info['size_mb'],
                    'size_gb': ollama_info['size_gb'],
                    'exists': ollama_info['exists'],
                    'file_count': ollama_info['file_count']
                },
                'chromadb': {
                    'path': chromadb_info['path'],
                    'size_mb': chromadb_info['size_mb'],
                    'size_gb': chromadb_info['size_gb'],
                    'exists': chromadb_info['exists'],
                    'file_count': chromadb_info['file_count']
                },
                'logs_cache': {
                    'logs_size_mb': logs_cache_info['logs']['size_mb'],
                    'cache_size_mb': logs_cache_info['cache']['size_mb'],
                    'total_size_mb': logs_cache_info['total_size_mb'],
                    'total_size_gb': logs_cache_info['total_size_gb'],
                    'total_file_count': logs_cache_info['total_file_count']
                },
                'project_files': {
                    'path': project_info['path'],
                    'size_mb': project_info['size_mb'],
                    'size_gb': project_info['size_gb'],
                    'file_count': project_info['file_count']
                },
                'total_storage': {
                    'size_mb': total_storage_bytes / (1024 * 1024),
                    'size_gb': total_storage_gb,
                    'warning_threshold_gb': self.warning_threshold_gb,
                    'warning': warning
                }
            }
            
        except Exception as e:
            return {
                'error': f'System status calculation failed: {str(e)}',
                'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            }
    
    def format_system_status_table(self, status: Dict[str, Any]) -> str:
        """Format system status as a clean table for terminal output"""
        try:
            if 'error' in status:
                return f"Error: {status['error']}"
            
            table_lines = []
            table_lines.append("=" * 60)
            table_lines.append("JARVIS SYSTEM STORAGE STATUS")
            table_lines.append("=" * 60)
            table_lines.append(f"Timestamp: {status['timestamp']}")
            table_lines.append("")
            
            # Ollama Models
            ollama = status['ollama_models']
            if ollama['exists']:
                table_lines.append("OLLAMA MODELS:")
                table_lines.append(f"  Path: {ollama['path']}")
                table_lines.append(f"  Size: {ollama['size_gb']:.2f} GB ({ollama['size_mb']:.1f} MB)")
                table_lines.append(f"  Files: {ollama['file_count']}")
            else:
                table_lines.append("OLLAMA MODELS: Not found")
            table_lines.append("")
            
            # ChromaDB
            chromadb = status['chromadb']
            if chromadb['exists']:
                table_lines.append("CHROMADB (Memory):")
                table_lines.append(f"  Path: {chromadb['path']}")
                table_lines.append(f"  Size: {chromadb['size_gb']:.2f} GB ({chromadb['size_mb']:.1f} MB)")
                table_lines.append(f"  Files: {chromadb['file_count']}")
            else:
                table_lines.append("CHROMADB (Memory): Not found")
            table_lines.append("")
            
            # Logs & Cache
            logs_cache = status['logs_cache']
            table_lines.append("LOGS & CACHE:")
            table_lines.append(f"  Logs: {logs_cache['logs']['size_mb']:.1f} MB")
            table_lines.append(f"  Cache: {logs_cache['cache']['size_mb']:.1f} MB")
            table_lines.append(f"  Total: {logs_cache['total_size_gb']:.2f} GB ({logs_cache['total_size_mb']:.1f} MB)")
            table_lines.append(f"  Files: {logs_cache['total_file_count']}")
            table_lines.append("")
            
            # Project Files
            project = status['project_files']
            table_lines.append("PROJECT FILES:")
            table_lines.append(f"  Path: {project['path']}")
            table_lines.append(f"  Size: {project['size_gb']:.2f} GB ({project['size_mb']:.1f} MB)")
            table_lines.append(f"  Files: {project['file_count']}")
            table_lines.append("")
            
            # Total Storage
            total = status['total_storage']
            table_lines.append("-" * 40)
            table_lines.append("TOTAL STORAGE USAGE:")
            table_lines.append(f"  Size: {total['size_gb']:.2f} GB ({total['size_mb']:.1f} MB)")
            table_lines.append(f"  Warning Threshold: {total['warning_threshold_gb']} GB")
            
            # Warning if needed
            if total['warning']:
                table_lines.append("")
                table_lines.append("WARNING: " + total['warning'])
            
            table_lines.append("=" * 60)
            
            return "\n".join(table_lines)
            
        except Exception as e:
            return f"Error formatting table: {str(e)}"
    
    def check_storage_warning(self) -> Optional[str]:
        """Check if storage exceeds warning threshold"""
        try:
            status = self.get_system_status()
            total_storage_gb = status['total_storage']['size_gb']
            
            if total_storage_gb > self.warning_threshold_gb:
                return f"Sir, storage is getting high; consider pruning unused models. Current usage: {total_storage_gb:.2f} GB"
            
            return None
            
        except Exception as e:
            return f"Storage check failed: {str(e)}"
    
    def get_status(self) -> Dict[str, Any]:
        """Get service status"""
        return {
            'is_active': self.is_active,
            'ollama_models_path': self.ollama_models_path,
            'project_root': self.project_root,
            'chromadb_path': self.chromadb_path,
            'logs_path': self.logs_path,
            'cache_path': self.cache_path,
            'warning_threshold_gb': self.warning_threshold_gb,
            'last_updated': datetime.now().isoformat()
        }

# Global instance for easy access
resource_monitor = ResourceMonitor()
