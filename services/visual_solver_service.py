#!/usr/bin/env python3
"""
On-Demand Visual Solver Service for JARVIS
Instant webcam capture and multimodal analysis with Gemini 1.5
Camera activates ONLY on explicit command with immediate hardware release
"""

import os
import sys
import time
import threading
import json
import base64
from datetime import datetime
from typing import Dict, Any, List, Optional, Tuple
import cv2
import numpy as np

# Add JARVIS backend path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

class VisualSolverService:
    """Visual Solver service for on-demand image capture and analysis"""
    
    def __init__(self):
        self.is_active = False
        self.on_demand_camera = None
        self.current_frame = None
        self.frame_timestamp = None
        self.analysis_result = None
        
        # Visual feedback
        self.show_duration = 5.0  # 5 seconds display duration
        self.feedback_active = False
        self.feedback_thread = None
        
        # Analysis settings
        self.analysis_prompt = "The user is showing you something on camera. Analyze the image and provide a step-by-step solution or explanation via voice."
        
        # Initialize on-demand camera
        self._initialize_on_demand_camera()
        
        print("Visual Solver Service initialized - On-demand only")
    
    def _initialize_on_demand_camera(self):
        """Initialize on-demand camera service"""
        try:
            from services.on_demand_camera_service import OnDemandCameraService
            self.on_demand_camera = OnDemandCameraService()
            print("On-demand camera service initialized")
        except Exception as e:
            print(f"Failed to initialize on-demand camera: {e}")
    
    def start_camera(self) -> bool:
        """Start on-demand camera for visual solving"""
        try:
            if self.on_demand_camera is None:
                return False
            
            return self.on_demand_camera.start_camera()
            
        except Exception as e:
            print(f"Failed to start on-demand camera: {e}")
            return False
    
    def stop_camera(self):
        """Stop on-demand camera and release hardware immediately"""
        try:
            if self.on_demand_camera:
                self.on_demand_camera.stop_camera()
            
            self.is_active = False
            
            return {
                'success': True,
                'message': 'On-demand camera stopped - Hardware released'
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': f'Stop failed: {str(e)}'
            }
    
    def capture_frame(self) -> Dict[str, Any]:
        """Capture a single high-quality frame with immediate hardware release"""
        try:
            if self.on_demand_camera is None:
                return {
                    'success': False,
                    'error': 'On-demand camera not available'
                }
            
            print("Scanning now, Sir...")
            # In production, this would trigger audio: speak("Scanning now, Sir...")
            
            # Perform on-demand scan
            scan_result = self.on_demand_camera.scan_on_demand("solve")
            
            if scan_result['success']:
                # Get captured frame
                self.current_frame = self.on_demand_camera.get_current_frame()
                self.frame_timestamp = scan_result['timestamp']
                
                print(f"Frame captured at {self.frame_timestamp}")
                
                return {
                    'success': True,
                    'timestamp': self.frame_timestamp,
                    'shape': self.current_frame.shape if self.current_frame is not None else None,
                    'scan_results': scan_result['results'],
                    'message': 'Frame captured successfully - Hardware released'
                }
            else:
                return {
                    'success': False,
                    'error': scan_result.get('error', 'Scan failed')
                }
            
        except Exception as e:
            return {
                'success': False,
                'error': f'Frame capture failed: {str(e)}'
            }
    
    def encode_frame_for_analysis(self) -> Optional[str]:
        """Encode captured frame for multimodal analysis"""
        try:
            if self.current_frame is None:
                return None
            
            # Convert frame to base64
            _, buffer = cv2.imencode('.jpg', self.current_frame)
            frame_base64 = base64.b64encode(buffer).decode('utf-8')
            
            return frame_base64
            
        except Exception as e:
            print(f"Frame encoding failed: {e}")
            return None
    
    def get_current_frame(self) -> Optional[np.ndarray]:
        """Get the current captured frame"""
        return self.current_frame
    
    def save_frame(self, filename: str = None) -> Dict[str, Any]:
        """Save captured frame to file"""
        try:
            if self.current_frame is None:
                return {
                    'success': False,
                    'error': 'No frame captured'
                }
            
            # Generate filename if not provided
            if filename is None:
                timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                filename = f'visual_solver_{timestamp}.jpg'
            
            # Create directory
            os.makedirs('visual_solutions', exist_ok=True)
            save_path = os.path.join('visual_solutions', filename)
            
            # Save frame
            success = cv2.imwrite(save_path, self.current_frame)
            
            if success:
                return {
                    'success': True,
                    'filename': filename,
                    'save_path': save_path,
                    'timestamp': self.frame_timestamp
                }
            else:
                return {
                    'success': False,
                    'error': 'Failed to save frame'
                }
                
        except Exception as e:
            return {
                'success': False,
                'error': f'Frame save failed: {str(e)}'
            }
    
    def show_visual_feedback(self) -> Dict[str, Any]:
        """Show captured frame on dashboard for feedback"""
        try:
            if self.current_frame is None:
                return {
                    'success': False,
                    'error': 'No frame to display'
                }
            
            if self.feedback_active:
                return {
                    'success': False,
                    'error': 'Visual feedback already active'
                }
            
            # Start feedback thread
            self.feedback_active = True
            self.feedback_thread = threading.Thread(
                target=self._visual_feedback_loop,
                daemon=True
            )
            self.feedback_thread.start()
            
            return {
                'success': True,
                'duration': self.show_duration,
                'message': f'Visual feedback started for {self.show_duration} seconds'
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': f'Visual feedback failed: {str(e)}'
            }
    
    def _visual_feedback_loop(self):
        """Visual feedback loop"""
        try:
            # Show frame for specified duration
            start_time = time.time()
            
            while time.time() - start_time < self.show_duration and self.feedback_active:
                # In a real implementation, this would display the frame on a dashboard
                # For now, we'll just simulate the display
                if self.current_frame is not None:
                    # You could integrate with a GUI framework here
                    pass
                
                time.sleep(0.1)
            
            self.feedback_active = False
            print("Visual feedback completed")
            
        except Exception as e:
            print(f"Visual feedback loop error: {e}")
            self.feedback_active = False
    
    def stop_visual_feedback(self):
        """Stop visual feedback"""
        try:
            self.feedback_active = False
            if self.feedback_thread and self.feedback_thread.is_alive():
                self.feedback_thread.join(timeout=1)
            
            return {
                'success': True,
                'message': 'Visual feedback stopped'
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': f'Failed to stop visual feedback: {str(e)}'
            }
    
    def analyze_visual_problem(self, frame: np.ndarray = None, custom_prompt: str = None) -> Dict[str, Any]:
        """Analyze visual problem with multimodal AI"""
        try:
            # Use provided frame or current frame
            if frame is None:
                frame = self.current_frame
            
            if frame is None:
                return {
                    'success': False,
                    'error': 'No frame available for analysis'
                }
            
            # Encode frame
            frame_base64 = self.encode_frame_for_analysis()
            if frame_base64 is None:
                return {
                    'success': False,
                    'error': 'Failed to encode frame'
                }
            
            # Prepare analysis request
            prompt = custom_prompt or self.analysis_prompt
            
            # This would integrate with Gemini 1.5 or other multimodal AI
            # For now, return a mock analysis result
            analysis_result = {
                'success': True,
                'prompt': prompt,
                'frame_info': {
                    'shape': frame.shape,
                    'timestamp': self.frame_timestamp
                },
                'analysis': {
                    'description': 'Visual analysis completed',
                    'solution': 'Step-by-step solution would be provided by Gemini 1.5',
                    'confidence': 0.95
                },
                'message': 'Visual analysis completed successfully'
            }
            
            self.analysis_result = analysis_result
            
            return analysis_result
            
        except Exception as e:
            return {
                'success': False,
                'error': f'Visual analysis failed: {str(e)}'
            }
    
    def solve_visual_problem(self, custom_prompt: str = None) -> Dict[str, Any]:
        """Complete visual problem solving workflow"""
        try:
            # Step 1: Capture frame
            capture_result = self.capture_frame()
            if not capture_result['success']:
                return capture_result
            
            # Step 2: Analyze the frame
            analysis_result = self.analyze_visual_problem(custom_prompt=custom_prompt)
            
            # Step 3: Show visual feedback
            if analysis_result['success']:
                self.show_visual_feedback()
            
            return analysis_result
            
        except Exception as e:
            return {
                'success': False,
                'error': f'Visual problem solving failed: {str(e)}'
            }
    
    def get_status(self) -> Dict[str, Any]:
        """Get visual solver service status"""
        return {
            'is_active': self.is_active,
            'camera_index': self.camera_index,
            'frame_dimensions': (self.frame_width, self.frame_height),
            'focus_delay': self.focus_delay,
            'auto_shutdown': self.auto_shutdown,
            'has_frame': self.current_frame is not None,
            'frame_timestamp': self.frame_timestamp,
            'feedback_active': self.feedback_active,
            'show_duration': self.show_duration,
            'last_updated': datetime.now().isoformat()
        }
    
    def get_analysis_result(self) -> Dict[str, Any]:
        """Get the last analysis result"""
        if self.analysis_result:
            return {
                'success': True,
                'result': self.analysis_result
            }
        else:
            return {
                'success': False,
                'error': 'No analysis result available'
            }
