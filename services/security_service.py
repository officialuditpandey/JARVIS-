"""
Security Service for JARVIS - The Guardian Upgrade
Implements background motion detection and human verification
"""

import cv2
import numpy as np
import threading
import time
import os
from datetime import datetime
from typing import Optional, Dict, Any, Callable
import sys

# Add JARVIS backend path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

try:
    from services.vision_service import VisionService
    VISION_AVAILABLE = True
except ImportError as e:
    print(f"Vision service not available: {e}")
    VISION_AVAILABLE = False

class SecurityService:
    """Security service with motion detection and human verification"""
    
    def __init__(self):
        self.camera = None
        self.baseline_frame = None
        self.is_monitoring = False
        self.monitor_thread = None
        self.stop_event = threading.Event()
        self.motion_threshold = 25  # Motion sensitivity threshold
        self.min_area = 500  # Minimum area for motion detection
        self.security_logs_dir = os.getenv("SECURITY_LOGS_DIR", os.path.join(os.getcwd(), "security_logs"))
        self.alert_callback = None
        
        # Face detection and PC lock features
        self.face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
        self.face_whitelist = self.load_face_whitelist()
        self.last_face_seen = time.time()
        self.security_status = "Away"  # "Present" or "Away"
        self.away_timeout = 60  # 60 seconds timeout
        self.pc_lock_enabled = True
        self.face_detection_enabled = True
        self.motion_detection_enabled = True
        
        # Privacy Screen Blur
        self.privacy_blur_enabled = True
        self.privacy_blur_active = False
        self.unknown_face_detected = False
        self.privacy_blur_start_time = None
        self.privacy_blur_threshold = 5  # seconds before triggering blur
        
        # Security logs
        self.security_events = []
        self.log_directory = "security_logs"
        os.makedirs(self.log_directory, exist_ok=True)
        
        print("Security Service initialized with face detection, PC lock, and privacy screen blur")
    
    def load_face_whitelist(self) -> list:
        """Load face whitelist for known faces"""
        try:
            whitelist_file = os.path.join(self.security_logs_dir, "face_whitelist.txt")
            if os.path.exists(whitelist_file):
                with open(whitelist_file, 'r') as f:
                    return f.read().splitlines()
            return []
        except Exception as e:
            print(f"Failed to load face whitelist: {e}")
            return []
    
    def is_known_face(self, face_roi) -> bool:
        """Check if face is in whitelist"""
        try:
            # For now, return False (all faces are unknown for privacy testing)
            return False
        except Exception as e:
            print(f"Face recognition error: {e}")
            return False
    
    def setup_camera(self) -> bool:
        """Initialize camera for security monitoring"""
        try:
            self.camera = cv2.VideoCapture(0)
            if not self.camera.isOpened():
                print("Failed to open camera for security monitoring")
                return False
            
            # Set camera properties for better detection
            self.camera.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
            self.camera.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
            self.camera.set(cv2.CAP_PROP_FPS, 15)
            
            print("Camera setup successful for security monitoring")
            return True
        except Exception as e:
            print(f"Camera setup failed: {e}")
            return False
    
    def capture_baseline(self) -> bool:
        """Capture baseline frame for motion detection"""
        if not self.camera:
            if not self.setup_camera():
                return False
        
        try:
            # Wait for camera to stabilize
            time.sleep(2)
            
            ret, frame = self.camera.read()
            if ret:
                # Convert to grayscale and apply Gaussian blur for better motion detection
                gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                gray = cv2.GaussianBlur(gray, (21, 21), 0)
                self.baseline_frame = gray
                print("Baseline frame captured for motion detection")
                return True
            else:
                print("Failed to capture baseline frame")
                return False
        except Exception as e:
            print(f"Baseline capture failed: {e}")
            return False
    
    def detect_motion(self, frame: np.ndarray) -> bool:
        """Detect motion by comparing current frame to baseline"""
        if self.baseline_frame is None:
            return False
        
        try:
            # Convert to grayscale and blur
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            gray = cv2.GaussianBlur(gray, (21, 21), 0)
            
            # Compute difference between current frame and baseline
            frame_delta = cv2.absdiff(self.baseline_frame, gray)
            thresh = cv2.threshold(frame_delta, self.motion_threshold, 255, cv2.THRESH_BINARY)[1]
            
            # Dilate the thresholded image to fill in holes
            thresh = cv2.dilate(thresh, None, iterations=2)
            
            # Find contours
            contours, _ = cv2.findContours(thresh.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            
            # Check if any contour meets minimum area requirement
            for contour in contours:
                if cv2.contourArea(contour) < self.min_area:
                    continue
                return True
            
            return False
        except Exception as e:
            print(f"Motion detection error: {e}")
            return False
    
    def verify_human_presence(self, frame: np.ndarray) -> bool:
        """Use vision service to verify if a human is present in the frame"""
        if not VISION_AVAILABLE:
            print("Vision service not available for human verification")
            return False
        
        try:
            vision_service = VisionService()
            
            # Analyze frame with human detection prompt
            result = vision_service.analyze_frame(
                frame, 
                prompt="Is there a human in this image? Answer only YES or NO.",
                model="moondream"
            )
            
            if result and "YES" in result.upper():
                print("Human detected in security frame")
                return True
            else:
                print("No human detected in security frame")
                return False
                
        except Exception as e:
            print(f"Human verification error: {e}")
            return False
    
    def save_security_image(self, frame: np.ndarray, event_type: str = "motion") -> str:
        """Save security image with timestamp"""
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"security_{event_type}_{timestamp}.jpg"
            filepath = os.path.join(self.security_logs_dir, filename)
            
            cv2.imwrite(filepath, frame)
            print(f"Security image saved: {filepath}")
            return filepath
        except Exception as e:
            print(f"Failed to save security image: {e}")
            return ""
    
    def log_security_event(self, event_type: str, image_path: str = "", details: str = ""):
        """Log security event to Syllabus_Progress.md"""
        try:
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            
            log_entry = f"""
## Security Event - {timestamp}

**Event Type:** {event_type}
**Image Saved:** {image_path}
**Details:** {details}

---
"""
            
            # Append to log file
            with open("Syllabus_Progress.md", 'a', encoding='utf-8') as f:
                f.write(log_entry)
            
            print(f"Security event logged to Syllabus_Progress.md")
        except Exception as e:
            print(f"Failed to log security event: {e}")
    
    def trigger_alert(self, frame: np.ndarray, image_path: str):
        """Trigger security alert"""
        if self.alert_callback:
            self.alert_callback(frame, image_path)
        else:
            print("Security alert triggered but no callback set")
    
    def monitor_loop(self):
        """Main monitoring loop running in background thread"""
        print("Security monitoring started")
        
        consecutive_motion_frames = 0
        motion_threshold_frames = 3  # Require 3 consecutive motion frames
        
        while not self.stop_event.is_set():
            try:
                if not self.camera or not self.camera.isOpened():
                    if not self.setup_camera():
                        time.sleep(5)
                        continue
                
                ret, frame = self.camera.read()
                if not ret:
                    time.sleep(0.1)
                    continue
                
                # Check for motion
                if self.detect_motion(frame):
                    consecutive_motion_frames += 1
                    print(f"Motion detected - frame {consecutive_motion_frames}")
                    
                    # Require multiple consecutive motion frames to reduce false positives
                    if consecutive_motion_frames >= motion_threshold_frames:
                        print("Sustained motion detected - verifying human presence")
                        
                        # Check for face presence (Sir detection)
                        self.check_face_presence(frame)
                        
                        # Verify if it's a human
                        if self.verify_human_presence(frame):
                            # Save evidence
                            image_path = self.save_security_image(frame, "human_detected")
                            
                            # Log the event
                            self.log_security_event(
                                "HUMAN_DETECTED", 
                                image_path, 
                                "Unknown person detected by security system"
                            )
                            
                            # Trigger alert
                            self.trigger_alert(frame, image_path)
                            
                            # Reset counter to avoid multiple alerts for same event
                            consecutive_motion_frames = 0
                            
                            # Wait before continuing monitoring
                            time.sleep(10)
                else:
                    consecutive_motion_frames = 0
                
                # Always check for presence lock (even without motion)
                self.check_presence_lock(frame)
                
                # Check for privacy blur (unknown faces)
                self.check_privacy_blur(frame)
                
                # Small delay to prevent excessive CPU usage
                time.sleep(0.1)
                
            except Exception as e:
                print(f"Security monitoring error: {e}")
                time.sleep(1)
        
        print("Security monitoring stopped")
    
    def start_monitoring(self, alert_callback: Optional[Callable] = None) -> bool:
        """Start security monitoring in background thread"""
        if self.is_monitoring:
            print("Security monitoring already active")
            return True
        
        # Setup camera and capture baseline
        if not self.setup_camera():
            return False
        
        if not self.capture_baseline():
            return False
        
        # Set alert callback
        self.alert_callback = alert_callback
        
        # Reset stop event
        self.stop_event.clear()
        
        # Start monitoring thread
        self.monitor_thread = threading.Thread(target=self.monitor_loop, daemon=True)
        self.monitor_thread.start()
        self.is_monitoring = True
        
        print("Security monitoring started successfully")
        return True
    
    def stop_monitoring(self) -> bool:
        """Stop security monitoring"""
        if not self.is_monitoring:
            print("Security monitoring not active")
            return True
        
        # Signal stop
        self.stop_event.set()
        
        # Wait for thread to finish
        if self.monitor_thread and self.monitor_thread.is_alive():
            self.monitor_thread.join(timeout=5)
        
        # Release camera
        if self.camera:
            self.camera.release()
            self.camera = None
        
        self.is_monitoring = False
        print("Security monitoring stopped")
        return True
    
    def detect_faces(self, frame: np.ndarray) -> list:
        """Detect faces in frame using OpenCV and Moondream verification"""
        if not self.face_detection_enabled or frame is None:
            return []
        
        try:
            # First use OpenCV for quick face detection
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            faces = self.face_cascade.detectMultiScale(gray, 1.1, 4)
            
            # If faces detected, use Moondream to verify if it's "Sir"
            if len(faces) > 0:
                return self._verify_sir_with_moondream(frame, faces)
            else:
                return []
                
        except Exception as e:
            print(f"Face detection error: {e}")
            return []
    
    def _verify_sir_with_moondream(self, frame: np.ndarray, faces: list) -> list:
        """Use Moondream to verify if detected faces are Sir for Presence Lock"""
        try:
            # Save frame temporarily for Moondream analysis
            temp_frame_path = "temp_presence_frame.jpg"
            cv2.imwrite(temp_frame_path, frame)
            
            # Use Moondream to analyze the frame
            from services.vision_service import VisionService
            vision = VisionService()
            
            # Ask Moondream for presence detection
            prompt = "Is the user Sir present at the desk? Check if this is the main user. Answer YES if Sir is present, NO if not."
            analysis = vision.analyze_image_with_ollama(temp_frame_path, prompt)
            
            # Clean up temp file
            if os.path.exists(temp_frame_path):
                os.remove(temp_frame_path)
            
            # Check if Moondream confirms Sir is present
            if analysis and ("yes" in analysis.lower() or "sir" in analysis.lower() or "present" in analysis.lower()):
                print(f"Moondream confirmed: Sir is present for Presence Lock")
                return faces
            else:
                print(f"Moondream analysis: {analysis}")
                return []
                
        except Exception as e:
            print(f"Moondream presence verification error: {e}")
            # Fallback to OpenCV detection
            return faces
    
    def check_presence_lock(self, frame: np.ndarray) -> bool:
        """Check for Sir presence and handle 60-second Presence Lock"""
        faces = self.detect_faces(frame)
        if len(faces) > 0:
            # Sir is present - update timestamp
            self.last_face_seen = time.time()
            if self.security_status == "Away":
                self.security_status = "Present"
                print("Presence Lock: Sir Present - Moondream confirmed presence")
            return True
        else:
            # Check if Sir has been away for 60 seconds
            time_since_last_face = time.time() - self.last_face_seen
            if time_since_last_face > self.away_timeout and self.security_status == "Present":
                self.security_status = "Away"
                print(f"Presence Lock: Sir Away for {time_since_last_face:.0f} seconds - Locking PC")
                self.lock_pc()
            return False
    
    def check_face_presence(self, frame: np.ndarray) -> bool:
        """Check if user face is present"""
        faces = self.detect_faces(frame)
        if len(faces) > 0:
            self.last_face_seen = time.time()
            if self.security_status == "Away":
                self.security_status = "Present"
                print("Security: Sir Present - Face detected")
            return True
        else:
            # Check if user has been away for too long
            time_since_last_face = time.time() - self.last_face_seen
            if time_since_last_face > self.away_timeout and self.security_status == "Present":
                self.security_status = "Away"
                print(f"Security: Sir Away - No face for {time_since_last_face:.0f} seconds")
                self.lock_pc()
            return False
    
    def lock_pc(self):
        """Lock the PC when user is away"""
        if not self.pc_lock_enabled:
            return
        
        try:
            print("Security: Locking PC - Sir has been away too long")
            os.system("rundll32.exe user32.dll,LockWorkStation")
            
            # Log the lock event
            log_entry = f"""
## Security Event - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

**Event:** PC Auto-Lock
**Reason:** User away for more than {self.away_timeout} seconds
**Status:** Sir Away

---
"""
            with open(os.path.join(self.security_logs_dir, "security_log.md"), 'a') as f:
                f.write(log_entry)
                
        except Exception as e:
            print(f"PC Lock failed: {e}")
    
    def get_security_status(self) -> Dict[str, Any]:
        """Get current security status"""
        return {
            'status': self.security_status,
            'last_face_seen': time.strftime('%H:%M:%S', time.localtime(self.last_face_seen)),
            'monitoring_active': self.is_monitoring,
            'away_timeout': self.away_timeout,
            'pc_lock_enabled': self.pc_lock_enabled,
            'face_detection_enabled': self.face_detection_enabled,
            'motion_detection_enabled': self.motion_detection_enabled,
            'privacy_blur_enabled': self.privacy_blur_enabled,
            'privacy_blur_active': self.privacy_blur_active,
            'unknown_face_detected': self.unknown_face_detected
        }
    
    def detect_unknown_faces(self, frame: np.ndarray) -> bool:
        """Detect unknown faces in the background"""
        try:
            if not self.face_detection_enabled:
                return False
            
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            faces = self.face_cascade.detectMultiScale(gray, 1.1, 4)
            
            unknown_face_count = 0
            for (x, y, w, h) in faces:
                face_roi = frame[y:y+h, x:x+w]
                if not self.is_known_face(face_roi):
                    unknown_face_count += 1
            
            self.unknown_face_detected = unknown_face_count > 0
            return self.unknown_face_detected
            
        except Exception as e:
            print(f"Unknown face detection error: {e}")
            return False
    
    def check_privacy_blur(self, frame: np.ndarray):
        """Check for unknown faces and trigger privacy blur"""
        try:
            if not self.privacy_blur_enabled:
                return
            
            current_time = time.time()
            has_unknown_faces = self.detect_unknown_faces(frame)
            
            if has_unknown_faces:
                if self.privacy_blur_start_time is None:
                    self.privacy_blur_start_time = current_time
                    print("Privacy monitoring: Unknown face detected in background")
                
                # Check if unknown face has been present for threshold time
                blur_duration = current_time - self.privacy_blur_start_time
                
                if blur_duration > self.privacy_blur_threshold and not self.privacy_blur_active:
                    self.trigger_privacy_blur()
            else:
                # Reset privacy blur detection
                if self.privacy_blur_start_time is not None:
                    blur_duration = current_time - self.privacy_blur_start_time
                    if blur_duration > 3:  # Only log if significant
                        print(f"Privacy monitoring: Unknown faces cleared after {blur_duration:.1f} seconds")
                
                self.privacy_blur_start_time = None
                if self.privacy_blur_active:
                    self.disable_privacy_blur()
            
        except Exception as e:
            print(f"Privacy blur check error: {e}")
    
    def trigger_privacy_blur(self):
        """Trigger privacy screen blur"""
        try:
            self.privacy_blur_active = True
            print("Privacy screen blur activated - Unknown face detected")
            
            # Method 1: Minimize all windows
            try:
                import pyautogui
                pyautogui.hotkey('win', 'd')  # Show desktop (minimize all windows)
                print("Privacy action: All windows minimized")
            except Exception as e:
                print(f"Window minimization failed: {e}")
                # Fallback to privacy overlay
                self.show_privacy_overlay()
            
            # Log the privacy event
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            log_entry = f"""
## Privacy Alert - {timestamp}

**Action**: Privacy screen blur activated
**Reason**: Unknown face detected in background
**Duration**: {self.privacy_blur_threshold}+ seconds

---
"""
            with open("Syllabus_Progress.md", 'a', encoding='utf-8') as f:
                f.write(log_entry)
                
        except Exception as e:
            print(f"Privacy blur trigger error: {e}")
    
    def show_privacy_overlay(self):
        """Show privacy overlay on dashboard"""
        try:
            # Create privacy overlay file
            overlay_html = """
<!DOCTYPE html>
<html>
<head>
    <title>Privacy Mode Active</title>
    <style>
        body {
            margin: 0;
            padding: 0;
            background: linear-gradient(45deg, #1a1a1a, #2d2d2d);
            display: flex;
            justify-content: center;
            align-items: center;
            height: 100vh;
            font-family: Arial, sans-serif;
            color: white;
        }
        .privacy-container {
            text-align: center;
            padding: 40px;
            background: rgba(0, 0, 0, 0.8);
            border-radius: 15px;
            border: 2px solid #ff4444;
            box-shadow: 0 0 20px rgba(255, 68, 68, 0.5);
        }
        .shield-icon {
            font-size: 80px;
            color: #ff4444;
            margin-bottom: 20px;
        }
        h1 {
            color: #ff4444;
            margin-bottom: 10px;
        }
        .message {
            font-size: 18px;
            margin-bottom: 30px;
            color: #cccccc;
        }
        .instructions {
            font-size: 14px;
            color: #888888;
        }
    </style>
</head>
<body>
    <div class="privacy-container">
        <div class="shield-icon">SHIELD</div>
        <h1>PRIVACY MODE ACTIVE</h1>
        <div class="message">
            Unknown face detected in background<br>
            Screen content has been protected
        </div>
        <div class="instructions">
            Privacy mode will deactivate when unknown faces are no longer detected
        </div>
    </div>
</body>
</html>
"""
            
            with open("privacy_overlay.html", 'w', encoding='utf-8') as f:
                f.write(overlay_html)
            
            # Open privacy overlay in browser
            import webbrowser
            webbrowser.open(f"file://{os.path.abspath('privacy_overlay.html')}")
            print("Privacy overlay displayed in browser")
            
        except Exception as e:
            print(f"Privacy overlay error: {e}")
    
    def disable_privacy_blur(self):
        """Disable privacy screen blur"""
        try:
            self.privacy_blur_active = False
            print("Privacy screen blur deactivated - Area is now secure")
            
            # Restore windows if they were minimized
            try:
                import pyautogui
                pyautogui.hotkey('win', 'd')  # Toggle desktop back
                print("Privacy action: Windows restored")
            except Exception as e:
                print(f"Window restoration failed: {e}")
            
            # Close privacy overlay if open
            try:
                os.remove("privacy_overlay.html")
            except:
                pass
                
        except Exception as e:
            print(f"Privacy blur disable error: {e}")
    
    def toggle_privacy_blur(self, enabled: bool):
        """Toggle privacy blur feature"""
        self.privacy_blur_enabled = enabled
        if not enabled:
            self.privacy_blur_active = False
            self.privacy_blur_start_time = None
        print(f"Privacy blur: {'Enabled' if enabled else 'Disabled'}")
    
    def set_away_timeout(self, seconds: int):
        """Set away timeout in seconds"""
        self.away_timeout = max(30, min(300, seconds))  # 30s to 5min range
        print(f"Security: Away timeout set to {self.away_timeout} seconds")
    
    def toggle_pc_lock(self, enabled: bool):
        """Toggle PC lock feature"""
        self.pc_lock_enabled = enabled
        print(f"Security: PC lock {'enabled' if enabled else 'disabled'}")

    def get_status(self) -> Dict[str, Any]:
        """Get current security service status"""
        return {
            "is_monitoring": self.is_monitoring,
            "camera_active": self.camera is not None and self.camera.isOpened() if self.camera else False,
            "baseline_captured": self.baseline_frame is not None,
            "security_logs_dir": self.security_logs_dir,
            "motion_threshold": self.motion_threshold,
            "min_area": self.min_area,
            "security_status": self.security_status,
            "last_face_seen": datetime.fromtimestamp(self.last_face_seen).strftime('%H:%M:%S'),
            "away_timeout": self.away_timeout,
            "pc_lock_enabled": self.pc_lock_enabled,
            "face_detection_enabled": self.face_detection_enabled
        }
