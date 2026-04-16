#!/usr/bin/env python3
"""
Health & Workspace Guardian Service for JARVIS - Features 36-40
Advanced Posture AI and Eye-Strain (20-20-20) Alerts with camera monitoring
"""

import os
import sys
import time
import threading
import math
from datetime import datetime, timedelta
from typing import Dict, Any, Optional, List, Tuple
import cv2
import numpy as np

# Add JARVIS backend path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

try:
    import mediapipe as mp
    MEDIAPIPE_AVAILABLE = True
except ImportError:
    print("MediaPipe not available - Installing...")
    os.system("pip install mediapipe")
    try:
        import mediapipe as mp
        MEDIAPIPE_AVAILABLE = True
    except ImportError:
        MEDIAPIPE_AVAILABLE = False

try:
    import winsound
    WINSOUND_AVAILABLE = True
except ImportError:
    print("winsound not available - Using alternative alerts")
    WINSOUND_AVAILABLE = False

class HealthGuardianService:
    """Health & Workspace Guardian service for posture and eye strain monitoring"""
    
    def __init__(self):
        self.camera = None
        self.is_active = False
        self.guardian_thread = None
        self.stop_event = threading.Event()
        
        # MediaPipe setup
        self.mp_pose = None
        self.pose = None
        self.mp_face_mesh = None
        self.face_mesh = None
        self.mp_drawing = None
        
        # Health monitoring state
        self.current_posture_score = 0
        self.eye_strain_timer = 0  # 20-20-20 rule timer (seconds)
        self.last_eye_break_time = time.time()
        self.slouch_start_time = None
        self.last_posture_warning = 0
        self.last_eye_warning = 0
        
        # Configuration
        self.posture_threshold = 60  # Below this is poor posture
        self.slouch_threshold_seconds = 30  # Warn after 30 seconds of slouching
        self.eye_break_interval = 1200  # 20 minutes in seconds
        self.posture_warning_interval = 60  # Seconds between posture warnings
        self.eye_warning_interval = 30  # Seconds between eye warnings
        
        # Alert system
        self.voice_alerts_enabled = True
        self.visual_alerts_enabled = True
        self.audio_alerts_enabled = True
        
        # Performance metrics
        self.fps = 0
        self.frame_count = 0
        self.start_time = time.time()
        self.posture_checks = 0
        self.eye_strain_alerts = 0
        self.posture_alerts = 0
        
        # Health data storage
        self.health_log = []
        self.daily_stats = {
            'posture_score_sum': 0,
            'posture_score_count': 0,
            'eye_breaks_taken': 0,
            'posture_warnings': 0,
            'eye_strain_warnings': 0
        }
        
        # Initialize
        self._initialize_guardian()
        
        print("Health & Workspace Guardian Service initialized with Posture AI & Eye-Strain Alerts")
    
    def _initialize_guardian(self):
        """Initialize MediaPipe and health monitoring systems"""
        try:
            # Initialize MediaPipe Pose
            if MEDIAPIPE_AVAILABLE:
                self.mp_pose = mp.solutions.pose
                self.pose = self.mp_pose.Pose(
                    static_image_mode=False,
                    model_complexity=1,
                    enable_segmentation=False,
                    min_detection_confidence=0.5,
                    min_tracking_confidence=0.5
                )
                
                # Initialize MediaPipe Face Mesh for eye tracking
                self.mp_face_mesh = mp.solutions.face_mesh
                self.face_mesh = self.mp_face_mesh.FaceMesh(
                    static_image_mode=False,
                    max_num_faces=1,
                    refine_landmarks=True,
                    min_detection_confidence=0.5,
                    min_tracking_confidence=0.5
                )
                
                self.mp_drawing = mp.solutions.drawing_utils
                print("MediaPipe pose and face mesh initialized")
            
        except Exception as e:
            print(f"Guardian initialization failed: {e}")
    
    def start_guardian(self, camera_index: int = 0) -> bool:
        """Start health guardian monitoring"""
        try:
            if self.is_active:
                return True
            
            # Initialize camera
            self.camera = cv2.VideoCapture(camera_index)
            if not self.camera.isOpened():
                print("Failed to open camera for health monitoring")
                return False
            
            self.camera.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
            self.camera.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
            self.camera.set(cv2.CAP_PROP_FPS, 30)
            
            self.is_active = True
            self.stop_event.clear()
            
            # Start guardian thread
            self.guardian_thread = threading.Thread(target=self._guardian_loop, daemon=True)
            self.guardian_thread.start()
            
            print("Health & Workspace Guardian started")
            return True
            
        except Exception as e:
            print(f"Failed to start guardian: {e}")
            return False
    
    def stop_guardian(self):
        """Stop health guardian monitoring"""
        try:
            self.is_active = False
            self.stop_event.set()
            
            if self.guardian_thread and self.guardian_thread.is_alive():
                self.guardian_thread.join(timeout=2)
            
            if self.camera:
                self.camera.release()
                self.camera = None
            
            print("Health & Workspace Guardian stopped")
            
        except Exception as e:
            print(f"Failed to stop guardian: {e}")
    
    def _guardian_loop(self):
        """Main guardian monitoring loop"""
        print("Health guardian loop started")
        
        while self.is_active and not self.stop_event.is_set():
            try:
                # Capture frame
                ret, frame = self.camera.read()
                if not ret:
                    continue
                
                # Convert to RGB
                frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                
                # Process pose for posture monitoring
                pose_results = self.pose.process(frame_rgb) if self.pose else None
                
                # Process face mesh for eye tracking
                face_results = self.face_mesh.process(frame_rgb) if self.face_mesh else None
                
                # Monitor posture
                if pose_results and pose_results.pose_landmarks:
                    self._monitor_posture(pose_results.pose_landmarks, frame)
                
                # Monitor eye strain
                if face_results and face_results.multi_face_landmarks:
                    self._monitor_eye_strain(face_results.multi_face_landmarks[0], frame)
                
                # Update eye strain timer
                self._update_eye_strain_timer()
                
                # Update FPS
                self._update_fps()
                
                # Display monitoring info (optional)
                self._display_monitoring_info(frame)
                
            except Exception as e:
                print(f"Guardian loop error: {e}")
                time.sleep(0.1)
        
        print("Health guardian loop ended")
    
    def _monitor_posture(self, pose_landmarks, frame):
        """Monitor user posture using pose landmarks"""
        try:
            # Get key landmarks
            left_shoulder = pose_landmarks.landmark[11]
            right_shoulder = pose_landmarks.landmark[12]
            left_hip = pose_landmarks.landmark[23]
            right_hip = pose_landmarks.landmark[24]
            nose = pose_landmarks.landmark[0]
            
            # Calculate shoulder alignment
            shoulder_slope = abs(left_shoulder.y - right_shoulder.y)
            
            # Calculate spine alignment (shoulder to hip)
            shoulder_center = (left_shoulder.y + right_shoulder.y) / 2
            hip_center = (left_hip.y + right_hip.y) / 2
            spine_alignment = abs(shoulder_center - hip_center)
            
            # Calculate head position (nose to shoulder center)
            head_to_shoulder = abs(nose.y - shoulder_center)
            
            # Calculate posture score (0-100)
            alignment_score = max(0, 100 - (shoulder_slope * 500))  # Shoulder alignment
            spine_score = max(0, 100 - (spine_alignment * 200))  # Spine alignment
            head_score = max(0, 100 - (head_to_shoulder * 300))  # Head position
            
            self.current_posture_score = (alignment_score + spine_score + head_score) / 3
            
            # Update daily stats
            self.daily_stats['posture_score_sum'] += self.current_posture_score
            self.daily_stats['posture_score_count'] += 1
            
            # Check for slouching
            current_time = time.time()
            if self.current_posture_score < self.posture_threshold:
                if self.slouch_start_time is None:
                    self.slouch_start_time = current_time
                elif (current_time - self.slouch_start_time > self.slouch_threshold_seconds and 
                      current_time - self.last_posture_warning > self.posture_warning_interval):
                    
                    self._trigger_posture_warning()
                    self.last_posture_warning = current_time
                    self.daily_stats['posture_warnings'] += 1
            else:
                self.slouch_start_time = None
            
            # Log posture data
            self._log_health_data('posture', {
                'score': self.current_posture_score,
                'alignment_score': alignment_score,
                'spine_score': spine_score,
                'head_score': head_score,
                'is_slouching': self.current_posture_score < self.posture_threshold
            })
            
            self.posture_checks += 1
            
        except Exception as e:
            print(f"Posture monitoring error: {e}")
    
    def _monitor_eye_strain(self, face_landmarks, frame):
        """Monitor eye strain using face mesh landmarks"""
        try:
            # Get eye landmarks
            left_eye_landmarks = [33, 7, 163, 144, 145, 153, 154, 155, 133, 173, 157, 158, 159, 160, 161, 246]
            right_eye_landmarks = [362, 398, 384, 385, 386, 387, 388, 389, 390, 374, 380, 381, 382, 373, 374, 380]
            
            # Calculate eye openness (simplified)
            left_eye_openness = self._calculate_eye_openness(face_landmarks, left_eye_landmarks)
            right_eye_openness = self._calculate_eye_openness(face_landmarks, right_eye_landmarks)
            
            avg_eye_openness = (left_eye_openness + right_eye_openness) / 2
            
            # Log eye data
            self._log_health_data('eye_strain', {
                'left_eye_openness': left_eye_openness,
                'right_eye_openness': right_eye_openness,
                'avg_openness': avg_eye_openness,
                'eyes_closed': avg_eye_openness < 0.3
            })
            
        except Exception as e:
            print(f"Eye strain monitoring error: {e}")
    
    def _calculate_eye_openness(self, face_landmarks, eye_landmarks):
        """Calculate eye openness from landmarks"""
        try:
            if len(eye_landmarks) < 4:
                return 0.5
            
            # Get top and bottom eye points
            top_point = face_landmarks.landmark[eye_landmarks[1]]
            bottom_point = face_landmarks.landmark[eye_landmarks[5]]
            
            # Calculate vertical distance
            eye_height = abs(top_point.y - bottom_point.y)
            
            # Normalize to 0-1 range
            openness = min(1.0, eye_height * 10)
            
            return openness
            
        except Exception as e:
            return 0.5
    
    def _update_eye_strain_timer(self):
        """Update 20-20-20 rule timer"""
        try:
            current_time = time.time()
            time_since_last_break = current_time - self.last_eye_break_time
            
            # Update timer (countdown to next break)
            self.eye_strain_timer = max(0, self.eye_break_interval - time_since_last_break)
            
            # Check if eye break is needed
            if (self.eye_strain_timer == 0 and 
                current_time - self.last_eye_warning > self.eye_warning_interval):
                
                self._trigger_eye_break_alert()
                self.last_eye_warning = current_time
                self.daily_stats['eye_strain_warnings'] += 1
            
        except Exception as e:
            print(f"Eye strain timer error: {e}")
    
    def _trigger_posture_warning(self):
        """Trigger posture correction warning"""
        try:
            message = "Sir, please adjust your posture for better focus. Your current posture score is below optimal."
            
            if self.voice_alerts_enabled:
                self._voice_alert(message)
            
            if self.visual_alerts_enabled:
                self._visual_alert("POSTURE ALERT", message)
            
            if self.audio_alerts_enabled:
                self._audio_alert()
            
            self.posture_alerts += 1
            print(f"Posture warning triggered - Score: {self.current_posture_score:.1f}")
            
        except Exception as e:
            print(f"Posture warning error: {e}")
    
    def _trigger_eye_break_alert(self):
        """Trigger 20-20-20 eye break alert"""
        try:
            message = "Sir, it's time for an eye break. Look at something 20 feet away for 20 seconds to reduce eye strain."
            
            if self.voice_alerts_enabled:
                self._voice_alert(message)
            
            if self.visual_alerts_enabled:
                self._visual_alert("EYE BREAK", message)
            
            if self.audio_alerts_enabled:
                self._audio_alert()
            
            self.eye_strain_alerts += 1
            self.daily_stats['eye_breaks_taken'] += 1
            print("Eye break alert triggered - 20-20-20 rule")
            
        except Exception as e:
            print(f"Eye break alert error: {e}")
    
    def _voice_alert(self, message: str):
        """Send voice alert"""
        try:
            # This would integrate with JARVIS voice system
            print(f"VOICE ALERT: {message}")
            # In production, this would call the JARVIS speak function
        except Exception as e:
            print(f"Voice alert error: {e}")
    
    def _visual_alert(self, title: str, message: str):
        """Send visual alert"""
        try:
            # This could show a popup or overlay
            print(f"VISUAL ALERT [{title}]: {message}")
            # In production, this would show a visual notification
        except Exception as e:
            print(f"Visual alert error: {e}")
    
    def _audio_alert(self):
        """Send audio alert"""
        try:
            if WINSOUND_AVAILABLE:
                winsound.Beep(1000, 500)  # 1000Hz for 500ms
            else:
                print("AUDIO ALERT: Beep")
        except Exception as e:
            print(f"Audio alert error: {e}")
    
    def _log_health_data(self, data_type: str, data: Dict[str, Any]):
        """Log health monitoring data"""
        try:
            log_entry = {
                'timestamp': datetime.now().isoformat(),
                'type': data_type,
                'data': data
            }
            
            self.health_log.append(log_entry)
            
            # Keep only last 1000 entries
            if len(self.health_log) > 1000:
                self.health_log = self.health_log[-1000:]
                
        except Exception as e:
            print(f"Health logging error: {e}")
    
    def _display_monitoring_info(self, frame):
        """Display monitoring information on frame"""
        try:
            # Add posture score
            cv2.putText(frame, f"Posture: {self.current_posture_score:.1f}", 
                       (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
            
            # Add eye strain timer
            minutes = int(self.eye_strain_timer // 60)
            seconds = int(self.eye_strain_timer % 60)
            cv2.putText(frame, f"Eye Break: {minutes:02d}:{seconds:02d}", 
                       (10, 60), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
            
            # Add status indicators
            posture_status = "GOOD" if self.current_posture_score >= self.posture_threshold else "POOR"
            eye_status = "OK" if self.eye_strain_timer > 60 else "BREAK NEEDED"
            
            cv2.putText(frame, f"Status: {posture_status} | {eye_status}", 
                       (10, 90), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
            
        except Exception as e:
            print(f"Display info error: {e}")
    
    def _update_fps(self):
        """Update FPS counter"""
        self.frame_count += 1
        elapsed_time = time.time() - self.start_time
        if elapsed_time > 1:
            self.fps = self.frame_count / elapsed_time
            self.frame_count = 0
            self.start_time = time.time()
    
    def take_eye_break(self):
        """Manually trigger eye break"""
        self.last_eye_break_time = time.time()
        print("Eye break taken manually - timer reset")
    
    def get_health_status(self) -> Dict[str, Any]:
        """Get current health monitoring status"""
        return {
            "is_active": self.is_active,
            "current_posture_score": self.current_posture_score,
            "posture_threshold": self.posture_threshold,
            "eye_strain_timer": self.eye_strain_timer,
            "eye_break_interval": self.eye_break_interval,
            "is_slouching": self.current_posture_score < self.posture_threshold,
            "eye_break_needed": self.eye_strain_timer == 0,
            "fps": self.fps,
            "posture_checks": self.posture_checks,
            "posture_alerts": self.posture_alerts,
            "eye_strain_alerts": self.eye_strain_alerts
        }
    
    def get_daily_stats(self) -> Dict[str, Any]:
        """Get daily health statistics"""
        avg_posture_score = 0
        if self.daily_stats['posture_score_count'] > 0:
            avg_posture_score = self.daily_stats['posture_score_sum'] / self.daily_stats['posture_score_count']
        
        return {
            "avg_posture_score": avg_posture_score,
            "posture_checks": self.daily_stats['posture_score_count'],
            "eye_breaks_taken": self.daily_stats['eye_breaks_taken'],
            "posture_warnings": self.daily_stats['posture_warnings'],
            "eye_strain_warnings": self.daily_stats['eye_strain_warnings'],
            "date": datetime.now().date().isoformat()
        }
    
    def reset_daily_stats(self):
        """Reset daily statistics"""
        self.daily_stats = {
            'posture_score_sum': 0,
            'posture_score_count': 0,
            'eye_breaks_taken': 0,
            'posture_warnings': 0,
            'eye_strain_warnings': 0
        }
        print("Daily health statistics reset")
    
    def get_health_log(self, limit: int = 100) -> List[Dict[str, Any]]:
        """Get recent health monitoring log"""
        return self.health_log[-limit:]
    
    def get_status(self) -> Dict[str, Any]:
        """Get health guardian service status"""
        return {
            "is_active": self.is_active,
            "mediapipe_available": MEDIAPIPE_AVAILABLE,
            "winsound_available": WINSOUND_AVAILABLE,
            "current_posture_score": self.current_posture_score,
            "eye_strain_timer": self.eye_strain_timer,
            "posture_checks": self.posture_checks,
            "posture_alerts": self.posture_alerts,
            "eye_strain_alerts": self.eye_strain_alerts,
            "health_log_entries": len(self.health_log),
            "last_updated": datetime.now().isoformat()
        }
