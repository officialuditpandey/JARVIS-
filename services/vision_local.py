"""
Local Vision Service for Cloud Cowork HUD
Uses only local Moondream model for all vision processing
"""

import os
import sys
import cv2
import numpy as np
import base64
import io
from PIL import Image
from typing import Optional, Tuple, Dict, List
from datetime import datetime

# Add JARVIS backend path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

try:
    import ollama
    OLLAMA_AVAILABLE = True
except ImportError as e:
    print(f"Ollama not available: {e}")
    OLLAMA_AVAILABLE = False

try:
    import pyautogui
    SCREEN_CAPTURE_AVAILABLE = True
except ImportError as e:
    print(f"Screen capture not available: {e}")
    SCREEN_CAPTURE_AVAILABLE = False

class LocalVision:
    """Local Vision Service using only Moondream"""
    
    def __init__(self, vision_model: str = "moondream"):
        self.vision_model = vision_model
        self.camera_active = False
        self.current_frame = None
        self.analysis_history = []
        
        # Check if vision model is available
        if OLLAMA_AVAILABLE:
            try:
                models = ollama.list()
                available_models = [model.model.split(':')[0] for model in models.models]
                self.model_available = vision_model.split(':')[0] in available_models
                
                if not self.model_available:
                    print(f"Vision model {vision_model} not found in Ollama")
                    # Try to find alternative vision model
                    for model in available_models:
                        if 'moondream' in model.lower() or 'vision' in model.lower():
                            self.vision_model = model
                            self.model_available = True
                            print(f"Using alternative vision model: {model}")
                            break
            except Exception as e:
                print(f"Vision model check failed: {e}")
                self.model_available = False
        else:
            self.model_available = False
    
    def is_available(self) -> bool:
        """Check if vision service is available"""
        return OLLAMA_AVAILABLE and self.model_available
    
    def get_status(self) -> Dict:
        """Get vision service status"""
        return {
            "ollama_available": OLLAMA_AVAILABLE,
            "model_available": self.model_available,
            "vision_model": self.vision_model,
            "camera_active": self.camera_active,
            "analysis_count": len(self.analysis_history)
        }
    
    def capture_screen(self) -> Optional[Image.Image]:
        """Capture screen screenshot"""
        if not SCREEN_CAPTURE_AVAILABLE:
            return None
        
        try:
            screenshot = pyautogui.screenshot()
            return screenshot
        except Exception as e:
            print(f"Screen capture failed: {e}")
            return None
    
    def capture_camera_frame(self) -> Optional[np.ndarray]:
        """Capture frame from camera"""
        try:
            cap = cv2.VideoCapture(0)
            if not cap.isOpened():
                return None
            
            ret, frame = cap.read()
            cap.release()
            
            if ret and frame is not None and len(frame) > 0:
                self.current_frame = frame
                return frame
            return None
        except Exception as e:
            print(f"Camera capture failed: {e}")
            return None
    
    def start_camera_feed(self) -> bool:
        """Start camera feed"""
        try:
            if self.camera_active:
                return True
            
            # Test camera access
            cap = cv2.VideoCapture(0)
            if cap.isOpened():
                cap.release()
                self.camera_active = True
                return True
            return False
        except Exception as e:
            print(f"Camera start failed: {e}")
            return False
    
    def stop_camera_feed(self):
        """Stop camera feed"""
        self.camera_active = False
    
    def analyze_image(self, image: Image.Image, prompt: str = "Analyze this image in detail.") -> str:
        """Analyze image using local Moondream"""
        if not self.is_available():
            return "Vision service is not available"
        
        try:
            # Convert image to base64
            buffered = io.BytesIO()
            image.save(buffered, format="JPEG")
            b64_image = base64.b64encode(buffered.getvalue()).decode()
            
            # Send to Moondream
            response = ollama.chat(
                model=self.vision_model,
                messages=[{
                    'role': 'user',
                    'content': prompt,
                    'images': [b64_image]
                }]
            )
            
            analysis = response['message']['content']
            
            # Store in history
            self.analysis_history.append({
                "prompt": prompt,
                "analysis": analysis,
                "timestamp": datetime.now().isoformat()
            })
            
            # Keep only last 50 analyses
            if len(self.analysis_history) > 50:
                self.analysis_history.pop(0)
            
            return analysis
            
        except Exception as e:
            return f"Vision analysis failed: {e}"
    
    def analyze_screen(self, prompt: str = "What is on my screen?") -> str:
        """Analyze screen screenshot"""
        screenshot = self.capture_screen()
        if screenshot is None:
            return "Screen capture failed"
        
        return self.analyze_image(screenshot, prompt)
    
    def analyze_camera_frame(self, prompt: str = "Analyze this camera frame.") -> str:
        """Analyze current camera frame"""
        if not self.camera_active:
            return "Camera is not active"
        
        frame = self.capture_camera_frame()
        if frame is None:
            return "Camera capture failed"
        
        # Convert frame to PIL Image
        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        pil_image = Image.fromarray(frame_rgb)
        
        return self.analyze_image(pil_image, prompt)
    
    def detect_objects(self, image: Image.Image) -> List[str]:
        """Detect objects in image"""
        prompt = """List all objects you can see in this image. Respond with only the object names, one per line, in this format:
object1
object2
object3
"""
        
        analysis = self.analyze_image(image, prompt)
        
        # Parse object list
        objects = [obj.strip() for obj in analysis.split('\n') if obj.strip()]
        return objects[:20]  # Limit to 20 objects
    
    def analyze_text(self, image: Image.Image) -> str:
        """Extract and analyze text from image"""
        prompt = "Read any text visible in this image and provide the content. If no text is visible, say 'No text detected'."
        
        return self.analyze_image(image, prompt)
    
    def get_analysis_history(self, limit: int = 10) -> List[Dict]:
        """Get recent analysis history"""
        return self.analysis_history[-limit:]
    
    def clear_history(self):
        """Clear analysis history"""
        self.analysis_history = []
