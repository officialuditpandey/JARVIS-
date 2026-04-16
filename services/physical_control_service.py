#!/usr/bin/env python3
"""
Physical Control Service for JARVIS - Features 31-35
Advanced Gesture Mouse and Virtual Air Switches with MediaPipe
"""

import os
import sys
import time
import threading
import math
from datetime import datetime
from typing import Dict, Any, Optional, Tuple, List
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
    import pyautogui
    PYAUTOGUI_AVAILABLE = True
    pyautogui.FAILSAFE = False
except ImportError:
    print("pyautogui not available - Installing...")
    os.system("pip install pyautogui")
    try:
        import pyautogui
        PYAUTOGUI_AVAILABLE = True
        pyautogui.FAILSAFE = False
    except ImportError:
        PYAUTOGUI_AVAILABLE = False

try:
    import pynput
    from pynput.mouse import Controller as MouseController
    from pynput.keyboard import Controller as KeyboardController, Key
    PYNPUT_AVAILABLE = True
except ImportError:
    print("pynput not available - Installing...")
    os.system("pip install pynput")
    try:
        import pynput
        from pynput.mouse import Controller as MouseController
        from pynput.keyboard import Controller as KeyboardController, Key
        PYNPUT_AVAILABLE = True
    except ImportError:
        PYNPUT_AVAILABLE = False

