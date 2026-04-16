#!/usr/bin/env python3
"""
Failure Transparency Service for JARVIS
Voice-explain exact failure reasons for transparency
"""

import os
import sys
import time
import json
import traceback
import logging
from datetime import datetime
from typing import Dict, Any, List, Optional, Tuple
import threading
import queue

# Add JARVIS backend path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

class FailureTransparencyService:
    """Failure Transparency service for detailed error reporting"""
    
    def __init__(self):
        self.is_active = False
        self.failure_queue = queue.Queue()
        self.failure_history = []
        self.failure_patterns = {}
        
        # Voice synthesis
        self.voice_enabled = True
        self.voice_speed = 1.0
        self.voice_volume = 0.8
        
        # Logging configuration
        self.log_file = 'failure_transparency.log'
        self.max_history = 1000
        
        # Failure categories
        self.failure_categories = {
            'network': ['ConnectionError', 'TimeoutError', 'HTTPError', 'URLError'],
            'file_system': ['FileNotFoundError', 'PermissionError', 'OSError', 'IOError'],
            'memory': ['MemoryError', 'OutOfMemoryError'],
            'syntax': ['SyntaxError', 'IndentationError', 'TabError'],
            'type': ['TypeError', 'AttributeError', 'KeyError', 'IndexError', 'ValueError'],
            'import': ['ImportError', 'ModuleNotFoundError'],
            'authentication': ['AuthenticationError', 'PermissionDenied'],
            'api': ['ApiError', 'RateLimitError', 'InvalidResponse'],
            'system': ['SystemError', 'RuntimeError', 'KeyboardInterrupt']
        }
        
        # Explanation templates
        self.explanation_templates = {
            'ConnectionError': "I cannot connect to the network or server. This might be due to internet connectivity issues, server downtime, or incorrect network settings.",
            'TimeoutError': "The operation took too long to complete. This could be due to slow network, heavy processing, or server overload.",
            'FileNotFoundError': "I cannot find the specified file or directory. The file might have been moved, deleted, or the path is incorrect.",
            'PermissionError': "I don't have permission to access this file or perform this operation. You may need to run as administrator or check file permissions.",
            'MemoryError': "I've run out of memory. This happens when processing large files or running memory-intensive operations.",
            'SyntaxError': "There's a syntax error in the code. This could be missing brackets, incorrect indentation, or invalid Python syntax.",
            'TypeError': "I'm trying to use an operation on an incompatible data type. For example, trying to add text to a number.",
            'KeyError': "I'm trying to access a dictionary key that doesn't exist. The key might be misspelled or not present in the data.",
            'IndexError': "I'm trying to access a list index that's out of range. The index is larger than the list size.",
            'ImportError': "I cannot import a required module. The module might not be installed or the import path is incorrect.",
            'AuthenticationError': "I cannot authenticate with the service. The credentials might be incorrect or expired.",
            'ApiError': "The API returned an error. This could be due to invalid parameters, rate limits, or service issues."
        }
        
        # Initialize logging
        self._initialize_logging()
        
        # Start failure processing thread
        self._start_failure_processor()
        
        print("Failure Transparency Service initialized")
    
    def _initialize_logging(self):
        """Initialize logging system"""
        try:
            # Create logger
            self.logger = logging.getLogger('FailureTransparency')
            self.logger.setLevel(logging.DEBUG)
            
            # Create file handler
            file_handler = logging.FileHandler(self.log_file)
            file_handler.setLevel(logging.DEBUG)
            
            # Create console handler
            console_handler = logging.StreamHandler()
            console_handler.setLevel(logging.INFO)
            
            # Create formatter
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
            file_handler.setFormatter(formatter)
            console_handler.setFormatter(formatter)
            
            # Add handlers to logger
            self.logger.addHandler(file_handler)
            self.logger.addHandler(console_handler)
            
        except Exception as e:
            print(f"Logging initialization failed: {e}")
    
    def _start_failure_processor(self):
        """Start failure processing thread"""
        try:
            self.is_active = True
            self.processor_thread = threading.Thread(target=self._failure_processor_loop, daemon=True)
            self.processor_thread.start()
            print("Failure processor started")
        except Exception as e:
            print(f"Failed to start failure processor: {e}")
    
    def _failure_processor_loop(self):
        """Main failure processing loop"""
        while self.is_active:
            try:
                # Get failure from queue
                failure = self.failure_queue.get(timeout=1)
                self._process_failure(failure)
                self.failure_queue.task_done()
            except queue.Empty:
                continue
            except Exception as e:
                print(f"Failure processor error: {e}")
                time.sleep(1)
    
    def _process_failure(self, failure: Dict[str, Any]):
        """Process a failure and generate explanation"""
        try:
            # Extract failure details
            exception_type = failure.get('exception_type', 'Unknown')
            error_message = failure.get('error_message', 'No message available')
            context = failure.get('context', {})
            timestamp = failure.get('timestamp', datetime.now().isoformat())
            
            # Generate detailed explanation
            explanation = self._generate_detailed_explanation(exception_type, error_message, context)
            
            # Add to history
            failure_entry = {
                'timestamp': timestamp,
                'exception_type': exception_type,
                'error_message': error_message,
                'context': context,
                'explanation': explanation,
                'category': self._categorize_failure(exception_type)
            }
            
            self.failure_history.append(failure_entry)
            
            # Keep only recent failures
            if len(self.failure_history) > self.max_history:
                self.failure_history = self.failure_history[-self.max_history:]
            
            # Log failure
            self.logger.error(f"Failure: {exception_type}: {error_message}")
            self.logger.info(f"Explanation: {explanation}")
            
            # Voice explanation
            if self.voice_enabled:
                self._voice_explain_failure(explanation)
            
            # Update failure patterns
            self._update_failure_patterns(exception_type, context)
            
        except Exception as e:
            print(f"Failure processing error: {e}")
    
    def _generate_detailed_explanation(self, exception_type: str, error_message: str, context: Dict[str, Any]) -> str:
        """Generate detailed explanation for failure"""
        try:
            # Base explanation from template
            base_explanation = self.explanation_templates.get(exception_type, 
                f"An unexpected error occurred: {exception_type}. {error_message}")
            
            # Add context-specific details
            context_details = self._extract_context_details(exception_type, context)
            
            # Add troubleshooting steps
            troubleshooting = self._generate_troubleshooting_steps(exception_type, context)
            
            # Combine all parts
            full_explanation = f"{base_explanation}"
            
            if context_details:
                full_explanation += f" {context_details}"
            
            if troubleshooting:
                full_explanation += f" {troubleshooting}"
            
            return full_explanation
            
        except Exception as e:
            return f"Failed to generate explanation: {str(e)}"
    
    def _extract_context_details(self, exception_type: str, context: Dict[str, Any]) -> str:
        """Extract relevant context details"""
        try:
            details = []
            
            # File-related errors
            if exception_type in ['FileNotFoundError', 'PermissionError', 'OSError', 'IOError']:
                if 'file_path' in context:
                    details.append(f"The problematic file is: {context['file_path']}")
                if 'operation' in context:
                    details.append(f"I was trying to: {context['operation']}")
            
            # Network-related errors
            if exception_type in ['ConnectionError', 'TimeoutError', 'HTTPError', 'URLError']:
                if 'url' in context:
                    details.append(f"The problematic URL is: {context['url']}")
                if 'service' in context:
                    details.append(f"The affected service is: {context['service']}")
            
            # Data-related errors
            if exception_type in ['KeyError', 'IndexError', 'TypeError', 'ValueError']:
                if 'data_structure' in context:
                    details.append(f"The problematic data structure is: {context['data_structure']}")
                if 'operation' in context:
                    details.append(f"I was performing: {context['operation']}")
            
            return " ".join(details) if details else ""
            
        except:
            return ""
    
    def _generate_troubleshooting_steps(self, exception_type: str, context: Dict[str, Any]) -> str:
        """Generate troubleshooting steps"""
        try:
            steps = []
            
            # Network issues
            if exception_type in ['ConnectionError', 'TimeoutError']:
                steps.extend([
                    "Check your internet connection",
                    "Verify the server is accessible",
                    "Try again in a few moments"
                ])
            
            # File system issues
            if exception_type in ['FileNotFoundError', 'PermissionError']:
                steps.extend([
                    "Verify the file path is correct",
                    "Check if you have the necessary permissions",
                    "Ensure the file exists and is not locked"
                ])
            
            # Memory issues
            if exception_type in ['MemoryError', 'OutOfMemoryError']:
                steps.extend([
                    "Close unnecessary applications",
                    "Try processing smaller chunks of data",
                    "Restart the system if needed"
                ])
            
            # Syntax and type errors
            if exception_type in ['SyntaxError', 'TypeError', 'AttributeError']:
                steps.extend([
                    "Review the code for syntax errors",
                    "Check variable types and names",
                    "Verify all brackets and quotes are properly matched"
                ])
            
            # Import errors
            if exception_type in ['ImportError', 'ModuleNotFoundError']:
                steps.extend([
                    "Install the missing module using pip",
                    "Check the module name and spelling",
                    "Verify the module is in the Python path"
                ])
            
            return "To fix this: " + "; ".join(steps) + "." if steps else ""
            
        except:
            return ""
    
    def _categorize_failure(self, exception_type: str) -> str:
        """Categorize failure type"""
        try:
            for category, exceptions in self.failure_categories.items():
                if exception_type in exceptions:
                    return category
            return 'unknown'
        except:
            return 'unknown'
    
    def _update_failure_patterns(self, exception_type: str, context: Dict[str, Any]):
        """Update failure patterns for analysis"""
        try:
            if exception_type not in self.failure_patterns:
                self.failure_patterns[exception_type] = {
                    'count': 0,
                    'first_occurrence': datetime.now().isoformat(),
                    'last_occurrence': datetime.now().isoformat(),
                    'contexts': []
                }
            
            pattern = self.failure_patterns[exception_type]
            pattern['count'] += 1
            pattern['last_occurrence'] = datetime.now().isoformat()
            
            # Store context for analysis
            if len(pattern['contexts']) < 10:
                pattern['contexts'].append(context)
            
        except Exception as e:
            print(f"Failed to update failure patterns: {e}")
    
    def _voice_explain_failure(self, explanation: str):
        """Voice explain the failure"""
        try:
            # This would integrate with JARVIS voice system
            # For now, just print the explanation
            print(f"VOICE EXPLANATION: {explanation}")
            
            # In production, this would call:
            # jarvis.speak(explanation, speed=self.voice_speed, volume=self.voice_volume)
            
        except Exception as e:
            print(f"Voice explanation failed: {e}")
    
    def report_failure(self, exception: Exception, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """Report a failure for processing"""
        try:
            if context is None:
                context = {}
            
            # Get exception details
            exception_type = type(exception).__name__
            error_message = str(exception)
            traceback_info = traceback.format_exc()
            
            # Create failure report
            failure = {
                'exception_type': exception_type,
                'error_message': error_message,
                'traceback': traceback_info,
                'context': context,
                'timestamp': datetime.now().isoformat()
            }
            
            # Add to queue for processing
            self.failure_queue.put(failure)
            
            return {
                'success': True,
                'failure_id': f"{exception_type}_{int(time.time())}",
                'message': 'Failure reported and will be explained'
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': f'Failed to report failure: {str(e)}'
            }
    
    def get_failure_analysis(self) -> Dict[str, Any]:
        """Get failure analysis and patterns"""
        try:
            # Calculate failure statistics
            total_failures = len(self.failure_history)
            category_counts = {}
            type_counts = {}
            
            for failure in self.failure_history:
                category = failure.get('category', 'unknown')
                exception_type = failure.get('exception_type', 'unknown')
                
                category_counts[category] = category_counts.get(category, 0) + 1
                type_counts[exception_type] = type_counts.get(exception_type, 0) + 1
            
            # Get most common failures
            most_common_category = max(category_counts.items(), key=lambda x: x[1]) if category_counts else ('unknown', 0)
            most_common_type = max(type_counts.items(), key=lambda x: x[1]) if type_counts else ('unknown', 0)
            
            return {
                'total_failures': total_failures,
                'category_distribution': category_counts,
                'type_distribution': type_counts,
                'most_common_category': most_common_category,
                'most_common_type': most_common_type,
                'failure_patterns': self.failure_patterns,
                'recent_failures': self.failure_history[-10:] if self.failure_history else []
            }
            
        except Exception as e:
            return {
                'error': f'Failure analysis failed: {str(e)}'
            }
    
    def get_failure_history(self, limit: int = 50, category: str = None) -> List[Dict[str, Any]]:
        """Get failure history"""
        try:
            history = self.failure_history
            
            # Filter by category if specified
            if category:
                history = [f for f in history if f.get('category') == category]
            
            return history[-limit:] if history else []
            
        except Exception as e:
            print(f"Failed to get failure history: {e}")
            return []
    
    def clear_failure_history(self, older_than_hours: int = 24) -> Dict[str, Any]:
        """Clear failure history older than specified hours"""
        try:
            cutoff_time = datetime.now() - timedelta(hours=older_than_hours)
            
            original_count = len(self.failure_history)
            self.failure_history = [
                f for f in self.failure_history 
                if datetime.fromisoformat(f['timestamp']) > cutoff_time
            ]
            
            cleared_count = original_count - len(self.failure_history)
            
            return {
                'success': True,
                'cleared_count': cleared_count,
                'remaining_count': len(self.failure_history),
                'message': f'Cleared {cleared_count} failures older than {older_than_hours} hours'
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': f'Failed to clear failure history: {str(e)}'
            }
    
    def set_voice_settings(self, enabled: bool = None, speed: float = None, volume: float = None):
        """Set voice explanation settings"""
        try:
            if enabled is not None:
                self.voice_enabled = enabled
            
            if speed is not None:
                self.voice_speed = max(0.5, min(2.0, speed))
            
            if volume is not None:
                self.voice_volume = max(0.0, min(1.0, volume))
            
            return {
                'success': True,
                'voice_enabled': self.voice_enabled,
                'voice_speed': self.voice_speed,
                'voice_volume': self.voice_volume
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': f'Failed to set voice settings: {str(e)}'
            }
    
    def explain_error(self, error_text: str) -> Dict[str, Any]:
        """Explain an error from text"""
        try:
            # Try to extract exception type from error text
            exception_type = 'Unknown'
            for exc_type in self.explanation_templates.keys():
                if exc_type in error_text:
                    exception_type = exc_type
                    break
            
            # Generate explanation
            explanation = self._generate_detailed_explanation(exception_type, error_text, {})
            
            return {
                'success': True,
                'exception_type': exception_type,
                'error_text': error_text,
                'explanation': explanation
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': f'Error explanation failed: {str(e)}'
            }
    
    def get_status(self) -> Dict[str, Any]:
        """Get failure transparency service status"""
        return {
            'is_active': self.is_active,
            'voice_enabled': self.voice_enabled,
            'voice_speed': self.voice_speed,
            'voice_volume': self.voice_volume,
            'failure_queue_size': self.failure_queue.qsize(),
            'failure_history_count': len(self.failure_history),
            'failure_patterns_count': len(self.failure_patterns),
            'log_file': self.log_file,
            'last_updated': datetime.now().isoformat()
        }
    
    def stop_service(self):
        """Stop the failure transparency service"""
        try:
            self.is_active = False
            if hasattr(self, 'processor_thread') and self.processor_thread.is_alive():
                self.processor_thread.join(timeout=2)
            print("Failure Transparency Service stopped")
        except Exception as e:
            print(f"Failed to stop service: {e}")
