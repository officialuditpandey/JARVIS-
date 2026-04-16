#!/usr/bin/env python3
"""
Proactive Camera Service for JARVIS
Auto-scan room/screen every 60s and suggest improvements live
"""

import os
import sys
import time
import threading
import json
from datetime import datetime, timedelta
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

class ProactiveCameraService:
    """Proactive camera scanning service for room and screen analysis"""
    
    def __init__(self):
        self.camera = None
        self.is_active = False
        self.scan_thread = None
        self.stop_event = threading.Event()
        
        # MediaPipe setup
        self.mp_pose = None
        self.pose = None
        self.mp_face_mesh = None
        self.face_mesh = None
        
        # Scanning configuration
        self.scan_interval = 60  # seconds
        self.last_scan_time = 0
        self.suggestions = []
        self.scan_history = []
        
        # Analysis results
        self.current_room_state = {}
        self.current_screen_state = {}
        self.improvement_suggestions = []
        
        # Performance metrics
        self.scan_count = 0
        self.suggestion_count = 0
        self.start_time = time.time()
        
        # Initialize
        self._initialize_scanner()
        
        print("Proactive Camera Service initialized")
    
    def _initialize_scanner(self):
        """Initialize camera and analysis systems"""
        try:
            # Initialize MediaPipe
            if MEDIAPIPE_AVAILABLE:
                self.mp_pose = mp.solutions.pose
                self.pose = self.mp_pose.Pose(
                    static_image_mode=False,
                    model_complexity=1,
                    min_detection_confidence=0.5,
                    min_tracking_confidence=0.5
                )
                
                self.mp_face_mesh = mp.solutions.face_mesh
                self.face_mesh = self.mp_face_mesh.FaceMesh(
                    static_image_mode=False,
                    max_num_faces=1,
                    refine_landmarks=True,
                    min_detection_confidence=0.5,
                    min_tracking_confidence=0.5
                )
                
                print("MediaPipe initialized for proactive scanning")
            
        except Exception as e:
            print(f"Scanner initialization failed: {e}")
    
    def start_proactive_scanning(self, camera_index: int = 0) -> bool:
        """Start proactive camera scanning"""
        try:
            if self.is_active:
                return True
            
            # Initialize camera
            self.camera = cv2.VideoCapture(camera_index)
            if not self.camera.isOpened():
                print("Failed to open camera for proactive scanning")
                return False
            
            self.camera.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
            self.camera.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
            self.camera.set(cv2.CAP_PROP_FPS, 30)
            
            self.is_active = True
            self.stop_event.clear()
            
            # Start scanning thread
            self.scan_thread = threading.Thread(target=self._scanning_loop, daemon=True)
            self.scan_thread.start()
            
            print("Proactive camera scanning started")
            return True
            
        except Exception as e:
            print(f"Failed to start proactive scanning: {e}")
            return False
    
    def stop_proactive_scanning(self):
        """Stop proactive camera scanning"""
        try:
            self.is_active = False
            self.stop_event.set()
            
            if self.scan_thread and self.scan_thread.is_alive():
                self.scan_thread.join(timeout=2)
            
            if self.camera:
                self.camera.release()
                self.camera = None
            
            print("Proactive camera scanning stopped")
            
        except Exception as e:
            print(f"Failed to stop proactive scanning: {e}")
    
    def _scanning_loop(self):
        """Main scanning loop"""
        print("Proactive scanning loop started")
        
        while self.is_active and not self.stop_event.is_set():
            try:
                current_time = time.time()
                
                # Perform scan at intervals
                if current_time - self.last_scan_time > self.scan_interval:
                    self._perform_comprehensive_scan()
                    self.last_scan_time = current_time
                
                time.sleep(1)
                
            except Exception as e:
                print(f"Scanning loop error: {e}")
                time.sleep(5)
        
        print("Proactive scanning loop ended")
    
    def _perform_comprehensive_scan(self):
        """Perform comprehensive room and screen scan"""
        try:
            print("Performing comprehensive scan...")
            
            # Scan room environment
            room_analysis = self._scan_room_environment()
            
            # Scan screen content
            screen_analysis = self._scan_screen_content()
            
            # Generate improvement suggestions
            suggestions = self._generate_improvement_suggestions(room_analysis, screen_analysis)
            
            # Store results
            scan_result = {
                'timestamp': datetime.now().isoformat(),
                'room_analysis': room_analysis,
                'screen_analysis': screen_analysis,
                'suggestions': suggestions
            }
            
            self.scan_history.append(scan_result)
            self.current_room_state = room_analysis
            self.current_screen_state = screen_analysis
            self.improvement_suggestions = suggestions
            
            # Keep only last 50 scans
            if len(self.scan_history) > 50:
                self.scan_history = self.scan_history[-50:]
            
            self.scan_count += 1
            
            # Announce suggestions
            self._announce_suggestions(suggestions)
            
            print(f"Scan completed: {len(suggestions)} suggestions generated")
            
        except Exception as e:
            print(f"Comprehensive scan failed: {e}")
    
    def _scan_room_environment(self) -> Dict[str, Any]:
        """Scan room environment for improvements"""
        try:
            ret, frame = self.camera.read()
            if not ret:
                return {}
            
            # Analyze lighting conditions
            brightness = np.mean(cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY))
            lighting_quality = self._assess_lighting(brightness)
            
            # Analyze posture if person detected
            posture_analysis = self._analyze_posture(frame)
            
            # Analyze room organization
            room_organization = self._analyze_room_organization(frame)
            
            # Analyze background noise (simplified)
            background_noise = self._analyze_background_noise()
            
            return {
                'lighting_quality': lighting_quality,
                'brightness_level': brightness,
                'posture_analysis': posture_analysis,
                'room_organization': room_organization,
                'background_noise': background_noise,
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            print(f"Room environment scan failed: {e}")
            return {}
    
    def _scan_screen_content(self) -> Dict[str, Any]:
        """Scan screen content for productivity insights"""
        try:
            # Capture screen
            screenshot = pyautogui.screenshot()
            screenshot_array = np.array(screenshot)
            screenshot_bgr = cv2.cvtColor(screenshot_array, cv2.COLOR_RGB2BGR)
            
            # Analyze screen content
            screen_analysis = {
                'active_windows': self._analyze_active_windows(),
                'screen_brightness': self._analyze_screen_brightness(screenshot_bgr),
                'window_organization': self._analyze_window_organization(),
                'productivity_apps': self._analyze_productivity_apps(),
                'distractions': self._analyze_screen_distractions(),
                'text_content': self._extract_screen_text(screenshot_bgr)
            }
            
            return screen_analysis
            
        except Exception as e:
            print(f"Screen content scan failed: {e}")
            return {}
    
    def _assess_lighting(self, brightness: float) -> Dict[str, Any]:
        """Assess lighting quality"""
        try:
            if brightness < 50:
                quality = "poor"
                suggestion = "Room is too dark. Consider adding more lighting for better visibility and eye comfort."
            elif brightness < 100:
                quality = "fair"
                suggestion = "Lighting could be improved. Consider adjusting blinds or adding a desk lamp."
            elif brightness < 180:
                quality = "good"
                suggestion = "Lighting is adequate for most tasks."
            else:
                quality = "excellent"
                suggestion = "Lighting is optimal for productivity."
            
            return {
                'quality': quality,
                'brightness_score': brightness,
                'suggestion': suggestion
            }
            
        except Exception as e:
            return {'quality': 'unknown', 'brightness_score': 0, 'suggestion': ''}
    
    def _analyze_posture(self, frame: np.ndarray) -> Dict[str, Any]:
        """Analyze user posture"""
        try:
            if not self.pose:
                return {'status': 'unavailable'}
            
            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            results = self.pose.process(frame_rgb)
            
            if results.pose_landmarks:
                # Calculate posture metrics
                landmarks = results.pose_landmarks.landmark
                
                # Head position
                head_y = landmarks[0].y
                
                # Shoulder alignment
                left_shoulder = landmarks[11].y
                right_shoulder = landmarks[12].y
                shoulder_tilt = abs(left_shoulder - right_shoulder)
                
                # Overall posture score
                posture_score = max(0, 100 - (head_y * 100) - (shoulder_tilt * 200))
                
                if posture_score < 60:
                    status = "poor"
                    suggestion = "Your posture needs improvement. Sit up straight and adjust your chair height."
                elif posture_score < 80:
                    status = "fair"
                    suggestion = "Posture could be better. Consider taking a stretch break."
                else:
                    status = "good"
                    suggestion = "Posture looks good. Keep it up!"
                
                return {
                    'status': status,
                    'score': posture_score,
                    'head_position': head_y,
                    'shoulder_tilt': shoulder_tilt,
                    'suggestion': suggestion
                }
            else:
                return {'status': 'no_person_detected'}
                
        except Exception as e:
            return {'status': 'error', 'error': str(e)}
    
    def _analyze_room_organization(self, frame: np.ndarray) -> Dict[str, Any]:
        """Analyze room organization"""
        try:
            # Simplified room organization analysis
            # In production, this would use computer vision to detect clutter
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            
            # Calculate edge density as a proxy for organization
            edges = cv2.Canny(gray, 50, 150)
            edge_density = np.sum(edges > 0) / edges.size
            
            if edge_density > 0.1:
                organization = "cluttered"
                suggestion = "Your workspace appears cluttered. Consider organizing for better focus."
            elif edge_density > 0.05:
                organization = "moderate"
                suggestion = "Workspace is moderately organized. Minor cleanup could help."
            else:
                organization = "organized"
                suggestion = "Your workspace looks well-organized!"
            
            return {
                'organization_level': organization,
                'edge_density': edge_density,
                'suggestion': suggestion
            }
            
        except Exception as e:
            return {'organization_level': 'unknown', 'suggestion': ''}
    
    def _analyze_background_noise(self) -> Dict[str, Any]:
        """Analyze background noise (simplified)"""
        try:
            # This would use audio analysis in production
            # For now, return system noise level
            cpu_usage = psutil.cpu_percent()
            
            if cpu_usage > 80:
                noise_level = "high"
                suggestion = "System is under heavy load. Consider closing unnecessary applications."
            elif cpu_usage > 50:
                noise_level = "moderate"
                suggestion = "System usage is moderate."
            else:
                noise_level = "low"
                suggestion = "System is running quietly."
            
            return {
                'noise_level': noise_level,
                'cpu_usage': cpu_usage,
                'suggestion': suggestion
            }
            
        except Exception as e:
            return {'noise_level': 'unknown', 'suggestion': ''}
    
    def _analyze_active_windows(self) -> List[Dict[str, Any]]:
        """Analyze active windows"""
        try:
            import win32gui
            import win32con
            
            windows = []
            
            def enum_windows_callback(hwnd, windows_list):
                if win32gui.IsWindowVisible(hwnd) and win32gui.GetWindowText(hwnd):
                    rect = win32gui.GetWindowRect(hwnd)
                    window_info = {
                        'title': win32gui.GetWindowText(hwnd),
                        'handle': hwnd,
                        'position': (rect[0], rect[1]),
                        'size': (rect[2] - rect[0], rect[3] - rect[1])
                    }
                    windows_list.append(window_info)
                return True
            
            win32gui.EnumWindows(enum_windows_callback, windows)
            
            return windows[:10]  # Return top 10 windows
            
        except Exception as e:
            print(f"Window analysis failed: {e}")
            return []
    
    def _analyze_screen_brightness(self, screenshot: np.ndarray) -> Dict[str, Any]:
        """Analyze screen brightness"""
        try:
            gray = cv2.cvtColor(screenshot, cv2.COLOR_BGR2GRAY)
            brightness = np.mean(gray)
            
            if brightness < 80:
                level = "too_dark"
                suggestion = "Screen brightness is too low. Increase for better visibility."
            elif brightness < 120:
                level = "optimal"
                suggestion = "Screen brightness is optimal."
            else:
                level = "too_bright"
                suggestion = "Screen brightness is too high. Reduce to prevent eye strain."
            
            return {
                'level': level,
                'brightness_value': brightness,
                'suggestion': suggestion
            }
            
        except Exception as e:
            return {'level': 'unknown', 'suggestion': ''}
    
    def _analyze_window_organization(self) -> Dict[str, Any]:
        """Analyze window organization"""
        try:
            windows = self._analyze_active_windows()
            
            if len(windows) > 8:
                organization = "cluttered"
                suggestion = "Too many open windows. Consider closing unused ones."
            elif len(windows) > 5:
                organization = "moderate"
                suggestion = "Several windows open. Consider organizing your workspace."
            else:
                organization = "organized"
                suggestion = "Window organization looks good."
            
            return {
                'organization': organization,
                'window_count': len(windows),
                'suggestion': suggestion
            }
            
        except Exception as e:
            return {'organization': 'unknown', 'suggestion': ''}
    
    def _analyze_productivity_apps(self) -> List[str]:
        """Analyze productivity applications"""
        try:
            windows = self._analyze_active_windows()
            productivity_apps = []
            
            productivity_keywords = ['visual studio', 'code', 'excel', 'word', 'powerpoint', 'notepad', 'terminal', 'command', 'jupyter']
            
            for window in windows:
                title = window['title'].lower()
                if any(keyword in title for keyword in productivity_keywords):
                    productivity_apps.append(window['title'])
            
            return productivity_apps
            
        except Exception as e:
            return []
    
    def _analyze_screen_distractions(self) -> List[str]:
        """Analyze potential distractions on screen"""
        try:
            windows = self._analyze_active_windows()
            distractions = []
            
            distraction_keywords = ['youtube', 'facebook', 'twitter', 'instagram', 'tiktok', 'reddit', 'netflix', 'spotify']
            
            for window in windows:
                title = window['title'].lower()
                if any(keyword in title for keyword in distraction_keywords):
                    distractions.append(window['title'])
            
            return distractions
            
        except Exception as e:
            return []
    
    def _extract_screen_text(self, screenshot: np.ndarray) -> str:
        """Extract text from screen using OCR"""
        try:
            if not TESSERACT_AVAILABLE:
                return "OCR not available"
            
            text = pytesseract.image_to_string(screenshot)
            return text[:500]  # Return first 500 characters
            
        except Exception as e:
            return f"Text extraction failed: {e}"
    
    def _generate_improvement_suggestions(self, room_analysis: Dict[str, Any], screen_analysis: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate comprehensive improvement suggestions"""
        suggestions = []
        
        # Room-based suggestions
        if 'lighting_quality' in room_analysis:
            lighting = room_analysis['lighting_quality']
            if lighting['quality'] in ['poor', 'fair']:
                suggestions.append({
                    'category': 'lighting',
                    'priority': 'high',
                    'suggestion': lighting['suggestion'],
                    'confidence': 0.8
                })
        
        if 'posture_analysis' in room_analysis:
            posture = room_analysis['posture_analysis']
            if posture.get('status') in ['poor', 'fair']:
                suggestions.append({
                    'category': 'posture',
                    'priority': 'high',
                    'suggestion': posture.get('suggestion', ''),
                    'confidence': 0.9
                })
        
        if 'room_organization' in room_analysis:
            organization = room_analysis['room_organization']
            if organization['organization_level'] in ['cluttered', 'moderate']:
                suggestions.append({
                    'category': 'organization',
                    'priority': 'medium',
                    'suggestion': organization['suggestion'],
                    'confidence': 0.7
                })
        
        # Screen-based suggestions
        if 'screen_brightness' in screen_analysis:
            brightness = screen_analysis['screen_brightness']
            if brightness['level'] in ['too_dark', 'too_bright']:
                suggestions.append({
                    'category': 'screen_brightness',
                    'priority': 'medium',
                    'suggestion': brightness['suggestion'],
                    'confidence': 0.8
                })
        
        if 'window_organization' in screen_analysis:
            windows = screen_analysis['window_organization']
            if windows['organization'] in ['cluttered', 'moderate']:
                suggestions.append({
                    'category': 'window_organization',
                    'priority': 'medium',
                    'suggestion': windows['suggestion'],
                    'confidence': 0.7
                })
        
        # Distraction suggestions
        if 'distractions' in screen_analysis and screen_analysis['distractions']:
            suggestions.append({
                'category': 'distractions',
                'priority': 'high',
                'suggestion': f"Potential distractions detected: {', '.join(screen_analysis['distractions'][:3])}. Consider focusing on work.",
                'confidence': 0.9
            })
        
        # System performance suggestions
        if 'background_noise' in room_analysis:
            noise = room_analysis['background_noise']
            if noise['noise_level'] == 'high':
                suggestions.append({
                    'category': 'performance',
                    'priority': 'medium',
                    'suggestion': noise['suggestion'],
                    'confidence': 0.8
                })
        
        # Sort by priority and confidence
        suggestions.sort(key=lambda x: (x['priority'] != 'high', x['confidence']), reverse=True)
        
        self.suggestion_count += len(suggestions)
        return suggestions
    
    def _announce_suggestions(self, suggestions: List[Dict[str, Any]]):
        """Announce suggestions to user"""
        try:
            if not suggestions:
                print("No new suggestions - everything looks good!")
                return
            
            # Announce top 3 suggestions
            top_suggestions = suggestions[:3]
            
            for i, suggestion in enumerate(top_suggestions, 1):
                message = f"Suggestion {i}: {suggestion['suggestion']}"
                print(f"ANNOUNCEMENT: {message}")
                
                # In production, this would use JARVIS voice system
                # For now, just print to console
            
        except Exception as e:
            print(f"Suggestion announcement failed: {e}")
    
    def get_current_suggestions(self) -> List[Dict[str, Any]]:
        """Get current improvement suggestions"""
        return self.improvement_suggestions
    
    def get_scan_history(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get recent scan history"""
        return self.scan_history[-limit:]
    
    def get_status(self) -> Dict[str, Any]:
        """Get proactive camera service status"""
        return {
            'is_active': self.is_active,
            'scan_interval': self.scan_interval,
            'last_scan_time': datetime.fromtimestamp(self.last_scan_time).isoformat() if self.last_scan_time > 0 else None,
            'scan_count': self.scan_count,
            'suggestion_count': self.suggestion_count,
            'current_suggestions': len(self.improvement_suggestions),
            'mediapipe_available': MEDIAPIPE_AVAILABLE,
            'tesseract_available': TESSERACT_AVAILABLE,
            'last_updated': datetime.now().isoformat()
        }
