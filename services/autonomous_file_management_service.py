#!/usr/bin/env python3
"""
Autonomous File Management Service for JARVIS
Organize, move, and rename local files natively
"""

import os
import sys
import time
import shutil
import json
import hashlib
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional, Tuple
import mimetypes
import threading
from pathlib import Path

# Add JARVIS backend path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

class AutonomousFileManagementService:
    """Autonomous File Management service for native file operations"""
    
    def __init__(self):
        self.is_active = False
        self.management_thread = None
        self.stop_event = threading.Event()
        
        # File organization rules
        self.organization_rules = {
            'documents': {
                'extensions': ['.pdf', '.doc', '.docx', '.txt', '.rtf', '.odt'],
                'keywords': ['document', 'report', 'essay', 'paper'],
                'target_folder': 'Documents'
            },
            'images': {
                'extensions': ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.tiff', '.svg', '.webp'],
                'keywords': ['photo', 'image', 'picture', 'screenshot'],
                'target_folder': 'Pictures'
            },
            'videos': {
                'extensions': ['.mp4', '.avi', '.mkv', '.mov', '.wmv', '.flv', '.webm'],
                'keywords': ['video', 'movie', 'clip'],
                'target_folder': 'Videos'
            },
            'music': {
                'extensions': ['.mp3', '.wav', '.flac', '.aac', '.ogg', '.m4a', '.wma'],
                'keywords': ['music', 'song', 'audio'],
                'target_folder': 'Music'
            },
            'archives': {
                'extensions': ['.zip', '.rar', '.7z', '.tar', '.gz', '.bz2'],
                'keywords': ['archive', 'compressed'],
                'target_folder': 'Archives'
            },
            'code': {
                'extensions': ['.py', '.js', '.html', '.css', '.java', '.cpp', '.c', '.h', '.php', '.rb', '.go'],
                'keywords': ['code', 'script', 'program'],
                'target_folder': 'Code'
            },
            'downloads': {
                'extensions': ['.exe', '.msi', '.dmg', '.pkg', '.deb', '.rpm'],
                'keywords': ['download', 'installer'],
                'target_folder': 'Downloads'
            }
        }
        
        # Auto-organization settings
        self.auto_organize = True
        self.scan_interval = 300  # 5 minutes
        self.last_scan_time = 0
        self.monitored_directories = [
            'Downloads',
            'Desktop',
            'Documents'
        ]
        
        # File tracking
        self.file_registry = {}
        self.organization_history = []
        self.duplicate_files = {}
        
        # Performance metrics
        self.files_organized = 0
        self.files_moved = 0
        self.files_renamed = 0
        self.duplicates_found = 0
        self.start_time = time.time()
        
        # Initialize
        self._initialize_file_management()
        
        print("Autonomous File Management Service initialized")
    
    def _initialize_file_management(self):
        """Initialize file management system"""
        try:
            # Create target directories
            for category, rules in self.organization_rules.items():
                target_folder = rules['target_folder']
                os.makedirs(target_folder, exist_ok=True)
            
            # Load file registry
            self._load_file_registry()
            
            # Scan initial files
            self._scan_all_directories()
            
        except Exception as e:
            print(f"File management initialization failed: {e}")
    
    def _load_file_registry(self):
        """Load file registry from disk"""
        try:
            registry_file = 'file_registry.json'
            if os.path.exists(registry_file):
                with open(registry_file, 'r') as f:
                    self.file_registry = json.load(f)
                print(f"Loaded {len(self.file_registry)} files from registry")
        except Exception as e:
            print(f"Failed to load file registry: {e}")
            self.file_registry = {}
    
    def _save_file_registry(self):
        """Save file registry to disk"""
        try:
            registry_file = 'file_registry.json'
            with open(registry_file, 'w') as f:
                json.dump(self.file_registry, f, indent=2)
        except Exception as e:
            print(f"Failed to save file registry: {e}")
    
    def _scan_all_directories(self):
        """Scan all monitored directories"""
        try:
            for directory in self.monitored_directories:
                if os.path.exists(directory):
                    self._scan_directory(directory)
        except Exception as e:
            print(f"Directory scan failed: {e}")
    
    def _scan_directory(self, directory: str):
        """Scan a specific directory for files"""
        try:
            for root, dirs, files in os.walk(directory):
                for file in files:
                    file_path = os.path.join(root, file)
                    self._register_file(file_path)
        except Exception as e:
            print(f"Directory scan failed for {directory}: {e}")
    
    def _register_file(self, file_path: str):
        """Register a file in the registry"""
        try:
            if not os.path.exists(file_path):
                return
            
            # Get file info
            stat = os.stat(file_path)
            file_hash = self._calculate_file_hash(file_path)
            
            file_info = {
                'path': file_path,
                'name': os.path.basename(file_path),
                'size': stat.st_size,
                'modified': stat.st_mtime,
                'hash': file_hash,
                'category': self._categorize_file(file_path),
                'registered_at': time.time()
            }
            
            self.file_registry[file_path] = file_info
            
            # Check for duplicates
            if file_hash in self.duplicate_files:
                self.duplicate_files[file_hash].append(file_path)
            else:
                self.duplicate_files[file_hash] = [file_path]
            
        except Exception as e:
            print(f"File registration failed for {file_path}: {e}")
    
    def _calculate_file_hash(self, file_path: str) -> str:
        """Calculate MD5 hash of file"""
        try:
            hash_md5 = hashlib.md5()
            with open(file_path, "rb") as f:
                for chunk in iter(lambda: f.read(4096), b""):
                    hash_md5.update(chunk)
            return hash_md5.hexdigest()
        except:
            return ""
    
    def _categorize_file(self, file_path: str) -> str:
        """Categorize file based on extension and name"""
        try:
            file_name = os.path.basename(file_path).lower()
            file_ext = os.path.splitext(file_path)[1].lower()
            
            # Check by extension
            for category, rules in self.organization_rules.items():
                if file_ext in rules['extensions']:
                    return category
            
            # Check by keywords
            for category, rules in self.organization_rules.items():
                for keyword in rules['keywords']:
                    if keyword in file_name:
                        return category
            
            return 'other'
            
        except Exception as e:
            return 'unknown'
    
    def start_automatic_organization(self) -> bool:
        """Start automatic file organization"""
        try:
            if self.is_active:
                return True
            
            self.is_active = True
            self.stop_event.clear()
            
            # Start management thread
            self.management_thread = threading.Thread(target=self._management_loop, daemon=True)
            self.management_thread.start()
            
            print("Automatic file organization started")
            return True
            
        except Exception as e:
            print(f"Failed to start automatic organization: {e}")
            return False
    
    def stop_automatic_organization(self):
        """Stop automatic file organization"""
        try:
            self.is_active = False
            self.stop_event.set()
            
            if self.management_thread and self.management_thread.is_alive():
                self.management_thread.join(timeout=2)
            
            print("Automatic file organization stopped")
            
        except Exception as e:
            print(f"Failed to stop automatic organization: {e}")
    
    def _management_loop(self):
        """Main management loop"""
        print("File management loop started")
        
        while self.is_active and not self.stop_event.is_set():
            try:
                current_time = time.time()
                
                # Perform organization at intervals
                if current_time - self.last_scan_time > self.scan_interval:
                    self._perform_organization()
                    self.last_scan_time = current_time
                
                time.sleep(10)  # Check every 10 seconds
                
            except Exception as e:
                print(f"Management loop error: {e}")
                time.sleep(30)
        
        print("File management loop ended")
    
    def _perform_organization(self):
        """Perform automatic file organization"""
        try:
            print("Performing automatic file organization...")
            
            # Scan for new files
            self._scan_all_directories()
            
            # Organize files
            organized_count = 0
            for file_path, file_info in self.file_registry.items():
                if self._should_organize_file(file_path, file_info):
                    result = self._organize_file(file_path, file_info)
                    if result['success']:
                        organized_count += 1
            
            # Clean up duplicates
            self._cleanup_duplicates()
            
            # Save registry
            self._save_file_registry()
            
            print(f"Organization completed: {organized_count} files organized")
            
        except Exception as e:
            print(f"Organization failed: {e}")
    
    def _should_organize_file(self, file_path: str, file_info: Dict[str, Any]) -> bool:
        """Check if file should be organized"""
        try:
            # Skip if already in correct category folder
            category = file_info['category']
            target_folder = self.organization_rules.get(category, {}).get('target_folder')
            
            if target_folder and target_folder in file_path:
                return False
            
            # Skip system files and hidden files
            if file_info['name'].startswith('.') or file_info['name'].startswith('$'):
                return False
            
            # Skip if file is too new (might still be downloading)
            if time.time() - file_info['modified'] < 60:  # Less than 1 minute old
                return False
            
            return True
            
        except:
            return False
    
    def _organize_file(self, file_path: str, file_info: Dict[str, Any]) -> Dict[str, Any]:
        """Organize a single file"""
        try:
            category = file_info['category']
            target_folder = self.organization_rules.get(category, {}).get('target_folder')
            
            if not target_folder:
                return {
                    'success': False,
                    'error': f'No target folder for category {category}'
                }
            
            # Create target folder if it doesn't exist
            os.makedirs(target_folder, exist_ok=True)
            
            # Generate new file path
            new_file_path = os.path.join(target_folder, file_info['name'])
            
            # Handle name conflicts
            if os.path.exists(new_file_path):
                base_name, ext = os.path.splitext(file_info['name'])
                counter = 1
                while os.path.exists(new_file_path):
                    new_file_path = os.path.join(target_folder, f"{base_name}_{counter}{ext}")
                    counter += 1
            
            # Move file
            shutil.move(file_path, new_file_path)
            
            # Update registry
            self.file_registry.pop(file_path, None)
            file_info['path'] = new_file_path
            file_info['organized_at'] = time.time()
            self.file_registry[new_file_path] = file_info
            
            # Log organization
            organization_entry = {
                'timestamp': datetime.now().isoformat(),
                'action': 'moved',
                'from': file_path,
                'to': new_file_path,
                'category': category
            }
            self.organization_history.append(organization_entry)
            
            # Keep only last 1000 entries
            if len(self.organization_history) > 1000:
                self.organization_history = self.organization_history[-1000:]
            
            self.files_organized += 1
            self.files_moved += 1
            
            return {
                'success': True,
                'action': 'moved',
                'from': file_path,
                'to': new_file_path,
                'category': category
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': f'File organization failed: {str(e)}'
            }
    
    def _cleanup_duplicates(self):
        """Clean up duplicate files"""
        try:
            duplicates_removed = 0
            
            for file_hash, file_list in self.duplicate_files.items():
                if len(file_list) > 1:
                    # Sort by modification time (keep newest)
                    file_list.sort(key=lambda x: self.file_registry.get(x, {}).get('modified', 0), reverse=True)
                    
                    # Remove duplicates (keep first one)
                    for duplicate_path in file_list[1:]:
                        try:
                            if os.path.exists(duplicate_path):
                                os.remove(duplicate_path)
                                self.file_registry.pop(duplicate_path, None)
                                duplicates_removed += 1
                        except:
                            pass
            
            if duplicates_removed > 0:
                self.duplicates_found += duplicates_removed
                print(f"Removed {duplicates_removed} duplicate files")
            
        except Exception as e:
            print(f"Duplicate cleanup failed: {e}")
    
    def organize_file(self, file_path: str, target_category: str = None) -> Dict[str, Any]:
        """Manually organize a specific file"""
        try:
            if not os.path.exists(file_path):
                return {
                    'success': False,
                    'error': f'File {file_path} not found'
                }
            
            # Register file if not in registry
            if file_path not in self.file_registry:
                self._register_file(file_path)
            
            file_info = self.file_registry[file_path]
            
            # Override category if specified
            if target_category:
                file_info['category'] = target_category
            
            # Organize file
            result = self._organize_file(file_path, file_info)
            
            return result
            
        except Exception as e:
            return {
                'success': False,
                'error': f'Manual organization failed: {str(e)}'
            }
    
    def rename_file(self, file_path: str, new_name: str) -> Dict[str, Any]:
        """Rename a file"""
        try:
            if not os.path.exists(file_path):
                return {
                    'success': False,
                    'error': f'File {file_path} not found'
                }
            
            # Get directory and new path
            directory = os.path.dirname(file_path)
            new_file_path = os.path.join(directory, new_name)
            
            # Check if new name already exists
            if os.path.exists(new_file_path):
                return {
                    'success': False,
                    'error': f'File {new_name} already exists'
                }
            
            # Rename file
            os.rename(file_path, new_file_path)
            
            # Update registry
            if file_path in self.file_registry:
                file_info = self.file_registry.pop(file_path)
                file_info['path'] = new_file_path
                file_info['name'] = new_name
                file_info['renamed_at'] = time.time()
                self.file_registry[new_file_path] = file_info
            
            # Log rename
            rename_entry = {
                'timestamp': datetime.now().isoformat(),
                'action': 'renamed',
                'from': file_path,
                'to': new_file_path
            }
            self.organization_history.append(rename_entry)
            
            self.files_renamed += 1
            
            return {
                'success': True,
                'from': file_path,
                'to': new_file_path,
                'message': f'File renamed to {new_name}'
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': f'Rename failed: {str(e)}'
            }
    
    def move_file(self, file_path: str, target_directory: str) -> Dict[str, Any]:
        """Move a file to target directory"""
        try:
            if not os.path.exists(file_path):
                return {
                    'success': False,
                    'error': f'File {file_path} not found'
                }
            
            if not os.path.exists(target_directory):
                os.makedirs(target_directory, exist_ok=True)
            
            # Get file name
            file_name = os.path.basename(file_path)
            new_file_path = os.path.join(target_directory, file_name)
            
            # Handle name conflicts
            if os.path.exists(new_file_path):
                base_name, ext = os.path.splitext(file_name)
                counter = 1
                while os.path.exists(new_file_path):
                    new_file_path = os.path.join(target_directory, f"{base_name}_{counter}{ext}")
                    counter += 1
            
            # Move file
            shutil.move(file_path, new_file_path)
            
            # Update registry
            if file_path in self.file_registry:
                file_info = self.file_registry.pop(file_path)
                file_info['path'] = new_file_path
                file_info['moved_at'] = time.time()
                self.file_registry[new_file_path] = file_info
            
            # Log move
            move_entry = {
                'timestamp': datetime.now().isoformat(),
                'action': 'moved',
                'from': file_path,
                'to': new_file_path
            }
            self.organization_history.append(move_entry)
            
            self.files_moved += 1
            
            return {
                'success': True,
                'from': file_path,
                'to': new_file_path,
                'message': f'File moved to {target_directory}'
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': f'Move failed: {str(e)}'
            }
    
    def find_duplicates(self, directory: str = None) -> List[Dict[str, Any]]:
        """Find duplicate files"""
        try:
            duplicates = []
            
            for file_hash, file_list in self.duplicate_files.items():
                if len(file_list) > 1:
                    # Filter by directory if specified
                    if directory:
                        file_list = [f for f in file_list if directory in f]
                    
                    if len(file_list) > 1:
                        duplicate_info = {
                            'hash': file_hash,
                            'files': file_list,
                            'count': len(file_list),
                            'total_size': sum(self.file_registry.get(f, {}).get('size', 0) for f in file_list)
                        }
                        duplicates.append(duplicate_info)
            
            return duplicates
            
        except Exception as e:
            print(f"Duplicate search failed: {e}")
            return []
    
    def get_file_info(self, file_path: str) -> Dict[str, Any]:
        """Get detailed information about a file"""
        try:
            if file_path not in self.file_registry:
                return {
                    'success': False,
                    'error': f'File {file_path} not in registry'
                }
            
            file_info = self.file_registry[file_path].copy()
            
            # Add additional information
            if os.path.exists(file_path):
                stat = os.stat(file_path)
                file_info.update({
                    'created': stat.st_ctime,
                    'accessed': stat.st_atime,
                    'is_readable': os.access(file_path, os.R_OK),
                    'is_writable': os.access(file_path, os.W_OK),
                    'is_executable': os.access(file_path, os.X_OK)
                })
            
            return {
                'success': True,
                'file_info': file_info
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': f'File info retrieval failed: {str(e)}'
            }
    
    def search_files(self, query: str, category: str = None, 
                   directory: str = None) -> List[Dict[str, Any]]:
        """Search files by name, category, or directory"""
        try:
            results = []
            query_lower = query.lower()
            
            for file_path, file_info in self.file_registry.items():
                # Filter by category
                if category and file_info.get('category') != category:
                    continue
                
                # Filter by directory
                if directory and directory not in file_path:
                    continue
                
                # Search in filename
                if query_lower in file_info['name'].lower():
                    results.append(file_info.copy())
            
            return results
            
        except Exception as e:
            print(f"File search failed: {e}")
            return []
    
    def get_organization_stats(self) -> Dict[str, Any]:
        """Get organization statistics"""
        try:
            # Count files by category
            category_counts = {}
            for file_info in self.file_registry.values():
                category = file_info.get('category', 'unknown')
                category_counts[category] = category_counts.get(category, 0) + 1
            
            # Calculate total size
            total_size = sum(info.get('size', 0) for info in self.file_registry.values())
            
            return {
                'total_files': len(self.file_registry),
                'total_size_bytes': total_size,
                'total_size_mb': total_size / (1024 * 1024),
                'files_organized': self.files_organized,
                'files_moved': self.files_moved,
                'files_renamed': self.files_renamed,
                'duplicates_found': self.duplicates_found,
                'category_distribution': category_counts,
                'monitored_directories': self.monitored_directories,
                'organization_history_count': len(self.organization_history)
            }
            
        except Exception as e:
            return {
                'error': f'Stats retrieval failed: {str(e)}'
            }
    
    def get_organization_history(self, limit: int = 50) -> List[Dict[str, Any]]:
        """Get recent organization history"""
        return self.organization_history[-limit:]
    
    def get_status(self) -> Dict[str, Any]:
        """Get file management service status"""
        return {
            'is_active': self.is_active,
            'auto_organize': self.auto_organize,
            'scan_interval': self.scan_interval,
            'last_scan_time': datetime.fromtimestamp(self.last_scan_time).isoformat() if self.last_scan_time > 0 else None,
            'monitored_directories': self.monitored_directories,
            'files_in_registry': len(self.file_registry),
            'files_organized': self.files_organized,
            'files_moved': self.files_moved,
            'files_renamed': self.files_renamed,
            'duplicates_found': self.duplicates_found,
            'last_updated': datetime.now().isoformat()
        }
