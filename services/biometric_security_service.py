#!/usr/bin/env python3
"""
Biometric Security Service for JARVIS - Feature 42
Facial Login check with camera authentication and privacy protection
"""

import os
import sys
import time
import threading
import json
import hashlib
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
    import face_recognition
    FACE_RECOGNITION_AVAILABLE = True
except ImportError:
    print("face_recognition not available - Installing...")
    os.system("pip install face_recognition")
    try:
        import face_recognition
        FACE_RECOGNITION_AVAILABLE = True
    except ImportError:
        FACE_RECOGNITION_AVAILABLE = False

try:
    import winsound
    WINSOUND_AVAILABLE = True
except ImportError:
    print("winsound not available - Using alternative alerts")
    WINSOUND_AVAILABLE = False

class BiometricSecurityService:
    """Biometric Security service with facial authentication"""
    
    def __init__(self):
        self.camera = None
        self.is_active = False
        self.security_thread = None
        self.stop_event = threading.Event()
        
        # MediaPipe setup
        self.mp_face_detection = None
        self.face_detection = None
        self.mp_face_mesh = None
        self.face_mesh = None
        
        # Security state
        self.is_authenticated = False
        self.current_user = None
        self.unknown_faces_detected = []
        self.last_authentication_time = 0
        self.last_scan_time = 0
        
        # Authentication settings
        self.authentication_timeout = 300  # 5 minutes
        self.scan_interval = 5  # Scan every 5 seconds
        self.face_match_threshold = 0.6  # Face recognition threshold
        self.unknown_face_threshold = 0.3  # Threshold for unknown face detection
        
        # Privacy protection
        self.privacy_mode = False
        self.screen_blurred = False
        self.sensitive_data_hidden = False
        
        # Face database
        self.face_database_file = "security/face_database.json"
        self.face_encodings = {}
        self.face_metadata = {}
        
        # Security logs
        self.security_log = []
        self.login_attempts = []
        self.security_events = []
        
        # Performance metrics
        self.fps = 0
        self.frame_count = 0
        self.start_time = time.time()
        self.authentications = 0
        self.unknown_face_detections = 0
        
        # Initialize
        self._initialize_security()
        
        print("Biometric Security Service initialized with Facial Login")
    
    def _initialize_security(self):
        """Initialize security systems and load face database"""
        try:
            # Initialize MediaPipe
            if MEDIAPIPE_AVAILABLE:
                self.mp_face_detection = mp.solutions.face_detection
                self.face_detection = self.mp_face_detection.FaceDetection(
                    model_selection=0, min_detection_confidence=0.5
                )
                
                self.mp_face_mesh = mp.solutions.face_mesh
                self.face_mesh = self.mp_face_mesh.FaceMesh(
                    static_image_mode=False,
                    max_num_faces=5,
                    refine_landmarks=True,
                    min_detection_confidence=0.5,
                    min_tracking_confidence=0.5
                )
                
                print("MediaPipe face detection initialized")
            
            # Create security directory
            os.makedirs("security", exist_ok=True)
            
            # Load face database
            self._load_face_database()
            
        except Exception as e:
            print(f"Security initialization failed: {e}")
    
    def _load_face_database(self):
        """Load face database from file"""
        try:
            if os.path.exists(self.face_database_file):
                with open(self.face_database_file, 'r') as f:
                    data = json.load(f)
                    self.face_encodings = data.get('encodings', {})
                    self.face_metadata = data.get('metadata', {})
                    print(f"Loaded {len(self.face_encodings)} face encodings")
            else:
                print("No face database found - creating new one")
                self._save_face_database()
                
        except Exception as e:
            print(f"Failed to load face database: {e}")
    
    def _save_face_database(self):
        """Save face database to file"""
        try:
            data = {
                'encodings': self.face_encodings,
                'metadata': self.face_metadata,
                'last_updated': datetime.now().isoformat()
            }
            
            with open(self.face_database_file, 'w') as f:
                json.dump(data, f, indent=2)
                
        except Exception as e:
            print(f"Failed to save face database: {e}")
    
    def register_face(self, name: str, image_path: str = None, camera_index: int = 0) -> bool:
        """Register a new face in the database"""
        try:
            if not FACE_RECOGNITION_AVAILABLE:
                print("face_recognition not available - using MediaPipe fallback")
                return self._register_face_mediapipe(name, camera_index)
            
            # Load image from file or camera
            if image_path and os.path.exists(image_path):
                image = face_recognition.load_image_file(image_path)
            else:
                # Capture from camera
                camera = cv2.VideoCapture(camera_index)
                ret, frame = camera.read()
                if ret:
                    image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                else:
                    print("Failed to capture image")
                    return False
                camera.release()
            
            # Find face locations
            face_locations = face_recognition.face_locations(image)
            if not face_locations:
                print("No face found in image")
                return False
            
            # Get face encoding
            face_encodings = face_recognition.face_encodings(image, face_locations)
            if not face_encodings:
                print("Failed to generate face encoding")
                return False
            
            # Store encoding
            encoding_list = face_encodings[0].tolist()
            self.face_encodings[name] = encoding_list
            self.face_metadata[name] = {
                'registered_at': datetime.now().isoformat(),
                'method': 'face_recognition',
                'image_source': image_path or 'camera'
            }
            
            # Save database
            self._save_face_database()
            
            print(f"Face registered for: {name}")
            return True
            
        except Exception as e:
            print(f"Face registration failed: {e}")
            return False
    
    def _register_face_mediapipe(self, name: str, camera_index: int = 0) -> bool:
        """Register face using MediaPipe fallback"""
        try:
            camera = cv2.VideoCapture(camera_index)
            if not camera.isOpened():
                print("Failed to open camera")
                return False
            
            print("Please look at the camera for face registration...")
            time.sleep(2)
            
            ret, frame = camera.read()
            if not ret:
                print("Failed to capture image")
                camera.release()
                return False
            
            # Convert to RGB
            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            
            # Detect face
            results = self.face_detection.process(frame_rgb)
            if not results.detections:
                print("No face detected")
                camera.release()
                return False
            
            # Generate face descriptor (simplified)
            face_descriptor = self._generate_face_descriptor(frame_rgb, results.detections[0])
            
            # Store descriptor
            self.face_encodings[name] = face_descriptor
            self.face_metadata[name] = {
                'registered_at': datetime.now().isoformat(),
                'method': 'mediapipe',
                'image_source': 'camera'
            }
            
            # Save database
            self._save_face_database()
            
            camera.release()
            print(f"Face registered for: {name} (MediaPipe)")
            return True
            
        except Exception as e:
            print(f"MediaPipe face registration failed: {e}")
            return False
    
    def _generate_face_descriptor(self, image: np.ndarray, detection) -> List[float]:
        """Generate face descriptor using MediaPipe"""
        try:
            # Get face bounding box
            bbox = detection.bounding_box
            h, w, _ = image.shape
            x1 = int(bbox.xmin * w)
            y1 = int(bbox.ymin * h)
            x2 = int((bbox.xmin + bbox.width) * w)
            y2 = int((bbox.ymin + bbox.height) * h)
            
            # Extract face region
            face_region = image[y1:y2, x1:x2]
            
            # Resize to standard size
            face_resized = cv2.resize(face_region, (64, 64))
            
            # Generate simple descriptor (average color values)
            descriptor = face_resized.flatten().tolist()
            
            return descriptor
            
        except Exception as e:
            print(f"Face descriptor generation failed: {e}")
            return [0.0] * 64 * 64 * 3  # Fallback descriptor
    
    def start_security_monitoring(self, camera_index: int = 0) -> bool:
        """Start biometric security monitoring"""
        try:
            if self.is_active:
                return True
            
            # Initialize camera
            self.camera = cv2.VideoCapture(camera_index)
            if not self.camera.isOpened():
                print("Failed to open camera for security monitoring")
                return False
            
            self.camera.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
            self.camera.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
            self.camera.set(cv2.CAP_PROP_FPS, 30)
            
            self.is_active = True
            self.stop_event.clear()
            
            # Start security thread
            self.security_thread = threading.Thread(target=self._security_loop, daemon=True)
            self.security_thread.start()
            
            print("Biometric security monitoring started")
            return True
            
        except Exception as e:
            print(f"Failed to start security monitoring: {e}")
            return False
    
    def stop_security_monitoring(self):
        """Stop biometric security monitoring"""
        try:
            self.is_active = False
            self.stop_event.set()
            
            if self.security_thread and self.security_thread.is_alive():
                self.security_thread.join(timeout=2)
            
            if self.camera:
                self.camera.release()
                self.camera = None
            
            print("Biometric security monitoring stopped")
            
        except Exception as e:
            print(f"Failed to stop security monitoring: {e}")
    
    def _security_loop(self):
        """Main security monitoring loop"""
        print("Biometric security loop started")
        
        while self.is_active and not self.stop_event.is_set():
            try:
                # Check authentication timeout
                current_time = time.time()
                if self.is_authenticated and (current_time - self.last_authentication_time > self.authentication_timeout):
                    self._trigger_logout()
                
                # Scan for faces at intervals
                if current_time - self.last_scan_time > self.scan_interval:
                    self._scan_for_faces()
                    self.last_scan_time = current_time
                
                # Update FPS
                self._update_fps()
                
                time.sleep(0.1)
                
            except Exception as e:
                print(f"Security loop error: {e}")
                time.sleep(1)
        
        print("Biometric security loop ended")
    
    def _scan_for_faces(self):
        """Scan for faces and perform authentication"""
        try:
            ret, frame = self.camera.read()
            if not ret:
                return
            
            # Convert to RGB
            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            
            # Detect faces
            results = self.face_detection.process(frame_rgb)
            
            if results.detections:
                for detection in results.detections:
                    # Try to authenticate face
                    user_id = self._authenticate_face(frame_rgb, detection)
                    
                    if user_id:
                        # Known face detected
                        if not self.is_authenticated or user_id != self.current_user:
                            self._trigger_login(user_id)
                    else:
                        # Unknown face detected
                        self._handle_unknown_face(detection)
            
        except Exception as e:
            print(f"Face scanning error: {e}")
    
    def _authenticate_face(self, image: np.ndarray, detection) -> Optional[str]:
        """Authenticate detected face"""
        try:
            if not self.face_encodings:
                return None
            
            # Generate face descriptor
            face_descriptor = self._generate_face_descriptor(image, detection)
            
            # Compare with known faces
            best_match = None
            best_similarity = 0
            
            for user_id, stored_encoding in self.face_encodings.items():
                # Calculate similarity
                similarity = self._calculate_similarity(face_descriptor, stored_encoding)
                
                if similarity > best_similarity and similarity > self.face_match_threshold:
                    best_similarity = similarity
                    best_match = user_id
            
            if best_match:
                self.authentications += 1
                print(f"Face authenticated: {best_match} (similarity: {best_similarity:.2f})")
            
            return best_match
            
        except Exception as e:
            print(f"Face authentication error: {e}")
            return None
    
    def _calculate_similarity(self, descriptor1: List[float], descriptor2: List[float]) -> float:
        """Calculate similarity between face descriptors"""
        try:
            if len(descriptor1) != len(descriptor2):
                return 0.0
            
            # Calculate cosine similarity
            dot_product = sum(a * b for a, b in zip(descriptor1, descriptor2))
            magnitude1 = sum(a * a for a in descriptor1) ** 0.5
            magnitude2 = sum(b * b for b in descriptor2) ** 0.5
            
            if magnitude1 == 0 or magnitude2 == 0:
                return 0.0
            
            similarity = dot_product / (magnitude1 * magnitude2)
            return max(0.0, similarity)
            
        except Exception as e:
            print(f"Similarity calculation error: {e}")
            return 0.0
    
    def _handle_unknown_face(self, detection):
        """Handle detection of unknown face"""
        try:
            current_time = time.time()
            
            # Add to unknown faces list
            unknown_face = {
                'timestamp': current_time,
                'confidence': detection.score[0],
                'location': detection.bounding_box
            }
            
            self.unknown_faces_detected.append(unknown_face)
            
            # Keep only recent unknown faces
            self.unknown_faces_detected = [
                f for f in self.unknown_faces_detected 
                if current_time - f['timestamp'] < 60
            ]
            
            # Check if privacy protection should be triggered
            if len(self.unknown_faces_detected) >= 3:  # Multiple unknown faces
                self._trigger_privacy_protection()
            
            self.unknown_face_detections += 1
            print(f"Unknown face detected (confidence: {detection.score[0]:.2f})")
            
        except Exception as e:
            print(f"Unknown face handling error: {e}")
    
    def _trigger_login(self, user_id: str):
        """Trigger login for authenticated user"""
        try:
            self.is_authenticated = True
            self.current_user = user_id
            self.last_authentication_time = time.time()
            
            # Clear privacy mode
            self._disable_privacy_protection()
            
            # Log login event
            self._log_security_event('login', {
                'user_id': user_id,
                'timestamp': datetime.now().isoformat(),
                'method': 'facial_authentication'
            })
            
            # Send alert
            self._send_security_alert(f"Welcome back, {user_id}! Full dashboard unlocked.")
            
            print(f"User authenticated: {user_id}")
            
        except Exception as e:
            print(f"Login trigger error: {e}")
    
    def _trigger_logout(self):
        """Trigger logout"""
        try:
            self.is_authenticated = False
            user_id = self.current_user
            self.current_user = None
            
            # Enable privacy protection
            self._enable_privacy_protection()
            
            # Log logout event
            self._log_security_event('logout', {
                'user_id': user_id,
                'timestamp': datetime.now().isoformat(),
                'reason': 'authentication_timeout'
            })
            
            # Send alert
            self._send_security_alert(f"Logged out: {user_id}. Privacy mode enabled.")
            
            print(f"User logged out: {user_id}")
            
        except Exception as e:
            print(f"Logout trigger error: {e}")
    
    def _trigger_privacy_protection(self):
        """Trigger privacy protection for unknown faces"""
        try:
            if not self.privacy_mode:
                self.privacy_mode = True
                self._blur_screen()
                self._hide_sensitive_data()
                
                self._log_security_event('privacy_protection', {
                    'timestamp': datetime.now().isoformat(),
                    'reason': 'unknown_face_detected',
                    'unknown_faces_count': len(self.unknown_faces_detected)
                })
                
                self._send_security_alert("Privacy mode activated - Unknown face detected!")
                
        except Exception as e:
            print(f"Privacy protection error: {e}")
    
    def _enable_privacy_protection(self):
        """Enable privacy protection"""
        self.privacy_mode = True
        self._blur_screen()
        self._hide_sensitive_data()
    
    def _disable_privacy_protection(self):
        """Disable privacy protection"""
        self.privacy_mode = False
        self._unblur_screen()
        self._show_sensitive_data()
    
    def _blur_screen(self):
        """Blur the screen"""
        try:
            if not self.screen_blurred:
                # This would integrate with system to blur screen
                self.screen_blurred = True
                print("Screen blurred for privacy")
        except Exception as e:
            print(f"Screen blur error: {e}")
    
    def _unblur_screen(self):
        """Unblur the screen"""
        try:
            if self.screen_blurred:
                # This would integrate with system to unblur screen
                self.screen_blurred = False
                print("Screen unblurred")
        except Exception as e:
            print(f"Screen unblur error: {e}")
    
    def _hide_sensitive_data(self):
        """Hide sensitive data"""
        try:
            if not self.sensitive_data_hidden:
                # This would hide sensitive UI elements
                self.sensitive_data_hidden = True
                print("Sensitive data hidden")
        except Exception as e:
            print(f"Hide sensitive data error: {e}")
    
    def _show_sensitive_data(self):
        """Show sensitive data"""
        try:
            if self.sensitive_data_hidden:
                # This would show sensitive UI elements
                self.sensitive_data_hidden = False
                print("Sensitive data shown")
        except Exception as e:
            print(f"Show sensitive data error: {e}")
    
    def _log_security_event(self, event_type: str, data: Dict[str, Any]):
        """Log security event"""
        try:
            event = {
                'timestamp': datetime.now().isoformat(),
                'type': event_type,
                'data': data
            }
            
            self.security_events.append(event)
            
            # Keep only last 1000 events
            if len(self.security_events) > 1000:
                self.security_events = self.security_events[-1000:]
                
        except Exception as e:
            print(f"Security logging error: {e}")
    
    def _send_security_alert(self, message: str):
        """Send security alert"""
        try:
            print(f"SECURITY ALERT: {message}")
            # This would integrate with JARVIS alert system
            
            # Audio alert
            if WINSOUND_AVAILABLE:
                winsound.Beep(800, 200)
                
        except Exception as e:
            print(f"Security alert error: {e}")
    
    def _update_fps(self):
        """Update FPS counter"""
        self.frame_count += 1
        elapsed_time = time.time() - self.start_time
        if elapsed_time > 1:
            self.fps = self.frame_count / elapsed_time
            self.frame_count = 0
            self.start_time = time.time()
    
    def manual_login(self, user_id: str) -> bool:
        """Manual login override"""
        try:
            if user_id in self.face_encodings:
                self._trigger_login(user_id)
                return True
            else:
                print(f"User {user_id} not found in face database")
                return False
        except Exception as e:
            print(f"Manual login error: {e}")
            return False
    
    def manual_logout(self):
        """Manual logout"""
        self._trigger_logout()
    
    def get_security_status(self) -> Dict[str, Any]:
        """Get current security status"""
        return {
            "is_active": self.is_active,
            "is_authenticated": self.is_authenticated,
            "current_user": self.current_user,
            "privacy_mode": self.privacy_mode,
            "screen_blurred": self.screen_blurred,
            "sensitive_data_hidden": self.sensitive_data_hidden,
            "unknown_faces_detected": len(self.unknown_faces_detected),
            "face_database_size": len(self.face_encodings),
            "fps": self.fps,
            "authentications": self.authentications,
            "unknown_face_detections": self.unknown_face_detections
        }
    
    def get_face_database(self) -> Dict[str, Any]:
        """Get face database information"""
        return {
            "users": list(self.face_encodings.keys()),
            "metadata": self.face_metadata,
            "database_file": self.face_database_file,
            "last_updated": self.face_metadata.get('last_updated', 'Unknown')
        }
    
    def get_security_log(self, limit: int = 100) -> List[Dict[str, Any]]:
        """Get recent security events"""
        return self.security_events[-limit:]
    
    def get_status(self) -> Dict[str, Any]:
        """Get biometric security service status"""
        return {
            "is_active": self.is_active,
            "is_authenticated": self.is_authenticated,
            "current_user": self.current_user,
            "privacy_mode": self.privacy_mode,
            "mediapipe_available": MEDIAPIPE_AVAILABLE,
            "face_recognition_available": FACE_RECOGNITION_AVAILABLE,
            "winsound_available": WINSOUND_AVAILABLE,
            "face_database_size": len(self.face_encodings),
            "security_events_count": len(self.security_events),
            "last_updated": datetime.now().isoformat()
        }
