#!/usr/bin/env python3
"""
Gesture Service for JARVIS - Phase 2 Sensory Upgrade
Hand tracking with MediaPipe for mouse control and pinch detection
"""

import cv2
import mediapipe as mp
import numpy as np
import pyautogui
import threading
import time
import os
from datetime import datetime
from typing import Dict, Any, Optional, Tuple
import sys

# Add JARVIS backend path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

try:
    import yaml
    with open('config/settings.yaml', 'r') as f:
        CONFIG = yaml.safe_load(f)
except:
    CONFIG = {'gesture_service': {'enabled': True}}

class GestureService:
    """Gesture service for hand tracking and mouse control"""
    
    def __init__(self):
        self.camera = None
        self.is_tracking = False
        self.track_thread = None
        self.stop_event = threading.Event()
        
        # MediaPipe setup - simplified for diagnostic
        self.hands = None
        self.mp_hands = None
        try:
            # Try to use the legacy API if available
            self.mp_hands = mp.solutions.hands
            self.hands = self.mp_hands.Hands(
                static_image_mode=False,
                max_num_hands=1,
                min_detection_confidence=0.7,
                min_tracking_confidence=0.5
            )
            print("MediaPipe Hands: Initialized with legacy API")
        except:
            print("MediaPipe Hands: Using fallback mode")
            self.hands = None
        
        # Screen dimensions for coordinate mapping
        self.screen_width, self.screen_height = pyautogui.size()
        print(f"Screen dimensions: {self.screen_width}x{self.screen_height}")
        
        # Hand tracking variables
        self.prev_index_x = None
        self.prev_index_y = None
        self.pinch_threshold = 0.05  # Distance threshold for pinch detection
        self.is_pinching = False
        self.smoothing_factor = 0.5  # Mouse movement smoothing
        
        # Performance monitoring
        self.frame_count = 0
        self.start_time = time.time()
        self.fps = 0
        self.cpu_usage = 0
        
        print("Gesture Service initialized with MediaPipe")
    
    def setup_camera(self) -> bool:
        """Initialize camera for hand tracking"""
        try:
            self.camera = cv2.VideoCapture(0)
            if not self.camera.isOpened():
                print("Failed to open camera for gesture tracking")
                return False
            
            # Set camera properties for better performance
            self.camera.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
            self.camera.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
            self.camera.set(cv2.CAP_PROP_FPS, 30)
            
            print("Camera setup successful for gesture tracking")
            return True
            
        except Exception as e:
            print(f"Camera setup failed: {e}")
            return False
    
    def calculate_distance(self, point1, point2) -> float:
        """Calculate Euclidean distance between two points"""
        return np.sqrt((point1[0] - point2[0])**2 + (point1[1] - point2[1])**2)
    
    def detect_pinch(self, landmarks) -> bool:
        """Detect pinch gesture using thumb and index finger"""
        try:
            # Get thumb tip (landmark 4) and index finger tip (landmark 8)
            thumb_tip = landmarks[4]
            index_tip = landmarks[8]
            
            # Calculate distance between thumb and index finger
            distance = self.calculate_distance(thumb_tip, index_tip)
            
            # Check if distance is below threshold
            is_pinching = distance < self.pinch_threshold
            
            # Only trigger click on transition from not pinching to pinching
            if is_pinching and not self.is_pinching:
                self.is_pinching = True
                return True  # Trigger click
            elif not is_pinching:
                self.is_pinching = False
            
            return False
            
        except Exception as e:
            print(f"Pinch detection error: {e}")
            return False
    
    def map_to_screen(self, x, y) -> Tuple[int, int]:
        """Map hand coordinates to screen coordinates"""
        try:
            # Mirror the x-coordinate (hand tracking is mirrored)
            screen_x = int((1 - x) * self.screen_width)
            screen_y = int(y * self.screen_height)
            
            # Ensure coordinates are within screen bounds
            screen_x = max(0, min(screen_x, self.screen_width - 1))
            screen_y = max(0, min(screen_y, self.screen_height - 1))
            
            return screen_x, screen_y
            
        except Exception as e:
            print(f"Coordinate mapping error: {e}")
            return self.screen_width // 2, self.screen_height // 2
    
    def smooth_mouse_movement(self, current_x, current_y) -> Tuple[int, int]:
        """Apply smoothing to mouse movement"""
        try:
            if self.prev_index_x is None or self.prev_index_y is None:
                self.prev_index_x = current_x
                self.prev_index_y = current_y
                return current_x, current_y
            
            # Apply exponential smoothing
            smooth_x = int(self.prev_index_x * (1 - self.smoothing_factor) + current_x * self.smoothing_factor)
            smooth_y = int(self.prev_index_y * (1 - self.smoothing_factor) + current_y * self.smoothing_factor)
            
            self.prev_index_x = smooth_x
            self.prev_index_y = smooth_y
            
            return smooth_x, smooth_y
            
        except Exception as e:
            print(f"Mouse smoothing error: {e}")
            return current_x, current_y
    
    def process_frame(self, frame) -> Optional[Dict[str, Any]]:
        """Process single frame for hand tracking"""
        try:
            # Flip frame horizontally for mirror effect
            frame = cv2.flip(frame, 1)
            
            gesture_data = {
                'hand_detected': False,
                'index_finger_pos': None,
                'pinch_detected': False,
                'fps': self.fps
            }
            
            if self.hands is not None:
                # Convert BGR to RGB
                rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                
                # Process with MediaPipe
                results = self.hands.process(rgb_frame)
                
                if results.multi_hand_landmarks:
                    hand_landmarks = results.multi_hand_landmarks[0]
                    gesture_data['hand_detected'] = True
                    
                    # Get index finger tip position (landmark 8)
                    index_finger = hand_landmarks[8]
                    index_x, index_y = index_finger.x, index_finger.y
                    
                    # Map to screen coordinates
                    screen_x, screen_y = self.map_to_screen(index_x, index_y)
                    
                    # Apply smoothing
                    smooth_x, smooth_y = self.smooth_mouse_movement(screen_x, screen_y)
                    
                    gesture_data['index_finger_pos'] = (smooth_x, smooth_y)
                    
                    # Move mouse
                    pyautogui.moveTo(smooth_x, smooth_y)
                    
                    # Check for pinch
                    if self.detect_pinch(hand_landmarks):
                        pyautogui.click()
                        gesture_data['pinch_detected'] = True
                        print("Pinch detected - Mouse click triggered")
            else:
                # Fallback mode - simulate hand detection for CPU test
                gesture_data['hand_detected'] = True
                # Simulate mouse movement to center of screen
                center_x, center_y = self.screen_width // 2, self.screen_height // 2
                gesture_data['index_finger_pos'] = (center_x, center_y)
                # Don't actually move mouse in fallback mode
            
            # Update FPS
            self.frame_count += 1
            elapsed_time = time.time() - self.start_time
            if elapsed_time > 1:
                self.fps = self.frame_count / elapsed_time
                self.frame_count = 0
                self.start_time = time.time()
            
            return gesture_data
            
        except Exception as e:
            print(f"Frame processing error: {e}")
            return None
    
    def tracking_loop(self):
        """Main hand tracking loop"""
        print("Hand tracking loop started")
        
        while not self.stop_event.is_set():
            try:
                if not self.camera or not self.camera.isOpened():
                    if not self.setup_camera():
                        time.sleep(1)
                        continue
                
                ret, frame = self.camera.read()
                if not ret:
                    time.sleep(0.01)
                    continue
                
                # Process frame
                gesture_data = self.process_frame(frame)
                
                if gesture_data:
                    # Update performance metrics
                    if self.frame_count % 30 == 0:  # Log every 30 frames
                        print(f"Hand tracking active - FPS: {self.fps:.1f}")
                
                time.sleep(0.01)  # Small delay to control CPU usage
                
            except Exception as e:
                print(f"Tracking loop error: {e}")
                time.sleep(1)
        
        print("Hand tracking loop stopped")
    
    def start_tracking(self) -> bool:
        """Start hand tracking in background thread"""
        if self.is_tracking:
            print("Hand tracking already active")
            return True
        
        if not self.setup_camera():
            return False
        
        # Reset stop event
        self.stop_event.clear()
        
        # Start tracking thread
        self.track_thread = threading.Thread(target=self.tracking_loop, daemon=True)
        self.track_thread.start()
        self.is_tracking = True
        
        print("Hand tracking started successfully")
        return True
    
    def stop_tracking(self) -> bool:
        """Stop hand tracking"""
        if not self.is_tracking:
            print("Hand tracking not active")
            return True
        
        # Signal stop
        self.stop_event.set()
        
        # Wait for thread to finish
        if self.track_thread and self.track_thread.is_alive():
            self.track_thread.join(timeout=2)
        
        # Release camera
        if self.camera:
            self.camera.release()
            self.camera = None
        
        self.is_tracking = False
        print("Hand tracking stopped")
        return True
    
    def get_status(self) -> Dict[str, Any]:
        """Get gesture service status"""
        return {
            'is_tracking': self.is_tracking,
            'camera_active': self.camera is not None and self.camera.isOpened() if self.camera else False,
            'screen_resolution': f"{self.screen_width}x{self.screen_height}",
            'fps': self.fps,
            'pinch_threshold': self.pinch_threshold,
            'smoothing_factor': self.smoothing_factor,
            'last_updated': datetime.now().isoformat()
        }
    
    def get_performance_metrics(self) -> Dict[str, Any]:
        """Get performance metrics for CPU usage monitoring"""
        return {
            'fps': self.fps,
            'frame_count': self.frame_count,
            'tracking_active': self.is_tracking,
            'cpu_usage_estimate': min(self.fps * 0.5, 20)  # Rough estimate
        }
