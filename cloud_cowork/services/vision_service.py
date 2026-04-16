"""Vision Service for Cloud Cowork HUD"""

import cv2
import numpy as np
import base64
import io
from PIL import Image
from typing import Optional, Tuple

# Add JARVIS backend path
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

try:
    import ollama
    VISION_MODEL = "moondream"
    VISION_AVAILABLE = True
except ImportError as e:
    print(f"Vision components not available: {e}")
    VISION_AVAILABLE = False

class VisionService:
    """Vision service for camera and object detection"""
    
    def __init__(self):
        self.camera_active = False
        self.current_frame = None
        self.analysis_result = ""
    
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
    
    def capture_frame(self) -> Optional[np.ndarray]:
        """Capture single frame from camera"""
        try:
            cap = cv2.VideoCapture(0)
            if not cap.isOpened():
                return None
            
            ret, frame = cap.read()
            cap.release()
            
            if ret:
                return frame
            return None
        except Exception as e:
            print(f"Error capturing frame: {e}")
            return None
    
    def analyze_frame(self, frame: np.ndarray) -> str:
        """Analyze frame using Moondream"""
        try:
            if not VISION_AVAILABLE:
                return "Vision model not available"
            
            # Convert frame to PIL Image
            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            pil_image = Image.fromarray(frame_rgb)
            
            # Encode to base64
            buffered = io.BytesIO()
            pil_image.save(buffered, format="JPEG")
            b64_image = base64.b64encode(buffered.getvalue()).decode()
            
            # Send to Moondream
            response = ollama.chat(
                model=VISION_MODEL,
                messages=[{
                    'role': 'user',
                    'content': 'Analyze this camera frame. Describe what you see in detail, including objects, people, and environment.',
                    'images': [b64_image]
                }]
            )
            
            return response['message']['content']
        except Exception as e:
            return f"Error analyzing frame: {e}"
    
    def get_status(self) -> dict:
        """Get current vision service status"""
        return {
            "camera_active": self.camera_active,
            "model_available": VISION_AVAILABLE,
            "model_name": VISION_MODEL if VISION_AVAILABLE else "Not Available"
        }