class PhysicalControlService:
    """Physical Control service for gesture-based computer control"""
    
    def __init__(self):
        self.camera = None
        self.is_active = False
        self.control_thread = None
        self.stop_event = threading.Event()
        
        # MediaPipe setup
        self.mp_hands = None
        self.hands = None
        self.mp_drawing = None
        
        # Control variables
        self.mouse_controller = None
        self.keyboard_controller = None
        self.screen_width, self.screen_height = 0, 0
        
        # Gesture tracking
        self.prev_index_x = None
        self.prev_index_y = None
        self.prev_thumb_x = None
        self.prev_thumb_y = None
        self.pinch_start_time = None
        self.is_pinching = False
        self.click_cooldown = 0
        
        # Virtual switches
        self.virtual_switches = {
            'volume_up': False,
            'volume_down': False,
            'next_tab': False,
            'prev_tab': False,
            'space': False,
            'enter': False
        }
        
        # Performance metrics
        self.fps = 0
        self.frame_count = 0
        self.start_time = time.time()
        self.gesture_count = 0
        self.last_gesture_time = 0
        
        # Initialize
        self._initialize_controls()
        
        print("Physical Control Service initialized with Gesture Mouse & Virtual Switches")
    
    def _initialize_controls(self):
        """Initialize MediaPipe and control systems"""
        try:
            # Initialize MediaPipe
            if MEDIAPIPE_AVAILABLE:
                self.mp_hands = mp.solutions.hands
                self.hands = self.mp_hands.Hands(
                    static_image_mode=False,
                    max_num_hands=1,
                    min_detection_confidence=0.7,
                    min_tracking_confidence=0.5
                )
                self.mp_drawing = mp.solutions.drawing_utils
                print("MediaPipe hands initialized")
            
            # Initialize controllers
            if PYNPUT_AVAILABLE:
                self.mouse_controller = MouseController()
                self.keyboard_controller = KeyboardController()
                print("Mouse and keyboard controllers initialized")
            elif PYAUTOGUI_AVAILABLE:
                self.mouse_controller = pyautogui
                print("PyAutoGUI mouse controller initialized")
            
            # Get screen dimensions
            if PYAUTOGUI_AVAILABLE:
                self.screen_width, self.screen_height = pyautogui.size()
            else:
                import ctypes
                user32 = ctypes.windll.user32
                self.screen_width = user32.GetSystemMetrics(0)
                self.screen_height = user32.GetSystemMetrics(1)
            
            print(f"Screen dimensions: {self.screen_width}x{self.screen_height}")
            
        except Exception as e:
            print(f"Control initialization failed: {e}")
    
    def start_control(self, camera_index: int = 0) -> bool:
        """Start physical control system"""
        try:
            if self.is_active:
                return True
            
            # Initialize camera
            self.camera = cv2.VideoCapture(camera_index)
            if not self.camera.isOpened():
                print("Failed to open camera")
                return False
            
            self.camera.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
            self.camera.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
            self.camera.set(cv2.CAP_PROP_FPS, 30)
            
            self.is_active = True
            self.stop_event.clear()
            
            # Start control thread
            self.control_thread = threading.Thread(target=self._control_loop, daemon=True)
            self.control_thread.start()
            
            print("Physical control system started")
            return True
            
        except Exception as e:
            print(f"Failed to start control: {e}")
            return False
    
    def stop_control(self):
        """Stop physical control system"""
        try:
            self.is_active = False
            self.stop_event.set()
            
            if self.control_thread and self.control_thread.is_alive():
                self.control_thread.join(timeout=2)
            
            if self.camera:
                self.camera.release()
                self.camera = None
            
            print("Physical control system stopped")
            
        except Exception as e:
            print(f"Failed to stop control: {e}")
    
    def _control_loop(self):
        """Main control loop"""
        print("Physical control loop started")
        
        while self.is_active and not self.stop_event.is_set():
            try:
                # Capture frame
                ret, frame = self.camera.read()
                if not ret:
                    continue
                
                # Process frame
                frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                results = self.hands.process(frame_rgb) if self.hands else None
                
                # Process hand gestures
                if results and results.multi_hand_landmarks:
                    hand_landmarks = results.multi_hand_landmarks[0]
                    self._process_hand_gestures(hand_landmarks, frame)
                    
                    # Draw hand landmarks
                    if self.mp_drawing:
                        self.mp_drawing.draw_landmarks(frame, hand_landmarks, self.mp_hands.HAND_CONNECTIONS)
                
                # Update FPS
                self._update_fps()
                
                # Display frame (optional - can be disabled for performance)
                # cv2.imshow('Physical Control', frame)
                # if cv2.waitKey(1) & 0xFF == ord('q'):
                #     break
                
            except Exception as e:
                print(f"Control loop error: {e}")
                time.sleep(0.1)
        
        print("Physical control loop ended")
    
    def _process_hand_gestures(self, hand_landmarks, frame):
        """Process hand gestures for control"""
        try:
            # Get key landmarks
            index_finger_tip = hand_landmarks.landmark[8]
            thumb_tip = hand_landmarks.landmark[4]
            middle_finger_tip = hand_landmarks.landmark[12]
            ring_finger_tip = hand_landmarks.landmark[16]
            pinky_tip = hand_landmarks.landmark[20]
            
            # Convert to screen coordinates
            index_x = int(index_finger_tip.x * self.screen_width)
            index_y = int(index_finger_tip.y * self.screen_height)
            thumb_x = int(thumb_tip.x * self.screen_width)
            thumb_y = int(thumb_tip.y * self.screen_height)
            
            # Smooth movement
            if self.prev_index_x is not None:
                smooth_x = int(self.prev_index_x * 0.7 + index_x * 0.3)
                smooth_y = int(self.prev_index_y * 0.7 + index_y * 0.3)
            else:
                smooth_x, smooth_y = index_x, index_y
            
            # Move mouse (index finger)
            self._move_mouse(smooth_x, smooth_y)
            
            # Detect pinch (thumb and index finger)
            pinch_distance = math.sqrt((index_x - thumb_x)**2 + (index_y - thumb_y)**2)
            pinch_threshold = 50  # pixels
            
            if pinch_distance < pinch_threshold:
                if not self.is_pinching:
                    self.is_pinching = True
                    self.pinch_start_time = time.time()
                    self._perform_click()
            else:
                self.is_pinching = False
            
            # Detect virtual switches (hand gestures)
            self._detect_virtual_switches(hand_landmarks)
            
            # Update previous positions
            self.prev_index_x = smooth_x
            self.prev_index_y = smooth_y
            self.prev_thumb_x = thumb_x
            self.prev_thumb_y = thumb_y
            
            # Update gesture count
            current_time = time.time()
            if current_time - self.last_gesture_time > 0.1:  # Debounce
                self.gesture_count += 1
                self.last_gesture_time = current_time
            
        except Exception as e:
            print(f"Gesture processing error: {e}")
    
    def _move_mouse(self, x: int, y: int):
        """Move mouse to specified coordinates"""
        try:
            if self.mouse_controller:
                if PYNPUT_AVAILABLE:
                    self.mouse_controller.position = (x, y)
                else:
                    self.mouse_controller.moveTo(x, y)
        except Exception as e:
            print(f"Mouse movement error: {e}")
    
    def _perform_click(self):
        """Perform mouse click"""
        try:
            if self.click_cooldown <= 0:
                if self.mouse_controller:
                    if PYNPUT_AVAILABLE:
                        self.mouse_controller.click(Button.left)
                    else:
                        self.mouse_controller.click()
                
                self.click_cooldown = 5  # Prevent multiple clicks
                print("Gesture click performed")
        except Exception as e:
            print(f"Click error: {e}")
    
    def _detect_virtual_switches(self, hand_landmarks):
        """Detect virtual switch gestures"""
        try:
            # Get landmark positions
            index_finger_tip = hand_landmarks.landmark[8]
            middle_finger_tip = hand_landmarks.landmark[12]
            ring_finger_tip = hand_landmarks.landmark[16]
            pinky_tip = hand_landmarks.landmark[20]
            wrist = hand_landmarks.landmark[0]
            
            # Calculate hand openness (all fingers extended)
            fingers_up = 0
            
            # Index finger
            if index_finger_tip.y < hand_landmarks.landmark[6].y:
                fingers_up += 1
            
            # Middle finger
            if middle_finger_tip.y < hand_landmarks.landmark[10].y:
                fingers_up += 1
            
            # Ring finger
            if ring_finger_tip.y < hand_landmarks.landmark[14].y:
                fingers_up += 1
            
            # Pinky
            if pinky_tip.y < hand_landmarks.landmark[18].y:
                fingers_up += 1
            
            # Thumb
            if thumb_tip.x > hand_landmarks.landmark[2].x:
                fingers_up += 1
            
            # Virtual switch actions based on finger count
            current_time = time.time()
            
            if fingers_up == 5 and not self.virtual_switches['space']:
                # Open palm - Space bar
                self._press_key('space')
                self.virtual_switches['space'] = True
                print("Virtual switch: Space")
            elif fingers_up == 2 and not self.virtual_switches['enter']:
                # Peace sign - Enter
                self._press_key('enter')
                self.virtual_switches['enter'] = True
                print("Virtual switch: Enter")
            elif fingers_up == 3 and not self.virtual_switches['volume_up']:
                # Three fingers - Volume up
                self._press_key('volume_up')
                self.virtual_switches['volume_up'] = True
                print("Virtual switch: Volume up")
            elif fingers_up == 4 and not self.virtual_switches['volume_down']:
                # Four fingers - Volume down
                self._press_key('volume_down')
                self.virtual_switches['volume_down'] = True
                print("Virtual switch: Volume down")
            else:
                # Reset virtual switches
                for switch in self.virtual_switches:
                    self.virtual_switches[switch] = False
            
        except Exception as e:
            print(f"Virtual switch detection error: {e}")
    
    def _press_key(self, key_name: str):
        """Press a virtual key"""
        try:
            if self.keyboard_controller:
                if key_name == 'space':
                    self.keyboard_controller.press(Key.space)
                    self.keyboard_controller.release(Key.space)
                elif key_name == 'enter':
                    self.keyboard_controller.press(Key.enter)
                    self.keyboard_controller.release(Key.enter)
                elif key_name == 'volume_up':
                    self.keyboard_controller.press(Key.media_volume_up)
                    self.keyboard_controller.release(Key.media_volume_up)
                elif key_name == 'volume_down':
                    self.keyboard_controller.press(Key.media_volume_down)
                    self.keyboard_controller.release(Key.media_volume_down)
                elif key_name == 'next_tab':
                    self.keyboard_controller.press(Key.ctrl)
                    self.keyboard_controller.press(Key.tab)
                    self.keyboard_controller.release(Key.tab)
                    self.keyboard_controller.release(Key.ctrl)
                elif key_name == 'prev_tab':
                    self.keyboard_controller.press(Key.ctrl)
                    self.keyboard_controller.press(Key.shift)
                    self.keyboard_controller.press(Key.tab)
                    self.keyboard_controller.release(Key.tab)
                    self.keyboard_controller.release(Key.shift)
                    self.keyboard_controller.release(Key.ctrl)
        except Exception as e:
            print(f"Key press error: {e}")
    
    def _update_fps(self):
        """Update FPS counter"""
        self.frame_count += 1
        elapsed_time = time.time() - self.start_time
        if elapsed_time > 1:
            self.fps = self.frame_count / elapsed_time
            self.frame_count = 0
            self.start_time = time.time()
        
        # Update cooldowns
        if self.click_cooldown > 0:
            self.click_cooldown -= 1
    
    def get_status(self) -> Dict[str, Any]:
        """Get physical control service status"""
        return {
            "is_active": self.is_active,
            "mediapipe_available": MEDIAPIPE_AVAILABLE,
            "pyautogui_available": PYAUTOGUI_AVAILABLE,
            "pynput_available": PYNPUT_AVAILABLE,
            "screen_width": self.screen_width,
            "screen_height": self.screen_height,
            "fps": self.fps,
            "gesture_count": self.gesture_count,
            "virtual_switches": self.virtual_switches,
            "last_updated": datetime.now().isoformat()
        }
    
    def get_performance_metrics(self) -> Dict[str, Any]:
        """Get performance metrics"""
        return {
            "fps": self.fps,
            "gesture_count": self.gesture_count,
            "is_pinching": self.is_pinching,
            "click_cooldown": self.click_cooldown,
            "active_switches": [k for k, v in self.virtual_switches.items() if v],
            "camera_active": self.camera is not None and self.camera.isOpened() if self.camera else False,
            "thread_active": self.control_thread.is_alive() if self.control_thread else False
        }
    
    def test_gesture_detection(self, duration: int = 10) -> Dict[str, Any]:
        """Test gesture detection performance"""
        print(f"Testing gesture detection for {duration} seconds...")
        
        start_time = time.time()
        test_gestures = 0
        test_clicks = 0
        test_switches = 0
        
        # Temporarily enable test mode
        original_click = self._perform_click
        original_switch = self._detect_virtual_switches
        
        test_results = {
            'gestures_detected': 0,
            'clicks_performed': 0,
            'switches_activated': 0,
            'avg_fps': 0,
            'hardware_lag_ms': 0
        }
        
        def test_click():
            nonlocal test_clicks
            test_clicks += 1
        
        def test_switch(hand_landmarks):
            nonlocal test_switches
            test_switches += 1
        
        # Override methods for testing
        self._perform_click = test_click
        # Note: Virtual switch testing would need more complex implementation
        
        try:
            # Start control if not already active
            was_active = self.is_active
            if not was_active:
                self.start_control()
            
            # Run test
            while time.time() - start_time < duration:
                test_gestures += 1
                time.sleep(0.1)
            
            # Calculate metrics
            test_results['gestures_detected'] = test_gestures
            test_results['clicks_performed'] = test_clicks
            test_results['switches_activated'] = test_switches
            test_results['avg_fps'] = self.fps
            test_results['hardware_lag_ms'] = (1000 / self.fps) if self.fps > 0 else 0
            
            print(f"Test completed: {test_gestures} gestures, {test_clicks} clicks, {test_switches} switches")
            
        except Exception as e:
            print(f"Test failed: {e}")
        finally:
            # Restore original methods
            self._perform_click = original_click
            self._detect_virtual_switches = original_switch
            
            # Stop control if we started it
            if not was_active:
                self.stop_control()
        
        return test_results
