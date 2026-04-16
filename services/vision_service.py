"""Vision Service for Cloud Cowork HUD - Enhanced with Sentinel Pack"""

import cv2
import numpy as np
import base64
import io
import json
import os
import threading
import time
from PIL import Image
from typing import Optional, Tuple, Dict, Any, List
from datetime import datetime
import pyautogui
import pygetwindow as gw

# Add JARVIS backend path
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

try:
    import ollama
    VISION_MODEL = "moondream"  # Use moondream which is available
    VISION_AVAILABLE = True
except ImportError as e:
    print(f"Vision components not available: {e}")
    VISION_AVAILABLE = False

try:
    import yaml
    with open('config/settings.yaml', 'r') as f:
        CONFIG = yaml.safe_load(f)
except:
    CONFIG = {
        'sentinel_pack': {
            'face_recognition': {'enabled': True, 'method': 'opencv', 'confidence_threshold': 0.7},
            'object_counting': {'enabled': True, 'track_objects': ['person', 'phone', 'book', 'key']},
            'motion_heatmaps': {'enabled': True, 'sensitivity': 25, 'min_area': 500}
        }
    }

class VisionService:
    """Vision service for camera and object detection"""
    
    def __init__(self):
        self.camera_active = False
        self.current_frame = None
        self.analysis_result = ""
        self.temp_image_path = "temp_eye.jpg"
        
        # Posture AI Features
        self.posture_monitoring = False
        self.slouch_start_time = None
        self.slouch_threshold = 30  # seconds
        self.last_posture_warning = 0
        self.posture_warning_interval = 60  # seconds between warnings
        
        # Face and pose detection for posture
        self.face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
        self.upper_body_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_upperbody.xml')
        
        # Posture metrics
        self.current_posture_score = 0
        self.eye_shoulder_ratio = 0
        self.slouching = False
        
        # Sentinel Pack Features
        self.face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
        self.face_whitelist = self.load_face_whitelist()
        self.object_counts = {}
        self.motion_accumulator = None
        self.motion_frame_count = 0
        self.baseline_frame = None
    
    def start_feed(self):
        """Start camera feed"""
        try:
            if not VISION_AVAILABLE:
                return "Vision components not available"
            
            self.camera_active = True
            return "Camera feed started"
        except Exception as e:
            return f"Error starting camera: {e}"
    
    def stop_feed(self):
        """Stop camera feed"""
        self.camera_active = False
        return "Camera feed stopped"
    
    def capture_frame(self, save_image: bool = True) -> Optional[np.ndarray]:
        """Capture single frame from camera and optionally save as temp_eye.jpg"""
        try:
            cap = cv2.VideoCapture(0)
            if not cap.isOpened():
                return None
            
            ret, frame = cap.read()
            cap.release()
            
            if ret:
                if save_image:
                    # Convert BGR to RGB (OpenCV uses BGR, PIL uses RGB)
                    frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                    
                    # Convert to PIL Image
                    image = Image.fromarray(frame_rgb)
                    
                    # Save as temp_eye.jpg
                    image.save(self.temp_image_path, "JPEG")
                    print(f"Image saved as {self.temp_image_path}")
                
                return frame
            return None
        except Exception as e:
            print(f"Error capturing frame: {e}")
            return None
    
    def check_model_availability(self, model_name: str) -> bool:
        """Check if a model is available in Ollama"""
        if not VISION_AVAILABLE:
            return False
            
        # Since we know moondream is available, return True for it
        if model_name == "moondream":
            return True
            
        try:
            models = ollama.list()
            return any(model.get('name', '').startswith(model_name) for model in models.get('models', []))
        except Exception as e:
            print(f"Error checking model availability: {e}")
            return False
    
    def analyze_frame(self, frame: np.ndarray, prompt: str = None, model: str = None) -> str:
        """Analyze frame using vision model"""
        try:
            if not VISION_AVAILABLE:
                return "Vision model not available"
            
            if model is None:
                model = VISION_MODEL
                
            if prompt is None:
                prompt = "You are JARVIS's eyes. Analyze the attached image and provide a natural, human-readable description of what you see. Describe objects, people, and the scene in natural language as if you're explaining it to a person. Avoid technical object detection IDs. Speak normally."
            
            # Convert frame to PIL Image
            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            pil_image = Image.fromarray(frame_rgb)
            
            # Check if model is available
            if not self.check_model_availability(model):
                # Try alternative models
                alternative_models = ["llava", "moondream", "llava-llama3", "bakllava"]
                for alt_model in alternative_models:
                    if self.check_model_availability(alt_model):
                        model = alt_model
                        print(f"Using alternative vision model: {model}")
                        break
                else:
                    return f"Vision model '{model}' not available. Please install with: ollama pull {model}"
            
            # Encode to base64
            buffered = io.BytesIO()
            pil_image.save(buffered, format="JPEG")
            b64_image = base64.b64encode(buffered.getvalue()).decode()
            
            print(f"Analyzing image with Ollama model: {model}")
            
            # Send to vision model with fresh context
            response = ollama.chat(
                model=model,
                messages=[{
                    'role': 'user',
                    'content': prompt,
                    'images': [b64_image]
                }],
                # Ensure no conversation history is used
                options={
                    'temperature': 0.1,  # Lower temperature for more factual responses
                    'top_p': 0.9,
                    'repeat_penalty': 1.1
                }
            )
            
            return response['message']['content']
        except Exception as e:
            return f"Error analyzing frame: {e}"
    
    def capture_and_analyze(self, prompt: str = None, model: str = None) -> Dict[str, Any]:
        """Capture image and analyze it in one call"""
        try:
            # First capture the image
            frame = self.capture_frame(save_image=True)
            
            if frame is None:
                return {
                    'success': False,
                    'error': "Failed to capture image from camera"
                }
            
            # Then analyze it
            analysis = self.analyze_frame(frame, prompt, model)
            
            return {
                'success': True,
                'analysis': analysis,
                'image_path': self.temp_image_path,
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': f"Capture and analyze failed: {e}"
            }
    
    def capture_active_window(self) -> Optional[np.ndarray]:
        """Capture screenshot of active window"""
        try:
            # Get active window
            active_window = gw.getActiveWindow()
            if not active_window:
                return None
            
            # Get window bounds
            left, top, right, bottom = active_window.left, active_window.top, active_window.right, active_window.bottom
            width, height = right - left, bottom - top
            
            # Capture screenshot of the window
            screenshot = pyautogui.screenshot(region=(left, top, width, height))
            
            # Convert to numpy array
            frame = cv2.cvtColor(np.array(screenshot), cv2.COLOR_RGB2BGR)
            
            return frame
            
        except Exception as e:
            print(f"Error capturing active window: {e}")
            return None
    
    def analyze_active_window(self, analysis_type: str = "general") -> Dict[str, Any]:
        """Analyze active window for code debugging, math solving, or general content"""
        try:
            # Capture active window
            frame = self.capture_active_window()
            if frame is None:
                return {
                    'success': False,
                    'error': 'Failed to capture active window'
                }
            
            # Determine prompt based on analysis type
            if analysis_type == "code":
                prompt = "You are JARVIS analyzing the active window which contains code. Look for bugs, syntax errors, logical errors, or optimization opportunities. Provide specific line-by-line analysis and suggestions for fixes. Focus on the code content, not the UI elements."
            elif analysis_type == "math":
                prompt = "You are JARVIS analyzing the active window which contains mathematical content. Look for equations, calculations, graphs, or mathematical problems. Provide step-by-step solutions, identify errors, and explain the mathematical concepts involved."
            else:
                prompt = "You are JARVIS analyzing the active window. Describe what you see in detail, focusing on the main content, text, and any actionable information. Ignore UI elements like buttons and menus unless they're relevant to the content."
            
            # Analyze the frame
            analysis = self.analyze_frame(frame, prompt)
            
            return {
                'success': True,
                'analysis_type': analysis_type,
                'analysis': analysis,
                'window_title': gw.getActiveWindow().title if gw.getActiveWindow() else 'Unknown',
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': f'Active window analysis failed: {str(e)}'
            }
    
    def debug_active_window_code(self) -> Dict[str, Any]:
        """Debug code in active window"""
        return self.analyze_active_window("code")
    
    def solve_active_window_math(self) -> Dict[str, Any]:
        """Solve math problems in active window"""
        return self.analyze_active_window("math")
    
    def get_status(self) -> dict:
        """Get current vision service status"""
        return {
            "camera_active": self.camera_active,
            "model_available": VISION_AVAILABLE,
            "model_name": VISION_MODEL if VISION_AVAILABLE else "Not Available",
            "sentinel_features": {
                "face_recognition": CONFIG['sentinel_pack']['face_recognition']['enabled'],
                "object_counting": CONFIG['sentinel_pack']['object_counting']['enabled'],
                "motion_heatmaps": CONFIG['sentinel_pack']['motion_heatmaps']['enabled']
            },
            'active_window_available': True,
            'active_window_title': gw.getActiveWindow().title if gw.getActiveWindow() else 'None'
        }
    
    # SENTINEL PACK METHODS
    
    def load_face_whitelist(self) -> List[Dict]:
        """Load face whitelist from file"""
        try:
            whitelist_file = CONFIG['sentinel_pack']['face_recognition'].get('whitelist_file', 'config/face_whitelist.json')
            if os.path.exists(whitelist_file):
                with open(whitelist_file, 'r') as f:
                    return json.load(f)
        except Exception as e:
            print(f"Failed to load face whitelist: {e}")
        return []
    
    def save_face_whitelist(self):
        """Save face whitelist to file"""
        try:
            whitelist_file = CONFIG['sentinel_pack']['face_recognition'].get('whitelist_file', 'config/face_whitelist.json')
            os.makedirs(os.path.dirname(whitelist_file), exist_ok=True)
            with open(whitelist_file, 'w') as f:
                json.dump(self.face_whitelist, f, indent=2)
        except Exception as e:
            print(f"Failed to save face whitelist: {e}")
    
    def detect_faces(self, frame: np.ndarray) -> List[Tuple[int, int, int, int]]:
        """Detect faces in frame using OpenCV"""
        if not CONFIG['sentinel_pack']['face_recognition']['enabled']:
            return []
        
        try:
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            faces = self.face_cascade.detectMultiScale(gray, 1.1, 4)
            return faces
        except Exception as e:
            print(f"Face detection error: {e}")
            return []
    
    def is_known_face(self, face_roi: np.ndarray) -> bool:
        """Check if face is in whitelist (simplified version)"""
        # For now, return True if whitelist is not empty (placeholder for actual face recognition)
        return len(self.face_whitelist) > 0
    
    def register_face(self, face_id: str, face_encoding: np.ndarray):
        """Register a new face to whitelist"""
        self.face_whitelist.append({
            'id': face_id,
            'encoding': face_encoding.tolist(),
            'registered_at': datetime.now().isoformat()
        })
        self.save_face_whitelist()
    
    def count_objects(self, frame: np.ndarray) -> Dict[str, int]:
        """Count objects in frame using vision analysis"""
        if not CONFIG['sentinel_pack']['object_counting']['enabled']:
            return {}
        
        try:
            # Use vision model to count objects
            prompt = f"Count and list the following objects in this image: {', '.join(CONFIG['sentinel_pack']['object_counting']['track_objects'])}. Return as JSON with object names as keys and counts as values."
            
            result = self.analyze_frame(frame, prompt)
            
            # Parse result (simplified)
            counts = {}
            for obj in CONFIG['sentinel_pack']['object_counting']['track_objects']:
                if obj.lower() in result.lower():
                    # Extract number from result (simplified parsing)
                    import re
                    numbers = re.findall(r'\d+', result)
                    if numbers:
                        counts[obj] = int(numbers[0])
                    else:
                        counts[obj] = 1
                else:
                    counts[obj] = 0
            
            self.object_counts = counts
            return counts
            
        except Exception as e:
            print(f"Object counting error: {e}")
            return {}
    
    def update_motion_heatmap(self, frame: np.ndarray):
        """Update motion heatmap accumulator"""
        if not CONFIG['sentinel_pack']['motion_heatmaps']['enabled']:
            return
        
        try:
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            
            if self.baseline_frame is None:
                self.baseline_frame = gray
                self.motion_accumulator = np.zeros_like(gray, dtype=np.float32)
                return
            
            # Calculate motion
            frame_delta = cv2.absdiff(self.baseline_frame, gray)
            thresh = cv2.threshold(frame_delta, CONFIG['sentinel_pack']['motion_heatmaps']['sensitivity'], 255, cv2.THRESH_BINARY)[1]
            
            # Update accumulator
            self.motion_accumulator = cv2.add(self.motion_accumulator, thresh.astype(np.float32))
            self.motion_frame_count += 1
            
            # Save heatmap periodically
            if self.motion_frame_count % 30 == 0:  # Every 30 frames
                self.save_motion_heatmap()
                
        except Exception as e:
            print(f"Motion heatmap error: {e}")
    
    def save_motion_heatmap(self):
        """Save motion heatmap to file"""
        try:
            if self.motion_accumulator is not None:
                # Normalize and convert to 8-bit
                heatmap = cv2.normalize(self.motion_accumulator, None, 0, 255, cv2.NORM_MINIMAL).astype(np.uint8)
                
                # Apply colormap
                heatmap_colored = cv2.applyColorMap(heatmap, cv2.COLORMAP_JET)
                
                # Save
                heatmap_file = CONFIG['sentinel_pack']['motion_heatmaps'].get('heatmap_file', 'temp_motion_heatmap.jpg')
                cv2.imwrite(heatmap_file, heatmap_colored)
                print(f"Motion heatmap saved: {heatmap_file}")
                
        except Exception as e:
            print(f"Failed to save motion heatmap: {e}")
    
    def get_sentinel_analysis(self, frame: np.ndarray) -> Dict[str, Any]:
        """Get comprehensive Sentinel Pack analysis"""
        analysis = {
            'faces_detected': [],
            'known_faces': 0,
            'unknown_faces': 0,
            'object_counts': {},
            'motion_detected': False,
            'heatmap_available': False
        }
        
        # Face detection
        faces = self.detect_faces(frame)
        analysis['faces_detected'] = len(faces)
        
        for (x, y, w, h) in faces:
            face_roi = frame[y:y+h, x:x+w]
            if self.is_known_face(face_roi):
                analysis['known_faces'] += 1
            else:
                analysis['unknown_faces'] += 1
        
        # Object counting
        analysis['object_counts'] = self.count_objects(frame)
        
        # Motion detection
        if self.motion_accumulator is not None:
            motion_intensity = np.mean(self.motion_accumulator)
            analysis['motion_detected'] = motion_intensity > CONFIG['sentinel_pack']['motion_heatmaps']['min_area']
            analysis['heatmap_available'] = True
        
        return analysis
    
    def calculate_posture_score(self, face_rect, upper_body_rect) -> float:
        """Calculate posture score based on eye-shoulder distance ratio"""
        try:
            if not face_rect or not upper_body_rect:
                return 0.0
            
            # Extract face and upper body coordinates
            fx, fy, fw, fh = face_rect
            ux, uy, uw, uh = upper_body_rect
            
            # Calculate eye level (top third of face)
            eye_y = fy + (fh * 0.3)
            
            # Calculate shoulder level (top of upper body)
            shoulder_y = uy
            
            # Calculate eye-shoulder distance
            eye_shoulder_distance = abs(eye_y - shoulder_y)
            
            # Calculate face height for normalization
            face_height = fh
            
            # Calculate ratio (higher ratio = better posture)
            if face_height > 0:
                self.eye_shoulder_ratio = eye_shoulder_distance / face_height
            else:
                self.eye_shoulder_ratio = 0
            
            # Normalize to 0-100 score (optimal ratio is around 1.5-2.0)
            optimal_ratio = 1.75
            if self.eye_shoulder_ratio > 0:
                if self.eye_shoulder_ratio < optimal_ratio:
                    score = (self.eye_shoulder_ratio / optimal_ratio) * 100
                else:
                    # Penalize too much distance (leaning back too far)
                    score = max(0, 100 - (self.eye_shoulder_ratio - optimal_ratio) * 20)
            else:
                score = 0
            
            return min(100, max(0, score))
            
        except Exception as e:
            print(f"Posture score calculation error: {e}")
            return 0.0
    
    def detect_posture(self, frame) -> Dict[str, Any]:
        """Detect posture from camera frame"""
        try:
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            
            # Detect face
            faces = self.face_cascade.detectMultiScale(gray, 1.1, 4)
            # Detect upper body
            try:
                upper_bodies = self.upper_body_cascade.detectMultiScale(gray, 1.1, 4)
            except:
                upper_bodies = []  # Fallback if upper body cascade fails
            
            posture_data = {
                'face_detected': len(faces) > 0,
                'upper_body_detected': len(upper_bodies) > 0,
                'posture_score': 0,
                'eye_shoulder_ratio': 0,
                'slouching': False
            }
            
            if len(faces) > 0 and len(upper_bodies) > 0:
                # Use the largest face and upper body
                face = max(faces, key=lambda x: x[2] * x[3])
                upper_body = max(upper_bodies, key=lambda x: x[2] * x[3])
                
                # Calculate posture score
                posture_score = self.calculate_posture_score(face, upper_body)
                self.current_posture_score = posture_score
                
                posture_data.update({
                    'posture_score': posture_score,
                    'eye_shoulder_ratio': self.eye_shoulder_ratio,
                    'slouching': posture_score < 60  # Consider slouching if score < 60
                })
                
                # Check for slouching
                self.check_slouching(posture_data['slouching'])
            
            return posture_data
            
        except Exception as e:
            print(f"Posture detection error: {e}")
            return {'error': str(e)}
    
    def check_slouching(self, is_slouching: bool):
        """Check slouching status and trigger warnings"""
        try:
            current_time = time.time()
            
            if is_slouching:
                if self.slouch_start_time is None:
                    self.slouch_start_time = current_time
                    self.slouching = True
                    print("Posture monitoring: Slouching detected")
                
                # Check if slouching for more than threshold
                slouch_duration = current_time - self.slouch_start_time
                
                if slouch_duration > self.slouch_threshold:
                    # Check if enough time has passed since last warning
                    if current_time - self.last_posture_warning > self.posture_warning_interval:
                        self.trigger_posture_warning()
                        self.last_posture_warning = current_time
            else:
                # Reset slouching detection
                if self.slouch_start_time is not None:
                    slouch_duration = current_time - self.slouch_start_time
                    if slouch_duration > 5:  # Only log if slouching was significant
                        print(f"Posture monitoring: Slouching corrected after {slouch_duration:.1f} seconds")
                    
                self.slouch_start_time = None
                self.slouching = False
            
        except Exception as e:
            print(f"Slouching check error: {e}")
    
    def trigger_posture_warning(self):
        """Trigger posture warning"""
        try:
            # Import speak function for voice warning
            from jarvis_final import speak
            
            warning_message = "Sir, please adjust your posture for better focus."
            speak(warning_message)
            print(f"Posture warning triggered: {warning_message}")
            
            # Log the warning
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            log_entry = f"""
## Posture Warning - {timestamp}

**Message**: {warning_message}
**Duration**: {self.slouch_threshold}+ seconds
**Posture Score**: {self.current_posture_score:.1f}
**Eye-Shoulder Ratio**: {self.eye_shoulder_ratio:.2f}

---
"""
            with open("Syllabus_Progress.md", 'a', encoding='utf-8') as f:
                f.write(log_entry)
                
        except Exception as e:
            print(f"Posture warning trigger error: {e}")
    
    def start_posture_monitoring(self) -> bool:
        """Start posture monitoring"""
        try:
            self.posture_monitoring = True
            print("Posture monitoring started")
            return True
        except Exception as e:
            print(f"Failed to start posture monitoring: {e}")
            return False
    
    def stop_posture_monitoring(self) -> bool:
        """Stop posture monitoring"""
        try:
            self.posture_monitoring = False
            self.slouch_start_time = None
            self.slouching = False
            print("Posture monitoring stopped")
            return True
        except Exception as e:
            print(f"Failed to stop posture monitoring: {e}")
            return False
    
    def get_posture_status(self) -> Dict[str, Any]:
        """Get current posture status"""
        return {
            'monitoring_active': self.posture_monitoring,
            'current_score': self.current_posture_score,
            'eye_shoulder_ratio': self.eye_shoulder_ratio,
            'slouching': self.slouching,
            'slouch_duration': (time.time() - self.slouch_start_time) if self.slouch_start_time else 0,
            'last_warning': self.last_posture_warning,
            'threshold_seconds': self.slouch_threshold
        }

    def get_status(self):
        return {
            'is_active': True,
            'camera_available': True
        }
