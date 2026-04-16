#!/usr/bin/env python3
"""
CMD Downloader Service for JARVIS
Download files directly via terminal (curl/wget) without opening a browser
"""

import os
import sys
import time
import subprocess
import threading
import json
import hashlib
from datetime import datetime
from typing import Dict, Any, List, Optional, Tuple
from urllib.parse import urlparse
import requests

# Add JARVIS backend path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

class CMDDownloaderService:
    """CMD Downloader service for terminal-based downloads"""
    
    def __init__(self):
        self.is_active = False
        self.download_queue = []
        self.active_downloads = {}
        self.download_history = []
        
        # Download settings
        self.default_timeout = 300  # 5 minutes
        self.max_concurrent_downloads = 3
        self.chunk_size = 8192
        self.retry_attempts = 3
        
        # Download directory
        if sys.platform == 'win32':
            self.download_dir = os.path.join(os.path.expanduser('~'), 'Downloads', 'Jarvis_Downloads')
        else:
            self.download_dir = os.path.join(os.path.expanduser('~'), 'Downloads', 'Jarvis_Downloads')
        os.makedirs(self.download_dir, exist_ok=True)
        
        # Supported methods
        self.download_methods = {
            'requests': True,  # Python requests library
            'curl': self._check_command('curl'),
            'wget': self._check_command('wget'),
            'powershell': self._check_command('powershell') if sys.platform == 'win32' else False
        }
        
        # Performance metrics
        self.total_downloaded = 0
        self.successful_downloads = 0
        self.failed_downloads = 0
        self.bytes_downloaded = 0
        self.start_time = time.time()
        
        # Start download processor
        self._start_download_processor()
        
        print("CMD Downloader Service initialized")
    
    def _check_command(self, command: str) -> bool:
        """Check if command is available"""
        try:
            result = subprocess.run(['where', command] if sys.platform == 'win32' else ['which', command],
                                   capture_output=True, text=True, timeout=5)
            return result.returncode == 0
        except:
            return False
    
    def _start_download_processor(self):
        """Start download processing thread"""
        try:
            self.is_active = True
            self.processor_thread = threading.Thread(target=self._download_processor_loop, daemon=True)
            self.processor_thread.start()
            print("Download processor started")
        except Exception as e:
            print(f"Failed to start download processor: {e}")
    
    def _download_processor_loop(self):
        """Main download processing loop"""
        while self.is_active:
            try:
                # Process downloads
                if len(self.active_downloads) < self.max_concurrent_downloads and self.download_queue:
                    download_task = self.download_queue.pop(0)
                    self._start_download(download_task)
                
                time.sleep(1)
                
            except Exception as e:
                print(f"Download processor error: {e}")
                time.sleep(5)
    
    def _start_download(self, download_task: Dict[str, Any]):
        """Start a download in a separate thread"""
        try:
            download_id = download_task['id']
            url = download_task['url']
            save_path = download_task['save_path']
            method = download_task.get('method', 'auto')
            
            # Create download thread
            thread = threading.Thread(
                target=self._execute_download,
                args=(download_id, url, save_path, method, download_task),
                daemon=True
            )
            
            # Track active download
            self.active_downloads[download_id] = {
                'thread': thread,
                'start_time': time.time(),
                'status': 'starting',
                'task': download_task
            }
            
            thread.start()
            
        except Exception as e:
            print(f"Failed to start download: {e}")
    
    def _execute_download(self, download_id: str, url: str, save_path: str, 
                         method: str, download_task: Dict[str, Any]):
        """Execute the download"""
        try:
            # Update status
            if download_id in self.active_downloads:
                self.active_downloads[download_id]['status'] = 'downloading'
            
            # Choose download method
            if method == 'auto':
                method = self._choose_best_method(url)
            
            # Execute download
            if method == 'requests':
                result = self._download_with_requests(url, save_path, download_task)
            elif method == 'curl':
                result = self._download_with_curl(url, save_path, download_task)
            elif method == 'wget':
                result = self._download_with_wget(url, save_path, download_task)
            elif method == 'powershell':
                result = self._download_with_powershell(url, save_path, download_task)
            else:
                result = {'success': False, 'error': f'Unsupported method: {method}'}
            
            # Update download status
            if download_id in self.active_downloads:
                self.active_downloads[download_id]['status'] = 'completed'
                self.active_downloads[download_id]['result'] = result
            
            # Add to history
            history_entry = {
                'id': download_id,
                'url': url,
                'save_path': save_path,
                'method': method,
                'start_time': self.active_downloads[download_id]['start_time'],
                'end_time': time.time(),
                'result': result
            }
            
            self.download_history.append(history_entry)
            
            # Keep only last 100 downloads
            if len(self.download_history) > 100:
                self.download_history = self.download_history[-100:]
            
            # Update metrics
            if result.get('success', False):
                self.successful_downloads += 1
                self.bytes_downloaded += result.get('file_size', 0)
            else:
                self.failed_downloads += 1
            
            self.total_downloaded += 1
            
            # Remove from active downloads
            if download_id in self.active_downloads:
                del self.active_downloads[download_id]
            
        except Exception as e:
            # Handle download error
            if download_id in self.active_downloads:
                self.active_downloads[download_id]['status'] = 'error'
                self.active_downloads[download_id]['error'] = str(e)
            
            self.failed_downloads += 1
            self.total_downloaded += 1
            
            if download_id in self.active_downloads:
                del self.active_downloads[download_id]
    
    def _choose_best_method(self, url: str) -> str:
        """Choose the best download method for the URL"""
        try:
            # Prefer requests for most cases
            if self.download_methods['requests']:
                return 'requests'
            
            # Fall back to system tools
            if sys.platform == 'win32':
                if self.download_methods['powershell']:
                    return 'powershell'
                elif self.download_methods['curl']:
                    return 'curl'
            else:
                if self.download_methods['wget']:
                    return 'wget'
                elif self.download_methods['curl']:
                    return 'curl'
            
            return 'requests'
            
        except:
            return 'requests'
    
    def _download_with_requests(self, url: str, save_path: str, download_task: Dict[str, Any]) -> Dict[str, Any]:
        """Download using Python requests library"""
        try:
            # Parse URL
            parsed_url = urlparse(url)
            
            # Create session
            session = requests.Session()
            
            # Set headers
            headers = download_task.get('headers', {})
            headers.update({
                'User-Agent': 'JARVIS-Downloader/1.0'
            })
            
            # Start download
            response = session.get(url, headers=headers, stream=True, timeout=self.default_timeout)
            response.raise_for_status()
            
            # Get file size
            total_size = int(response.headers.get('content-length', 0))
            
            # Create directory if needed
            os.makedirs(os.path.dirname(save_path), exist_ok=True)
            
            # Download file
            downloaded_size = 0
            with open(save_path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=self.chunk_size):
                    if chunk:
                        f.write(chunk)
                        downloaded_size += len(chunk)
            
            # Verify download
            if os.path.exists(save_path):
                actual_size = os.path.getsize(save_path)
                
                return {
                    'success': True,
                    'method': 'requests',
                    'file_size': actual_size,
                    'expected_size': total_size,
                    'save_path': save_path,
                    'download_time': time.time() - time.time(),
                    'url': url
                }
            else:
                return {
                    'success': False,
                    'error': 'File not saved properly'
                }
                
        except Exception as e:
            return {
                'success': False,
                'error': f'Requests download failed: {str(e)}'
            }
    
    def _download_with_curl(self, url: str, save_path: str, download_task: Dict[str, Any]) -> Dict[str, Any]:
        """Download using curl command"""
        try:
            # Create directory if needed
            os.makedirs(os.path.dirname(save_path), exist_ok=True)
            
            # Build curl command
            cmd = ['curl', '-L', '-o', save_path, url]
            
            # Add custom headers if provided
            headers = download_task.get('headers', {})
            for header, value in headers.items():
                cmd.extend(['-H', f'{header}: {value}'])
            
            # Add timeout
            cmd.extend(['--max-time', str(self.default_timeout)])
            
            # Add user agent
            cmd.extend(['-A', 'JARVIS-Downloader/1.0'])
            
            # Execute curl
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=self.default_timeout + 60)
            
            if result.returncode == 0 and os.path.exists(save_path):
                file_size = os.path.getsize(save_path)
                
                return {
                    'success': True,
                    'method': 'curl',
                    'file_size': file_size,
                    'save_path': save_path,
                    'download_time': time.time() - time.time(),
                    'url': url,
                    'curl_output': result.stdout
                }
            else:
                return {
                    'success': False,
                    'error': f'Curl failed: {result.stderr}',
                    'return_code': result.returncode
                }
                
        except Exception as e:
            return {
                'success': False,
                'error': f'Curl download failed: {str(e)}'
            }
    
    def _download_with_wget(self, url: str, save_path: str, download_task: Dict[str, Any]) -> Dict[str, Any]:
        """Download using wget command"""
        try:
            # Create directory if needed
            os.makedirs(os.path.dirname(save_path), exist_ok=True)
            
            # Build wget command
            cmd = ['wget', '-O', save_path, url]
            
            # Add timeout
            cmd.extend(['--timeout', str(self.default_timeout)])
            
            # Add user agent
            cmd.extend(['--user-agent', 'JARVIS-Downloader/1.0'])
            
            # Add custom headers if provided
            headers = download_task.get('headers', {})
            for header, value in headers.items():
                cmd.extend(['--header', f'{header}: {value}'])
            
            # Execute wget
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=self.default_timeout + 60)
            
            if result.returncode == 0 and os.path.exists(save_path):
                file_size = os.path.getsize(save_path)
                
                return {
                    'success': True,
                    'method': 'wget',
                    'file_size': file_size,
                    'save_path': save_path,
                    'download_time': time.time() - time.time(),
                    'url': url,
                    'wget_output': result.stdout
                }
            else:
                return {
                    'success': False,
                    'error': f'Wget failed: {result.stderr}',
                    'return_code': result.returncode
                }
                
        except Exception as e:
            return {
                'success': False,
                'error': f'Wget download failed: {str(e)}'
            }
    
    def _download_with_powershell(self, url: str, save_path: str, download_task: Dict[str, Any]) -> Dict[str, Any]:
        """Download using PowerShell Invoke-WebRequest"""
        try:
            # Create directory if needed
            os.makedirs(os.path.dirname(save_path), exist_ok=True)
            
            # Build PowerShell command
            ps_script = f"""
            Invoke-WebRequest -Uri "{url}" -OutFile "{save_path}" -TimeoutSec {self.default_timeout} -UserAgent "JARVIS-Downloader/1.0"
            """
            
            # Execute PowerShell
            result = subprocess.run(
                ['powershell', '-Command', ps_script],
                capture_output=True,
                text=True,
                timeout=self.default_timeout + 60
            )
            
            if result.returncode == 0 and os.path.exists(save_path):
                file_size = os.path.getsize(save_path)
                
                return {
                    'success': True,
                    'method': 'powershell',
                    'file_size': file_size,
                    'save_path': save_path,
                    'download_time': time.time() - time.time(),
                    'url': url,
                    'powershell_output': result.stdout
                }
            else:
                return {
                    'success': False,
                    'error': f'PowerShell failed: {result.stderr}',
                    'return_code': result.returncode
                }
                
        except Exception as e:
            return {
                'success': False,
                'error': f'PowerShell download failed: {str(e)}'
            }
    
    def download_file(self, url: str, save_path: str = None, method: str = 'auto',
                     headers: Dict[str, str] = None, overwrite: bool = False) -> Dict[str, Any]:
        """Download a file"""
        try:
            # Validate URL
            if not url or not url.startswith(('http://', 'https://')):
                return {
                    'success': False,
                    'error': 'Invalid URL provided'
                }
            
            # Generate save path if not provided
            if save_path is None:
                filename = self._extract_filename(url)
                save_path = os.path.join(self.download_dir, filename)
            
            # Check if file exists
            if os.path.exists(save_path) and not overwrite:
                return {
                    'success': False,
                    'error': f'File already exists: {save_path}. Use overwrite=True to replace.'
                }
            
            # Generate download ID
            download_id = hashlib.md5(f"{url}_{time.time()}".encode()).hexdigest()[:16]
            
            # Create download task
            download_task = {
                'id': download_id,
                'url': url,
                'save_path': save_path,
                'method': method,
                'headers': headers or {},
                'overwrite': overwrite,
                'queued_at': time.time()
            }
            
            # Add to queue
            self.download_queue.append(download_task)
            
            return {
                'success': True,
                'download_id': download_id,
                'url': url,
                'save_path': save_path,
                'method': method,
                'message': f'Download queued: {download_id}'
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': f'Download failed: {str(e)}'
            }
    
    def _extract_filename(self, url: str) -> str:
        """Extract filename from URL"""
        try:
            parsed = urlparse(url)
            filename = os.path.basename(parsed.path)
            
            if not filename or '.' not in filename:
                # Generate filename from URL hash
                filename = f"download_{hashlib.md5(url.encode()).hexdigest()[:8]}"
            
            return filename
            
        except:
            return f"download_{int(time.time())}"
    
    def get_download_status(self, download_id: str) -> Dict[str, Any]:
        """Get status of a specific download"""
        try:
            # Check active downloads
            if download_id in self.active_downloads:
                active = self.active_downloads[download_id]
                return {
                    'status': active['status'],
                    'download_id': download_id,
                    'start_time': active['start_time'],
                    'elapsed_time': time.time() - active['start_time'],
                    'task': active['task']
                }
            
            # Check download history
            for entry in self.download_history:
                if entry['id'] == download_id:
                    return {
                        'status': 'completed',
                        'download_id': download_id,
                        'result': entry['result'],
                        'download_time': entry['end_time'] - entry['start_time']
                    }
            
            return {
                'status': 'not_found',
                'download_id': download_id,
                'error': 'Download not found'
            }
            
        except Exception as e:
            return {
                'error': f'Status check failed: {str(e)}'
            }
    
    def cancel_download(self, download_id: str) -> Dict[str, Any]:
        """Cancel a download"""
        try:
            if download_id in self.active_downloads:
                # Remove from active downloads
                del self.active_downloads[download_id]
                
                # Remove from queue if present
                self.download_queue = [task for task in self.download_queue if task['id'] != download_id]
                
                return {
                    'success': True,
                    'download_id': download_id,
                    'message': 'Download cancelled'
                }
            else:
                return {
                    'success': False,
                    'error': 'Download not found or already completed'
                }
                
        except Exception as e:
            return {
                'success': False,
                'error': f'Cancel failed: {str(e)}'
            }
    
    def get_download_history(self, limit: int = 50) -> List[Dict[str, Any]]:
        """Get download history"""
        return self.download_history[-limit:] if self.download_history else []
    
    def get_active_downloads(self) -> Dict[str, Any]:
        """Get information about active downloads"""
        try:
            active_info = {}
            for download_id, active in self.active_downloads.items():
                active_info[download_id] = {
                    'status': active['status'],
                    'start_time': active['start_time'],
                    'elapsed_time': time.time() - active['start_time'],
                    'url': active['task']['url'],
                    'save_path': active['task']['save_path'],
                    'method': active['task']['method']
                }
            
            return {
                'active_downloads': active_info,
                'queue_size': len(self.download_queue),
                'max_concurrent': self.max_concurrent_downloads
            }
            
        except Exception as e:
            return {
                'error': f'Failed to get active downloads: {str(e)}'
            }
    
    def get_download_stats(self) -> Dict[str, Any]:
        """Get download statistics"""
        try:
            return {
                'total_downloads': self.total_downloaded,
                'successful_downloads': self.successful_downloads,
                'failed_downloads': self.failed_downloads,
                'bytes_downloaded': self.bytes_downloaded,
                'success_rate': (self.successful_downloads / self.total_downloaded * 100) if self.total_downloaded > 0 else 0,
                'average_speed': self.bytes_downloaded / (time.time() - self.start_time) if time.time() - self.start_time > 0 else 0,
                'download_methods': self.download_methods,
                'download_directory': self.download_dir
            }
            
        except Exception as e:
            return {
                'error': f'Stats retrieval failed: {str(e)}'
            }
    
    def clear_download_history(self, older_than_hours: int = 24) -> Dict[str, Any]:
        """Clear download history older than specified hours"""
        try:
            cutoff_time = time.time() - (older_than_hours * 3600)
            
            original_count = len(self.download_history)
            self.download_history = [
                entry for entry in self.download_history 
                if entry['end_time'] > cutoff_time
            ]
            
            cleared_count = original_count - len(self.download_history)
            
            return {
                'success': True,
                'cleared_count': cleared_count,
                'remaining_count': len(self.download_history),
                'message': f'Cleared {cleared_count} downloads older than {older_than_hours} hours'
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': f'Failed to clear history: {str(e)}'
            }
    
    def get_status(self) -> Dict[str, Any]:
        """Get downloader service status"""
        return {
            'is_active': self.is_active,
            'download_queue_size': len(self.download_queue),
            'active_downloads': len(self.active_downloads),
            'download_methods': self.download_methods,
            'download_directory': self.download_dir,
            'total_downloads': self.total_downloaded,
            'successful_downloads': self.successful_downloads,
            'failed_downloads': self.failed_downloads,
            'bytes_downloaded': self.bytes_downloaded,
            'last_updated': datetime.now().isoformat()
        }
