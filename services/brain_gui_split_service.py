#!/usr/bin/env python3
"""
Brain vs GUI Split Service for JARVIS
Heavy AI processing in Terminal, Results in GUI for thermal optimization
"""

import os
import sys
import time
import threading
import queue
import json
from datetime import datetime
from typing import Dict, Any, List, Optional, Callable
import psutil
import subprocess

# Add JARVIS backend path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

class BrainGUISplitService:
    """Brain vs GUI split service for thermal optimization"""
    
    def __init__(self):
        self.is_active = False
        self.brain_queue = queue.Queue()
        self.gui_results = {}
        self.processing_threads = {}
        
        # Thermal management
        self.cpu_threshold = 70.0  # CPU temperature threshold
        self.memory_threshold = 80.0  # Memory usage threshold
        self.thermal_mode = 'normal'
        
        # Processing settings
        self.max_brain_threads = 2  # Limit concurrent brain processing
        self.gui_update_interval = 1.0  # GUI update frequency
        
        # Result caching
        self.result_cache = {}
        self.cache_expiry = 300  # 5 minutes
        
        # Performance metrics
        self.brain_processing_count = 0
        self.gui_updates_count = 0
        self.thermal_adjustments = 0
        self.start_time = time.time()
        
        # Initialize
        self._initialize_split_service()
        
        print("Brain vs GUI Split Service initialized")
    
    def _initialize_split_service(self):
        """Initialize the split service"""
        try:
            self.is_active = True
            self._start_brain_processor()
            self._start_gui_updater()
            self._start_thermal_monitor()
            
            print("Brain-GUI split service started")
        except Exception as e:
            print(f"Split service initialization failed: {e}")
    
    def _start_brain_processor(self):
        """Start brain processing thread"""
        try:
            self.brain_thread = threading.Thread(target=self._brain_processor_loop, daemon=True)
            self.brain_thread.start()
        except Exception as e:
            print(f"Failed to start brain processor: {e}")
    
    def _start_gui_updater(self):
        """Start GUI updater thread"""
        try:
            self.gui_thread = threading.Thread(target=self._gui_updater_loop, daemon=True)
            self.gui_thread.start()
        except Exception as e:
            print(f"Failed to start GUI updater: {e}")
    
    def _start_thermal_monitor(self):
        """Start thermal monitoring thread"""
        try:
            self.thermal_thread = threading.Thread(target=self._thermal_monitor_loop, daemon=True)
            self.thermal_thread.start()
        except Exception as e:
            print(f"Failed to start thermal monitor: {e}")
    
    def _brain_processor_loop(self):
        """Main brain processing loop - runs in terminal"""
        print("Brain processor loop started (Terminal processing)")
        
        while self.is_active:
            try:
                # Check thermal constraints
                if self._should_pause_processing():
                    time.sleep(2)
                    continue
                
                # Process brain tasks
                if not self.brain_queue.empty() and len(self.processing_threads) < self.max_brain_threads:
                    brain_task = self.brain_queue.get(timeout=1)
                    self._process_brain_task(brain_task)
                
                time.sleep(0.1)
                
            except queue.Empty:
                continue
            except Exception as e:
                print(f"Brain processor error: {e}")
                time.sleep(1)
        
        print("Brain processor loop ended")
    
    def _gui_updater_loop(self):
        """GUI updater loop - lightweight updates only"""
        print("GUI updater loop started (Lightweight GUI updates)")
        
        while self.is_active:
            try:
                # Update GUI with cached results
                self._update_gui_display()
                
                # Clean up old results
                self._cleanup_old_results()
                
                time.sleep(self.gui_update_interval)
                
            except Exception as e:
                print(f"GUI updater error: {e}")
                time.sleep(2)
        
        print("GUI updater loop ended")
    
    def _thermal_monitor_loop(self):
        """Thermal monitoring loop"""
        print("Thermal monitor loop started")
        
        while self.is_active:
            try:
                # Check system temperature and load
                cpu_temp = self._get_cpu_temperature()
                cpu_usage = psutil.cpu_percent(interval=1)
                memory_usage = psutil.virtual_memory().percent
                
                # Adjust thermal mode
                if cpu_temp > self.cpu_threshold or memory_usage > self.memory_threshold:
                    self.thermal_mode = 'thermal_throttle'
                    self.thermal_adjustments += 1
                    print(f"Thermal throttling activated - CPU: {cpu_usage:.1f}%, Temp: {cpu_temp:.1f}°C, Memory: {memory_usage:.1f}%")
                elif cpu_temp > 60 or memory_usage > 70:
                    self.thermal_mode = 'moderate'
                else:
                    self.thermal_mode = 'normal'
                
                time.sleep(10)  # Check every 10 seconds
                
            except Exception as e:
                print(f"Thermal monitor error: {e}")
                time.sleep(30)
        
        print("Thermal monitor loop ended")
    
    def _should_pause_processing(self) -> bool:
        """Check if brain processing should be paused"""
        return self.thermal_mode == 'thermal_throttle'
    
    def _process_brain_task(self, brain_task: Dict[str, Any]):
        """Process a brain task in terminal"""
        try:
            task_id = brain_task['id']
            task_type = brain_task['type']
            task_data = brain_task['data']
            
            # Create processing thread
            processing_thread = threading.Thread(
                target=self._execute_brain_task,
                args=(task_id, task_type, task_data),
                daemon=True
            )
            
            # Track processing thread
            self.processing_threads[task_id] = {
                'thread': processing_thread,
                'start_time': time.time(),
                'task_type': task_type,
                'status': 'processing'
            }
            
            processing_thread.start()
            
        except Exception as e:
            print(f"Failed to process brain task: {e}")
    
    def _execute_brain_task(self, task_id: str, task_type: str, task_data: Dict[str, Any]):
        """Execute brain task (heavy AI processing)"""
        try:
            start_time = time.time()
            
            # Execute based on task type
            if task_type == 'ai_response':
                result = self._process_ai_response(task_data)
            elif task_type == 'visual_analysis':
                result = self._process_visual_analysis(task_data)
            elif task_type == 'complex_reasoning':
                result = self._process_complex_reasoning(task_data)
            elif task_type == 'data_analysis':
                result = self._process_data_analysis(task_data)
            elif task_type == 'code_generation':
                result = self._process_code_generation(task_data)
            else:
                result = {'success': False, 'error': f'Unknown brain task type: {task_type}'}
            
            # Add processing metadata
            result.update({
                'task_id': task_id,
                'task_type': task_type,
                'processing_time': time.time() - start_time,
                'processed_at': datetime.now().isoformat(),
                'thermal_mode': self.thermal_mode
            })
            
            # Store result for GUI
            self.gui_results[task_id] = result
            self.result_cache[task_id] = {
                'result': result,
                'timestamp': time.time()
            }
            
            # Update metrics
            self.brain_processing_count += 1
            
            # Remove from processing threads
            if task_id in self.processing_threads:
                del self.processing_threads[task_id]
            
        except Exception as e:
            error_result = {
                'success': False,
                'error': f'Brain task execution failed: {str(e)}',
                'task_id': task_id,
                'task_type': task_type,
                'processed_at': datetime.now().isoformat()
            }
            
            self.gui_results[task_id] = error_result
            
            if task_id in self.processing_threads:
                del self.processing_threads[task_id]
    
    def _process_ai_response(self, task_data: Dict[str, Any]) -> Dict[str, Any]:
        """Process AI response (heavy computation)"""
        try:
            query = task_data['query']
            context = task_data.get('context', {})
            
            # This would integrate with the actual AI models
            # For now, simulate heavy processing
            time.sleep(2)  # Simulate AI processing time
            
            # Simulate AI response
            response = f"AI Response to: {query}"
            
            return {
                'success': True,
                'query': query,
                'response': response,
                'context': context,
                'model': 'brain_terminal',
                'processing_location': 'terminal'
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': f'AI response processing failed: {str(e)}'
            }
    
    def _process_visual_analysis(self, task_data: Dict[str, Any]) -> Dict[str, Any]:
        """Process visual analysis (heavy computation)"""
        try:
            image_data = task_data['image_data']
            analysis_type = task_data.get('analysis_type', 'general')
            
            # This would integrate with computer vision models
            # For now, simulate heavy processing
            time.sleep(3)  # Simulate visual analysis time
            
            # Simulate analysis result
            analysis = f"Visual analysis completed for {analysis_type}"
            
            return {
                'success': True,
                'analysis': analysis,
                'analysis_type': analysis_type,
                'model': 'vision_terminal',
                'processing_location': 'terminal'
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': f'Visual analysis processing failed: {str(e)}'
            }
    
    def _process_complex_reasoning(self, task_data: Dict[str, Any]) -> Dict[str, Any]:
        """Process complex reasoning (heavy computation)"""
        try:
            problem = task_data['problem']
            reasoning_type = task_data.get('reasoning_type', 'logical')
            
            # This would integrate with reasoning models
            # For now, simulate heavy processing
            time.sleep(4)  # Simulate reasoning time
            
            # Simulate reasoning result
            reasoning = f"Complex reasoning completed for {reasoning_type}"
            
            return {
                'success': True,
                'reasoning': reasoning,
                'problem': problem,
                'reasoning_type': reasoning_type,
                'model': 'reasoning_terminal',
                'processing_location': 'terminal'
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': f'Complex reasoning processing failed: {str(e)}'
            }
    
    def _process_data_analysis(self, task_data: Dict[str, Any]) -> Dict[str, Any]:
        """Process data analysis (heavy computation)"""
        try:
            data = task_data['data']
            analysis_type = task_data.get('analysis_type', 'statistical')
            
            # This would integrate with data analysis models
            # For now, simulate heavy processing
            time.sleep(2.5)  # Simulate analysis time
            
            # Simulate analysis result
            analysis = f"Data analysis completed for {analysis_type}"
            
            return {
                'success': True,
                'analysis': analysis,
                'data_size': len(str(data)),
                'analysis_type': analysis_type,
                'model': 'analysis_terminal',
                'processing_location': 'terminal'
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': f'Data analysis processing failed: {str(e)}'
            }
    
    def _process_code_generation(self, task_data: Dict[str, Any]) -> Dict[str, Any]:
        """Process code generation (heavy computation)"""
        try:
            prompt = task_data['prompt']
            language = task_data.get('language', 'python')
            
            # This would integrate with code generation models
            # For now, simulate heavy processing
            time.sleep(3.5)  # Simulate code generation time
            
            # Simulate code result
            code = f"# Generated {language} code for: {prompt}\ndef example():\n    pass"
            
            return {
                'success': True,
                'code': code,
                'language': language,
                'prompt': prompt,
                'model': 'code_terminal',
                'processing_location': 'terminal'
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': f'Code generation processing failed: {str(e)}'
            }
    
    def _get_cpu_temperature(self) -> float:
        """Get CPU temperature (simplified)"""
        try:
            # This would use proper temperature monitoring
            # For now, estimate based on CPU load
            cpu_load = psutil.cpu_percent()
            
            if cpu_load > 80:
                return 75.0 + (cpu_load - 80) * 0.5
            elif cpu_load > 60:
                return 60.0 + (cpu_load - 60) * 0.75
            else:
                return 40.0 + cpu_load * 0.25
                
        except:
            return 45.0
    
    def _update_gui_display(self):
        """Update GUI with lightweight results"""
        try:
            # This would integrate with the actual GUI
            # For now, just log the updates
            if self.gui_results:
                recent_results = list(self.gui_results.values())[-5:]  # Last 5 results
                
                for result in recent_results:
                    if result.get('success', False):
                        self.gui_updates_count += 1
                        # In production, this would update the GUI display
                        # For now, just print the result type
                        result_type = result.get('task_type', 'unknown')
                        print(f"GUI Update: {result_type} result ready for display")
            
        except Exception as e:
            print(f"GUI display update failed: {e}")
    
    def _cleanup_old_results(self):
        """Clean up old results"""
        try:
            current_time = time.time()
            
            # Clean up old brain results
            old_tasks = []
            for task_id, result in self.gui_results.items():
                timestamp = result.get('processed_at', '')
                if timestamp:
                    try:
                        result_time = datetime.fromisoformat(timestamp).timestamp()
                        if current_time - result_time > self.cache_expiry:
                            old_tasks.append(task_id)
                    except:
                        old_tasks.append(task_id)
            
            for task_id in old_tasks:
                del self.gui_results[task_id]
                if task_id in self.result_cache:
                    del self.result_cache[task_id]
            
            # Clean up old cache entries
            old_cache = []
            for task_id, cache_entry in self.result_cache.items():
                if current_time - cache_entry['timestamp'] > self.cache_expiry:
                    old_cache.append(task_id)
            
            for task_id in old_cache:
                if task_id in self.result_cache:
                    del self.result_cache[task_id]
            
        except Exception as e:
            print(f"Result cleanup failed: {e}")
    
    def submit_brain_task(self, task_type: str, task_data: Dict[str, Any], 
                         priority: str = 'normal') -> Dict[str, Any]:
        """Submit a task for brain processing (terminal)"""
        try:
            # Generate task ID
            task_id = f"brain_{task_type}_{int(time.time() * 1000)}"
            
            # Create brain task
            brain_task = {
                'id': task_id,
                'type': task_type,
                'data': task_data,
                'priority': priority,
                'submitted_at': datetime.now().isoformat(),
                'processing_location': 'terminal'
            }
            
            # Add to brain queue
            self.brain_queue.put(brain_task)
            
            return {
                'success': True,
                'task_id': task_id,
                'task_type': task_type,
                'processing_location': 'terminal',
                'message': 'Task submitted for terminal brain processing'
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': f'Brain task submission failed: {str(e)}'
            }
    
    def get_result(self, task_id: str) -> Dict[str, Any]:
        """Get result from brain processing for GUI display"""
        try:
            # Check if result is available
            if task_id in self.gui_results:
                result = self.gui_results[task_id].copy()
                result['available_for_gui'] = True
                return result
            else:
                # Check if task is still processing
                if task_id in self.processing_threads:
                    return {
                        'status': 'processing',
                        'task_id': task_id,
                        'processing_location': 'terminal',
                        'message': 'Task still being processed in terminal'
                    }
                else:
                    return {
                        'status': 'not_found',
                        'task_id': task_id,
                        'error': 'Task not found'
                    }
            
        except Exception as e:
            return {
                'error': f'Result retrieval failed: {str(e)}'
            }
    
    def get_cached_result(self, task_id: str) -> Optional[Dict[str, Any]]:
        """Get cached result if available"""
        try:
            if task_id in self.result_cache:
                cache_entry = self.result_cache[task_id]
                if time.time() - cache_entry['timestamp'] < self.cache_expiry:
                    return cache_entry['result']
            return None
        except:
            return None
    
    def get_split_status(self) -> Dict[str, Any]:
        """Get brain-GUI split status"""
        try:
            return {
                'is_active': self.is_active,
                'thermal_mode': self.thermal_mode,
                'brain_queue_size': self.brain_queue.qsize(),
                'processing_threads': len(self.processing_threads),
                'gui_results_count': len(self.gui_results),
                'cache_size': len(self.result_cache),
                'brain_processing_count': self.brain_processing_count,
                'gui_updates_count': self.gui_updates_count,
                'thermal_adjustments': self.thermal_adjustments,
                'cpu_temperature': self._get_cpu_temperature(),
                'cpu_usage': psutil.cpu_percent(),
                'memory_usage': psutil.virtual_memory().percent,
                'last_updated': datetime.now().isoformat()
            }
            
        except Exception as e:
            return {
                'error': f'Split status retrieval failed: {str(e)}'
            }
    
    def get_status(self) -> Dict[str, Any]:
        """Get service status"""
        return {
            'is_active': self.is_active,
            'thermal_mode': self.thermal_mode,
            'max_brain_threads': self.max_brain_threads,
            'gui_update_interval': self.gui_update_interval,
            'cpu_threshold': self.cpu_threshold,
            'memory_threshold': self.memory_threshold,
            'cache_expiry': self.cache_expiry,
            'brain_queue_size': self.brain_queue.qsize(),
            'processing_threads': len(self.processing_threads),
            'gui_results_count': len(self.gui_results),
            'cache_size': len(self.result_cache),
            'last_updated': datetime.now().isoformat()
        }
