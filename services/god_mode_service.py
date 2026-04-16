#!/usr/bin/env python3
"""
God Mode Service for JARVIS - Native OpenClaw-style capabilities
Direct Terminal OS Control, Autonomous File System Mastery, Kernel-Level Intelligence,
Universal Integration, and Self-Correction Loop
"""

import os
import sys
import time
import threading
import queue
import json
import subprocess
import psutil
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional, Tuple
import re
import glob
import shutil
from pathlib import Path

# Add JARVIS backend path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

class GodModeService:
    """God Mode service with native OpenClaw-style capabilities"""
    
    def __init__(self):
        self.is_active = False
        self.command_queue = queue.Queue()
        self.active_processes = {}
        self.execution_history = []
        self.file_system_cache = {}
        
        # Terminal control settings
        self.default_timeout = 60  # 60 seconds default timeout
        self.max_concurrent_commands = 3
        self.admin_privileges = self._check_admin_privileges()
        
        # File system mastery settings
        self.monitored_directories = ['Desktop', 'Documents', 'Downloads', 'Pictures', 'Videos']
        self.file_index = {}
        self.last_index_time = 0
        self.index_interval = 300  # 5 minutes
        
        # Process monitoring settings
        self.process_thresholds = {
            'memory_mb': 1000,  # 1GB memory threshold
            'cpu_percent': 80,  # 80% CPU threshold
            'suspicious_processes': ['malware', 'virus', 'trojan', 'miner']
        }
        
        # Universal integration settings
        self.command_chains = []
        self.chain_results = {}
        
        # Self-correction settings
        self.correction_attempts = 3
        self.web_search_timeout = 30
        self.correction_patterns = {
            'permission_denied': ['access denied', 'permission denied', 'admin rights'],
            'file_not_found': ['not found', 'no such file', 'cannot find'],
            'network_error': ['network', 'connection', 'dns', 'timeout'],
            'syntax_error': ['syntax', 'invalid', 'unrecognized'],
            'dependency_error': ['missing', 'not installed', 'dependency']
        }
        
        # Performance metrics
        self.commands_executed = 0
        self.commands_failed = 0
        self.corrections_applied = 0
        self.processes_optimized = 0
        self.files_managed = 0
        self.start_time = time.time()
        
        # Initialize
        self._initialize_god_mode()
        
        print("God Mode Service initialized with OpenClaw-style capabilities")
    
    def _initialize_god_mode(self):
        """Initialize God Mode capabilities"""
        try:
            self.is_active = True
            
            # Start monitoring threads
            self._start_process_monitor()
            self._start_file_system_indexer()
            self._start_command_processor()
            
            # Initial file system indexing
            self._index_file_system()
            
            print("God Mode fully activated - All systems online")
            
        except Exception as e:
            print(f"God Mode initialization failed: {e}")
    
    def _check_admin_privileges(self) -> bool:
        """Check if running with administrator privileges"""
        try:
            if sys.platform == 'win32':
                import ctypes
                return ctypes.windll.shell32.IsUserAnAdmin() != 0
            else:
                return os.geteuid() == 0
        except:
            return False
    
    def _start_process_monitor(self):
        """Start kernel-level process monitoring"""
        try:
            self.process_monitor_thread = threading.Thread(target=self._process_monitor_loop, daemon=True)
            self.process_monitor_thread.start()
        except Exception as e:
            print(f"Failed to start process monitor: {e}")
    
    def _start_file_system_indexer(self):
        """Start file system indexing"""
        try:
            self.file_indexer_thread = threading.Thread(target=self._file_system_indexer_loop, daemon=True)
            self.file_indexer_thread.start()
        except Exception as e:
            print(f"Failed to start file system indexer: {e}")
    
    def _start_command_processor(self):
        """Start command processor"""
        try:
            self.command_processor_thread = threading.Thread(target=self._command_processor_loop, daemon=True)
            self.command_processor_thread.start()
        except Exception as e:
            print(f"Failed to start command processor: {e}")
    
    def _process_monitor_loop(self):
        """Kernel-level process monitoring loop"""
        print("Process monitoring started - Kernel-level intelligence active")
        
        while self.is_active:
            try:
                # Monitor system processes
                processes = list(psutil.process_iter(['pid', 'name', 'memory_percent', 'cpu_percent', 'memory_info']))
                
                for proc in processes:
                    try:
                        proc_info = proc.info
                        memory_mb = proc_info['memory_info'].rss / (1024 * 1024) if proc_info['memory_info'] else 0
                        
                        # Check for resource hogs
                        if (memory_mb > self.process_thresholds['memory_mb'] or 
                            proc_info['cpu_percent'] > self.process_thresholds['cpu_percent']):
                            
                            # Check if it's a suspicious process
                            process_name = proc_info['name'].lower()
                            is_suspicious = any(suspicious in process_name for suspicious in self.process_thresholds['suspicious_processes'])
                            
                            if is_suspicious or memory_mb > 2000:  # 2GB threshold for auto-kill
                                self._handle_problem_process(proc_info, is_suspicious)
                    
                    except (psutil.NoSuchProcess, psutil.AccessDenied):
                        continue
                
                time.sleep(10)  # Check every 10 seconds
                
            except Exception as e:
                print(f"Process monitoring error: {e}")
                time.sleep(30)
        
        print("Process monitoring stopped")
    
    def _handle_problem_process(self, proc_info: Dict[str, Any], is_suspicious: bool):
        """Handle problematic process"""
        try:
            pid = proc_info['pid']
            name = proc_info['name']
            memory_mb = proc_info['memory_info'].rss / (1024 * 1024) if proc_info['memory_info'] else 0
            
            # Log the issue
            issue = {
                'timestamp': datetime.now().isoformat(),
                'pid': pid,
                'name': name,
                'memory_mb': memory_mb,
                'cpu_percent': proc_info['cpu_percent'],
                'suspicious': is_suspicious,
                'action_taken': None
            }
            
            if is_suspicious:
                # Auto-kill suspicious processes
                try:
                    process = psutil.Process(pid)
                    process.terminate()
                    issue['action_taken'] = 'terminated_suspicious'
                    self.processes_optimized += 1
                    print(f"Auto-terminated suspicious process: {name} (PID: {pid})")
                except:
                    pass
            else:
                # Ask user about resource hogs
                print(f"Resource hog detected: {name} (PID: {pid}, Memory: {memory_mb:.1f}MB)")
                # In production, this would trigger a voice prompt to the user
            
            self.execution_history.append(issue)
            
        except Exception as e:
            print(f"Error handling problem process: {e}")
    
    def _file_system_indexer_loop(self):
        """File system indexing loop"""
        print("File system indexing started")
        
        while self.is_active:
            try:
                current_time = time.time()
                
                # Reindex periodically
                if current_time - self.last_index_time > self.index_interval:
                    self._index_file_system()
                    self.last_index_time = current_time
                
                time.sleep(60)  # Check every minute
                
            except Exception as e:
                print(f"File system indexing error: {e}")
                time.sleep(300)
        
        print("File system indexing stopped")
    
    def _index_file_system(self):
        """Index the file system for autonomous mastery"""
        try:
            print("Indexing file system...")
            self.file_index = {}
            
            # Get user directories
            user_home = os.path.expanduser('~')
            
            for directory in self.monitored_directories:
                dir_path = os.path.join(user_home, directory)
                if os.path.exists(dir_path):
                    self._index_directory(dir_path, directory)
            
            print(f"File system indexed: {len(self.file_index)} files")
            
        except Exception as e:
            print(f"File system indexing failed: {e}")
    
    def _index_directory(self, dir_path: str, category: str):
        """Index a directory and its contents"""
        try:
            for root, dirs, files in os.walk(dir_path):
                for file in files:
                    file_path = os.path.join(root, file)
                    
                    try:
                        # Get file info
                        stat = os.stat(file_path)
                        file_info = {
                            'path': file_path,
                            'name': file,
                            'category': category,
                            'size': stat.st_size,
                            'modified': stat.st_mtime,
                            'created': stat.st_ctime,
                            'extension': os.path.splitext(file)[1].lower(),
                            'indexed_at': time.time()
                        }
                        
                        # Add to index
                        self.file_index[file_path] = file_info
                        
                    except (OSError, PermissionError):
                        continue
                        
        except Exception as e:
            print(f"Directory indexing failed for {dir_path}: {e}")
    
    def _command_processor_loop(self):
        """Command processing loop"""
        print("Command processor started")
        
        while self.is_active:
            try:
                if not self.command_queue.empty() and len(self.active_processes) < self.max_concurrent_commands:
                    command = self.command_queue.get(timeout=1)
                    self._execute_command_with_correction(command)
                
                time.sleep(0.1)
                
            except queue.Empty:
                continue
            except Exception as e:
                print(f"Command processor error: {e}")
                time.sleep(1)
        
        print("Command processor stopped")
    
    def execute_terminal_command(self, command: str, shell: str = 'auto', 
                                timeout: int = None, admin: bool = False) -> Dict[str, Any]:
        """Execute terminal command with direct OS control"""
        try:
            # Determine shell
            if shell == 'auto':
                shell = 'powershell' if sys.platform == 'win32' else 'bash'
            
            # Prepare command
            if shell == 'powershell':
                full_command = f'powershell -Command "{command}"'
                if admin and not self.admin_privileges:
                    full_command = f'powershell -Command "Start-Process powershell -ArgumentList \'-Command {command}\' -Verb RunAs"'
            elif shell == 'cmd':
                full_command = f'cmd /c "{command}"'
                if admin and not self.admin_privileges:
                    full_command = f'powershell -Command "Start-Process cmd -ArgumentList \'/c {command}\' -Verb RunAs"'
            else:  # bash
                full_command = command
                if admin and not self.admin_privileges:
                    full_command = f'sudo {command}'
            
            # Execute command
            start_time = time.time()
            
            process = subprocess.Popen(
                full_command,
                shell=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                creationflags=subprocess.CREATE_NEW_PROCESS_GROUP if sys.platform == 'win32' else 0
            )
            
            self.active_processes[process.pid] = {
                'process': process,
                'command': command,
                'shell': shell,
                'start_time': start_time,
                'status': 'running'
            }
            
            try:
                stdout, stderr = process.communicate(timeout=timeout or self.default_timeout)
                execution_time = time.time() - start_time
                
                result = {
                    'success': process.returncode == 0,
                    'command': command,
                    'shell': shell,
                    'stdout': stdout,
                    'stderr': stderr,
                    'return_code': process.returncode,
                    'execution_time': execution_time,
                    'pid': process.pid,
                    'timestamp': datetime.now().isoformat()
                }
                
                # Update metrics
                self.commands_executed += 1
                if not result['success']:
                    self.commands_failed += 1
                
                # Remove from active processes
                if process.pid in self.active_processes:
                    del self.active_processes[process.pid]
                
                return result
                
            except subprocess.TimeoutExpired:
                process.kill()
                return {
                    'success': False,
                    'error': 'Command timed out',
                    'command': command,
                    'execution_time': timeout or self.default_timeout,
                    'timestamp': datetime.now().isoformat()
                }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'command': command,
                'timestamp': datetime.now().isoformat()
            }
    
    def _execute_command_with_correction(self, command_data: Dict[str, Any]):
        """Execute command with self-correction loop"""
        try:
            command = command_data['command']
            max_attempts = command_data.get('max_attempts', self.correction_attempts)
            shell = command_data.get('shell', 'auto')
            timeout = command_data.get('timeout', self.default_timeout)
            admin = command_data.get('admin', False)
            
            for attempt in range(max_attempts):
                # Execute command
                result = self.execute_terminal_command(command, shell, timeout, admin)
                
                if result['success']:
                    # Command succeeded
                    command_data['result'] = result
                    command_data['attempts'] = attempt + 1
                    command_data['status'] = 'success'
                    return
                else:
                    # Command failed - analyze and correct
                    if attempt < max_attempts - 1:
                        correction = self._analyze_and_correct_command(command, result)
                        if correction['corrected']:
                            command = correction['corrected_command']
                            print(f"Command corrected (attempt {attempt + 1}): {command}")
                        else:
                            break
                    else:
                        # Max attempts reached
                        command_data['result'] = result
                        command_data['attempts'] = attempt + 1
                        command_data['status'] = 'failed'
                        return
            
        except Exception as e:
            command_data['result'] = {'success': False, 'error': str(e)}
            command_data['status'] = 'error'
    
    def _analyze_and_correct_command(self, original_command: str, failed_result: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze failed command and attempt correction"""
        try:
            stderr = failed_result.get('stderr', '').lower()
            error_message = failed_result.get('error', '').lower()
            
            # Identify error type
            error_type = None
            for pattern_type, patterns in self.correction_patterns.items():
                if any(pattern in stderr or pattern in error_message for pattern in patterns):
                    error_type = pattern_type
                    break
            
            if not error_type:
                return {'corrected': False, 'reason': 'Unknown error type'}
            
            # Apply corrections based on error type
            corrected_command = original_command
            
            if error_type == 'permission_denied':
                # Add admin privileges
                if sys.platform == 'win32':
                    corrected_command = f'powershell -Command "Start-Process powershell -ArgumentList \'-Command {original_command}\' -Verb RunAs"'
                else:
                    corrected_command = f'sudo {original_command}'
            
            elif error_type == 'file_not_found':
                # Try to find the file
                if 'install' in original_command.lower():
                    # Add package manager prefix
                    if sys.platform == 'win32':
                        corrected_command = f'choco install {original_command.split()[-1]}'
                    elif 'ubuntu' in os.uname().version.lower() or 'debian' in os.uname().version.lower():
                        corrected_command = f'sudo apt-get install {original_command.split()[-1]}'
                    elif 'centos' in os.uname().version.lower() or 'rhel' in os.uname().version.lower():
                        corrected_command = f'sudo yum install {original_command.split()[-1]}'
            
            elif error_type == 'network_error':
                # Add network troubleshooting
                if 'ping' not in original_command:
                    corrected_command = f'ping google.com && {original_command}'
            
            elif error_type == 'syntax_error':
                # Fix common syntax issues
                corrected_command = original_command.strip()
                if not corrected_command.endswith(';') and sys.platform != 'win32':
                    corrected_command += ';'
            
            elif error_type == 'dependency_error':
                # Try to install missing dependencies
                if sys.platform == 'win32':
                    corrected_command = f'choco install -y {original_command.split()[-1]}'
                else:
                    corrected_command = f'sudo apt-get install -y {original_command.split()[-1]}'
            
            return {
                'corrected': corrected_command != original_command,
                'corrected_command': corrected_command,
                'error_type': error_type,
                'original_command': original_command
            }
            
        except Exception as e:
            return {'corrected': False, 'reason': f'Correction analysis failed: {str(e)}'}
    
    def autonomous_file_operation(self, voice_command: str) -> Dict[str, Any]:
        """Execute autonomous file system operation based on vague voice command"""
        try:
            # Parse voice command
            parsed = self._parse_file_command(voice_command)
            
            if not parsed['success']:
                return parsed
            
            operation = parsed['operation']
            target = parsed['target']
            destination = parsed.get('destination')
            
            # Search for files
            matching_files = self._search_files(target)
            
            if not matching_files:
                return {
                    'success': False,
                    'error': f'No files found matching: {target}',
                    'voice_command': voice_command
                }
            
            results = []
            
            # Execute operation on matching files
            for file_info in matching_files:
                file_path = file_info['path']
                
                if operation == 'find':
                    results.append({'file': file_path, 'info': file_info})
                
                elif operation == 'move' and destination:
                    try:
                        dest_path = os.path.join(destination, os.path.basename(file_path))
                        shutil.move(file_path, dest_path)
                        results.append({'moved_from': file_path, 'moved_to': dest_path})
                        self.files_managed += 1
                    except Exception as e:
                        results.append({'error': str(e), 'file': file_path})
                
                elif operation == 'copy' and destination:
                    try:
                        dest_path = os.path.join(destination, os.path.basename(file_path))
                        shutil.copy2(file_path, dest_path)
                        results.append({'copied_from': file_path, 'copied_to': dest_path})
                        self.files_managed += 1
                    except Exception as e:
                        results.append({'error': str(e), 'file': file_path})
                
                elif operation == 'delete':
                    try:
                        os.remove(file_path)
                        results.append({'deleted': file_path})
                        self.files_managed += 1
                    except Exception as e:
                        results.append({'error': str(e), 'file': file_path})
                
                elif operation == 'organize':
                    # Organize based on file type
                    self._organize_file(file_path)
                    results.append({'organized': file_path})
                    self.files_managed += 1
            
            return {
                'success': True,
                'operation': operation,
                'target': target,
                'destination': destination,
                'files_processed': len(results),
                'results': results,
                'voice_command': voice_command
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': f'Autonomous file operation failed: {str(e)}',
                'voice_command': voice_command
            }
    
    def _parse_file_command(self, voice_command: str) -> Dict[str, Any]:
        """Parse vague voice command into structured operation"""
        try:
            command_lower = voice_command.lower()
            
            # Identify operation
            operation = 'find'
            destination = None
            
            if 'move' in command_lower or 'put' in command_lower:
                operation = 'move'
                # Extract destination
                dest_match = re.search(r'to\s+([^.!?]+)', command_lower)
                if dest_match:
                    destination = dest_match.group(1).strip()
            
            elif 'copy' in command_lower:
                operation = 'copy'
                # Extract destination
                dest_match = re.search(r'to\s+([^.!?]+)', command_lower)
                if dest_match:
                    destination = dest_match.group(1).strip()
            
            elif 'delete' in command_lower or 'remove' in command_lower:
                operation = 'delete'
            
            elif 'organize' in command_lower:
                operation = 'organize'
            
            # Extract target (what to find)
            target_patterns = [
                r'find\s+(.+?)(?:\s+and|\s+to|\s+from|$)',
                r'move\s+(.+?)(?:\s+to|\s+from|$)',
                r'copy\s+(.+?)(?:\s+to|\s+from|$)',
                r'delete\s+(.+?)(?:\s+and|\s+to|\s+from|$)',
                r'organize\s+(.+?)(?:\s+and|\s+to|\s+from|$)',
                r'that\s+(.+?)(?:\s+and|\s+to|\s+from|$)',
                r'(.+?)(?:\s+from|\s+last|$)'
            ]
            
            target = None
            for pattern in target_patterns:
                match = re.search(pattern, command_lower)
                if match:
                    target = match.group(1).strip()
                    break
            
            if not target:
                return {
                    'success': False,
                    'error': 'Could not determine target from voice command',
                    'voice_command': voice_command
                }
            
            # Clean up target
            target = re.sub(r'\b(that|this|the|a|an)\b', '', target).strip()
            
            return {
                'success': True,
                'operation': operation,
                'target': target,
                'destination': destination,
                'voice_command': voice_command
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': f'Voice command parsing failed: {str(e)}',
                'voice_command': voice_command
            }
    
    def _search_files(self, target: str) -> List[Dict[str, Any]]:
        """Search files based on target description"""
        try:
            target_lower = target.lower()
            matching_files = []
            
            # Time-based search
            time_keywords = {
                'today': time.time() - 86400,
                'yesterday': time.time() - 172800,
                'last week': time.time() - 604800,
                'last month': time.time() - 2592000
            }
            
            time_threshold = None
            for keyword, threshold in time_keywords.items():
                if keyword in target_lower:
                    time_threshold = threshold
                    break
            
            # Search in file index
            for file_path, file_info in self.file_index.items():
                # Check name match
                name_match = any(word in file_info['name'].lower() for word in target_lower.split() if word not in time_keywords)
                
                # Check content match (for text files)
                content_match = False
                if not name_match and file_info['extension'] in ['.txt', '.md', '.py', '.js', '.html', '.css']:
                    try:
                        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                            content = f.read(1000).lower()  # Read first 1000 chars
                            content_match = target_lower in content
                    except:
                        pass
                
                # Check time match
                time_match = True
                if time_threshold:
                    time_match = file_info['modified'] > time_threshold
                
                if (name_match or content_match) and time_match:
                    matching_files.append(file_info)
            
            # Sort by relevance (name matches first, then by modification time)
            matching_files.sort(key=lambda x: (0 if any(word in x['name'].lower() for word in target_lower.split()) else 1, -x['modified']))
            
            return matching_files[:10]  # Return top 10 matches
            
        except Exception as e:
            print(f"File search failed: {e}")
            return []
    
    def _organize_file(self, file_path: str):
        """Organize file into appropriate directory"""
        try:
            file_info = self.file_index.get(file_path)
            if not file_info:
                return
            
            # Determine target directory based on file type
            extension = file_info['extension']
            name = file_info['name'].lower()
            
            target_dir = None
            
            if extension in ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.svg']:
                target_dir = 'Pictures'
            elif extension in ['.mp4', '.avi', '.mkv', '.mov', '.wmv']:
                target_dir = 'Videos'
            elif extension in ['.mp3', '.wav', '.flac', '.aac', '.ogg']:
                target_dir = 'Music'
            elif extension in ['.pdf', '.doc', '.docx', '.txt', '.rtf']:
                target_dir = 'Documents'
            elif extension in ['.zip', '.rar', '.7z', '.tar', '.gz']:
                target_dir = 'Archives'
            elif extension in ['.exe', '.msi', '.dmg', '.pkg']:
                target_dir = 'Applications'
            elif 'exam' in name or 'test' in name or 'study' in name:
                target_dir = 'Study'
            elif 'work' in name or 'project' in name or 'office' in name:
                target_dir = 'Work'
            else:
                target_dir = 'Other'
            
            if target_dir:
                user_home = os.path.expanduser('~')
                dest_dir = os.path.join(user_home, target_dir)
                os.makedirs(dest_dir, exist_ok=True)
                
                dest_path = os.path.join(dest_dir, file_info['name'])
                
                # Move file if not already in target directory
                if file_path != dest_path:
                    shutil.move(file_path, dest_path)
                    print(f"Organized: {file_path} -> {dest_path}")
            
        except Exception as e:
            print(f"File organization failed: {e}")
    
    def execute_command_chain(self, commands: List[str], chain_name: str = None) -> Dict[str, Any]:
        """Execute chain of commands autonomously"""
        try:
            if not chain_name:
                chain_name = f"chain_{int(time.time())}"
            
            chain_id = f"{chain_name}_{int(time.time())}"
            
            chain_info = {
                'id': chain_id,
                'name': chain_name,
                'commands': commands,
                'start_time': time.time(),
                'status': 'running',
                'results': [],
                'current_command': 0
            }
            
            self.command_chains.append(chain_info)
            
            # Execute commands sequentially
            for i, command in enumerate(commands):
                try:
                    print(f"Executing command {i+1}/{len(commands)}: {command}")
                    
                    # Submit to command queue
                    command_data = {
                        'command': command,
                        'chain_id': chain_id,
                        'chain_index': i,
                        'max_attempts': self.correction_attempts
                    }
                    
                    self.command_queue.put(command_data)
                    
                    # Wait for completion (with timeout)
                    max_wait = 120  # 2 minutes per command
                    wait_time = 0
                    
                    while wait_time < max_wait:
                        # Check if command completed
                        if command_data.get('status') in ['success', 'failed', 'error']:
                            chain_info['results'].append(command_data.get('result'))
                            break
                        
                        time.sleep(1)
                        wait_time += 1
                    
                    # Check if command failed
                    if command_data.get('status') in ['failed', 'error']:
                        chain_info['status'] = 'failed'
                        chain_info['failed_at'] = i
                        break
                
                except Exception as e:
                    chain_info['results'].append({'error': str(e)})
                    chain_info['status'] = 'error'
                    break
            
            chain_info['end_time'] = time.time()
            chain_info['execution_time'] = chain_info['end_time'] - chain_info['start_time']
            
            if chain_info['status'] == 'running':
                chain_info['status'] = 'completed'
            
            self.chain_results[chain_id] = chain_info
            
            return {
                'success': chain_info['status'] in ['completed'],
                'chain_id': chain_id,
                'chain_name': chain_name,
                'status': chain_info['status'],
                'commands_executed': len(chain_info['results']),
                'execution_time': chain_info['execution_time'],
                'results': chain_info['results']
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': f'Command chain execution failed: {str(e)}',
                'chain_name': chain_name
            }
    
    def get_system_status(self) -> Dict[str, Any]:
        """Get comprehensive system status"""
        try:
            # System information
            cpu_percent = psutil.cpu_percent(interval=1)
            memory = psutil.virtual_memory()
            disk = psutil.disk_usage('/')
            
            # Process information
            processes = list(psutil.process_iter(['pid', 'name', 'memory_percent', 'cpu_percent']))
            total_processes = len(processes)
            
            # High resource processes
            high_memory = [p for p in processes if p.info['memory_percent'] > 10]
            high_cpu = [p for p in processes if p.info['cpu_percent'] > 50]
            
            return {
                'system': {
                    'cpu_percent': cpu_percent,
                    'memory_percent': memory.percent,
                    'memory_available_gb': memory.available / (1024**3),
                    'disk_percent': disk.percent,
                    'disk_free_gb': disk.free / (1024**3)
                },
                'processes': {
                    'total': total_processes,
                    'high_memory': len(high_memory),
                    'high_cpu': len(high_cpu),
                    'problem_processes': high_memory + high_cpu
                },
                'god_mode': {
                    'is_active': self.is_active,
                    'admin_privileges': self.admin_privileges,
                    'commands_executed': self.commands_executed,
                    'commands_failed': self.commands_failed,
                    'corrections_applied': self.corrections_applied,
                    'processes_optimized': self.processes_optimized,
                    'files_managed': self.files_managed,
                    'files_indexed': len(self.file_index),
                    'active_processes': len(self.active_processes),
                    'command_chains': len(self.command_chains)
                },
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            return {
                'error': f'System status retrieval failed: {str(e)}',
                'timestamp': datetime.now().isoformat()
            }
    
    def get_status(self) -> Dict[str, Any]:
        """Get God Mode service status"""
        return {
            'is_active': self.is_active,
            'admin_privileges': self.admin_privileges,
            'commands_executed': self.commands_executed,
            'commands_failed': self.commands_failed,
            'corrections_applied': self.corrections_applied,
            'processes_optimized': self.processes_optimized,
            'files_managed': self.files_managed,
            'files_indexed': len(self.file_index),
            'active_processes': len(self.active_processes),
            'command_chains': len(self.command_chains),
            'monitored_directories': self.monitored_directories,
            'last_updated': datetime.now().isoformat()
        }
