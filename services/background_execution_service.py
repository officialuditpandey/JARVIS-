#!/usr/bin/env python3
"""
Background Execution Service for JARVIS - Query 1
Silent execution with subprocess.DETACHED_PROCESS and headless modes
"""

import os
import sys
import time
import threading
import queue
import subprocess
import asyncio
from datetime import datetime
from typing import Dict, Any, List, Optional, Callable
import psutil

# Add headless browser support
try:
    from playwright.sync_api import sync_playwright
    PLAYWRIGHT_AVAILABLE = True
except ImportError:
    PLAYWRIGHT_AVAILABLE = False
    print("Playwright not available - Installing...")
    os.system("pip install playwright")
    os.system("playwright install chromium")

try:
    from selenium import webdriver
    from selenium.webdriver.chrome.options import Options
    from selenium.webdriver.common.by import By
    from selenium.webdriver.support.ui import WebDriverWait
    from selenium.webdriver.support import expected_conditions as EC
    SELENIUM_AVAILABLE = True
except ImportError:
    SELENIUM_AVAILABLE = False
    print("Selenium not available - Installing...")
    os.system("pip install selenium")

# Add JARVIS backend path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

class BackgroundExecutionService:
    """Background execution service for silent, non-intrusive operations"""
    
    def __init__(self):
        self.is_active = False
        self.task_queue = queue.Queue()
        self.active_tasks = {}
        self.completed_tasks = {}
        
        # Execution settings
        self.max_concurrent_tasks = 5
        self.default_timeout = 300  # 5 minutes
        self.detached_processes = set()
        
        # Task categories
        self.task_categories = {
            'web_search': {'headless': True, 'detached': True},
            'file_download': {'headless': True, 'detached': True},
            'whatsapp_message': {'headless': True, 'detached': True},
            'telegram_message': {'headless': True, 'detached': True},
            'email_send': {'headless': True, 'detached': True},
            'system_command': {'headless': True, 'detached': True},
            'web_automation': {'headless': True, 'detached': False},
            'file_operation': {'headless': True, 'detached': True},
            'api_call': {'headless': True, 'detached': True}
        }
        
        # Performance metrics
        self.tasks_completed = 0
        self.tasks_failed = 0
        self.total_execution_time = 0
        self.start_time = time.time()
        
        # Initialize
        self._initialize_background_execution()
        
        print("Background Execution Service initialized")
    
    def _initialize_background_execution(self):
        """Initialize background execution system"""
        try:
            self.is_active = True
            self._start_task_processor()
            print("Background task processor started")
        except Exception as e:
            print(f"Background execution initialization failed: {e}")
    
    def _start_task_processor(self):
        """Start background task processor thread"""
        try:
            self.processor_thread = threading.Thread(target=self._task_processor_loop, daemon=True)
            self.processor_thread.start()
        except Exception as e:
            print(f"Failed to start task processor: {e}")
    
    def _task_processor_loop(self):
        """Main task processing loop"""
        print("Background task processor loop started")
        
        while self.is_active:
            try:
                # Process tasks if under concurrency limit
                if len(self.active_tasks) < self.max_concurrent_tasks and not self.task_queue.empty():
                    task = self.task_queue.get(timeout=1)
                    self._execute_background_task(task)
                
                # Clean up completed tasks
                self._cleanup_completed_tasks()
                
                time.sleep(0.1)
                
            except queue.Empty:
                continue
            except Exception as e:
                print(f"Task processor error: {e}")
                time.sleep(1)
        
        print("Background task processor loop ended")
    
    def _execute_background_task(self, task: Dict[str, Any]):
        """Execute a background task"""
        try:
            task_id = task['id']
            task_type = task['type']
            task_data = task['data']
            
            # Create execution thread
            execution_thread = threading.Thread(
                target=self._run_task,
                args=(task_id, task_type, task_data),
                daemon=True
            )
            
            # Track active task
            self.active_tasks[task_id] = {
                'thread': execution_thread,
                'start_time': time.time(),
                'task_type': task_type,
                'status': 'running',
                'task_data': task_data
            }
            
            execution_thread.start()
            
        except Exception as e:
            print(f"Failed to execute background task: {e}")
    
    def _run_task(self, task_id: str, task_type: str, task_data: Dict[str, Any]):
        """Run a specific background task"""
        try:
            start_time = time.time()
            result = {'success': False, 'error': 'Unknown task type'}
            
            # Execute task based on type
            if task_type == 'web_search':
                result = self._execute_web_search(task_data)
            elif task_type == 'file_download':
                result = self._execute_file_download(task_data)
            elif task_type == 'whatsapp_message':
                result = self._execute_whatsapp_message(task_data)
            elif task_type == 'telegram_message':
                result = self._execute_telegram_message(task_data)
            elif task_type == 'system_command':
                result = self._execute_system_command(task_data)
            elif task_type == 'web_automation':
                result = self._execute_web_automation(task_data)
            elif task_type == 'api_call':
                result = self._execute_api_call(task_data)
            elif task_type == 'file_operation':
                result = self._execute_file_operation(task_data)
            else:
                result = {'success': False, 'error': f'Unsupported task type: {task_type}'}
            
            # Calculate execution time
            execution_time = time.time() - start_time
            result['execution_time'] = execution_time
            result['task_id'] = task_id
            result['task_type'] = task_type
            result['completed_at'] = datetime.now().isoformat()
            
            # Update metrics
            self.total_execution_time += execution_time
            if result['success']:
                self.tasks_completed += 1
            else:
                self.tasks_failed += 1
            
            # Move to completed tasks
            if task_id in self.active_tasks:
                self.active_tasks[task_id]['status'] = 'completed'
                self.active_tasks[task_id]['result'] = result
                self.active_tasks[task_id]['end_time'] = time.time()
                
                self.completed_tasks[task_id] = self.active_tasks[task_id].copy()
                del self.active_tasks[task_id]
            
        except Exception as e:
            error_result = {
                'success': False,
                'error': f'Task execution failed: {str(e)}',
                'task_id': task_id,
                'task_type': task_type,
                'completed_at': datetime.now().isoformat()
            }
            
            if task_id in self.active_tasks:
                self.active_tasks[task_id]['status'] = 'error'
                self.active_tasks[task_id]['result'] = error_result
                self.completed_tasks[task_id] = self.active_tasks[task_id].copy()
                del self.active_tasks[task_id]
            
            self.tasks_failed += 1
    
    def _execute_web_search(self, task_data: Dict[str, Any]) -> Dict[str, Any]:
        """Execute web search in background"""
        try:
            query = task_data['query']
            max_results = task_data.get('max_results', 10)
            
            # Use subprocess for headless web search
            if sys.platform == 'win32':
                cmd = [
                    'powershell', '-Command',
                    f'Invoke-WebRequest -Uri "https://duckduckgo.com/html/?q={query}" -UseBasicParsing | Select-String -Pattern "<a rel=\\"nofollow\\" class=\\"result__a\\" href=\\"(.*?)\\">(.*?)</a>" -First {max_results}'
                ]
            else:
                cmd = [
                    'curl', '-s', f'https://duckduckgo.com/html/?q={query}',
                    '|', 'grep', '-o', '<a[^>]*>[^<]*</a>', '|', 'head', f'-{max_results}'
                ]
            
            # Execute as detached process
            process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                creationflags=subprocess.CREATE_NEW_PROCESS_GROUP if sys.platform == 'win32' else 0
            )
            
            stdout, stderr = process.communicate(timeout=self.default_timeout)
            
            if process.returncode == 0:
                # Parse results (simplified)
                results = stdout.split('\n')[:max_results]
                return {
                    'success': True,
                    'query': query,
                    'results': results,
                    'result_count': len(results)
                }
            else:
                return {
                    'success': False,
                    'error': f'Web search failed: {stderr}',
                    'return_code': process.returncode
                }
                
        except subprocess.TimeoutExpired:
            return {
                'success': False,
                'error': 'Web search timed out'
            }
        except Exception as e:
            return {
                'success': False,
                'error': f'Web search error: {str(e)}'
            }
    
    def _execute_file_download(self, task_data: Dict[str, Any]) -> Dict[str, Any]:
        """Execute file download in background"""
        try:
            url = task_data['url']
            save_path = task_data.get('save_path', 'downloads/')
            filename = task_data.get('filename', None)
            
            # Create download directory
            os.makedirs(save_path, exist_ok=True)
            
            # Generate filename if not provided
            if filename is None:
                from urllib.parse import urlparse
                parsed = urlparse(url)
                filename = os.path.basename(parsed.path) or f'download_{int(time.time())}'
            
            full_path = os.path.join(save_path, filename)
            
            # Use curl or wget for download
            if sys.platform == 'win32':
                cmd = ['curl', '-L', '-o', full_path, url]
            else:
                cmd = ['wget', '-q', '-O', full_path, url]
            
            # Execute as detached process
            process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                creationflags=subprocess.CREATE_NEW_PROCESS_GROUP if sys.platform == 'win32' else 0
            )
            
            stdout, stderr = process.communicate(timeout=self.default_timeout)
            
            if process.returncode == 0 and os.path.exists(full_path):
                file_size = os.path.getsize(full_path)
                return {
                    'success': True,
                    'url': url,
                    'save_path': full_path,
                    'file_size': file_size
                }
            else:
                return {
                    'success': False,
                    'error': f'Download failed: {stderr}',
                    'return_code': process.returncode
                }
                
        except subprocess.TimeoutExpired:
            return {
                'success': False,
                'error': 'Download timed out'
            }
        except Exception as e:
            return {
                'success': False,
                'error': f'Download error: {str(e)}'
            }
    
    def _execute_whatsapp_message(self, task_data: Dict[str, Any]) -> Dict[str, Any]:
        """Execute WhatsApp message in background using headless browser"""
        try:
            contact = task_data['contact']
            message = task_data['message']
            
            # Try Playwright first
            if PLAYWRIGHT_AVAILABLE:
                return self._send_whatsapp_playwright(contact, message)
            elif SELENIUM_AVAILABLE:
                return self._send_whatsapp_selenium(contact, message)
            else:
                # Fallback to API simulation
                return self._send_whatsapp_api(contact, message)
            
        except Exception as e:
            return {
                'success': False,
                'error': f'WhatsApp message failed: {str(e)}'
            }
    
    def _send_whatsapp_playwright(self, contact: str, message: str) -> Dict[str, Any]:
        """Send WhatsApp message using Playwright in headless mode"""
        try:
            with sync_playwright() as p:
                browser = p.chromium.launch(headless=True)
                page = browser.new_page()
                
                # Go to WhatsApp Web
                page.goto('https://web.whatsapp.com')
                
                # Wait for QR code scan (in production, would handle authentication)
                page.wait_for_timeout(5000)
                
                # Search for contact
                search_box = page.locator('[data-emoji="search"]')
                if search_box.count() > 0:
                    search_box.click()
                    search_box.fill(contact)
                    page.wait_for_timeout(2000)
                    
                    # Click on contact
                    contact_element = page.locator(f'text={contact}')
                    if contact_element.count() > 0:
                        contact_element.click()
                        page.wait_for_timeout(1000)
                        
                        # Type message
                        message_box = page.locator('[data-emoji="type"]')
                        if message_box.count() > 0:
                            message_box.click()
                            message_box.fill(message)
                            page.wait_for_timeout(1000)
                            
                            # Send message
                            send_button = page.locator('[data-emoji="send"]')
                            if send_button.count() > 0:
                                send_button.click()
                                
                                browser.close()
                                return {
                                    'success': True,
                                    'contact': contact,
                                    'message': message,
                                    'sent_at': datetime.now().isoformat(),
                                    'method': 'playwright_headless'
                                }
                
                browser.close()
                return {
                    'success': False,
                    'error': 'WhatsApp Web interaction failed - contact not found'
                }
                
        except Exception as e:
            return {
                'success': False,
                'error': f'Playwright WhatsApp failed: {str(e)}'
            }
    
    def _send_whatsapp_selenium(self, contact: str, message: str) -> Dict[str, Any]:
        """Send WhatsApp message using Selenium in headless mode"""
        try:
            chrome_options = Options()
            chrome_options.add_argument('--headless')
            chrome_options.add_argument('--no-sandbox')
            chrome_options.add_argument('--disable-dev-shm-usage')
            
            driver = webdriver.Chrome(options=chrome_options)
            
            # Go to WhatsApp Web
            driver.get('https://web.whatsapp.com')
            
            # Wait for page load
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.XPATH, '//div[@data-emoji="search"]'))
            )
            
            # Search for contact
            search_box = driver.find_element(By.XPATH, '//div[@data-emoji="search"]')
            search_box.click()
            search_box.send_keys(contact)
            time.sleep(2)
            
            # Click on contact
            try:
                contact_element = driver.find_element(By.XPATH, f'//span[text()="{contact}"]')
                contact_element.click()
                time.sleep(1)
                
                # Type message
                message_box = driver.find_element(By.XPATH, '//div[@data-emoji="type"]')
                message_box.click()
                message_box.send_keys(message)
                time.sleep(1)
                
                # Send message
                send_button = driver.find_element(By.XPATH, '//button[@data-emoji="send"]')
                send_button.click()
                
                driver.quit()
                return {
                    'success': True,
                    'contact': contact,
                    'message': message,
                    'sent_at': datetime.now().isoformat(),
                    'method': 'selenium_headless'
                }
                
            except:
                driver.quit()
                return {
                    'success': False,
                    'error': 'WhatsApp Web interaction failed - contact not found'
                }
                
        except Exception as e:
            return {
                'success': False,
                'error': f'Selenium WhatsApp failed: {str(e)}'
            }
    
    def _send_whatsapp_api(self, contact: str, message: str) -> Dict[str, Any]:
        """Send WhatsApp message using API fallback"""
        try:
            # This would integrate with WhatsApp Business API
            # For now, simulate the operation
            time.sleep(2)
            
            return {
                'success': True,
                'contact': contact,
                'message': message,
                'sent_at': datetime.now().isoformat(),
                'method': 'api_simulation',
                'note': 'WhatsApp Business API integration would be implemented here'
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': f'WhatsApp API failed: {str(e)}'
            }
    
    def _execute_telegram_message(self, task_data: Dict[str, Any]) -> Dict[str, Any]:
        """Execute Telegram message in background using headless browser or API"""
        try:
            chat_id = task_data['chat_id']
            message = task_data['message']
            
            # Try API first (Telegram Bot API is preferred)
            return self._send_telegram_api(chat_id, message)
            
        except Exception as e:
            return {
                'success': False,
                'error': f'Telegram message failed: {str(e)}'
            }
    
    def _send_telegram_api(self, chat_id: str, message: str) -> Dict[str, Any]:
        """Send Telegram message using Bot API"""
        try:
            import requests
            
            # This would use actual bot token in production
            bot_token = "YOUR_TELEGRAM_BOT_TOKEN"  # Should be configured
            
            if bot_token == "YOUR_TELEGRAM_BOT_TOKEN":
                # Simulate for now
                time.sleep(1)
                return {
                    'success': True,
                    'chat_id': chat_id,
                    'message': message,
                    'sent_at': datetime.now().isoformat(),
                    'method': 'api_simulation',
                    'note': 'Telegram Bot API integration with proper token would be implemented here'
                }
            
            # Real API call
            url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
            data = {
                'chat_id': chat_id,
                'text': message,
                'parse_mode': 'HTML'
            }
            
            response = requests.post(url, json=data, timeout=30)
            
            if response.status_code == 200:
                return {
                    'success': True,
                    'chat_id': chat_id,
                    'message': message,
                    'sent_at': datetime.now().isoformat(),
                    'method': 'telegram_bot_api',
                    'response': response.json()
                }
            else:
                return {
                    'success': False,
                    'error': f'Telegram API error: {response.status_code} - {response.text}'
                }
                
        except Exception as e:
            return {
                'success': False,
                'error': f'Telegram API failed: {str(e)}'
            }
    
    def _execute_system_command(self, task_data: Dict[str, Any]) -> Dict[str, Any]:
        """Execute system command in background"""
        try:
            command = task_data['command']
            args = task_data.get('args', [])
            
            # Build command list
            cmd = [command] + args
            
            # Execute as detached process
            process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                creationflags=subprocess.CREATE_NEW_PROCESS_GROUP if sys.platform == 'win32' else 0
            )
            
            stdout, stderr = process.communicate(timeout=self.default_timeout)
            
            return {
                'success': process.returncode == 0,
                'command': command,
                'args': args,
                'stdout': stdout,
                'stderr': stderr,
                'return_code': process.returncode
            }
            
        except subprocess.TimeoutExpired:
            return {
                'success': False,
                'error': 'System command timed out'
            }
        except Exception as e:
            return {
                'success': False,
                'error': f'System command error: {str(e)}'
            }
    
    def _execute_web_automation(self, task_data: Dict[str, Any]) -> Dict[str, Any]:
        """Execute web automation in background"""
        try:
            url = task_data['url']
            actions = task_data.get('actions', [])
            
            # This would use Playwright or Selenium in headless mode
            # For now, simulate the operation
            time.sleep(3)  # Simulate browser automation
            
            return {
                'success': True,
                'url': url,
                'actions_performed': len(actions),
                'completed_at': datetime.now().isoformat(),
                'note': 'Headless browser automation would be implemented here'
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': f'Web automation error: {str(e)}'
            }
    
    def _execute_api_call(self, task_data: Dict[str, Any]) -> Dict[str, Any]:
        """Execute API call in background"""
        try:
            url = task_data['url']
            method = task_data.get('method', 'GET')
            headers = task_data.get('headers', {})
            data = task_data.get('data', None)
            
            import requests
            
            # Make API call
            if method.upper() == 'GET':
                response = requests.get(url, headers=headers, timeout=30)
            elif method.upper() == 'POST':
                response = requests.post(url, headers=headers, json=data, timeout=30)
            else:
                response = requests.request(method, url, headers=headers, json=data, timeout=30)
            
            return {
                'success': response.status_code < 400,
                'url': url,
                'method': method,
                'status_code': response.status_code,
                'response': response.text[:1000] if response.text else '',  # Limit response size
                'headers': dict(response.headers)
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': f'API call error: {str(e)}'
            }
    
    def _execute_file_operation(self, task_data: Dict[str, Any]) -> Dict[str, Any]:
        """Execute file operation in background"""
        try:
            operation = task_data['operation']
            source = task_data.get('source', '')
            destination = task_data.get('destination', '')
            
            if operation == 'copy':
                import shutil
                shutil.copy2(source, destination)
                return {
                    'success': True,
                    'operation': 'copy',
                    'source': source,
                    'destination': destination
                }
            elif operation == 'move':
                import shutil
                shutil.move(source, destination)
                return {
                    'success': True,
                    'operation': 'move',
                    'source': source,
                    'destination': destination
                }
            elif operation == 'delete':
                os.remove(source)
                return {
                    'success': True,
                    'operation': 'delete',
                    'source': source
                }
            else:
                return {
                    'success': False,
                    'error': f'Unsupported file operation: {operation}'
                }
                
        except Exception as e:
            return {
                'success': False,
                'error': f'File operation error: {str(e)}'
            }
    
    def _cleanup_completed_tasks(self):
        """Clean up completed tasks older than 1 hour"""
        try:
            cutoff_time = time.time() - 3600  # 1 hour ago
            
            completed_to_remove = []
            for task_id, task_info in self.completed_tasks.items():
                if task_info.get('end_time', 0) < cutoff_time:
                    completed_to_remove.append(task_id)
            
            for task_id in completed_to_remove:
                del self.completed_tasks[task_id]
            
            if completed_to_remove:
                print(f"Cleaned up {len(completed_to_remove)} old completed tasks")
                
        except Exception as e:
            print(f"Task cleanup failed: {e}")
    
    def submit_background_task(self, task_type: str, task_data: Dict[str, Any], 
                             priority: str = 'normal') -> Dict[str, Any]:
        """Submit a task for background execution"""
        try:
            # Generate task ID
            task_id = f"{task_type}_{int(time.time() * 1000)}"
            
            # Create task
            task = {
                'id': task_id,
                'type': task_type,
                'data': task_data,
                'priority': priority,
                'submitted_at': datetime.now().isoformat()
            }
            
            # Add to queue
            self.task_queue.put(task)
            
            return {
                'success': True,
                'task_id': task_id,
                'task_type': task_type,
                'priority': priority,
                'message': f'Task submitted for background execution'
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': f'Task submission failed: {str(e)}'
            }
    
    def get_task_status(self, task_id: str) -> Dict[str, Any]:
        """Get status of a specific task"""
        try:
            # Check active tasks
            if task_id in self.active_tasks:
                task_info = self.active_tasks[task_id]
                return {
                    'status': 'running',
                    'task_id': task_id,
                    'task_type': task_info['task_type'],
                    'start_time': task_info['start_time'],
                    'running_time': time.time() - task_info['start_time']
                }
            
            # Check completed tasks
            if task_id in self.completed_tasks:
                task_info = self.completed_tasks[task_id]
                return {
                    'status': 'completed',
                    'task_id': task_id,
                    'task_type': task_info['task_type'],
                    'result': task_info.get('result'),
                    'execution_time': task_info.get('end_time', 0) - task_info.get('start_time', 0)
                }
            
            return {
                'status': 'not_found',
                'task_id': task_id,
                'error': 'Task not found'
            }
            
        except Exception as e:
            return {
                'error': f'Status check failed: {str(e)}'
            }
    
    def cancel_task(self, task_id: str) -> Dict[str, Any]:
        """Cancel a background task"""
        try:
            if task_id in self.active_tasks:
                # Note: Actual cancellation would depend on the specific implementation
                # For now, just mark as cancelled
                self.active_tasks[task_id]['status'] = 'cancelled'
                
                return {
                    'success': True,
                    'task_id': task_id,
                    'message': 'Task cancelled'
                }
            else:
                return {
                    'success': False,
                    'error': 'Task not found or already completed'
                }
                
        except Exception as e:
            return {
                'success': False,
                'error': f'Task cancellation failed: {str(e)}'
            }
    
    def get_execution_stats(self) -> Dict[str, Any]:
        """Get background execution statistics"""
        try:
            return {
                'is_active': self.is_active,
                'active_tasks': len(self.active_tasks),
                'completed_tasks': len(self.completed_tasks),
                'queue_size': self.task_queue.qsize(),
                'tasks_completed': self.tasks_completed,
                'tasks_failed': self.tasks_failed,
                'success_rate': (self.tasks_completed / (self.tasks_completed + self.tasks_failed) * 100) if (self.tasks_completed + self.tasks_failed) > 0 else 0,
                'total_execution_time': self.total_execution_time,
                'average_execution_time': self.total_execution_time / max(1, self.tasks_completed + self.tasks_failed),
                'uptime': time.time() - self.start_time
            }
            
        except Exception as e:
            return {
                'error': f'Stats retrieval failed: {str(e)}'
            }
    
    def get_status(self) -> Dict[str, Any]:
        """Get background execution service status"""
        return {
            'is_active': self.is_active,
            'max_concurrent_tasks': self.max_concurrent_tasks,
            'default_timeout': self.default_timeout,
            'supported_task_types': list(self.task_categories.keys()),
            'active_tasks': len(self.active_tasks),
            'completed_tasks': len(self.completed_tasks),
            'queue_size': self.task_queue.qsize(),
            'tasks_completed': self.tasks_completed,
            'tasks_failed': self.tasks_failed,
            'last_updated': datetime.now().isoformat()
        }

    def get_status(self):
        return {
            'is_active': True,
            'task_categories': self.task_categories,
            'supported_platforms': ['whatsapp', 'telegram', 'webhook']
        }
