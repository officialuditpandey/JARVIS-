"""
Git Service for JARVIS - Auto-backup and Version Control
Feature 14: Git Service for automatic backups
"""

import os
import subprocess
import threading
import time
from datetime import datetime
from typing import Dict, Any, Optional, List
import sys

# Add JARVIS backend path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

try:
    import yaml
    with open('config/settings.yaml', 'r') as f:
        CONFIG = yaml.safe_load(f)
except:
    CONFIG = {
        'architect_pack': {
            'git_service': {'enabled': True, 'auto_backup': True, 'backup_interval': 3600}
        }
    }

class GitService:
    """Git service for automatic backups and version control"""
    
    def __init__(self):
        self.repo_path = CONFIG['architect_pack']['git_service'].get('repo_path', '.')
        self.backup_thread = None
        self.stop_event = threading.Event()
        self.auto_backup_enabled = CONFIG['architect_pack']['git_service']['auto_backup']
        self.backup_interval = CONFIG['architect_pack']['git_service']['backup_interval']
        
    def initialize_repo(self) -> bool:
        """Initialize git repository if not exists"""
        try:
            if not os.path.exists(os.path.join(self.repo_path, '.git')):
                # Initialize new repository
                subprocess.run(['git', 'init'], cwd=self.repo_path, check=True, capture_output=True)
                subprocess.run(['git', 'config', 'user.name', 'JARVIS'], cwd=self.repo_path, check=True, capture_output=True)
                subprocess.run(['git', 'config', 'user.email', 'jarvis@ai.local'], cwd=self.repo_path, check=True, capture_output=True)
                
                # Create initial commit
                self._create_commit("Initial JARVIS repository setup")
                print("Git repository initialized")
            else:
                print("Git repository already exists")
            
            return True
            
        except subprocess.CalledProcessError as e:
            print(f"Git initialization failed: {e}")
            return False
        except Exception as e:
            print(f"Git service error: {e}")
            return False
    
    def start_auto_backup(self) -> bool:
        """Start automatic backup thread"""
        if not self.auto_backup_enabled or not CONFIG['architect_pack']['git_service']['enabled']:
            return False
        
        try:
            self.stop_event.clear()
            self.backup_thread = threading.Thread(target=self._auto_backup_loop, daemon=True)
            self.backup_thread.start()
            print("Auto backup started")
            return True
            
        except Exception as e:
            print(f"Failed to start auto backup: {e}")
            return False
    
    def stop_auto_backup(self) -> bool:
        """Stop automatic backup thread"""
        try:
            self.stop_event.set()
            if self.backup_thread and self.backup_thread.is_alive():
                self.backup_thread.join(timeout=5)
            print("Auto backup stopped")
            return True
            
        except Exception as e:
            print(f"Failed to stop auto backup: {e}")
            return False
    
    def _auto_backup_loop(self):
        """Background thread for automatic backups"""
        while not self.stop_event.is_set():
            try:
                time.sleep(self.backup_interval)
                
                if not self.stop_event.is_set():
                    self.perform_backup()
                    
            except Exception as e:
                print(f"Auto backup loop error: {e}")
                time.sleep(60)  # Wait before retrying
    
    def perform_backup(self) -> bool:
        """Perform immediate backup"""
        try:
            # Check if there are changes
            result = subprocess.run(['git', 'status', '--porcelain'], 
                                   cwd=self.repo_path, capture_output=True, text=True)
            
            if result.stdout.strip():
                # There are changes to commit
                commit_message = CONFIG['architect_pack']['git_service'].get('commit_message', 
                                                                       'Auto-backup by JARVIS')
                self._create_commit(commit_message)
                print(f"Backup completed: {commit_message}")
                return True
            else:
                print("No changes to backup")
                return True
                
        except Exception as e:
            print(f"Backup failed: {e}")
            return False
    
    def _create_commit(self, message: str) -> bool:
        """Create git commit with all changes"""
        try:
            # Add all changes
            subprocess.run(['git', 'add', '.'], cwd=self.repo_path, check=True, capture_output=True)
            
            # Commit changes
            subprocess.run(['git', 'commit', '-m', message], cwd=self.repo_path, check=True, capture_output=True)
            
            return True
            
        except subprocess.CalledProcessError as e:
            print(f"Git commit failed: {e}")
            return False
    
    def get_repo_status(self) -> Dict[str, Any]:
        """Get current repository status"""
        try:
            # Get git status
            result = subprocess.run(['git', 'status', '--porcelain'], 
                                   cwd=self.repo_path, capture_output=True, text=True)
            
            changed_files = len([line for line in result.stdout.split('\n') if line.strip()])
            
            # Get last commit info
            result = subprocess.run(['git', 'log', '-1', '--format=%H|%s|%ci'], 
                                   cwd=self.repo_path, capture_output=True, text=True)
            
            last_commit = "No commits"
            if result.stdout.strip():
                commit_hash, commit_msg, commit_date = result.stdout.strip().split('|')
                last_commit = f"{commit_hash[:8]} - {commit_msg} ({commit_date})"
            
            return {
                'repo_path': self.repo_path,
                'auto_backup_enabled': self.auto_backup_enabled,
                'backup_interval': self.backup_interval,
                'changed_files': changed_files,
                'last_commit': last_commit,
                'auto_backup_active': self.backup_thread.is_alive() if self.backup_thread else False
            }
            
        except Exception as e:
            return {'error': str(e)}
    
    def create_branch(self, branch_name: str) -> bool:
        """Create and switch to new branch"""
        try:
            subprocess.run(['git', 'checkout', '-b', branch_name], 
                           cwd=self.repo_path, check=True, capture_output=True)
            print(f"Created and switched to branch: {branch_name}")
            return True
            
        except subprocess.CalledProcessError as e:
            print(f"Failed to create branch: {e}")
            return False
    
    def merge_branch(self, branch_name: str) -> bool:
        """Merge branch into current branch"""
        try:
            subprocess.run(['git', 'merge', branch_name], 
                           cwd=self.repo_path, check=True, capture_output=True)
            print(f"Merged branch: {branch_name}")
            return True
            
        except subprocess.CalledProcessError as e:
            print(f"Failed to merge branch: {e}")
            return False
    
    def get_commit_history(self, limit: int = 10) -> List[Dict]:
        """Get commit history"""
        try:
            result = subprocess.run(['git', 'log', f'--oneline', '-{limit}'], 
                                   cwd=self.repo_path, capture_output=True, text=True)
            
            commits = []
            for line in result.stdout.split('\n'):
                if line.strip():
                    parts = line.split(' ', 1)
                    if len(parts) >= 2:
                        commits.append({
                            'hash': parts[0],
                            'message': parts[1]
                        })
            
            return commits
            
        except Exception as e:
            print(f"Failed to get commit history: {e}")
            return []
