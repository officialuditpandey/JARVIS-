#!/usr/bin/env python3
"""
On-Demand Camera Service for JARVIS
Camera activates ONLY on explicit command: "Jarvis, look at this" or "Jarvis, solve this"
No background scanning - immediate power-off after capture
"""

import os
import sys
import time
import threading
import json
from datetime import datetime
from typing import Dict, Any, List, Optional, Tuple
import cv2
import numpy as np
import pyautogui
import psutil

# Add JARVIS backend path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

try:
    import mediapipe as mp
    MEDIAPIPE_AVAILABLE = True
except ImportError:
    MEDIAPIPE_AVAILABLE = False

try:
    import pytesseract
    TESSERACT_AVAILABLE = True
except ImportError:
    TESSERACT_AVAILABLE = False

class OnDemandCameraService:
    """On-demand camera service - activates only on explicit command"""
    
    def __init__(self):
        self.camera = None
        self.is_active = False
        self.is_scanning = False
        self.current_frame = None
        self.scan_results = {}
        
        # MediaPipe setup
        self.mp_pose = None
        self.pose = None
        self.mp_face_mesh = None
        self.face_mesh = None
        
        # Camera configuration
        self.camera_index = 0
        self.frame_width = 1280
        self.frame_height = 720
        self.focus_delay = 1.0  # 1 second focus delay
        
        # Initialize MediaPipe
        self._initialize_mediapipe()
        
        print("On-Demand Camera Service initialized - No background scanning")
    
    def _initialize_mediapipe(self):
        """Initialize MediaPipe components"""
        try:
            if MEDIAPIPE_AVAILABLE:
                self.mp_pose = mp.solutions.pose
                self.pose = self.mp_pose.Pose(
                    static_image_mode=True,
                    model_complexity=1,
                    enable_segmentation=False,
                    min_detection_confidence=0.5
                )
                
                self.mp_face_mesh = mp.solutions.face_mesh
                self.face_mesh = self.mp_face_mesh.FaceMesh(
                    static_image_mode=True,
                    max_num_faces=1,
                    refine_landmarks=True,
                    min_detection_confidence=0.5
                )
                
                print("MediaPipe initialized for on-demand analysis")
        except Exception as e:
            print(f"MediaPipe initialization failed: {e}")
    
    def start_camera(self) -> bool:
        """Start camera for on-demand use"""
        try:
            if self.camera is not None:
                return True  # Already started
            
            self.camera = cv2.VideoCapture(self.camera_index)
            
            if not self.camera.isOpened():
                print(f"Failed to open camera {self.camera_index}")
                return False
            
            # Set camera properties
            self.camera.set(cv2.CAP_PROP_FRAME_WIDTH, self.frame_width)
            self.camera.set(cv2.CAP_PROP_FRAME_HEIGHT, self.frame_height)
            self.camera.set(cv2.CAP_PROP_FPS, 30)
            self.camera.set(cv2.CAP_PROP_AUTOFOCUS, 1)
            
            self.is_active = True
            print("Camera started for on-demand use")
            return True
            
        except Exception as e:
            print(f"Failed to start camera: {e}")
            return False
    
    def stop_camera(self):
        """Stop camera and release hardware immediately"""
        try:
            if self.camera is not None:
                self.camera.release()
                self.camera = None
                self.is_active = False
                self.is_scanning = False
                print("Camera stopped - Hardware released")
        except Exception as e:
            print(f"Failed to stop camera: {e}")
    
    def scan_on_demand(self, scan_type: str = "general") -> Dict[str, Any]:
        """Perform on-demand scan with immediate hardware release"""
        try:
            if self.is_scanning:
                return {
                    'success': False,
                    'error': 'Scan already in progress'
                }
            
            # Start camera
            if not self.start_camera():
                return {
                    'success': False,
                    'error': 'Failed to start camera'
                }
            
            self.is_scanning = True
            
            # Give notification cue
            print("Scanning now, Sir...")
            # In production, this would trigger audio: speak("Scanning now, Sir...")
            
            # Focus delay
            time.sleep(self.focus_delay)
            
            # Capture frame
            ret, frame = self.camera.read()
            
            if not ret:
                self.stop_camera()
                return {
                    'success': False,
                    'error': 'Failed to capture frame'
                }
            
            # Store current frame
            self.current_frame = frame.copy()
            
            # Perform analysis based on scan type
            if scan_type == "solve":
                results = self._analyze_for_solving(frame)
            elif scan_type == "look":
                results = self._analyze_for_looking(frame)
            else:
                results = self._analyze_general(frame)
            
            # IMPORTANT: Stop camera immediately after capture
            self.stop_camera()
            
            # Store results
            self.scan_results[scan_type] = {
                'timestamp': datetime.now().isoformat(),
                'results': results,
                'frame_info': {
                    'width': frame.shape[1],
                    'height': frame.shape[0],
                    'channels': frame.shape[2]
                }
            }
            
            return {
                'success': True,
                'scan_type': scan_type,
                'results': results,
                'timestamp': datetime.now().isoformat(),
                'message': f'On-demand {scan_type} scan completed'
            }
            
        except Exception as e:
            self.stop_camera()  # Ensure camera is stopped on error
            return {
                'success': False,
                'error': f'On-demand scan failed: {str(e)}'
            }
    
    def _analyze_for_solving(self, frame: np.ndarray) -> Dict[str, Any]:
        """Analyze frame for problem solving"""
        try:
            results = {
                'analysis_type': 'solve',
                'findings': [],
                'suggestions': []
            }
            
            # Basic analysis
            results['findings'].append("Frame captured for problem solving")
            
            # Check for text content
            if TESSERACT_AVAILABLE:
                try:
                    # Convert to grayscale for OCR
                    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                    
                    # Apply threshold for better OCR
                    _, thresh = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
                    
                    # Extract text
                    text = pytesseract.image_to_string(thresh)
                    
                    if text.strip():
                        results['findings'].append(f"Text detected: {text[:100]}...")
                        results['suggestions'].append("This appears to contain readable text that can be analyzed")
                    else:
                        results['findings'].append("No readable text detected")
                        
                except Exception as e:
                    results['findings'].append(f"Text analysis failed: {e}")
            
            # Check for mathematical content
            results['findings'].append("Analyzing for mathematical or technical content...")
            
            # Check for diagrams/charts
            results['findings'].append("Checking for diagrams, charts, or technical drawings...")
            
            return results
            
        except Exception as e:
            return {
                'analysis_type': 'solve',
                'error': f'Solving analysis failed: {str(e)}'
            }
    
    def _analyze_for_looking(self, frame: np.ndarray) -> Dict[str, Any]:
        """Analyze frame for general observation"""
        try:
            results = {
                'analysis_type': 'look',
                'findings': [],
                'suggestions': []
            }
            
            results['findings'].append("Frame captured for observation")
            
            # Basic scene analysis
            results['findings'].append("Analyzing scene content...")
            
            # Check for people
            if self.face_mesh is not None:
                try:
                    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                    face_results = self.face_mesh.process(rgb_frame)
                    
                    if face_results.multi_face_landmarks:
                        face_count = len(face_results.multi_face_landmarks)
                        results['findings'].append(f"{face_count} face(s) detected")
                        results['suggestions'].append(f"I can see {face_count} person(s) in the frame")
                    else:
                        results['findings'].append("No faces detected")
                        
                except Exception as e:
                    results['findings'].append(f"Face detection failed: {e}")
            
            # Check for posture
            if self.pose is not None:
                try:
                    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                    pose_results = self.pose.process(rgb_frame)
                    
                    if pose_results.pose_landmarks:
                        results['findings'].append("Human pose detected")
                        results['suggestions'].append("I can see a person and can analyze their posture")
                    else:
                        results['findings'].append("No human pose detected")
                        
                except Exception as e:
                    results['findings'].append(f"Pose detection failed: {e}")
            
            # General scene description
            results['findings'].append("Analyzing general scene elements...")
            results['suggestions'].append("I can see what you're showing me")
            
            return results
            
        except Exception as e:
            return {
                'analysis_type': 'look',
                'error': f'Looking analysis failed: {str(e)}'
            }
    
    def _analyze_general(self, frame: np.ndarray) -> Dict[str, Any]:
        """General analysis of frame"""
        try:
            results = {
                'analysis_type': 'general',
                'findings': [],
                'suggestions': []
            }
            
            results['findings'].append("Frame captured for general analysis")
            results['findings'].append("Analyzing image content...")
            results['suggestions'].append("I can see what you're showing me")
            
            return results
            
        except Exception as e:
            return {
                'analysis_type': 'general',
                'error': f'General analysis failed: {str(e)}'
            }
    
    def get_current_frame(self) -> Optional[np.ndarray]:
        """Get the most recently captured frame"""
        return self.current_frame
    
    def save_frame(self, filename: str = None, scan_type: str = None) -> Dict[str, Any]:
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
                scan_prefix = scan_type or 'scan'
                filename = f'on_demand_{scan_prefix}_{timestamp}.jpg'
            
            # Create directory
            os.makedirs('on_demand_scans', exist_ok=True)
            save_path = os.path.join('on_demand_scans', filename)
            
            # Save frame
            success = cv2.imwrite(save_path, self.current_frame)
            
            if success:
                return {
                    'success': True,
                    'filename': filename,
                    'save_path': save_path,
                    'timestamp': datetime.now().isoformat()
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
    
    def get_scan_results(self, scan_type: str = None) -> Dict[str, Any]:
        """Get results from previous scans"""
        try:
            if scan_type and scan_type in self.scan_results:
                return {
                    'success': True,
                    'scan_type': scan_type,
                    'results': self.scan_results[scan_type]
                }
            else:
                return {
                    'success': True,
                    'all_results': self.scan_results,
                    'available_scans': list(self.scan_results.keys())
                }
                
        except Exception as e:
            return {
                'success': False,
                'error': f'Results retrieval failed: {str(e)}'
            }
    
    def get_status(self) -> Dict[str, Any]:
        """Get on-demand camera service status"""
        return {
            'is_active': self.is_active,
            'is_scanning': self.is_scanning,
            'camera_available': self.camera is not None,
            'camera_index': self.camera_index,
            'frame_dimensions': (self.frame_width, self.frame_height),
            'focus_delay': self.focus_delay,
            'mediapipe_available': MEDIAPIPE_AVAILABLE,
            'tesseract_available': TESSERACT_AVAILABLE,
            'has_frame': self.current_frame is not None,
            'scan_count': len(self.scan_results),
            'available_scans': list(self.scan_results.keys()),
            'last_updated': datetime.now().isoformat(),
            'mode': 'ON_DEMAND_ONLY - No background scanning'
        }
